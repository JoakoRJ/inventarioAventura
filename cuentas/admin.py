from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from cuentas.models import Perfil

# Register your models here.

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    min_num = 1
    max_num = 1
    extra = 0


class UsuarioAdmin(UserAdmin):
    inlines = [PerfilInline]


admin.site.unregister(User)
admin.site.register(User, UsuarioAdmin)
