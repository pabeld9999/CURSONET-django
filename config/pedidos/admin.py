from django.contrib import admin

# Register your models here.
# Importamos nuestros modelos
from .models import Producto, Pedido
from .models import DetallePedido, Categoria


class PedidoAdmin(admin.ModelAdmin):
    search_fields = ['documento', 'estudiante_nombre', 'email', 'telefono']
    list_display = ['id', 'estudiante_nombre', 'documento', 'fecha', 'total', 'estado_pago']
    list_filter = ['estado_pago', 'metodo_pago', 'fecha']


# Registramos los modelos para que aparezcan en el panel admin
admin.site.register(Producto)
admin.site.register(Pedido, PedidoAdmin)

admin.site.register(DetallePedido)
admin.site.register(Categoria)
