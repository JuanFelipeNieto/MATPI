from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Usuario, Administrador, Cajero, DashboardConfig

class UsuarioViewsTest(TestCase):
    def setUp(self):
        # 1. Configuración de datos comunes para las pruebas
        # Usuario Administrador
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Administrador de Pruebas",
            contraseña="admin123",
            correo_electronico="admin@pruebas.com",
            telefono="3101234567",
            fecha_nacimiento="1990-05-15",
            direccion="Calle Falsa 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(
            usuario=self.admin_user,
            formacion_educativa="Ingeniero de Sistemas"
        )
        
        # Usuario Cajero
        self.cajero_user = Usuario.objects.create(
            id="0987654321",
            nombre_completo="Cajero de Pruebas",
            contraseña="cajero123",
            correo_electronico="cajero@pruebas.com",
            telefono="3201234567",
            fecha_nacimiento="1995-10-20",
            direccion="Carrera Falsa 456",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.cajero = Cajero.objects.create(
            usuario=self.cajero_user,
            eps="SURA",
            tipo_contrato="Indefinido",
            turno="Mañana"
        )
        
        # Configuración por defecto del dashboard
        self.db_config = DashboardConfig.objects.create(id=1, meta_reservas=50, meta_pedidos=200)

    def login_admin(self):
        #Simulacion de inicio de sesion
        session = self.client.session
        session['usuario_id'] = self.admin_user.id
        session['usuario_nombre'] = self.admin_user.nombre_completo
        session.save()

    def login_cajero(self):
        """Helper para simular inicio de sesión de cajero."""
        session = self.client.session
        session['usuario_id'] = self.cajero_user.id
        session['usuario_nombre'] = self.cajero_user.nombre_completo
        session.save()

    # 1. login_view (GET)
    def test_login_view_get(self):
        """1. login_view (GET): Verifica el acceso a la pantalla de login"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    # 2. login_view (POST - Éxito)
    def test_login_view_post_success(self):
        """2. login_view (POST - Éxito): Autenticación exitosa y redirección al Dashboard"""
        response = self.client.post(reverse('login'), {
            'txt_id': '1234567890',
            'txt_contrasena': 'admin123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.client.session.get('usuario_id'), '1234567890')

    # 3. login_view (POST - Fallo)
    def test_login_view_post_failure(self):
        """3. login_view (POST - Fallo): Intento de login con credenciales incorrectas"""
        response = self.client.post(reverse('login'), {
            'txt_id': '1234567890',
            'txt_contrasena': 'clave_incorrecta'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')
        self.assertNotIn('usuario_id', self.client.session)

    # 4. logout_view
    def test_logout_view(self):
        """4. logout_view: Cierre de sesión y limpieza de datos en sesión"""
        self.login_admin()
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('usuario_id', self.client.session)

    # 5. dashboard (Sin Login)
    def test_dashboard_sin_login(self):
        """5. dashboard (Sin Login): Redirección si se intenta acceder sin sesión iniciada"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    # 6. dashboard (Con Login)
    def test_dashboard_con_login(self):
        """6. dashboard (Con Login): Acceso exitoso y carga de datos del dashboard"""
        self.login_admin()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('es_admin', response.context)
        self.assertTrue(response.context['es_admin'])

    # 7. listar_usuarios (Denegado para Cajeros)
    def test_listar_usuarios_denegado_cajero(self):
        """7. listar_usuarios (Denegado): Cajeros no tienen acceso a listar usuarios"""
        self.login_cajero()
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    # 8. listar_usuarios (Permitido para Administrador)
    def test_listar_usuarios_permitido_admin(self):
        """8. listar_usuarios (Permitido): Administradores pueden ver la lista de cajeros"""
        self.login_admin()
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/listar.html')
        self.assertIn('usuarios', response.context)

    # 9. listar_usuarios (Búsqueda)
    def test_listar_usuarios_busqueda(self):
        """9. listar_usuarios (Búsqueda): Filtrado de usuarios por término de búsqueda"""
        self.login_admin()
        response = self.client.get(reverse('listar_usuarios'), {'buscar': 'Cajero'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usuarios', response.context)
        self.assertEqual(response.context['usuarios'].count(), 1)
        self.assertEqual(response.context['usuarios'].first().nombre_completo, "Cajero de Pruebas")

    # 10. ver_perfil
    def test_ver_perfil(self):
        """10. ver_perfil: Visualización del perfil detallado de un cajero"""
        self.login_admin()
        response = self.client.get(reverse('ver_perfil', kwargs={'id': self.cajero_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/perfil.html')
        self.assertEqual(response.context['usuario'].id, self.cajero_user.id)

    # 11. registrar_usuario (GET)
    def test_registrar_usuario_get(self):
        """11. registrar_usuario (GET): Carga del formulario de registro de cajeros"""
        self.login_admin()
        response = self.client.get(reverse('registrar_usuario'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registrar.html')

    # 12. registrar_usuario (POST - Éxito)
    def test_registrar_usuario_post_success(self):
        """12. registrar_usuario (POST - Éxito): Creación de un nuevo cajero con datos válidos"""
        self.login_admin()
        
        # Simular un archivo PDF para la experiencia laboral
        pdf_file = SimpleUploadedFile("experiencia.pdf", b"pdf_content", content_type="application/pdf")
        
        response = self.client.post(reverse('registrar_usuario'), {
            'txt_id': '1122334455',
            'txt_nombre': 'Nuevo Cajero Test',
            'txt_contrasena': 'contrasenia123',
            'txt_correo': 'nuevo@cajero.com',
            'txt_telefono': '3331112222',
            'txt_fecha_nacimiento': '1998-12-12',
            'txt_direccion': 'Avenida Central 789',
            'txt_fecha_ingreso': '2026-01-01',
            'txt_eps': 'SURA',
            'txt_tipo_contrato': 'Fijo',
            'txt_fecha_terminacion': '2026-12-31',
            'txt_turno': 'Tarde',
            'txt_emergencia_nombre': 'Contacto de Emergencia',
            'txt_emergencia_parentesco': 'Familiar',
            'txt_emergencia_numero': '3159876543',
            'txt_experiencia': pdf_file
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertTrue(Usuario.objects.filter(id='1122334455').exists())
        self.assertTrue(Cajero.objects.filter(usuario_id='1122334455').exists())

    # 13. registrar_usuario (POST - Fallo Validación)
    def test_registrar_usuario_post_failure_validation(self):
        """13. registrar_usuario (POST - Fallo Validación): Error por longitud incorrecta del documento"""
        self.login_admin()
        # El documento debe tener exactamente 10 caracteres
        response = self.client.post(reverse('registrar_usuario'), {
            'txt_id': '123',
            'txt_nombre': 'Cajero Corto',
            'txt_contrasena': 'pwd',
            'txt_correo': 'corto@cajero.com',
            'txt_fecha_ingreso': '2026-01-01'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registrar.html')
        self.assertFalse(Usuario.objects.filter(id='123').exists())

    # 14. editar_usuario (GET)
    def test_editar_usuario_get(self):
        """14. editar_usuario (GET): Carga del formulario de edición cargado con datos actuales"""
        self.login_admin()
        response = self.client.get(reverse('editar_usuario', kwargs={'id': self.cajero_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/editar.html')
        self.assertEqual(response.context['usuario'].id, self.cajero_user.id)

    # 15. editar_usuario (POST - Éxito)
    def test_editar_usuario_post_success(self):
        """15. editar_usuario (POST - Éxito): Edición de datos de un usuario"""
        self.login_admin()
        response = self.client.post(reverse('procesar_edicion'), {
            'txt_id': self.cajero_user.id,
            'txt_nombre': 'Cajero Editado',
            'txt_correo': 'editado@cajero.com',
            'txt_telefono': '3000000000',
            'txt_fecha_nacimiento': '1995-10-20',
            'txt_direccion': 'Nueva Direccion 789',
            'txt_fecha_ingreso': '2026-05-21',
            'txt_estado': 'Activo',
            'txt_eps': 'Compensar',
            'txt_tipo_contrato': 'Indefinido',
            'txt_turno': 'Noche',
            'txt_emergencia_nombre': 'Contacto Nuevo',
            'txt_emergencia_parentesco': 'Hermano',
            'txt_emergencia_numero': '3200000000'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.cajero_user.refresh_from_db()
        self.assertEqual(self.cajero_user.nombre_completo, 'Cajero Editado')

    # 16. editar_usuario (POST - Fallo Validación)
    def test_editar_usuario_post_failure_validation(self):
        """16. editar_usuario (POST - Fallo Validación): Error al ingresar números en el nombre"""
        self.login_admin()
        response = self.client.post(reverse('procesar_edicion'), {
            'txt_id': self.cajero_user.id,
            'txt_nombre': 'Nombre Con Numeros 123',
            'txt_correo': 'error@cajero.com'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('editar_usuario', kwargs={'id': self.cajero_user.id}))
        self.cajero_user.refresh_from_db()
        self.assertNotEqual(self.cajero_user.nombre_completo, 'Nombre Con Numeros 123')

    # 17. eliminar_usuario (Éxito)
    def test_eliminar_usuario_success(self):
        """17. eliminar_usuario: Eliminación de un cajero por parte de un administrador"""
        self.login_admin()
        response = self.client.get(reverse('eliminar_usuario', kwargs={'id': self.cajero_user.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertFalse(Usuario.objects.filter(id=self.cajero_user.id).exists())

    # 18. eliminar_usuario (Fallo por autoeliminación)
    def test_eliminar_usuario_no_autoeliminar(self):
        """18. eliminar_usuario (Autoeliminación): Evita que el administrador se autoelimine"""
        self.login_admin()
        response = self.client.get(reverse('eliminar_usuario', kwargs={'id': self.admin_user.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertTrue(Usuario.objects.filter(id=self.admin_user.id).exists())

    # 19. reporte_modulo_pdf
    def test_reporte_modulo_pdf_usuarios(self):
        """19. reporte_modulo_pdf: Descarga de reporte de usuarios en formato PDF"""
        self.login_admin()
        response = self.client.get(reverse('generar_reporte', kwargs={'modulo': 'usuarios', 'periodo': 'general'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    # 20. actualizar_metas
    def test_actualizar_metas(self):
        """20. actualizar_metas: Modificación de metas de reservas y pedidos"""
        self.login_admin()
        response = self.client.post(reverse('actualizar_metas'), {
            'meta_reservas': '80',
            'meta_pedidos': '250'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))
        
        self.db_config.refresh_from_db()
        self.assertEqual(self.db_config.meta_reservas, 80)
        self.assertEqual(self.db_config.meta_pedidos, 250)
