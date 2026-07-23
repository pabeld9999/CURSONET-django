from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# Importamos el modelo de usuario de Django
from django.contrib.auth.models import User


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

# Create your models here.
# Modelo que representa los productos de la cafetería
class Producto(models.Model):
    # ... (deja tus campos actuales aquí) ...

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    # Nombre del producto (texto corto)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")

    # Precio con 2 decimales (ej: 5.50)
    precio = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Precio")

    # Cantidad disponible en inventario
    stock = models.IntegerField(verbose_name="Vacantes")

    # Indica si el producto está disponible para venta
    activo = models.BooleanField(default=True, verbose_name="Activo")

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, verbose_name="Categoría")

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

    # Datos del estudiante
    estudiante_nombre = models.CharField(max_length=150, blank=True, null=True)
    documento = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    # Relación muchos a muchos:
    # Un pedido puede contener varios productos
    productos = models.ManyToManyField(Producto, through="DetallePedido")

    # Fecha en que se creó el pedido (automática)
    fecha = models.DateTimeField(auto_now_add=True)

    # Total del pedido
    total = models.DecimalField(max_digits=8, decimal_places=2)

    # Métodos y estado de pago
    METODO_CHOICES = [
        ("efectivo", "Efectivo"),
        ("yape", "Yape"),
        ("plin", "Plin"),
        ("transferencia", "Transferencia"),
        ("tarjeta", "Tarjeta"),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES, default="transferencia")
    referencia_pago = models.CharField(max_length=120, blank=True, null=True)
    ESTADO_PAGO_CHOICES = [
        ("pagado", "Pagado"),
        ("pendiente", "Pendiente"),
    ]
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default="pagado")

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.username}"


class DetallePedido(models.Model):
    class Meta:
        verbose_name = "Detalle Matrícula"
        verbose_name_plural = "Detalle Matrículas"

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


@receiver(pre_delete, sender=DetallePedido)
def restore_stock_on_detalle_delete(sender, instance, **kwargs):
    producto = instance.producto
    producto.stock += instance.cantidad
    producto.save()
