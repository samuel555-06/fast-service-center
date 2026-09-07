from django import forms
from .models import Usuario


class TecnicoForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label='Contraseña',
        help_text='Mínimo 8 caracteres.',
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'telefono', 'password']
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'telefono': 'Teléfono',
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.Rol.TECNICO
        usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario