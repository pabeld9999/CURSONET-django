from django.db import models

# Importamos el modelo de usuario de Django
from django.contrib.auth.models import User


class Categoria(models.Model):
    # ... (deja tus campos actuales aquí, no los borres) ...

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


# Create your models here.
# Modelo que representa los productos de la cafetería
class Producto(models.Model):
    # ... (deja tus campos actuales aquí) ...

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    # Nombre del producto (texto corto)
    nombre = models.CharField(max_length=100)

    # Precio con 2 decimales (ej: 5.50)
    precio = models.DecimalField(max_digits=6, decimal_places=2)

    # Cantidad disponible en inventario
    stock = models.IntegerField()

    # Indica si el producto está disponible para venta
    activo = models.BooleanField(default=True)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)

    # Representación en texto del objeto (usado en admin)
    def __str__(self):
        return self.nombre


# Modelo que representa un pedido realizado por un usuario
class Pedido(models.Model):  # O como se llame tu clase de pedidos
    # ... (deja tus campos actuales aquí) ...

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"

    # Relación muchos a uno:
    # Muchos pedidos pueden pertenecer a un usuario
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    # Relación muchos a muchos:
    # Un pedido puede contener varios productos
    productos = models.ManyToManyField(Producto, through="DetallePedido")

    # Fecha en que se creó el pedido (automática)
    fecha = models.DateTimeField(auto_now_add=True)

    # Total del pedido
    total = models.DecimalField(max_digits=8, decimal_places=2)

    # Representación en texto
    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.username}"


class DetallePedido(models.Model):  # O como se llame tu clase de detalle
    # ... (deja tus campos actuales aquí) ...

    class Meta:
        verbose_name = "Detalle Matrícula"
        verbose_name_plural = "Detalle Matrículas"
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
