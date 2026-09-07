from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from clientes.models import Cliente
from cuentas.models import Usuario
from .models import Equipo, ReporteEstado, Evidencia
from .forms import ClienteForm, EquipoForm
from .reportes import generar_reporte_cliente_pdf, generar_reporte_marca_pdf
from datetime import timedelta
from django.db.models import Count
from .models import Consulta


def _es_admin(user):
    return user.is_authenticated and user.es_administrador()


def _es_tecnico(user):
    return user.is_authenticated and user.es_tecnico()


@login_required
@user_passes_test(_es_admin)
def dashboard_admin(request):
    equipos = Equipo.objects.select_related('cliente', 'tecnico_asignado').exclude(
        estado='ENTREGADO'
    )
    return render(request, 'equipos/dashboard_admin.html', {'equipos': equipos})


@login_required
@user_passes_test(_es_admin)
def ingresar_equipo(request):
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        cliente = Cliente.objects.filter(cedula=cedula).first()

        cliente_form = ClienteForm(request.POST, instance=cliente)
        equipo_form = EquipoForm(request.POST)

        if cliente_form.is_valid() and equipo_form.is_valid():
            cliente = cliente_form.save()
            equipo = equipo_form.save(commit=False)
            equipo.cliente = cliente
            equipo.save()
            messages.success(request, f'Equipo ingresado con orden {equipo.numero_orden}.')
            return redirect('equipos:dashboard_admin')
    else:
        cliente_form = ClienteForm()
        equipo_form = EquipoForm()

    return render(request, 'equipos/ingresar_equipo.html', {
        'cliente_form': cliente_form,
        'equipo_form': equipo_form,
        'back_url': reverse('equipos:dashboard_admin'),
    })


@login_required
@user_passes_test(_es_admin)
def transferir_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    tecnicos = Usuario.objects.filter(rol=Usuario.Rol.TECNICO, is_active=True)

    if request.method == 'POST':
        tecnico_id = request.POST.get('tecnico_id')
        tecnico = get_object_or_404(Usuario, id=tecnico_id, rol=Usuario.Rol.TECNICO)
        equipo.tecnico_asignado = tecnico
        equipo.estado = Equipo.Estado.MESA_TRABAJO
        equipo.fecha_mesa_trabajo = timezone.now()
        equipo.save()
        messages.success(request, f'{equipo.numero_orden} fue transferido a {tecnico.get_full_name() or tecnico.username}.')
        return redirect('equipos:dashboard_admin')

    return render(request, 'equipos/transferir_equipo.html', {
        'equipo': equipo,
        'tecnicos': tecnicos,
        'back_url': reverse('equipos:dashboard_admin'),
    })


@login_required
@user_passes_test(_es_admin)
def notificar_cliente(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)

    if request.method == 'POST':
        equipo.estado = Equipo.Estado.ENTREGADO
        equipo.fecha_entregado = timezone.now()
        equipo.save()
        messages.success(request, f'Cliente notificado. {equipo.numero_orden} marcado como entregado.')
        return redirect('equipos:dashboard_admin')

    return render(request, 'equipos/notificar_cliente.html', {
        'equipo': equipo,
        'back_url': reverse('equipos:dashboard_admin'),
    })


@login_required
@user_passes_test(_es_tecnico)
def dashboard_tecnico(request):
    equipos = Equipo.objects.filter(
        tecnico_asignado=request.user
    ).exclude(estado='ENTREGADO').select_related('cliente')
    return render(request, 'equipos/dashboard_tecnico.html', {'equipos': equipos})


@login_required
def detalle_equipo(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    if request.user.es_tecnico() and equipo.tecnico_asignado_id != request.user.id:
        messages.error(request, 'No tienes acceso a ese equipo.')
        return redirect('equipos:dashboard_tecnico')

    equipo_password = equipo.get_password_equipo() if equipo.tiene_password else ''

    destino = 'equipos:dashboard_admin' if request.user.es_administrador() else 'equipos:dashboard_tecnico'
    return render(request, 'equipos/detalle_equipo.html', {
        'equipo': equipo,
        'equipo_password': equipo_password,
        'back_url': reverse(destino),
    })


@login_required
@user_passes_test(_es_tecnico)
def adjuntar_evidencia(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id, tecnico_asignado=request.user)
    if request.method == 'POST' and request.FILES.get('imagen'):
        Evidencia.objects.create(
            equipo=equipo,
            imagen=request.FILES['imagen'],
            descripcion=request.POST.get('descripcion', ''),
            subida_por=request.user,
        )
        messages.success(request, 'Evidencia adjuntada.')
    return redirect('equipos:detalle_equipo', equipo_id=equipo.id)


@login_required
@user_passes_test(_es_tecnico)
def agregar_reporte(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id, tecnico_asignado=request.user)
    if request.method == 'POST' and request.POST.get('descripcion'):
        ReporteEstado.objects.create(
            equipo=equipo,
            tecnico=request.user,
            descripcion=request.POST['descripcion'],
        )
        messages.success(request, 'Reporte de estado guardado.')
    return redirect('equipos:detalle_equipo', equipo_id=equipo.id)


@login_required
@user_passes_test(_es_tecnico)
def notificar_reparado(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id, tecnico_asignado=request.user)
    if request.method == 'POST':
        equipo.estado = Equipo.Estado.REPARADO
        equipo.fecha_reparado = timezone.now()
        equipo.save()
        messages.success(request, f'{equipo.numero_orden} notificado como reparado al administrador.')
    return redirect('equipos:dashboard_tecnico')

@login_required
@user_passes_test(_es_admin)
def descargar_reporte_cliente(request, equipo_id):
    equipo = get_object_or_404(Equipo, id=equipo_id)
    return generar_reporte_cliente_pdf(equipo)

@login_required
@user_passes_test(_es_admin)
def reportes_marcas(request):
    hace_un_mes = timezone.now() - timedelta(days=30)
    marcas = (
        Equipo.objects
        .filter(fecha_ingreso__gte=hace_un_mes)
        .values('marca')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    return render(request, 'equipos/reportes_marcas.html', {
        'marcas': marcas,
        'back_url': reverse('equipos:dashboard_admin'),
    })


@login_required
@user_passes_test(_es_admin)
def descargar_reporte_marca(request, marca):
    hace_un_mes = timezone.now() - timedelta(days=30)
    equipos = Equipo.objects.filter(
        marca=marca, fecha_ingreso__gte=hace_un_mes
    ).select_related('cliente').prefetch_related('evidencias')
    return generar_reporte_marca_pdf(marca, equipos)

@login_required
@user_passes_test(_es_admin)
def consultas_clientes(request):
    consultas = Consulta.objects.select_related('equipo', 'equipo__cliente').all()
    return render(request, 'equipos/consultas_clientes.html', {
        'consultas': consultas,
        'back_url': reverse('equipos:dashboard_admin'),
    })


@login_required
@user_passes_test(_es_admin)
def responder_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    if request.method == 'POST':
        respuesta = request.POST.get('respuesta', '').strip()
        if respuesta:
            consulta.respuesta = respuesta
            consulta.respondida = True
            consulta.respondida_en = timezone.now()
            consulta.save()
            messages.success(request, 'Respuesta enviada al cliente.')
    return redirect('equipos:consultas_clientes')