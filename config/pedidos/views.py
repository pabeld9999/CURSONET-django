# Importa HttpResponse para devolver texto simple al navegador
# from django.http import HttpResponse

# (Opcional) render se usará más adelante para templates
from django.shortcuts import render
from .models import Producto, Pedido, DetallePedido, Categoria
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Count, Sum, F
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta
from django.http import HttpResponse
from django.contrib.auth import logout
import csv
import io
import json


# Vista básica que responde a una solicitud HTTP
def inicio(request):
    # Retorna texto simple al navegador
    # return HttpResponse("Bienvenido al sistema de cafetería")
    return render(request, "inicio.html")


def lista_productos(request, categoria_id=None):
    categorias = Categoria.objects.filter(producto__activo=True).distinct().order_by("nombre")
    categoria = None
    productos = Producto.objects.none()

    if categoria_id:
        categoria = get_object_or_404(Categoria, pk=categoria_id)
        productos = Producto.objects.filter(activo=True, categoria=categoria).order_by("nombre")

    context = {
        "categorias": categorias,
        "categoria": categoria,
        "productos": productos,
    }
    return render(request, "productos/lista.html", context)


@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    # también incluir selecciones en la sesión (carrito)
    session_cart = request.session.get('cart', {})
    session_items = []
    session_total = Decimal('0.00')
    for pid, qty in session_cart.items():
        try:
            producto = Producto.objects.get(pk=pid)
        except Producto.DoesNotExist:
            continue
        subtotal = producto.precio * int(qty)
        session_total += subtotal
        session_items.append({
            'producto': producto,
            'cantidad': qty,
            'subtotal': subtotal,
        })
    return render(request, "pedidos/mis_pedidos.html", {"pedidos": pedidos, "session_items": session_items, "session_total": session_total})


@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    detalles = DetallePedido.objects.filter(pedido=pedido)
    return render(request, "pedidos/detalle.html", {"pedido": pedido, "detalles": detalles})


@login_required
def delete_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
    if request.method == 'POST':
        detalles = DetallePedido.objects.filter(pedido=pedido)
        for detalle in detalles:
            producto = detalle.producto
            producto.stock += detalle.cantidad
            producto.save()
        pedido.delete()
        return redirect('mis_pedidos')
    return redirect('detalle_pedido', pedido_id=pedido_id)


@login_required
def carrito(request):
    # Usar carrito en sesión: {'product_id': cantidad}
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')
    for pid, qty in cart.items():
        try:
            producto = Producto.objects.get(pk=pid)
        except Producto.DoesNotExist:
            continue
        subtotal = producto.precio * int(qty)
        total += subtotal
        cart_items.append({
            'producto': producto,
            'cantidad': qty,
            'subtotal': subtotal,
        })
    return render(request, "pedidos/carrito.html", {"cart_items": cart_items, "cart_total": total})


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=product_id, activo=True)
        cart = request.session.get('cart', {})
        cart[str(product_id)] = int(cart.get(str(product_id), 0)) + 1
        request.session['cart'] = cart
        request.session.modified = True
        return redirect('carrito')
    return redirect('lista_productos')


