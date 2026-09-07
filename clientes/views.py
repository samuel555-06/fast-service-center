from django.shortcuts import render, redirect
from django.contrib import messages
from equipos.models import Equipo
from equipos.models import Consulta


def login_cliente(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        numero_orden = request.POST.get('numero_orden', '').strip().upper()

        equipo = Equipo.objects.filter(
            numero_orden=numero_orden,
            cliente__cedula=cedula,
        ).select_related('cliente').first()

        if equipo:
            # Guardamos la identidad del cliente en la sesión.
            request.session['cliente_id'] = equipo.cliente.id
            request.session['cliente_cedula'] = equipo.cliente.cedula
            return redirect('clientes:mis_equipos')

        messages.error(request, 'No encontramos un equipo con esa cédula y número de orden.')

    return render(request, 'clientes/login_cliente.html')


def logout_cliente(request):
    request.session.pop('cliente_id', None)
    request.session.pop('cliente_cedula', None)
    return redirect('clientes:login')

from .decorators import cliente_requerido
from .models import Cliente


@cliente_requerido
def mis_equipos(request):
    cliente = Cliente.objects.get(id=request.session['cliente_id'])
    equipos = cliente.equipos.all()
    return render(request, 'clientes/mis_equipos.html', {
        'cliente': cliente,
        'equipos': equipos,
    })
    
@cliente_requerido
def enviar_consulta(request, equipo_id):
    cliente = Cliente.objects.get(id=request.session['cliente_id'])
    equipo = cliente.equipos.filter(id=equipo_id).first()

    if not equipo:
        messages.error(request, 'No se encontró el equipo.')
        return redirect('clientes:mis_equipos')

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '').strip()
        if mensaje:
            Consulta.objects.create(equipo=equipo, mensaje=mensaje)
            messages.success(request, 'Tu consulta fue enviada. Te responderemos pronto.')

    return redirect('clientes:mis_equipos')