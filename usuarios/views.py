import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Sum, Count
from matplotlib.ticker import MaxNLocator
from django.http import HttpResponse
from django.template.loader import get_template, TemplateDoesNotExist
from django.views.decorators.http import require_http_methods, require_GET, require_POST

# Librería para PDF
from xhtml2pdf import pisa

# Importación de modelos
from .models import Usuario, Administrador, Cajero, DashboardConfig
from clientes.models import Cliente
from productos.models import Producto
from pedidos.models import Pedido, DetallePedidoProducto
from reservas.models import Reserva
from materia_prima.models import MateriaPrima
from facturas.models import Factura
from proveedores.models import Proveedor


# Función auxiliar para validar si el ID en sesión es Administrador
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def validar_nombre(nombre):
    """Retorna True si el nombre solo tiene letras, espacios y acentos."""
    import re
    if not nombre: return False
    return bool(re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre))

def validar_solo_numeros(valor):
    """Retorna True si el valor solo tiene números."""
    if not valor: return False
    return valor.isdigit()

def es_administrador(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return False
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def login_requerido(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.info(request, "Sesión expirada. Por favor ingresa de nuevo.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        documento = request.POST.get('txt_id')
        clave = request.POST.get('txt_contrasena')
        try:
            user = Usuario.objects.get(id=documento, contraseña=clave)

            # Activación perezosa: Si hoy es su fecha de ingreso y está inactivo, activarlo.
            if user.estado == 'Inactivo' and user.fecha_ingreso <= timezone.now().date():
                user.estado = 'Activo'
                user.save()

            request.session['usuario_id'] = user.id
            request.session['usuario_nombre'] = user.nombre_completo
            # Guardar solo el primer nombre y primer apellido para mostrar en UI
            partes = user.nombre_completo.split()
            nombre_corto = partes[0] if len(partes) < 3 else f"{partes[0]} {partes[2]}"
            request.session['usuario_nombre_corto'] = nombre_corto
            request.session['tipo_navegacion'] = getattr(user, 'tipo_navegacion', 'desplegable')
            return redirect('dashboard')
        except Usuario.DoesNotExist:
            messages.error(request, "Documento o contraseña incorrectos.")
    return render(request, 'usuarios/login.html')

@require_GET
def logout_view(request):
    request.session.flush()
    return redirect('login')



@login_requerido
def dashboard(request):
    # Auto-eliminación de reservas pasadas al entrar al dashboard
    Reserva.objects.filter(fecha__lt=timezone.now()).delete()

    config, _ = DashboardConfig.objects.get_or_create(id=1)

    # Calcular inicio y fin del día en hora local para evitar problemas con MySQL/UTC
    ahora_local = timezone.localtime()
    hoy_inicio = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = hoy_inicio + timedelta(days=1)

    contexto = {
        'es_admin': es_administrador(request),
        'total_clientes': Cliente.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_pedidos': Pedido.objects.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin, facturas__isnull=False).count(),
        'total_reservas': Reserva.objects.filter(fecha_registro__gte=hoy_inicio, fecha_registro__lt=hoy_fin).count(),
        'ingresos': Pedido.objects.filter(
            fecha__gte=hoy_inicio,
            fecha__lt=hoy_fin,
            estado__in=['Preparacion', 'Completado'],
            facturas__isnull=False
        ).aggregate(total=Sum('valor'))['total'] or 0,
        'recent_pedidos': Pedido.objects.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin, facturas__isnull=False).order_by('-id')[:5],
        'recent_ingresos_pedidos': Pedido.objects.filter(
            fecha__gte=hoy_inicio,
            fecha__lt=hoy_fin,
            estado__in=['Preparacion', 'Completado'],
            facturas__isnull=False
        ).order_by('-id')[:5],
        'recent_clientes': Cliente.objects.all().order_by('-id')[:5],
        'recent_productos_vendidos': DetallePedidoProducto.objects.filter(
            pedido__fecha__gte=hoy_inicio,
            pedido__fecha__lt=hoy_fin,
            pedido__facturas__isnull=False
        ).values(
            'producto__nombre_producto'
        ).annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')[:5],
        'recent_reservas': Reserva.objects.filter(fecha_registro__gte=hoy_inicio, fecha_registro__lt=hoy_fin).order_by('-fecha_registro')[:5],
        'config': config,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_nombre_corto': (' '.join([
            p for i, p in enumerate(request.session.get('usuario_nombre', 'Usuario').split())
            if i in (0, 2)
        ]) or request.session.get('usuario_nombre', 'Usuario')),
    }
    return render(request, 'dashboard.html', contexto)

# ==========================================
# --- GESTIÓN DE USUARIOS (CRUD) ---
# ==========================================

@login_requerido
def listar_usuarios(request):
    if not es_administrador(request):
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')

    buscar = request.GET.get('buscar', '')
    usuarios = Usuario.objects.filter(cajero__isnull=False).order_by('nombre_completo')
    if buscar:
        usuarios = usuarios.filter(
            models.Q(id__icontains=buscar) | models.Q(nombre_completo__icontains=buscar)
        )

    from django.core.paginator import Paginator
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    usuarios_paginated = paginator.get_page(page_number)

    return render(request, 'usuarios/listar.html', {
        'usuarios': usuarios_paginated,
        'buscar': buscar,
        'es_admin': True
    })

