from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_GET
from .models import Producto
from materia_prima.models import MateriaPrima, DetalleProductoMateriaP
from usuarios.models import Administrador
import math

MATERIA_ID_KEY = 'materia_id[]'
MATERIA_CANTIDAD_KEY = 'materia_cantidad[]'
MATERIA_UNIDAD_KEY = 'materia_unidad[]'

# Función rápida para verificar si es admin desde la sesión
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def recalcular_stock_producto(producto):
    detalles = producto.detalles_materia.all()
    if not detalles:
        producto.cantidad = 0
        producto.descripcion = "Sin composición definida"
        producto.save()
        return 0

    cantidades_posibles = []
    componentes_desc = []

    for detalle in detalles:
        stock_mp = detalle.materia_prima.stock_total
        equivalencia = detalle.materia_prima.cantidad_por_unidad
        
        # Si es bebida, el stock base es directamente stock_mp (stock total en unidades/botellas) y no su equivalencia
        if producto.categoria == 'Bebidas' or detalle.materia_prima.tipo == 'Bebida':
            stock_base = stock_mp
        else:
            stock_base = stock_mp * equivalencia

        # La cantidad usada ahora siempre viene en medida base desde el frontend
        cantidad_usada_base = detalle.cantidad_usada

        if cantidad_usada_base > 0:
            posible = int(stock_base / cantidad_usada_base)
            cantidades_posibles.append(posible)
            # Para visualización legible
            if producto.categoria == 'Bebidas' or detalle.materia_prima.tipo == 'Bebida':
                cant_legible = float(cantidad_usada_base)
            else:
                cant_legible = float(cantidad_usada_base / equivalencia) if equivalencia > 0 else float(cantidad_usada_base)
            componentes_desc.append(f"{detalle.materia_prima.nombre_materia_prima} ({cant_legible} {detalle.unidad_medida})")

    # El stock del producto es el limitante (mínimo de los ingredientes)
    stock_final = min(cantidades_posibles) if cantidades_posibles else 0
    producto.cantidad = stock_final
    producto.descripcion = ", ".join(componentes_desc)
    producto.save()
    return producto.cantidad

# --- VISTA PRINCIPAL (LISTADO) ---

