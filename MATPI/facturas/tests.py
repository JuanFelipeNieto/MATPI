from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Factura
from pedidos.models import Pedido
from usuarios.models import Usuario, Cajero
from clientes.models import Cliente

class FacturaViewsTest(TestCase):
    def setUp(self):
        # Crear usuario para la sesión y cajero
        self.cajero_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Cajero Facturas",
            contraseña="cajeropass123",
            correo_electronico="cajero@matpi.com",
            telefono="3001234567",
            fecha_nacimiento="1990-01-01",
            direccion="Calle 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.cajero = Cajero.objects.create(usuario=self.cajero_user)

        self.cliente = Cliente.objects.create(
            id=1020304050,
            nombre_completo="Juan Perez",
            telefono="3009876543",
            direccion="Calle Falsa 123",
            localidad="Usaquén",
            usuario=self.cajero_user
        )

        self.pedido = Pedido.objects.create(
            estado='Registrado',
            valor=10000,
            numero_orden=1,
            metodo_pago='Efectivo',
            usuario=self.cajero_user,
            cliente=self.cliente
        )

        self.factura = Factura.objects.create(
            id=1,
            valor_total=10800,
            descripcion="Hamburguesa + Coca Cola",
            iva=8.0,
            pedido=self.pedido
        )

    def login_como_cajero(self):
        session = self.client.session
        session['usuario_id'] = self.cajero_user.id
        session['usuario_nombre'] = self.cajero_user.nombre_completo
        session.save()

    def test_listar_facturas_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('listar_facturas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facturas/listar.html')
        self.assertIn('facturas', response.context)

    def test_mostrar_registro_factura_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('mostrar_registro_factura'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facturas/registrar.html')

    def test_mostrar_registro_factura_con_pedido_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('mostrar_registro_factura') + f'?pedido_id={self.pedido.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facturas/registrar.html')
        self.assertEqual(response.context['pedido_seleccionado'], self.pedido)

    def test_registrar_factura_post_success(self):
        self.login_como_cajero()

        # Crear otro pedido para facturar
        otro_pedido = Pedido.objects.create(
            estado='Registrado',
            valor=15000,
            numero_orden=2,
            metodo_pago='Nequi',
            usuario=self.cajero_user,
            cliente=self.cliente
        )

        datos = {
            'txt_id': '2',
            'txt_valor_total': '16200',
            'txt_descripcion': 'Hamburguesa Especial',
            'txt_iva': '8.0',
            'txt_pedido': otro_pedido.id
        }
        response = self.client.post(reverse('registrar_factura'), datos)
        self.assertRedirects(response, reverse('listar_facturas'))

        # Validar persistencia y cambio de estado del pedido
        self.assertTrue(Factura.objects.filter(id=2).exists())
        otro_pedido.refresh_from_db()
        self.assertEqual(otro_pedido.estado, 'Preparacion')

    def test_eliminar_factura_blocked(self):
        self.login_como_cajero()
        response = self.client.post(reverse('eliminar_factura', args=[self.factura.id]))
        self.assertRedirects(response, reverse('listar_facturas'))
        # La factura debe seguir existiendo por integridad contable
        self.assertTrue(Factura.objects.filter(id=self.factura.id).exists())
