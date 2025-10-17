import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petmarket.settings')
django.setup()

from productos.models import Categoria, Producto

# Crear categorías
categorias = [
    'Alimentos',
    'Accesorios',
    'Juguetes',
    'Higiene',
    'Salud',
    'Ropa'
]

print("Creando categorías...")
categorias_obj = {}
for cat_nombre in categorias:
    cat, created = Categoria.objects.get_or_create(nombre=cat_nombre)
    categorias_obj[cat_nombre] = cat
    if created:
        print(f"✓ Categoría creada: {cat_nombre}")
    else:
        print(f"- Categoría ya existe: {cat_nombre}")

# Crear productos
productos = [
    {
        'nombre': 'Alimento Premium para Perros',
        'descripcion': 'Alimento balanceado de alta calidad para perros adultos. Rico en proteínas y vitaminas.',
        'precio': 45000,
        'stock': 50,
        'categoria': 'Alimentos'
    },
    {
        'nombre': 'Alimento para Gatos Adultos',
        'descripcion': 'Alimento completo para gatos adultos con omega 3 y 6.',
        'precio': 38000,
        'stock': 45,
        'categoria': 'Alimentos'
    },
    {
        'nombre': 'Collar Antipulgas',
        'descripcion': 'Collar efectivo contra pulgas y garrapatas por hasta 8 meses.',
        'precio': 25000,
        'stock': 30,
        'categoria': 'Accesorios'
    },
    {
        'nombre': 'Correa Extensible',
        'descripcion': 'Correa retráctil de 5 metros para paseos cómodos.',
        'precio': 35000,
        'stock': 25,
        'categoria': 'Accesorios'
    },
    {
        'nombre': 'Pelota Kong',
        'descripcion': 'Juguete resistente para perros, ideal para ejercicio y entretenimiento.',
        'precio': 18000,
        'stock': 60,
        'categoria': 'Juguetes'
    },
    {
        'nombre': 'Ratón de Juguete',
        'descripcion': 'Juguete interactivo para gatos con catnip incluido.',
        'precio': 8000,
        'stock': 80,
        'categoria': 'Juguetes'
    },
    {
        'nombre': 'Shampoo para Mascotas',
        'descripcion': 'Shampoo hipoalergénico con aroma a lavanda.',
        'precio': 22000,
        'stock': 40,
        'categoria': 'Higiene'
    },
    {
        'nombre': 'Cepillo Dental Canino',
        'descripcion': 'Kit de limpieza dental completo para perros.',
        'precio': 15000,
        'stock': 35,
        'categoria': 'Higiene'
    },
    {
        'nombre': 'Suplemento Vitamínico',
        'descripcion': 'Multivitamínico para fortalecer el sistema inmune.',
        'precio': 42000,
        'stock': 20,
        'categoria': 'Salud'
    },
    {
        'nombre': 'Antipulgas Pipeta',
        'descripcion': 'Tratamiento tópico contra pulgas, garrapatas y piojos.',
        'precio': 32000,
        'stock': 55,
        'categoria': 'Salud'
    },
    {
        'nombre': 'Suéter para Perro',
        'descripcion': 'Suéter abrigado para perros pequeños y medianos.',
        'precio': 28000,
        'stock': 15,
        'categoria': 'Ropa'
    },
    {
        'nombre': 'Cama Ortopédica',
        'descripcion': 'Cama ergonómica con memory foam para mascotas.',
        'precio': 65000,
        'stock': 12,
        'categoria': 'Accesorios'
    },
]

print("\nCreando productos...")
for prod_data in productos:
    cat_nombre = prod_data.pop('categoria')
    categoria = categorias_obj[cat_nombre]
    
    prod, created = Producto.objects.get_or_create(
        nombre=prod_data['nombre'],
        defaults={
            **prod_data,
            'categoria': categoria
        }
    )
    if created:
        print(f"✓ Producto creado: {prod.nombre}")
    else:
        print(f"- Producto ya existe: {prod.nombre}")

print("\n✅ ¡Base de datos poblada exitosamente!")
print(f"Total categorías: {Categoria.objects.count()}")
print(f"Total productos: {Producto.objects.count()}")
