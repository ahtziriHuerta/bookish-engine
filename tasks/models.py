from django.db import models
from django.contrib.auth.models import User
import uuid
import qrcode

from django.conf import settings

# Create your models here.
import os
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

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

import qrcode
from io import BytesIO
from django.core.files import File

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(default='Sin descripción')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    codigo_barras = models.CharField(max_length=50, unique=True)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.CASCADE, null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Si no hay imagen y no se ha asignado aún
        if not self.imagen:
            default_path = os.path.join(settings.MEDIA_ROOT, 'productos/default.png')
            with open(default_path, 'rb') as f:
                self.imagen.save('default.png', File(f), save=False)

        # Generar QR si no existe
        if not self.qr_code:
            qr_data = f'{self.codigo_barras}'
            qr_img = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f'qr_{self.codigo_barras}.png'
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)


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
    
    



class Venta(models.Model):
    folio = models.CharField(primary_key=True, max_length=20, editable=False, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if not self.folio:
            import uuid
            self.folio = f'V-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)



class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)


class IngresoProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ingreso de {self.cantidad} {self.producto.nombre}"
    
class EgresoProducto(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    motivo = models.CharField(max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Egreso de {self.cantidad} de {self.producto.nombre}"

class CorteCaja(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2)
    total_por_metodo = models.JSONField(default=dict)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')} → {self.fecha_fin.strftime('%H:%M')}"
