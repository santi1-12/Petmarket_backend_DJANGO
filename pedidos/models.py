
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


# Pedido principal
class Pedido(models.Model):
	ESTADO_CHOICES = [
		("sin_entregar", "Sin entregar"),
		("en_camino", "En camino"),
		("entregado", "Entregado"),
	]
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos")
	productos = models.ManyToManyField(Producto, through="PedidoItem")
	estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="sin_entregar")
	creado_por_empleado = models.BooleanField(default=False)
	creado_en = models.DateTimeField(auto_now_add=True)
	actualizado_en = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Pedido {self.id} - {self.user} - {self.get_estado_display()}"


class PedidoItem(models.Model):
	pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
	producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
	cantidad = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.producto.nombre} x {self.cantidad}"


# Notificaciones de usuario a empleado
class Notificacion(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notificaciones")
	mensaje = models.TextField()
	leida = models.BooleanField(default=False)
	creada_en = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Notificación de {self.user.username} - {'Leída' if self.leida else 'No leída'}"
