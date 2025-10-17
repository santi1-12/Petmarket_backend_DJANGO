from django.urls import path
from .views import (
    empleado_dashboard, admin_dashboard,
    empleados_list, empleado_create, empleado_edit, empleado_delete, empleado_detail,
    clientes_list, cliente_create, cliente_edit, cliente_delete, cliente_detail
)

app_name = 'empleados'

urlpatterns = [
    # Web panel for empleados
    path('panel/', empleado_dashboard, name='dashboard'),
    path('admin/', admin_dashboard, name='admin_dashboard'),
    # CRUD empleados para admin
    path('admin/empleados/', empleados_list, name='empleados_list'),
    path('admin/empleado/add/', empleado_create, name='empleado_create'),
    path('admin/empleado/<int:pk>/', empleado_detail, name='empleado_detail'),
    path('admin/empleado/<int:pk>/edit/', empleado_edit, name='empleado_edit'),
    path('admin/empleado/<int:pk>/delete/', empleado_delete, name='empleado_delete'),
    # CRUD clientes para admin
    path('admin/clientes/', clientes_list, name='clientes_list'),
    path('admin/cliente/add/', cliente_create, name='cliente_create'),
    path('admin/cliente/<int:pk>/', cliente_detail, name='cliente_detail'),
    path('admin/cliente/<int:pk>/edit/', cliente_edit, name='cliente_edit'),
    path('admin/cliente/<int:pk>/delete/', cliente_delete, name='cliente_delete'),
]
