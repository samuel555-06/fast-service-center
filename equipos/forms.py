from django import forms
from clientes.models import Cliente
from .models import Equipo


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombre_completo', 'telefono']


class EquipoForm(forms.ModelForm):
    password_equipo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Dejar en blanco si no tiene'}),
        label='Contraseña del equipo',
    )

    class Meta:
        model = Equipo
        fields = [
            'marca', 'modelo', 'tipo_equipo', 'falla_reportada',
            'fecha_compra', 'tiene_garantia', 'garantia_hasta',
            'estado_fisico', 'accesorios',
        ]
        widgets = {
            'fecha_compra': forms.DateInput(attrs={'type': 'date'}),
            'garantia_hasta': forms.DateInput(attrs={'type': 'date'}),
            'falla_reportada': forms.Textarea(attrs={'rows': 3}),
            'estado_fisico': forms.Textarea(attrs={'rows': 3}),
        }

    def save(self, commit=True):
        equipo = super().save(commit=False)
        password = self.cleaned_data.get('password_equipo')
        if password:
            equipo.set_password_equipo(password)
        if commit:
            equipo.save()
        return equipo