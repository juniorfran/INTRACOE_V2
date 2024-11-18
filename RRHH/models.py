from django.db import models

class Departamentos (models.Model):
    nombre_departamento = models.CharField(max_length=50)
    def __str__(self):
        return self.nombre_departamento


class Cargo (models.Model):
    departamento  = models.ForeignKey(Departamentos, on_delete=models.CASCADE)
    nombre_cargo = models.CharField(max_length=50)
    #funcion str
    def __str__(self):
        return self.nombre_cargo

# Create your models here.
class Empleados (models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    dui = models.CharField(max_length=10)
    codigo_empleado = models.CharField(max_length=10)
    edad = models.IntegerField()
    salario = models.IntegerField()
    cargo = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    num_telefono = models.CharField(max_length=10)
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
    def __str__(self):
        return self.nombre + " " + self.apellido

    

class Boleta_pago (models.Model):
    fecha_pago = models.DateField()
    fecha_inicio = models.DateField()
    fecha_fin  = models.DateField()
    dias_laborados  = models.IntegerField()
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE)
    descuento_afp = models.IntegerField()
    descuento_isss = models.IntegerField()
    descuento_renta = models.IntegerField()
    otro_descuento1 = models.IntegerField()
    otro_descuento2 = models.IntegerField()
    total_descuentos = models.IntegerField()
    hr_extra_di = models.IntegerField()
    hr_extra_noc  = models.IntegerField()
    hr_extra_fer  = models.IntegerField()
    hr_extra_fer_noc  = models.IntegerField()
    total_pago = models.IntegerField()
    liquido_recibir = models.IntegerField()

    class Meta:
        verbose_name = "Boleta de pago"
        verbose_name_plural = "Boletas de pago"

    def __str__(self):
        return self.fecha_pago


