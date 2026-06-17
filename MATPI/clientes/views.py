from django.shortcuts import render, redirect
from .models import Cliente
from usuarios.models import Cajero, Administrador
from .servicices import obtener_localidades
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods, require_GET

# Función auxiliar para validar si el ID en sesión es Administrador
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

@require_GET
def listar_clientes(request):
    buscar = request.GET.get('buscar', '')
    localidad_filtro = request.GET.get('localidad', '')

    clientes = Cliente.objects.annotate(total_pedidos=Count('pedidos')).order_by('nombre_completo')

    if buscar:
        clientes = clientes.filter(
            Q(id__icontains=buscar) |
            Q(nombre_completo__icontains=buscar)
        )

    if localidad_filtro:
        clientes = clientes.filter(localidad=localidad_filtro)

    from django.core.paginator import Paginator
    paginator = Paginator(clientes, 10)
    page_number = request.GET.get('page')
    clientes_paginated = paginator.get_page(page_number)

    localidades = obtener_localidades()

    data = {
        'clientes': clientes_paginated,
        'buscar': buscar,
        'localidad_filtro': localidad_filtro,
        'localidades': localidades,
        'es_admin': check_admin(request)
    }
    return render(request, 'clientes/listar.html', data)


@require_GET
def mostrar_registro_cliente(request):
    localidades = obtener_localidades()
    return render(request, 'clientes/registrar.html', {'localidades': localidades})


def _validar_datos_cliente(cliente_id, nombre, telefono):
    if cliente_id and len(cliente_id) != 10:
        raise ValueError("El número de documento debe tener exactamente 10 caracteres.")
    if nombre and len(nombre) < 3:
        raise ValueError("El nombre no puede tener menos de 3 caracteres.")
    if telefono and len(telefono) < 6:
        raise ValueError("El teléfono no puede tener menos de 6 caracteres.")

def _obtener_usuario_registrador(usuario_id):
    if not usuario_id:
        return None
    from usuarios.models import Usuario
    try:
        return Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return None

def _actualizar_usuario_cajero(cliente, usuario_id_post):
    if usuario_id_post:
        from usuarios.models import Usuario
        try:
            cliente.usuario = Usuario.objects.get(pk=usuario_id_post)
        except Usuario.DoesNotExist:
            pass
    else:
        cliente.usuario = None

@require_http_methods(["GET", "POST"])
def registrar_cliente(request):
    if request.method != 'POST':
        return redirect('mostrar_registro_cliente')

    cliente_id = request.POST.get('txt_id', '')
    nombre = request.POST.get('txt_nombre', '')
    telefono = request.POST.get('txt_telefono', '')
    direccion = request.POST.get('txt_direccion', '')
    localidad = request.POST.get('txt_localidad', '')
    try:
        from django.contrib import messages
        _validar_datos_cliente(cliente_id, nombre, telefono)
        usuario_registrador = _obtener_usuario_registrador(request.session.get('usuario_id'))

        Cliente.objects.create(
            id=cliente_id,
            nombre_completo=nombre,
            telefono=telefono,
            direccion=direccion,
            localidad=localidad,
            usuario=usuario_registrador,
        )
        messages.success(request, f"Cliente {nombre} registrado correctamente.")
        return redirect('listar_clientes')
    except ValueError as e:
        from django.contrib import messages
        messages.error(request, str(e))
        localidades = obtener_localidades()
        datos = {
            'id': cliente_id,
            'nombre': nombre,
            'telefono': telefono,
            'direccion': direccion,
            'localidad': localidad,
        }
        return render(request, 'clientes/registrar.html', {
            'localidades': localidades,
            'datos': datos
        })


@require_GET
def pre_editar_cliente(request, id):
    cajeros = Cajero.objects.all()
    cliente = Cliente.objects.get(pk=id)
    localidades = obtener_localidades()
    es_admin = check_admin(request)
    data = {
        'cliente': cliente,
        'cajeros': cajeros,
        'localidades': localidades,
        'es_admin': es_admin
    }
    return render(request, 'clientes/editar.html', data)


@require_http_methods(["GET", "POST"])
def editar_cliente(request):
    if request.method != 'POST':
        return redirect('listar_clientes')

    try:
        from django.contrib import messages
        cliente_id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        telefono = request.POST.get('txt_telefono')
        direccion = request.POST.get('txt_direccion')
        localidad = request.POST.get('txt_localidad')

        _validar_datos_cliente(None, nombre, telefono)

        cliente = Cliente.objects.get(pk=cliente_id)
        cliente.nombre_completo = nombre
        cliente.telefono = telefono
        cliente.direccion = direccion
        cliente.localidad = localidad

        cliente.save()
        messages.success(request, f"Cliente {nombre} actualizado correctamente.")
        return redirect('listar_clientes')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('pre_editar_cliente', id=request.POST.get('txt_id'))


@require_http_methods(["GET", "POST"])
def eliminar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    cliente.delete()
    return redirect('listar_clientes')
