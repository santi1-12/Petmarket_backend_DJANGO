#!/usr/bin/env python
"""
Script para verificar productos y sus precios
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petmarket.settings')
django.setup()

from productos.models import Producto

# Listar primeros 5 productos
print("=" * 60)
print("PRODUCTOS EN LA BASE DE DATOS")
print("=" * 60)

productos = Producto.objects.all()[:5]
for p in productos:
    print(f"ID: {p.id:3d} | Nombre: {p.nombre:30s} | Precio: ${p.precio}")

print("=" * 60)
print(f"Total de productos: {Producto.objects.count()}")
