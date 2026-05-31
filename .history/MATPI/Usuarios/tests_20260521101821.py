from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Usuario, Administrador, Cajero

def crear_usuario(id, nombre, contrasena, rol='cajero', estado='Activo'):
    """Helper para crear usuarios rápidos en los tests."""
    usuario = Usuario.objects.create(
        id=id,
        nombre_completo=nombre,
        contraseña=contrasena,
        correo_electronico=f"{nombre.lower().replace(' ', '')}@test.com",
        telefono="3001234567",
        fecha_nacimiento="1995-05-15",
        direccion="Calle Falsa 123",
        fecha_ingreso=timezone.now().date(),
        estado=estado
    )
    if rol == 'admin':
        Administrador.objects.create(usuario=usuario, formacion_educativa="Ingeniería")
    else:
        Cajero.objects.create(
            usuario=usuario,
            eps="SURA",
            tipo_contrato="Indefinido",
            turno="Mañana",
            contacto_emergencia_nombre="Contacto Prueba",
            contacto_emergencia_parentesco="Madre",
            contacto_emergencia_numero="3109876543"
        )
    return usuario


class AutenticacionTests(TestCase):
    #Login y cierre de sesion de usuarios

    def setUp(self):
        self.usuario = crear_usuario("1000000001", "Cajero Test", "clave123", rol='cajero')

    def test_ver_formulario_login(self):
        # Comentario: Verifica la carga exitosa (código 200) del formulario de login.
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    def test_login_exitoso(self):
        # Comentario: Verifica que un inicio de sesión válido redirija al Dashboard y guarde la sesión.
        datos_login = {
            'txt_id': '1000000001',
            'txt_contrasena': 'clave123'
        }
        response = self.client.post(reverse('login'), datos_login)
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.client.session['usuario_id'], '1000000001')

    def test_login_fallido(self):
        # Comentario: Verifica que el login falle con clave incorrecta y permanezca en la plantilla de login.
        datos_login = {
            'txt_id': '1000000001',
            'txt_contrasena': 'clave_incorrecta'
        }
        response = self.client.post(reverse('login'), datos_login)
        self.assertEqual(response.status_code, 200)  # Se queda en la misma página
        self.assertTemplateUsed(response, 'usuarios/login.html')

    def test_logout(self):
        # Comentario: Verifica que al cerrar sesión se redirija a login y se limpie la sesión actual.
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('usuario_id', self.client.session)


class DashboardTests(TestCase):
    """Pruebas unitarias para el acceso y renderizado del Dashboard."""

    def setUp(self):
        self.admin = crear_usuario("1000000002", "Admin Test", "admin123", rol='admin')
        self.cajero = crear_usuario("1000000003", "Cajero Test", "cajero123", rol='cajero')

    def test_dashboard_requiere_login(self):
        # Comentario: Verifica que no se pueda acceder al Dashboard sin haber iniciado sesión.
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, reverse('login'))

    def test_dashboard_acceso_admin(self):
        # Comentario: Verifica que un Administrador pueda entrar al Dashboard y ver los datos administrativos.
        session = self.client.session
        session['usuario_id'] = self.admin.id
        session['usuario_nombre'] = self.admin.nombre_completo
        session.save()

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['es_admin'])
        self.assertEqual(response.context['usuario_nombre'], "Admin Test")

    def test_dashboard_acceso_cajero(self):
        # Comentario: Verifica que un Cajero pueda entrar al Dashboard pero sin bandera de administrador.
        session = self.client.session
        session['usuario_id'] = self.cajero.id
        session['usuario_nombre'] = self.cajero.nombre_completo
        session.save()

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['es_admin'])


