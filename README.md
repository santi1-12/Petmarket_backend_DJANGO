# PetMarket - Tu tienda de mascotas online

![PetMarket Logo](static/img/logo.png)

PetMarket es una plataforma completa de comercio electrónico especializada en productos para mascotas. Desarrollada con Django y Django REST Framework, ofrece tanto una interfaz web moderna como una API REST completa para gestionar productos, usuarios, carrito de compras y pedidos.

## Características Principales

- **Interfaz Web Moderna**: Landing page atractiva con diseño responsive
- **Sistema de Autenticación**: Registro, login y gestión de usuarios con JWT
- **Carrito de Compras**: Funcionalidad completa de e-commerce
- **Gestión de Productos**: CRUD completo con categorías y filtros
- **Catálogo Web**: Vista de productos con búsqueda y paginación
- **API REST**: Endpoints completos para desarrollo de apps móviles
- **Múltiples Roles**: Clientes, empleados y administradores
- **Integración de Pagos**: Soporte para MercadoPago
- **Generación de PDFs**: Facturas y reportes automáticos

## Tecnologías Utilizadas

- **Backend**: Django 5.2 + Django REST Framework
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: JWT (SimpleJWT)
- **Frontend**: Bootstrap 5 + CSS personalizado
- **Pagos**: MercadoPago SDK
- **PDFs**: ReportLab
- **Despliegue**: Gunicorn + WhiteNoise

## Requisitos del Sistema

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

## Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd Petmarket_backend_DJANGO
```

### 2. Crear y activar entorno virtual
```bash
# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos
```bash
python manage.py migrate
```

### 5. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 6. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

¡Listo! Visita `http://127.0.0.1:8000` para ver PetMarket en acción.

## URLs Principales

### Interfaz Web
- **Inicio**: `http://127.0.0.1:8000/`
- **Catálogo**: `http://127.0.0.1:8000/productos/`
- **Carrito**: `http://127.0.0.1:8000/carrito/`
- **Admin**: `http://127.0.0.1:8000/admin/`

### API REST
- **Documentación API**: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **Base API**: `http://127.0.0.1:8000/api/`

## Documentación de la API

### Autenticación

#### Registro de Usuario
```http
POST /api/accounts/register/
Content-Type: application/json

{
    "username": "usuario123",
    "email": "usuario@ejemplo.com",
    "password": "contraseña_segura",
    "first_name": "Juan",
    "last_name": "Pérez"
}
```

#### Iniciar Sesión
```http
POST /api/accounts/login/
Content-Type: application/json

{
    "username": "usuario123",
    "password": "contraseña_segura"
}
```

**Respuesta:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com"
    }
}
```

#### Perfil de Usuario
```http
GET /api/accounts/profile/
Authorization: Bearer <access_token>
```

### Productos

#### Listar Productos
```http
GET /api/productos/
```

**Parámetros de consulta:**
- `search`: Buscar por nombre o descripción
- `categoria`: Filtrar por categoría
- `precio_min`, `precio_max`: Rango de precios
- `page`: Número de página

#### Obtener Producto Específico
```http
GET /api/productos/{id}/
```

#### Crear Producto (requiere permisos)
```http
POST /api/productos/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "nombre": "Alimento Premium para Perros",
    "descripcion": "Alimento balanceado de alta calidad",
    "precio": 25.99,
    "categoria": "alimentos",
    "stock": 100,
    "marca": "PetFood Pro"
}
```

### Carrito de Compras

#### Ver Carrito
```http
GET /api/carrito/
Authorization: Bearer <access_token>
```

#### Agregar al Carrito
```http
POST /api/carrito/agregar/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "producto_id": 1,
    "cantidad": 2
}
```

#### Actualizar Cantidad
```http
PUT /api/carrito/actualizar/{producto_id}/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "cantidad": 3
}
```

#### Eliminar del Carrito
```http
DELETE /api/carrito/eliminar/{producto_id}/
Authorization: Bearer <access_token>
```

#### Vaciar Carrito
```http
DELETE /api/carrito/limpiar/
Authorization: Bearer <access_token>
```

### Pedidos

#### Crear Pedido
```http
POST /api/pedidos/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "direccion_envio": "Calle Principal 123, Ciudad",
    "metodo_pago": "mercadopago"
}
```

#### Listar Pedidos del Usuario
```http
GET /api/pedidos/
Authorization: Bearer <access_token>
```

## Interfaz Web

### Características de la Landing Page
- **Hero Section**: Presentación atractiva con animaciones CSS
- **Sección de Características**: Productos premium, entrega rápida, garantía total
- **Estadísticas Animadas**: Contadores que se animan al hacer scroll
- **Testimoniales**: Reseñas de clientes satisfechos
- **Call to Action**: Invitación a registrarse y comprar

### Sistema de Autenticación Web
- **Modales de Login/Registro**: Diseño moderno con efectos de cristal
- **Validación en tiempo real**: JavaScript para mejor UX
- **Mensajes de feedback**: Notificaciones elegantes para el usuario

## Configuración Avanzada

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/petmarket

# Seguridad
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN=tu_access_token
MERCADOPAGO_PUBLIC_KEY=tu_public_key

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

### Configuración de PostgreSQL
```python
# En settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'petmarket',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Estructura del Proyecto

```
petmarket/
├── accounts/           # Gestión de usuarios y autenticación
├── productos/          # Catálogo de productos
├── carrito/           # Carrito de compras
├── pedidos/           # Gestión de pedidos
├── facturas/          # Facturación y reportes
├── clientes/          # Gestión de clientes
├── empleados/         # Gestión de empleados
├── static/            # Archivos estáticos (CSS, JS, imágenes)
├── templates/         # Plantillas HTML
├── media/             # Archivos subidos por usuarios
└── petmarket/         # Configuración principal
```

## Testing

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test accounts
python manage.py test productos

# Con coverage
coverage run manage.py test
coverage report
coverage html
```

### Datos de Prueba
```bash
# Cargar datos de ejemplo
python manage.py loaddata fixtures/productos.json
python manage.py loaddata fixtures/usuarios.json
```

## Despliegue en Producción

### Preparación
```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### Con Gunicorn
```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar en producción
gunicorn petmarket.wsgi:application --bind 0.0.0.0:8000
```

### Con Docker (opcional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "petmarket.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Contribuir

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Ejemplos de Uso con curl

### Registro y Login
```bash
# Registrar usuario
curl -X POST http://127.0.0.1:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@ejemplo.com",
    "password": "contraseña123",
    "first_name": "Usuario",
    "last_name": "Prueba"
  }'

# Login
curl -X POST http://127.0.0.1:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "contraseña123"
  }'
```

### Gestión de Productos
```bash
# Listar productos
curl -X GET http://127.0.0.1:8000/api/productos/

# Buscar productos
curl -X GET "http://127.0.0.1:8000/api/productos/?search=perro&categoria=alimentos"

# Agregar al carrito (requiere token)
curl -X POST http://127.0.0.1:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "producto_id": 1,
    "cantidad": 2
  }'
```

## Solución de Problemas Comunes

### Error de Migración
```bash
# Resetear migraciones
python manage.py migrate --fake-initial
```

### Error de Archivos Estáticos
```bash
# Verificar configuración
python manage.py findstatic css/site.css
```

### Error de JWT
```bash
# Verificar configuración de SimpleJWT en settings.py
```

---

**¡Gracias por usar PetMarket!**

*Desarrollado con cariño para amantes de las mascotas*

