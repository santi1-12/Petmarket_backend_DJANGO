# 🛡️ Sistema de Validación de Precios en Facturas

## Resumen de Implementación

Se ha implementado un **sistema de validación de tres capas** para prevenir que productos con precios inválidos causen errores `InvalidOperation` en la base de datos:

---

## 📋 Capas de Validación

### 1️⃣ **Validación Frontend (JavaScript en tiempo real)**
**Ubicación:** `templates/admin_panel/factura_manual_form.html`

**Funcionalidad:**
- Cuando el usuario selecciona un producto en el formulario, JavaScript verifica inmediatamente si el precio es válido
- Si detecta un precio inválido (≤0, NaN, Infinity), muestra una **alerta visual** en la fila del producto
- El select del producto se resalta en **rojo** con un mensaje de advertencia
- Al intentar enviar el formulario, muestra un **alert** bloqueando el submit si hay precios inválidos

**Ejemplo de alerta mostrada:**
```
⚠️ Precio Inválido: El producto "PRODUCTO DE PRUEBA - PRECIO INVÁLIDO" 
tiene un precio inválido ($0). No podrás guardar esta factura hasta que 
corrijas el precio del producto en el catálogo.
```

**Código clave:**
```javascript
function validateProductPrice(event) {
  const productoId = parseInt(event.target.value);
  const producto = productoPrices[productoId];
  const precio = parseFloat(producto.precio);
  
  if (isNaN(precio) || precio <= 0 || !isFinite(precio)) {
    // Mostrar alerta y resaltar select en rojo
  }
}
```

---

### 2️⃣ **Validación Backend (Form Validation)**
**Ubicación:** `facturas/forms.py` - `FacturaItemForm.clean()`

**Funcionalidad:**
- Si el JavaScript falla o el usuario manipula el HTML, esta capa valida en el servidor
- Convierte `producto.precio` a `Decimal` y captura excepciones `InvalidOperation`
- Verifica que `precio > 0`
- Verifica que `subtotal` no exceda el límite de la base de datos (`9999999999.99`)
- Levanta `forms.ValidationError` con mensaje descriptivo que incluye el nombre del producto

**Código clave:**
```python
def clean(self):
    cleaned_data = super().clean()
    producto = cleaned_data.get('producto')
    cantidad = cleaned_data.get('cantidad')
    
    if producto and cantidad:
        try:
            precio = Decimal(str(producto.precio))
            if precio <= 0:
                raise forms.ValidationError(
                    f'El producto "{producto.nombre}" tiene un precio inválido...'
                )
            # Validar overflow
        except (InvalidOperation, ValueError, TypeError):
            raise forms.ValidationError(
                f'El producto "{producto.nombre}" tiene un precio con formato inválido...'
            )
```

---

### 3️⃣ **Display de Errores en Vista**
**Ubicación:** `empleados/views.py` - `factura_manual_create()`

**Funcionalidad:**
- Valida formularios por separado para capturar todos los errores
- Itera sobre errores de `factura_form` y `formset`
- Usa `messages.error()` para mostrar cada error en la UI de Django
- Formato de mensajes: `"Producto #1 - Error en precio: ..."` para claridad

**Código clave:**
```python
factura_valid = factura_form.is_valid()
formset_valid = formset.is_valid()

if not factura_valid:
    for field, errors in factura_form.errors.items():
        for error in errors:
            messages.error(request, f'Error en {field}: {error}')

if not formset_valid:
    for i, form in enumerate(formset):
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Producto #{i+1} - {error}')
```

---

## 🧪 Producto de Prueba Creado

Se ha creado un producto específicamente para demostrar la validación:

**Detalles:**
- **ID:** 13
- **Nombre:** PRODUCTO DE PRUEBA - PRECIO INVÁLIDO
- **Precio:** $0.00
- **Categoría:** TEST
- **Stock:** 100

---

## 🎯 Flujo de Validación Completo

