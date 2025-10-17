from django.urls import path
from . import front_views
from .views import (
    productos_list, producto_create, producto_edit, producto_delete, producto_detail,
    categorias_list, categoria_create, categoria_edit, categoria_delete
)

urlpatterns = [
    path('', front_views.catalogo, name='catalogo'),
    path('dashboard/', front_views.dashboard, name='dashboard'),
    path('crear/', front_views.producto_crear, name='producto_crear'),
    path('<int:pk>/editar/', front_views.producto_editar, name='producto_editar'),
    path('<int:pk>/eliminar/', front_views.producto_eliminar, name='producto_eliminar'),
    path('<int:pk>/', front_views.producto_detalle, name='producto_detalle'),
    # Admin CRUD for productos
    path('admin/list/', productos_list, name='admin_productos_list'),
    path('admin/create/', producto_create, name='admin_producto_create'),
    path('admin/edit/<int:pk>/', producto_edit, name='admin_producto_edit'),
    path('admin/delete/<int:pk>/', producto_delete, name='admin_producto_delete'),
    path('admin/detail/<int:pk>/', producto_detail, name='admin_producto_detail'),
    # Admin CRUD for categorías
    path('admin/categorias/', categorias_list, name='admin_categorias_list'),
    path('admin/categorias/create/', categoria_create, name='admin_categoria_create'),
    path('admin/categorias/edit/<int:pk>/', categoria_edit, name='admin_categoria_edit'),
    path('admin/categorias/delete/<int:pk>/', categoria_delete, name='admin_categoria_delete'),
]
