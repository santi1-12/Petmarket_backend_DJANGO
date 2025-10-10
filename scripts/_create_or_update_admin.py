import os
import sys

# Ensure project root is on PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'petmarket.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
email = 'adminPetmarket@gmail.com'
password = 'Admin#*'

u = User.objects.filter(username=username).first()
if u:
    u.email = email
    u.set_password(password)
    u.save()
    print(f"Superuser '{username}' updated")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created")
