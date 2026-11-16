from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.deletion import ProtectedError
from cuentas.models import Perfil
from cuentas.forms import RegistroForm, UsuarioForm, PerfilForm
from cuentas.decoradores import rol_requerido, obtener_rol

# Create your views here.

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            Perfil.objects.create(usuario=usuario, rol='turista')
            return HttpResponseRedirect(reverse('login'))
    else:
        form = RegistroForm()
    data = {'form': form}
    return render(request, 'registration/registro.html', data)


@login_required
def redireccion(request):
    request.session.pop('rol', None)
    rol = obtener_rol(request)
    if rol == 'admin':
        return HttpResponseRedirect(reverse('panel_control'))
    if rol == 'guia':
        return HttpResponseRedirect(reverse('perfil'))
    return HttpResponseRedirect(reverse('catalogo'))


@login_required
def mi_perfil(request):
    perfil, creado = Perfil.objects.get_or_create(usuario=request.user, defaults={'rol': obtener_rol(request)})
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            perfil.telefono = form.cleaned_data['telefono']
            perfil.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return HttpResponseRedirect(reverse('perfil'))
    else:
        form = PerfilForm(instance=request.user, initial={'telefono': perfil.telefono})
    data = {'form': form, 'perfil': perfil}
    return render(request, 'cuentas/perfil.html', data)


@rol_requerido('admin')
def usuario_lista(request):
    usuarios = User.objects.all().order_by('username')
    data = {'usuarios': usuarios}
    return render(request, 'cuentas/usuario_lista.html', data)


@rol_requerido('admin')
def usuario_registro(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['password']:
                form.add_error('password', 'La contraseña es obligatoria.')
            else:
                usuario = form.save(commit=False)
                usuario.set_password(form.cleaned_data['password'])
                usuario.save()
                Perfil.objects.update_or_create(
                    usuario=usuario,
                    defaults={'rol': form.cleaned_data['rol'], 'telefono': form.cleaned_data['telefono']}
                )
                messages.success(request, 'Usuario creado correctamente.')
                return HttpResponseRedirect(reverse('usuario_lista'))
    else:
        form = UsuarioForm(initial={'is_active': True})
    data = {'form': form, 'titulo': 'Nuevo usuario', 'volver': 'usuario_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def usuario_editar(request, id):
    usuario = get_object_or_404(User, id=id)
    perfil = Perfil.objects.filter(usuario=usuario).first()
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save(commit=False)
            if form.cleaned_data['password']:
                usuario.set_password(form.cleaned_data['password'])
            usuario.save()
            Perfil.objects.update_or_create(
                usuario=usuario,
                defaults={'rol': form.cleaned_data['rol'], 'telefono': form.cleaned_data['telefono']}
            )
            messages.success(request, 'Usuario actualizado correctamente.')
            return HttpResponseRedirect(reverse('usuario_lista'))
    else:
        inicial = {}
        if perfil:
            inicial = {'rol': perfil.rol, 'telefono': perfil.telefono}
        form = UsuarioForm(instance=usuario, initial=inicial)
    data = {'form': form, 'titulo': 'Editar usuario', 'volver': 'usuario_lista'}
    return render(request, 'form.html', data)


@rol_requerido('admin')
def usuario_eliminar(request, id):
    usuario = get_object_or_404(User, id=id)
    if request.method == 'POST':
        if usuario == request.user:
            messages.error(request, 'No puedes eliminar tu propia cuenta.')
        else:
            try:
                usuario.delete()
                messages.success(request, 'Usuario eliminado correctamente.')
            except ProtectedError:
                messages.error(request, 'No se puede eliminar un usuario que tiene experiencias registradas.')
    return HttpResponseRedirect(reverse('usuario_lista'))


@rol_requerido('admin')
def guia_lista(request):
    guias = User.objects.filter(perfil__rol='guia').annotate(
        num_experiencias=Count('experiencias_creadas', distinct=True),
        num_reservas=Count('experiencias_creadas__inscripciones', distinct=True),
    ).order_by('username')
    data = {'guias': guias}
    return render(request, 'cuentas/guia_lista.html', data)
