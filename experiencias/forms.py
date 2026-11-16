from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from experiencias.models import Categoria, Experiencia, Inscripcion

FORMATO = '%Y-%m-%dT%H:%M'


def estilo(form):
    for campo in form.fields.values():
        if isinstance(campo.widget, forms.CheckboxInput):
            campo.widget.attrs['class'] = 'form-check-input'
        else:
            campo.widget.attrs['class'] = 'form-control'


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'activo']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estilo(self)


class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = Experiencia
        fields = ['titulo', 'descripcion', 'categoria', 'precio', 'cupo_maximo', 'fecha_hora', 'activa']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format=FORMATO),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_hora'].input_formats = [FORMATO]
        self.fields['categoria'].queryset = Categoria.objects.filter(
            Q(activo=True) | Q(id=self.instance.categoria_id)
        )
        estilo(self)

    def clean_fecha_hora(self):
        fecha = self.cleaned_data['fecha_hora']
        if not self.instance.pk and fecha < timezone.now():
            raise forms.ValidationError('La fecha debe ser futura.')
        return fecha

    def clean_cupo_maximo(self):
        cupo = self.cleaned_data['cupo_maximo']
        if self.instance.pk and cupo < self.instance.cupos_ocupados:
            raise forms.ValidationError('El cupo no puede ser menor a la cantidad de inscritos.')
        return cupo


class ExperienciaAdminForm(ExperienciaForm):
    class Meta(ExperienciaForm.Meta):
        fields = ['titulo', 'descripcion', 'categoria', 'precio', 'cupo_maximo', 'fecha_hora', 'creador', 'activa']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['creador'].queryset = User.objects.filter(
            Q(perfil__rol__in=['guia', 'admin']) | Q(is_superuser=True)
        ).distinct()
        estilo(self)


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['estado_pago']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estilo(self)


class ReservaAdminForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['usuario', 'experiencia', 'estado_pago']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].queryset = User.objects.filter(is_active=True, perfil__rol='turista')
        estilo(self)

    def clean(self):
        datos = super().clean()
        experiencia = datos.get('experiencia')
        if experiencia and experiencia.esta_llena:
            raise forms.ValidationError('La experiencia no tiene cupos disponibles.')
        return datos


class VisitanteForm(forms.Form):
    turista = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        experiencia = kwargs.pop('experiencia')
        super().__init__(*args, **kwargs)
        self.fields['turista'].queryset = User.objects.filter(
            is_active=True, perfil__rol='turista'
        ).exclude(inscripciones__experiencia=experiencia)
        self.fields['turista'].widget.attrs['class'] = 'form-control'
