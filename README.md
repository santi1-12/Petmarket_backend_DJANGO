Petmarket backend
=================

Quick notes about URL configuration changes done on Oct 7, 2025:

- Added `AUTH_USER_MODEL = 'accounts.CustomUser'` to `petmarket/settings.py`.
- Added `app_name` and named routes in `accounts/urls.py`.
- Made `productos` router explicit by registering under `productos/` with basename `producto`.
- Added placeholder `urls.py` files for `clientes`, `empleados`, and `pedidos` so `include()` calls don't error.

How to test locally

1. Activate the virtualenv:

	.\env\Scripts\Activate.ps1

2. Run Django system checks:

	.\env\Scripts\python.exe manage.py check

3. Start the dev server:

	.\env\Scripts\python.exe manage.py runserver

Then visit:

- http://127.0.0.1:8000/admin/
- http://127.0.0.1:8000/api/productos/productos/  (DRF router list endpoint)
- http://127.0.0.1:8000/api/accounts/login/ (and other account endpoints)

If you want any additional routes for `clientes`, `empleados` or `pedidos` I can scaffold viewsets and serializers next.
