from django.db import models
from django.conf import settings
from datetime import datetime


class Factura(models.Model):
    TIPO_CHOICES = [
        ('factura', 'Factura'),
        ('cotizacion', 'Cotización'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    numero = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='factura')
    aplica_iva = models.BooleanField(default=True, verbose_name='Aplica IVA 19%')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagada'),
        ('cancelled', 'Anulada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    mp_preference_id = models.CharField(max_length=255, null=True, blank=True)
    mp_payment_id = models.CharField(max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    email_cliente = models.EmailField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.numero:
            fecha_hoy = datetime.now().strftime('%Y%m%d')
            prefijo = 'F' if self.tipo == 'factura' else 'COT'
            patron = f"{prefijo}-{fecha_hoy}-"
            # Usar values_list para evitar cargar columnas decimales que pueden causar InvalidOperation
            ultimo_numero = (
                Factura.objects
                .filter(numero__startswith=patron)
                .values_list('numero', flat=True)
                .order_by('-numero')
                .first()
            )
            if ultimo_numero:
                ultimo_secuencial = int(ultimo_numero.split('-')[-1])
                nuevo_secuencial = ultimo_secuencial + 1
            else:
                nuevo_secuencial = 1
            self.numero = f"{prefijo}-{fecha_hoy}-{nuevo_secuencial:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero} - {self.nombre_cliente or (self.user and self.user.username)}"


class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
