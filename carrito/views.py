from django.shortcuts import render, redirect, get_object_or_404
from productos.models import Producto


def add_to_cart(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER', '/'))


def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            p = Producto.objects.get(pk=int(pid))
            items.append({'producto': p, 'qty': qty, 'subtotal': p.precio * qty})
            total += p.precio * qty
        except Producto.DoesNotExist:
            pass
    return render(request, 'carrito/cart.html', {'items': items, 'total': total})


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
    return redirect('/carrito/')
