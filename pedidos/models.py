from django.db import models
from django.conf import settings
from productos.models import Producto


class Cart(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"Carrito {self.id} - {self.user}"


class CartItem(models.Model):
	cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Producto, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	price = models.DecimalField(max_digits=12, decimal_places=2)

	def __str__(self) -> str:
		return f"{self.product.nombre} x {self.quantity}"
