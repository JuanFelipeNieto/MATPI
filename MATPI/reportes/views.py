from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from .services import generar_csv_general
from productos.models import Producto

@require_GET
def dashboard_reportes(request):
    """Renderiza la vista principal del dashboard de reportes."""
    productos = Producto.objects.all().order_by('nombre_producto')
    return render(request, 'reportes/dashboard_reportes.html', {'productos': productos})

def _procesar_logica_reporte(tipo_reporte, periodo):
    """Helper que maneja la lógica de generar el string según parámetros."""
    if tipo_reporte == 'general':
        return generar_csv_general(periodo)
    return None, None

@require_GET
def generar_reporte_csv(request):
    """Endpoint para descargar el CSV."""
    tipo_reporte = request.GET.get('tipo', 'general')
    periodo = request.GET.get('periodo', 'mensual')

    nombre_archivo, contenido = _procesar_logica_reporte(tipo_reporte, periodo)

    if not nombre_archivo:
        messages.error(request, 'Tipo de reporte inválido.')
        return redirect('dashboard_reportes')

    # Preparar la respuesta HTTP
    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
    )
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    response.write(contenido)
    return response

@require_POST
def enviar_reporte_correo(request):
    """Endpoint para enviar el reporte como adjunto por correo."""
    tipo_reporte = request.POST.get('tipo', 'general')
    periodo = request.POST.get('periodo', 'mensual')
    destinatario = request.POST.get('correo', 'admin@matpi.com')

    nombre_archivo, contenido = _procesar_logica_reporte(tipo_reporte, periodo)

    if not nombre_archivo:
        messages.error(request, 'Tipo de reporte inválido.')
        return redirect('dashboard_reportes')

    try:
        from_email = getattr(settings, 'EMAIL_HOST_USER', 'no-reply@matpi.com')

        email = EmailMessage(
            subject=f'MATPI: Reporte {tipo_reporte.capitalize()} ({periodo.capitalize()})',
            body=f'Hola,\n\nAdjunto encontrarás el reporte solicitado ({tipo_reporte.capitalize()} - {periodo.capitalize()}).',
            from_email=from_email,
            to=[destinatario],
        )
        email.attach(nombre_archivo, contenido, 'text/csv')
        email.send()

        messages.success(request, f'Reporte {tipo_reporte} enviado exitosamente a {destinatario}!')
    except Exception as e:
        messages.error(request, f'Error al enviar correo: {str(e)}')

    return redirect('dashboard_reportes')

@require_GET
def generar_reporte_pdf(request):
    """Endpoint para descargar el PDF de General/Específico."""
    tipo_reporte = request.GET.get('tipo', 'general')
    periodo = request.GET.get('periodo', 'mensual')

    from usuarios.views import generar_pdf
    from .services import obtener_contexto_general

    if tipo_reporte == 'general':
        ctx = obtener_contexto_general(periodo)
        contexto_pdf = {
            'titulo': 'Reporte General',
            'fecha': ctx['fecha_generada'],
            'vendedor': request.session.get('usuario_nombre', 'Sistema'),
            'datos_general': ctx
        }
        return generar_pdf('reportes/pdf_general.html', contexto_pdf, f"reporte_general_{periodo}")

    return redirect('dashboard_reportes')
