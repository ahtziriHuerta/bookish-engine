from django.contrib import admin
from django.urls import path
from tasks import views  

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # Autenticación y Sesión
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Dashboard de Administrador
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/add_role/', views.add_role, name='add_role'),
    path('dashboard/create_user/', views.create_user, name='create_user'),
    path('dashboard/edit_user/<int:user_id>/', views.edit_user, name='edit_user'),  # ✅ Agregamos la URL faltante
    path('dashboard/delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    



    # Gestión de Tareas
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),

    # Página de Inicio
    path('', views.home, name='home'),
]

