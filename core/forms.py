from django import forms
from core.models import ConfiguracionEcoparque


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEcoparque
        fields = ['nombre', 'lema', 'descripcion', 'telefono', 'correo', 'direccion', 'horario']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs['class'] = 'form-control'
