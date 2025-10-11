from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from productos.models import Producto
import random


class Command(BaseCommand):
    help = 'Crea un superusuario de prueba y puebla productos de ejemplo'

    def add_arguments(self, parser):
        parser.add_argument('--products', type=int, default=30, help='Número de productos a crear')
        parser.add_argument('--admin', action='store_true', help='Crear superusuario admin (username=admin, password=adminpass)')

    def handle(self, *args, **options):
        User = get_user_model()
        if options['admin']:
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
                self.stdout.write(self.style.SUCCESS('Superusuario "admin" creado con password "adminpass"'))
            else:
                self.stdout.write('Superusuario "admin" ya existe')

        count = options['products']
        categorias = ['Alimentos', 'Juguetes', 'Higiene', 'Accesorios', 'Camas', 'Ropa']
        created = 0
        for i in range(count):
            name = f"Producto {i+1}"
            desc = f"Descripción del producto {i+1}. Ideal para tu mascota. Calidad garantizada."
            precio = round(random.uniform(5, 150), 2)
            stock = random.randint(0, 50)
            categoria = random.choice(categorias)
            Producto.objects.create(nombre=name, descripcion=desc, precio=precio, stock=stock, categoria=categoria)
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Productos creados: {created}'))
