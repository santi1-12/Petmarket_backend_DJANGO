from django.shortcuts import render, get_object_or_404
from .models import Producto
from django.shortcuts import redirect
from django.core.paginator import Paginator
from .forms import ProductoForm
from accounts.decorators import role_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def catalogo(request):
    qs = Producto.objects.all()
    q = request.GET.get('q')
    categorias = request.GET.getlist('categoria')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if q:
        qs = qs.filter(nombre__icontains=q) | qs.filter(descripcion__icontains=q)
    if categorias:
        qs = qs.filter(categoria__in=categorias)
    if min_price:
        try:
            qs = qs.filter(precio__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(precio__lte=float(max_price))
        except ValueError:
            pass

    categorias_disponibles = Producto.objects.order_by().values_list('categoria', flat=True).distinct()
    selected_categories = request.GET.getlist('categoria')

    return render(request, 'productos/catalogo.html', {
        'productos': qs,
        'categorias': [c for c in categorias_disponibles if c],
        'selected_categories': selected_categories,
    })


def producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'productos/detalle.html', {'producto': producto})


@role_required(('empleado', 'admin'))
def producto_crear(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('catalogo')
    else:
        form = ProductoForm()
    return render(request, 'productos/form.html', {'form': form, 'action': 'Crear producto'})


@role_required(('empleado', 'admin'))
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('producto_detalle', pk=producto.pk)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/form.html', {'form': form, 'action': 'Editar producto'})


@role_required(('empleado', 'admin'))
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('catalogo')
    return render(request, 'productos/confirm_delete.html', {'producto': producto})


@login_required
def dashboard(request):
    # Simple dashboard: counts
    total = Producto.objects.count()
    low_stock = Producto.objects.filter(stock__lt=5).count()
    return render(request, 'productos/dashboard.html', {'total': total, 'low_stock': low_stock})
