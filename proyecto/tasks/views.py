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
            return redirect("admin_dashboard" if user.is_superuser else "tasks")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return render(request, "login.html")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


### 🔹 DASHBOARD PARA ADMINISTRADOR
@superuser_required
def admin_dashboard(request):
    usuarios = Usuario.objects.all()
    roles = Rol.objects.all()
    return render(request, 'admin_dashboard.html', {'usuarios': usuarios, 'roles': roles})

from .decorators import roles_permitidos  # Asegúrate de tener esta línea

@roles_permitidos(["Cajero"])
def cajero_dashboard(request):
    return render(request, 'cajero_dashboard.html')

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
@superuser_required
def delete_user(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.user.delete()
    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente")
    return redirect('admin_dashboard')



def cajero_dashboard(request):
    productos = Producto.objects.all()
    return render(request, 'cajero_dashboard.html', {'productos': productos})


def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('cajero_dashboard')

    else:
        form = ProductoForm()
    return render(request, 'create_product.html', {'form': form})


from django.shortcuts import render, redirect
from .forms import ProveedorForm

def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard.html')  # Cambia por el nombre de tu vista de lista si tienes
    else:
        form = ProveedorForm()
    
    return render(request, 'crear_proveedor.html', {'form': form})