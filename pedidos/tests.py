from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from productos.models import Producto

User = get_user_model()


class CartAPITest(TestCase):
	def setUp(self):
		self.client = Client()
		# create users
		self.cliente = User.objects.create_user(username='testcliente', password='clientepass')
		self.cliente.role = 'cliente'
		self.cliente.save()
		self.empleado = User.objects.create_user(username='testemple', password='empleadopass')
		self.empleado.role = 'empleado'
		self.empleado.save()
		# create a product
		self.product = Producto.objects.create(nombre='P1', descripcion='d', precio=10.00, stock=5)

	def test_anonymous_cannot_add_to_cart(self):
		resp = self.client.post('/api/pedidos/agregar/', {'productId': self.product.id, 'quantity': 1}, content_type='application/json')
		self.assertIn(resp.status_code, (302, 401, 403))

	def test_cliente_can_add_and_count(self):
		self.client.login(username='testcliente', password='clientepass')
		resp = self.client.post('/api/pedidos/agregar/', {'productId': self.product.id, 'quantity': 1}, content_type='application/json')
		self.assertEqual(resp.status_code, 200)
		resp2 = self.client.get('/api/pedidos/count/')
		self.assertEqual(resp2.status_code, 200)
		self.assertEqual(resp2.json().get('count'), 1)

	def test_empleado_cannot_use_cart(self):
		self.client.login(username='testemple', password='empleadopass')
		resp = self.client.post('/api/pedidos/agregar/', {'productId': self.product.id, 'quantity': 1}, content_type='application/json')
		# empleado should be forbidden
		self.assertIn(resp.status_code, (302, 401, 403))


