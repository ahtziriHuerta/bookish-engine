from django.forms import ModelForm
from .models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important']

from django import forms
from .models import Rol

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
