from django.test import TestCase
from django.contrib.auth import get_user_model
from productos.models import Producto

class CarritoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('u1', 'u1@example.com', 'pass')
        Producto.objects.create(nombre='C1', descripcion='d', precio=10, stock=5)

    def test_add_to_cart_session(self):
        p = Producto.objects.first()
        resp = self.client.post(f'/carrito/add/{p.pk}/', follow=True)
        self.assertEqual(resp.status_code, 200)
        # session cart should have product id
        session_cart = self.client.session.get('cart')
        self.assertIsNotNone(session_cart)
        self.assertIn(str(p.pk), session_cart)

    def test_add_to_cart_authenticated(self):
        self.client.login(username='u1', password='pass')
        p = Producto.objects.first()
        resp = self.client.post(f'/carrito/add/{p.pk}/', follow=True)
        self.assertEqual(resp.status_code, 200)
        # check DB cart
        from carrito.models import Cart, CartItem
        cart = Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(cart)
        self.assertTrue(cart.carrito_items.exists())
