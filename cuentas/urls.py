from django.urls import path
from cuentas.views import (registro, redireccion, mi_perfil, usuario_lista, usuario_registro,
                           usuario_editar, usuario_eliminar, guia_lista)

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('redireccion/', redireccion, name='redireccion'),
    path('perfil/', mi_perfil, name='perfil'),
    path('usuarios/', usuario_lista, name='usuario_lista'),
    path('usuarios/nuevo/', usuario_registro, name='usuario_registro'),
    path('usuarios/editar/<int:id>/', usuario_editar, name='usuario_editar'),
    path('usuarios/eliminar/<int:id>/', usuario_eliminar, name='usuario_eliminar'),
    path('guias/', guia_lista, name='guia_lista'),
]
