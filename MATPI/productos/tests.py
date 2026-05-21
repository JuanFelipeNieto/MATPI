from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from usuarios.models import Usuario, Administrador
from productos.models import Producto
import datetime

class ProductoImagenValidationTests(TestCase):
    def setUp(self):
        # Create an administrator user
        self.usuario = Usuario.objects.create(
            id="12345678",
            telefono="3001234567",
            contraseña="adminpassword",
            correo_electronico="admin@matpi.com",
            estado="Activo",
            fecha_nacimiento=datetime.date(1990, 1, 1),
            nombre_completo="Admin Test",
            direccion="Calle 123",
            fecha_ingreso=datetime.date(2023, 1, 1)
        )
        self.admin = Administrador.objects.create(usuario=self.usuario)
        
        # Initialize client and session
        self.client = Client()
        session = self.client.session
        session['usuario_id'] = self.usuario.id
        session.save()

    def test_registrar_comida_con_imagen_valida_png(self):
        # Simple blank PNG image
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        uploaded_image = SimpleUploadedFile("test.png", image_content, content_type="image/png")
        
        response = self.client.post(reverse('registrar_producto'), {
            'txt_nombre': 'Hamburguesa Test',
            'txt_categoria': 'Hamburguesas',
            'txt_precio': 12000,
            'txt_imagen': uploaded_image,
            'materia_id[]': [],
            'materia_cantidad[]': [],
            'materia_unidad[]': []
        })
        # Check if the product was created
        producto = Producto.objects.filter(nombre_producto='Hamburguesa Test').first()
        self.assertIsNotNone(producto)
        self.assertTrue(producto.imagen.name.endswith('.png'))

    def test_registrar_comida_con_imagen_invalida_gif(self):
        uploaded_image = SimpleUploadedFile("test.gif", b"GIF89a...", content_type="image/gif")
        
        response = self.client.post(reverse('registrar_producto'), {
            'txt_nombre': 'Hamburguesa Invalida',
            'txt_categoria': 'Hamburguesas',
            'txt_precio': 12000,
            'txt_imagen': uploaded_image,
            'materia_id[]': [],
            'materia_cantidad[]': [],
            'materia_unidad[]': []
        })
        
        # Check that product was not created because validation failed and redirected
        producto = Producto.objects.filter(nombre_producto='Hamburguesa Invalida').first()
        self.assertIsNone(producto)
        self.assertRedirects(response, reverse('mostrar_registro_comida'))

    def test_editar_comida_con_imagen_invalida_gif(self):
        producto = Producto.objects.create(
            nombre_producto='Comida Editar',
            precio=10000,
            categoria='Hamburguesas'
        )
        
        uploaded_image = SimpleUploadedFile("test.gif", b"GIF89a...", content_type="image/gif")
        
        response = self.client.post(reverse('editar_producto'), {
            'txt_id': producto.id,
            'txt_nombre': 'Comida Editada',
            'txt_categoria': 'Hamburguesas',
            'txt_precio': 11000,
            'txt_imagen': uploaded_image,
            'materia_id[]': [],
            'materia_cantidad[]': [],
            'materia_unidad[]': []
        })
        
        # Verify it redirected back to edit page and product name was not updated
        self.assertRedirects(response, reverse('pre_editar_producto', kwargs={'id': producto.id}))
        producto.refresh_from_db()
        self.assertEqual(producto.nombre_producto, 'Comida Editar')
