from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

router = DefaultRouter()
# Register the productos viewset under the 'productos' prefix so generated
# routes are predictable (list, detail, etc.). Use a basename in case the
# ViewSet does not define a queryset attribute.
router.register(r'productos', ProductoViewSet, basename='producto')

urlpatterns = [
    path('', include(router.urls)),
]
