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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_page(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
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
            return redirect('/')
        else:
            from django.contrib import messages
            messages.error(request, 'Credenciales inválidas. Intenta de nuevo.')
            # If the POST comes from hero (no form rendering), redirect back to home
            if request.META.get('HTTP_REFERER', '').endswith('/'):
                return redirect('/')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_page(request):
    auth_logout(request)
    return redirect('/')


@login_required
def profile_page(request):
    return render(request, 'accounts/profile.html', {'user': request.user})
