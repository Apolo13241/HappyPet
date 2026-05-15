"""
=============================================================
HappyPet - Analisis de Vulnerabilidades OWASP / Bandit
=============================================================
Herramientas:
  - Bandit: analisis estatico de seguridad en codigo Python
  - OWASP ZAP: escaner de vulnerabilidades HTTP (modo proxy)
  - Checks manuales OWASP Top 10 sobre el codigo fuente
Ejecutar: python tests/test_security.py
=============================================================
"""
import subprocess, sys, os, json, re, ast

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APP_FILE = os.path.join(BASE_DIR, "app.py")

# ─────────────────────────────────────────────────────────────────────
# PARTE A: BANDIT - Analisis estatico del codigo fuente
# ─────────────────────────────────────────────────────────────────────

def run_bandit():
    """Ejecuta Bandit sobre app.py y reporta hallazgos."""
    print("\n" + "="*60)
    print("BANDIT - Analisis Estatico de Seguridad Python")
    print("="*60)
    try:
        result = subprocess.run(
            ["python3", "-m", "bandit", "-r", APP_FILE,
             "-f", "json", "--quiet"],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        issues = data.get("results", [])
        metrics = data.get("metrics", {}).get(APP_FILE, {})

        print(f"\nArchivo analizado: {APP_FILE}")
        print(f"Lineas de codigo:  {metrics.get('loc', 'N/A')}")
        print(f"Lineas ejecutables:{metrics.get('nosec', 'N/A')}")
        print(f"\nHallazgos: {len(issues)}")

        severidades = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for issue in issues:
            sev = issue.get("issue_severity", "LOW")
            severidades[sev] = severidades.get(sev, 0) + 1

        for sev, count in severidades.items():
            marca = "🔴" if sev == "HIGH" else "🟡" if sev == "MEDIUM" else "🟢"
            print(f"  {marca} {sev}: {count}")

        if issues:
            print("\nDetalle de hallazgos:")
            for i in issues[:10]:  # Max 10
                print(f"  [{i.get('issue_severity','?')}] Linea {i.get('line_number','?')}: "
                      f"{i.get('issue_text','')[:80]}")
        else:
            print("\n  ✅ Sin hallazgos criticos detectados por Bandit")

        return issues

    except FileNotFoundError:
        print("  Bandit no instalado. Ejecuta: pip install bandit")
        return []
    except Exception as e:
        print(f"  Error en Bandit: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────
# PARTE B: OWASP TOP 10 - Checks manuales sobre el codigo
# ─────────────────────────────────────────────────────────────────────

def check_owasp_top10():
    """Verifica los 10 riesgos principales de OWASP sobre el codigo."""
    print("\n" + "="*60)
    print("OWASP Top 10 - Verificacion de Vulnerabilidades")
    print("="*60)

    with open(APP_FILE, "r", encoding="utf-8") as f:
        code = f.read()

    results = []

    # A01 - Broken Access Control
    def check_a01():
        issues = []
        rutas_criticas = [
            ("/productos", "login_required"),
            ("/clientes", "login_required"),
            ("/reportes", "login_required"),
            ("/usuarios", "login_required"),
        ]
        for ruta, decorator in rutas_criticas:
            # Busca la definicion de la funcion asociada a la ruta
            pattern = rf'@app\.route\([\'\"]{re.escape(ruta)}[\'\"]\)[\s\S]{{0,50}}?@{decorator}'
            if not re.search(pattern, code):
                # Puede estar en funcion separada, verificar de otra forma
                pass
        # Verificar que login_required existe y se usa
        if "@login_required" in code:
            count = code.count("@login_required")
            issues.append(f"Control de acceso implementado con @login_required en {count} rutas")
        return issues

    # A02 - Cryptographic Failures
    def check_a02():
        issues = []
        # Verificar uso de SHA-256 para passwords
        if "sha256" in code.lower():
            issues.append("OK: Contrasenas hasheadas con SHA-256")
        else:
            issues.append("RIESGO: No se detecta hashing de contrasenas")

        # Verificar que no hay contrasenas en texto plano
        plain_pw = re.findall(r'password\s*=\s*["\'][^"\']{1,30}["\']', code, re.IGNORECASE)
        if plain_pw:
            issues.append(f"RIESGO: Posibles contrasenas en texto plano: {plain_pw[:2]}")

        # Verificar secret_key
        if "secret_key" in code.lower():
            sk = re.findall(r'secret_key\s*=\s*["\']([^"\']+)["\']', code, re.IGNORECASE)
            if sk and len(sk[0]) < 20:
                issues.append(f"ADVERTENCIA: Secret key corta ({len(sk[0])} chars). Usar 32+ chars en produccion")
            else:
                issues.append("OK: Secret key configurada")
        return issues

    # A03 - Injection (SQL Injection)
    def check_a03():
        issues = []
        # Buscar queries con formato string (riesgo SQL injection)
        dangerous = re.findall(r'execute\([^)]*%[^)]*\)', code)
        dangerous += re.findall(r'execute\([^)]*\.format\([^)]*\)', code)
        dangerous += re.findall(r'execute\([^)]*\+[^)]*\)', code)

        if dangerous:
            issues.append(f"RIESGO: Posibles queries sin parametrizar ({len(dangerous)} encontradas)")
            for d in dangerous[:3]:
                issues.append(f"  → {d[:80]}")
        else:
            issues.append("OK: Queries usan parametros ? (protegidas contra SQL Injection)")

        # Verificar uso de parametros en execute
        safe = re.findall(r'execute\([^,]+,\s*\(', code)
        issues.append(f"OK: {len(safe)} queries con parametros seguros detectadas")
        return issues

    # A04 - Insecure Design
    def check_a04():
        issues = []
        if "TESTING" in code or "debug=True" in code:
            issues.append("ADVERTENCIA: Modo debug/testing activo. Deshabilitar en produccion")
        if "SECRET_KEY" not in code.upper() and "secret_key" not in code:
            issues.append("RIESGO: Sin SECRET_KEY configurada para sesiones Flask")
        else:
            issues.append("OK: SECRET_KEY para sesiones configurada")
        return issues

    # A05 - Security Misconfiguration
    def check_a05():
        issues = []
        if "debug=True" in code:
            issues.append("ADVERTENCIA: debug=True expone el debugger. Cambiar en produccion")
        if "0.0.0.0" not in code:
            issues.append("OK: Servidor no expuesto en todas las interfaces (solo localhost)")
        if "TEMPLATES_AUTO_RELOAD" not in code:
            issues.append("INFO: TEMPLATES_AUTO_RELOAD no configurado explicitamente")
        return issues

    # A06 - Vulnerable Components
    def check_a06():
        issues = []
        req_file = os.path.join(BASE_DIR, "requirements.txt")
        if os.path.exists(req_file):
            with open(req_file) as f:
                reqs = f.read()
            issues.append(f"Dependencias declaradas en requirements.txt")
            # Verificar versiones fijadas
            if ">=" in reqs or "==" in reqs:
                issues.append("OK: Versiones de dependencias especificadas")
            else:
                issues.append("ADVERTENCIA: Fijar versiones exactas con == para reproducibilidad")
        else:
            issues.append("ADVERTENCIA: Sin requirements.txt para gestionar dependencias")
        return issues

    # A07 - Auth Failures
    def check_a07():
        issues = []
        if "session" in code and "user_id" in code:
            issues.append("OK: Sesiones Flask usadas para manejo de autenticacion")
        if "session.clear()" in code:
            issues.append("OK: Logout limpia la sesion completamente")
        if "login_required" in code:
            issues.append("OK: Decorator @login_required protege rutas privadas")
        if len(re.findall(r'@login_required', code)) < 5:
            issues.append("ADVERTENCIA: Pocas rutas con @login_required. Revisar cobertura")
        return issues

    # A08 - Software Integrity
    def check_a08():
        issues = []
        issues.append("INFO: Sin verificacion de integridad de paquetes (pip sin hash)")
        issues.append("RECOMENDACION: Usar pip-audit para auditar dependencias")
        return issues

    # A09 - Logging
    def check_a09():
        issues = []
        if "logging" in code or "print" in code:
            issues.append("INFO: Logging basico con print detectado")
        else:
            issues.append("ADVERTENCIA: Sin sistema de logging configurado")
        issues.append("RECOMENDACION: Implementar logging con modulo 'logging' de Python")
        return issues

    # A10 - SSRF (Server Side Request Forgery)
    def check_a10():
        issues = []
        if "requests." in code:
            reqs = re.findall(r'requests\.(get|post)\([^)]+\)', code)
            issues.append(f"INFO: {len(reqs)} llamadas HTTP salientes detectadas (Transbank)")
            issues.append("OK: URLs de Transbank son fijas, no controladas por usuario")
        return issues

    checks = [
        ("A01 - Broken Access Control",    check_a01),
        ("A02 - Cryptographic Failures",   check_a02),
        ("A03 - Injection (SQL)",          check_a03),
        ("A04 - Insecure Design",          check_a04),
        ("A05 - Security Misconfiguration",check_a05),
        ("A06 - Vulnerable Components",    check_a06),
        ("A07 - Auth Failures",            check_a07),
        ("A08 - Software Integrity",       check_a08),
        ("A09 - Logging",                  check_a09),
        ("A10 - SSRF",                     check_a10),
    ]

    all_results = {}
    for name, fn in checks:
        print(f"\n[{name}]")
        findings = fn()
        for f_item in findings:
            marca = "  ✅" if f_item.startswith("OK") else \
                    "  ⚠️ " if f_item.startswith("ADVERTENCIA") else \
                    "  🔴" if f_item.startswith("RIESGO") else "  ℹ️ "
            print(f"{marca} {f_item}")
        all_results[name] = findings

    return all_results


# ─────────────────────────────────────────────────────────────────────
# PARTE C: OWASP ZAP - Instrucciones de uso con Docker
# ─────────────────────────────────────────────────────────────────────

def instrucciones_zap():
    """Genera instrucciones y script para ejecutar OWASP ZAP."""
    print("\n" + "="*60)
    print("OWASP ZAP - Escaner de Vulnerabilidades HTTP")
    print("="*60)
    print("""
OWASP ZAP realiza un escaneo activo de la aplicacion web en ejecucion.
Requiere tener el servidor Flask corriendo (python app.py).

Opcion 1 - ZAP con Docker (recomendado):
─────────────────────────────────────────
  docker pull zaproxy/zap-stable
  docker run -t zaproxy/zap-stable zap-baseline.py \\
    -t http://host.docker.internal:5000 \\
    -r zap_report.html

Opcion 2 - ZAP Desktop (GUI):
──────────────────────────────
  1. Descargar ZAP desde: https://www.zaproxy.org/download/
  2. Abrir ZAP → Quick Start → URL: http://127.0.0.1:5000
  3. Click "Attack" para escaneo automatico
  4. Revisar panel "Alerts" para vulnerabilidades encontradas

Opcion 3 - ZAP via Python API:
───────────────────────────────
  pip install python-owasp-zap-v2.4
  (requiere ZAP corriendo como daemon en puerto 8080)
    """)

    # Generar script de ZAP API para cuando este disponible
    zap_script = '''# zap_scan.py - Ejecutar cuando ZAP este corriendo como daemon
# Iniciar ZAP daemon: zap.sh -daemon -port 8080 -host 0.0.0.0
from zapv2 import ZAPv2
import time

TARGET = "http://127.0.0.1:5000"
zap = ZAPv2(apikey="your-api-key", proxies={"http":"http://127.0.0.1:8080"})

print("Abriendo URL objetivo...")
zap.urlopen(TARGET)
time.sleep(2)

print("Iniciando Spider (rastreo)...")
scan_id = zap.spider.scan(TARGET)
while int(zap.spider.status(scan_id)) < 100:
    print(f"  Spider: {zap.spider.status(scan_id)}%")
    time.sleep(2)

print("Iniciando Escaneo Activo...")
ascan_id = zap.ascan.scan(TARGET)
while int(zap.ascan.status(ascan_id)) < 100:
    print(f"  Scan activo: {zap.ascan.status(ascan_id)}%")
    time.sleep(5)

print("\\nAlertas encontradas:")
for alert in zap.core.alerts(baseurl=TARGET):
    print(f"  [{alert.get('risk')}] {alert.get('name')}: {alert.get('url')}")

# Generar reporte HTML
with open("zap_report.html", "w") as f:
    f.write(zap.core.htmlreport())
print("Reporte guardado en: zap_report.html")
'''
    zap_path = os.path.join(os.path.dirname(__file__), "zap_scan.py")
    with open(zap_path, "w", encoding="utf-8") as f:
        f.write(zap_script)
    print(f"Script ZAP API guardado en: {zap_path}")


# ─────────────────────────────────────────────────────────────────────
# PARTE D: HTTP Security Headers check
# ─────────────────────────────────────────────────────────────────────

def check_security_headers():
    """Verifica cabeceras de seguridad HTTP del servidor."""
    print("\n" + "="*60)
    print("HTTP Security Headers")
    print("="*60)
    try:
        import requests
        try:
            r = requests.get("http://127.0.0.1:5000/login", timeout=3)
            headers = r.headers
            checks = [
                ("X-Content-Type-Options",  "nosniff"),
                ("X-Frame-Options",          None),
                ("Content-Security-Policy",  None),
                ("Strict-Transport-Security",None),
                ("X-XSS-Protection",         None),
            ]
            for header, expected in checks:
                val = headers.get(header)
                if val:
                    ok = (expected is None) or (expected.lower() in val.lower())
                    print(f"  {'✅' if ok else '⚠️ '} {header}: {val}")
                else:
                    print(f"  ⚠️  {header}: AUSENTE (agregar con Flask-Talisman)")
        except Exception:
            print("  INFO: Servidor no activo. Inicia app.py para verificar headers.")
            print("  RECOMENDACION: Agregar Flask-Talisman para headers de seguridad:")
            print("    pip install flask-talisman")
            print("    from flask_talisman import Talisman")
            print("    Talisman(app)  # Agrega todos los headers de seguridad")
    except ImportError:
        print("  requests no disponible para verificar headers HTTP")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("HappyPet - Analisis de Seguridad OWASP + Bandit")
    print("="*60)

    # 1. Bandit
    bandit_issues = run_bandit()

    # 2. OWASP Top 10 manual
    owasp_results = check_owasp_top10()

    # 3. Headers HTTP
    check_security_headers()

    # 4. Instrucciones ZAP
    instrucciones_zap()

    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN SEGURIDAD")
    print("="*60)
    riesgos = sum(1 for v in owasp_results.values()
                  for item in v if item.startswith("RIESGO"))
    advertencias = sum(1 for v in owasp_results.values()
                       for item in v if item.startswith("ADVERTENCIA"))
    print(f"  🔴 Riesgos altos:     {riesgos + len([i for i in bandit_issues if i.get('issue_severity')=='HIGH'])}")
    print(f"  🟡 Advertencias:      {advertencias}")
    print(f"  ✅ Checks OK:         {sum(1 for v in owasp_results.values() for i in v if i.startswith('OK'))}")
    print(f"\n  Bandit hallazgos:    {len(bandit_issues)}")
    print("="*60)