@require_GET
def listar_productos(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return redirect('login')

    es_admin = check_admin(request)
    query = request.GET.get('buscar', '')
    categoria = request.GET.get('categoria', '')
    ordenar = request.GET.get('ordenar', '')

    from django.db.models import Exists, OuterRef
    from facturas.models import Factura

    productos = Producto.objects.annotate(
        asociado_factura=Exists(Factura.objects.filter(pedido__detalles__producto=OuterRef('pk')))
    ).prefetch_related('detalles_materia__materia_prima')

    if query:
        productos = productos.filter(nombre_producto__icontains=query)

    if categoria:
        productos = productos.filter(categoria=categoria)

    sorting_map = {
        'nombre_asc': 'nombre_producto',
        'nombre_desc': '-nombre_producto',
        'fecha_desc': '-id',
        'fecha_asc': 'id',
        'stock_desc': '-cantidad',
        'stock_asc': 'cantidad',
        'precio_desc': '-precio',
        'precio_asc': 'precio',
    }

    if ordenar not in sorting_map:
        ordenar = 'fecha_desc'
    order_field = sorting_map[ordenar]

    productos = productos.order_by(order_field)

    from django.core.paginator import Paginator
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    productos_paginated = paginator.get_page(page_number)

    return render(request, 'productos/listar.html', {
        'productos': productos_paginated,
        'es_admin': es_admin,
        'buscar': query,
        'categoria': categoria,
        'ordenar': ordenar,
        'categorias': Producto.CATEGORIAS,
    })


@require_GET
def mostrar_registro_comida(request):
    if not request.session.get('usuario_id'): return redirect('login')
    es_admin = check_admin(request)
    if not es_admin:
        messages.error(request, "Solo el administrador puede registrar productos.")
        return redirect('listar_productos')

    materias_primas = MateriaPrima.objects.filter(tipo='Comida')
    return render(request, 'productos/registrar_comida.html', {
        'es_admin': es_admin,
        'materias_primas': materias_primas
    })

@require_GET
def mostrar_registro_bebida(request):
    if not request.session.get('usuario_id'): return redirect('login')
    es_admin = check_admin(request)
    if not es_admin:
        messages.error(request, "Solo el administrador puede registrar productos.")
        return redirect('listar_productos')

    # Obtenemos los IDs y nombres de bebidas ya registradas para excluirlas de la lista
    materias_usadas_ids = DetalleProductoMateriaP.objects.filter(
        producto__categoria='Bebidas'
    ).values_list('materia_prima_id', flat=True)

    nombres_bebidas = Producto.objects.filter(categoria='Bebidas').values_list('nombre_producto', flat=True)

    materias_primas = MateriaPrima.objects.filter(tipo='Bebida').exclude(id__in=materias_usadas_ids).exclude(nombre_materia_prima__in=nombres_bebidas)

    return render(request, 'productos/registrar_bebida.html', {
        'es_admin': es_admin,
        'materias_primas': materias_primas
    })


def _validar_imagen_y_obtener_extension(imagen):
    if imagen:
        ext = imagen.name.split('.')[-1].lower()
        if ext not in ['png', 'jpg', 'jpeg']:
            raise ValueError("Solo se permiten imágenes en formato JPG o PNG.")

def _guardar_composicion_producto(producto, materias_ids, materias_cantidades, materias_unidades, materias_prioridades=None):
    if not materias_prioridades or len(materias_prioridades) != len(materias_ids):
        materias_prioridades = ['0'] * len(materias_ids)

    for m_id, m_cant, m_uni, m_prio in zip(materias_ids, materias_cantidades, materias_unidades, materias_prioridades):
        if m_id and m_cant:
            from decimal import Decimal
            es_prio = (m_prio == '1')
            DetalleProductoMateriaP.objects.create(
                producto=producto,
                materia_prima_id=m_id,
                cantidad_usada=Decimal(m_cant),
                unidad_medida=m_uni,
                es_prioridad=es_prio
            )

@require_http_methods(["GET", "POST"])
def registrar_producto(request):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('listar_productos')

    if request.method != 'POST':
        return redirect('mostrar_registro_comida')

    imagen = request.FILES.get('txt_imagen')
    try:
        _validar_imagen_y_obtener_extension(imagen)
    except ValueError as e:
        messages.error(request, str(e))
        if request.POST.get('txt_categoria') == 'Bebidas':
            return redirect('mostrar_registro_bebida')
        else:
            return redirect('mostrar_registro_comida')

    nombre = request.POST.get('txt_nombre')
    categoria = request.POST.get('txt_categoria')

    if not nombre and categoria == 'Bebidas':
        materia_id = request.POST.getlist(MATERIA_ID_KEY)[0] if request.POST.getlist(MATERIA_ID_KEY) else None
        if materia_id:
            from materia_prima.models import MateriaPrima
            mp = MateriaPrima.objects.get(pk=materia_id)
            nombre = mp.nombre_materia_prima

    nombre_normalizado = (nombre or "Sin nombre").strip()
    if Producto.objects.filter(nombre_producto__iexact=nombre_normalizado).exists():
        messages.error(request, f"Ya existe un producto con el nombre '{nombre_normalizado}'.")
        if categoria == 'Bebidas':
            return redirect('mostrar_registro_bebida')
        else:
            return redirect('mostrar_registro_comida')

    producto = Producto.objects.create(
        nombre_producto=nombre_normalizado,
        precio=request.POST.get('txt_precio'),
        categoria=categoria,
        imagen=imagen,
    )

    materias_ids = request.POST.getlist(MATERIA_ID_KEY)
    materias_cantidades = request.POST.getlist(MATERIA_CANTIDAD_KEY)
    materias_unidades = request.POST.getlist(MATERIA_UNIDAD_KEY)
    materias_prioridades = request.POST.getlist('materia_prioridad[]')

    _guardar_composicion_producto(producto, materias_ids, materias_cantidades, materias_unidades, materias_prioridades)
    recalcular_stock_producto(producto)

    messages.success(request, f"Producto '{producto.nombre_producto}' registrado exitosamente con stock calculado.")
    return redirect('listar_productos')


# --- EDICIÓN Y ELIMINACIÓN (SOLO ADMIN) ---

@require_GET
def pre_editar_producto(request, id):
    es_admin = check_admin(request)
    if not es_admin:
        messages.error(request, "Acceso denegado. Solo el administrador puede modificar productos.")
        return redirect('listar_productos')

    producto = get_object_or_404(Producto, pk=id)

    if producto.categoria == 'Bebidas':
        materias_primas = MateriaPrima.objects.filter(tipo='Bebida')
        current_materia = producto.detalles_materia.first().materia_prima if producto.detalles_materia.exists() else None

        if not current_materia:
            current_materia = MateriaPrima.objects.filter(nombre_materia_prima=producto.nombre_producto, tipo='Bebida').first()

        return render(request, 'productos/editar_bebida.html', {
            'producto': producto,
            'es_admin': es_admin,
            'materias_primas': materias_primas,
            'current_materia': current_materia
        })
    else:
        materias_primas = MateriaPrima.objects.all()
        composicion = producto.detalles_materia.all()

        return render(request, 'productos/editar.html', {
            'producto': producto,
            'es_admin': es_admin,
            'materias_primas': materias_primas,
            'composicion': composicion
        })

@require_http_methods(["GET", "POST"])
def editar_producto(request):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para editar.")
        return redirect('listar_productos')

    if request.method != 'POST':
        return redirect('listar_productos')

    id_prod = request.POST.get('txt_id')
    producto = get_object_or_404(Producto, pk=id_prod)

    nombre = request.POST.get('txt_nombre')
    categoria = request.POST.get('txt_categoria')

    if not nombre and categoria == 'Bebidas':
        materia_id = request.POST.getlist(MATERIA_ID_KEY)
        if materia_id and materia_id[0]:
            from materia_prima.models import MateriaPrima
            mp = MateriaPrima.objects.get(pk=materia_id[0])
            nombre = mp.nombre_materia_prima

    nombre_normalizado = (nombre or producto.nombre_producto).strip()
    if Producto.objects.filter(nombre_producto__iexact=nombre_normalizado).exclude(pk=producto.pk).exists():
        messages.error(request, f"Ya existe un producto con el nombre '{nombre_normalizado}'.")
        return redirect('pre_editar_producto', id=producto.id)

    producto.nombre_producto = nombre_normalizado
    producto.precio          = request.POST.get('txt_precio')
    producto.categoria       = categoria

    imagen = request.FILES.get('txt_imagen')
    try:
        _validar_imagen_y_obtener_extension(imagen)
        if imagen:
            producto.imagen = imagen
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('pre_editar_producto', id=producto.id)

    producto.save()
    producto.detalles_materia.all().delete()

    materias_ids = request.POST.getlist(MATERIA_ID_KEY)
    materias_cantidades = request.POST.getlist(MATERIA_CANTIDAD_KEY)
    materias_unidades = request.POST.getlist(MATERIA_UNIDAD_KEY)
    materias_prioridades = request.POST.getlist('materia_prioridad[]')

    _guardar_composicion_producto(producto, materias_ids, materias_cantidades, materias_unidades, materias_prioridades)
    recalcular_stock_producto(producto)

    messages.success(request, "Producto actualizado correctamente y stock recalculado.")
    return redirect('listar_productos')

@require_http_methods(["GET", "POST"])
def eliminar_producto(request, id):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para eliminar productos.")
        return redirect('listar_productos')

    producto = get_object_or_404(Producto, pk=id)

    from facturas.models import Factura
    if Factura.objects.filter(pedido__detalles__producto=producto).exists():
        messages.error(request, f"No se puede eliminar el producto '{producto.nombre_producto}' porque está asociado a una factura.")
        return redirect('listar_productos')

    producto.delete()
    messages.success(request, "Producto eliminado.")
    return redirect('listar_productos')
