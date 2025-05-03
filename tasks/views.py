# Django core
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.messages import get_messages
from django.template.loader import get_template


# Decoradores personalizados
from .decorators import roles_permitidos
from .utils import superuser_required

# Modelos
from .models import (
    Task, Rol, Usuario, Credencial, DatosPersonales,
    Producto, IngresoProducto, EgresoProducto,
    Venta, DetalleVenta, CorteCaja
)

# Formularios
from .forms import TaskForm, UsuarioForm, ProductoForm

# Reportes
from .reportes import generar_excel_ventas, generar_pdf_ventas

# Librerías para PDF y correo
import tempfile
from django.core.mail import EmailMessage
import io
import json
from weasyprint import HTML
from django.template.loader import render_to_string

# Fechas y utilidades
from django.utils import timezone
from django.utils.timezone import now, make_aware
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from calendar import monthrange
from datetime import datetime, date, time, timedelta


### 🔹 VISTA DE INICIO
def home(request):
    return render(request, 'home.html')


### 🔹 AUTENTICACIÓN Y LOGIN

def login_view(request):
    # Limpiar mensajes anteriores si los hay
    storage = get_messages(request)
    for _ in storage:
        pass

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            usuario = Usuario.objects.get(user=user)
            rol = usuario.rol.nombre_rol

            if rol == "Administrador":
                return redirect("admin_dashboard")
            elif rol == "Gerente":
                return redirect("gerente_dashboard")
            elif rol == "Ventas":
                return redirect("dashboard_ventas")
            elif rol == "Cajero":
                return redirect("cajero_dashboard")
            else:
                return redirect("no_autorizado")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")



def logout_view(request):
    logout(request)
    return redirect('login')



### 🔹 DASHBOARD PARA ADMINISTRADOR
@superuser_required
def admin_dashboard(request):
    usuarios = Usuario.objects.all()
    roles = Rol.objects.all()
    return render(request, 'admin_dashboard.html', {'usuarios': usuarios, 'roles': roles})

from .decorators import roles_permitidos  # Asegúrate de tener esta línea


@roles_permitidos(["Cajero", 'Administrador', 'Gerente'])
def cajero_dashboard(request):
    productos = Producto.objects.all()  # 👈 debe ser así de simple
    return render(request, 'cajero_dashboard.html', {'productos': productos})


### 🔹 REGISTRO DE USUARIOS
def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UsuarioForm()})

    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, 'signup.html', {'form': UsuarioForm()})

        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, "El usuario ya existe")
                return render(request, 'signup.html', {'form': UsuarioForm()})

            user = User.objects.create_user(username=username, password=password1)
            user.save()
            login(request, user)
            return redirect('tasks')

        except Exception as e:
            messages.error(request, f"Error al crear usuario: {str(e)}")
            return render(request, 'signup.html', {'form': UsuarioForm()})
        
 ### 🔹 no autoriza el acceso       
def no_autorizado(request):
    return render(request, 'no_autorizado.html')



### 🔹 LISTAR Y CREAR TAREAS
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {'form': TaskForm()})

    try:
        form = TaskForm(request.POST)
        new_task = form.save(commit=False)
        new_task.user = request.user
        new_task.save()
        messages.success(request, "Tarea creada exitosamente")
        return redirect('tasks')
    except ValueError:
        messages.error(request, "Datos inválidos")
        return render(request, 'create_task.html', {'form': TaskForm()})


