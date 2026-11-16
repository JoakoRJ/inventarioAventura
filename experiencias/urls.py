from django.urls import path
from experiencias.views import (categoria_lista, categoria_registro, categoria_editar, categoria_eliminar,
                                experiencia_lista, experiencia_registro, experiencia_editar,
                                experiencia_eliminar, experiencia_estado, grupo_detalle, visitante_registro,
                                calendario, reserva_lista, reserva_registro, reserva_editar, reserva_eliminar, reportes, catalogo, ruta_detalle,
                                reserva_nueva, mis_reservas, reserva_detalle, reserva_cancelar)

urlpatterns = [
    path('categorias/', categoria_lista, name='categoria_lista'),
    path('categorias/nueva/', categoria_registro, name='categoria_registro'),
    path('categorias/editar/<int:id>/', categoria_editar, name='categoria_editar'),
    path('categorias/eliminar/<int:id>/', categoria_eliminar, name='categoria_eliminar'),

    path('experiencias/', experiencia_lista, name='experiencia_lista'),
    path('experiencias/nueva/', experiencia_registro, name='experiencia_registro'),
    path('experiencias/editar/<int:id>/', experiencia_editar, name='experiencia_editar'),
    path('experiencias/eliminar/<int:id>/', experiencia_eliminar, name='experiencia_eliminar'),
    path('experiencias/estado/<int:id>/', experiencia_estado, name='experiencia_estado'),
    path('experiencias/grupo/<int:id>/', grupo_detalle, name='grupo_detalle'),
    path('experiencias/grupo/<int:id>/visitante/', visitante_registro, name='visitante_registro'),
    path('calendario/', calendario, name='calendario'),

    path('reservas/', reserva_lista, name='reserva_lista'),
    path('reservas/nueva/', reserva_registro, name='reserva_registro'),
    path('reservas/editar/<int:id>/', reserva_editar, name='reserva_editar'),
    path('reservas/eliminar/<int:id>/', reserva_eliminar, name='reserva_eliminar'),
    path('reportes/', reportes, name='reportes'),

    path('catalogo/', catalogo, name='catalogo'),
    path('catalogo/<int:id>/', ruta_detalle, name='ruta_detalle'),
    path('catalogo/<int:id>/reservar/', reserva_nueva, name='reserva_nueva'),
    path('mis-reservas/', mis_reservas, name='mis_reservas'),
    path('mis-reservas/<int:id>/', reserva_detalle, name='reserva_detalle'),
    path('mis-reservas/cancelar/<int:id>/', reserva_cancelar, name='reserva_cancelar'),
]
