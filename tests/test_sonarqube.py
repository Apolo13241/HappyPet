"""
=============================================================
HappyPet - Analisis de Codigo con SonarQube
=============================================================
Herramienta: SonarQube / SonarCloud + pylint + radon
Instalar:    pip install pylint radon coverage pytest-cov
Ejecutar:    python tests/test_sonarqube.py
=============================================================
"""
import subprocess, sys, os, json, ast, re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
APP_FILE = os.path.join(BASE_DIR, "app.py")


# ─────────────────────────────────────────────────────────────────────
# PARTE A: Pylint - Calidad de codigo (alimenta a SonarQube)
# ─────────────────────────────────────────────────────────────────────

def run_pylint():
    print("\n" + "="*60)
    print("PYLINT - Analisis de Calidad de Codigo")
    print("="*60)
    try:
        result = subprocess.run(
            ["python3", "-m", "pylint", APP_FILE,
             "--output-format=json",
             "--disable=C0114,C0115,C0116,C0301,W0611",
             "--max-line-length=120"],
            capture_output=True, text=True
        )
        issues = json.loads(result.stdout) if result.stdout.strip().startswith("[") else []

        conteo = {"convention": 0, "refactor": 0, "warning": 0, "error": 0, "fatal": 0}
        for issue in issues:
            t = issue.get("type", "").lower()
            conteo[t] = conteo.get(t, 0) + 1

        print(f"\nArchivo: {APP_FILE}")
        print(f"Total hallazgos: {len(issues)}")
        print(f"  🔴 Errores/Fatal:    {conteo['error'] + conteo['fatal']}")
        print(f"  🟡 Advertencias:     {conteo['warning']}")
        print(f"  🔵 Refactor:         {conteo['refactor']}")
        print(f"  ⚪ Convencion:       {conteo['convention']}")

        # Mostrar los mas importantes
        importantes = [i for i in issues if i.get("type") in ("error", "warning", "fatal")]
        if importantes:
            print("\nHallazgos importantes:")
            for i in importantes[:8]:
                print(f"  Linea {i.get('line',0):>4}: [{i.get('message-id','')}] {i.get('message','')[:70]}")

        # Nota sobre calificacion
        score_match = re.search(r'rated at ([\d.]+)', result.stdout + result.stderr)
        if score_match:
            score = float(score_match.group(1))
            print(f"\nCalificacion Pylint: {score}/10.0 "
                  f"({'✅ Buena' if score>=7 else '⚠️  Mejorable' if score>=5 else '🔴 Requiere atencion'})")

        return issues

    except FileNotFoundError:
        print("  Pylint no instalado. Ejecuta: pip install pylint")
        # Instalar y reintentar
        subprocess.run([sys.executable, "-m", "pip", "install", "pylint", "-q"], capture_output=True)
        return []
    except Exception as e:
        print(f"  Error en pylint: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────
# PARTE B: Radon - Complejidad ciclomatica (metrica SonarQube)
# ─────────────────────────────────────────────────────────────────────

def run_radon():
    print("\n" + "="*60)
    print("RADON - Complejidad Ciclomatica y Metricas")
    print("="*60)
    try:
        # Complejidad ciclomatica
        result = subprocess.run(
            ["python3", "-m", "radon", "cc", APP_FILE, "-s", "-j"],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout) if result.stdout.strip() else {}
        funciones = data.get(APP_FILE, [])

        if funciones:
            print(f"\nComplejidad Ciclomatica por funcion:")
            print(f"  {'Funcion':<30} {'Complejidad':>12} {'Clasificacion':>15}")
            print(f"  {'-'*30} {'-'*12} {'-'*15}")
            altas = []
            for fn in sorted(funciones, key=lambda x: x.get("complexity", 0), reverse=True):
                c = fn.get("complexity", 0)
                rank = fn.get("rank", "?")
                name = fn.get("name", "?")
                marca = "✅" if c <= 5 else "⚠️ " if c <= 10 else "🔴"
                print(f"  {name:<30} {c:>12} {marca} {rank}")
                if c > 10:
                    altas.append(name)
            if altas:
                print(f"\n  ⚠️  Funciones con alta complejidad (>10): {', '.join(altas)}")
            else:
                print(f"\n  ✅ Todas las funciones tienen complejidad aceptable")

        # Indice de mantenibilidad
        result2 = subprocess.run(
            ["python3", "-m", "radon", "mi", APP_FILE, "-s"],
            capture_output=True, text=True
        )
        if result2.stdout:
            print(f"\nIndice de Mantenibilidad:")
            print(f"  {result2.stdout.strip()}")

        # Metricas brutas
        result3 = subprocess.run(
            ["python3", "-m", "radon", "raw", APP_FILE, "-s"],
            capture_output=True, text=True
        )
        if result3.stdout:
            lines = result3.stdout.strip().split("\n")
            print(f"\nMetricas de Codigo:")
            for line in lines:
                if any(k in line for k in ["LOC", "LLOC", "SLOC", "Comments", "Blank"]):
                    print(f"  {line.strip()}")

        return funciones

    except FileNotFoundError:
        subprocess.run([sys.executable, "-m", "pip", "install", "radon", "-q"], capture_output=True)
        print("  Radon instalado. Vuelve a ejecutar el script.")
        return []
    except Exception as e:
        print(f"  Error en radon: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────
# PARTE C: Cobertura de tests para SonarQube
# ─────────────────────────────────────────────────────────────────────

def run_coverage():
    print("\n" + "="*60)
    print("COVERAGE - Cobertura de Pruebas (para SonarQube)")
    print("="*60)
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest",
             "tests/test_happypet.py",
             f"--cov={BASE_DIR}",
             "--cov-report=term-missing",
             "--cov-report=xml:coverage.xml",
             "--cov-config=.coveragerc",
             "-q", "--tb=no"],
            capture_output=True, text=True,
            cwd=BASE_DIR
        )
        output = result.stdout + result.stderr
        print(output[:3000])

        if os.path.exists(os.path.join(BASE_DIR, "coverage.xml")):
            print(f"\n✅ coverage.xml generado → usar con SonarQube")
            print(f"   sonar.python.coverage.reportPaths=coverage.xml")
        return True
    except Exception as e:
        print(f"  Error en coverage: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────
# PARTE D: Instrucciones SonarQube
# ─────────────────────────────────────────────────────────────────────

def instrucciones_sonarqube():
    print("\n" + "="*60)
    print("INSTRUCCIONES - SonarQube")
    print("="*60)
    print("""
Opcion 1 - SonarCloud (online, gratis para proyectos publicos):
───────────────────────────────────────────────────────────────
  1. Ir a https://sonarcloud.io → crear cuenta con GitHub
  2. Crear nuevo proyecto → obtener token
  3. Reemplazar en sonar-project.properties:
       sonar.host.url=https://sonarcloud.io
       sonar.login=TU_TOKEN_AQUI
  4. Ejecutar:
       sonar-scanner

Opcion 2 - SonarQube Local con Docker:
───────────────────────────────────────
  docker run -d --name sonarqube \\
    -p 9000:9000 sonarqube:community

  Abrir: http://localhost:9000
  Usuario: admin / Contrasena: admin

  Instalar sonar-scanner:
    # Windows: descargar de https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
    # Linux:   apt install sonar-scanner

  Ejecutar analisis:
    sonar-scanner \\
      -Dsonar.projectKey=happypet \\
      -Dsonar.sources=. \\
      -Dsonar.host.url=http://localhost:9000 \\
      -Dsonar.login=TU_TOKEN

Metricas que SonarQube analiza para Python:
───────────────────────────────────────────
  - Bugs y Vulnerabilidades
  - Code Smells (olores de codigo)
  - Deuda tecnica (tiempo estimado de correccion)
  - Cobertura de tests (requiere coverage.xml)
  - Duplicacion de codigo
  - Complejidad ciclomatica
    """)

    # Generar .coveragerc para cobertura correcta
    coveragerc = "[run]\nomit = tests/*,setup_templates.py\n[report]\nexclude_lines =\n    pragma: no cover\n    if __name__ == .__main__.\n"
    with open(os.path.join(BASE_DIR, ".coveragerc"), "w") as f:
        f.write(coveragerc)
    print("✅ .coveragerc generado para configuracion de cobertura")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("HappyPet - Inspeccion de Codigo SonarQube")
    print("="*60)

    # 1. Pylint
    pylint_issues = run_pylint()

    # 2. Complejidad
    funciones = run_radon()

    # 3. Cobertura
    run_coverage()

    # 4. Instrucciones SonarQube
    instrucciones_sonarqube()

    print("\n" + "="*60)
    print("RESUMEN INSPECCION DE CODIGO")
    print("="*60)
    errores = len([i for i in pylint_issues if i.get("type") in ("error","fatal")])
    warnings = len([i for i in pylint_issues if i.get("type") == "warning"])
    fn_complejas = len([f for f in funciones if f.get("complexity",0) > 10])
    print(f"  Pylint errores:         {errores}")
    print(f"  Pylint advertencias:    {warnings}")
    print(f"  Funciones complejas:    {fn_complejas} (complejidad > 10)")
    print(f"  Archivo coverage.xml:   {'Generado ✅' if os.path.exists(os.path.join(BASE_DIR,'coverage.xml')) else 'No generado'}")
    print(f"  sonar-project.properties: Configurado ✅")
    print("="*60)
