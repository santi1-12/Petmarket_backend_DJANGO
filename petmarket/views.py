from django.shortcuts import render


def index(request):
    """Vista simple para la página de inicio (landing)."""
    return render(request, 'index.html')
