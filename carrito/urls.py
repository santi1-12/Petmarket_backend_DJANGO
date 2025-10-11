from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('', views.view_cart, name='view_cart'),
    path('remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
]
