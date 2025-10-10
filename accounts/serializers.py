from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.utils import timezone

# Lockout / rate-limit settings
MAX_LOGIN_ATTEMPTS = 5
FAILED_WINDOW_SECONDS = 15 * 60  # window to count failed attempts
LOCKOUT_SECONDS = 15 * 60  # lockout duration when max attempts reached

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # Use username-based keys to track failures. Preferably also include IP.
        username = data.get('username')
        request = self.context.get('request') if hasattr(self, 'context') else None
        ip = None
        if request is not None:
            xff = request.META.get('HTTP_X_FORWARDED_FOR')
            if xff:
                ip = xff.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

        fail_key = f"login_fail:{username}"
        lock_key = f"login_lock:{username}"

        # If account is locked, block immediately
        locked = cache.get(lock_key)
        if locked:
            raise serializers.ValidationError(f"Cuenta bloqueada por varios intentos. Intenta de nuevo más tarde.")

        user = authenticate(**data)
        if user:
            # Successful login: clear fail counter and return tokens
            try:
                cache.delete(fail_key)
                cache.delete(lock_key)
            except Exception:
                pass
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

        # Authentication failed: increment fail counter
        try:
            fails = cache.get(fail_key) or 0
            fails += 1
            cache.set(fail_key, fails, timeout=FAILED_WINDOW_SECONDS)
            if fails >= MAX_LOGIN_ATTEMPTS:
                cache.set(lock_key, True, timeout=LOCKOUT_SECONDS)
                cache.delete(fail_key)
                raise serializers.ValidationError(f"Demasiados intentos fallidos. Cuenta bloqueada por {int(LOCKOUT_SECONDS/60)} minutos.")
            else:
                remaining = MAX_LOGIN_ATTEMPTS - fails
                raise serializers.ValidationError(f"Credenciales inválidas. Te quedan {remaining} intentos antes del bloqueo.")
        except serializers.ValidationError:
            raise
        except Exception:
            # On cache errors or unexpected issues, fall back to generic message
            raise serializers.ValidationError("Credenciales inválidas")

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']
