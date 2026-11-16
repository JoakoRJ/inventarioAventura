import calendar
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from cuentas.decoradores import rol_requerido, obtener_rol
from experiencias.models import Categoria, Experiencia, Inscripcion
from experiencias.forms import (CategoriaForm, ExperienciaForm, ExperienciaAdminForm,
                                ReservaForm, ReservaAdminForm, VisitanteForm)

# Create your views here.

def experiencias_del_usuario(request):
    if obtener_rol(request) == 'admin':
        return Experiencia.objects.all()
    return Experiencia.objects.filter(creador=request.user)


def inscribir(usuario, experiencia):
    if Inscripcion.objects.filter(usuario=usuario, experiencia=experiencia).exists():
        return 'Ya estás inscrito en esta experiencia.'
    if experiencia.ya_ocurrio:
        return 'Esta experiencia ya se realizó.'
    if experiencia.esta_llena:
        return 'No quedan cupos disponibles.'
    Inscripcion.objects.create(usuario=usuario, experiencia=experiencia)
    return None


@rol_requerido('admin')
def categoria_lista(request):
    categorias = Categoria.objects.annotate(num_experiencias=Count('experiencias'))
    data = {'categorias': categorias}
    return render(request, 'experiencias/categoria_lista.html', data)


@rol_requerido('admin')
def categoria_registro(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('categoria_lista'))
    else:
        form = CategoriaForm(initial={'activo': True})
    data = {'form': form, 'titulo': 'Nueva categoría', 'volver': 'categoria_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def categoria_editar(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('categoria_lista'))
    else:
        form = CategoriaForm(instance=categoria)
    data = {'form': form, 'titulo': 'Editar categoría', 'volver': 'categoria_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def categoria_eliminar(request, id):
    categoria = get_object_or_404(Categoria, id=id)
    if request.method == 'POST':
        try:
            categoria.delete()
        except ProtectedError:
            messages.error(request, 'No se puede eliminar una categoría que tiene experiencias. Márcala como inactiva.')
    return HttpResponseRedirect(reverse('categoria_lista'))


@rol_requerido('admin', 'guia')
def experiencia_lista(request):
    experiencias = experiencias_del_usuario(request)
    data = {'experiencias': experiencias}
    return render(request, 'experiencias/experiencia_lista.html', data)


@rol_requerido('admin', 'guia')
def experiencia_registro(request):
    rol = obtener_rol(request)
    FormClase = ExperienciaAdminForm if rol == 'admin' else ExperienciaForm
    if request.method == 'POST':
        form = FormClase(request.POST)
        if form.is_valid():
            experiencia = form.save(commit=False)
            if rol != 'admin':
                experiencia.creador = request.user
            experiencia.save()
            return HttpResponseRedirect(reverse('experiencia_lista'))
    else:
        form = FormClase(initial={'activa': True, 'creador': request.user})
    data = {'form': form, 'titulo': 'Nueva experiencia', 'volver': 'experiencia_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin', 'guia')
def experiencia_editar(request, id):
    experiencia = get_object_or_404(experiencias_del_usuario(request), id=id)
    FormClase = ExperienciaAdminForm if obtener_rol(request) == 'admin' else ExperienciaForm
    if request.method == 'POST':
        form = FormClase(request.POST, instance=experiencia)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('experiencia_lista'))
    else:
        form = FormClase(instance=experiencia)
    data = {'form': form, 'titulo': 'Editar experiencia', 'volver': 'experiencia_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def experiencia_eliminar(request, id):
    experiencia = get_object_or_404(Experiencia, id=id)
    if request.method == 'POST':
        experiencia.delete()
    return HttpResponseRedirect(reverse('experiencia_lista'))


@rol_requerido('admin', 'guia')
def experiencia_estado(request, id):
    experiencia = get_object_or_404(experiencias_del_usuario(request), id=id)
    if request.method == 'POST':
        experiencia.activa = not experiencia.activa
        experiencia.save()
    destino = request.POST.get('volver')
    if destino == 'grupo':
        return HttpResponseRedirect(reverse('grupo_detalle', args=[experiencia.id]))
    return HttpResponseRedirect(reverse('experiencia_lista'))


@rol_requerido('admin', 'guia')
def grupo_detalle(request, id):
    experiencia = get_object_or_404(experiencias_del_usuario(request), id=id)
    inscripciones = experiencia.inscripciones.select_related('usuario')
    form = VisitanteForm(experiencia=experiencia)
    data = {'experiencia': experiencia, 'inscripciones': inscripciones, 'form': form}
    return render(request, 'experiencias/grupo_detalle.html', data)


@rol_requerido('admin', 'guia')
def visitante_registro(request, id):
    experiencia = get_object_or_404(experiencias_del_usuario(request), id=id)
    if request.method == 'POST':
        form = VisitanteForm(request.POST, experiencia=experiencia)
        if form.is_valid():
            error = inscribir(form.cleaned_data['turista'], experiencia)
            if error:
                messages.error(request, error)
            else:
                messages.success(request, 'Visitante registrado en el grupo.')
        else:
            messages.error(request, 'Selecciona un turista válido.')
    return HttpResponseRedirect(reverse('grupo_detalle', args=[experiencia.id]))


@rol_requerido('admin', 'guia')
def calendario(request):
    hoy = timezone.localdate()
    try:
        anio = int(request.GET.get('anio', hoy.year))
        mes = int(request.GET.get('mes', hoy.month))
        if mes < 1 or mes > 12 or anio < 2000 or anio > 2100:
            raise ValueError
    except ValueError:
        anio = hoy.year
        mes = hoy.month
    inicio = timezone.make_aware(datetime(anio, mes, 1))
    if mes == 12:
        fin = timezone.make_aware(datetime(anio + 1, 1, 1))
    else:
        fin = timezone.make_aware(datetime(anio, mes + 1, 1))
    experiencias = experiencias_del_usuario(request).filter(
        fecha_hora__gte=inicio, fecha_hora__lt=fin
    ).order_by('fecha_hora')
    por_dia = {}
    for e in experiencias:
        dia = timezone.localtime(e.fecha_hora).day
        por_dia.setdefault(dia, []).append(e)
    semanas = []
    for semana in calendar.monthcalendar(anio, mes):
        semanas.append([{'dia': d, 'experiencias': por_dia.get(d, [])} for d in semana])
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto',
             'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    if mes == 1:
        anterior = {'anio': anio - 1, 'mes': 12}
    else:
        anterior = {'anio': anio, 'mes': mes - 1}
    if mes == 12:
        siguiente = {'anio': anio + 1, 'mes': 1}
    else:
        siguiente = {'anio': anio, 'mes': mes + 1}
    data = {
        'semanas': semanas,
        'titulo_mes': meses[mes - 1] + ' ' + str(anio),
        'anterior': anterior,
        'siguiente': siguiente,
        'hoy': hoy if (hoy.year == anio and hoy.month == mes) else None,
    }
    return render(request, 'experiencias/calendario.html', data)


@rol_requerido('admin')
def reserva_lista(request):
    reservas = Inscripcion.objects.select_related('usuario', 'experiencia', 'experiencia__categoria')
    data = {'reservas': reservas}
    return render(request, 'experiencias/reserva_lista.html', data)


@rol_requerido('admin')
def reserva_registro(request):
    if request.method == 'POST':
        form = ReservaAdminForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva creada correctamente.')
            return HttpResponseRedirect(reverse('reserva_lista'))
    else:
        form = ReservaAdminForm()
    data = {'form': form, 'titulo': 'Nueva reserva', 'volver': 'reserva_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def reserva_editar(request, id):
    reserva = get_object_or_404(Inscripcion, id=id)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('reserva_lista'))
    else:
        form = ReservaForm(instance=reserva)
    data = {'form': form, 'titulo': 'Editar reserva', 'volver': 'reserva_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def reserva_eliminar(request, id):
    reserva = get_object_or_404(Inscripcion, id=id)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva eliminada correctamente.')
    return HttpResponseRedirect(reverse('reserva_lista'))


@rol_requerido('admin')
def reportes(request):
    filas = []
    total_confirmado = 0
    total_pendiente = 0
    total_inscritos = 0
    for e in Experiencia.objects.select_related('categoria', 'creador'):
        confirmados = e.inscripciones.filter(estado_pago='confirmado').count()
        pendientes = e.inscripciones.filter(estado_pago='pendiente').count()
        filas.append({
            'experiencia': e,
            'confirmados': confirmados,
            'pendientes': pendientes,
            'ingreso': e.precio * confirmados,
        })
        total_confirmado += e.precio * confirmados
        total_pendiente += e.precio * pendientes
        total_inscritos += confirmados + pendientes
    data = {
        'filas': filas,
        'total_confirmado': total_confirmado,
        'total_pendiente': total_pendiente,
        'total_inscritos': total_inscritos,
    }
    return render(request, 'experiencias/reportes.html', data)


@rol_requerido('turista')
def catalogo(request):
    if 'categoria' in request.GET:
        valor = request.GET['categoria']
        if valor.isdigit():
            request.session['categoria'] = int(valor)
        else:
            request.session.pop('categoria', None)
    experiencias = Experiencia.objects.filter(activa=True, categoria__activo=True).select_related('categoria', 'creador')
    categoria_id = request.session.get('categoria')
    if categoria_id:
        experiencias = experiencias.filter(categoria_id=categoria_id)
    vistas = request.session.get('vistas', [])
    recientes = []
    for id in vistas:
        e = Experiencia.objects.filter(id=id, activa=True).first()
        if e:
            recientes.append(e)
    reservadas = list(Inscripcion.objects.filter(usuario=request.user).values_list('experiencia_id', flat=True))
    data = {
        'experiencias': experiencias,
        'categorias': Categoria.objects.filter(activo=True),
        'categoria_id': categoria_id,
        'recientes': recientes,
        'reservadas': reservadas,
    }
    return render(request, 'experiencias/catalogo.html', data)


@rol_requerido('turista')
def ruta_detalle(request, id):
    experiencia = get_object_or_404(Experiencia, id=id, activa=True, categoria__activo=True)
    vistas = request.session.get('vistas', [])
    if experiencia.id in vistas:
        vistas.remove(experiencia.id)
    vistas.insert(0, experiencia.id)
    request.session['vistas'] = vistas[:5]
    reserva = Inscripcion.objects.filter(usuario=request.user, experiencia=experiencia).first()
    data = {'experiencia': experiencia, 'reserva': reserva}
    return render(request, 'experiencias/ruta_detalle.html', data)


@rol_requerido('turista')
def reserva_nueva(request, id):
    experiencia = get_object_or_404(Experiencia, id=id, activa=True, categoria__activo=True)
    if request.method == 'POST':
        error = inscribir(request.user, experiencia)
        if error:
            messages.error(request, error)
            return HttpResponseRedirect(reverse('ruta_detalle', args=[experiencia.id]))
        messages.success(request, 'Reserva realizada. Quedó en estado Pendiente.')
        return HttpResponseRedirect(reverse('mis_reservas'))
    reserva = Inscripcion.objects.filter(usuario=request.user, experiencia=experiencia).first()
    data = {'experiencia': experiencia, 'reserva': reserva}
    return render(request, 'experiencias/reserva_nueva.html', data)


@rol_requerido('turista')
def mis_reservas(request):
    reservas = Inscripcion.objects.filter(usuario=request.user).select_related('experiencia', 'experiencia__categoria')
    data = {'reservas': reservas}
    return render(request, 'experiencias/mis_reservas.html', data)


@rol_requerido('turista')
def reserva_detalle(request, id):
    reserva = get_object_or_404(Inscripcion, id=id, usuario=request.user)
    data = {'reserva': reserva}
    return render(request, 'experiencias/reserva_detalle.html', data)


@rol_requerido('turista')
def reserva_cancelar(request, id):
    reserva = get_object_or_404(Inscripcion, id=id, usuario=request.user, estado_pago='pendiente')
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva cancelada correctamente.')
    return HttpResponseRedirect(reverse('mis_reservas'))
