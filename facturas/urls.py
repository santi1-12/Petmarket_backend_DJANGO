from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet

router = DefaultRouter()
router.register(r'', FacturaViewSet, basename='factura')

urlpatterns = [
    path('', include(router.urls)),
    # webhook will be available at /api/facturas/webhook/
]
