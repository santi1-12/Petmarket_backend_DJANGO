from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'email', 'telefono')
	search_fields = ('nombre', 'email')
