from django.forms import ModelForm
from .models import Task
from .models import Rol
from django import forms
from .models import Producto
from .models import Proveedor
from django.template.defaultfilters import register
from django.db import models


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']


class UsuarioForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), required=True)
    correo = forms.EmailField(required=True)
    nombre = forms.CharField(max_length=100, required=True)
    apellido = forms.CharField(max_length=100, required=True)
    nss = forms.CharField(max_length=15, required=True)
    domicilio = forms.CharField(widget=forms.Textarea, required=False)
    telefono = forms.CharField(max_length=15, required=False)

from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'codigo_barras', 'proveedor', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'proveedor': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }

    def clean_codigo_barras(self):
        codigo = self.cleaned_data['codigo_barras']

        if not codigo.isdigit():
            raise forms.ValidationError("El código de barras solo debe contener números.")
        if not 8 <= len(codigo) <= 13:
            raise forms.ValidationError("Debe tener entre 8 y 13 dígitos.")

        return codigo

       



class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'telefono', 'direccion']
        
        
@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

