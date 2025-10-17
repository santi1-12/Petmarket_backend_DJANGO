from rest_framework import viewsets, permissions
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Categoria
from .serializers import ProductoSerializer
from .forms import ProductoForm
from accounts.permissions import IsEmpleadoOrAdmin


def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        # Allow read-only access to anyone, but require empleado/admin for unsafe methods
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [IsEmpleadoOrAdmin()]


# CRUD Productos para admin
@login_required
@user_passes_test(is_admin)
def productos_list(request):
    q = request.GET.get('q', '')
    productos = Producto.objects.select_related('categoria').all().order_by('-id')
    if q:
        productos = productos.filter(nombre__icontains=q) | productos.filter(descripcion__icontains=q)
    return render(request, 'admin_panel/productos_list.html', {'productos': productos, 'q': q})


@login_required
@user_passes_test(is_admin)
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/empleados/admin/?tab=productos')
    else:
        form = ProductoForm()
    return render(request, 'admin_panel/producto_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def producto_edit(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('/empleados/admin/?tab=productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'admin_panel/producto_form.html', {'form': form, 'producto': producto})


@login_required
@user_passes_test(is_admin)
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('/empleados/admin/?tab=productos')
    return render(request, 'admin_panel/producto_confirm_delete.html', {'producto': producto})


@login_required
@user_passes_test(is_admin)
def producto_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'admin_panel/producto_detail.html', {'producto': producto})


# CRUD Categorías para admin
@login_required
@user_passes_test(is_admin)
def categorias_list(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'admin_panel/categorias_list.html', {'categorias': categorias})


@login_required
@user_passes_test(is_admin)
def categoria_create(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre)
            return redirect('/productos/admin/categorias/')
    return render(request, 'admin_panel/categoria_form.html')


@login_required
@user_passes_test(is_admin)
def categoria_edit(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            categoria.nombre = nombre
            categoria.save()
            return redirect('/productos/admin/categorias/')
    return render(request, 'admin_panel/categoria_form.html', {'categoria': categoria})


@login_required
@user_passes_test(is_admin)
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('/productos/admin/categorias/')
    return render(request, 'admin_panel/categoria_confirm_delete.html', {'categoria': categoria})