```
Usuario selecciona producto con precio $0
    ↓
[1] JavaScript detecta precio inválido
    → Muestra alerta amarilla en la fila
    → Resalta select en rojo
    ↓
Usuario intenta guardar factura
    ↓
[2] JavaScript previene submit
    → Alert: "No se puede guardar la factura..."
    ↓
(Si JavaScript está deshabilitado)
    ↓
[3] Form.clean() valida en backend
    → Levanta ValidationError
    ↓
[4] Vista captura errores
    → messages.error() muestra mensaje al usuario
    ↓
Usuario ve error claro: "Producto #1 - El producto 'X' tiene un precio inválido ($0)..."
```

---

## 📊 Beneficios de Esta Arquitectura

✅ **UX Mejorado:** Usuario ve errores ANTES de enviar el formulario  
✅ **Seguridad:** Validación backend previene manipulación de HTML  
✅ **Claridad:** Mensajes específicos referencian el producto problemático  
✅ **Prevención:** No permite que datos inválidos lleguen a la base de datos  
✅ **Debugging:** Errores claros facilitan corrección de precios en catálogo  

---

## 🔧 Cómo Probar

1. **Iniciar servidor Django:**
   ```bash
   python manage.py runserver
   ```

2. **Ir a crear factura manual:**
   ```
   http://localhost:8000/empleados/admin/factura/manual/
   ```

3. **Seleccionar "PRODUCTO DE PRUEBA - PRECIO INVÁLIDO" (ID: 13)**

4. **Observar:**
   - Alerta amarilla aparece inmediatamente
   - Select se resalta en rojo
   - Al intentar guardar, aparece alert bloqueando el submit

5. **Intentar enviar con JavaScript deshabilitado:**
   - Backend captura el error
   - Muestra mensaje: "Producto #1 - El producto 'PRODUCTO DE PRUEBA - PRECIO INVÁLIDO' tiene un precio inválido ($0.00)..."

---

## 🔄 Mantenimiento Futuro

**Recomendaciones:**

1. **Validar precios al crear/editar productos:**
   - Agregar `clean_precio()` a `ProductoForm`
   - Prevenir que se guarden productos con precio ≤ 0

2. **Agregar validación a ProductoAdmin:**
   - En `productos/admin.py`, agregar validación de formulario

3. **Monitorear logs:**
   - Si aparecen errores `InvalidOperation`, ejecutar:
     ```bash
     python manage.py sanitize_facturas_decimals
     ```

4. **Considerar migración a PostgreSQL:**
   - PostgreSQL maneja `Decimal` nativamente sin conversiones de texto
   - Eliminaría la raíz del problema de conversión SQLite

---

## 📝 Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `facturas/forms.py` | Agregado `FacturaItemForm.clean()` con validación Decimal |
| `empleados/views.py` | Agregado loop de errores con `messages.error()` |
| `templates/admin_panel/factura_manual_form.html` | Agregado JavaScript de validación en tiempo real |
| `scripts/create_test_invalid_product.py` | Script para crear producto de prueba |

---

## 🎓 Contexto Técnico

**Problema original:**
- SQLite convierte `Decimal` a/desde texto
- Si el texto no es un decimal válido (ej: "", "NaN", "Inf"), lanza `InvalidOperation`
- Esto causaba crashes al ver o crear facturas

**Solución evolutiva:**
1. ✅ Sanitización de datos existentes (comando `sanitize_facturas_decimals`)
2. ✅ Quantización de decimales en `save()` (ROUND_HALF_UP)
3. ✅ Uso de `values_list()` para evitar cargar decimales corruptos
4. ✅ **Validación de formularios para prevenir entrada de datos inválidos** ← ESTA IMPLEMENTACIÓN

---

**Fecha:** 17 de Octubre, 2025  
**Estado:** ✅ Implementado y funcional  
**Producto de prueba ID:** 13
