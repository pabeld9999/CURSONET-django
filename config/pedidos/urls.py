from django.urls import path
from . import views

urlpatterns = [
    path("productos/", views.lista_productos),
    path("mis-pedidos/", views.mis_pedidos),
    path("pedido/<int:pedido_id>/", views.detalle_pedido),
]
