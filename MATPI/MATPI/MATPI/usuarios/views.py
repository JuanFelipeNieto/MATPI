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
from pedidos.models import Pedido
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
        'total_pedidos': Pedido.objects.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin).count(),
        'total_reservas': Reserva.objects.filter(fecha_registro__gte=hoy_inicio, fecha_registro__lt=hoy_fin).count(),
        'ingresos': Pedido.objects.filter(
            fecha__gte=hoy_inicio,
            fecha__lt=hoy_fin,
            estado__in=['Preparacion', 'Completado']
        ).aggregate(total=Sum('valor'))['total'] or 0,
        'pedidos_recientes': Pedido.objects.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin).order_by('-id')[:5],
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
    usuarios = Usuario.objects.filter(cajero__isnull=False)
    if buscar:
        usuarios = usuarios.filter(
            models.Q(id__icontains=buscar) | models.Q(nombre_completo__icontains=buscar)
        )
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios, 'buscar': buscar})

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
            return redirect('ver_perfil', usuario_id=usuario_id)

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
            usuario.fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')
            usuario.direccion = request.POST.get('txt_direccion')

            nueva_f_ingreso = request.POST.get('txt_fecha_ingreso')
            if nueva_f_ingreso:
                usuario.fecha_ingreso = nueva_f_ingreso
                f_date = datetime.strptime(nueva_f_ingreso, '%Y-%m-%d').date()
                hoy = timezone.now().date()
                usuario.estado = 'Activo' if f_date <= hoy else 'Inactivo'
            else:
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
            return redirect('ver_perfil', usuario_id=usuario.id)
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
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'
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

        qs = cajeros
        template_path = 'reportes/pdf_usuarios.html'
        titulo = "Reporte de Cajeros"
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
        'chart_base64': chart_base64
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
