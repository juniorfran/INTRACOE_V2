from django.contrib import admin
from .models import Quedan, facturas_quedan, Proveedor, quedan_pago_state
# Register your models here.

#registrar en el admin quedan
admin.site.register(Quedan)
class QuedanAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'numero_quedan', 'fecha_alta')

admin.site.register(facturas_quedan)
class facturas_quedanAdmin(admin.ModelAdmin):
    list_display = ('id', 'proveedor', 'quedan', 'num_doc')

