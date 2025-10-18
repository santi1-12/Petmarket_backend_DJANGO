from django.urls import path
from .views import (
    empleado_dashboard, admin_dashboard,
    empleados_list, empleado_create, empleado_edit, empleado_delete, empleado_detail,
    clientes_list, cliente_create, cliente_edit, cliente_delete, cliente_detail,
    pedidos_list, pedido_detail, pedido_update_status,
    notificaciones_list, notificacion_marcar_leida, notificacion_marcar_todas_leidas,
    admin_facturas_list, admin_factura_detail, factura_manual_create,
    admin_factura_pdf
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
    # Gestión de Pedidos
    path('pedidos/', pedidos_list, name='pedidos_list'),
    path('pedido/<int:pk>/', pedido_detail, name='pedido_detail'),
    path('pedido/<int:pk>/actualizar/', pedido_update_status, name='pedido_update_status'),
    # Gestión de Notificaciones
    path('notificaciones/', notificaciones_list, name='notificaciones_list'),
    path('notificacion/<int:pk>/marcar-leida/', notificacion_marcar_leida, name='notificacion_marcar_leida'),
    path('notificaciones/marcar-todas-leidas/', notificacion_marcar_todas_leidas, name='notificacion_marcar_todas_leidas'),
    # Gestión de Facturas
    path('admin/facturas/', admin_facturas_list, name='admin_facturas_list'),
    path('admin/factura/<int:pk>/', admin_factura_detail, name='admin_factura_detail'),
    path('admin/factura/<int:pk>/pdf/', admin_factura_pdf, name='admin_factura_pdf'),
    path('admin/factura/manual/', factura_manual_create, name='factura_manual_create'),
]