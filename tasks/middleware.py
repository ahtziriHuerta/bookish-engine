from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            settings.LOGIN_URL,
            '/register/',
            '/admin/',
            '/static/',
        ]

    def __call__(self, request):
        path = request.path_info

        if any(path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)

        if not request.user.is_authenticated:
            messages.warning(request, "⚠️ Debes iniciar sesión para acceder a esta página.")
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)

