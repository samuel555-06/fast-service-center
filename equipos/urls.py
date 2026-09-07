from django.urls import path
from . import views

app_name = 'equipos'

urlpatterns = [
    path('admin/', views.dashboard_admin, name='dashboard_admin'),
    path('admin/ingresar/', views.ingresar_equipo, name='ingresar_equipo'),
    path('admin/transferir/<int:equipo_id>/', views.transferir_equipo, name='transferir_equipo'),
    path('admin/notificar/<int:equipo_id>/', views.notificar_cliente, name='notificar_cliente'),
    path('tecnico/', views.dashboard_tecnico, name='dashboard_tecnico'),
    path('detalle/<int:equipo_id>/', views.detalle_equipo, name='detalle_equipo'),
    path('evidencia/<int:equipo_id>/', views.adjuntar_evidencia, name='adjuntar_evidencia'),
    path('reporte/<int:equipo_id>/', views.agregar_reporte, name='agregar_reporte'),
    path('notificar-reparado/<int:equipo_id>/', views.notificar_reparado, name='notificar_reparado'),
    path('reporte-cliente/<int:equipo_id>/', views.descargar_reporte_cliente, name='descargar_reporte_cliente'),
    path('reportes-marcas/', views.reportes_marcas, name='reportes_marcas'),
    path('reportes-marcas/<str:marca>/descargar/', views.descargar_reporte_marca, name='descargar_reporte_marca'),
    path('consultas/', views.consultas_clientes, name='consultas_clientes'),
    path('consultas/<int:consulta_id>/responder/', views.responder_consulta, name='responder_consulta'),
]