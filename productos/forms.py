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
    categoria = forms.ChoiceField(choices=CATEGORIAS, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'image']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

