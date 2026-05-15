"""
=============================================================
HappyPet - Pruebas de Carga y Estres con Locust
=============================================================
Herramienta: Locust (equivalente a JMeter)
Instalar:    pip install locust
Ejecutar:
  Modo Web UI:
    locust -f tests/test_carga.py --host=http://127.0.0.1:5000
    → Abrir http://localhost:8089 y configurar usuarios/tasa

  Modo Headless (sin UI):
    locust -f tests/test_carga.py --host=http://127.0.0.1:5000 \
           --headless -u 50 -r 10 --run-time 60s \
           --html reporte_carga.html

  Modo rapido de prueba:
    python tests/test_carga.py
=============================================================
"""
import os, sys, time, json, threading
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging


# ═══════════════════════════════════════════════════════════════════════
# ESCENARIOS DE USUARIOS
# ═══════════════════════════════════════════════════════════════════════

class UsuarioCliente(HttpUser):
    """
    Simula un cliente navegando la tienda.
    Peso: 70% del trafico (la mayoria son compradores).
    """
    wait_time = between(1, 4)   # Pausa realista entre acciones
    weight = 7

    def on_start(self):
        """Login como cliente al iniciar sesion."""
        self.client.post("/cliente-login", data={
            "cliente_nombre": "Cliente Locust Test",
            "cliente_email": "locust@test.cl"
        })

    @task(5)
    def ver_tienda(self):
        """Ver catalogo principal - accion mas frecuente."""
        self.client.get("/tienda", name="Tienda - Catalogo")

    @task(3)
    def ver_tienda_filtro_gato(self):
        """Tienda con filtro (simulado via JS, pero carga la misma pagina)."""
        self.client.get("/tienda", name="Tienda - Carga pagina")

    @task(2)
    def agregar_al_carrito(self):
        """Simular agregar producto al carrito (llamada POST JSON)."""
        self.client.post("/ventas/procesar",
            json={
                "cliente_nombre": "Cliente Locust",
                "cliente_email": "locust@test.cl",
                "items": [{"id": 1, "cantidad": 1}]
            },
            name="Venta - Procesar compra",
            catch_response=True
        )

    @task(1)
    def ver_login(self):
        """Ver pagina de login."""
        self.client.get("/login", name="Login - Pagina")


class UsuarioAdministrador(HttpUser):
    """
    Simula un administrador gestionando el sistema.
    Peso: 30% del trafico.
    """
    wait_time = between(2, 6)
    weight = 3

    def on_start(self):
        """Login como admin."""
        self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        })

    @task(4)
    def ver_dashboard(self):
        self.client.get("/dashboard", name="Admin - Dashboard")

    @task(3)
    def ver_productos(self):
        self.client.get("/productos", name="Admin - Productos")

    @task(2)
    def ver_ventas(self):
        self.client.get("/ventas", name="Admin - Ventas")

    @task(2)
    def ver_reportes(self):
        self.client.get("/reportes", name="Admin - Reportes")

    @task(1)
    def ver_clientes(self):
        self.client.get("/clientes", name="Admin - Clientes")

    @task(1)
    def buscar_productos(self):
        self.client.get("/productos?search=alimento", name="Admin - Buscar producto")

    @task(1)
    def filtrar_por_tipo(self):
        self.client.get("/productos?tipo=Gato", name="Admin - Filtrar productos")

    @task(1)
    def nueva_venta_form(self):
        self.client.get("/ventas/nueva", name="Admin - Form nueva venta")


class UsuarioConcurrente(HttpUser):
    """
    Usuario de prueba de estres - acciones rapidas y aleatorias.
    Para prueba de estres/pico de carga.
    """
    wait_time = between(0.1, 0.5)  # Muy rapido para estres
    weight = 0  # Solo activar en modo estres

    @task
    def carga_home(self):
        self.client.get("/", name="Estres - Home")

    @task
    def carga_login(self):
        self.client.get("/login", name="Estres - Login")

    @task
    def login_post(self):
        self.client.post("/login", data={
            "username": "admin", "password": "admin123"
        }, name="Estres - POST Login")


# ═══════════════════════════════════════════════════════════════════════
# EJECUTAR EN MODO PROGRAMATICO (sin UI)
# ═══════════════════════════════════════════════════════════════════════

def verificar_servidor(host="http://127.0.0.1:5000"):
    import urllib.request
    try:
        urllib.request.urlopen(host + "/login", timeout=3)
        return True
    except Exception:
        return False