@login_required
def reporte_matriculas(request):
    # Filtros
    nombre = request.GET.get('nombre', '').strip()
    curso = request.GET.get('curso', '').strip()
    fecha = request.GET.get('fecha', '').strip()
    estado = request.GET.get('estado', '').strip()
    metodo = request.GET.get('metodo', '').strip()

    pedidos = Pedido.objects.all().select_related('usuario').prefetch_related('productos')

    if nombre:
        pedidos = pedidos.filter(estudiante_nombre__icontains=nombre)
    if curso:
        pedidos = pedidos.filter(productos__nombre__icontains=curso)
    if fecha:
        try:
            fecha_obj = date.fromisoformat(fecha)
            pedidos = pedidos.filter(fecha__date=fecha_obj)
        except ValueError:
            pass
    if estado:
        pedidos = pedidos.filter(estado_pago=estado)
    if metodo:
        pedidos = pedidos.filter(metodo_pago=metodo)

    pedidos = pedidos.distinct()

    hoy = timezone.localdate()
    primer_dia_mes = hoy.replace(day=1)
    total_estudiantes = Pedido.objects.exclude(estudiante_nombre__isnull=True).exclude(estudiante_nombre__exact='').count()
    total_dia = pedidos.filter(fecha__date=hoy).count()
    total_mes = pedidos.filter(fecha__date__gte=primer_dia_mes).count()
    total_ingresos = pedidos.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    cursos_activos = Producto.objects.filter(activo=True).count()
    vacantes = Producto.objects.filter(activo=True).aggregate(total_vacantes=Sum('stock'))['total_vacantes'] or 0
    vacantes_por_curso = list(Producto.objects.filter(activo=True).values('nombre', 'stock').order_by('-stock'))

    detail = DetallePedido.objects.filter(pedido__in=pedidos)
    matriculas_por_curso = list(detail.values(producto_nombre=F('producto__nombre')).annotate(count=Count('id')).order_by('-count'))
    ingresos_por_curso = list(detail.values(producto_nombre=F('producto__nombre')).annotate(ingresos=Sum(F('cantidad') * F('producto__precio'))).order_by('-ingresos'))

    pedidos_list = pedidos.order_by('fecha')
    daily = {}
    weekly = {}
    monthly = {}
    for pedido in pedidos_list:
        dia = pedido.fecha.date().isoformat()
        daily[dia] = daily.get(dia, 0) + 1
        week_label = f"{pedido.fecha.isocalendar()[0]}-S{pedido.fecha.isocalendar()[1]}"
        weekly[week_label] = weekly.get(week_label, 0) + 1
        month_label = pedido.fecha.strftime('%Y-%m')
        monthly[month_label] = monthly.get(month_label, 0) + 1

    matriculas_por_dia = [{'periodo': k, 'count': v} for k, v in sorted(daily.items())]
    matriculas_por_semana = [{'periodo': k, 'count': v} for k, v in sorted(weekly.items())]
    matriculas_por_mes = [{'periodo': k, 'count': v} for k, v in sorted(monthly.items())]

    context = {
        'pedidos': pedidos,
        'nombre': nombre,
        'curso': curso,
        'fecha': fecha,
        'estado': estado,
        'metodo': metodo,
        'total_estudiantes': total_estudiantes,
        'total_dia': total_dia,
        'total_mes': total_mes,
        'total_ingresos': total_ingresos,
        'cursos_activos': cursos_activos,
        'vacantes': vacantes,
        'vacantes_por_curso': vacantes_por_curso,
        'matriculas_por_curso': matriculas_por_curso,
        'ingresos_por_curso': ingresos_por_curso,
        'matriculas_por_dia': matriculas_por_dia,
        'matriculas_por_semana': matriculas_por_semana,
        'matriculas_por_mes': matriculas_por_mes,
    }

    if request.GET.get('export') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Nombre', 'Documento', 'Curso', 'Fecha', 'Monto', 'Método', 'Estado', 'Usuario'])
        for pedido in pedidos:
            cursos_nombres = ", ".join([p.nombre for p in pedido.productos.all()])
            writer.writerow([
                pedido.estudiante_nombre or '',
                pedido.documento or '',
                cursos_nombres,
                pedido.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                pedido.total,
                pedido.get_metodo_pago_display(),
                pedido.get_estado_pago_display(),
                pedido.usuario.username,
            ])
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_matriculas.csv"'
        return response

    return render(request, "pedidos/reporte_matriculas.html", context)


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def select_course(request, product_id):
    producto = get_object_or_404(Producto, pk=product_id, activo=True)
    errors = []
    form_data = {
        'nombre': '',
        'documento': '',
        'telefono': '',
        'email': '',
        'cantidad': 1,
    }
    if request.method == 'POST':
        form_data['nombre'] = request.POST.get('nombre', '').strip()
        form_data['documento'] = request.POST.get('documento', '').strip()
        form_data['telefono'] = request.POST.get('telefono', '').strip()
        form_data['email'] = request.POST.get('email', '').strip()
        form_data['cantidad'] = int(request.POST.get('cantidad', 1))

        if not form_data['nombre']:
            errors.append('Nombre completo es obligatorio.')
        if not form_data['documento']:
            errors.append('Documento es obligatorio.')
        if not form_data['telefono']:
            errors.append('Teléfono es obligatorio.')
        if not form_data['email']:
            errors.append('Email es obligatorio.')
        if form_data['cantidad'] < 1:
            errors.append('La cantidad debe ser al menos 1.')
        if form_data['cantidad'] > producto.stock:
            errors.append('No hay suficientes vacantes disponibles para este curso.')

        if not errors:
            request.session['pending_enrollment'] = {
                'product_id': product_id,
                'nombre': form_data['nombre'],
                'documento': form_data['documento'],
                'telefono': form_data['telefono'],
                'email': form_data['email'],
                'cantidad': form_data['cantidad'],
            }
            request.session.modified = True
            return redirect('payment')

    return render(request, 'pedidos/select_course.html', {'producto': producto, 'errors': errors, 'form_data': form_data})


@login_required
def payment(request):
    # Mostrar datos guardados y pedir datos de pago
    pending = request.session.get('pending_enrollment')
    if not pending:
        return redirect('lista_productos')
    producto = get_object_or_404(Producto, pk=pending['product_id'])
    cantidad = int(pending.get('cantidad', 1))
    amount = producto.precio * cantidad
    errors = []
    form_data = {
        'method': 'efectivo',
        'reference': '',
    }
    if request.method == 'POST':
        form_data['method'] = request.POST.get('method', 'transferencia')
        form_data['reference'] = request.POST.get('reference', '').strip()

        if form_data['method'] != 'efectivo' and not form_data['reference']:
            errors.append('Por favor ingrese la referencia de la transacción para el método de pago seleccionado.')

        if not errors:
            payment_info = {
                'method': form_data['method'],
                'reference': form_data['reference'],
            }
            request.session['pending_payment'] = payment_info
            request.session.modified = True
            return redirect('confirm_enrollment')

    return render(request, 'pedidos/payment.html', {'producto': producto, 'cantidad': cantidad, 'amount': amount, 'errors': errors, 'form_data': form_data})


@login_required
def confirm_enrollment(request):
    pending = request.session.get('pending_enrollment')
    payment = request.session.get('pending_payment')
    if not pending or not payment:
        return redirect('lista_productos')
    producto = get_object_or_404(Producto, pk=pending['product_id'])
    cantidad = int(pending.get('cantidad', 1))
    total = producto.precio * cantidad

    metodo_pago = payment.get('method', 'transferencia')
    referencia_pago = payment.get('reference', '')
    estado_pago = 'pagado' if metodo_pago == 'efectivo' or referencia_pago else 'pendiente'

    pedido = Pedido.objects.create(
        usuario=request.user,
        estudiante_nombre=pending.get('nombre', ''),
        documento=pending.get('documento', ''),
        telefono=pending.get('telefono', ''),
        email=pending.get('email', ''),
        total=total,
        metodo_pago=metodo_pago,
        referencia_pago=referencia_pago,
        estado_pago=estado_pago,
    )
    DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
    
    # Disminuir el stock del producto
    producto.stock -= cantidad
    producto.save()

    request.session.pop('pending_enrollment', None)
    request.session.pop('pending_payment', None)
    request.session.pop('cart', None)
    request.session.modified = True

    return redirect('mis_pedidos')
