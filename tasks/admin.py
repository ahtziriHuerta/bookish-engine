from django.contrib import admin
from .models import Task, Rol, Usuario, Credencial, Proveedor, Producto, Venta, DetalleVenta, DatosPersonales
from .models import PinGerente

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", )
# Register your models here.
admin.site.register(Task, TaskAdmin)

admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(Credencial)
admin.site.register(Proveedor)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(DatosPersonales)

admin.site.register(PinGerente)

