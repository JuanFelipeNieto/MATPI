from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
import io
import openpyxl
from .models import MateriaPrima, Lote, DetalleProductoMateriaP
from usuarios.models import Usuario, Administrador
from productos.models import Producto

class MateriaPrimaViewsCompleteTest(TestCase):
    def setUp(self):
        # 1. Crear un Administrador para las pruebas de permisos
        self.admin_user = Usuario.objects.create(
            id="1234567890",
            nombre_completo="Admin Materias",
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

        # 2. Crear un Cajero (Usuario común sin rol admin)
        self.cajero_user = Usuario.objects.create(
            id="0987654321",
            nombre_completo="Cajero Materias",
            contraseña="cajeropass123",
            correo_electronico="cajero@matpi.com",
            telefono="3007654321",
            fecha_nacimiento="1995-05-05",
            direccion="Carrera Falsa 321",
            fecha_ingreso=timezone.now().date(),
            estado="Activo"
        )

        # 3. Crear registros iniciales de Materia Prima y Lote para pruebas
        self.materia_pan = MateriaPrima.objects.create(
            nombre_materia_prima="Pan de Hamburguesa",
            unidad_medida="und",
            cantidad_por_unidad=1,
            tipo="Comida"
        )
        self.lote_pan = Lote.objects.create(
            materia_prima=self.materia_pan,
            cantidad_inicial=100.0,
            cantidad_actual=80.0,
            fecha_vencimiento=timezone.now().date() + timedelta(days=10),
            precio_unidad=500.0
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

    def create_in_memory_excel(self, rows):
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)

        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        return SimpleUploadedFile(
            "test_import.xlsx",
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # 1. Listado
    def test_listar_materia_prima_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_materia_prima'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'materia_prima/listar.html')
        self.assertIn('materia_primas', response.context)

    def test_listar_materia_prima_confirmation_message_contains_products(self):
        self.login_como_admin()
        # Create a product and relate it to the raw material
        producto = Producto.objects.create(
            nombre_producto="Hamburguesa Clasica",
            precio=15000,
            categoria="Hamburguesas",
            cantidad=10
        )
        DetalleProductoMateriaP.objects.create(
            producto=producto,
            materia_prima=self.materia_pan,
            cantidad_usada=1.0,
            unidad_medida="und"
        )
        
        response = self.client.get(reverse('listar_materia_prima'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Se eliminará de los siguientes productos:")
        self.assertContains(response, "- Hamburguesa Clasica")


    # 2. Buscar materia prima con el filtro
    def test_listar_materia_prima_buscar(self):
        self.login_como_admin()
        response = self.client.get(reverse('listar_materia_prima') + '?buscar=Pan')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.materia_pan, response.context['materia_primas'])

    # 3.Registro Materia Prima (exitoso)
    def test_registrar_materia_prima_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_nombre': 'Carne Angus',
            'txt_unidad': 'g',
            'txt_cantidad_unidad': '150',
            'txt_tipo': 'Comida',
            'txt_cantidad': '50',
            'txt_fecha_ingreso': timezone.now().date().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('registrar_materia_prima'), datos)
        self.assertRedirects(response, reverse('listar_materia_prima'))

        materia = MateriaPrima.objects.get(nombre_materia_prima='Carne Angus')
        self.assertEqual(materia.unidad_medida, 'g')
        self.assertEqual(materia.cantidad_por_unidad, 150)
        self.assertTrue(Lote.objects.filter(materia_prima=materia, cantidad_inicial=50).exists())



    # 4.Pre-Editar Materia Prima Carga el formulario de edición de la materia prima seleccionada.
    def test_pre_editar_materia_prima_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('pre_editar_materia_prima', args=[self.materia_pan.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'materia_prima/editar.html')
        self.assertEqual(response.context['materia_prima'], self.materia_pan)

    # 7.Editar Materia Prima (Exitoso)
    def test_editar_materia_prima_post_success(self):
        self.login_como_admin()
        datos = {
            'txt_id': self.materia_pan.id,
            'txt_nombre': 'Pan Brioche Premium',
            'txt_unidad': 'und',
            'txt_cantidad_unidad': '1',
            'txt_tipo': 'Comida'
        }
        response = self.client.post(reverse('editar_materia_prima'), datos)
        self.assertRedirects(response, reverse('listar_materia_prima'))

        self.materia_pan.refresh_from_db()
        self.assertEqual(self.materia_pan.nombre_materia_prima, 'Pan Brioche Premium')

    # 5.Eliminar Materia Prima (Exitoso)
    def test_eliminar_materia_prima_success(self):
        self.login_como_admin()

        producto = Producto.objects.create(
            nombre_producto="Hamburguesa Clásica",
            precio=15000,
            categoria="Hamburguesas",
            cantidad=10
        )
        # Crear detalle de receta
        DetalleProductoMateriaP.objects.create(
            producto=producto,
            materia_prima=self.materia_pan,
            cantidad_usada=1.0,
            unidad_medida="und"
        )

        response = self.client.post(reverse('eliminar_materia_prima', args=[self.materia_pan.id]))
        self.assertRedirects(response, reverse('listar_materia_prima'))

        # La materia prima debe dejar de existir
        self.assertFalse(MateriaPrima.objects.filter(id=self.materia_pan.id).exists())

    # 6. Ver Lotes
    def test_ver_lotes_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('ver_lotes', args=[self.materia_pan.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'materia_prima/lotes.html')
        self.assertEqual(response.context['materia'], self.materia_pan)

    # 7. Pre-Editar Lote carga la plantilla de edición para un lote especifico
    def test_pre_editar_lote_get(self):
        self.login_como_admin()
        response = self.client.get(reverse('pre_editar_lote', args=[self.lote_pan.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'materia_prima/editar_lote.html')
        self.assertEqual(response.context['lote'], self.lote_pan)

    # 8. Editar Lote (exitoso)
    def test_editar_lote_post_success(self):
        self.login_como_admin()
        fecha_vencimiento_nueva = (timezone.now().date() + timedelta(days=20)).strftime('%Y-%m-%d')
        datos = {
            'txt_id': self.lote_pan.id,
            'txt_cantidad': '95',
            'txt_fecha_vencimiento': fecha_vencimiento_nueva
        }
        response = self.client.post(reverse('editar_lote'), datos)
        self.assertRedirects(response, reverse('ver_lotes', args=[self.materia_pan.id]))

        self.lote_pan.refresh_from_db()
        self.assertEqual(self.lote_pan.cantidad_actual, 95)

    # 9. Eliminar lote
    def test_eliminar_lote_success(self):
        self.login_como_admin()
        response = self.client.post(reverse('eliminar_lote', args=[self.lote_pan.id]))
        self.assertRedirects(response, reverse('ver_lotes', args=[self.materia_pan.id]))
        self.assertFalse(Lote.objects.filter(id=self.lote_pan.id).exists())

    # 10.  Importar Materia Prima Excel
    def test_importar_materia_prima_excel_post_success(self):
        self.login_como_admin()

        # simulación de Excel válido
        filas = [
            ("Nombre Materia Prima", "Unidad de Medida", "Cantidad por Unidad", "Tipo"),
            ("Cheddar", "und", 1, "Comida"),
            ("Tocineta", "g", 500, "Comida")
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_materia_prima_excel'), {'archivo_excel': archivo_excel})
        self.assertRedirects(response, reverse('listar_materia_prima'))

        # Deben haberse creado las dos materias primas importadas
        self.assertTrue(MateriaPrima.objects.filter(nombre_materia_prima="Cheddar").exists())
        self.assertTrue(MateriaPrima.objects.filter(nombre_materia_prima="Tocineta").exists())

    # 11. Importar Materia Prima Excel (Registro Duplicado)
    def test_importar_materia_prima_excel_duplicate_fail(self):
        self.login_como_admin()

        filas = [
            ("Nombre Materia Prima", "Unidad de Medida", "Cantidad por Unidad", "Tipo"),
            ("Pan de Hamburguesa", "und", 1, "Comida")
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_materia_prima_excel'), {'archivo_excel': archivo_excel})
        self.assertRedirects(response, reverse('listar_materia_prima'))

    # 12. Importar Lotes Excel
    def test_importar_lotes_excel_post_success(self):
        self.login_como_admin()

        filas = [
            ("Nombre Materia Prima Completo", "Cantidad Inicial", "Fecha Vencimiento", "Precio Unidad"),
            ("Pan de Hamburguesa", 50, "2026-06-01", 600)
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_lotes_excel'), {'archivo_excel': archivo_excel})
        self.assertRedirects(response, reverse('listar_materia_prima'))

        self.assertTrue(Lote.objects.filter(materia_prima=self.materia_pan, cantidad_inicial=50, precio_unidad=600).exists())

    # 13. PRUEBA: Importar Lotes Excel (Insumo No Encontrado)
    def test_importar_lotes_excel_not_found_fail(self):
        self.login_como_admin()

        filas = [
            ("Nombre Materia Prima Completo", "Cantidad Inicial", "Fecha Vencimiento", "Precio Unidad"),
            ("Insumo Fantasma No Existente", 50, "2026-06-01", 600)
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_lotes_excel'), {'archivo_excel': archivo_excel})
        self.assertRedirects(response, reverse('importar_lotes_excel'))

    # 14. PRUEBA: Importar Materia Prima Excel (Datos Inválidos - No cumple condiciones)
    def test_importar_materia_prima_excel_invalid_data(self):
        self.login_como_admin()

        # Fila con cantidad por unidad no entero
        filas = [
            ("Nombre Materia Prima", "Unidad de Medida", "Cantidad por Unidad", "Tipo"),
            ("Queso", "und", "tres", "Comida")
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_materia_prima_excel'), {'archivo_excel': archivo_excel}, follow=True)
        self.assertContains(response, "El contenido del archivo Excel no cumple con las condiciones para agregarlo al listado.")

    # 15. PRUEBA: Importar Materia Prima Excel (Archivo Vacío)
    def test_importar_materia_prima_excel_empty_file(self):
        self.login_como_admin()

        # Solo encabezados
        filas = [
            ("Nombre Materia Prima", "Unidad de Medida", "Cantidad por Unidad", "Tipo")
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_materia_prima_excel'), {'archivo_excel': archivo_excel}, follow=True)
        self.assertContains(response, "El contenido del archivo Excel no cumple con las condiciones para agregarlo al listado.")

    # 16. PRUEBA: Importar Lotes Excel (Datos Inválidos - No cumple condiciones)
    def test_importar_lotes_excel_invalid_data(self):
        self.login_como_admin()

        # Fila con cantidad no numérica
        filas = [
            ("Nombre Materia Prima Completo", "Cantidad Inicial", "Fecha Vencimiento", "Precio Unidad"),
            ("Pan de Hamburguesa", "cincuenta", "2026-06-01", 600)
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_lotes_excel'), {'archivo_excel': archivo_excel}, follow=True)
        self.assertContains(response, "El contenido del archivo Excel no cumple con las condiciones para agregarlo al listado.")

    # 17. PRUEBA: Importar Lotes Excel (Archivo Vacío)
    def test_importar_lotes_excel_empty_file(self):
        self.login_como_admin()

        # Solo encabezados
        filas = [
            ("Nombre Materia Prima Completo", "Cantidad Inicial", "Fecha Vencimiento", "Precio Unidad")
        ]
        archivo_excel = self.create_in_memory_excel(filas)

        response = self.client.post(reverse('importar_lotes_excel'), {'archivo_excel': archivo_excel}, follow=True)
        self.assertContains(response, "El contenido del archivo Excel no cumple con las condiciones para agregarlo al listado.")

    # 18. PRUEBA: Registrar Materia Prima Duplicada (Mismo nombre y equivalencia)
    def test_registrar_materia_prima_duplicate(self):
        self.login_como_admin()
        # self.materia_pan has name 'Pan de hamburguesa' and equivalence 1 (default from setUp)
        datos = {
            'txt_nombre': 'Pan de hamburguesa',
            'txt_unidad': 'und',
            'txt_cantidad_unidad': str(self.materia_pan.cantidad_por_unidad),
            'txt_tipo': 'Comida',
            'txt_cantidad': '10',
            'txt_fecha_ingreso': timezone.now().date().strftime('%Y-%m-%d')
        }
        response = self.client.post(reverse('registrar_materia_prima'), datos, follow=True)
        self.assertContains(response, "Ya existe una materia prima con ese nombre y equivalencia.")

    # 19. PRUEBA: Editar Materia Prima a una Duplicada
    def test_editar_materia_prima_duplicate(self):
        self.login_como_admin()
        # Create a second raw material
        materia2 = MateriaPrima.objects.create(
            nombre_materia_prima="Carne",
            unidad_medida="g",
            cantidad_por_unidad=150,
            tipo="Comida"
        )
        # Try to edit materia2 to match self.materia_pan (Pan de hamburguesa, equivalence 1)
        datos = {
            'txt_id': materia2.id,
            'txt_nombre': 'Pan de hamburguesa',
            'txt_unidad': 'und',
            'txt_cantidad_unidad': str(self.materia_pan.cantidad_por_unidad),
            'txt_tipo': 'Comida'
        }
        response = self.client.post(reverse('editar_materia_prima'), datos, follow=True)
        self.assertContains(response, "Ya existe otra materia prima con ese nombre y equivalencia.")

    # 20. PRUEBA: Importar Excel de Materias Primas con Duplicados
    def test_importar_materia_prima_excel_duplicate_db(self):
        self.login_como_admin()
        # Excel contains self.materia_pan duplicate
        filas = [
            ("Nombre Materia Prima", "Unidad de Medida", "Cantidad por Unidad", "Tipo"),
            ("Pan de hamburguesa", "und", str(self.materia_pan.cantidad_por_unidad), "Comida")
        ]
        archivo_excel = self.create_in_memory_excel(filas)
        response = self.client.post(reverse('importar_materia_prima_excel'), {'archivo_excel': archivo_excel}, follow=True)
        self.assertContains(response, "No se puede importar el archivo debido a que los datos ya existen o ya fueron ingresados")

    # 21. PRUEBA: Importar Excel de Materias Primas con Duplicados dentro del archivo
    def test_importar_materia_prima_excel_duplicate_in_file(self):
        self.login_como_admin()
        # Excel contains two rows with the same name and equivalence
        filas = [
            ("Nombre Materia Prima", "Unidad de Medida", "Cantidad por Unidad", "Tipo"),
            ("Queso Cheddar", "g", "200", "Comida"),
            ("Queso Cheddar", "g", "200", "Comida")
        ]
        archivo_excel = self.create_in_memory_excel(filas)
        response = self.client.post(reverse('importar_materia_prima_excel'), {'archivo_excel': archivo_excel}, follow=True)
        self.assertContains(response, "No se puede importar el archivo debido a que contiene registros duplicados")




