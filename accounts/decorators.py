from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied()
            if getattr(request.user, 'role', None) not in allowed_roles:
                raise PermissionDenied()
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
