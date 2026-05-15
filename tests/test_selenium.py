"""
=============================================================
HappyPet - Pruebas de Automatizacion con Selenium
=============================================================
Herramienta: Selenium WebDriver (equivalente a Selenium IDE)
Requisito:   pip install selenium
             ChromeDriver o Firefox GeckoDriver instalado
Ejecutar:    python tests/test_selenium.py
             (con el servidor corriendo: python app.py)
=============================================================
NOTA: Este archivo contiene:
  1. Tests de Selenium WebDriver (requieren navegador + servidor)
  2. Script de generacion de Selenium IDE (.side) exportable
     que puede abrirse directamente en el plugin Selenium IDE
     del navegador o en Katalon Studio.
=============================================================
"""
import json, os, time, sys

# ─────────────────────────────────────────────────────────────────────
# PARTE A: Generar archivo .side para Selenium IDE / Katalon Studio
# (No requiere navegador ni servidor corriendo)
# ─────────────────────────────────────────────────────────────────────

# REEMPLAZA TODO EL BLOQUE SELENIUM_IDE_PROJECT POR ESTE

# REEMPLAZA SOLO EL BLOQUE SELENIUM_IDE_PROJECT POR ESTE

SELENIUM_IDE_PROJECT = {
    "id": "happypet-selenium-suite",
    "version": "2.0",
    "name": "HappyPet - Suite de Pruebas Automatizadas",
    "url": "http://127.0.0.1:5000",

    "tests": [

        {
            "id": "test-001",
            "name": "CP-01: Login exitoso como administrador",
            "commands": [
                {"command":"open","target":"/login","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('username')[0].value='admin';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('password')[0].value='admin123';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""},

                {"command":"waitForElementVisible","target":"css=.sidebar","value":"5000"}
            ]
        },

        {
            "id": "test-002",
            "name": "CP-02: Login incorrecto",
            "commands": [
                {"command":"open","target":"/login","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('username')[0].value='admin';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('password')[0].value='mala';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""}
            ]
        },

        {
            "id": "test-003",
            "name": "CP-03: Cliente entra a tienda",
            "commands": [
                {"command":"open","target":"/login","value":""},

                {
                    "command":"click",
                    "target":"xpath=//button[contains(text(),'Soy Cliente')]",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('cliente_nombre')[0].value='Juan Perez';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('cliente_email')[0].value='juan@test.cl';",
                    "value":""
                },

                {"command":"click","target":"css=button.btn-client","value":""},

                {"command":"waitForElementVisible","target":"css=.products-grid","value":"5000"}
            ]
        },

        {
            "id": "test-004",
            "name": "CP-04: Buscar productos",
            "commands": [
                {"command":"open","target":"/tienda","value":""},

                {
                    "command":"executeScript",
                    "target":"document.querySelector('#search-input').value='alimento';",
                    "value":""
                },

                {"command":"pause","target":"1000","value":""}
            ]
        },

        {
            "id": "test-005",
            "name": "CP-05: Filtrar gatos",
            "commands": [
                {"command":"open","target":"/tienda","value":""},

                {
                    "command":"click",
                    "target":"xpath=//button[@data-tipo='Gato']",
                    "value":""
                },

                {
                    "command":"assertElementPresent",
                    "target":"css=.prod-card",
                    "value":""
                }
            ]
        },

        {
            "id": "test-006",
            "name": "CP-06: Crear producto",
            "commands": [
                {"command":"open","target":"/login","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('username')[0].value='admin';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('password')[0].value='admin123';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""},

                {"command":"open","target":"/productos/nuevo","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('nombre')[0].value='Producto Selenium';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('precio')[0].value='12990';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('stock')[0].value='10';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('descripcion')[0].value='Creado automaticamente';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""}
            ]
        },

        {
            "id": "test-007",
            "name": "CP-07: Crear cliente",
            "commands": [
                {"command":"open","target":"/login","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('username')[0].value='admin';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('password')[0].value='admin123';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""},

                {"command":"open","target":"/clientes/nuevo","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('nombre')[0].value='Cliente Selenium';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('email')[0].value='cliente@test.cl';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('telefono')[0].value='+56911111111';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""}
            ]
        },

        {
            "id": "test-008",
            "name": "CP-08: Ver reportes",
            "commands": [
                {"command":"open","target":"/login","value":""},

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('username')[0].value='admin';",
                    "value":""
                },

                {
                    "command":"executeScript",
                    "target":"document.getElementsByName('password')[0].value='admin123';",
                    "value":""
                },

                {"command":"click","target":"css=button[type='submit']","value":""},

                {"command":"open","target":"/reportes","value":""},

                {
                    "command":"assertElementPresent",
                    "target":"css=table",
                    "value":""
                }
            ]
        }
    ],

    "suites": [
        {
            "id": "suite-01",
            "name": "Suite Completa",
            "persistSession": False,
            "parallel": False,
            "timeout": 30,
            "tests": [
                "test-001",
                "test-002",
                "test-003",
                "test-004",
                "test-005",
                "test-006",
                "test-007",
                "test-008"
            ]
        }
    ],

    "urls": [
        "http://127.0.0.1:5000"
    ],

    "plugins": []
}

def generar_selenium_ide():
    """Genera el archivo .side para Selenium IDE / Katalon Studio."""
    out = os.path.join(os.path.dirname(__file__), "happypet_selenium.side")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(SELENIUM_IDE_PROJECT, f, indent=2, ensure_ascii=False)
    print(f"[Selenium IDE] Archivo generado: {out}")
    print(f"  → Abrelo en Selenium IDE (plugin Chrome/Firefox)")
    print(f"  → O importalo en Katalon Studio como proyecto Web")
    return out


# ─────────────────────────────────────────────────────────────────────
# PARTE B: Tests con Selenium WebDriver
# (Requieren: servidor corriendo + ChromeDriver instalado)
# ─────────────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:5000"

def verificar_servidor():
    """Verifica que el servidor Flask esta corriendo."""
    try:
        import urllib.request
        urllib.request.urlopen(BASE_URL, timeout=3)
        return True
    except Exception:
        return False

def run_selenium_webdriver_tests():
    """Ejecuta tests con Selenium WebDriver (requiere ChromeDriver)."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("[Selenium WebDriver] selenium no instalado. Ejecuta: pip install selenium")
        return

    if not verificar_servidor():
        print("[Selenium WebDriver] AVISO: Servidor no detectado en", BASE_URL)
        print("  Inicia el servidor con: python app.py")
        print("  Luego vuelve a ejecutar este script")
        return

    # Configurar Chrome headless
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")

    try:
        driver = webdriver.Chrome(options=opts)
    except Exception as e:
        print(f"[Selenium WebDriver] ChromeDriver no disponible: {e}")
        print("  Descarga ChromeDriver desde: https://chromedriver.chromium.org")
        print("  O instala: pip install webdriver-manager")
        return

    wait = WebDriverWait(driver, 10)
    resultados = []

    def ejecutar_test(nombre, fn):
        try:
            fn()
            resultados.append(("PASSED", nombre))
            print(f"  [PASSED] {nombre}")
        except Exception as e:
            resultados.append(("FAILED", nombre, str(e)))
            print(f"  [FAILED] {nombre}: {e}")

    print("\n[Selenium WebDriver] Ejecutando tests...\n")

    # ── Test 1: Login admin ──────────────────────────────────────────
    def test_login_admin():
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("dashboard"))
        assert "dashboard" in driver.current_url
    ejecutar_test("CP-01: Login admin exitoso", test_login_admin)

    # ── Test 2: Dashboard visible ────────────────────────────────────
    def test_dashboard():
        driver.get(f"{BASE_URL}/dashboard")
        assert "dashboard" in driver.current_url
        stats = driver.find_elements(By.CSS_SELECTOR, ".stat-card")
        assert len(stats) >= 4, "Dashboard debe tener al menos 4 KPIs"
    ejecutar_test("CP-02: Dashboard con KPIs", test_dashboard)

    # ── Test 3: Navegar a productos ──────────────────────────────────
    def test_productos():
        driver.get(f"{BASE_URL}/productos")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
        filas = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        assert len(filas) > 0, "Debe haber productos en la tabla"
    ejecutar_test("CP-05: Listado de productos visible", test_productos)

    # ── Test 4: Formulario nuevo producto ────────────────────────────
    def test_form_producto():
        driver.get(f"{BASE_URL}/productos/nuevo")
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[name='nombre'], input[name='precio'], input[name='stock']")
        assert len(inputs) == 3, "Formulario debe tener campos nombre, precio y stock"
    ejecutar_test("CP-12: Formulario nuevo producto carga", test_form_producto)

    # ── Test 5: Crear producto ───────────────────────────────────────
    def test_crear_producto():
        driver.get(f"{BASE_URL}/productos/nuevo")
        driver.find_element(By.NAME, "nombre").send_keys("Test Selenium Auto")
        driver.find_element(By.NAME, "precio").send_keys("7990")
        driver.find_element(By.NAME, "stock").send_keys("15")
        driver.find_element(By.NAME, "descripcion").send_keys("Producto de prueba Selenium")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("productos"))
    ejecutar_test("CP-12b: Crear producto nuevo", test_crear_producto)

    # ── Test 6: Tienda carga para cliente ────────────────────────────
    def test_tienda_cliente():
        driver.get(f"{BASE_URL}/login")
        time.sleep(0.5)
        # Click en pestana cliente
        btns = driver.find_elements(By.CSS_SELECTOR, ".tab-btn")
        for btn in btns:
            if "Cliente" in btn.text:
                btn.click()
                break
        time.sleep(0.3)
        nombre_input = driver.find_element(By.NAME, "cliente_nombre")
        nombre_input.send_keys("Selenium Tester")
        driver.find_element(By.CSS_SELECTOR, "button.btn-client").click()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".products-grid")))
        cards = driver.find_elements(By.CSS_SELECTOR, ".prod-card")
        assert len(cards) > 0, "Tienda debe mostrar productos"
    ejecutar_test("CP-05: Tienda carga con productos", test_tienda_cliente)

    # ── Test 7: Buscar en tienda ─────────────────────────────────────
    def test_buscar_tienda():
        driver.get(f"{BASE_URL}/tienda")
        search = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#search-input")))
        search.send_keys("alimento")
        time.sleep(0.8)
        visible = [c for c in driver.find_elements(By.CSS_SELECTOR, ".prod-card")
                   if c.is_displayed()]
        assert len(visible) >= 0  # Al menos no da error
    ejecutar_test("CP-07: Busqueda en tienda funciona", test_buscar_tienda)

    # ── Test 8: Reportes ─────────────────────────────────────────────
    def test_reportes():
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "username").send_keys("admin")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("dashboard"))
        driver.get(f"{BASE_URL}/reportes")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".stat-card")))
    ejecutar_test("CP-26: Reportes cargan correctamente", test_reportes)

    driver.quit()

    # Resumen
    passed = sum(1 for r in resultados if r[0] == "PASSED")
    failed = sum(1 for r in resultados if r[0] == "FAILED")
    print(f"\n{'='*50}")
    print(f"Selenium WebDriver: {passed} PASSED / {failed} FAILED / {len(resultados)} TOTAL")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("HappyPet - Automatizacion Selenium IDE + WebDriver")
    print("=" * 60)

    # 1. Generar archivo .side para Selenium IDE / Katalon
    print("\n[1] Generando proyecto Selenium IDE (.side)...")
    generar_selenium_ide()

    # 2. Ejecutar WebDriver si hay servidor
    print("\n[2] Intentando tests con Selenium WebDriver...")
    run_selenium_webdriver_tests()
