from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Usuario, Administrador, Cajero, DashboardConfig


class UsuarioViewsCompleteTest(TestCase):
    def setUp(self):
        # Configuración inicial del Dashboard
        self.config = DashboardConfig.objects.create(id=1, meta_reservas=50, meta_pedidos=200)

        # 1. Crear un Administrador para pruebas
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Administrador de Pruebas",
            contraseña="adminpass123",
            correo_electronico="admin@matpi.com",
            telefono="3001234567",
            fecha_nacimiento="1990-01-01",
            direccion="Calle Falsa 123",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.admin = Administrador.objects.create(
            usuario=self.admin_user,
            formacion_educativa="Ingeniería"
        )

        # 2. Crear un Cajero para pruebas
        self.cajero_user = Usuario.objects.create(
            id="0987654321",
            nombre_completo="Cajero de Pruebas",
            contraseña="cajeropass123",
            correo_electronico="cajero@matpi.com",
            telefono="3007654321",
            fecha_nacimiento="1995-05-05",
            direccion="Carrera Falsa 321",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )
        self.cajero = Cajero.objects.create(
            usuario=self.cajero_user,
            eps="SURA",
            tipo_contrato="Indefinido",
            turno="Mañana"
        )

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


    # 1.Vista de inicio de sesion
    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    # 2. Vista de inicio de sesion (Exitoso)
    def test_login_view_post_success(self):
        datos_login = {
            'txt_id': self.admin_user.id,
            'txt_contrasena': 'adminpass123'
        }
        response = self.client.post(reverse('login'), datos_login)
        # redirige al dashboard
        self.assertRedirects(response, reverse('dashboard'))
        self.assertEqual(self.client.session['usuario_id'], self.admin_user.id)


    # 3. Vista de inicio de sesion (Fallido)
    def test_login_view_post_fail(self):
        datos_login = {
            'txt_id': self.admin_user.id,
            'txt_contrasena': 'clave_incorrecta'
        }
        response = self.client.post(reverse('login'), datos_login)
        self.assertEqual(response.status_code, 200)
        # No debe haber sesión de usuario_id
        self.assertNotIn('usuario_id', self.client.session)

    # 4. cierre de sesion
    def test_logout_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('logout'))
        # Debe redirigir al inicio de sesion tras cerrar sesión
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('usuario_id', self.client.session)

    # 5. PRUEBA: Vista del Dashboard
    def test_dashboard_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('config', response.context)

    # 6. Lista de Usuarios
    def test_listar_usuarios_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_usuarios'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/listar.html')
        self.assertIn('usuarios', response.context)

    # 7. Ver Perfil seleccionado
    def test_ver_perfil_view(self):
        self.login_como_admin()
        response = self.client.get(reverse('ver_perfil', args=[self.cajero_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/perfil.html')
        self.assertEqual(response.context['usuario'], self.cajero_user)

    # 8.Registrar Usuario (Existoso)
    def test_registrar_usuario_post_success(self):
        self.login_como_admin()
        datos_registro = {
            'txt_id': '1122334455',
            'txt_nombre': 'Nuevo Colaborador',
            'txt_contrasena': 'secure123',
            'txt_correo': 'nuevo@matpi.com',
            'txt_telefono': '3123456789',
            'txt_fecha_nacimiento': '1998-10-10',
            'txt_direccion': 'Avenida Siempre Viva 742',
            'txt_fecha_ingreso': timezone.now().date().strftime('%Y-%m-%d'),
            'txt_eps': 'SURA',
            'txt_tipo_contrato': 'Indefinido',
            'txt_turno': 'Tarde',
            'txt_emergencia_nombre': 'Contacto Auxiliar',
            'txt_emergencia_parentesco': 'Hermano',
            'txt_emergencia_numero': '3159876543'
        }
        response = self.client.post(reverse('registrar_usuario'), datos_registro)
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertTrue(Usuario.objects.filter(id='1122334455').exists())
        self.assertTrue(Cajero.objects.filter(usuario_id='1122334455').exists())

    # 9. Registrar Usuario (Falla)
    def test_registrar_usuario_post_fail_validation(self):
        self.login_como_admin()
        datos_incorrectos = {
            'txt_id': '123',  # Documento inválido (Debe ser de 10 caracteres)
            'txt_nombre': 'Erróneo',
            'txt_contrasena': 'pass',
            'txt_fecha_ingreso': timezone.now().date().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('registrar_usuario'), datos_incorrectos)
        # Debe recargar la misma página mostrando el error
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registrar.html')
        self.assertFalse(Usuario.objects.filter(id='123').exists())




    # 10. PRUEBA: Editar Usuario (POST Exitoso)

    def test_editar_usuario_post_success(self):
        self.login_como_admin()
        datos_edicion = {
            'txt_id': self.cajero_user.id,
            'txt_nombre': 'Cajero Editado Exitosamente',
            'txt_correo': 'cajero_editado@matpi.com',
            'txt_telefono': '3209876543',
            'txt_fecha_nacimiento': '1995-05-05',
            'txt_direccion': 'Calle Nueva 789',
            'txt_estado': 'Activo',
            'txt_eps': 'Sanitas',
            'txt_tipo_contrato': 'Fijo',
            'txt_fecha_terminacion': (timezone.now().date() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'txt_turno': 'Noche',
            'txt_emergencia_nombre': 'Contacto Madre',
            'txt_emergencia_parentesco': 'Madre',
            'txt_emergencia_numero': '3101112222'
        }
        # En la app, la edición se procesa a través de la URL de procesar_edicion (editar/guardar/) vía POST
        response = self.client.post(reverse('procesar_edicion'), datos_edicion)
        self.assertRedirects(response, reverse('listar_usuarios'))

        # Validar cambios
        self.cajero_user.refresh_from_db()
        self.cajero.refresh_from_db()
        self.assertEqual(self.cajero_user.nombre_completo, 'Cajero Editado Exitosamente')
        self.assertEqual(self.cajero.eps, 'Sanitas')
        self.assertEqual(self.cajero.tipo_contrato, 'Fijo')


    # 11 Eliminar Usuario (Exitoso)

    def test_eliminar_usuario_success(self):
        self.login_como_admin()
        cajero_a_eliminar_id = self.cajero_user.id
        response = self.client.post(reverse('eliminar_usuario', args=[cajero_a_eliminar_id]))
        self.assertRedirects(response, reverse('listar_usuarios'))
        self.assertFalse(Usuario.objects.filter(id=cajero_a_eliminar_id).exists())


    # 12.Eliminar Usuario (Auto-eliminación bloqueada)
    def test_eliminar_usuario_self_fail(self):
        self.login_como_admin()
        response = self.client.post(reverse('eliminar_usuario', args=[self.admin_user.id]))
        self.assertRedirects(response, reverse('listar_usuarios'))
        # El administrador no debe haber sido eliminado
        self.assertTrue(Usuario.objects.filter(id=self.admin_user.id).exists())


    # 13.Reporte Módulo PDF (Usuarios)

    def test_reporte_modulo_pdf(self):
        self.login_como_admin()
        response = self.client.get(reverse('generar_reporte', kwargs={'modulo': 'usuarios', 'periodo': 'general'}))
        # Debe retornar el archivo PDF listo para descarga
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline; filename="MATPI_usuarios.pdf"', response['Content-Disposition'])

    def test_reporte_facturas_con_producto_pdf(self):
        from productos.models import Producto
        from pedidos.models import Pedido, DetallePedidoProducto
        from facturas.models import Factura

        self.login_como_admin()

        producto = Producto.objects.create(
            nombre_producto="Hamburguesa Especial",
            precio=12000,
            categoria="Hamburguesas"
        )
        pedido = Pedido.objects.create(
            estado='Completado',
            valor=12000,
            numero_orden=101,
            metodo_pago='Efectivo',
            usuario=self.admin_user
        )
        DetallePedidoProducto.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=1,
            precio_unitario=12000
        )
        factura = Factura.objects.create(
            id=999,
            valor_total=12960,
            descripcion="Test",
            iva=8.0,
            pedido=pedido
        )

        response = self.client.get(
            reverse('generar_reporte', kwargs={'modulo': 'facturas', 'periodo': 'general'}) + f'?producto={producto.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline; filename="MATPI_facturas.pdf"', response['Content-Disposition'])

    def test_reporte_proveedores_con_proveedor_pdf(self):
        from proveedores.models import Proveedor, DetalleProveedorMateriaP
        from materia_prima.models import MateriaPrima

        self.login_como_admin()

        proveedor = Proveedor.objects.create(
            nombre_proveedor="Proveedor Carnes",
            direccion="Calle 1",
            correo_electronico="carnes@matpi.com",
            telefono="3009876543"
        )
        materia = MateriaPrima.objects.create(
            nombre_materia_prima="Carne de res",
            unidad_medida="kg",
            cantidad_por_unidad=1,
            tipo="Comida"
        )
        DetalleProveedorMateriaP.objects.create(
            proveedor=proveedor,
            materia_prima=materia,
            precio_unitario=15000,
            fecha_suministro=timezone.now(),
            fecha_vencimiento=timezone.now().date() + timedelta(days=10)
        )

        response = self.client.get(
            reverse('generar_reporte', kwargs={'modulo': 'proveedores', 'periodo': 'general'}) + f'?proveedor={proveedor.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline; filename="MATPI_proveedores.pdf"', response['Content-Disposition'])


    # 16. Actualizar Metas
    def test_actualizar_metas(self):
        self.login_como_admin()
        datos_metas = {
            'meta_reservas': 100,
            'meta_pedidos': 350
        }
        response = self.client.post(reverse('actualizar_metas'), datos_metas)
        self.assertRedirects(response, reverse('dashboard'))

        self.config.refresh_from_db()
        self.assertEqual(self.config.meta_reservas, 100)
        self.assertEqual(self.config.meta_pedidos, 350)

    # 17. PRUEBA: Intentar editar campos de fecha inmutables (nacimiento y ingreso)
    def test_editar_usuario_fechas_inmutables(self):
        self.login_como_admin()
        # Intentamos enviar fechas diferentes en la petición POST
        datos_edicion = {
            'txt_id': self.cajero_user.id,
            'txt_nombre': 'Cajero Pruebas Modificado',
            'txt_correo': 'cajero@matpi.com',
            'txt_telefono': '3007654321',
            'txt_fecha_nacimiento': '1980-01-01',  # Original '1995-05-05'
            'txt_fecha_ingreso': '2010-01-01',     # Original timezone.now().date()
            'txt_direccion': 'Carrera Falsa 321',
            'txt_estado': 'Activo',
            'txt_eps': 'SURA',
            'txt_tipo_contrato': 'Indefinido',
            'txt_turno': 'Mañana',
            'txt_emergencia_nombre': 'Contacto Auxiliar',
            'txt_emergencia_parentesco': 'Hermano',
            'txt_emergencia_numero': '3159876543'
        }
        response = self.client.post(reverse('procesar_edicion'), datos_edicion)
        self.assertRedirects(response, reverse('listar_usuarios'))

        # Refrescar desde DB
        self.cajero_user.refresh_from_db()
        # Verificar que el nombre cambió
        self.assertEqual(self.cajero_user.nombre_completo, 'Cajero Pruebas Modificado')
        # Verificar que las fechas NO cambiaron (deben seguir siendo las originales)
        self.assertEqual(str(self.cajero_user.fecha_nacimiento), '1995-05-05')
        self.assertNotEqual(str(self.cajero_user.fecha_ingreso), '2010-01-01')
