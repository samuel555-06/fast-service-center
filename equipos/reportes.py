from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from collections import Counter
from reportlab.platypus import Image
from django.conf import settings
from .categorias_falla import clasificar_falla
from django.utils import timezone

def generar_reporte_cliente_pdf(equipo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'TituloTaller', parent=styles['Title'],
        fontSize=18, spaceAfter=4,
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#5C6B7D'), spaceAfter=20,
    )
    seccion_style = ParagraphStyle(
        'Seccion', parent=styles['Heading2'],
        fontSize=12, spaceBefore=16, spaceAfter=8,
        textColor=colors.HexColor('#1B2A3D'),
    )

    story = []

    story.append(Paragraph("Taller Familiar", titulo_style))
    story.append(Paragraph("Reporte de servicio técnico", subtitulo_style))

    # --- Datos generales ---
    datos_generales = [
        ['Número de orden', equipo.numero_orden],
        ['Cliente', equipo.cliente.nombre_completo],
        ['Cédula', equipo.cliente.cedula],
        ['Equipo', f"{equipo.marca} {equipo.modelo}"],
        ['Fecha de ingreso', equipo.fecha_ingreso.strftime('%d/%m/%Y')],
        ['Estado actual', equipo.get_estado_display()],
    ]
    if equipo.fecha_entregado:
        datos_generales.append(['Fecha de entrega', equipo.fecha_entregado.strftime('%d/%m/%Y')])

    tabla_datos = Table(datos_generales, colWidths=[5*cm, 10*cm])
    tabla_datos.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#5C6B7D')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#DAD5CA')),
    ]))
    story.append(tabla_datos)

    # --- Falla reportada ---
    story.append(Paragraph("Falla reportada", seccion_style))
    story.append(Paragraph(equipo.falla_reportada, styles['Normal']))

    # --- Estado físico al ingresar ---
    story.append(Paragraph("Estado físico al ingresar", seccion_style))
    story.append(Paragraph(equipo.estado_fisico, styles['Normal']))

    # --- Garantía ---
    story.append(Paragraph("Garantía", seccion_style))
    if equipo.tiene_garantia:
        texto_garantia = "Equipo con garantía vigente"
        if equipo.garantia_hasta:
            texto_garantia += f" hasta {equipo.garantia_hasta.strftime('%d/%m/%Y')}"
        story.append(Paragraph(texto_garantia, styles['Normal']))
    else:
        story.append(Paragraph("Equipo sin garantía", styles['Normal']))

    # --- Historial de reportes de avance ---
    reportes = equipo.reportes.all()
    if reportes:
        story.append(Paragraph("Historial de reportes de avance", seccion_style))
        for reporte in reportes:
            fecha = reporte.creado_en.strftime('%d/%m/%Y %H:%M')
            texto = f"<b>{fecha}</b> — {reporte.descripcion}"
            story.append(Paragraph(texto, styles['Normal']))
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"reporte_{equipo.numero_orden}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def generar_reporte_marca_pdf(marca, equipos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=2*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        'TituloTaller', parent=styles['Title'], fontSize=18, spaceAfter=4,
    )
    subtitulo_style = ParagraphStyle(
        'Subtitulo', parent=styles['Normal'], fontSize=10,
        textColor=colors.HexColor('#5C6B7D'), spaceAfter=20,
    )
    seccion_style = ParagraphStyle(
        'Seccion', parent=styles['Heading2'], fontSize=13,
        spaceBefore=18, spaceAfter=8, textColor=colors.HexColor('#1B2A3D'),
    )
    caso_style = ParagraphStyle(
        'Caso', parent=styles['Heading3'], fontSize=11,
        spaceBefore=14, spaceAfter=4, textColor=colors.HexColor('#1B2A3D'),
    )

    story = []
    story.append(Paragraph(f"Reporte de fallas — {marca}", titulo_style))
    story.append(Paragraph(
        f"Taller Familiar · Período: últimos 30 días · Generado el {timezone.now().strftime('%d/%m/%Y')}",
        subtitulo_style
    ))

    # --- Resumen estadístico ---
    story.append(Paragraph("Resumen estadístico de fallas", seccion_style))

    conteo = Counter(clasificar_falla(e.tipo_equipo, e.falla_reportada) for e in equipos)
    total = sum(conteo.values())

    if total == 0:
        story.append(Paragraph(
            "No se registraron equipos de esta marca en el período indicado.",
            styles['Normal']
        ))
    else:
        filas = [['Tipo de falla', 'Cantidad', '% del total']]
        for categoria, cantidad in conteo.most_common():
            porcentaje = f"{(cantidad / total * 100):.0f}%"
            filas.append([categoria, str(cantidad), porcentaje])

        tabla = Table(filas, colWidths=[8*cm, 4*cm, 4*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B2A3D')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#DAD5CA')),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(tabla)
        story.append(Paragraph(
            f"Total de equipos {marca} atendidos en el período: {total}",
            styles['Normal']
        ))

    # --- Detalle de casos con evidencias ---
    if equipos:
        story.append(Paragraph("Detalle de casos", seccion_style))

        for equipo in equipos:
            categoria = clasificar_falla(equipo.tipo_equipo, equipo.falla_reportada)
            story.append(Paragraph(
                f"{equipo.numero_orden} — {equipo.modelo} ({categoria})",
                caso_style
            ))
            story.append(Paragraph(equipo.falla_reportada, styles['Normal']))
            story.append(Spacer(1, 6))

            evidencias = list(equipo.evidencias.all())[:2]  # máximo 2 fotos por caso
            for evidencia in evidencias:
                try:
                    ruta_imagen = settings.MEDIA_ROOT / str(evidencia.imagen)
                    img = Image(str(ruta_imagen), width=6*cm, height=4.5*cm)
                    story.append(img)
                    story.append(Spacer(1, 4))
                except Exception:
                    pass  # si la imagen no se puede cargar, se omite sin romper el PDF

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"reporte_{marca}_{timezone.now().strftime('%Y%m')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

