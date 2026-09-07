from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .models import Usuario
from .forms import TecnicoForm


@login_required
def redireccionar_por_rol(request):
    """
    Después del login, cada rol va a su propio dashboard.
    """
    usuario = request.user
    if usuario.es_administrador():
        return redirect('equipos:dashboard_admin')
    return redirect('equipos:dashboard_tecnico')


def _es_admin(user):
    return user.is_authenticated and user.es_administrador()


@login_required
@user_passes_test(_es_admin)
def gestionar_tecnicos(request):
    tecnicos = Usuario.objects.filter(rol=Usuario.Rol.TECNICO)

    if request.method == 'POST':
        form = TecnicoForm(request.POST)
        if form.is_valid():
            tecnico = form.save()
            messages.success(request, f'Cuenta creada para {tecnico.get_full_name()}.')
            return redirect('cuentas:gestionar_tecnicos')
    else:
        form = TecnicoForm()

    return render(request, 'cuentas/gestionar_tecnicos.html', {
        'form': form,
        'tecnicos': tecnicos,
        'back_url': reverse('equipos:dashboard_admin'),
    })


@login_required
@user_passes_test(_es_admin)
def desactivar_tecnico(request, tecnico_id):
    tecnico = Usuario.objects.get(id=tecnico_id, rol=Usuario.Rol.TECNICO)
    if request.method == 'POST':
        tecnico.is_active = not tecnico.is_active
        tecnico.save()
        estado = 'activada' if tecnico.is_active else 'desactivada'
        messages.success(request, f'Cuenta de {tecnico.get_full_name()} {estado}.')
    return redirect('cuentas:gestionar_tecnicos')