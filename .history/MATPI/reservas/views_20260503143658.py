# pylint: disable=no-member
from django.shortcuts import render, redirect
from django.db import DatabaseError
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from contextlib import suppress
import re
from datetime import datetime
from django.core.paginator import Paginator
from .models import Reserva
from usuarios.models import Cajero
from clientes.models import Cliente


def listar_reservas(request, edit_id=None):
    # Auto-eliminación de reservas pasadas al acceder al listado
    with suppress(DatabaseError):
        Reserva.objects.filter(fecha__lt=timezone.now()).delete()
    
    buscar = request.GET.get('buscar', '')
    try:
        if buscar:
            reservas_list = Reserva.objects.filter(
                Q(cliente__nombre_completo__icontains=buscar) |
                Q(cliente__id__icontains=buscar)
            ).order_by('-fecha')
        else:
            reservas_list = Reserva.objects.all().order_by('-fecha')
    except Exception:
        reservas_list = []
        
    paginator = Paginator(reservas_list, 4)
    page_number = request.GET.get('page')
    reservas = paginator.get_page(page_number)
    
    clientes = Cliente.objects.all()
    ahora = timezone.now()
    
    context = {
        'reservas': reservas, 
        'buscar': buscar,
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


def registrar_reserva(request):
    if request.method == 'POST':
        fecha_str     = request.POST.get('txt_fecha')
        
        # Validación de fecha
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
            if timezone.is_naive(fecha_dt):
                fecha_dt = timezone.make_aware(fecha_dt)
                
            if fecha_dt < timezone.now():
                messages.error(request, "La fecha de reserva no puede ser anterior a la actual.")
                return redirect('listar_reservas')
        except (ValueError, TypeError):
            messages.error(request, "Formato de fecha inválido o vacío.")
            return redirect('listar_reservas')
            
        estado        = request.POST.get('txt_estado', '1') == '1'
        observaciones = request.POST.get('txt_observaciones')
        cliente_text  = request.POST.get('txt_cliente_text')
        
        # Extraer el ID del formato "Nombre (ID)"
        cliente_id = None
        if cliente_text:
            match = re.search(r'\((\d+)\)$', cliente_text)
            if match:
                cliente_id = match.group(1)
        
        try:
            cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        except Cliente.DoesNotExist:
            messages.error(request, "El cliente seleccionado no existe.")
            return redirect('listar_reservas')

        # Asignación automática del cajero basada en la sesión del usuario actual
        usuario_id = request.session.get('usuario_id')
        cajero = None
        if usuario_id:
            try:
                cajero = Cajero.objects.get(pk=usuario_id)
            except Cajero.DoesNotExist:
                pass

        try:
            Reserva.objects.create(
                fecha=fecha_dt,
                estado=estado,
                observaciones=observaciones,
                cliente=cliente,
                cajero=cajero,
            )
            messages.success(request, "Reserva creada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al crear la reserva: {str(e)}")
            
        return redirect('listar_reservas')
    return redirect('listar_reservas')


def pre_editar_reserva(request, id):
    return listar_reservas(request, edit_id=id)


def editar_reserva(request):
    if request.method == 'POST':
        id            = request.POST.get('txt_id')
        fecha_str     = request.POST.get('txt_fecha')
        
        # Validación de fecha
        try:
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
            if timezone.is_naive(fecha_dt):
                fecha_dt = timezone.make_aware(fecha_dt)
                
            if fecha_dt < timezone.now():
                messages.error(request, "La fecha de reserva no puede ser anterior a la actual.")
                return redirect('pre_editar_reserva', id=id)
        except (ValueError, TypeError):
            messages.error(request, "Formato de fecha inválido o vacío.")
            return redirect('pre_editar_reserva', id=id)

        estado        = request.POST.get('txt_estado', '1') == '1'
        observaciones = request.POST.get('txt_observaciones')
        cliente_text  = request.POST.get('txt_cliente_text')
        
        # Extraer el ID del formato "Nombre (ID)"
        cliente_id = None
        if cliente_text:
            match = re.search(r'\((\d+)\)$', cliente_text)
            if match:
                cliente_id = match.group(1)
        
        try:
            cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        except Cliente.DoesNotExist:
            messages.error(request, "El cliente seleccionado no existe.")
            return redirect('pre_editar_reserva', id=id)
            
        try:
            reserva = Reserva.objects.get(pk=id)
            reserva.fecha         = fecha_dt
            reserva.estado        = estado
            reserva.observaciones = observaciones
            reserva.cliente       = cliente
            reserva.save()
            messages.success(request, "Reserva actualizada exitosamente.")
        except Reserva.DoesNotExist:
            messages.error(request, "La reserva no existe.")
        except Exception as e:
            messages.error(request, f"Error al actualizar la reserva: {str(e)}")
            
    return redirect('listar_reservas')


def eliminar_reserva(request, id):
    try:
        Reserva.objects.get(pk=id).delete()
        messages.success(request, "Reserva eliminada exitosamente.")
    except Reserva.DoesNotExist:
        messages.error(request, "La reserva no existe.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la reserva: {str(e)}")
    return redirect('listar_reservas')
