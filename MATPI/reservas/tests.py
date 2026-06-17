from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Reserva
from usuarios.models import Usuario, Cajero
from clientes.models import Cliente

class ReservaViewsTest(TestCase):
    def setUp(self):
        # Crear usuario para la sesión y cajero
        self.cajero_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Cajero Reservas",
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

        self.fecha_valida = (timezone.now() + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)

        self.reserva = Reserva.objects.create(
            fecha=self.fecha_valida,
            estado=True,
            observaciones="Reserva para almuerzo",
            cliente=self.cliente,
            cajero=self.cajero
        )

    def login_como_cajero(self):
        session = self.client.session
        session['usuario_id'] = self.cajero_user.id
        session['usuario_nombre'] = self.cajero_user.nombre_completo
        session.save()

    def test_listar_reservas_get(self):
        self.login_como_cajero(
        )
        response = self.client.get(reverse('listar_reservas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/listar.html')
        self.assertIn('reservas', response.context)

    def test_registrar_reserva_post_success(self):
        self.login_como_cajero()
        nueva_fecha = (timezone.now() + timedelta(days=2)).replace(hour=15, minute=30, second=0, microsecond=0)
        datos = {
            'txt_fecha': nueva_fecha.strftime('%Y-%m-%dT%H:%M'),
            'txt_estado': '1',
            'txt_observaciones': 'Nueva reserva familiar',
            'txt_cliente_text': f"{self.cliente.nombre_completo} ({self.cliente.id})"
        }
        response = self.client.post(reverse('registrar_reserva'), datos)
        self.assertRedirects(response, reverse('listar_reservas'))
        self.assertTrue(Reserva.objects.filter(observaciones='Nueva reserva familiar').exists())

    def test_registrar_reserva_post_fail_fecha_pasada(self):
        self.login_como_cajero()
        fecha_pasada = (timezone.now() - timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
        datos = {
            'txt_fecha': fecha_pasada.strftime('%Y-%m-%dT%H:%M'),
            'txt_estado': '1',
            'txt_observaciones': 'Reserva fallida',
            'txt_cliente_text': f"{self.cliente.nombre_completo} ({self.cliente.id})"
        }
        response = self.client.post(reverse('registrar_reserva'), datos)
        self.assertRedirects(response, reverse('listar_reservas'))
        self.assertFalse(Reserva.objects.filter(observaciones='Reserva fallida').exists())

    def test_pre_editar_reserva_get(self):
        self.login_como_cajero()
        response = self.client.get(reverse('pre_editar_reserva', args=[self.reserva.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/listar.html')
        self.assertIn('reserva_edit', response.context)

    def test_editar_reserva_post_success(self):
        self.login_como_cajero()
        nueva_fecha = (timezone.now() + timedelta(days=3)).replace(hour=16, minute=0, second=0, microsecond=0)
        datos = {
            'txt_id': self.reserva.id,
            'txt_fecha': nueva_fecha.strftime('%Y-%m-%dT%H:%M'),
            'txt_estado': '0',
            'txt_observaciones': 'Observación editada',
            'txt_cliente_text': f"{self.cliente.nombre_completo} ({self.cliente.id})"
        }
        response = self.client.post(reverse('editar_reserva'), datos)
        self.assertRedirects(response, reverse('listar_reservas'))
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.observaciones, 'Observación editada')
        self.assertFalse(self.reserva.estado)

    def test_eliminar_reserva_success(self):
        self.login_como_cajero()
        response = self.client.post(reverse('eliminar_reserva', args=[self.reserva.id]))
        self.assertRedirects(response, reverse('listar_reservas'))
        self.assertFalse(Reserva.objects.filter(id=self.reserva.id).exists())

    def test_registrar_reserva_observaciones_opcionales(self):
        self.login_como_cajero()
        nueva_fecha = (timezone.now() + timedelta(days=2)).replace(hour=15, minute=30, second=0, microsecond=0)
        datos = {
            'txt_fecha': nueva_fecha.strftime('%Y-%m-%dT%H:%M'),
            'txt_estado': '1',
            'txt_observaciones': '',  # Vacío para probar opcionalidad
            'txt_cliente_text': f"{self.cliente.nombre_completo} ({self.cliente.id})"
        }
        response = self.client.post(reverse('registrar_reserva'), datos)
        self.assertRedirects(response, reverse('listar_reservas'))
        # La reserva debe haberse guardado exitosamente con observaciones vacías o nulas
        self.assertTrue(Reserva.objects.filter(observaciones='').exists() or Reserva.objects.filter(observaciones__isnull=True).exists())
