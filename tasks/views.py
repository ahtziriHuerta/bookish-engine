from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Task, Rol, Usuario, Credencial, DatosPersonales
from .forms import TaskForm, UsuarioForm
from .utils import superuser_required  # Decorador para restringir acceso a superusuarios
from .decorators import roles_permitidos
from .forms import ProductoForm
from .models import Producto
from django.http import JsonResponse
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Venta, DetalleVenta
from django.db.models import Sum, Count
from .reportes import generar_excel_ventas, generar_pdf_ventas
from django.db.models import Sum
from datetime import datetime
from .models import Producto, IngresoProducto, EgresoProducto
from django.contrib import messages
from datetime import datetime, date



### 🔹 VISTA DE INICIO
def home(request):
    return render(request, 'home.html')


### 🔹 AUTENTICACIÓN Y LOGIN


def login_view(request):
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


@roles_permitidos(['Gerente'])
def gerente_dashboard(request):
    hoy = datetime.now()

    # Ventas del mes
    ventas = Venta.objects.filter(fecha__month=hoy.month, fecha__year=hoy.year)
    total_ventas = ventas.count()
    total_ingresos = ventas.aggregate(suma=Sum('total'))['suma'] or 0

    # Inventario
    productos = Producto.objects.all()
    stock_bajo = productos.filter(stock__lte=5)  # Cambia el umbral según necesites

    entradas_totales = IngresoProducto.objects.filter(
        fecha__month=hoy.month, fecha__year=hoy.year
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    egresos_totales = EgresoProducto.objects.filter(
        fecha__month=hoy.month, fecha__year=hoy.year
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    return render(request, 'dashboard_gerente.html', {
        'total_ventas': total_ventas,
        'total_ingresos': total_ingresos,
        'stock_bajo': stock_bajo,
        'total_entradas': entradas_totales,
        'total_egresos': egresos_totales,
        'mes': hoy.strftime('%B').capitalize()
    })




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
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductoForm()
    return render(request, 'create_product.html', {'form': form})  # ✅ esto está bien


@login_required
@roles_permitidos(['Cajero', 'Ventas', 'Administrador', 'Gerente'])
def buscar_producto(request, codigo):
    try:
        producto = Producto.objects.get(codigo_barras=codigo)
        return JsonResponse({
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'fecha': Venta.fecha.strftime('%d/%m/%Y %H:%M'),
            'imagen': producto.imagen.url if producto.imagen else '',
            'stock': producto.stock 
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    

def escanear_view(request):
    return render(request, 'escaner.html')


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
                fecha=datetime.now(),
                usuario=request.user  # 👈 aquí está la clave
            )
        elif diferencia < 0:
            # Registrar egreso
            EgresoProducto.objects.create(
                producto=producto,
                cantidad=abs(diferencia),
                fecha=datetime.now(),
                usuario=request.user  # 👈 aquí también
            )

        producto.stock = nuevo_stock
        producto.save()

        return redirect('dashboard_inventario')
    
    return render(request, 'actualizar_stock.html', {'producto': producto})




@roles_permitidos(['Administrador', 'Ventas', 'Gerente'])
def dashboard_ventas(request):
    mes_str = request.GET.get('mes')
    hoy = datetime.now()

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


@roles_permitidos(['Administrador', 'Gerente' , 'Ventas'])
def dashboard_inventario(request):
    hoy = datetime.now()

    productos = Producto.objects.all()
    inventario = []

    for producto in productos:
        entradas = IngresoProducto.objects.filter(
            producto=producto, fecha__month=hoy.month, fecha__year=hoy.year
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        egresos = EgresoProducto.objects.filter(
            producto=producto, fecha__month=hoy.month, fecha__year=hoy.year
        ).aggregate(total=Sum('cantidad'))['total'] or 0

        inventario.append({
            'producto': producto,
            'stock_actual': producto.stock,
            'total_entradas': entradas,
            'total_egresos': egresos
        })

    total_entradas = IngresoProducto.objects.filter(
        fecha__month=hoy.month, fecha__year=hoy.year
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    total_egresos = EgresoProducto.objects.filter(
        fecha__month=hoy.month, fecha__year=hoy.year
    ).aggregate(total=Sum('cantidad'))['total'] or 0

    return render(request, 'panel_inventario.html', {
        'inventario': inventario,
        'total_entradas': total_entradas,
        'total_egresos': total_egresos,
        'mes': hoy.strftime('%B').capitalize()
    })



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

