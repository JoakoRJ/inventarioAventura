from django.urls import path
from core.views import inicio, panel_control, configuracion

urlpatterns = [
    path('', inicio, name='inicio'),
    path('panel/', panel_control, name='panel_control'),
    path('configuracion/', configuracion, name='configuracion'),
]
