from django.shortcuts import redirect

def superuser_required(view_func):
    """Decorador para restringir vistas solo a superusuarios."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('home')  # Redirige a home si el usuario no es superusuario
        return view_func(request, *args, **kwargs)
    return wrapper
