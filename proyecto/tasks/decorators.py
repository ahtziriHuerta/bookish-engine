from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from tasks.models import Usuario  # O cambia 'tasks' por la app donde esté tu modelo

def roles_permitidos(lista_roles):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                usuario = Usuario.objects.get(user=request.user)
                if usuario.rol.nombre_rol in lista_roles or request.user.is_superuser:
                    return view_func(request, *args, **kwargs)
            except Usuario.DoesNotExist:
                pass
            return redirect('no_autorizado')
        return _wrapped_view
    return decorator
