from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date
from usuarios.models import Usuario, Administrador
from productos.models import Producto
from materia_prima.models import MateriaPrima, Lote, DetalleProductoMateriaP
from productos.views import recalcular_stock_producto

class ProductoViewsCompleteTest(TestCase):
    def setUp(self):
        # 1. Crear un Administrador para las pruebas de permisos
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Admin Productos",
            contraseña="adminpass123",
            correo_electronico="admin@matpi.com",
            telefono="3001234567",
            fecha_nacimiento=date(1990, 1, 1),
            direccion="Calle Falsa 123",
            fecha_ingreso=date(2023, 1, 1),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(usuario=self.admin_user)

        # 2. Crear un Cajero (Usuario común)
        self.cajero_user = Usuario.objects.create(
            id="0987654321",
            nombre_completo="Cajero Productos",
            contraseña="cajeropass123",
            correo_electronico="cajero@matpi.com",
            telefono="3007654321",
            fecha_nacimiento=date(1995, 5, 5),
            direccion="Carrera Falsa 321",
            fecha_ingreso=date(2023, 1, 1),
            estado="Activo"
        )

        # 3. Crear insumos iniciales de materia prima y lote para el cálculo de stock
        self.materia_carne = MateriaPrima.objects.create(
            nombre_materia_prima="Carne de Res",
            unidad_medida="g",
            cantidad_por_unidad=150,
            tipo="Comida"
        )
        self.lote_carne = Lote.objects.create(
            materia_prima=self.materia_carne,
            cantidad_inicial=10.0,  
            cantidad_actual=10.0,
            precio_unidad=2000
        )

        self.materia_coca = MateriaPrima.objects.create(
            nombre_materia_prima="Coca Cola 350ml",
            unidad_medida="und",
            cantidad_por_unidad=1,
            tipo="Bebida"
        )
        self.lote_coca = Lote.objects.create(
            materia_prima=self.materia_coca,
            cantidad_inicial=24.0,  # 24 latas
            cantidad_actual=24.0,
            precio_unidad=1500
        )

        # 4. Crear un producto base de comida
        self.producto_comida = Producto.objects.create(
            nombre_producto="Hamburguesa Sencilla",
            precio=12000,
            categoria="Hamburguesas"
        )
        # Receta: requiere 1 porción de Carne de Res (150g en base)
        self.detalle_comida = DetalleProductoMateriaP.objects.create(
            producto=self.producto_comida,
            materia_prima=self.materia_carne,
            cantidad_usada=150.0,
            unidad_medida="g"
        )
        recalcular_stock_producto(self.producto_comida)

        # 5. Crear un producto base de bebida
        self.producto_bebida = Producto.objects.create(
            nombre_producto="Coca Cola 350ml",
            precio=3500,
            categoria="Bebidas"
        )
        # Receta: requiere 1 Coca Cola de materia prima
        self.detalle_bebida = DetalleProductoMateriaP.objects.create(
            producto=self.producto_bebida,
            materia_prima=self.materia_coca,
            cantidad_usada=1.0,
            unidad_medida="und"
        )
        recalcular_stock_producto(self.producto_bebida)

        # Configurar cliente y sesiones iniciales
        self.client = Client()

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

    def get_valid_png_image(self):
        png_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        return SimpleUploadedFile("test.png", png_content, content_type="image/png")

    def get_invalid_gif_image(self):
        return SimpleUploadedFile("test.gif", b"GIF89a...", content_type="image/gif")

    # 1. Listado 
    def test_01_listar_productos_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/listar.html')
        self.assertIn('productos', response.context)

    # 2. Buscar productos con el filtro
    def test_02_listar_productos_buscar(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_productos') + '?buscar=Hamburguesa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.producto_comida, response.context['productos'])

    # 5. Registrar producto Comida (exitoso)
    def test_05_registrar_comida_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_nombre': 'Hamburguesa Especial Angus',
            'txt_categoria': 'Hamburguesas',
            'txt_precio': '18000',
            'materia_id[]': [self.materia_carne.id],
            'materia_cantidad[]': ['150.0'],
            'materia_unidad[]': ['g']
        }
        response = self.client.post(reverse('registrar_producto'), datos)
        self.assertRedirects(response, reverse('listar_productos'))
        
        producto = Producto.objects.get(nombre_producto='Hamburguesa Especial Angus')
        self.assertEqual(producto.precio, 18000)
        self.assertTrue(DetalleProductoMateriaP.objects.filter(producto=producto, materia_prima=self.materia_carne).exists())
        self.assertEqual(producto.cantidad, 10)

    # 6. Registrar producto Bebida (exitoso)
    def test_06_registrar_bebida_auto_nombre_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_nombre': '',  
            'txt_categoria': 'Bebidas',
            'txt_precio': '4000',
            'materia_id[]': [self.materia_coca.id],
            'materia_cantidad[]': ['1.0'],
            'materia_unidad[]': ['und']
        }
        response = self.client.post(reverse('registrar_producto'), datos)
        self.assertRedirects(response, reverse('listar_productos'))
        
        producto = Producto.objects.filter(categoria='Bebidas', precio=4000).first()
        self.assertIsNotNone(producto)
        self.assertEqual(producto.nombre_producto, self.materia_coca.nombre_materia_prima)

    # 7. Registrar Producto (Fallido o Imagen Inválida)
    def test_07_registrar_producto_invalid_image(self):
        self.login_como_admin()
        imagen_invalida = self.get_invalid_gif_image()
        datos = {
            'txt_nombre': 'Hamburguesa Rechazada',
            'txt_categoria': 'Hamburguesas',
            'txt_precio': '15000',
            'txt_imagen': imagen_invalida
        }
        response = self.client.post(reverse('registrar_producto'), datos)
        self.assertRedirects(response, reverse('mostrar_registro_comida'))
        self.assertFalse(Producto.objects.filter(nombre_producto='Hamburguesa Rechazada').exists())

    # 8. PRUEBA: Editar Producto (exitoso)
    def test_11_editar_producto_post_success(self):
        self.login_como_admin()
        
        materia_queso = MateriaPrima.objects.create(
            nombre_materia_prima="Queso Cheddar",
            unidad_medida="und",
            cantidad_por_unidad=1,
            tipo="Comida"
        )
        Lote.objects.create(
            materia_prima=materia_queso,
            cantidad_inicial=5.0,
            cantidad_actual=5.0
        )

        datos = {
            'txt_id': self.producto_comida.id,
            'txt_nombre': 'Hamburguesa Especial de la Casa',
            'txt_precio': '16000',
            'txt_categoria': 'Hamburguesas',
            'materia_id[]': [materia_queso.id],
            'materia_cantidad[]': ['1.0'],
            'materia_unidad[]': ['und']
        }
        response = self.client.post(reverse('editar_producto'), datos)
        self.assertRedirects(response, reverse('listar_productos'))
        
        # Validar cambios
        self.producto_comida.refresh_from_db()
        self.assertEqual(self.producto_comida.nombre_producto, 'Hamburguesa Especial de la Casa')
        self.assertEqual(self.producto_comida.precio, 16000)
        # La composición antigua debe haber sido reemplazada
        self.assertFalse(DetalleProductoMateriaP.objects.filter(producto=self.producto_comida, materia_prima=self.materia_carne).exists())
        self.assertTrue(DetalleProductoMateriaP.objects.filter(producto=self.producto_comida, materia_prima=materia_queso).exists())
        # Stock nuevo debe ser 5 (basado en el lote de queso cheddar)
        self.assertEqual(self.producto_comida.cantidad, 5)


    # 12. Editar Producto (falla)
    def test_12_editar_producto_invalid_image(self):
        self.login_como_admin()
        imagen_invalida = self.get_invalid_gif_image()
        datos = {
            'txt_id': self.producto_comida.id,
            'txt_nombre': 'Hamburguesa Editada Mal',
            'txt_precio': '16000',
            'txt_categoria': 'Hamburguesas',
            'txt_imagen': imagen_invalida
        }
        response = self.client.post(reverse('editar_producto'), datos)
        self.assertRedirects(response, reverse('pre_editar_producto', args=[self.producto_comida.id]))
        
        # No deben haberse aplicado los cambios
        self.producto_comida.refresh_from_db()
        self.assertEqual(self.producto_comida.nombre_producto, 'Hamburguesa Sencilla')

    # 13.Eliminar Producto
    def test_13_eliminar_producto_success(self):
        """13. test_eliminar_producto_success: Elimina físicamente un producto de la carta."""
        self.login_como_admin()
        response = self.client.post(reverse('eliminar_producto', args=[self.producto_comida.id]))
        self.assertRedirects(response, reverse('listar_productos'))
        self.assertFalse(Producto.objects.filter(id=self.producto_comida.id).exists())

    # ==========================================
    # 14. PRUEBA: Control de Seguridad (Acceso Bloqueado a Cajero)
    # ==========================================
    def test_14_seguridad_cajero_bloqueado(self):
        """14. test_seguridad_cajero_bloqueado: Garantiza que un colaborador cajero no pueda acceder a funciones CRUD administrativas."""
        self.login_como_cajero()
        
        # Bloqueo en registro comida
        response = self.client.get(reverse('mostrar_registro_comida'))
        self.assertRedirects(response, reverse('listar_productos'))
        
        # Bloqueo en registro bebida
        response = self.client.get(reverse('mostrar_registro_bebida'))
        self.assertRedirects(response, reverse('listar_productos'))
        
        # Bloqueo en proceso guardar registro
        response = self.client.post(reverse('registrar_producto'), {})
        self.assertRedirects(response, reverse('listar_productos'))
        
        # Bloqueo en pre-edición
        response = self.client.get(reverse('pre_editar_producto', args=[self.producto_comida.id]))
        self.assertRedirects(response, reverse('listar_productos'))
        
        # Bloqueo en proceso guardar edición
        response = self.client.post(reverse('editar_producto'), {})
        self.assertRedirects(response, reverse('listar_productos'))
        
        # Bloqueo en eliminación
        response = self.client.post(reverse('eliminar_producto', args=[self.producto_comida.id]))
        self.assertRedirects(response, reverse('listar_productos'))

    # ==========================================
    # 15. PRUEBA: Lógica de Recálculo de Stock
    # ==========================================
    def test_15_recalcular_stock_logica(self):
        """15. test_recalcular_stock_logica: Valida el algoritmo de cálculo de stock basado en múltiplos de lotes e insumos."""
        # Inicialmente el stock recalculado en setUp fue 10 (Carne disponible = 10 uds de 150g)
        self.assertEqual(self.producto_comida.cantidad, 10)
        
        # Reducimos a la mitad la disponibilidad del lote de carne
        self.lote_carne.cantidad_actual = 4.0
        self.lote_carne.save()
        
        # Recalculamos stock del producto
        recalcular_stock_producto(self.producto_comida)
        
        # La cantidad de hamburguesas disponibles debe bajar automáticamente a 4
        self.assertEqual(self.producto_comida.cantidad, 4)


