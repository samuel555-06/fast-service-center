from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet
from decouple import config

from clientes.models import Cliente


def _fernet():
    return Fernet(config('FERNET_KEY').encode())


class Equipo(models.Model):

    class Estado(models.TextChoices):
        INGRESADO = 'INGRESADO', 'Ingresado'
        MESA_TRABAJO = 'MESA_TRABAJO', 'Mesa de trabajo'
        REPARADO = 'REPARADO', 'Reparado'
        ENTREGADO = 'ENTREGADO', 'Entregado'

    numero_orden = models.CharField(max_length=20, unique=True, editable=False)

    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name='equipos'
    )
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='equipos_asignados'
    )

    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=100)
    tipo_equipo = models.CharField(max_length=60)  # laptop, PC escritorio, celular, etc.

    falla_reportada = models.TextField()
    fecha_compra = models.DateField(null=True, blank=True)

    tiene_garantia = models.BooleanField(default=False)
    garantia_hasta = models.DateField(null=True, blank=True)

    estado_fisico = models.TextField(
        help_text="Golpes, daño por agua, marcas visibles al ingresar"
    )
    accesorios = models.CharField(max_length=255, blank=True)

    # Contraseña del equipo, cifrada. Nunca se guarda en texto plano.
    _password_cifrada = models.BinaryField(null=True, blank=True)

    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.INGRESADO
    )

    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_mesa_trabajo = models.DateTimeField(null=True, blank=True)
    fecha_reparado = models.DateTimeField(null=True, blank=True)
    fecha_entregado = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_ingreso']

    def __str__(self):
        return f"{self.numero_orden} — {self.marca} {self.modelo}"

    def save(self, *args, **kwargs):
        if not self.numero_orden:
            self.numero_orden = self._generar_numero_orden()
        super().save(*args, **kwargs)

    @staticmethod
    def _generar_numero_orden():
        ultimo = Equipo.objects.order_by('id').last()
        siguiente = (ultimo.id + 1) if ultimo else 1
        return f"OT-{siguiente:05d}"

    def set_password_equipo(self, password_plano: str):
        if password_plano:
            self._password_cifrada = _fernet().encrypt(password_plano.encode())
        else:
            self._password_cifrada = None

    def get_password_equipo(self) -> str:
        if not self._password_cifrada:
            return ''
        return _fernet().decrypt(bytes(self._password_cifrada)).decode()

    @property
    def tiene_password(self):
        return bool(self._password_cifrada)


class ReporteEstado(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='reportes')
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Reporte de {self.equipo.numero_orden} — {self.creado_en:%d/%m/%Y}"


class Evidencia(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='evidencias')
    imagen = models.ImageField(upload_to='evidencias/%Y/%m/')
    descripcion = models.CharField(max_length=255, blank=True)
    subida_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia de {self.equipo.numero_orden}"


class Consulta(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='consultas')
    mensaje = models.TextField()
    respuesta = models.TextField(blank=True)
    respondida = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    respondida_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Consulta de {self.equipo.numero_orden} — {self.creado_en:%d/%m/%Y}"