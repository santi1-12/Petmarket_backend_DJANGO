from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet

router = DefaultRouter()
# register as a viewset with custom basename
router.register(r'', CartViewSet, basename='cart')

app_name = 'pedidos'

urlpatterns = [
    path('', include(router.urls)),
]
