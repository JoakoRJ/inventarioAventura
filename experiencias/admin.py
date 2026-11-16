from django.contrib import admin
from experiencias.models import Categoria, Experiencia, Inscripcion

# Register your models here.

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')


class ExperienciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'creador', 'precio', 'cupo_maximo', 'fecha_hora', 'activa')


class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'experiencia', 'fecha_inscripcion', 'estado_pago')


admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Experiencia, ExperienciaAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)
