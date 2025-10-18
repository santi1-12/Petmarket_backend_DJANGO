#!/usr/bin/env python
"""
Script para crear un producto de prueba con precio inválido
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petmarket.settings')
django.setup()

from productos.models import Producto, Categoria
from decimal import Decimal

# Obtener o crear categoría de prueba
categoria_test, _ = Categoria.objects.get_or_create(nombre="TEST")

# Crear producto de prueba con precio 0 (inválido)
try:
    producto_test = Producto.objects.create(
        nombre="PRODUCTO DE PRUEBA - PRECIO INVÁLIDO",
        descripcion="Este producto tiene precio 0 para probar la validación del formulario",
        precio=Decimal('0.00'),
        stock=100,
        categoria=categoria_test
    )
    print(f"✅ Producto de prueba creado:")
    print(f"   ID: {producto_test.id}")
    print(f"   Nombre: {producto_test.nombre}")
    print(f"   Precio: ${producto_test.precio}")
    print(f"\n⚠️  Este producto NO se podrá agregar a una factura debido a la validación.")
except Exception as e:
    print(f"❌ Error al crear producto: {e}")
