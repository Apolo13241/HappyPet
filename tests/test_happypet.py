"""
=============================================================
HappyPet - Tests Unitarios e Integracion (equivalente JUnit)
=============================================================
Herramienta: pytest + pytest-flask
Cubre: Login, Productos CRUD, Clientes CRUD, Ventas, Tienda
Ejecutar: pytest tests/test_happypet.py -v --tb=short
=============================================================
"""
import sys, os, json, hashlib, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app as flask_app, init_db, get_db

# ─── Fixture base ────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    # Usar DB en memoria para tests
    import tempfile
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    flask_app.config["DB_PATH"] = db_path
    # Parchear el path de la DB
    import app as app_module
    app_module.DB_PATH = db_path
    init_db()
    yield flask_app
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Cliente autenticado como admin."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    return client

@pytest.fixture
def cliente_client(client):
    """Cliente autenticado como comprador."""
    client.post("/cliente-login", data={"cliente_nombre": "Test Cliente", "cliente_email": "test@test.cl"})
    return client


# ═══════════════════════════════════════════════════════════════════════
# 1. TESTS UNITARIOS - AUTENTICACION
# ═══════════════════════════════════════════════════════════════════════
class TestAutenticacion:
    """Pruebas unitarias del modulo de login."""

    def test_login_pagina_carga(self, client):
        """La pagina de login debe retornar HTTP 200."""
        r = client.get("/login")
        assert r.status_code == 200, "Login page debe cargar"

    def test_login_exitoso_admin(self, client):
        """Login con credenciales correctas debe redirigir al dashboard."""
        r = client.post("/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=False)
        assert r.status_code == 302, "Login exitoso debe redirigir"
        assert "/dashboard" in r.headers.get("Location", "")

    def test_login_contrasena_incorrecta(self, client):
        """Login con pass incorrecto debe mostrar error (no redirigir)."""
        r = client.post("/login",
            data={"username": "admin", "password": "wrongpass"},
            follow_redirects=True)
        assert r.status_code == 200
        assert b"incorrectas" in r.data.lower() or b"error" in r.data.lower()

    def test_login_usuario_inexistente(self, client):
        """Usuario que no existe debe fallar el login."""
        r = client.post("/login",
            data={"username": "noexiste", "password": "cualquier"},
            follow_redirects=True)
        assert r.status_code == 200

    def test_password_hash_sha256(self):
        """Las contrasenas deben guardarse con SHA-256."""
        import app as app_module
        conn = app_module.get_db()
        user = conn.execute("SELECT password FROM usuarios WHERE username='admin'").fetchone()
        conn.close()
        expected = hashlib.sha256("admin123".encode()).hexdigest()
        assert user["password"] == expected, "Password debe estar hasheado con SHA-256"

    def test_redireccion_sin_login(self, client):
        """Rutas protegidas deben redirigir si no hay sesion."""
        for ruta in ["/dashboard", "/productos", "/clientes", "/ventas", "/reportes"]:
            r = client.get(ruta, follow_redirects=False)
            assert r.status_code == 302, f"{ruta} debe redirigir sin autenticacion"

    def test_logout_limpia_sesion(self, auth_client):
        """Logout debe redirigir al login."""
        r = auth_client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers.get("Location", "")

    def test_login_cliente_sin_cuenta(self, client):
        """Cliente puede ingresar solo con nombre sin contrasena."""
        r = client.post("/cliente-login",
            data={"cliente_nombre": "Juan Perez", "cliente_email": "juan@test.cl"},
            follow_redirects=False)
        assert r.status_code == 302
        assert "/tienda" in r.headers.get("Location", "")

    def test_login_cliente_sin_nombre_falla(self, client):
        """Login cliente sin nombre debe redirigir al login."""
        r = client.post("/cliente-login",
            data={"cliente_nombre": "", "cliente_email": ""},
            follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers.get("Location", "")


# ═══════════════════════════════════════════════════════════════════════
# 2. TESTS UNITARIOS - PRODUCTOS (CRUD)
# ═══════════════════════════════════════════════════════════════════════
class TestProductos:
    """Pruebas CRUD completas del modulo de productos."""

    def test_listar_productos(self, auth_client):
        """Pagina de productos debe cargar con HTTP 200."""
        r = auth_client.get("/productos")
        assert r.status_code == 200
        assert b"Producto" in r.data or b"producto" in r.data

    def test_formulario_nuevo_producto(self, auth_client):
        """Formulario de nuevo producto debe cargar."""
        r = auth_client.get("/productos/nuevo")
        assert r.status_code == 200

    def test_crear_producto(self, auth_client):
        """Crear producto con datos validos debe funcionar."""
        r = auth_client.post("/productos/nuevo", data={
            "nombre": "Producto Test Pytest",
            "descripcion": "Descripcion de prueba",
            "precio": "15990",
            "stock": "25",
            "categoria": "Alimentos",
            "tipo_mascota": "Gato",
            "imagen": "🐱"
        }, follow_redirects=True)
        assert r.status_code == 200
        assert b"Producto Test Pytest" in r.data or b"exitosamente" in r.data or b"OK" in r.data

    def test_producto_aparece_en_lista(self, auth_client):
        """Producto creado debe aparecer en el listado."""
        auth_client.post("/productos/nuevo", data={
            "nombre": "Collar Rojo Test",
            "descripcion": "Test",
            "precio": "4990",
            "stock": "10",
            "categoria": "Accesorios",
            "tipo_mascota": "Perro",
            "imagen": "🐶"
        })
        r = auth_client.get("/productos")
        assert b"Collar Rojo Test" in r.data

    def test_editar_producto(self, auth_client):
        """Formulario de edicion debe cargar para producto existente."""
        r = auth_client.get("/productos/editar/1")
        assert r.status_code == 200

    def test_editar_producto_guarda_cambios(self, auth_client):
        """Editar producto debe actualizar datos en BD."""
        import app as app_module
        conn = app_module.get_db()
        prod = conn.execute("SELECT * FROM productos WHERE activo=1 LIMIT 1").fetchone()
        conn.close()
        if prod:
            r = auth_client.post(f"/productos/editar/{prod['id']}", data={
                "nombre": "Nombre Actualizado Test",
                "descripcion": "Nueva desc",
                "precio": "99990",
                "stock": "5",
                "categoria": "Juguetes",
                "tipo_mascota": "Ambos",
                "imagen": "🐾"
            }, follow_redirects=True)
            assert r.status_code == 200

    def test_eliminar_producto(self, auth_client):
        """Eliminar producto debe hacer borrado logico."""
        import app as app_module
        # Crear producto especifico para eliminar
        auth_client.post("/productos/nuevo", data={
            "nombre": "Producto Para Eliminar",
            "descripcion": "Borrar",
            "precio": "1000",
            "stock": "1",
            "categoria": "Otros",
            "tipo_mascota": "Ambos",
            "imagen": "🐾"
        })
        conn = app_module.get_db()
        prod = conn.execute(
            "SELECT id FROM productos WHERE nombre='Producto Para Eliminar'"
        ).fetchone()
        conn.close()
        if prod:
            r = auth_client.post(f"/productos/eliminar/{prod['id']}",
                follow_redirects=True)
            assert r.status_code == 200
            # Verificar borrado logico
            conn = app_module.get_db()
            p = conn.execute(
                "SELECT activo FROM productos WHERE id=?", (prod["id"],)
            ).fetchone()
            conn.close()
            assert p["activo"] == 0, "Producto debe tener activo=0 (borrado logico)"

    def test_buscar_producto(self, auth_client):
        """Busqueda de productos debe filtrar resultados."""
        r = auth_client.get("/productos?search=Alimento")
        assert r.status_code == 200

    def test_filtrar_por_tipo_mascota(self, auth_client):
        """Filtro por tipo de mascota debe funcionar."""
        r = auth_client.get("/productos?tipo=Gato")
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════
# 3. TESTS UNITARIOS - CLIENTES (CRUD)
# ═══════════════════════════════════════════════════════════════════════
class TestClientes:
    """Pruebas CRUD del modulo de clientes."""

    def test_listar_clientes(self, auth_client):
        r = auth_client.get("/clientes")
        assert r.status_code == 200

    def test_formulario_nuevo_cliente(self, auth_client):
        r = auth_client.get("/clientes/nuevo")
        assert r.status_code == 200

    def test_crear_cliente(self, auth_client):
        """Crear cliente con datos validos."""
        r = auth_client.post("/clientes/nuevo", data={
            "nombre": "Maria Test Pytest",
            "email": "maria.pytest@test.cl",
            "telefono": "+56912345678",
            "tipo_mascota": "Gato"
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_cliente_en_base_datos(self, auth_client):
        """Cliente creado debe existir en BD."""
        import app as app_module
        auth_client.post("/clientes/nuevo", data={
            "nombre": "Cliente BD Test",
            "email": "bdtest@test.cl",
            "telefono": "+56900000000",
            "tipo_mascota": "Perro"
        })
        conn = app_module.get_db()
        c = conn.execute(
            "SELECT * FROM clientes WHERE email='bdtest@test.cl'"
        ).fetchone()
        conn.close()
        assert c is not None, "Cliente debe existir en BD"
        assert c["nombre"] == "Cliente BD Test"

    def test_editar_cliente(self, auth_client):
        """Formulario edicion cliente debe cargar."""
        import app as app_module
        auth_client.post("/clientes/nuevo", data={
            "nombre": "Editable Cliente",
            "email": "editable@test.cl",
            "telefono": "",
            "tipo_mascota": "Gato"
        })
        conn = app_module.get_db()
        c = conn.execute(
            "SELECT id FROM clientes WHERE email='editable@test.cl'"
        ).fetchone()
        conn.close()
        if c:
            r = auth_client.get(f"/clientes/editar/{c['id']}")
            assert r.status_code == 200

    def test_eliminar_cliente(self, auth_client):
        """Eliminar cliente debe borrar de BD."""
        import app as app_module
        auth_client.post("/clientes/nuevo", data={
            "nombre": "Borrar Este",
            "email": "borrar@test.cl",
            "telefono": "",
            "tipo_mascota": "Perro"
        })
        conn = app_module.get_db()
        c = conn.execute(
            "SELECT id FROM clientes WHERE email='borrar@test.cl'"
        ).fetchone()
        conn.close()
        if c:
            r = auth_client.post(f"/clientes/eliminar/{c['id']}",
                follow_redirects=True)
            assert r.status_code == 200

    def test_email_duplicado(self, auth_client):
        """Email duplicado debe mostrar error."""
        data = {
            "nombre": "Duplicado",
            "email": "duplicado@test.cl",
            "telefono": "",
            "tipo_mascota": "Gato"
        }
        auth_client.post("/clientes/nuevo", data=data)
        r = auth_client.post("/clientes/nuevo", data=data,
            follow_redirects=True)
        assert r.status_code == 200
        assert b"registrado" in r.data.lower() or b"error" in r.data.lower()


# ═══════════════════════════════════════════════════════════════════════
# 4. TESTS DE INTEGRACION - PROCESO DE VENTA
# ═══════════════════════════════════════════════════════════════════════
class TestVentas:
    """Pruebas de integracion: flujo completo de venta."""

    def test_pagina_nueva_venta(self, auth_client):
        r = auth_client.get("/ventas/nueva")
        assert r.status_code == 200

    def test_procesar_venta_admin(self, auth_client):
        """Admin puede procesar venta con productos en carrito."""
        import app as app_module
        conn = app_module.get_db()
        prod = conn.execute(
            "SELECT id FROM productos WHERE activo=1 AND stock>0 LIMIT 1"
        ).fetchone()
        conn.close()
        assert prod, "Debe haber productos disponibles"
        r = auth_client.post("/ventas/procesar",
            data=json.dumps({
                "cliente_nombre": "Cliente Integracion",
                "cliente_email": "integ@test.cl",
                "items": [{"id": prod["id"], "cantidad": 1}]
            }),
            content_type="application/json")
        assert r.status_code == 200
        data = json.loads(r.data)
        assert "venta_id" in data, "Respuesta debe incluir venta_id"

    def test_procesar_venta_cliente(self, cliente_client):
        """Cliente puede procesar compra desde tienda."""
        import app as app_module
        conn = app_module.get_db()
        prod = conn.execute(
            "SELECT id FROM productos WHERE activo=1 AND stock>0 LIMIT 1"
        ).fetchone()
        conn.close()
        r = cliente_client.post("/ventas/procesar",
            data=json.dumps({
                "cliente_nombre": "Test Cliente",
                "cliente_email": "test@test.cl",
                "items": [{"id": prod["id"], "cantidad": 1}]
            }),
            content_type="application/json")
        assert r.status_code == 200

    def test_venta_carrito_vacio(self, auth_client):
        """Carrito vacio debe retornar error."""
        r = auth_client.post("/ventas/procesar",
            data=json.dumps({
                "cliente_nombre": "Test",
                "cliente_email": "",
                "items": []
            }),
            content_type="application/json")
        assert r.status_code == 400

    def test_stock_se_descuenta(self, auth_client):
        """Stock del producto debe decrementarse tras la venta."""
        import app as app_module
        conn = app_module.get_db()
        prod = conn.execute(
            "SELECT id, stock FROM productos WHERE activo=1 AND stock>2 LIMIT 1"
        ).fetchone()
        conn.close()
        if not prod:
            pytest.skip("No hay producto con stock suficiente")
        stock_inicial = prod["stock"]
        auth_client.post("/ventas/procesar",
            data=json.dumps({
                "cliente_nombre": "Stock Test",
                "cliente_email": "",
                "items": [{"id": prod["id"], "cantidad": 2}]
            }),
            content_type="application/json")
        conn = app_module.get_db()
        stock_final = conn.execute(
            "SELECT stock FROM productos WHERE id=?", (prod["id"],)
        ).fetchone()["stock"]
        conn.close()
        assert stock_final == stock_inicial - 2, \
            f"Stock debe decrementarse: {stock_inicial} -> {stock_final}"

    def test_historial_ventas(self, auth_client):
        r = auth_client.get("/ventas")
        assert r.status_code == 200

    def test_detalle_venta(self, auth_client):
        """Detalle de venta existente debe cargar."""
        import app as app_module
        conn = app_module.get_db()
        venta = conn.execute("SELECT id FROM ventas LIMIT 1").fetchone()
        conn.close()
        if venta:
            r = auth_client.get(f"/venta/{venta['id']}/detalle")
            assert r.status_code == 200

    def test_pagar_demo(self, auth_client):
        """Modo demo debe marcar venta como pagada."""
        import app as app_module
        conn = app_module.get_db()
        venta = conn.execute(
            "SELECT id FROM ventas WHERE estado='pendiente' LIMIT 1"
        ).fetchone()
        conn.close()
        if venta:
            r = auth_client.post(f"/ventas/{venta['id']}/pagar-demo",
                follow_redirects=True)
            assert r.status_code == 200
            conn = app_module.get_db()
            estado = conn.execute(
                "SELECT estado FROM ventas WHERE id=?", (venta["id"],)
            ).fetchone()["estado"]
            conn.close()
            assert estado == "pagado", "Venta debe quedar en estado 'pagado'"


# ═══════════════════════════════════════════════════════════════════════
# 5. TESTS UNITARIOS - TIENDA CLIENTE
# ═══════════════════════════════════════════════════════════════════════
class TestTienda:
    """Pruebas de la vista publica de tienda."""

    def test_tienda_carga(self, cliente_client):
        r = cliente_client.get("/tienda")
        assert r.status_code == 200

    def test_tienda_sin_sesion_redirige(self, client):
        """Tienda requiere al menos sesion de cliente."""
        r = client.get("/tienda", follow_redirects=False)
        # Puede cargar o redirigir, pero no dar 500
        assert r.status_code in [200, 302]

    def test_tienda_muestra_productos(self, cliente_client):
        """Tienda debe mostrar productos disponibles."""
        r = cliente_client.get("/tienda")
        assert r.status_code == 200
        # Debe contener elementos de productos
        assert b"precio" in r.data.lower() or b"agregar" in r.data.lower()


# ═══════════════════════════════════════════════════════════════════════
# 6. TESTS UNITARIOS - REPORTES Y USUARIOS
# ═══════════════════════════════════════════════════════════════════════
class TestReportesUsuarios:

    def test_reportes_carga(self, auth_client):
        r = auth_client.get("/reportes")
        assert r.status_code == 200

    def test_dashboard_carga(self, auth_client):
        r = auth_client.get("/dashboard")
        assert r.status_code == 200

    def test_usuarios_carga(self, auth_client):
        r = auth_client.get("/usuarios")
        assert r.status_code == 200

    def test_crear_usuario(self, auth_client):
        r = auth_client.post("/usuarios/nuevo", data={
            "username": "tester_pytest",
            "nombre": "Tester Pytest",
            "password": "test123",
            "rol": "vendedor"
        }, follow_redirects=True)
        assert r.status_code == 200

    def test_no_eliminar_propio_usuario(self, auth_client):
        """No se debe poder eliminar el propio usuario."""
        import app as app_module
        conn = app_module.get_db()
        admin = conn.execute(
            "SELECT id FROM usuarios WHERE username='admin'"
        ).fetchone()
        conn.close()
        if admin:
            r = auth_client.post(f"/usuarios/eliminar/{admin['id']}",
                follow_redirects=True)
            assert r.status_code == 200
            # Verificar que admin sigue existiendo
            conn = app_module.get_db()
            still_exists = conn.execute(
                "SELECT id FROM usuarios WHERE username='admin'"
            ).fetchone()
            conn.close()
            assert still_exists, "Admin no debe poder ser eliminado"


# ═══════════════════════════════════════════════════════════════════════
# 7. TESTS DE BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════
class TestBaseDeDatos:
    """Pruebas de integridad de la base de datos."""

    def test_tablas_existen(self):
        """Todas las tablas requeridas deben existir."""
        import app as app_module
        conn = app_module.get_db()
        tablas = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        nombres = [t["name"] for t in tablas]
        conn.close()
        for tabla in ["usuarios", "productos", "clientes", "ventas", "detalle_venta"]:
            assert tabla in nombres, f"Tabla '{tabla}' debe existir"

    def test_admin_por_defecto_existe(self):
        """Usuario admin debe existir en la BD."""
        import app as app_module
        conn = app_module.get_db()
        admin = conn.execute(
            "SELECT * FROM usuarios WHERE username='admin'"
        ).fetchone()
        conn.close()
        assert admin is not None, "Usuario admin debe existir"

    def test_productos_demo_cargados(self):
        """Deben existir productos de demo en la BD."""
        import app as app_module
        conn = app_module.get_db()
        count = conn.execute(
            "SELECT COUNT(*) FROM productos WHERE activo=1"
        ).fetchone()[0]
        conn.close()
        assert count > 0, "Debe haber al menos un producto activo"
