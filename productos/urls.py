from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

router = DefaultRouter()
# Register at root of this include so that when we include this file under
# `path('api/productos/', include(...))` the list endpoint is exactly
# `/api/productos/` (not `/api/productos/productos/`).
router.register(r'', ProductoViewSet, basename='producto')

urlpatterns = [
    path('', include(router.urls)),
]
