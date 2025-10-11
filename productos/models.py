from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='productos/', null=True, blank=True)
    categoria = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.nombre
