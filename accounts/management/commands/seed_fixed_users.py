from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create fixed users: usuario, empleado, admin with specified emails and passwords"

    def handle(self, *args, **options):
        User = get_user_model()

        created = 0

        # Normal user
        u1, _ = User.objects.get_or_create(
            username="usuario",
            defaults={
                "email": "usuario@gmail.com",
            },
        )
        u1.email = "usuario@gmail.com"
        if hasattr(u1, "role"):
            u1.role = "cliente"
        u1.is_staff = False
        u1.is_superuser = False
        u1.set_password("usuario1")
        u1.save()
        created += 1

        # Employee
        u2, _ = User.objects.get_or_create(
            username="empleado",
            defaults={
                "email": "empleado@gmail.com",
            },
        )
        u2.email = "empleado@gmail.com"
        if hasattr(u2, "role"):
            u2.role = "empleado"
        u2.is_staff = True  # allow access to admin if needed
        u2.is_superuser = False
        u2.set_password("empleado1")
        u2.save()
        created += 1

        # Admin (superuser)
        u3, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@gmail.com",
            },
        )
        u3.email = "admin@gmail.com"
        if hasattr(u3, "role"):
            u3.role = "admin"
        u3.is_staff = True
        u3.is_superuser = True
        u3.set_password("admin1")
        u3.save()
        created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded/updated {created} users (usuario, empleado, admin)."))