def _validar_usuario_base(doc_id, nombre, telefono, experiencia_file=None):
    if doc_id is not None and len(doc_id) != 10:
        raise ValueError("El documento debe tener exactamente 10 caracteres.")
    if nombre:
        if len(nombre) < 3:
            raise ValueError("El nombre no puede tener menos de 3 caracteres.")
        if not validar_nombre(nombre):
            raise ValueError("El nombre no puede tener números ni caracteres especiales.")
    if telefono and len(telefono) < 6:
        raise ValueError("El teléfono no puede tener menos de 6 caracteres.")
    if experiencia_file and not experiencia_file.name.lower().endswith('.pdf'):
        raise ValueError("El archivo de experiencia laboral debe ser en formato PDF.")

def _validar_emergencia_requerido(emergencia_nombre, emergencia_parentesco, emergencia_numero):
    if not (emergencia_nombre and emergencia_parentesco and emergencia_numero):
        raise ValueError("Todos los campos de contacto de emergencia son requeridos.")
    if len(emergencia_nombre) < 3:
        raise ValueError("El nombre del contacto de emergencia no puede tener menos de 3 caracteres.")
    if not validar_nombre(emergencia_nombre):
        raise ValueError("El nombre del contacto de emergencia no puede tener números.")
    if len(emergencia_parentesco) > 15:
        raise ValueError("El parentesco no puede tener más de 15 caracteres.")
    if not validar_nombre(emergencia_parentesco):
        raise ValueError("El parentesco no puede tener números.")
    if len(emergencia_numero) < 6:
        raise ValueError("El teléfono de emergencia no puede tener menos de 6 caracteres.")
    if not validar_solo_numeros(emergencia_numero):
        raise ValueError("El teléfono de emergencia solo puede tener números.")

def _validar_emergencia_opcional(emergencia_nombre, emergencia_parentesco, emergencia_numero):
    if emergencia_nombre:
        if len(emergencia_nombre) < 3:
            raise ValueError("El nombre del contacto de emergencia no puede tener menos de 3 caracteres.")
        if not validar_nombre(emergencia_nombre):
            raise ValueError("El nombre del contacto de emergencia no puede tener números.")
    if emergencia_parentesco:
        if len(emergencia_parentesco) > 15:
            raise ValueError("El parentesco no puede tener más de 15 caracteres.")
        if not validar_nombre(emergencia_parentesco):
            raise ValueError("El parentesco no puede tener números.")
    if emergencia_numero:
        if len(emergencia_numero) < 6:
            raise ValueError("El teléfono de emergencia no puede tener menos de 6 caracteres.")
        if not validar_solo_numeros(emergencia_numero):
            raise ValueError("El teléfono de emergencia solo puede tener números.")

def _validar_emergencia(emergencia_nombre, emergencia_parentesco, emergencia_numero, required=True):
    if required:
        _validar_emergencia_requerido(emergencia_nombre, emergencia_parentesco, emergencia_numero)
    else:
        _validar_emergencia_opcional(emergencia_nombre, emergencia_parentesco, emergencia_numero)

@login_requerido
@require_http_methods(["GET", "POST"])
def ver_perfil(request, id):
    usuario_id = id
    usuario = get_object_or_404(Usuario, id=usuario_id)
    cajero = Cajero.objects.filter(usuario=usuario).first()

    es_propio = str(usuario.id) == str(request.session.get('usuario_id'))

    if request.method == 'POST' and es_propio:
        tipo_nav = request.POST.get('tipo_navegacion')
        if tipo_nav in ['desplegable', 'fijo']:
            usuario.tipo_navegacion = tipo_nav
            usuario.save()
            request.session['tipo_navegacion'] = tipo_nav
            messages.success(request, "Preferencia de navegación actualizada.")
            return redirect('ver_perfil', id=usuario_id)

    return render(request, 'usuarios/perfil.html', {
        'usuario': usuario,
        'cajero': cajero,
        'es_admin': es_administrador(request),
        'es_propio': es_propio
    })

