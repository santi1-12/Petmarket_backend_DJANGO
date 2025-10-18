from django import forms
from facturas.models import Factura, FacturaItem
from productos.models import Producto
from django.contrib.auth import get_user_model

User = get_user_model()

class FacturaManualForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=User.objects.all(), required=False, label="Cliente (opcional)")
    nombre_cliente = forms.CharField(max_length=100, required=False, label="Nombre del cliente (si no está registrado)")
    email_cliente = forms.EmailField(required=False, label="Email del cliente (opcional)")
    tipo = forms.ChoiceField(choices=[('factura', 'Factura'), ('cotizacion', 'Cotización')], label="Tipo de documento")
    aplica_iva = forms.BooleanField(required=False, label="¿Aplicar IVA 19%?", initial=True)

    class Meta:
        model = Factura
        fields = ['cliente', 'nombre_cliente', 'email_cliente', 'tipo', 'aplica_iva']

class FacturaItemForm(forms.ModelForm):
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), label="Producto")
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")

    class Meta:
        model = FacturaItem
        fields = ['producto', 'cantidad']
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        
        if producto and cantidad:
            from decimal import Decimal, InvalidOperation
            try:
                # Validar que el precio del producto sea un decimal válido
                precio = Decimal(str(producto.precio))
                if precio <= 0:
                    raise forms.ValidationError(
                        f'El producto "{producto.nombre}" tiene un precio inválido (${producto.precio}). '
                        'Por favor, corrija el precio del producto antes de agregarlo a la factura.'
                    )
                # Validar que el subtotal no cause overflow
                subtotal = precio * Decimal(str(cantidad))
                if subtotal > Decimal('9999999999.99'):
                    raise forms.ValidationError(
                        f'La cantidad ({cantidad}) multiplicada por el precio (${precio}) excede el límite permitido. '
                        'Reduzca la cantidad o el precio del producto.'
                    )
            except (InvalidOperation, ValueError, TypeError) as e:
                raise forms.ValidationError(
                    f'El producto "{producto.nombre}" tiene un precio con formato inválido. '
                    f'Por favor, corrija el precio del producto (actual: {producto.precio}) antes de continuar.'
                )
        
        return cleaned_data
