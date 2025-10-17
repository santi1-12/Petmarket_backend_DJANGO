from django import forms
from .models import Producto

CATEGORIAS = [
    ("alimento", "Alimento"),
    ("accesorios", "Accesorios"),
    ("ropa", "Ropa"),
    ("juguetes", "Juguetes"),
    ("higiene", "Higiene"),
]

class ProductoForm(forms.ModelForm):
    categoria = forms.ChoiceField(choices=CATEGORIAS, required=False)
    image = forms.ImageField(required=False)

    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria', 'descripcion', 'image']
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'image']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
