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
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/add_role/', views.add_role, name='add_role'),
    path('dashboard/create_user/', views.create_user, name='create_user'),
    path('dashboard/edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('dashboard/delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin_dashboard/create_product/', views.crear_producto, name='create_product'),

    # Dashboard de Gerente
    path('dashboard/gerente/', views.gerente_dashboard, name='gerente_dashboard'),

    # Dashboard de Cajero
    path('cajero/', views.cajero_dashboard, name='cajero_dashboard'),

    # Gestión de Productos
    path('crear-producto/', views.crear_producto, name='crear_producto'),
    path('buscar_producto/<str:codigo>/', views.buscar_producto, name='buscar_producto'),
    path('escanear/', views.escanear_view, name='escanear_producto'),
    path('actualizar_stock/<int:producto_id>/', views.actualizar_stock, name='actualizar_stock'),

    # Gestión de Ventas
    path('dashboard/ventas/', views.dashboard_ventas, name='dashboard_ventas'),
    path('dashboard/ventas/excel/', views.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('dashboard/ventas/pdf/', views.exportar_ventas_pdf, name='exportar_ventas_pdf'),
    path('registrar_venta/', views.registrar_venta, name='registrar_venta'),
    path('dashboard/inventario/', views.dashboard_inventario, name='dashboard_inventario'),

    # Gestión de Proveedores
    path('proveedor/nuevo/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedor/editar/<int:proveedor_id>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedor/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    
  
    path('ver_ticket/<str:folio>/', views.ver_ticket, name='ver_ticket'),
    path('historial_ventas/', views.historial_ventas, name='historial_ventas'),



    # Gestión de Tareas
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    

    # Página de Inicio
    path('', views.home, name='home'),

    # Vista de acceso no autorizado
    path('no-autorizado/', views.no_autorizado, name='no_autorizado'),
]

# Archivos estáticos y multimedia (solo en desarrollo)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)