@login_requerido
@require_http_methods(["GET", "POST"])
def registrar_usuario(request):
    if not es_administrador(request): return redirect('dashboard')
    if request.method != 'POST':
        return render(request, 'usuarios/registrar.html', {'es_admin': True})

    try:
        with transaction.atomic():
            doc_id = request.POST.get('txt_id')
            nombre = request.POST.get('txt_nombre')
            f_ingreso_str = request.POST.get('txt_fecha_ingreso')
            telefono = request.POST.get('txt_telefono')
            emergencia_nombre = request.POST.get('txt_emergencia_nombre')
            emergencia_parentesco = request.POST.get('txt_emergencia_parentesco')
            emergencia_numero = request.POST.get('txt_emergencia_numero')
            experiencia_file = request.FILES.get('txt_experiencia')

            _validar_usuario_base(doc_id, nombre, telefono, experiencia_file)
            _validar_emergencia(emergencia_nombre, emergencia_parentesco, emergencia_numero, required=True)

            f_ingreso = datetime.strptime(f_ingreso_str, '%Y-%m-%d').date()
            hoy = timezone.now().date()
            estado = 'Activo' if f_ingreso <= hoy else 'Inactivo'

            u = Usuario.objects.create(
                id=doc_id,
                nombre_completo=nombre,
                contraseña=request.POST.get('txt_contrasena'),
                correo_electronico=request.POST.get('txt_correo'),
                telefono=request.POST.get('txt_telefono'),
                fecha_nacimiento=request.POST.get('txt_fecha_nacimiento'),
                direccion=request.POST.get('txt_direccion'),
                fecha_ingreso=f_ingreso,
                experiencia_laboral=experiencia_file,
                estado=estado
            )
            fecha_term = request.POST.get('txt_fecha_terminacion')
            Cajero.objects.create(
                usuario=u,
                eps=request.POST.get('txt_eps'),
                tipo_contrato=request.POST.get('txt_tipo_contrato'),
                turno=request.POST.get('txt_turno'),
                fecha_terminacion_contrato=fecha_term if (fecha_term and request.POST.get('txt_tipo_contrato') == 'Fijo') else None,
                contacto_emergencia_nombre=emergencia_nombre,
                contacto_emergencia_parentesco=emergencia_parentesco,
                contacto_emergencia_numero=emergencia_numero
            )
        messages.success(request, f"Cajero {u.nombre_completo} creado.")
        return redirect('listar_usuarios')
    except ValueError as e:
        messages.error(request, f"Error: {e}")
        return render(request, 'usuarios/registrar.html', {'es_admin': True, 'datos': request.POST})

