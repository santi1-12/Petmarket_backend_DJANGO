from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.contrib import messages
from clientes.forms import ClienteForm
from clientes.models import Cliente
from facturas.models import Factura
from productos.models import Producto
from pedidos.models import Pedido, Notificacion
from .forms import EmpleadoForm
from facturas.forms import FacturaManualForm, FacturaItemForm
from django.forms import formset_factory
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

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
    pedidos = Pedido.objects.select_related('user').prefetch_related('items__producto').all().order_by('-creado_en')
    
    # Estadísticas de pedidos
    pedidos_stats = {
        'total': pedidos.count(),
        'sin_entregar': pedidos.filter(estado='sin_entregar').count(),
        'en_camino': pedidos.filter(estado='en_camino').count(),
        'entregado': pedidos.filter(estado='entregado').count(),
    }
    
    return render(request, 'admin_panel/dashboard.html', {
        'clientes': clientes,
        'empleados': empleados,
        'productos': productos,
        'facturas': facturas,
        'pedidos': pedidos,
        'pedidos_stats': pedidos_stats,
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
    
    # Estadísticas de pedidos
    pedidos_stats = {
        'total': pedidos.count(),
        'sin_entregar': pedidos.filter(estado='sin_entregar').count(),
        'en_camino': pedidos.filter(estado='en_camino').count(),
        'entregado': pedidos.filter(estado='entregado').count(),
    }

    return render(request, 'empleados/dashboard.html', {
        'productos': productos,
        'pedidos': pedidos,
        'notificaciones': notificaciones,
        'pedidos_stats': pedidos_stats,
    })


# Gestión de Pedidos para Empleados
@login_required
def pedidos_list(request):
    """Lista todos los pedidos con filtros de estado"""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ['empleado', 'admin']):
        return HttpResponseForbidden("No autorizado")
    
    estado = request.GET.get('estado', '')
    q = request.GET.get('q', '')
    
    pedidos = Pedido.objects.select_related('user').prefetch_related('items__producto').all().order_by('-creado_en')
    
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    if q:
        pedidos = pedidos.filter(user__username__icontains=q) | pedidos.filter(user__email__icontains=q)
    
    # Contar pedidos por estado
    stats = {
        'total': Pedido.objects.count(),
        'sin_entregar': Pedido.objects.filter(estado='sin_entregar').count(),
        'en_camino': Pedido.objects.filter(estado='en_camino').count(),
        'entregado': Pedido.objects.filter(estado='entregado').count(),
    }
    
    return render(request, 'empleados/pedidos_list.html', {
        'pedidos': pedidos,
        'estado': estado,
        'q': q,
        'stats': stats,
    })


@login_required
def pedido_detail(request, pk):
    """Muestra detalles de un pedido específico"""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ['empleado', 'admin']):
        return HttpResponseForbidden("No autorizado")
    
    pedido = get_object_or_404(
        Pedido.objects.select_related('user').prefetch_related('items__producto'),
        pk=pk
    )
    
    return render(request, 'empleados/pedido_detail.html', {'pedido': pedido})


@login_required
def pedido_update_status(request, pk):
    """Actualiza el estado de un pedido"""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ['empleado', 'admin']):
        return HttpResponseForbidden("No autorizado")
    
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del pedido #{pedido.id} actualizado a: {pedido.get_estado_display()}')
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'estado': pedido.estado,
                    'estado_display': pedido.get_estado_display()
                })
        else:
            messages.error(request, 'Estado inválido')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Estado inválido'})
    
    return redirect('empleados:pedido_detail', pk=pk)


# Gestión de Notificaciones
@login_required
def notificaciones_list(request):
    """Lista todas las notificaciones de usuarios"""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ['empleado', 'admin']):
        return HttpResponseForbidden("No autorizado")
    
    filtro = request.GET.get('filtro', 'todas')
    
    notificaciones = Notificacion.objects.select_related('user').order_by('-creada_en')
    
    if filtro == 'no_leidas':
        notificaciones = notificaciones.filter(leida=False)
    elif filtro == 'leidas':
        notificaciones = notificaciones.filter(leida=True)
    
    stats = {
        'total': Notificacion.objects.count(),
        'no_leidas': Notificacion.objects.filter(leida=False).count(),
        'leidas': Notificacion.objects.filter(leida=True).count(),
    }
    
    return render(request, 'empleados/notificaciones_list.html', {
        'notificaciones': notificaciones,
        'filtro': filtro,
        'stats': stats,
    })


