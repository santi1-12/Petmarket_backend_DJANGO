from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'role', None) == 'admin')


class IsEmpleadoOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'role', None) in ('empleado', 'admin'))


class IsCliente(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'role', None) == 'cliente')
