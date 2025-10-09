from django.db import models


class Cliente(models.Model):
	nombre = models.CharField(max_length=150)
	email = models.EmailField(unique=True)
	telefono = models.CharField(max_length=30, blank=True, null=True)
	direccion = models.TextField(blank=True, null=True)

	def __str__(self) -> str:
		return f"{self.nombre} <{self.email}>"
