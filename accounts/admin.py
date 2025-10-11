from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
	list_display = ('id', 'username', 'email', 'role', 'is_staff', 'is_active')
	list_filter = ('role', 'is_staff', 'is_active')
	search_fields = ('username', 'email')


# Admin site branding
admin.site.site_header = 'PetMarket Administration'
admin.site.site_title = 'PetMarket Admin'
admin.site.index_title = 'Panel de administración - PetMarket'

# Register your models here.
