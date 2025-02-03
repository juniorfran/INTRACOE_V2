from django.db import models

class DocumentoTributario(models.Model):
    numero_control = models.CharField(max_length=31, unique=True)
    codigo_generacion = models.CharField(max_length=36, unique=True)
    nit_emisor = models.CharField(max_length=14)
    nombre_emisor = models.CharField(max_length=250)
    total_pagar = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_emision = models.DateField()
    hora_emision = models.TimeField()
    receptor_nombre = models.CharField(max_length=250, null=True, blank=True)
    receptor_nit = models.CharField(max_length=14, null=True, blank=True)
    detalles = models.TextField()  # Detalles del cuerpo del DTE en formato JSON
    archivo_pdf = models.FileField(upload_to='documentos/pdf/', null=True, blank=True)
    archivo_json = models.FileField(upload_to='documentos/json/', null=True, blank=True)

    def __str__(self):
        return f"{self.numero_control} - {self.nombre_emisor}"
