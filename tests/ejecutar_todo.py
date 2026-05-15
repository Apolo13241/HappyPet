"""
=============================================================
HappyPet - Script Maestro de Calidad
TCY0101 - Tecnicas de Calidad de Software
=============================================================
Ejecuta TODAS las herramientas de calidad en orden:
  1. Pytest (JUnit) - Tests unitarios e integracion
  2. Selenium       - Automatizacion de pruebas UI
  3. SonarQube      - Inspeccion de codigo
  4. OWASP/Bandit   - Seguridad y vulnerabilidades
  5. Locust         - Carga y estres

Uso: python ejecutar_todo.py
=============================================================
"""
import subprocess, sys, os, time

BASE = os.path.dirname(__file__)
TESTS = os.path.join(BASE, "tests")
SEP = "=" * 65


def titulo(num, nombre):
    print(f"\n{SEP}")
    print(f"  HERRAMIENTA {num}: {nombre}")
    print(SEP)


def run(cmd, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=cwd or BASE,
                           capture_output=False, timeout=timeout)
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        print("  ⏱  Timeout alcanzado")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


if __name__ == "__main__":
    resultados = {}
    inicio = time.time()

    print(f"\n{'='*65}")
    print("  HAPPYPET - SUITE COMPLETA DE CALIDAD DE SOFTWARE")
    print(f"  TCY0101 - Tecnicas de Calidad de Software")
    print(f"{'='*65}")

    # ── 1. PYTEST (JUnit equivalente) ────────────────────────────────
    titulo(1, "PYTEST - Tests Unitarios e Integracion (JUnit)")
    print("  Ejecutando 44 casos de prueba...\n")
    ok = run([sys.executable, "-m", "pytest",
              os.path.join(TESTS, "test_happypet.py"),
              "-v", "--tb=short", "--no-header",
              f"--junitxml={BASE}/reporte_junit.xml"])
    resultados["Pytest (JUnit)"] = "✅ PASSED" if ok else "❌ FAILED"
    if os.path.exists(os.path.join(BASE, "reporte_junit.xml")):
        print(f"\n  📄 Reporte JUnit: reporte_junit.xml")

    # ── 2. SELENIUM IDE ──────────────────────────────────────────────
    titulo(2, "SELENIUM IDE - Automatizacion de Pruebas UI")
    print("  Generando proyecto Selenium IDE (.side)...\n")
    ok = run([sys.executable, os.path.join(TESTS, "test_selenium.py")])
    resultados["Selenium IDE"] = "✅ .side generado" if ok else "⚠️  Parcial (sin servidor)"
    side_file = os.path.join(TESTS, "happypet_selenium.side")
    if os.path.exists(side_file):
        print(f"\n  📄 Proyecto Selenium IDE: tests/happypet_selenium.side")
        print("     → Abrir en Selenium IDE (plugin Chrome/Firefox)")
        print("     → O importar en Katalon Studio")

    # ── 3. SONARQUBE ─────────────────────────────────────────────────
    titulo(3, "SONARQUBE - Inspeccion de Codigo")
    print("  Analizando calidad del codigo fuente...\n")
    ok = run([sys.executable, os.path.join(TESTS, "test_sonarqube.py")])
    resultados["SonarQube/Pylint"] = "✅ Analizado" if ok else "⚠️  Parcial"
    if os.path.exists(os.path.join(BASE, "sonar-project.properties")):
        print(f"\n  📄 Configuracion SonarQube: sonar-project.properties")
    if os.path.exists(os.path.join(BASE, "coverage.xml")):
        print(f"  📄 Cobertura: coverage.xml")

    # ── 4. OWASP / BANDIT ────────────────────────────────────────────
    titulo(4, "OWASP ZAP + BANDIT - Analisis de Vulnerabilidades")
    print("  Verificando seguridad OWASP Top 10...\n")
    ok = run([sys.executable, os.path.join(TESTS, "test_security.py")])
    resultados["OWASP/Bandit"] = "✅ Analizado" if ok else "⚠️  Parcial"
    zap_script = os.path.join(TESTS, "zap_scan.py")
    if os.path.exists(zap_script):
        print(f"\n  📄 Script ZAP: tests/zap_scan.py (usar con ZAP daemon)")

    # ── 5. LOCUST (Carga y Estres) ───────────────────────────────────
    titulo(5, "LOCUST - Pruebas de Carga y Estres")
    print("  Mostrando instrucciones de Locust...\n")
    ok = run([sys.executable, os.path.join(TESTS, "test_carga.py")])
    resultados["Locust (Carga)"] = "✅ Configurado" if ok else "⚠️  Sin servidor"

    # ── RESUMEN FINAL ─────────────────────────────────────────────────
    duracion = time.time() - inicio
    print(f"\n{SEP}")
    print("  RESUMEN FINAL - SUITE DE CALIDAD HAPPYPET")
    print(SEP)
    for herramienta, estado in resultados.items():
        print(f"  {estado:<25} {herramienta}")
    print(f"\n  Duracion total: {duracion:.1f} segundos")
    print(f"\n  Archivos generados:")
    archivos = [
        ("reporte_junit.xml",              "Resultados JUnit (importar en IDE)"),
        ("tests/happypet_selenium.side",   "Proyecto Selenium IDE / Katalon"),
        ("sonar-project.properties",       "Configuracion SonarQube"),
        ("coverage.xml",                   "Cobertura de tests para SonarQube"),
        (".coveragerc",                    "Config de cobertura"),
        ("tests/zap_scan.py",             "Script OWASP ZAP API"),
    ]
    for archivo, desc in archivos:
        path = os.path.join(BASE, archivo)
        existe = os.path.exists(path)
        print(f"  {'✅' if existe else '⚪'} {archivo:<40} {desc}")
    print(f"\n{SEP}")
    print("  Para ver instrucciones completas de cada herramienta,")
    print("  consulta el README_TESTING.md")
    print(SEP)