### 🔹 CREAR USUARIOS DESDE EL PANEL DE ADMINISTRACIÓN
@superuser_required
@roles_permitidos(['Administrador','Gerente'])
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        rol_id = request.POST['rol']
        correo = request.POST['correo']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        nss = request.POST['nss']
        domicilio = request.POST['domicilio']
        telefono = request.POST['telefono']

        try:
            if User.objects.filter(username=username).exists():
                messages.error(request, "El usuario ya existe")
                return redirect('create_user')

            user = User.objects.create_user(username=username, password=password)
            rol = Rol.objects.get(id=rol_id)
            usuario = Usuario.objects.create(user=user, rol=rol)

            Credencial.objects.create(usuario=usuario, correo=correo, contraseña=password)
            DatosPersonales.objects.create(
                usuario=user, nombre=nombre, apellido=apellido, nss=nss, domicilio=domicilio, telefono=telefono
            )

            messages.success(request, "Usuario creado correctamente")
            return redirect('admin_dashboard')

        except Exception as e:
            messages.error(request, f"Error al crear usuario: {str(e)}")
            return redirect('create_user')

    roles = Rol.objects.all()
    return render(request, 'create_user.html', {'roles': roles})



### 🔹 EDITAR USUARIO
@roles_permitidos(['Administrador','Gerente'])
def edit_user(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    if request.method == 'POST':
        usuario.user.username = request.POST['username']
        usuario.user.email = request.POST['correo']
        usuario.nombre = request.POST['nombre']
        usuario.apellido = request.POST['apellido']
        usuario.nss = request.POST['nss']
        usuario.domicilio = request.POST['domicilio']
        usuario.telefono = request.POST['telefono']

        nuevo_rol_id = request.POST['rol']
        usuario.rol = Rol.objects.get(id=nuevo_rol_id)

        usuario.user.save()
        usuario.save()

        messages.success(request, "Usuario actualizado correctamente")
        return redirect('admin_dashboard')

    roles = Rol.objects.all()
    return render(request, 'edit_user.html', {'usuario': usuario, 'roles': roles})


### 🔹 AGREGAR ROLES DESDE EL PANEL DE ADMINISTRACIÓN
@superuser_required
def add_role(request):
    if request.method == 'POST':
        nombre_rol = request.POST['nombre_rol']
        if Rol.objects.filter(nombre_rol=nombre_rol).exists():
            messages.error(request, "El rol ya existe")
        else:
            Rol.objects.create(nombre_rol=nombre_rol)
            messages.success(request, "Rol agregado correctamente")
        return redirect('admin_dashboard')

    return render(request, 'admin_dashboard.html')


### 🔹 ELIMINAR USUARIO
@roles_permitidos(['Administrador','Gerente'])
@superuser_required
def delete_user(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.user.delete()
    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente")
    return redirect('admin_dashboard')


@roles_permitidos(['Administrador','Ventas', 'Gerente'])
def crear_producto(request):
    creado = False
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            return redirect('ver_producto', producto_id=producto.id)
    else:
        form = ProductoForm()
    return render(request, 'create_product.html', {'form': form, 'creado': creado})


def ver_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'ver_producto.html', {'producto': producto})






@csrf_exempt
@roles_permitidos(['Administrador','Ventas', 'Gerente'])
def actualizar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        nuevo_stock = int(request.POST.get('nuevo_stock'))
        diferencia = nuevo_stock - producto.stock

        if diferencia > 0:
            # Registrar ingreso
            IngresoProducto.objects.create(
                producto=producto,
                cantidad=diferencia,
                fecha=timezone.now(),
                usuario=request.user  # 👈 aquí está la clave
            )
        elif diferencia < 0:
            # Registrar egreso
            EgresoProducto.objects.create(
                producto=producto,
                cantidad=abs(diferencia),
                fecha=timezone.now(),
                usuario=request.user  # 👈 aquí también
            )

        producto.stock = nuevo_stock
        producto.save()

        return redirect('dashboard_inventario')
    
    return render(request, 'actualizar_stock.html', {'producto': producto})




@roles_permitidos(['Administrador', 'Ventas', 'Gerente'])
def dashboard_ventas(request):
    mes_str = request.GET.get('mes')
    hoy = timezone.now()

    if mes_str:
        año, mes = map(int, mes_str.split('-'))
    else:
        año, mes = hoy.year, hoy.month

    ventas = Venta.objects.filter(fecha__month=mes, fecha__year=año).annotate(
        tiene_ticket=Count('detalleventa')
    )
    total_ingresos = ventas.aggregate(total=Sum('total'))['total'] or 0
    total_por_metodo = list(ventas.values('metodo_pago').annotate(total=Sum('total')))

    return render(request, 'dashboard_ventas.html', {
        'ventas': ventas,
        'total_ingresos': total_ingresos,
        'total_por_metodo': total_por_metodo,
        'mes': date(año, mes, 1).strftime('%B').capitalize(),
        'mes_valor': f'{año}-{mes:02d}'
    })


@roles_permitidos(['Administrador', 'Ventas','Gerente'])
def exportar_ventas_excel(request):
    return generar_excel_ventas()

@roles_permitidos(['Administrador', 'Ventas' , 'Gerente'])
def exportar_ventas_pdf(request):
    return generar_pdf_ventas()


from django.shortcuts import render, redirect
from .forms import ProveedorForm

def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')  # Cambia por el nombre de tu vista de lista si tienes
    else:
        form = ProveedorForm()
    
    return render(request, 'crear_proveedor.html', {'form': form})


# views.py
from .models import Proveedor

def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'lista_proveedores.html', {'proveedores': proveedores})

