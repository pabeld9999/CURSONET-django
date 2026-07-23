from django.urls import path
from . import views

urlpatterns = [
    path("inicio/", views.inicio, name="inicio"),
    path("productos/", views.lista_productos, name="lista_productos"),
    path("productos/categoria/<int:categoria_id>/", views.lista_productos, name="lista_productos_categoria"),
    path("carrito/", views.carrito, name="carrito"),
    path("reporte-matriculas/", views.reporte_matriculas, name="reporte_matriculas"),
    path("carrito/agregar/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("seleccionar/<int:product_id>/", views.select_course, name="select_course"),
    path("pago/", views.payment, name="payment"),
    path("confirmar/", views.confirm_enrollment, name="confirm_enrollment"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("pedido/<int:pedido_id>/", views.detalle_pedido, name="detalle_pedido"),
    path("pedido/<int:pedido_id>/eliminar/", views.delete_pedido, name="delete_pedido"),
]
