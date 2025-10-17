from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


def index(request):
    """Vista simple para la página de inicio (landing)."""
    return render(request, 'index.html')


@ensure_csrf_cookie
def test_csrf_page(request):
    """Página de prueba de CSRF"""
    if request.method == 'POST':
        return JsonResponse({
            'status': 'success',
            'message': '✓ CSRF verificado correctamente',
            'data': request.POST.get('test_field', '')
        })
    return render(request, 'test_csrf.html')
