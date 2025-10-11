from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'precio', 'stock', 'thumbnail')
	search_fields = ('nombre',)
	readonly_fields = ('preview',)

	def thumbnail(self, obj):
		if obj.image:
			return f"<img src='{obj.image.url}' style='height:40px; object-fit:cover'/>"
		return "-"
	thumbnail.allow_tags = True

	def preview(self, obj):
		if obj.image:
			return f"<img src='{obj.image.url}' style='max-height:200px; object-fit:contain'/>"
		return "No image"
	preview.allow_tags = True

