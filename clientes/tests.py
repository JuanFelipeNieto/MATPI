from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Cliente
from usuarios.models import Usuario, Administrador

class ClienteViewsTest(TestCase):
    def setUp(self):
        # Crear usuario para la sesión y asignaciones
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Admin Clientes",
            contraseña="adminpass123",
            correo_electronico="admin@matpi.com",
            telefono="3001234567",
            fecha_nacimiento="1990-01-01",
            direccion="Calle 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(usuario=self.admin_user)

        self.cliente = Cliente.objects.create(
            id=1020304050,
            nombre_completo="Juan Perez",
            telefono="3009876543",
            direccion="Calle Falsa 123",
            localidad="Usaquén",
            usuario=self.admin_user
        )

    def login_como_admin(self):
        session = self.client.session
        session['usuario_id'] = self.admin_user.id
        session['usuario_nombre'] = self.admin_user.nombre_completo
        session.save()

    def test_listar_clientes_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_clientes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/listar.html')
        self.assertIn('clientes', response.context)

    def test_listar_clientes_buscar(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_clientes') + '?buscar=Juan')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.cliente, response.context['clientes'])

    def test_mostrar_registro_cliente_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('mostrar_registro_cliente'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/registrar.html')

    def test_registrar_cliente_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_id': '9876543210',
            'txt_nombre': 'Maria Gomez',
            'txt_telefono': '3123456789',
            'txt_direccion': 'Carrera 7',
            'txt_localidad': 'Chapinero'
        }
        response = self.client.post(reverse('registrar_cliente'), datos)
        self.assertRedirects(response, reverse('listar_clientes'))
        self.assertTrue(Cliente.objects.filter(id=9876543210).exists())

    def test_registrar_cliente_post_fail_validation(self):
        self.login_como_admin()
        datos = {
            'txt_id': '123',  # Menos de 10 caracteres
            'txt_nombre': 'Ma',  # Menos de 3 caracteres
            'txt_telefono': '312',  # Menos de 6 caracteres
            'txt_direccion': 'Carrera 7',
            'txt_localidad': 'Chapinero'
        }
        response = self.client.post(reverse('registrar_cliente'), datos)
        # Recarga la vista mostrando el error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/registrar.html')
        self.assertFalse(Cliente.objects.filter(id=123).exists())

    def test_pre_editar_cliente_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('pre_editar_cliente', args=[self.cliente.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/editar.html')
        self.assertEqual(response.context['cliente'], self.cliente)

    def test_editar_cliente_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_id': self.cliente.id,
            'txt_nombre': 'Juan Perez Editado',
            'txt_telefono': '3001112233',
            'txt_direccion': 'Calle Nueva 456',
            'txt_localidad': 'Suba',
            'txt_cajero': self.admin_user.id
        }
        response = self.client.post(reverse('editar_cliente'), datos)
        self.assertRedirects(response, reverse('listar_clientes'))
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nombre_completo, 'Juan Perez Editado')

    def test_eliminar_cliente_success(self):
        self.login_como_admin()
        response = self.client.post(reverse('eliminar_cliente', args=[self.cliente.id]))
        self.assertRedirects(response, reverse('listar_clientes'))
        self.assertFalse(Cliente.objects.filter(id=self.cliente.id).exists())
