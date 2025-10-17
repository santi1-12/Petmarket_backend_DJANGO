from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet,
    productos_list, producto_create, producto_edit, producto_delete, producto_detail,
    categorias_list, categoria_create, categoria_edit, categoria_delete
)

router = DefaultRouter()
# Register at root of this include so that when we include this file under
# `path('api/productos/', include(...))` the list endpoint is exactly
# `/api/productos/` (not `/api/productos/productos/`).
router.register(r'', ProductoViewSet, basename='producto')

urlpatterns = [
    path('', include(router.urls)),
    # Admin CRUD para productos
    path('admin/list/', productos_list, name='admin_productos_list'),
    path('admin/create/', producto_create, name='admin_producto_create'),
    path('admin/edit/<int:pk>/', producto_edit, name='admin_producto_edit'),
    path('admin/delete/<int:pk>/', producto_delete, name='admin_producto_delete'),
    path('admin/detail/<int:pk>/', producto_detail, name='admin_producto_detail'),
    # Admin CRUD para categorías
    path('admin/categorias/', categorias_list, name='admin_categorias_list'),
    path('admin/categorias/create/', categoria_create, name='admin_categoria_create'),
    path('admin/categorias/edit/<int:pk>/', categoria_edit, name='admin_categoria_edit'),
    path('admin/categorias/delete/<int:pk>/', categoria_delete, name='admin_categoria_delete'),
]
