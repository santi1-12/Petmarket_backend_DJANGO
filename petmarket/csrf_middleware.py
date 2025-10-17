from django.middleware.csrf import get_token

class EnsureCSRFMiddleware:
    """
    Middleware para asegurar que el token CSRF esté siempre disponible
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Forzar la generación del token CSRF
        get_token(request)
        response = self.get_response(request)
        return response
