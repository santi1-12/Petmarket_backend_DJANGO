from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_page, name='web_register'),
    path('login/', views.login_page, name='web_login'),
    path('logout/', views.logout_page, name='web_logout'),
    path('profile/', views.profile_page, name='web_profile'),
    path('panel/', views.user_dashboard, name='web_user_dashboard'),
]
