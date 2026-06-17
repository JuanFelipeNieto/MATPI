from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core import mail
from usuarios.models import Usuario, Administrador
from pedidos.models import Pedido
from clientes.models import Cliente

class ReporteViewsTest(TestCase):
    def setUp(self):
        # Crear usuario admin para la sesión
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Admin Reportes",
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

        self.pedido = Pedido.objects.create(
            estado='Completado',
            valor=10000,
            numero_orden=1,
            metodo_pago='Efectivo',
            usuario=self.admin_user,
            cliente=self.cliente
        )

    def login_como_admin(self):
        session = self.client.session
        session['usuario_id'] = self.admin_user.id
        session['usuario_nombre'] = self.admin_user.nombre_completo
        session.save()

    def test_dashboard_reportes_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('dashboard_reportes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportes/dashboard_reportes.html')

    def test_generar_reporte_csv_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('generar_reporte_csv') + '?tipo=general&periodo=mensual')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment; filename="reporte_general_detallado_mensual_', response['Content-Disposition'])

    def test_generar_reporte_pdf_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('generar_reporte_pdf') + '?tipo=general&periodo=mensual')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="reporte_general_mensual.pdf"', response['Content-Disposition'])

    def test_enviar_reporte_correo_post_success(self):
        self.login_como_admin()
        datos = {
            'tipo': 'general',
            'periodo': 'mensual',
            'correo': 'test_admin@matpi.com'
        }
        response = self.client.post(reverse('enviar_reporte_correo'), datos)
        self.assertRedirects(response, reverse('dashboard_reportes'))

        # Verificar que el correo fue enviado (colocado en el outbox de pruebas de Django)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['test_admin@matpi.com'])
        self.assertIn('MATPI: Reporte General (Mensual)', mail.outbox[0].subject)
