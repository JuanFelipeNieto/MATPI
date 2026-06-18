from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Pedido, DetallePedidoProducto
from usuarios.models import Usuario, Cajero, Administrador
from clientes.models import Cliente
from productos.models import Producto
from materia_prima.models import MateriaPrima, Lote, DetalleProductoMateriaP
from reservas.models import Reserva

class PedidoViewsTest(TestCase):
    def setUp(self):
        # Crear usuario para la sesión y cajero
        self.cajero_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Cajero Pedidos",
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

        self.materia = MateriaPrima.objects.create(
            nombre_materia_prima="Carne",
            unidad_medida="g",
            cantidad_por_unidad=150,
            tipo="Comida"
        )
        self.lote = Lote.objects.create(
            materia_prima=self.materia,
            cantidad_inicial=10,
            cantidad_actual=10,
            precio_unidad=2000
        )

        self.producto = Producto.objects.create(
            nombre_producto="Hamburguesa Sencilla",
            precio=12000,
            categoria="Hamburguesas",
            cantidad=10
        )
        self.detalle_materia = DetalleProductoMateriaP.objects.create(
            producto=self.producto,
            materia_prima=self.materia,
            cantidad_usada=150.0,
            unidad_medida="g"
        )

        self.pedido = Pedido.objects.create(
            estado='Registrado',
            valor=12000,
            numero_orden=1,
            metodo_pago='Efectivo',
            usuario=self.cajero_user,
            cliente=self.cliente
        )
        self.detalle_pedido = DetallePedidoProducto.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=1,
            precio_unitario=12000
        )

    def login_como_cajero(self):
        session = self.client.session
        session['usuario_id'] = self.cajero_user.id
        session['usuario_nombre'] = self.cajero_user.nombre_completo
        session.save()

    def test_listar_pedidos_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('listar_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/listar.html')

    def test_detalles_pedido_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('detalles_pedido', args=[self.pedido.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/detalles.html')
        self.assertEqual(response.context['pedido'], self.pedido)

    def test_mostrar_registro_pedido_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('mostrar_registro_pedido'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/registrar.html')

    def test_registrar_pedido_post_success(self):
        self.login_como_cajero()
        datos = {
            'txt_cliente_id': self.cliente.id,
            'txt_cliente_search': f"{self.cliente.nombre_completo} ({self.cliente.id})",
            'txt_numero_orden': '2',
            'txt_metodo_pago': 'Nequi',
            'producto_id[]': [self.producto.id],
            'producto_cantidad[]': ['1'],
            'producto_exclusiones_0[]': [],
            'producto_notas_0': 'Sin cebolla'
        }
        response = self.client.post(reverse('registrar_pedido'), datos)
        # Redirige a facturas/registrar con el nuevo pedido id
        self.assertEqual(response.status_code, 302)
        self.assertIn('/facturas/registrar/', response.url)

    def test_pre_editar_pedido_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('pre_editar_pedido', args=[self.pedido.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/editar.html')

    def test_editar_pedido_post_success(self):
        self.login_como_cajero()
        datos = {
            'txt_id': self.pedido.id,
            'txt_metodo_pago': 'Tarjeta Débito',
            'txt_cajero': self.cajero_user.id,
            'txt_cliente': self.cliente.id,
            'producto_id[]': [self.producto.id],
            'producto_cantidad[]': ['2'],
            'producto_exclusiones_0[]': [],
            'producto_notas_0': 'Editado'
        }
        response = self.client.post(reverse('editar_pedido'), datos)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/facturas/registrar/', response.url)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.metodo_pago, 'Tarjeta Débito')

    def test_pedidos_pendientes_get(self):
        self.login_como_cajero()
        # Cambiamos estado para que aparezca en pendientes
        self.pedido.estado = 'Preparacion'
        self.pedido.save()
        response = self.client.get(reverse('pedidos_pendientes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/pendientes.html')
        self.assertIn(self.pedido, response.context['pedidos'])

    def test_entregar_pedido_success(self):
        self.login_como_cajero()
        self.pedido.estado = 'Preparacion'
        self.pedido.save()
        response = self.client.post(reverse('entregar_pedido', args=[self.pedido.id]))
        self.assertRedirects(response, reverse('pedidos_pendientes'))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'Completado')

    def test_cancelar_pedido_success(self):
        self.login_como_cajero()
        response = self.client.post(reverse('cancelar_pedido', args=[self.pedido.id]))
        self.assertRedirects(response, reverse('listar_pedidos'))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'Cancelado')

    def test_cocina_get(self):
        self.login_como_cajero()
        self.pedido.estado = 'Preparacion'
        self.pedido.save()
        response = self.client.get(reverse('cocina'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/cocina.html')

    def test_mostrar_registro_pedido_excluye_vencidos_y_sin_stock(self):
        self.login_como_cajero()

        # 1. Producto con ingrediente vencido
        self.lote.fecha_vencimiento = timezone.now().date() - timedelta(days=1)
        self.lote.save()
        response = self.client.get(reverse('mostrar_registro_pedido'))
        self.assertNotIn(self.producto, response.context['productos'])

        # 2. Producto con ingrediente sin stock (pero no vencido)
        self.lote.fecha_vencimiento = timezone.now().date() + timedelta(days=5)
        self.lote.cantidad_actual = 0
        self.lote.save()
        response = self.client.get(reverse('mostrar_registro_pedido'))
        self.assertNotIn(self.producto, response.context['productos'])
