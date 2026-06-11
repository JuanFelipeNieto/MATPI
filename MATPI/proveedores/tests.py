from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Proveedor, DetalleProveedorMateriaP
from usuarios.models import Usuario, Administrador, Cajero
from materia_prima.models import MateriaPrima

class ProveedorViewsTest(TestCase):
    def setUp(self):
        # Crear admin y cajero
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Admin Proveedores",
            contraseña="adminpass123",
            correo_electronico="admin@matpi.com",
            telefono="3001234567",
            fecha_nacimiento="1990-01-01",
            direccion="Calle 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(usuario=self.admin_user)
        
        self.cajero_user = Usuario.objects.create(
            id="0987654321",
            nombre_completo="Cajero Proveedores",
            contraseña="cajeropass123",
            correo_electronico="cajero@matpi.com",
            telefono="3007654321",
            fecha_nacimiento="1995-05-05",
            direccion="Carrera 321",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.cajero = Cajero.objects.create(usuario=self.cajero_user)

        self.proveedor = Proveedor.objects.create(
            nombre_proveedor="Distribuidora Carnes",
            direccion="Calle 45",
            correo_electronico="carnes@distribuidora.com",
            telefono="3111111111"
        )

        self.materia = MateriaPrima.objects.create(
            nombre_materia_prima="Lomo de Res",
            unidad_medida="g",
            cantidad_por_unidad=1,
            tipo="Comida"
        )

    def login_como_admin(self):
        session = self.client.session
        session['usuario_id'] = self.admin_user.id
        session['usuario_nombre'] = self.admin_user.nombre_completo
        session.save()

    def test_listar_proveedores_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_proveedores'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/listar.html')

    def test_mostrar_registro_proveedor_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('mostrar_registro_proveedor'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/registrar.html')

    def test_registrar_proveedor_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_nombre': 'Nuevo Proveedor S.A.',
            'txt_direccion': 'Calle Nueva 99',
            'txt_correo': 'nuevo@prov.com',
            'txt_telefono': '3000000000'
        }
        response = self.client.post(reverse('registrar_proveedor'), datos)
        self.assertRedirects(response, reverse('listar_proveedores'))
        self.assertTrue(Proveedor.objects.filter(nombre_proveedor='Nuevo Proveedor S.A.').exists())

    def test_pre_editar_proveedor_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('pre_editar_proveedor', args=[self.proveedor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/editar.html')

    def test_editar_proveedor_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_id': self.proveedor.id,
            'txt_nombre': 'Proveedor Editado S.A.S.',
            'txt_direccion': self.proveedor.direccion,
            'txt_correo': self.proveedor.correo_electronico,
            'txt_telefono': self.proveedor.telefono
        }
        response = self.client.post(reverse('editar_proveedor'), datos)
        self.assertRedirects(response, reverse('listar_proveedores'))
        self.proveedor.refresh_from_db()
        self.assertEqual(self.proveedor.nombre_proveedor, 'Proveedor Editado S.A.S.')

    def test_eliminar_proveedor_success(self):
        self.login_como_admin()
        response = self.client.post(reverse('eliminar_proveedor', args=[self.proveedor.id]))
        self.assertRedirects(response, reverse('listar_proveedores'))
        self.assertFalse(Proveedor.objects.filter(id=self.proveedor.id).exists())

    def test_mostrar_registro_suministro_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('mostrar_registro_suministro', args=[self.proveedor.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proveedores/registrar_suministro.html')

    def test_registrar_suministro_materia_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_proveedor_id': self.proveedor.id,
            'txt_materia_id': self.materia.id,
            'txt_cantidad': '50',
            'txt_precio': '1500',
            'txt_fecha': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'txt_vencimiento': (timezone.now().date() + timedelta(days=5)).strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('registrar_suministro_materia'), datos)
        self.assertRedirects(response, reverse('listar_proveedores'))
        self.assertTrue(DetalleProveedorMateriaP.objects.filter(proveedor=self.proveedor, materia_prima=self.materia).exists())
