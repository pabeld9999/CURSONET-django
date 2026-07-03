from django.contrib import admin

# Register your models here.
# Importamos nuestros modelos
from .models import Producto, Pedido
from .models import DetallePedido, Categoria

# Registramos los modelos para que aparezcan en el panel admin
admin.site.register(Producto)
admin.site.register(Pedido)

admin.site.register(DetallePedido)
admin.site.register(Categoria)
