from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from cuentas.models import Perfil


def obtener_rol(request):
    rol = request.session.get('rol')
    if rol is None:
        if request.user.is_superuser:
            rol = 'admin'
        else:
            perfil = Perfil.objects.filter(usuario=request.user).first()
            rol = perfil.rol if perfil else 'turista'
        request.session['rol'] = rol
    return rol


def rol_requerido(*roles):
    def decorador(vista):
        @login_required
        def revisar(request, *args, **kwargs):
            if obtener_rol(request) not in roles:
                raise PermissionDenied
            return vista(request, *args, **kwargs)
        return revisar
    return decorador
