from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Usuario, Administrador, Cajero, DashboardConfig

class UsuarioViewsTest(TestCase):
    def setUp(self):
        # Configuración inicial de datos de prueba
        # Crear usuario Administrador
        self.admin_user = Usuario.objects.create(
            id="1000000001",
            nombre_completo="Administrador de Pruebas",
            contraseña="admin123",
            correo_electronico="admin@matpi.com",
            telefono="3000000001",
            fecha_nacimiento="1990-01-01",
            direccion="Calle Admin 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(
            usuario=self.admin_user,
            formacion_educativa="Ingeniero de Sistemas"
        )

        # Crear usuario Cajero (normal)
        self.cajero_user = Usuario.objects.create(
            id="1000000002",
            nombre_completo="Cajero de Pruebas",
            contraseña="cajero123",
            correo_electronico="cajero@matpi.com",
            telefono="3000000002",
            fecha_nacimiento="1995-05-05",
            direccion="Calle Cajero 456",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.cajero = Cajero.objects.create(
            usuario=self.cajero_user,
            eps="SURA",
            tipo_contrato="Indefinido",
            turno="Mañana"
        )

        # Configuración por defecto para el Dashboard
        self.dashboard_config = DashboardConfig.objects.create(
            id=1,
            meta_reservas=50,
            meta_pedidos=200
        )

    def iniciar_sesion(self, usuario):
        """Método auxiliar para simular el inicio de sesión en pruebas."""
        session = self.client.session
        session['usuario_id'] = usuario.id
        session['usuario_nombre'] = usuario.nombre_completo
        session.save()

    # =========================================================================
    # 1. VISTA DE INICIO DE SESIÓN (login_view)
    # =========================================================================
    
    def test_1_login_view_get(self):
        """1. Vista de Login (GET) - Carga del Formulario"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    def test_1_login_view_post_success(self):
        """1. Vista de Login (POST) - Autenticación Exitosa"""
        data = {
            'txt_id': '1000000001',
            'txt_contrasena': 'admin123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.client.session.get('usuario_id'), '1000000001')

    def test_1_login_view_post_fail(self):
        """1. Vista de Login (POST) - Credenciales Incorrectas"""
        data = {
            'txt_id': '1000000001',
            'txt_contrasena': 'clave_incorrecta'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200) # Permanece en la misma página de login
        self.assertTemplateUsed(response, 'usuarios/login.html')

    # =========================================================================
    # 2. VISTA DE CIERRE DE SESIÓN (logout_view)
    # =========================================================================

    def test_2_logout_view(self):
        """2. Vista de Logout - Finalización de Sesión"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('usuario_id', self.client.session)

    # =========================================================================
    # 3. PANEL DE CONTROL (dashboard)
    # =========================================================================

    def test_3_dashboard_view(self):
        """3. Panel de Control (Dashboard) - Carga de Datos y Métricas"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('es_admin', response.context)
        self.assertTrue(response.context['es_admin'])

    # =========================================================================
    # 4. LISTADO DE USUARIOS (listar_usuarios)
    # =========================================================================

    def test_4_listar_usuarios_admin(self):
        """4. Listado de Usuarios - Acceso Autorizado (Administrador)"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/listar.html')
        self.assertIn('usuarios', response.context)

    def test_4_listar_usuarios_cajero_denegado(self):
        """4. Listado de Usuarios - Acceso Restringido (Cajero)"""
        self.iniciar_sesion(self.cajero_user)
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    # =========================================================================
    # 5. VER PERFIL DE USUARIO (ver_perfil)
    # =========================================================================

    def test_5_ver_perfil(self):
        """5. Ver Perfil de Usuario - Carga de Datos Personales"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('ver_perfil', args=[self.cajero_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/perfil.html')
        self.assertEqual(response.context['usuario'], self.cajero_user)

    # =========================================================================
    # 6. REGISTRO DE USUARIOS (registrar_usuario)
    # =========================================================================

    def test_6_registrar_usuario_get(self):
        """6. Registro de Usuario (GET) - Carga del Formulario de Registro"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('registrar_usuario'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registrar.html')

    def test_6_registrar_usuario_post_success(self):
        """6. Registro de Usuario (POST) - Creación Exitosa de Nuevo Cajero"""
        self.iniciar_sesion(self.admin_user)
        data = {
            'txt_id': '1000000003',
            'txt_nombre': 'Nuevo Colaborador',
            'txt_contrasena': 'secure123',
            'txt_correo': 'nuevo@matpi.com',
            'txt_telefono': '3000000003',
            'txt_fecha_nacimiento': '1998-08-08',
            'txt_direccion': 'Calle Nueva 789',
            'txt_fecha_ingreso': '2026-05-21',
            'txt_eps': 'SURA',
            'txt_tipo_contrato': 'Indefinido',
            'txt_turno': 'Tarde'
        }
        response = self.client.post(reverse('registrar_usuario'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertTrue(Usuario.objects.filter(id='1000000003').exists())

    # =========================================================================
    # 7. EDICIÓN DE USUARIOS (editar_usuario)
    # =========================================================================

    def test_7_editar_usuario_get(self):
        """7. Editar Usuario (GET) - Carga del Formulario de Edición"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('editar_usuario', args=[self.cajero_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/editar.html')

    def test_7_editar_usuario_post_success(self):
        """7. Editar Usuario (POST) - Actualización Exitosa de Datos"""
        self.iniciar_sesion(self.admin_user)
        data = {
            'txt_id': self.cajero_user.id,
            'txt_nombre': 'Cajero Modificado',
            'txt_correo': 'cajeromod@matpi.com',
            'txt_telefono': '3009999999',
            'txt_fecha_nacimiento': '1995-05-05',
            'txt_direccion': 'Nueva Direccion 123',
            'txt_estado': 'Activo',
            'txt_eps': 'Sanitas',
            'txt_tipo_contrato': 'Fijo',
            'txt_turno': 'Noche',
            'txt_fecha_terminacion': '2026-12-31'
        }
        response = self.client.post(reverse('procesar_edicion'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        
        # Verificar actualización en la Base de Datos
        self.cajero_user.refresh_from_db()
        self.assertEqual(self.cajero_user.nombre_completo, 'Cajero Modificado')

    # =========================================================================
    # 8. ELIMINACIÓN DE USUARIOS (eliminar_usuario)
    # =========================================================================

    def test_8_eliminar_usuario_otro(self):
        """8. Eliminar Usuario - Eliminación Exitosa de un Cajero"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.post(reverse('eliminar_usuario', args=[self.cajero_user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertFalse(Usuario.objects.filter(id=self.cajero_user.id).exists())

    def test_8_eliminar_usuario_autodelete_denegado(self):
        """8. Eliminar Usuario - Restricción de Auto-Eliminación"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.post(reverse('eliminar_usuario', args=[self.admin_user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        # El administrador no debe haber sido borrado
        self.assertTrue(Usuario.objects.filter(id=self.admin_user.id).exists())

    # =========================================================================
    # 9. GENERACIÓN DE REPORTES EN PDF (reporte_modulo_pdf)
    # =========================================================================

    def test_9_reporte_modulo_pdf(self):
        """9. Reporte Módulo PDF - Descarga Exitosa de Archivo PDF"""
        self.iniciar_sesion(self.admin_user)
        response = self.client.get(reverse('generar_reporte', args=['clientes', 'general']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    # =========================================================================
    # 10. CONFIGURACIÓN DE METAS (actualizar_metas)
    # =========================================================================

    def test_10_actualizar_metas(self):
        """10. Actualizar Metas - Modificación Exitosa en DashboardConfig"""
        self.iniciar_sesion(self.admin_user)
        data = {
            'meta_reservas': 80,
            'meta_pedidos': 300
        }
        response = self.client.post(reverse('actualizar_metas'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Verificar actualización en Base de Datos
        self.dashboard_config.refresh_from_db()
        self.assertEqual(self.dashboard_config.meta_reservas, 80)
        self.assertEqual(self.dashboard_config.meta_pedidos, 300)