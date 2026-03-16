# HappyPet - Sistema de Gestión de Tienda de Mascotas
## Tabla de Requisitos de Software

| ID | Tipo | Requisito | Descripción |
|----|------|-----------|-------------|
| RF-01 | Funcional | Login de acceso | El sistema debe permitir autenticación mediante usuario y contraseña con hash SHA-256 |
| RF-02 | Funcional | Menú principal (Dashboard) | El sistema debe mostrar un dashboard con KPIs: total ventas, ingresos, productos activos y clientes |
| RF-03 | Funcional | Gestión de Productos - Insertar | El sistema debe permitir crear nuevos productos con nombre, descripción, precio, stock, categoría y tipo de mascota |
| RF-04 | Funcional | Gestión de Productos - Consultar | El sistema debe permitir listar y buscar productos por nombre, tipo de mascota y categoría |
| RF-05 | Funcional | Gestión de Productos - Actualizar | El sistema debe permitir editar todos los atributos de un producto existente |
| RF-06 | Funcional | Gestión de Productos - Eliminar | El sistema debe permitir deshabilitar (borrado lógico) productos del catálogo |
| RF-07 | Funcional | Gestión de Clientes - Insertar | El sistema debe permitir registrar nuevos clientes con nombre, email, teléfono y tipo de mascota |
| RF-08 | Funcional | Gestión de Clientes - Consultar | El sistema debe permitir listar todos los clientes registrados |
| RF-09 | Funcional | Gestión de Clientes - Actualizar | El sistema debe permitir editar los datos de un cliente existente |
| RF-10 | Funcional | Gestión de Clientes - Eliminar | El sistema debe permitir eliminar clientes del sistema |
| RF-11 | Funcional | Proceso de Venta | El sistema debe permitir crear una venta seleccionando productos, cantidades y datos del cliente |
| RF-12 | Funcional | Carrito de compras | El sistema debe gestionar un carrito con productos, cantidades y subtotales en tiempo real |
| RF-13 | Funcional | Integración Webpay Transbank | El sistema debe procesar pagos mediante la API de Webpay Plus de Transbank |
| RF-14 | Funcional | Confirmación de pago | El sistema debe confirmar y actualizar el estado de la venta tras respuesta de Transbank |
| RF-15 | Funcional | Reporte de ventas | El sistema debe mostrar un reporte de ventas con top productos, ventas por mes y por tipo de mascota |
| RF-16 | Funcional | Alerta stock bajo | El sistema debe mostrar alertas cuando el stock de un producto sea menor o igual a 10 unidades |
| RF-17 | Funcional | Detalle de venta | El sistema debe permitir ver el detalle completo de cada venta (productos, cantidades, subtotales) |
| RF-18 | Funcional | Gestión de usuarios | El sistema debe permitir crear, listar y eliminar usuarios del sistema |
| RF-19 | Funcional | Filtro de productos por mascota | El sistema debe permitir filtrar el catálogo por tipo de mascota (gato, perro, ambos) |
| RF-20 | Funcional | Historial de ventas | El sistema debe mostrar el historial completo de ventas con su estado y monto |
| RNF-01 | No Funcional | Seguridad de contraseñas | Las contraseñas deben almacenarse con hash SHA-256, nunca en texto plano |
| RNF-02 | No Funcional | Control de sesión | El sistema debe requerir autenticación para acceder a cualquier módulo interno |
| RNF-03 | No Funcional | Persistencia de datos | El sistema debe usar SQLite como base de datos relacional con integridad referencial |
| RNF-04 | No Funcional | Disponibilidad | El sistema debe funcionar en cualquier sistema operativo compatible con Python 3.8+ |
| RNF-05 | No Funcional | Usabilidad | La interfaz debe ser intuitiva, responsiva y orientada a dispositivos de escritorio y móvil |
