from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from productos.models import Producto
from .models import Cart, CartItem
from pedidos.models import Pedido, PedidoItem, Notificacion
from facturas.models import Factura
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
import random
import string

@login_required
def finalizar_compra(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.carrito_items.exists():
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('/carrito/')

    # Calcular total
    total = Decimal('0.00')
    for item in cart.carrito_items.select_related('producto').all():
        total += item.subtotal()

    # Crear pedido
    pedido = Pedido.objects.create(user=request.user)
    for item in cart.carrito_items.select_related('producto').all():
        PedidoItem.objects.create(
            pedido=pedido, 
            producto=item.producto, 
            cantidad=item.quantity
        )
        # Reducir stock
        item.producto.stock -= item.quantity
        item.producto.save()

    # Generar factura
    numero_factura = f"FAC-{timezone.now().strftime('%Y%m%d')}-{''.join(random.choices(string.digits, k=6))}"
    factura = Factura.objects.create(
        user=request.user,
        numero=numero_factura,
        total=total,
        status='paid',
        paid_at=timezone.now()
    )

    # Limpiar carrito
    cart.carrito_items.all().delete()

    # Notificar admin y empleados
    User = get_user_model()
    admins = User.objects.filter(is_superuser=True)
    empleados = User.objects.filter(role='empleado')
    mensaje = f"Nuevo pedido de {request.user.username} (ID pedido: {pedido.id}, Factura: {factura.numero})"
    for admin in admins:
        Notificacion.objects.create(user=admin, mensaje=mensaje)
    for emp in empleados:
        Notificacion.objects.create(user=emp, mensaje=mensaje)

    messages.success(request, f'¡Compra realizada exitosamente! Número de factura: {factura.numero}')
    return render(request, 'carrito/compra_exitosa.html', {
        'pedido': pedido,
        'factura': factura,
        'items': pedido.items.select_related('producto').all()
    })


def add_to_cart(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, producto=producto)
        if not created:
            item.quantity += 1
        item.save()
        
        if is_ajax:
            # Return JSON response for AJAX requests
            from django.http import JsonResponse
            cart_count = cart.carrito_items.count()
            return JsonResponse({
                'success': True,
                'message': f'{producto.nombre} agregado al carrito',
                'cart_count': cart_count
            })
    else:
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart
        
        if is_ajax:
            from django.http import JsonResponse
            cart_count = len(cart)
            return JsonResponse({
                'success': True,
                'message': f'{producto.nombre} agregado al carrito',
                'cart_count': cart_count
            })
    
    messages.success(request, f'{producto.nombre} agregado al carrito')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def view_cart(request):
    items = []
    total = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        # related_name on CartItem is 'carrito_items'
        for it in cart.carrito_items.select_related('producto').all():
            items.append({'producto': it.producto, 'qty': it.quantity, 'subtotal': it.subtotal(), 'id': it.id})
            total += it.subtotal()
    else:
        cart = request.session.get('cart', {})
        for pid, qty in cart.items():
            try:
                p = Producto.objects.get(pk=int(pid))
                items.append({'producto': p, 'qty': qty, 'subtotal': p.precio * qty})
                total += p.precio * qty
            except Producto.DoesNotExist:
                pass
    return render(request, 'carrito/cart.html', {'items': items, 'total': total})


def remove_from_cart(request, pk):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart, producto_id=pk).delete()
    else:
        cart = request.session.get('cart', {})
        if str(pk) in cart:
            del cart[str(pk)]
            request.session['cart'] = cart
    return redirect('/carrito/')


@login_required
def update_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')  # 'increase', 'decrease', or 'set'
        qty = request.POST.get('qty')
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if item:
            if action == 'increase':
                item.quantity += 1
                item.save()
            elif action == 'decrease':
                if item.quantity > 1:
                    item.quantity -= 1
                    item.save()
                else:
                    item.delete()
                    if is_ajax:
                        from django.http import JsonResponse
                        return JsonResponse({
                            'success': True,
                            'deleted': True,
                            'message': 'Producto eliminado del carrito'
                        })
            elif action == 'set' and qty:
                try:
                    qty = int(qty)
                    if qty <= 0:
                        item.delete()
                        if is_ajax:
                            from django.http import JsonResponse
                            return JsonResponse({
                                'success': True,
                                'deleted': True,
                                'message': 'Producto eliminado del carrito'
                            })
                    else:
                        item.quantity = qty
                        item.save()
                except (TypeError, ValueError):
                    pass
            
            if is_ajax and item.pk:  # Item still exists
                from django.http import JsonResponse
                cart_items = CartItem.objects.filter(cart__user=request.user)
                total = sum(it.subtotal() for it in cart_items)
                return JsonResponse({
                    'success': True,
                    'quantity': item.quantity,
                    'subtotal': float(item.subtotal()),
                    'total': float(total),
                    'message': 'Carrito actualizado'
                })
        
        if is_ajax:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'message': 'Item no encontrado'})
    
    return redirect('/carrito/')
