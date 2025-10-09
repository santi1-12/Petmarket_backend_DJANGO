from django.db import models
from django.conf import settings

class Factura(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    numero = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mp_preference_id = models.CharField(max_length=255, null=True, blank=True)
    mp_payment_id = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Factura {self.numero} - {self.user}"
