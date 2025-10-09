from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer
from productos.models import Producto
from django.shortcuts import get_object_or_404
from accounts.permissions import IsCliente
from decimal import Decimal


class CartViewSet(viewsets.ViewSet):
	def list(self, request):
		# devolver el carrito del usuario (suponiendo autenticación)
		user = request.user
		cart = Cart.objects.filter(user=user).first()
		if not cart:
			return Response({}, status=status.HTTP_200_OK)
		serializer = CartSerializer(cart)
		return Response(serializer.data)

	permission_classes = [permissions.IsAuthenticated, IsCliente]

	@action(detail=False, methods=['post'])
	def agregar(self, request):
		user = request.user
		product_id = request.data.get('productId')
		quantity = int(request.data.get('quantity', 1))
		product = get_object_or_404(Producto, pk=product_id)

		cart, _ = Cart.objects.get_or_create(user=user)
		item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity, 'price': product.precio})
		if not created:
			item.quantity += quantity
			item.save()
		# recalcular totales (simple)
		subtotal = sum(i.quantity * i.price for i in cart.items.all())
		if not isinstance(subtotal, Decimal):
			subtotal = Decimal(subtotal)
		iva = subtotal * Decimal('0.19')
		cart.subtotal = subtotal
		cart.iva = iva
		cart.total = subtotal + iva
		cart.save()
		return Response({'mensaje': 'Producto agregado al carrito'})
    
	@action(detail=False, methods=['get'])
	def count(self, request):
		user = request.user
		cart = Cart.objects.filter(user=user).first()
		count = sum(i.quantity for i in cart.items.all()) if cart else 0
		return Response({'count': count})

	@action(detail=False, methods=['put'], url_path='actualizar/(?P<productId>[^/.]+)')
	def actualizar(self, request, productId=None):
		user = request.user
		cart = Cart.objects.filter(user=user).first()
		if not cart:
			return Response({'error': 'Carrito no encontrado'}, status=404)
		try:
			item = cart.items.get(product__id=productId)
			qty = int(request.data.get('quantity', item.quantity))
			item.quantity = qty
			item.save()
			# recalc totals
			subtotal = sum(i.quantity * i.price for i in cart.items.all())
			if not isinstance(subtotal, Decimal):
				subtotal = Decimal(subtotal)
			cart.subtotal = subtotal
			cart.iva = subtotal * Decimal('0.19')
			cart.total = cart.subtotal + cart.iva
			cart.save()
			return Response({'mensaje': 'Cantidad actualizada'})
		except CartItem.DoesNotExist:
			return Response({'error': 'Item no encontrado'}, status=404)

	@action(detail=False, methods=['delete'], url_path='eliminar/(?P<productId>[^/.]+)')
	def eliminar(self, request, productId=None):
		user = request.user
		cart = Cart.objects.filter(user=user).first()
		if not cart:
			return Response({'error': 'Carrito no encontrado'}, status=404)
		deleted, _ = cart.items.filter(product__id=productId).delete()
		# recalc totals
		subtotal = sum(i.quantity * i.price for i in cart.items.all()) if cart.items.exists() else Decimal('0')
		if not isinstance(subtotal, Decimal):
			subtotal = Decimal(subtotal)
		cart.subtotal = subtotal
		cart.iva = subtotal * Decimal('0.19')
		cart.total = cart.subtotal + cart.iva
		cart.save()
		return Response({'mensaje': 'Item eliminado'})

	@action(detail=False, methods=['delete'])
	def limpiar(self, request):
		user = request.user
		cart = Cart.objects.filter(user=user).first()
		if cart:
			cart.items.all().delete()
			cart.subtotal = 0
			cart.iva = 0
			cart.total = 0
			cart.save()
		return Response({'mensaje': 'Carrito limpiado'})
