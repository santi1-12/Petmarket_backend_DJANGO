from django.shortcuts import render, redirect, get_object_or_404
from productos.models import Producto
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required


def add_to_cart(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, producto=producto)
        if not created:
            item.quantity += 1
        item.save()
    else:
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart
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
        qty = request.POST.get('qty')
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 1
        item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()
        if item:
            if qty <= 0:
                item.delete()
            else:
                item.quantity = qty
                item.save()
    return redirect('/carrito/')