@login_requerido
@require_http_methods(["GET", "POST"])
def _editar_usuario_get(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    cajero = Cajero.objects.filter(usuario=usuario).first()
    return render(request, 'usuarios/editar.html', {
        'usuario': usuario,
        'eps': cajero.eps if cajero else "",
        'es_admin': True
    })

def _actualizar_cajero_datos(cajero, request, emergencia_nombre, emergencia_parentesco, emergencia_numero):
    if request.POST.get('txt_eps'):
        cajero.eps = request.POST.get('txt_eps')

    tipo_c = request.POST.get('txt_tipo_contrato')
    if tipo_c:
        cajero.tipo_contrato = tipo_c
    if request.POST.get('txt_turno'):
        cajero.turno = request.POST.get('txt_turno')
    if emergencia_nombre:
        cajero.contacto_emergencia_nombre = emergencia_nombre
    if emergencia_parentesco:
        cajero.contacto_emergencia_parentesco = emergencia_parentesco
    if emergencia_numero:
        cajero.contacto_emergencia_numero = emergencia_numero

    fecha_term = request.POST.get('txt_fecha_terminacion')
    if tipo_c == 'Indefinido':
        cajero.fecha_terminacion_contrato = None
    elif fecha_term:
        cajero.fecha_terminacion_contrato = fecha_term

    cajero.save()

def _editar_usuario_post(request):
    usuario_id = request.POST.get('txt_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    try:
        with transaction.atomic():
            nombre = request.POST.get('txt_nombre')
            telefono = request.POST.get('txt_telefono')
            emergencia_nombre = request.POST.get('txt_emergencia_nombre')
            emergencia_parentesco = request.POST.get('txt_emergencia_parentesco')
            emergencia_numero = request.POST.get('txt_emergencia_numero')
            experiencia_file = request.FILES.get('txt_experiencia')

            _validar_usuario_base(None, nombre, telefono, experiencia_file)
            _validar_emergencia(emergencia_nombre, emergencia_parentesco, emergencia_numero, required=False)

            usuario.nombre_completo = nombre
            usuario.correo_electronico = request.POST.get('txt_correo')
            usuario.telefono = telefono
            usuario.direccion = request.POST.get('txt_direccion')
            usuario.estado = request.POST.get('txt_estado')

            if experiencia_file:
                usuario.experiencia_laboral = experiencia_file
            if request.POST.get('txt_contrasena'):
                usuario.contraseña = request.POST.get('txt_contrasena')
            usuario.save()

            if usuario.es_cajero:
                cajero, _ = Cajero.objects.get_or_create(usuario=usuario)
                _actualizar_cajero_datos(cajero, request, emergencia_nombre, emergencia_parentesco, emergencia_numero)

        if str(usuario.id) == str(request.session.get('usuario_id')):
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect('ver_perfil', id=usuario.id)
        else:
            messages.success(request, "Cajero actualizado correctamente.")
            return redirect('listar_usuarios')
    except ValueError as e:
        messages.error(request, f"Error al editar: {e}")
        return redirect('editar_usuario', usuario_id=usuario_id)

@login_requerido
@require_http_methods(["GET", "POST"])
def editar_usuario(request, id=None):
    usuario_id = id
    if not es_administrador(request):
        return redirect('dashboard')

    if request.method == 'POST':
        return _editar_usuario_post(request)
    elif usuario_id:
        return _editar_usuario_get(request, usuario_id)
    return redirect('listar_usuarios')

@login_requerido
@require_http_methods(["GET", "POST"])
def eliminar_usuario(request, id):
    usuario_id = id
    if not es_administrador(request): return redirect('dashboard')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if str(usuario.id) == str(request.session.get('usuario_id')):
        messages.error(request, "No puedes eliminarte a ti mismo.")
    else:
        usuario.delete()
        messages.success(request, "Usuario eliminado.")
    return redirect('listar_usuarios')



def generar_pdf(template_src, contexto, nombre_archivo):
    try:
        template = get_template(template_src)
        html = template.render(contexto)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{nombre_archivo}.pdf"'
            return response
    except TemplateDoesNotExist:
        return HttpResponse("Error: No se encontró la plantilla del reporte.", status=404)
    return HttpResponse("Error al generar PDF", status=500)


def generar_grafica_pedidos(queryset, periodo):
    """Genera una imagen base64 de una gráfica de barras según el periodo."""
    from collections import Counter

    # Obtener lista de componentes (hora, día, etc.) en tiempo local
    if periodo == 'diario':
        datos_raw = [timezone.localtime(p.fecha).hour for p in queryset]
        xlabel = 'Hora del Día'
        title = 'Pedidos por Hora'
        xticks = list(range(0, 24))
        xticklabels = [f"{h}h" for h in xticks]
    elif periodo == 'semanal':
        # isoweekday(): 1=Lun, 2=Mar, ..., 7=Dom
        datos_raw = [timezone.localtime(p.fecha).isoweekday() for p in queryset]
        xlabel = 'Día de la Semana'
        title = 'Pedidos por Día (Semana)'
        xticks = list(range(1, 8))
        xticklabels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    elif periodo == 'mensual':
        datos_raw = [timezone.localtime(p.fecha).day for p in queryset]
        xlabel = 'Día del Mes'
        title = 'Pedidos por Día (Mes)'
        xticks = list(range(1, 32))
        xticklabels = [str(d) for d in xticks]
    else:
        return None

    # Agrupar y contar frecuencias en Python
    counts = Counter(datos_raw)
    full_y_vals = [counts.get(x, 0) for x in xticks]

    # Crear la gráfica con estilo premium
    plt.figure(figsize=(10, 5))
    plt.bar(xticks, full_y_vals, color='#FFD700', edgecolor='#B8860B', alpha=0.8)
    plt.xlabel(xlabel, fontweight='bold')
    plt.ylabel('Cantidad de Pedidos', fontweight='bold')
    # Asegurar que el eje Y empiece en 0 y tenga un rango mínimo para números enteros
    max_val = max(full_y_vals) if full_y_vals else 0
    plt.ylim(0, max(max_val + 1, 5))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.xticks(xticks, xticklabels, rotation=45 if periodo == 'mensual' else 0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Guardar en buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@login_requerido
@require_GET
def reporte_modulo_pdf(request, modulo, periodo):
    from reportes.services import obtener_rango_fechas
    ahora = timezone.now()
    fecha_inicio, fecha_fin = obtener_rango_fechas(periodo)
    cajero_estrella_mensaje = None
    producto_estrella_mensaje = None
    materia_estrella_mensaje = None
    pedidos_pico_mensaje = None
    cliente_estrella_mensaje = None
    reserva_estrella_mensaje = None
    proveedor_estrella_mensaje = None

    pedidos_completados = Pedido.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin, estado__in=['Preparacion', 'Completado'])
    reservas_periodo = Reserva.objects.filter(fecha__gte=fecha_inicio)
    facturas_periodo = Factura.objects.filter(pedido__fecha__gte=fecha_inicio, pedido__fecha__lte=fecha_fin)

    config_reporte = {
        'ventas': (pedidos_completados, 'reportes/pdf_pedidos.html'),
        'pedidos': (pedidos_completados, 'reportes/pdf_pedidos.html'),
        'productos': (Producto.objects.all(), 'reportes/pdf_productos.html'),
        'materias': (MateriaPrima.objects.all(), 'reportes/pdf_materias.html'),
        'materia_prima': (MateriaPrima.objects.all(), 'reportes/pdf_materias.html'),
        'clientes': (Cliente.objects.all(), 'reportes/pdf_clientes.html'),
        'facturas': (facturas_periodo, 'reportes/pdf_facturas.html'),
        'proveedores': (Proveedor.objects.all(), 'reportes/pdf_proveedores.html'),
        'reservas': (reservas_periodo, 'reportes/pdf_reservas.html'),
    }

    if modulo == 'usuarios':
        if not es_administrador(request):
            return redirect('dashboard')

        cajeros = Cajero.objects.filter(usuario__estado='Activo').annotate(
            pedidos_totales=models.Count('usuario__pedidos', filter=models.Q(usuario__pedidos__estado__in=['Preparacion', 'Completado'])),
            pedidos_periodo=models.Count('usuario__pedidos', filter=models.Q(usuario__pedidos__estado__in=['Preparacion', 'Completado'], usuario__pedidos__fecha__gte=fecha_inicio, usuario__pedidos__fecha__lte=fecha_fin))
        ).select_related('usuario')

        # Encontrar el cajero que más pedidos atendió en el periodo (soportando empates)
        cajero_estrella_pedidos = 0
        cajeros_ganadores = []
        for c in cajeros:
            if c.pedidos_periodo > cajero_estrella_pedidos:
                cajero_estrella_pedidos = c.pedidos_periodo
                cajeros_ganadores = [c.usuario.nombre_completo]
            elif c.pedidos_periodo == cajero_estrella_pedidos and cajero_estrella_pedidos > 0:
                cajeros_ganadores.append(c.usuario.nombre_completo)

        if cajero_estrella_pedidos > 0:
            periodo_durante_map = {
                'diario': 'el día',
                'semanal': 'la semana',
                'mensual': 'el mes',
                'general': 'todo el tiempo'
            }
            p_durante = periodo_durante_map.get(periodo, 'el periodo')
            if len(cajeros_ganadores) > 1:
                nombres = ", ".join(cajeros_ganadores[:-1]) + " y " + cajeros_ganadores[-1]
                cajero_estrella_mensaje = f"Los cajeros que más pedidos atendieron durante {p_durante} fueron: {nombres}"
            else:
                cajero_estrella_mensaje = f"El cajero que más pedidos atendió durante {p_durante} fue: {cajeros_ganadores[0]}"

        # Filtros y ordenamiento adicionales
        min_pedidos = request.GET.get('min_pedidos')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        ordenar = request.GET.get('ordenar')

        if min_pedidos:
            try:
                cajeros = cajeros.filter(pedidos_periodo__gte=int(min_pedidos))
            except ValueError:
                pass

        if fecha_desde:
            cajeros = cajeros.filter(usuario__fecha_ingreso__gte=fecha_desde)
        if fecha_hasta:
            cajeros = cajeros.filter(usuario__fecha_ingreso__lte=fecha_hasta)

        if ordenar == 'pedidos_desc':
            cajeros = cajeros.order_by('-pedidos_periodo')
        elif ordenar == 'pedidos_asc':
            cajeros = cajeros.order_by('pedidos_periodo')
        elif ordenar == 'fecha_desc':
            cajeros = cajeros.order_by('-usuario__fecha_ingreso')
        elif ordenar == 'fecha_asc':
            cajeros = cajeros.order_by('usuario__fecha_ingreso')

        qs = cajeros
        template_path = 'reportes/pdf_usuarios.html'
        titulo = "Reporte de Cajeros"
    elif modulo == 'productos':
        from django.db.models.functions import Coalesce

        categoria = request.GET.get('categoria', '')
        ordenar = request.GET.get('ordenar', '')

        # Annotate each product with total sold quantity during the selected period
        productos = Producto.objects.annotate(
            total_vendido=Coalesce(
                models.Sum(
                    'detalles_pedido__cantidad',
                    filter=models.Q(
                        detalles_pedido__pedido__fecha__gte=fecha_inicio,
                        detalles_pedido__pedido__fecha__lte=fecha_fin,
                        detalles_pedido__pedido__facturas__isnull=False
                    )
                ),
                0
            )
        )

        if categoria:
            productos = productos.filter(categoria=categoria)

        # Encontrar el producto más vendido en el periodo (soportando empates)
        producto_estrella_cantidad = 0
        productos_ganadores = []
        for p in productos:
            if p.total_vendido > producto_estrella_cantidad:
                producto_estrella_cantidad = p.total_vendido
                productos_ganadores = [p.nombre_producto]
            elif p.total_vendido == producto_estrella_cantidad and producto_estrella_cantidad > 0:
                productos_ganadores.append(p.nombre_producto)

        if producto_estrella_cantidad > 0:
            periodo_durante_map = {
                'diario': 'el día',
                'semanal': 'la semana',
                'mensual': 'el mes',
                'general': 'todo el tiempo'
            }
            p_durante = periodo_durante_map.get(periodo, 'el periodo')
            if len(productos_ganadores) > 1:
                nombres = ", ".join(productos_ganadores[:-1]) + " y " + productos_ganadores[-1]
                producto_estrella_mensaje = f"Los productos más vendidos durante {p_durante} fueron: {nombres}"
            else:
                producto_estrella_mensaje = f"El producto más vendido durante {p_durante} fue: {productos_ganadores[0]}"

        if ordenar == 'ventas_desc':
            productos = productos.order_by('-total_vendido')
        elif ordenar == 'ventas_asc':
            productos = productos.order_by('total_vendido')
        elif ordenar == 'nombre_asc':
            productos = productos.order_by('nombre_producto')
        elif ordenar == 'nombre_desc':
            productos = productos.order_by('-nombre_producto')
        else:
            productos = productos.order_by('-total_vendido')

        qs = productos
        template_path = 'reportes/pdf_productos.html'
        titulo = "Reporte de Productos"
    elif modulo == 'clientes':
        from django.db.models.functions import Coalesce

        ordenar = request.GET.get('ordenar', '')

        # Annotate each client with total orders, total reservations, and total consumption in the selected period
        clientes = Cliente.objects.annotate(
            total_pedidos=Coalesce(
                models.Count(
                    'pedidos',
                    filter=models.Q(
                        pedidos__fecha__gte=fecha_inicio,
                        pedidos__fecha__lte=fecha_fin,
                        pedidos__facturas__isnull=False
                    )
                ),
                0
            ),
            total_reservas=Coalesce(
                models.Count(
                    'reservas',
                    filter=models.Q(
                        reservas__fecha_registro__gte=fecha_inicio,
                        reservas__fecha_registro__lte=fecha_fin
                    )
                ),
                0
            ),
            total_consumo=Coalesce(
                models.Sum(
                    'pedidos__valor',
                    filter=models.Q(
                        pedidos__fecha__gte=fecha_inicio,
                        pedidos__fecha__lte=fecha_fin,
                        pedidos__facturas__isnull=False
                    )
                ),
                0
            )
        )

        # Encontrar el cliente que más consumió (soportando empates)
        cliente_estrella_consumo = 0
        clientes_ganadores = []
        for c in clientes:
            if c.total_consumo > cliente_estrella_consumo:
                cliente_estrella_consumo = c.total_consumo
                clientes_ganadores = [c.nombre_completo]
            elif c.total_consumo == cliente_estrella_consumo and cliente_estrella_consumo > 0:
                clientes_ganadores.append(c.nombre_completo)

        if cliente_estrella_consumo > 0:
            periodo_durante_map = {
                'diario': 'el día',
                'semanal': 'la semana',
                'mensual': 'el mes',
                'general': 'todo el tiempo'
            }
            p_durante = periodo_durante_map.get(periodo, 'el periodo')
            if len(clientes_ganadores) > 1:
                nombres = ", ".join(clientes_ganadores[:-1]) + " y " + clientes_ganadores[-1]
                cliente_estrella_mensaje = f"Los clientes que más consumieron durante {p_durante} fueron: {nombres}"
            else:
                cliente_estrella_mensaje = f"El cliente que más consumió durante {p_durante} fue: {clientes_ganadores[0]}"

        if ordenar == 'pedidos_desc':
            clientes = clientes.order_by('-total_pedidos')
        elif ordenar == 'pedidos_asc':
            clientes = clientes.order_by('total_pedidos')
        elif ordenar == 'reservas_desc':
            clientes = clientes.order_by('-total_reservas')
        elif ordenar == 'reservas_asc':
            clientes = clientes.order_by('total_reservas')
        else:
            clientes = clientes.order_by('-total_pedidos')

        qs = clientes
        template_path = 'reportes/pdf_clientes.html'
        titulo = "Reporte de Clientes"
    elif modulo == 'proveedores':
        from django.db.models.functions import Coalesce

        ordenar = request.GET.get('ordenar', '')

        # Annotate each supplier with the count of registered supplies in the selected period
        proveedores = Proveedor.objects.annotate(
            total_suministros=Coalesce(
                models.Count(
                    'detalles_materia',
                    filter=models.Q(
                        detalles_materia__fecha_suministro__gte=fecha_inicio,
                        detalles_materia__fecha_suministro__lte=fecha_fin
                    )
                ),
                0
            )
        )

        # Encontrar el proveedor que más suministró (soportando empates)
        proveedor_estrella_cantidad = 0
        proveedores_ganadores = []
        for p in proveedores:
            if p.total_suministros > proveedor_estrella_cantidad:
                proveedor_estrella_cantidad = p.total_suministros
                proveedores_ganadores = [p.nombre_proveedor]
            elif p.total_suministros == proveedor_estrella_cantidad and proveedor_estrella_cantidad > 0:
                proveedores_ganadores.append(p.nombre_proveedor)

        if proveedor_estrella_cantidad > 0:
            periodo_durante_map = {
                'diario': 'el día',
                'semanal': 'la semana',
                'mensual': 'el mes',
                'general': 'todo el tiempo'
            }
            p_durante = periodo_durante_map.get(periodo, 'el periodo')
            if len(proveedores_ganadores) > 1:
                nombres = ", ".join(proveedores_ganadores[:-1]) + " y " + proveedores_ganadores[-1]
                proveedor_estrella_mensaje = f"Los proveedores que más cantidad suministraron durante {p_durante} fueron: {nombres}"
            else:
                proveedor_estrella_mensaje = f"El proveedor que más cantidad suministró durante {p_durante} fue: {proveedores_ganadores[0]}"

        if ordenar == 'suministros_desc':
            proveedores = proveedores.order_by('-total_suministros')
        elif ordenar == 'suministros_asc':
            proveedores = proveedores.order_by('total_suministros')
        else:
            proveedores = proveedores.order_by('-total_suministros')

        qs = proveedores
        template_path = 'reportes/pdf_proveedores.html'
        titulo = "Reporte de Proveedores"
    elif modulo in ['materias', 'materia_prima']:
        from materia_prima.models import DetalleProductoMateriaP

        ordenar = request.GET.get('ordenar', '')

        # Fetch all raw materials
        materias = list(MateriaPrima.objects.all())
        cons_dict = {mp.id: 0.0 for mp in materias}

        # Calculate consumption based on completed/preparando orders in the period
        detalles = DetallePedidoProducto.objects.filter(
            pedido__fecha__gte=fecha_inicio,
            pedido__fecha__lte=fecha_fin,
            pedido__estado__in=['Preparacion', 'Completado']
        ).select_related('producto').prefetch_related('materias_excluidas')

        for det in detalles:
            excluidas = set(det.materias_excluidas.all())
            composicion = DetalleProductoMateriaP.objects.filter(producto=det.producto).select_related('materia_prima')
            for comp in composicion:
                if comp.materia_prima not in excluidas:
                    cant_consumida = float(comp.cantidad_usada) * det.cantidad
                    cons_dict[comp.materia_prima.id] += cant_consumida

        # Attach total_consumido attribute to each raw material object
        for mp in materias:
            mp.total_consumido = cons_dict.get(mp.id, 0.0)

        # Encontrar la materia prima más consumida en el periodo (soportando empates)
        materia_estrella_consumo = 0.0
        materias_ganadoras = []
        for mp in materias:
            if mp.total_consumido > materia_estrella_consumo:
                materia_estrella_consumo = mp.total_consumido
                materias_ganadoras = [mp.nombre_materia_prima]
            elif mp.total_consumido == materia_estrella_consumo and materia_estrella_consumo > 0:
                materias_ganadoras.append(mp.nombre_materia_prima)

        if materia_estrella_consumo > 0:
            periodo_durante_map = {
                'diario': 'el día',
                'semanal': 'la semana',
                'mensual': 'el mes',
                'general': 'todo el tiempo'
            }
            p_durante = periodo_durante_map.get(periodo, 'el periodo')
            if len(materias_ganadoras) > 1:
                nombres = ", ".join(materias_ganadoras[:-1]) + " y " + materias_ganadoras[-1]
                materia_estrella_mensaje = f"Las materias primas más consumidas durante {p_durante} fueron: {nombres}"
            else:
                materia_estrella_mensaje = f"La materia prima más consumida durante {p_durante} fue: {materias_ganadoras[0]}"

        # Sort the materias list based on the select parameter
        if ordenar == 'consumo_desc':
            materias.sort(key=lambda x: x.total_consumido, reverse=True)
        elif ordenar == 'consumo_asc':
            materias.sort(key=lambda x: x.total_consumido)
        else:
            materias.sort(key=lambda x: x.total_consumido, reverse=True)

        qs = materias
        template_path = 'reportes/pdf_materias.html'
        titulo = "Reporte de Materia Prima"
    elif modulo == 'facturas':
        ordenar = request.GET.get('ordenar', '')

        facturas = facturas_periodo

        if ordenar == 'valor_desc':
            facturas = facturas.order_by('-valor_total')
        elif ordenar == 'valor_asc':
            facturas = facturas.order_by('valor_total')
        else:
            facturas = facturas.order_by('-valor_total')

        qs = facturas
        template_path = 'reportes/pdf_facturas.html'
        titulo = "Reporte de Facturas"
    elif modulo in ['pedidos', 'ventas']:
        from django.db.models.functions import Coalesce

        ordenar = request.GET.get('ordenar', '')

        # Annotate each order with total quantity of products (sum of detalles__cantidad)
        pedidos = pedidos_completados.annotate(
            total_productos=Coalesce(
                models.Sum('detalles__cantidad'),
                0
            )
        )

        if ordenar == 'cantidad_desc':
            pedidos = pedidos.order_by('-total_productos')
        elif ordenar == 'cantidad_asc':
            pedidos = pedidos.order_by('total_productos')
        else:
            pedidos = pedidos.order_by('-fecha')

        qs = pedidos

        # Calcular el pico de pedidos según el período (soportando empates)
        pedidos_pico_mensaje = None
        if pedidos.exists():
            from collections import Counter
            if periodo == 'diario':
                horas = [timezone.localtime(p.fecha).hour for p in pedidos]
                if horas:
                    counter = Counter(horas)
                    most_common = counter.most_common()
                    max_count = most_common[0][1]
                    picos = [h for h, c in most_common if c == max_count]
                    picos_str = ", ".join(f"{h:02d}:00" for h in picos[:-1]) + " y " + f"{picos[-1]:02d}:00" if len(picos) > 1 else f"{picos[0]:02d}:00"
                    if len(picos) > 1:
                        pedidos_pico_mensaje = f"Las horas en las que más pedidos se hicieron durante el día fueron: {picos_str}"
                    else:
                        pedidos_pico_mensaje = f"La hora en la que más pedidos se hicieron durante el día fue: {picos_str}"
            elif periodo == 'semanal':
                dias_semana_nombres = {
                    1: 'Lunes', 2: 'Martes', 3: 'Miércoles',
                    4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'
                }
                dias = [timezone.localtime(p.fecha).isoweekday() for p in pedidos]
                if dias:
                    counter = Counter(dias)
                    most_common = counter.most_common()
                    max_count = most_common[0][1]
                    picos = [dias_semana_nombres.get(d) for d, c in most_common if c == max_count]
                    picos_str = ", ".join(picos[:-1]) + " y " + picos[-1] if len(picos) > 1 else picos[0]
                    if len(picos) > 1:
                        pedidos_pico_mensaje = f"Los días de la semana en los que más pedidos se hicieron durante la semana fueron: {picos_str}"
                    else:
                        pedidos_pico_mensaje = f"El día de la semana en el que más pedidos se hicieron durante la semana fue: {picos_str}"
            elif periodo == 'mensual':
                semanas_mes = [(timezone.localtime(p.fecha).day - 1) // 7 + 1 for p in pedidos]
                if semanas_mes:
                    counter = Counter(semanas_mes)
                    most_common = counter.most_common()
                    max_count = most_common[0][1]
                    semanas_nombres = {
                        1: 'la primera semana',
                        2: 'la segunda semana',
                        3: 'la tercera semana',
                        4: 'la cuarta semana',
                        5: 'la quinta semana'
                    }
                    picos = [semanas_nombres.get(s) for s, c in most_common if c == max_count]
                    picos_str = ", ".join(picos[:-1]) + " y " + picos[-1] if len(picos) > 1 else picos[0]
                    if len(picos) > 1:
                        pedidos_pico_mensaje = f"Las semanas del mes en las que más pedidos se hicieron durante el mes fueron: {picos_str}"
                    else:
                        pedidos_pico_mensaje = f"La semana del mes en la que más pedidos se hicieron durante el mes fue: {picos_str}"
            elif periodo == 'general':
                semanas = []
                for p in pedidos:
                    fl = timezone.localtime(p.fecha).date()
                    lunes = fl - timedelta(days=fl.weekday())
                    semanas.append(lunes)
                if semanas:
                    counter = Counter(semanas)
                    most_common = counter.most_common()
                    max_count = most_common[0][1]
                    picos = [s.strftime("%d/%m/%Y") for s, c in most_common if c == max_count]
                    picos_str = ", ".join(f"la del {p}" for p in picos[:-1]) + " y " + f"la del {picos[-1]}" if len(picos) > 1 else f"la del {picos[0]}"
                    if len(picos) > 1:
                        pedidos_pico_mensaje = f"Las semanas en las que más pedidos se hicieron fueron: {picos_str}"
                    else:
                        pedidos_pico_mensaje = f"La semana en la que más pedidos se hicieron fue: {picos_str}"

        template_path = 'reportes/pdf_pedidos.html'
        titulo = "Reporte de Pedidos"
    elif modulo == 'reservas':
        agendado_para = request.GET.get('agendado_para', '')

        # Start with all reservations in the period
        reservas = reservas_periodo

        if agendado_para:
            ahora_local = timezone.localtime(timezone.now())
            if agendado_para == 'proximos_dias':
                # Next 3 days (from now to now + 3 days)
                limite = ahora_local + timedelta(days=3)
                reservas = Reserva.objects.filter(fecha__gte=ahora_local, fecha__lte=limite)
            elif agendado_para == 'proxima_semana':
                # Next 7 days
                limite = ahora_local + timedelta(days=7)
                reservas = Reserva.objects.filter(fecha__gte=ahora_local, fecha__lte=limite)
            elif agendado_para == 'proximo_mes':
                # Next 30 days
                limite = ahora_local + timedelta(days=30)
                reservas = Reserva.objects.filter(fecha__gte=ahora_local, fecha__lte=limite)

        qs = list(reservas.order_by('fecha'))

        # Encontrar el cliente con más reservas en el período (soportando empates)
        reserva_estrella_cantidad = 0
        reservas_ganadores = []
        if qs:
            from collections import Counter
            clientes_reservas = [r.cliente.nombre_completo for r in qs if r.cliente]
            if clientes_reservas:
                counter = Counter(clientes_reservas)
                most_common = counter.most_common()
                reserva_estrella_cantidad = most_common[0][1]
                reservas_ganadores = [name for name, count in most_common if count == reserva_estrella_cantidad]

            # Contar total de reservas por cliente y asociarlo a cada objeto Reserva
            counts = Counter(r.cliente_id for r in qs if r.cliente_id)
            for r in qs:
                r.cliente_total_reservas = counts.get(r.cliente_id, 0)

        if reserva_estrella_cantidad > 0:
            if len(reservas_ganadores) > 1:
                nombres = ", ".join(reservas_ganadores[:-1]) + " y " + reservas_ganadores[-1]
                reserva_estrella_mensaje = f"Los clientes que más reservas realizaron fueron: {nombres}"
            else:
                reserva_estrella_mensaje = f"El cliente que más reservas realizó fue: {reservas_ganadores[0]}"

        template_path = 'reportes/pdf_reservas.html'
        titulo = "Reporte de Reservas"
    else:
        qs, template_path = config_reporte.get(modulo, (None, ""))
        titulo = f"Reporte de {modulo.capitalize()}"


    periodo_map = {
        'diario': 'del Día',
        'semanal': 'de la Semana',
        'mensual': 'del Mes',
        'general': 'en Total'
    }

    # Generar gráfica solo para pedidos/ventas y periodos específicos
    chart_base64 = None
    if modulo in ['pedidos', 'ventas'] and periodo in ['diario', 'semanal', 'mensual']:
        chart_base64 = generar_grafica_pedidos(qs, periodo)

    contexto = {
        'datos': qs,
        'titulo': titulo,
        'fecha': ahora,
        'vendedor': request.session.get('usuario_nombre'),
        'periodo_str': periodo_map.get(periodo, 'del Periodo'),
        'chart_base64': chart_base64,
        'cajero_estrella_mensaje': cajero_estrella_mensaje,
        'producto_estrella_mensaje': producto_estrella_mensaje,
        'materia_estrella_mensaje': materia_estrella_mensaje,
        'pedidos_pico_mensaje': pedidos_pico_mensaje,
        'cliente_estrella_mensaje': cliente_estrella_mensaje,
        'reserva_estrella_mensaje': reserva_estrella_mensaje,
        'proveedor_estrella_mensaje': proveedor_estrella_mensaje,
    }
    return generar_pdf(template_path, contexto, f"MATPI_{modulo}")

@login_requerido
@require_POST
def actualizar_metas(request):
    if not es_administrador(request): return redirect('dashboard')
    config, _ = DashboardConfig.objects.get_or_create(id=1)
    config.meta_reservas = int(request.POST.get('meta_reservas', 0))
    config.meta_pedidos = int(request.POST.get('meta_pedidos', 0))
    config.save()
    messages.success(request, "Metas actualizadas.")
    return redirect('dashboard')
