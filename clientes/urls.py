from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.login_cliente, name='login'),
    path('logout/', views.logout_cliente, name='logout'),
    path('mis-equipos/', views.mis_equipos, name='mis_equipos'),
    path('consulta/<int:equipo_id>/', views.enviar_consulta, name='enviar_consulta'),
]