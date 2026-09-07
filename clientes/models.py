from django.db import models


class Cliente(models.Model):
    cedula = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} ({self.cedula})"