# views.py
from django.shortcuts import get_object_or_404

def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'editar_proveedor.html', {'form': form})


def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        proveedor.delete()
        return redirect('lista_proveedores')
    return render(request, 'eliminar_proveedor.html', {'proveedor': proveedor})


@roles_permitidos(['Administrador', 'Cajero', 'Ventas', 'Gerente'])
def ver_ticket(request, folio):
    venta = get_object_or_404(Venta, folio=folio)
    detalles = DetalleVenta.objects.filter(venta=venta)

    # Agregar el subtotal directamente al objeto detalle
    for d in detalles:
        d.subtotal = d.cantidad * d.precio_unitario

    return render(request, 'ver_ticket.html', {
        'venta': venta,
        'detalles': detalles
    })


@csrf_exempt
def registrar_venta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            metodo_pago = data.get('metodo_pago')

            if not items:
                return JsonResponse({'success': False, 'error': 'No hay productos en el ticket'}, status=400)

            total_calculado = 0
            detalles_a_guardar = []

            # 🔎 Validar stock antes de crear la venta
            for item in items:
                producto = Producto.objects.get(id=item['id'])
                cantidad = int(item['qty'])

                if producto.stock < cantidad:
                    return JsonResponse({
                        'success': False,
                        'error': f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}, solicitado: {cantidad}"
                    }, status=400)

            # ✅ Crear la venta con total temporal
            venta = Venta.objects.create(
                usuario=request.user,
                total=0,
                metodo_pago=metodo_pago
            )

            # 🧾 Crear los detalles y descontar stock
            for item in items:
                producto = Producto.objects.get(id=item['id'])
                cantidad = int(item['qty'])
                precio = float(item['price'])

                subtotal = cantidad * precio
                total_calculado += subtotal

                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio
                )

                # Descontar stock
                producto.stock -= cantidad
                producto.save()

                print(f"✅ Agregado: {producto.nombre} x{cantidad} - ${precio}")
                print(f"📦 Nuevo stock de {producto.nombre}: {producto.stock}")

            # Guardar el total final
            venta.total = total_calculado
            venta.save()
            venta.refresh_from_db()

            return JsonResponse({
                'success': True,
                'folio': venta.folio,
                'fecha': venta.fecha.strftime('%d/%m/%Y %H:%M'),
                'metodo_pago': venta.metodo_pago
            })

        except Exception as e:
            print(f"❌ Error al registrar venta: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)



@roles_permitidos(['Administrador', 'Cajero', 'Ventas', 'Gerente'])
def historial_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')  # 👈 así ordenas por fecha descendente
    return render(request, 'historial_ventas.html', {'ventas': ventas})



@roles_permitidos(['Administrador'])
def eliminar_venta(request, folio):
    venta = get_object_or_404(Venta, folio=folio)

    detalles = DetalleVenta.objects.filter(venta=venta)
    for detalle in detalles:
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()

    detalles.delete()
    venta.delete()

    messages.success(request, "Venta eliminada correctamente")
    return redirect('admin_dashboard')  # o donde estés redirigiendo


@roles_permitidos(['Administrador', 'Gerente','Ventas'])
def dashboard_gerente(request):
    from django.utils.timezone import make_aware
    mes_param = request.GET.get('mes')

    if mes_param:
        year, month = map(int, mes_param.split('-'))
        primer_dia_mes = timezone.make_aware(datetime(year, month, 1))
        ultimo_dia = monthrange(year, month)[1]
        ultimo_dia_mes = timezone.make_aware(datetime(year, month, ultimo_dia, 23, 59, 59))
    else:
        hoy = timezone.now()
        primer_dia_mes = hoy.replace(day=1)
        ultimo_dia_mes = hoy
        mes_param = hoy.strftime('%Y-%m')

    print("Mes recibido desde el GET:", mes_param)  # 👈 asegúrate de que cambie

    ventas_mes = Venta.objects.filter(fecha__range=(primer_dia_mes, ultimo_dia_mes))
    total_ventas = ventas_mes.count()
    ingresos_totales = ventas_mes.aggregate(Sum('total'))['total__sum'] or 0
    sin_ventas = total_ventas == 0

    productos_bajo_stock = Producto.objects.filter(stock__lt=5)

    ventas_por_dia = (
        ventas_mes
        .annotate(fecha_dia=TruncDate('fecha'))
        .values('fecha_dia')
        .annotate(total_dia=Sum('total'))
        .order_by('fecha_dia')
    )

    productos_mas_vendidos = (
        DetalleVenta.objects.filter(venta__fecha__range=(primer_dia_mes, ultimo_dia_mes))
        .values('producto__nombre')
        .annotate(cantidad_total=Sum('cantidad'))
        .order_by('-cantidad_total')[:5]
    )

    return render(request, 'dashboard_gerente.html', {
        'total_ventas': total_ventas,
        'ingresos_totales': ingresos_totales,
        'productos_bajo_stock': productos_bajo_stock,
        'ventas_por_dia': ventas_por_dia,
        'productos_mas_vendidos': productos_mas_vendidos,
        'mes_actual': mes_param,
        'sin_ventas': sin_ventas,
    })


@roles_permitidos(['Administrador', 'Gerente', 'Ventas'])
def dashboard_inventario(request):
    mes_param = request.GET.get('mes')
    hoy = timezone.now()

    if mes_param:
        year, month = map(int, mes_param.split('-'))
        primer_dia = timezone.make_aware(datetime(year, month, 1))
        ultimo_dia = monthrange(year, month)[1]
        ultimo_dia_mes = timezone.make_aware(datetime(year, month, ultimo_dia, 23, 59, 59))
    else:
        primer_dia = hoy.replace(day=1)
        ultimo_dia_mes = hoy
        mes_param = hoy.strftime('%Y-%m')

    productos = Producto.objects.all()
    inventario = []

    for producto in productos:
        entradas = IngresoProducto.objects.filter(
            producto=producto, fecha__range=(primer_dia, ultimo_dia_mes)
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        egresos = DetalleVenta.objects.filter(
            producto=producto,
            venta__fecha__range=(primer_dia, ultimo_dia_mes)
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        inventario.append({
            'producto': producto,
            'stock_actual': producto.stock,
            'total_entradas': entradas,
            'total_egresos': egresos
        })

    total_entradas = IngresoProducto.objects.filter(
        fecha__range=(primer_dia, ultimo_dia_mes)
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    total_egresos = DetalleVenta.objects.filter(
        venta__fecha__range=(primer_dia, ultimo_dia_mes)
    ).aggregate(total=Sum('cantidad'))['total'] or 0


    return render(request, 'panel_inventario.html', {
        'inventario': inventario,
        'total_entradas': total_entradas,
        'total_egresos': total_egresos,
        'mes_actual': mes_param,
    })


@roles_permitidos(['Cajero', 'Administrador'])
def corte_caja(request):
    usuario = request.user

    # Determinar rango de fechas
    ultimo_corte = CorteCaja.objects.filter(usuario=usuario).order_by('-fecha_fin').first()
    if ultimo_corte:
        fecha_inicio = ultimo_corte.fecha_fin
    else:
        primera_venta = Venta.objects.filter(usuario=usuario).order_by('fecha').first()
        fecha_inicio = primera_venta.fecha if primera_venta else now() - timedelta(days=1)

    fecha_fin = now()

    # Ventas del periodo
    ventas = Venta.objects.filter(usuario=usuario, fecha__range=(fecha_inicio, fecha_fin))
    total_ventas = ventas.aggregate(Sum('total'))['total__sum'] or 0
    ventas_resumen = ventas.order_by('fecha')

    total_por_metodo = list(
        ventas.values('metodo_pago').annotate(total=Sum('total'))
    )
    for item in total_por_metodo:
        item['total'] = float(item['total'])

    # Acción: generar PDF solo
    if request.GET.get('pdf') == '1':
        return generar_pdf(request, ventas_resumen, total_ventas, total_por_metodo, fecha_inicio, fecha_fin)

    # Acción: enviar PDF por correo solo
    if request.GET.get('enviar') == '1':
        enviado = enviar_pdf(request, ventas_resumen, total_ventas, total_por_metodo, fecha_inicio, fecha_fin)
        if enviado:
            messages.success(request, "Corte enviado al gerente.")
        return redirect('corte_caja')

    # ✅ Acción al hacer POST (guardar + enviar + renderizar para imprimir)
    if request.method == 'POST':
        # 1. Guardar el corte
        CorteCaja.objects.create(
            usuario=usuario,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_ventas=total_ventas,
            total_por_metodo=total_por_metodo
        )

        # 2. Enviar correo
        enviar_pdf(request, ventas_resumen, total_ventas, total_por_metodo, fecha_inicio, fecha_fin)

        # 3. Renderizar HTML imprimible
        html_string = render_to_string('corte_pdf.html', {
            'ventas_resumen': ventas_resumen,
            'total_ventas': total_ventas,
            'total_por_metodo': total_por_metodo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'request': request
        })
        return HttpResponse(html_string)

    # Vista por defecto (GET normal)
    return render(request, 'corte_caja.html', {
        'ventas_resumen': ventas_resumen,
        'total_ventas': total_ventas,
        'total_por_metodo': total_por_metodo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })

            
            
def generar_pdf(request, ventas, total, metodo, inicio, fin):
    html_string = render_to_string('corte_pdf.html', {
        'ventas_resumen': ventas,
        'total_ventas': total,
        'total_por_metodo': metodo,
        'fecha_inicio': inicio,
        'fecha_fin': fin,
        'request': request
    })
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    return HttpResponse(pdf_file, content_type='application/pdf')

def enviar_pdf(request, ventas, total, metodo, inicio, fin):
    html_string = render_to_string('corte_pdf.html', {
        'ventas_resumen': ventas,
        'total_ventas': total,
        'total_por_metodo': metodo,
        'fecha_inicio': inicio,
        'fecha_fin': fin,
        'request': request
    })
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
    email = EmailMessage(
        '📋 Corte de Caja',
        'Adjunto el corte realizado.',
        to=['gerente@tiendacorozo.com']
    )
    email.attach('corte_caja.pdf', pdf_file, 'application/pdf')
    email.send()
    return True


@login_required
@roles_permitidos(['Cajero', 'Ventas', 'Administrador', 'Gerente'])
def buscar_producto(request, codigo):
    try:
        producto = Producto.objects.get(codigo_barras=codigo)
        return JsonResponse({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'stock': producto.stock,
            'imagen': producto.imagen.url if producto.imagen else '',
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


def escanear_view(request):
    return render(request, 'escaner.html')