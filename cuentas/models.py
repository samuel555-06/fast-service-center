from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UsuarioManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('rol', Usuario.Rol.ADMINISTRADOR)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Extiende el usuario de Django para el personal del taller
    (administradores y técnicos). Los clientes NO usan este modelo,
    ellos se autentican por cédula + número de orden (ver app clientes).
    """

    class Rol(models.TextChoices):
        ADMINISTRADOR = 'ADMIN', 'Administrador'
        TECNICO = 'TECNICO', 'Técnico'

    rol = models.CharField(
        max_length=10,
        choices=Rol.choices,
        default=Rol.TECNICO,
    )
    telefono = models.CharField(max_length=20, blank=True)

    objects = UsuarioManager()

    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR

    def es_tecnico(self):
        return self.rol == self.Rol.TECNICO

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"