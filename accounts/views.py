from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, ProfileSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from carrito.models import Cart, CartItem
from django.http import HttpResponseForbidden


# API views (existing JWT endpoints)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        data['show_password'] = False
        return Response(data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({"detail": "Sesión cerrada"})
        except Exception:
            return Response({"error": "Token inválido"}, status=400)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Server-rendered session views
def register_page(request):
    if request.method == 'POST':
        # Handle modal form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Basic validation
        if not username or not email or not password1 or not password2:
            from django.contrib import messages
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('/')
            
        if password1 != password2:
            from django.contrib import messages
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('/')
            
        if len(password1) < 8:
            from django.contrib import messages
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return redirect('/')
            
        if CustomUser.objects.filter(username=username).exists():
            from django.contrib import messages
            messages.error(request, 'El nombre de usuario ya existe.')
            return redirect('/')
            
        if CustomUser.objects.filter(email=email).exists():
            from django.contrib import messages
            messages.error(request, 'El email ya está registrado.')
            return redirect('/')
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            auth_login(request, user)
            from django.contrib import messages
            messages.success(request, f'¡Bienvenido a PetMarket, {user.first_name or user.username}! Tu cuenta ha sido creada exitosamente.')
            return redirect('/')
        except Exception as e:
            from django.contrib import messages
            messages.error(request, 'Hubo un error al crear tu cuenta. Intenta de nuevo.')
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            from django.contrib import messages
            messages.error(request, 'Por favor, completa todos los campos.')
            return redirect('/')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            
            # Forzar rotación del token CSRF
            from django.middleware.csrf import rotate_token
            rotate_token(request)
            
            # Merge session cart into persistent cart for logged-in users
            session_cart = request.session.get('cart', {})
            if session_cart:
                cart, _ = Cart.objects.get_or_create(user=user)
                for pid, qty in session_cart.items():
                    try:
                        pid_int = int(pid)
                        item, created = CartItem.objects.get_or_create(cart=cart, producto_id=pid_int)
                        if not created:
                            item.quantity += int(qty)
                        else:
                            item.quantity = int(qty)
                        item.save()
                    except Exception:
                        continue
                # clear session cart
                try:
                    del request.session['cart']
                except KeyError:
                    pass
            
            from django.contrib import messages
            messages.success(request, f'¡Bienvenido de vuelta, {user.first_name or user.username}!')
            
            # Role-based redirection
            try:
                user_role = getattr(user, 'role', None)
            except Exception:
                user_role = None
            
            # Crear respuesta de redirección
            if getattr(user, 'is_superuser', False) or user_role == 'admin':
                response = redirect('/empleados/admin/')
            elif user_role == 'empleado' or getattr(user, 'is_staff', False):
                response = redirect('/empleados/panel/')
            else:
                response = redirect('/accounts/web/panel/')
            
            # Agregar header para evitar caché
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            return response
        else:
            from django.contrib import messages
            messages.error(request, 'Usuario o contraseña incorrectos. Intenta de nuevo.')
            return redirect('/')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_page(request):
    user_name = request.user.first_name or request.user.username if request.user.is_authenticated else ''
    auth_logout(request)
    from django.contrib import messages
    if user_name:
        messages.success(request, f'¡Hasta luego, {user_name}! Vuelve pronto.')
    else:
        messages.success(request, '¡Hasta luego! Vuelve pronto.')
    return redirect('/')


@login_required
def profile_page(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        
        # Update user
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        
        # Check if email is unique
        if email != user.email:
            if CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
                from django.contrib import messages
                messages.error(request, 'Ese email ya está en uso por otro usuario.')
                return redirect('web_profile')
            user.email = email
        
        user.save()
        
        from django.contrib import messages
        messages.success(request, '¡Perfil actualizado correctamente!')
        return redirect('web_profile')
    
    return render(request, 'accounts/profile.html', {'user': request.user})


# Simple dashboards
@login_required
def user_dashboard(request):
    # Only non-staff, non-superuser general users
    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("No autorizado")
    return render(request, 'accounts/dashboard_user.html')


@login_required
def empleado_dashboard(request):
    # Only staff or role empleado
    role = getattr(request.user, 'role', None)
    if not (request.user.is_staff or role == 'empleado'):
        return HttpResponseForbidden("No autorizado")
    return render(request, 'empleados/dashboard.html')
