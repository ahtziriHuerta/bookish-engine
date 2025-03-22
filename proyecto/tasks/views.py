from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .forms import TaskForm, UsuarioForm
from .models import Task, Rol, Usuario

from django.contrib.auth.decorators import login_required

@login_required
def edit_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    usuario = Usuario.objects.get(id=user_id)
    
    if request.method == 'POST':
        # Aquí puedes manejar la edición de usuario, como cambiar su rol
        nuevo_rol = request.POST['rol']
        usuario.rol = Rol.objects.get(id=nuevo_rol)
        usuario.save()
        return redirect('admin_dashboard')
    
    return render(request, 'edit_user.html', {'usuario': usuario, 'roles': Rol.objects.all()})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Verificar si es superusuario
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirigir a la vista de admin
            else:
                return redirect('home')  # O alguna otra vista para usuarios normales
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    else:
        return render(request, 'login.html')

# Create your views here.

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')  # Redirige si no es superusuario
    # Aquí se pueden pasar los objetos para gestionar roles y usuarios
    return render(request, 'admin_dashboard.html')

@login_required
def add_role(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        nombre_rol = request.POST['nombre_rol']
        Rol.objects.create(nombre_rol=nombre_rol)
        return redirect('admin_dashboard')
    return render(request, 'admin_dashboard.html')


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
        'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'User already exists'
                })
        else:
            return render(request, 'signup.html', {
                'form': UserCreationForm,
                'error': 'Passwords do not match'
            })


def tasks(request):
    tasks = Task.objects.filter(user = request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

def create_task(request):

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm()
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm(),
                'error': 'Bad data passed in. Try again.'
            })


def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'User does not exist'
            })
        else:
            login(request, user)
            return redirect('tasks')
        
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Usuario, Rol, Credencial, DatosPersonales
from .forms import UsuarioForm

def create_user(request):
    if not request.user.is_superuser:
        return redirect('home')  # Redirigir si no es superusuario

    if request.method == 'POST':
        # Recoger datos del formulario de Usuario
        username = request.POST['username']
        password = request.POST['password']
        rol_id = request.POST['rol']  # Obtener el ID del rol asignado
        
        # Crear el usuario de Django
        user = User.objects.create_user(username=username, password=password)
        
        # Crear el objeto Usuario y asociarlo con el rol
        rol = Rol.objects.get(id=rol_id)
        usuario = Usuario.objects.create(user=user, rol=rol)
        
        # Crear las credenciales del usuario
        correo = request.POST['correo']
        contraseña = request.POST['password']  # La misma contraseña o puedes cambiarla
        Credencial.objects.create(usuario=usuario, correo=correo, contraseña=contraseña)
        
        # Crear los datos personales
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        nss = request.POST['nss']
        domicilio = request.POST['domicilio']
        telefono = request.POST['telefono']
        
        DatosPersonales.objects.create(
            usuario=user,
            nombre=nombre,
            apellido=apellido,
            nss=nss,
            domicilio=domicilio,
            telefono=telefono
        )

        messages.success(request, "Usuario creado correctamente")
        return redirect('admin_dashboard')  # O donde necesites redirigir

    # Si el método es GET, mostrar el formulario vacío
    roles = Rol.objects.all()  # Obtener todos los roles disponibles
    return render(request, 'create_user.html', {'roles': roles})
