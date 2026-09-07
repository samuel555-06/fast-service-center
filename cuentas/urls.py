from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.redireccionar_por_rol, name='home'),
    path('tecnicos/', views.gestionar_tecnicos, name='gestionar_tecnicos'),
    path('tecnicos/<int:tecnico_id>/toggle/', views.desactivar_tecnico, name='desactivar_tecnico'),
]