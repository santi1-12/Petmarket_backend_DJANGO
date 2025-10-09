from rest_framework import viewsets, permissions
from .models import Producto
from .serializers import ProductoSerializer
from accounts.permissions import IsEmpleadoOrAdmin


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        # Allow read-only access to anyone, but require empleado/admin for unsafe methods
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsEmpleadoOrAdmin()]
