from django.shortcuts import render, redirect
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
import re
from datetime import datetime
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods, require_GET
from .models import Reserva
from usuarios.models import Cajero
from clientes.models import Cliente


@require_GET
def listar_reservas(request, edit_id=None):
    # Auto-eliminación de reservas pasadas al acceder al listado
    Reserva.objects.filter(fecha__lt=timezone.now()).delete()

    buscar = request.GET.get('buscar', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')

    reservas_list = Reserva.objects.all()

    if buscar:
        reservas_list = reservas_list.filter(
            Q(cliente__nombre_completo__icontains=buscar) |
            Q(cliente__id__icontains=buscar)
        )

    if fecha_desde:
        try:
            desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            desde_dt = timezone.make_aware(desde_dt)
            if desde_dt.date() < timezone.localdate():
                messages.error(request, "No se puede buscar una fecha menor a la actual.")
                return redirect('listar_reservas')
            reservas_list = reservas_list.filter(fecha__gte=desde_dt)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            hasta_dt = hasta_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            hasta_dt = timezone.make_aware(hasta_dt)
            if hasta_dt.date() < timezone.localdate():
                messages.error(request, "No se puede buscar una fecha menor a la actual.")
                return redirect('listar_reservas')
            reservas_list = reservas_list.filter(fecha__lte=hasta_dt)
        except ValueError:
            pass

    reservas_list = reservas_list.order_by('-fecha')

    paginator = Paginator(reservas_list, 4)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)

    clientes = Cliente.objects.all()
    ahora = timezone.now()

    context = {
        'reservas': reservas,
        'buscar': buscar,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'clientes': clientes,
        'ahora': ahora
    }

    if edit_id:
        try:
            reserva_edit = Reserva.objects.get(pk=edit_id)
            context['reserva_edit'] = reserva_edit
        except Reserva.DoesNotExist:
            pass

    return render(request, 'reservas/listar.html', context)


def _validar_fecha_reserva(fecha_str):
    if not fecha_str:
        raise ValueError("La fecha de reserva es requerida.")

    fecha_dt = None
    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            fecha_dt = datetime.strptime(fecha_str, fmt)
            break
        except ValueError:
            pass

    if not fecha_dt:
        raise ValueError("El formato de fecha no es válido.")

    if timezone.is_naive(fecha_dt):
        fecha_dt = timezone.make_aware(fecha_dt)

    if fecha_dt < timezone.now():
        raise ValueError("La fecha de reserva no puede ser anterior a la actual.")

    if fecha_dt.hour < 11 or fecha_dt.hour > 19 or (fecha_dt.hour == 19 and fecha_dt.minute > 0):
        raise ValueError("Las reservas solo están permitidas entre las 11:00 AM y las 7:00 PM.")

    return fecha_dt

def _obtener_cliente_id_desde_texto(cliente_text):
    if cliente_text:
        match = re.search(r'\((\d+)\)$', cliente_text)
        if match:
            return match.group(1)
    return None

def _obtener_cajero_reserva(usuario_id):
    if usuario_id:
        try:
            return Cajero.objects.get(pk=usuario_id)
        except Cajero.DoesNotExist:
            pass
    return None


@require_http_methods(["GET", "POST"])
def registrar_reserva(request):
    if request.method != 'POST':
        return redirect('listar_reservas')

    fecha_str = request.POST.get('txt_fecha')
    try:
        fecha_dt = _validar_fecha_reserva(fecha_str)
        if not fecha_dt:
            return redirect('listar_reservas')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('listar_reservas')

    estado        = request.POST.get('txt_estado', '1') == '1'
    observaciones = request.POST.get('txt_observaciones')
    cliente_text  = request.POST.get('txt_cliente_text')

    if not observaciones or not observaciones.strip():
        observaciones = "ninguna"
    else:
        observaciones = observaciones.strip()

    cliente_id = _obtener_cliente_id_desde_texto(cliente_text)
    cajero = _obtener_cajero_reserva(request.session.get('usuario_id'))
    cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None

    Reserva.objects.create(
        fecha=fecha_dt,
        estado=estado,
        observaciones=observaciones,
        cliente=cliente,
        cajero=cajero,
    )
    return redirect('listar_reservas')


@require_GET
def pre_editar_reserva(request, id):
    return listar_reservas(request, edit_id=id)


@require_http_methods(["GET", "POST"])
def editar_reserva(request):
    if request.method != 'POST':
        return redirect('listar_reservas')

    reserva_id = request.POST.get('txt_id')
    fecha_str  = request.POST.get('txt_fecha')

    try:
        fecha_dt = _validar_fecha_reserva(fecha_str)
        if not fecha_dt:
            return redirect('pre_editar_reserva', id=reserva_id)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('pre_editar_reserva', id=reserva_id)

    estado        = request.POST.get('txt_estado', '1') == '1'
    observaciones = request.POST.get('txt_observaciones')
    cliente_text  = request.POST.get('txt_cliente_text')

    if not observaciones or not observaciones.strip():
        observaciones = "ninguna"
    else:
        observaciones = observaciones.strip()

    cliente_id = _obtener_cliente_id_desde_texto(cliente_text)
    cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None

    reserva = Reserva.objects.get(pk=reserva_id)
    reserva.fecha         = fecha_dt
    reserva.estado        = estado
    reserva.observaciones = observaciones
    reserva.cliente       = cliente
    reserva.save()

    return redirect('listar_reservas')


@require_http_methods(["GET", "POST"])
def eliminar_reserva(request, id):
    Reserva.objects.get(pk=id).delete()
    return redirect('listar_reservas')