def run_load_test_programatico():
    """
    Ejecuta prueba de carga directamente desde Python.
    No requiere UI ni CLI de Locust.
    """
    from locust.env import Environment
    from locust.stats import stats_printer, stats_history
    from locust.log import setup_logging
    import gevent

    HOST = "http://127.0.0.1:5000"

    print("\n" + "="*60)
    print("Locust - Prueba de Carga Programatica")
    print("="*60)

    if not verificar_servidor(HOST):
        print(f"\n⚠️  Servidor no detectado en {HOST}")
        print("   Inicia el servidor con: python app.py")
        print("   Luego vuelve a ejecutar: python tests/test_carga.py")
        return None

    setup_logging("WARNING")

    # Crear entorno
    env = Environment(user_classes=[UsuarioCliente, UsuarioAdministrador])
    env.create_local_runner()

    # Iniciar stats
    gevent.spawn(stats_printer(env.stats))
    gevent.spawn(stats_history, env.runner)

    USUARIOS    = 20    # Usuarios concurrentes
    TASA        = 5     # Usuarios nuevos por segundo
    DURACION    = 30    # Segundos de prueba

    print(f"\nConfiguracion:")
    print(f"  Usuarios:  {USUARIOS}")
    print(f"  Tasa:      {TASA} usuarios/seg")
    print(f"  Duracion:  {DURACION} segundos")
    print(f"  Host:      {HOST}\n")

    env.runner.start(USUARIOS, spawn_rate=TASA)
    gevent.sleep(DURACION)
    env.runner.stop()
    gevent.sleep(2)

    return env.stats

def imprimir_reporte(stats):
    """Imprime reporte de resultados de carga."""
    if not stats:
        return

    print("\n" + "="*60)
    print("REPORTE DE PRUEBA DE CARGA - HappyPet")
    print("="*60)

    total = stats.total
    print(f"\nResumen Global:")
    print(f"  Peticiones totales:  {total.num_requests}")
    print(f"  Peticiones fallidas: {total.num_failures}")
    print(f"  Tasa de error:       {total.fail_ratio*100:.1f}%")
    print(f"  Req/seg promedio:    {total.current_rps:.1f}")
    print(f"  Tiempo resp. medio:  {total.avg_response_time:.0f} ms")
    print(f"  Tiempo resp. 95p:    {total.get_response_time_percentile(0.95):.0f} ms")
    print(f"  Tiempo resp. 99p:    {total.get_response_time_percentile(0.99):.0f} ms")
    print(f"  Tiempo resp. max:    {total.max_response_time:.0f} ms")

    print(f"\nResultados por Endpoint:")
    print(f"  {'Endpoint':<35} {'Req':>6} {'Fail':>6} {'Avg(ms)':>8} {'95p(ms)':>8}")
    print(f"  {'-'*35} {'-'*6} {'-'*6} {'-'*8} {'-'*8}")

    for name, entry in sorted(stats.entries.items(),
                               key=lambda x: x[1].num_requests, reverse=True):
        if entry.num_requests == 0:
            continue
        n = name[1] if isinstance(name, tuple) else str(name)
        p95 = entry.get_response_time_percentile(0.95)
        print(f"  {n:<35} {entry.num_requests:>6} {entry.num_failures:>6} "
              f"{entry.avg_response_time:>8.0f} {p95:>8.0f}")

    # Criterios de aceptacion
    print(f"\nCriterios de Aceptacion:")
    criterios = [
        ("Tasa de error < 5%",          total.fail_ratio * 100 < 5),
        ("Tiempo resp. promedio < 2s",   total.avg_response_time < 2000),
        ("Tiempo resp. 95p < 5s",        (total.get_response_time_percentile(0.95) or 0) < 5000),
        ("Al menos 1 peticion exitosa",  total.num_requests - total.num_failures > 0),
    ]
    for desc, ok in criterios:
        print(f"  {'✅' if ok else '❌'} {desc}")


def mostrar_instrucciones():
    print("\n" + "="*60)
    print("INSTRUCCIONES - Pruebas de Carga Locust")
    print("="*60)
    print("""
1. MODO WEB UI (recomendado para presentacion):
   ───────────────────────────────────────────
   Con el servidor corriendo (python app.py):

   locust -f tests/test_carga.py --host=http://127.0.0.1:5000

   Abrir navegador en: http://localhost:8089
   Configurar:
     - Number of users: 50
     - Spawn rate: 10
     - Host: http://127.0.0.1:5000
   Click "Start Swarming"

2. MODO HEADLESS (automatico, genera HTML):
   ─────────────────────────────────────────
   locust -f tests/test_carga.py \\
     --host=http://127.0.0.1:5000 \\
     --headless -u 50 -r 10 \\
     --run-time 60s \\
     --html reporte_carga.html \\
     --csv resultados_carga

   Esto genera:
     - reporte_carga.html  (graficos interactivos)
     - resultados_carga_stats.csv
     - resultados_carga_failures.csv

3. ESCENARIOS INCLUIDOS:
   ──────────────────────
   UsuarioCliente (70%):  Navega tienda, agrega al carrito, compra
   UsuarioAdministrador (30%): Dashboard, CRUD, reportes
    """)


if __name__ == "__main__":
    mostrar_instrucciones()

    print("\n[Locust] Intentando prueba de carga programatica (30s)...")
    try:
        stats = run_load_test_programatico()
        imprimir_reporte(stats)
    except ImportError as e:
        print(f"Error de importacion: {e}")
        print("Instala con: pip install locust")
    except Exception as e:
        print(f"Error en prueba de carga: {e}")
        print("Usa el modo CLI: locust -f tests/test_carga.py --host=http://127.0.0.1:5000")
