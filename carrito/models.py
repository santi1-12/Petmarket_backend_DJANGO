from django.db import models
from django.conf import settings
from productos.models import Producto


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carrito_cart')
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.user})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='carrito_items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='carrito_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'producto')

    def subtotal(self):
        return self.producto.precio * self.quantity

    def __str__(self):
        return f"{self.producto.nombre} x {self.quantity}"
