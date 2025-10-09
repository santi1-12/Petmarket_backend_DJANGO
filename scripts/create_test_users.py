import os
import sys
import django

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petmarket.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

users = [
    ('empleado1', 'empleado1@example.com', 'empleadopass', 'empleado'),
    ('cliente1', 'cliente1@example.com', 'clientepass', 'cliente'),
]

for username, email, password, role in users:
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, email=email, password=password)
        u.role = role
        u.save()
        print(f'Created user {username} with role {role}')
    else:
        print(f'User {username} already exists')
