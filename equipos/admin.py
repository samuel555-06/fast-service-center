from django.contrib import admin
from .models import Equipo, ReporteEstado, Evidencia


class ReporteEstadoInline(admin.TabularInline):
    model = ReporteEstado
    extra = 0
    readonly_fields = ('creado_en',)


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    readonly_fields = ('creado_en',)


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        'numero_orden', 'cliente', 'marca', 'modelo',
        'estado', 'tecnico_asignado', 'tiene_garantia', 'fecha_ingreso',
    )
    list_filter = ('estado', 'marca', 'tiene_garantia')
    search_fields = ('numero_orden', 'cliente__nombre_completo', 'cliente__cedula')
    readonly_fields = ('numero_orden', 'fecha_ingreso')
    inlines = [ReporteEstadoInline, EvidenciaInline]


@admin.register(ReporteEstado)
class ReporteEstadoAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'tecnico', 'creado_en')


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'subida_por', 'creado_en')