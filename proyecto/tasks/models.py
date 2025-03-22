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

class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Usa la tabla de Django
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Credencial(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    codigo_barras = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Venta {self.id} - {self.fecha_hora}'

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Detalle {self.id} - Venta {self.venta.id}'

# Modelo para almacenar los datos personales de los usuarios
class DatosPersonales(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación uno a uno con el modelo User
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    nss = models.CharField(max_length=15, unique=True)  # Número de Seguro Social
    domicilio = models.TextField(blank=True, null=True)  # Domicilio del usuario
    telefono = models.CharField(max_length=15, blank=True, null=True)  # Teléfono del usuario

    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.usuario.username}'