from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ' | ' + str(self.user)
    


class Rol(models.Model):
    nombre_rol = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre_rol
    
def crear_usuario_con_rol(sender, instance, created, **kwargs):
    if created:
        from .models import Rol, Usuario
        try:
            rol_empleado = Rol.objects.get(nombre_rol="Empleado")
        except Rol.DoesNotExist:
            rol_empleado = Rol.objects.create(nombre_rol="Empleado")
        Usuario.objects.create(user=instance, rol=rol_empleado)

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Usa la tabla de Django
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Credencial(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)
# Modelo para almacenar los datos personales de los usuarios


class CorteCaja(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2)
    total_por_metodo = models.JSONField(default=dict)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - Corte {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')} → {self.fecha_fin.strftime('%H:%M')}"