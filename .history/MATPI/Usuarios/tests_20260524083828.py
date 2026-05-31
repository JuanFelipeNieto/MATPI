from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Usuario, Administrador, Cajero, DashboardConfig

class UsuarioViewsCompleteTest(TestCase):
    def setUp(self):
        # Configuración inicial del Dashboard
        self.config = DashboardConfig.objects.create(id=1, meta_reservas=50, meta_pedidos=200)

        # 1. Crear un Administrador para pruebas
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Administrador de Pruebas",
            contraseña="adminpass123",
            correo_electronico="admin@matpi.com",
            telefono="3001234567",
            fecha_nacimiento="1990-01-01",
            direccion="Calle Falsa 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(
            usuario=self.admin_user,
            formacion_educativa="Ingeniería"
        )

        # 2. Crear un Cajero para pruebas
        self.cajero_user = Usuario.objects.create(
            id="0987654321",
            nombre_completo="Cajero de Pruebas",
            contraseña="cajeropass123",
            correo_electronico="cajero@matpi.com",
            telefono="3007654321",
            fecha_nacimiento="1995-05-05",
            direccion="Carrera Falsa 321",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.cajero = Cajero.objects.create(
            usuario=self.cajero_user,
            eps="SURA",
            tipo_contrato="Indefinido",
            turno="Mañana"
        )

    def login_como_admin(self):
        session = self.client.session
        session['usuario_id'] = self.admin_user.id
        session['usuario_nombre'] = self.admin_user.nombre_completo
        session.save()

    def login_como_cajero(self):
        session = self.client.session
        session['usuario_id'] = self.cajero_user.id
        session['usuario_nombre'] = self.cajero_user.nombre_completo
        session.save()

  
    # 1.Vista de inicio de sesion
    def test_01_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')
    
    # 2. Vista de inicio de sesion (Exitoso)
    def test_02_login_view_post_success(self):
        datos_login = {
            'txt_id': self.admin_user.id,
            'txt_contrasena': 'adminpass123'
        }
        response = self.client.post(reverse('login'), datos_login)
        # redirige al dashboard
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.client.session['usuario_id'], self.admin_user.id)

  
    # 3. Vista de inicio de sesion (Fallido)
    def test_03_login_view_post_fail(self):
        datos_login = {
            'txt_id': self.admin_user.id,
            'txt_contrasena': 'clave_incorrecta'
        }
        response = self.client.post(reverse('login'), datos_login)
        self.assertEqual(response.status_code, 200)
        # No debe haber sesión de usuario_id
        self.assertNotIn('usuario_id', self.client.session)

    # 4. cierre de sesion
    def test_04_logout_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('logout'))
        # Debe redirigir al inicio de sesion tras cerrar sesión
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('usuario_id', self.client.session)

    # 5. PRUEBA: Vista del Dashboard
    def test_05_dashboard_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('config', response.context)

    # 6. Lista de Usuarios
    def test_06_listar_usuarios_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/listar.html')
        self.assertIn('usuarios', response.context)

    # 7. Ver Perfil seleccionado
    def test_07_ver_perfil_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('ver_perfil', args=[self.cajero_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/perfil.html')
        self.assertEqual(response.context['usuario'], self.cajero_user)

    # 8.Registrar Usuario (Existoso)
    def test_09_registrar_usuario_post_success(self):
        self.login_como_admin()
        datos_registro = {
            'txt_id': '1122334455',
            'txt_nombre': 'Nuevo Colaborador',
            'txt_contrasena': 'secure123',
            'txt_correo': 'nuevo@matpi.com',
            'txt_telefono': '3123456789',
            'txt_fecha_nacimiento': '1998-10-10',
            'txt_direccion': 'Avenida Siempre Viva 742',
            'txt_fecha_ingreso': timezone.now().date().strftime('%Y-%m-%d'),
            'txt_eps': 'SURA',
            'txt_tipo_contrato': 'Indefinido',
            'txt_turno': 'Tarde',
            'txt_emergencia_nombre': 'Contacto Auxiliar',
            'txt_emergencia_parentesco': 'Hermano',
            'txt_emergencia_numero': '3159876543'
        }
        response = self.client.post(reverse('registrar_usuario'), datos_registro)
        # Redirección exitosa a la lista de usuarios
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertTrue(Usuario.objects.filter(id='1122334455').exists())
        self.assertTrue(Cajero.objects.filter(usuario_id='1122334455').exists())

    # 9. Registrar Usuario (Falla)
    def test_10_registrar_usuario_post_fail_validation(self):
        self.login_como_admin()
        datos_incorrectos = {
            'txt_id': '123',  # Documento inválido (Debe ser de 10 caracteres)
            'txt_nombre': 'Erróneo',
            'txt_contrasena': 'pass',
            'txt_fecha_ingreso': timezone.now().date().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('registrar_usuario'), datos_incorrectos)
        # Debe recargar la misma página mostrando el error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registrar.html')
        self.assertFalse(Usuario.objects.filter(id='123').exists())



    
    # 1. PRUEBA: Editar Usuario (POST Exitoso) 
   
    def test_12_editar_usuario_post_success(self):
        """12. test_editar_usuario_post_success: Verifica la actualización correcta de la información del Cajero."""
        self.login_como_admin()
        datos_edicion = {
            'txt_id': self.cajero_user.id,
            'txt_nombre': 'Cajero Editado Exitosamente',
            'txt_correo': 'cajero_editado@matpi.com',
            'txt_telefono': '3209876543',
            'txt_fecha_nacimiento': '1995-05-05',
            'txt_direccion': 'Calle Nueva 789',
            'txt_estado': 'Activo',
            'txt_eps': 'Sanitas',
            'txt_tipo_contrato': 'Fijo',
            'txt_fecha_terminacion': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'txt_turno': 'Noche',
            'txt_emergencia_nombre': 'Contacto Madre',
            'txt_emergencia_parentesco': 'Madre',
            'txt_emergencia_numero': '3101112222'
        }
        # En la app, la edición se procesa a través de la URL de procesar_edicion (editar/guardar/) vía POST
        response = self.client.post(reverse('procesar_edicion'), datos_edicion)
        self.assertRedirects(response, reverse('listar_usuarios'))
        
        # Validar cambios
        self.cajero_user.refresh_from_db()
        self.cajero.refresh_from_db()
        self.assertEqual(self.cajero_user.nombre_completo, 'Cajero Editado Exitosamente')
        self.assertEqual(self.cajero.eps, 'Sanitas')
        self.assertEqual(self.cajero.tipo_contrato, 'Fijo')

    
    # 11 Eliminar Usuario (Exitoso)
    
    def test_13_eliminar_usuario_success(self):
        """13. test_eliminar_usuario_success: Verifica que el administrador pueda eliminar a un cajero."""
        self.login_como_admin()
        cajero_a_eliminar_id = self.cajero_user.id
        response = self.client.post(reverse('eliminar_usuario', args=[cajero_a_eliminar_id]))
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertFalse(Usuario.objects.filter(id=cajero_a_eliminar_id).exists())

    # ==========================================
    # 14. PRUEBA: Eliminar Usuario (Auto-eliminación bloqueada)
    # ==========================================
    def test_14_eliminar_usuario_self_fail(self):
        """14. test_eliminar_usuario_self_fail: Evita que un administrador se elimine a sí mismo del sistema."""
        self.login_como_admin()
        response = self.client.post(reverse('eliminar_usuario', args=[self.admin_user.id]))
        self.assertRedirects(response, reverse('listar_usuarios'))
        # El administrador no debe haber sido eliminado
        self.assertTrue(Usuario.objects.filter(id=self.admin_user.id).exists())

    # ==========================================
    # 15. PRUEBA: Reporte Módulo PDF (Usuarios)
    # ==========================================
    
    def test_15_reporte_modulo_pdf(self):
        """15. test_reporte_modulo_pdf: Verifica la generación y descarga en PDF del reporte de colaboradores."""
        self.login_como_admin()
        response = self.client.get(reverse('generar_reporte', kwargs={'modulo': 'usuarios', 'periodo': 'general'}))
        # Debe retornar el archivo PDF listo para descarga
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="MATPI_usuarios.pdf"', response['Content-Disposition'])

    # ==========================================
    # 16. PRUEBA: Actualizar Metas
    # ==========================================
    def test_16_actualizar_metas(self):
        """16. test_actualizar_metas: Verifica que el administrador pueda cambiar las metas globales del negocio."""
        self.login_como_admin()
        datos_metas = {
            'meta_reservas': 100,
            'meta_pedidos': 350
        }
        response = self.client.post(reverse('actualizar_metas'), datos_metas)
        self.assertRedirects(response, reverse('dashboard'))
        
        # Validar actualización en BD
        self.config.refresh_from_db()
        self.assertEqual(self.config.meta_reservas, 100)
        self.assertEqual(self.config.meta_pedidos, 350)