@login_required
def notificacion_marcar_leida(request, pk):
    """Marca una notificación como leída"""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ['empleado', 'admin']):
        return HttpResponseForbidden("No autorizado")
    
    notificacion = get_object_or_404(Notificacion, pk=pk)
    notificacion.leida = True
    notificacion.save()
    
    messages.success(request, 'Notificación marcada como leída')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('empleados:notificaciones_list')


@login_required
def notificacion_marcar_todas_leidas(request):
    """Marca todas las notificaciones como leídas"""
    role = getattr(request.user, 'role', None)
    if not (request.user.is_superuser or role in ['empleado', 'admin']):
        return HttpResponseForbidden("No autorizado")
    
    if request.method == 'POST':
        count = Notificacion.objects.filter(leida=False).update(leida=True)
        messages.success(request, f'{count} notificaciones marcadas como leídas')
    
    return redirect('empleados:notificaciones_list')

@login_required
@user_passes_test(is_admin)
def admin_facturas_list(request):
    facturas = Factura.objects.order_by('-created_at')
    return render(request, 'admin_panel/facturas_list.html', {'facturas': facturas})

@login_required
@user_passes_test(is_admin)
def admin_factura_detail(request, pk):
    factura = get_object_or_404(Factura, pk=pk)
    return render(request, 'admin_panel/factura_detail.html', {'factura': factura})


