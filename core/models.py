from django.db import models

# Create your models here.

class ConfiguracionEcoparque(models.Model):
    nombre = models.CharField(max_length=150)
    lema = models.CharField(max_length=200, blank=True)
    descripcion = models.TextField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    horario = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.nombre
