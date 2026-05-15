# HappyPet - Suite de Calidad de Software
## TCY0101 - Tecnicas de Calidad de Software

---

## Instalacion rapida

```bash
pip install flask requests pytest pytest-flask pytest-cov selenium locust bandit pylint radon
python setup_templates.py
python ejecutar_todo.py
```

---

## Herramientas incluidas

### 1. Pytest — Tests Unitarios e Integracion (JUnit)
```bash
# Ejecutar todos los tests
pytest tests/test_happypet.py -v

# Con reporte JUnit XML (importable en Jenkins/SonarQube)
pytest tests/test_happypet.py -v --junitxml=reporte_junit.xml

# Con cobertura
pytest tests/test_happypet.py --cov=. --cov-report=html
```
**Cubre:** Login, Productos CRUD, Clientes CRUD, Ventas, Tienda, DB  
**Tests:** 44 casos de prueba

---

### 2. Selenium IDE / Katalon Studio
```bash
python tests/test_selenium.py
```
Genera `tests/happypet_selenium.side`

**Para abrir en Selenium IDE:**
1. Instalar plugin Selenium IDE en Chrome o Firefox
2. Abrir Selenium IDE → Open existing project
3. Seleccionar `happypet_selenium.side`
4. Click Run All Tests

**Para importar en Katalon Studio:**
1. File → Import → Selenium IDE project
2. Seleccionar `happypet_selenium.side`
3. Run → Execute

**Suites incluidas:**
- Suite Completa (9 tests)
- Suite Rapida - Login y Tienda (4 tests)

---

### 3. SonarQube — Inspeccion de Codigo
```bash
python tests/test_sonarqube.py
```

**Con SonarCloud (online gratis):**
1. Crear cuenta en https://sonarcloud.io
2. Obtener token
3. Editar `sonar-project.properties` con el token
4. `sonar-scanner`

**Con SonarQube local (Docker):**
```bash
docker run -d -p 9000:9000 sonarqube:community
# Abrir http://localhost:9000
sonar-scanner -Dsonar.login=TU_TOKEN
```

**Metricas analizadas:** Bugs, Vulnerabilidades, Code Smells, Cobertura, Duplicaciones

---

### 4. OWASP ZAP + Bandit — Seguridad
```bash
python tests/test_security.py
```

**Bandit** (analisis estatico):
```bash
bandit -r app.py -f html -o reporte_bandit.html
```

**OWASP ZAP** (escaneo activo):
```bash
# Con Docker (servidor corriendo)
docker run -t zaproxy/zap-stable zap-baseline.py \
  -t http://host.docker.internal:5000 \
  -r zap_report.html
```

**Cubre:** OWASP Top 10 (A01-A10), SQL Injection, Auth, Crypto, Headers

---

### 5. Locust — Carga y Estres
```bash
# Modo Web UI (recomendado para presentacion)
locust -f tests/test_carga.py --host=http://127.0.0.1:5000
# Abrir http://localhost:8089

# Modo headless con reporte HTML
locust -f tests/test_carga.py \
  --host=http://127.0.0.1:5000 \
  --headless -u 50 -r 10 --run-time 60s \
  --html reporte_carga.html
```

**Escenarios:**
- `UsuarioCliente` (70%): Navega tienda, filtra, agrega al carrito, compra
- `UsuarioAdministrador` (30%): Dashboard, CRUD, reportes

**Criterios de aceptacion:**
- Tasa de error < 5%
- Tiempo respuesta promedio < 2s
- Percentil 95 < 5s

---

## Archivos generados

| Archivo | Herramienta | Descripcion |
|---------|-------------|-------------|
| `reporte_junit.xml` | Pytest | Resultados XML importable |
| `tests/happypet_selenium.side` | Selenium IDE | Proyecto ejecutable en IDE |
| `coverage.xml` | pytest-cov | Cobertura para SonarQube |
| `sonar-project.properties` | SonarQube | Configuracion del proyecto |
| `tests/zap_scan.py` | OWASP ZAP | Script para ZAP API |
| `reporte_carga.html` | Locust | Informe de carga (generado al correr) |
