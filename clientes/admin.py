from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'cedula', 'telefono', 'creado_en')
    search_fields = ('nombre_completo', 'cedula')