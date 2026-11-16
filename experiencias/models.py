from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone

# Create your models here.

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Experiencia(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=0, validators=[MinValueValidator(0)])
    cupo_maximo = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    fecha_hora = models.DateTimeField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='experiencias')
    creador = models.ForeignKey(User, on_delete=models.PROTECT, related_name='experiencias_creadas')
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    @property
    def cupos_ocupados(self):
        return self.inscripciones.count()

    @property
    def cupos_disponibles(self):
        return max(self.cupo_maximo - self.cupos_ocupados, 0)

    @property
    def esta_llena(self):
        return self.cupos_ocupados >= self.cupo_maximo

    @property
    def ya_ocurrio(self):
        return self.fecha_hora < timezone.now()


class Inscripcion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    experiencia = models.ForeignKey(Experiencia, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(max_length=12, choices=ESTADOS, default='pendiente')

    class Meta:
        ordering = ['-fecha_inscripcion']
        unique_together = ['usuario', 'experiencia']

    def __str__(self):
        return self.usuario.username + ' - ' + self.experiencia.titulo
