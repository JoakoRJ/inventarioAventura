from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from core.models import ConfiguracionEcoparque
from core.forms import ConfiguracionForm
from cuentas.models import Perfil
from cuentas.decoradores import rol_requerido
from experiencias.models import Categoria, Experiencia, Inscripcion

# Create your views here.

def obtener_configuracion():
    config = ConfiguracionEcoparque.objects.first()
    if config is None:
        config = ConfiguracionEcoparque.objects.create(
            nombre='Ecoparque y Reserva Natural "Aventuras del Sur"',
            lema='Naturaleza, aventura y descubrimiento',
            descripcion='Trekking, canopy, kayak y arriendo de equipos con guías expertos.'
        )
    return config


def inicio(request):
    destacadas = Experiencia.objects.filter(
        activa=True, categoria__activo=True, fecha_hora__gte=timezone.now()
    ).select_related('categoria').order_by('fecha_hora')[:6]
    data = {
        'config': obtener_configuracion(),
        'destacadas': destacadas,
        'categorias': Categoria.objects.filter(activo=True),
    }
    return render(request, 'core/inicio.html', data)


@rol_requerido('admin')
def panel_control(request):
    ingresos = Inscripcion.objects.filter(estado_pago='confirmado').aggregate(total=Sum('experiencia__precio'))
    data = {
        'total_usuarios': User.objects.count(),
        'total_guias': Perfil.objects.filter(rol='guia').count(),
        'total_turistas': Perfil.objects.filter(rol='turista').count(),
        'total_categorias': Categoria.objects.filter(activo=True).count(),
        'total_experiencias': Experiencia.objects.filter(activa=True).count(),
        'total_reservas': Inscripcion.objects.count(),
        'reservas_pendientes': Inscripcion.objects.filter(estado_pago='pendiente').count(),
        'reservas_confirmadas': Inscripcion.objects.filter(estado_pago='confirmado').count(),
        'ingresos': ingresos['total'] or 0,
        'ultimas': Inscripcion.objects.select_related('usuario', 'experiencia')[:5],
    }
    return render(request, 'core/panel_control.html', data)


@rol_requerido('admin')
def configuracion(request):
    config = obtener_configuracion()
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente.')
            return HttpResponseRedirect(reverse('configuracion'))
    else:
        form = ConfiguracionForm(instance=config)
    data = {'form': form, 'titulo': 'Configuración del Ecoparque', 'volver': 'panel_control'}
    return render(request, 'form.html', data)
