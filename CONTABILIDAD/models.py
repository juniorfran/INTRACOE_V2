from django.db import models

# Create your models here.

#Modelo para guardar informacion del clientes
class Proveedor(models.Model):
    nombre = models.CharField(max_length=250, null=True)
    apellido = models.CharField(max_length=250, null=True)
    nombre_empresa = models.CharField(max_length=250, null=True)
    nit = models.CharField(max_length=200, null=True)
    nrc = models.CharField(max_length=200, null=True)
    telefono_empresa = models.CharField(max_length=200, null=True)
    correo_empresa = models.EmailField(max_length=250, null=True)
    direccion_empresa = models.CharField(max_length=250, null=True)
    email = models.EmailField(max_length=250, null=True)
    telefono = models.CharField(max_length=200, null=True)
    direccion = models.CharField(max_length=250, null=True)
    fecha_alta = models.DateField(null=True, blank=True)
    fecha_baja = models.DateField(null=True, blank=True, default=None)
    estado = models.BooleanField(default=True)
    
    # Nuevos campos para reflejar otros datos
    codigo = models.CharField(max_length=250, null=True, blank=True)
    giro = models.CharField(max_length=250, null=True, blank=True)
    es_proveedor = models.BooleanField(default=False)
    contacto = models.CharField(max_length=250, null=True, blank=True)
    # Agregar más campos según sea necesario...

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    
#modelo para guardar la informacion del quedan
class Quedan(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    numero_quedan = models.CharField(max_length=20)
    fecha_entrega = models.DateField()
    comentario_quedan = models.CharField(max_length=100, null=True)
    cant_facturas = models.IntegerField()
    estado_enviado = models.BooleanField(default=False)
    ultima_fecha_pago = models.DateField()
    #creamos un campo para guardar la fecha de alta del quedan
    fecha_alta = models.DateField(auto_now_add=True)
    #creamos un campo para guardar la fecha de baja del quedan
    fecha_baja = models.DateField(null=True, blank=True, default=None)

    def __str__(self):
        return f'{self.numero_quedan} - {self.proveedor.nombre} {self.proveedor.apellido}'

#modelo para guardar los datos de las facturas de los quedan
class facturas_quedan(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    quedan = models.ForeignKey(Quedan, on_delete=models.CASCADE)
    tipo_doc = models.CharField(max_length=10)
    num_doc = models.CharField(max_length=150)
    fecha_doc = models.DateField()
    suma_efect = models.DecimalField(max_digits=25, decimal_places=2)
    porcentaje_ret_iva = models.DecimalField(max_digits=20, decimal_places=2)
    porcentaje_percep = models.DecimalField(max_digits=20, decimal_places=2)
    total_pagar = models.DecimalField(max_digits=25, decimal_places=2)
    porcentaje_iva = models.DecimalField(max_digits=20, decimal_places=2)

    def __str__(self):
        return f'{self.quedan.numero_quedan} - {self.proveedor.nombre}'


#modelo para guardar un estado de los pago de los quedan
class quedan_pago_state(models.Model):
    quedan = models.ForeignKey(Quedan, on_delete=models.CASCADE)
    estado_pago = models.BooleanField(default=True)
    fecha_pago = models.DateField()
    monto_pago = models.DecimalField(max_digits=10, decimal_places=2)
    #estado_pago = models.CharField(max_length=50, choices=ESTADOS_PAGO)

    def __str__(self):
        return f'{self.quedan.numero_quedan} - {self.estado_pago}'