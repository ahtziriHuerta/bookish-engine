


def rol_usuario(request):
    if request.user.is_authenticated:
        try:
            return {'user_rol': request.user.usuario.rol.nombre_rol}
        except:
            return {'user_rol': None}
    return {'user_rol': None}
