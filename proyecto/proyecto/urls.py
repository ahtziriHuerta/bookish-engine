from django.contrib import admin
from django.urls import path
from tasks import views  
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
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
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('cajero/', views.cajero_dashboard, name='cajero_dashboard'), 
    path('crear-producto/', views.crear_producto, name='crear_producto'),
    path('no-autorizado/', views.no_autorizado, name='no_autorizado'),
    


    # Gestión de Tareas
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),

    # Página de Inicio
    path('', views.home, name='home'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


