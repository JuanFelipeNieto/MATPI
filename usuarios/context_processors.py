from datetime import timedelta
from django.utils import timezone
from .models import Administrador
from materia_prima.models import MateriaPrima, Lote

def roles_usuario(request):
    id_usuario = request.session.get('usuario_id')

    # Por defecto decimos que no es admin
    es_admin = False
    materias_bajas = []
    lotes_vencidos = []
    lotes_por_vencer = []

    if id_usuario:
        # Buscamos en la tabla de administradores
        es_admin = Administrador.objects.filter(usuario_id=id_usuario).exists()

        # Asegurar tipo_navegacion y usuario_nombre_corto en sesión
        if 'tipo_navegacion' not in request.session or 'usuario_nombre_corto' not in request.session:
            from .models import Usuario
            usuario = Usuario.objects.filter(id=id_usuario).first()
            if usuario:
                if 'tipo_navegacion' not in request.session:
                    request.session['tipo_navegacion'] = getattr(usuario, 'tipo_navegacion', 'desplegable')
                if 'usuario_nombre_corto' not in request.session:
                    partes = usuario.nombre_completo.split()
                    nombre_corto = partes[0] if len(partes) < 3 else f"{partes[0]} {partes[2]}"
                    request.session['usuario_nombre_corto'] = nombre_corto

        # 1. Materias con bajo stock
        materias_bajas = [mp for mp in MateriaPrima.objects.all() if mp.stock_total <= 10]

        # 2. Lotes vencidos o por vencer
        hoy = timezone.localtime().date()
        diez_dias = hoy + timedelta(days=10)

        # Lotes que tienen stock y ya vencieron
        lotes_vencidos = Lote.objects.filter(
            fecha_vencimiento__lte=hoy,
            cantidad_actual__gt=0
        ).select_related('materia_prima')

        # Lotes que tienen stock y vencen en los próximos 10 días
        lotes_por_vencer = Lote.objects.filter(
            fecha_vencimiento__gt=hoy,
            fecha_vencimiento__lte=diez_dias,
            cantidad_actual__gt=0
        ).select_related('materia_prima')

    total_notif = len(materias_bajas) + len(lotes_vencidos) + len(lotes_por_vencer)

    return {
        'es_admin': es_admin,
        'materias_bajas': materias_bajas,
        'lotes_vencidos': lotes_vencidos,
        'lotes_por_vencer': lotes_por_vencer,
        'notificaciones_count': total_notif
    }
