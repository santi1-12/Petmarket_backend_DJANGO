from django.test import TestCase
from .models import Producto

class ProductoViewsTests(TestCase):
	def setUp(self):
		Producto.objects.all().delete()
		for i in range(3):
			Producto.objects.create(nombre=f'P{i}', descripcion='desc', precio=10+i, stock=5, categoria='Test')

	def test_catalogo_status_and_content(self):
		resp = self.client.get('/productos/')
		self.assertEqual(resp.status_code, 200)
		# Check at least one product name in response
		self.assertContains(resp, 'P0')

	def test_producto_detalle(self):
		p = Producto.objects.first()
		resp = self.client.get(f'/productos/{p.pk}/')
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, p.nombre)

# Create your tests here.