class GestionUsuariosTests(TestCase):
    """Pruebas unitarias para el CRUD y gestión de usuarios (exclusivo de Admin)."""

    def setUp(self):
        self.admin = crear_usuario("1000000002", "Admin Test", "admin123", rol='admin')
        self.cajero = crear_usuario("1000000003", "Cajero Test", "cajero123", rol='cajero')
        
    def login_como(self, usuario):
        """Método auxiliar para simular el inicio de sesión de un usuario."""
        session = self.client.session
        session['usuario_id'] = usuario.id
        session['usuario_nombre'] = usuario.nombre_completo
        session.save()

    def test_listar_usuarios_denegado_cajero(self):
        # Comentario: Verifica que un Cajero tenga denegado el acceso al listado general de usuarios.
        self.login_como(self.cajero)
        response = self.client.get(reverse('listar_usuarios'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_listar_usuarios_permitido_admin(self):
        # Comentario: Verifica que un Administrador pueda listar exitosamente a todos los usuarios del sistema.
        self.login_como(self.admin)
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('usuarios', response.context)
        self.assertTemplateUsed(response, 'usuarios/listar.html')

    def test_ver_perfil(self):
        # Comentario: Verifica que un usuario logueado pueda visualizar la información detallada de su perfil.
        self.login_como(self.cajero)
        response = self.client.get(reverse('ver_perfil', args=[self.cajero.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['usuario'].id, self.cajero.id)
        self.assertTemplateUsed(response, 'usuarios/perfil.html')

    def test_registrar_usuario_exitoso(self):
        # Registro de un cajero por parte del administrador
        self.login_como(self.admin)
        
        datos_registro = {
            'txt_id': '2000000001',
            'txt_nombre': 'Nuevo Colaborador',
            'txt_contrasena': 'securepass',
            'txt_correo': 'nuevo@test.com',
            'txt_telefono': '3124567890',
            'txt_fecha_nacimiento': '2000-01-01',
            'txt_direccion': 'Avenida Siempre Viva 742',
            'txt_fecha_ingreso': '2026-05-21',
            'txt_eps': 'SURA',
            'txt_tipo_contrato': 'Indefinido',
            'txt_turno': 'Tarde',
            'txt_emergencia_nombre': 'Contacto Emergencia',
            'txt_emergencia_parentesco': 'Hermano',
            'txt_emergencia_numero': '3151234567'
        }
        
        response = self.client.post(reverse('registrar_usuario'), datos_registro)
        self.assertRedirects(response, reverse('listar_usuarios'))
        
        # Comprobar persistencia en base de datos
        self.assertTrue(Usuario.objects.filter(id='2000000001').exists())
        self.assertTrue(Cajero.objects.filter(usuario_id='2000000001').exists())

    def test_registrar_usuario_validacion_id_invalido(self):
        # Comentario: Verifica que el formulario falle al registrar si la longitud del documento de identidad es inválida.
        self.login_como(self.admin)
        
        datos_registro = {
            'txt_id': '12345',  # Inválido por longitud
            'txt_nombre': 'Nombre Invalido',
            'txt_contrasena': 'securepass',
            'txt_fecha_ingreso': '2026-05-21',
        }
        
        response = self.client.post(reverse('registrar_usuario'), datos_registro)
        self.assertEqual(response.status_code, 200)  # Carga de nuevo el form con errores
        self.assertFalse(Usuario.objects.filter(id='12345').exists())

    def test_eliminar_usuario_exitoso(self):
        # Comentario: Verifica que un Administrador pueda eliminar de forma exitosa a un Cajero.
        self.login_como(self.admin)
        
        response = self.client.get(reverse('eliminar_usuario', args=[self.cajero.id]))
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertFalse(Usuario.objects.filter(id=self.cajero.id).exists())
    def test_eliminar_usuario_a_si_mismo_no_permitido(self):
        # Comentario: Verifica que un Administrador no tenga permitido eliminarse a sí mismo por seguridad.
        self.login_como(self.admin)
        
        response = self.client.get(reverse('eliminar_usuario', args=[self.admin.id]))
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertTrue(Usuario.objects.filter(id=self.admin.id).exists())



