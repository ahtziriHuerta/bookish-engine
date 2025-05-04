from django.contrib import admin
from django.urls import path
from tasks import views  
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from tasks.views import buscar_producto
from tasks.views import validar_pin




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

    # Dashboard de Gerente
   path('dashboard/gerente/', views.dashboard_gerente, name='gerente_dashboard'),


    # Dashboard de Cajero
    path('cajero/', views.cajero_dashboard, name='cajero_dashboard'),

    # Gestión de Productos
    path('inventario/crear-producto/', views.crear_producto, name='crear_producto'),
    path('inventario/create_product/', views.crear_producto, name='crear_producto'),
    path('buscar_producto/<str:codigo>/', views.buscar_producto, name='buscar_producto'),
    path('api/producto/<str:codigo>/', views.buscar_producto, name='buscar_producto'),
    path('escanear/', views.escanear_view, name='escanear_producto'),
    path('inventario/actualizar_stock/<int:producto_id>/', views.actualizar_stock, name='actualizar_stock'),
    path('dashboard/inventario/create_product/', views.crear_producto, name='create_product'),
    path('dashboard/inventario/', views.dashboard_inventario, name='dashboard_inventario'),
    path('inventario/producto/<int:producto_id>/', views.ver_producto, name='ver_producto'),
    path('producto/<int:producto_id>/', views.ver_producto, name='ver_producto'),
    path('buscar-producto/<str:codigo>/', buscar_producto, name='buscar_producto'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('producto/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),

    # Gestión de Proveedores
    path('dashboard/inventario/proveedor/nuevo/', views.crear_proveedor, name='crear_proveedor'),
    path('dashboard/inventario/proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('dashboard/inventario/proveedor/editar/<int:proveedor_id>/', views.editar_proveedor, name='editar_proveedor'),
    path('dashboard/inventario/proveedor/eliminar/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    

    # Gestión de Ventas
    path('dashboard/ventas/', views.dashboard_ventas, name='dashboard_ventas'),
    path('dashboard/ventas/excel/', views.exportar_ventas_excel, name='exportar_ventas_excel'),
    path('dashboard/ventas/pdf/', views.exportar_ventas_pdf, name='exportar_ventas_pdf'),
    path('registrar_venta/', views.registrar_venta, name='registrar_venta'),
    path('dashboard/inventario/', views.dashboard_inventario, name='dashboard_inventario'),
    path('ventas/eliminar/<str:folio>/', views.eliminar_venta, name='eliminar_venta'),
    path('corte-caja/', views.corte_caja, name='corte_caja'),
    path('ver_ticket/<str:folio>/', views.ver_ticket, name='ver_ticket'),
    path('historial_ventas/', views.historial_ventas, name='historial_ventas'),
   

    # Gestión de Tareas
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    

    # Página de Inicio
    path('', views.home, name='home'),

    # Vista de acceso no autorizado
    path('no-autorizado/', views.no_autorizado, name='no_autorizado'),
    path('validar-pin/', validar_pin, name='validar_pin'),
    
]

# Archivos estáticos y multimedia (solo en desarrollo)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)