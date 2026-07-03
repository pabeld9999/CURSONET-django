# Importa HttpResponse para devolver texto simple al navegador
# from django.http import HttpResponse

# (Opcional) render se usará más adelante para templates
from django.shortcuts import render
from .models import Producto, Pedido, DetallePedido
from django.contrib.auth.decorators import login_required


# Vista básica que responde a una solicitud HTTP
def inicio(request):
    # Retorna texto simple al navegador
    # return HttpResponse("Bienvenido al sistema de cafetería")
    return render(request, "inicio.html")


def lista_productos(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, "productos/lista.html", {"productos": productos})


@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, "pedidos/mis_pedidos.html", {"pedidos": pedidos})


@login_required
def detalle_pedido(request, pedido_id):
    detalles = DetallePedido.objects.filter(pedido_id=pedido_id)
    return render(request, "pedidos/detalle.html", {"detalles": detalles})
