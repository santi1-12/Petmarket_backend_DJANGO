from django.urls import path
from . import front_views

urlpatterns = [
    path('', front_views.catalogo, name='catalogo'),
    path('dashboard/', front_views.dashboard, name='dashboard'),
    path('crear/', front_views.producto_crear, name='producto_crear'),
    path('<int:pk>/editar/', front_views.producto_editar, name='producto_editar'),
    path('<int:pk>/eliminar/', front_views.producto_eliminar, name='producto_eliminar'),
    path('<int:pk>/', front_views.producto_detalle, name='producto_detalle'),
]