@login_required
@user_passes_test(is_admin)
def admin_factura_pdf(request, pk):
    factura = get_object_or_404(Factura.objects.prefetch_related('items__producto'), pk=pk)

    # Configurar respuesta PDF
    response = HttpResponse(content_type='application/pdf')
    filename = f"{factura.get_tipo_display()}-{factura.numero}.pdf".replace(' ', '_')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Crear PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    margin = 18 * mm

    # Encabezado
    p.setFillColorRGB(0.40, 0.49, 0.92)  # ~ #667eea
    p.rect(0, height - 40, width, 40, stroke=0, fill=1)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, height - 25, f"{factura.get_tipo_display()} #{factura.numero}")
    p.setFont("Helvetica", 10)
    p.drawString(margin, height - 38, f"Fecha: {factura.created_at.strftime('%d/%m/%Y %H:%M')}")

    # Datos cliente
    y = height - 70
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(margin, y, "Información del Cliente")
    p.setFont("Helvetica", 10)
    y -= 14
    nombre = factura.nombre_cliente or (factura.user.get_full_name() if factura.user and factura.user.get_full_name() else (factura.user.username if factura.user else "Cliente sin registrar"))
    email = factura.email_cliente or (factura.user.email if factura.user else "No especificado")
    p.drawString(margin, y, f"Cliente: {nombre}")
    y -= 12
    p.drawString(margin, y, f"Email: {email}")

    # Items table header
    y -= 24
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margin, y, "Producto")
    p.drawRightString(width - margin - 110, y, "Cantidad")
    p.drawRightString(width - margin - 60, y, "Precio")
    p.drawRightString(width - margin, y, "Subtotal")
    p.setLineWidth(0.5)
    p.line(margin, y - 2, width - margin, y - 2)

    # Items rows
    p.setFont("Helvetica", 10)
    y -= 16
    for item in factura.items.all():
        if y < 80:  # salto de página si necesario
            p.showPage()
            y = height - 40
        p.drawString(margin, y, item.producto.nombre[:50])
        p.drawRightString(width - margin - 110, y, str(item.cantidad))
        p.drawRightString(width - margin - 60, y, f"${item.precio:.2f}")
        p.drawRightString(width - margin, y, f"${item.subtotal:.2f}")
        y -= 14

    # Resumen
    y -= 10
    p.setLineWidth(0.5)
    p.line(width - margin - 200, y, width - margin, y)
    y -= 16
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(width - margin - 80, y, "Subtotal:")
    p.setFont("Helvetica", 11)
    p.drawRightString(width - margin, y, f"${float(factura.subtotal):.2f}")
    if factura.aplica_iva:
        y -= 14
        p.setFont("Helvetica-Bold", 11)
        p.drawRightString(width - margin - 80, y, "IVA (19%):")
        p.setFont("Helvetica", 11)
        p.drawRightString(width - margin, y, f"${float(factura.iva):.2f}")
    y -= 16
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - margin - 80, y, "Total:")
    p.drawRightString(width - margin, y, f"${float(factura.total):.2f}")

    p.showPage()
    p.save()
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser or u.role in ['admin', 'empleado'])
def factura_manual_create(request):
    FacturaItemFormSet = formset_factory(FacturaItemForm, extra=1, min_num=1, validate_min=True)
    if request.method == 'POST':
        factura_form = FacturaManualForm(request.POST)
        formset = FacturaItemFormSet(request.POST)
        
        # Validar formularios y mostrar errores específicos
        factura_valid = factura_form.is_valid()
        formset_valid = formset.is_valid()
        
        if not factura_valid:
            for field, errors in factura_form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
        
        if not formset_valid:
            for i, form in enumerate(formset):
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(request, f'Producto #{i+1} - {error}')
        
        if factura_valid and formset_valid:
            factura = factura_form.save(commit=False)
            # Asignar cliente o datos manuales
            if factura_form.cleaned_data['cliente']:
                factura.user = factura_form.cleaned_data['cliente']
                factura.nombre_cliente = ''
                factura.email_cliente = ''
            else:
                factura.user = None
                factura.nombre_cliente = factura_form.cleaned_data['nombre_cliente']
                factura.email_cliente = factura_form.cleaned_data['email_cliente']
            factura.tipo = factura_form.cleaned_data['tipo']
            factura.aplica_iva = factura_form.cleaned_data['aplica_iva']
            # Calcular subtotal, iva y total y generar número sin tocar el save() del modelo
            from decimal import Decimal, ROUND_HALF_UP
            from datetime import datetime

            subtotal = Decimal('0.00')
            
            # Primero calculamos el subtotal SIN guardar los items
            for item_form in formset:
                if item_form.cleaned_data.get('producto') and item_form.cleaned_data.get('cantidad'):
                    producto = item_form.cleaned_data['producto']
                    cantidad = item_form.cleaned_data['cantidad']
                    precio = producto.precio
                    item_subtotal = cantidad * precio
                    subtotal += item_subtotal
            
            # IVA y totales (cuantizados a 2 decimales)
            iva = Decimal('0.00')
            if factura.aplica_iva:
                iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            subtotal = subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total = (subtotal + iva).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            factura.subtotal = subtotal
            factura.iva = iva
            factura.total = total

            # Generar número de documento aquí para evitar leer columnas decimales desde el modelo
            prefijo = 'F' if factura.tipo == 'factura' else 'COT'
            fecha_hoy = datetime.now().strftime('%Y%m%d')
            patron = f"{prefijo}-{fecha_hoy}-"
            ultimo_numero = (
                Factura.objects
                .filter(numero__startswith=patron)
                .values_list('numero', flat=True)
                .order_by('-numero')
                .first()
            )
            if ultimo_numero:
                ultimo_secuencial = int(ultimo_numero.split('-')[-1])
                nuevo_secuencial = ultimo_secuencial + 1
            else:
                nuevo_secuencial = 1
            factura.numero = f"{prefijo}-{fecha_hoy}-{nuevo_secuencial:03d}"

            factura.save()
            
            # Ahora guardamos los items (cuantizar decimales a 2 lugares)
            for item_form in formset:
                if item_form.cleaned_data.get('producto') and item_form.cleaned_data.get('cantidad'):
                    producto = item_form.cleaned_data['producto']
                    cantidad = item_form.cleaned_data['cantidad']
                    
                    item = item_form.save(commit=False)
                    item.factura = factura
                    item.producto = producto
                    item.cantidad = cantidad
                    # Cuantizar precio y subtotal a 2 decimales para evitar InvalidOperation
                    item.precio = Decimal(str(producto.precio)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    item.subtotal = (Decimal(str(cantidad)) * item.precio).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    item.save()
            
            messages.success(request, f'Factura #{factura.numero} creada exitosamente')
            return redirect('empleados:admin_factura_detail', pk=factura.pk)
    else:
        factura_form = FacturaManualForm()
        formset = FacturaItemFormSet()
    
    # Obtener todos los productos para validación JavaScript
    from productos.models import Producto
    productos = Producto.objects.all()
    
    return render(request, 'admin_panel/factura_manual_form.html', {
        'factura_form': factura_form,
        'formset': formset,
        'productos': productos,
    })
