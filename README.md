# 🐾 HappyPet - Sistema de Gestión de Tienda de Mascotas

Sistema web desarrollado en **Python + Flask** para gestión de ventas de productos para gatos y perros, con integración de **Webpay Plus de Transbank**.

---

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install flask requests
```

### 2. Ejecutar la aplicación
```bash
python app.py
```

### 3. Abrir en el navegador
```
http://localhost:5000
```

### 4. Credenciales de acceso (demo)
- **Usuario:** `admin`
- **Contraseña:** `admin123`

---

## 🏗️ Estructura del Proyecto

```
petshop/
├── app.py                  # Aplicación principal Flask
├── petshop.db              # Base de datos SQLite (se crea automáticamente)
├── requirements.txt        # Dependencias
├── REQUISITOS.md           # Tabla de requisitos funcionales y no funcionales
└── templates/
    ├── base.html           # Plantilla base con sidebar y navegación
    ├── login.html          # Pantalla de login
    ├── dashboard.html      # Panel principal con KPIs
    ├── productos.html      # Listado de productos (CRUD)
    ├── producto_form.html  # Formulario crear/editar producto
    ├── clientes.html       # Listado de clientes (CRUD)
    ├── cliente_form.html   # Formulario crear/editar cliente
    ├── nueva_venta.html    # Proceso de venta con carrito
    ├── ventas.html         # Historial de ventas
    ├── detalle_venta.html  # Detalle de una venta
    ├── pago_exitoso.html   # Confirmación de pago Webpay
    ├── reportes.html       # Reportes y estadísticas
    ├── usuarios.html       # Gestión de usuarios
    └── usuario_form.html   # Formulario nuevo usuario
```

---

## 💳 Integración Transbank Webpay

El sistema usa el **ambiente de integración** de Transbank (no requiere credenciales reales):

- **Endpoint:** `https://webpay3gint.transbank.cl`
- **Commerce Code:** `597055555532` (credenciales de prueba oficiales)
- **Flujo:**
  1. Sistema crea la venta y llama a la API de Webpay
  2. Usuario es redirigido al portal de pago de Transbank
  3. Tras el pago, Transbank retorna al sistema con el token
  4. Sistema confirma la transacción y actualiza el estado

> **Nota:** En entorno local sin acceso a internet, el sistema activa automáticamente un **modo demo** que simula el flujo completo.

---

## 📋 Módulos del Sistema

| Módulo | Descripción |
|--------|-------------|
| **Dashboard** | KPIs, ventas recientes, alertas de stock |
| **Productos** | CRUD completo con filtros por tipo de mascota |
| **Clientes** | CRUD completo de clientes |
| **Nueva Venta** | Carrito de compras + pago con Webpay |
| **Historial Ventas** | Listado con estados y detalles |
| **Reportes** | Top productos, ventas por mes, por tipo de mascota |
| **Usuarios** | Gestión de usuarios del sistema |

---