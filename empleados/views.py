from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from clientes.forms import ClienteForm
from clientes.models import Cliente
from facturas.models import Factura
from productos.models import Producto
from pedidos.models import Pedido, Notificacion
from .forms import EmpleadoForm

# Función para verificar si el usuario es admin
def is_admin(user):
    return user.is_superuser or getattr(user, 'role', None) == 'admin'

# CRUD clientes para admin
@login_required
@user_passes_test(is_admin)
def clientes_list(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.all().order_by('-id')
    if q:
        clientes = clientes.filter(nombre__icontains=q) | clientes.filter(email__icontains=q)
    return render(request, 'admin_panel/clientes_list.html', {'clientes': clientes, 'q': q})

@login_required
@user_passes_test(is_admin)
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/empleados/admin/?tab=clientes')
    else:
        form = ClienteForm()
    return render(request, 'admin_panel/cliente_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def cliente_edit(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('/empleados/admin/?tab=clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'admin_panel/cliente_form.html', {'form': form, 'cliente': cliente})

@login_required
@user_passes_test(is_admin)
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('/empleados/admin/?tab=clientes')
    return render(request, 'admin_panel/cliente_confirm_delete.html', {'cliente': cliente})

@login_required
@user_passes_test(is_admin)
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'admin_panel/cliente_detail.html', {'cliente': cliente})

# CRUD empleados para admin
@login_required
@user_passes_test(is_admin)
def empleados_list(request):
    User = get_user_model()
    q = request.GET.get('q', '')
    empleados = User.objects.filter(role='empleado')
    if q:
        empleados = empleados.filter(first_name__icontains=q) | empleados.filter(last_name__icontains=q) | empleados.filter(email__icontains=q)
    return render(request, 'admin_panel/empleados_list.html', {'empleados': empleados, 'q': q})

@login_required
@user_passes_test(is_admin)
def empleado_create(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/empleados/admin/?tab=empleados')
    else:
        form = EmpleadoForm(initial={'role': 'empleado'})
    return render(request, 'admin_panel/empleado_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def empleado_edit(request, pk):
    User = get_user_model()
    empleado = get_object_or_404(User, pk=pk, role='empleado')
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('/empleados/admin/?tab=empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'admin_panel/empleado_form.html', {'form': form, 'empleado': empleado})

@login_required
@user_passes_test(is_admin)
def empleado_delete(request, pk):
    User = get_user_model()
    empleado = get_object_or_404(User, pk=pk, role='empleado')
    if request.method == 'POST':
        empleado.delete()
        return redirect('/empleados/admin/?tab=empleados')
    return render(request, 'admin_panel/empleado_confirm_delete.html', {'empleado': empleado})

@login_required
@user_passes_test(is_admin)
def empleado_detail(request, pk):
    User = get_user_model()
    empleado = get_object_or_404(User, pk=pk, role='empleado')
    return render(request, 'admin_panel/empleado_detail.html', {'empleado': empleado})

# Vista para el panel de admin
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    User = get_user_model()
    clientes = Cliente.objects.all()
    empleados = User.objects.filter(role='empleado')
    productos = Producto.objects.all()
    facturas = Factura.objects.all()
    return render(request, 'admin_panel/dashboard.html', {
        'clientes': clientes,
        'empleados': empleados,
        'productos': productos,
        'facturas': facturas,
    })

# Vista para el panel de empleado
@login_required
def empleado_dashboard(request):
    role = getattr(request.user, 'role', None)
    if not (request.user.is_staff or role == 'empleado'):
        return HttpResponseForbidden("No autorizado")

    productos = Producto.objects.all()
    pedidos = Pedido.objects.select_related('user').prefetch_related('items__producto').all().order_by('-creado_en')
    notificaciones = Notificacion.objects.select_related('user').order_by('-creada_en')[:20]

    return render(request, 'empleados/dashboard.html', {
        'productos': productos,
        'pedidos': pedidos,
        'notificaciones': notificaciones,
    })

