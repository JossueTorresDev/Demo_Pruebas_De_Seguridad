# 🔐 Demo Pruebas de Seguridad — OWASP Top 10

Proyecto académico que demuestra **pruebas funcionales automatizadas** con Selenium y **pruebas de seguridad** basadas en OWASP Top 10 sobre una mini aplicación web de gestión de estudiantes.

---

## 📁 Estructura del proyecto

```
Demo_Pruebas_De_Seguridad/
│
├── app/
│   ├── app.py                  ← Backend Flask (Python)
│   ├── estudiantes.db          ← SQLite (se genera al arrancar)
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── index.html
│   │   ├── agregar.html
│   │   └── buscar.html
│   └── static/
│       └── style.css
│
├── tests/
│   └── test_selenium.py        ← 6 pruebas funcionales automatizadas
│
├── requirements.txt
└── README.md                   ← Este archivo (informe completo)
```

---

## 🚀 Cómo ejecutar la aplicación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Arrancar el servidor Flask

```bash
cd app
python app.py
```

La app estará en → **http://localhost:5000**

Credenciales de demo: `admin` / `admin123`

### 3. Ejecutar las pruebas de Selenium

> Con la app ya corriendo, en otra terminal:

```bash
python tests/test_selenium.py
```

---

## ✅ Prueba Funcional Automatizada (Selenium)

### ¿Qué hace el script?

El archivo `tests/test_selenium.py` contiene **6 casos de prueba** organizados en 4 clases:

| ID    | Clase                    | Descripción                                         |
|-------|--------------------------|-----------------------------------------------------|
| TC-01 | TestLogin                | Login exitoso con credenciales válidas              |
| TC-02 | TestLogin                | Login fallido muestra mensaje de error              |
| TC-03 | TestAgregarEstudiante    | Agregar estudiante con datos válidos                |
| TC-04 | TestAgregarEstudiante    | Formulario rechaza envío si el nombre está vacío    |
| TC-05 | TestBusqueda             | Búsqueda sin resultados muestra aviso               |
| TC-06 | TestSesion               | Acceso sin sesión redirige a /login                 |

### Acciones cubiertos por Selenium

- Abrir página (`driver.get`)
- Localizar elementos (`find_element` por ID, clase)
- Llenar formularios (`send_keys`)
- Hacer clic en botones (`click`)
- Validar resultados (`assert`, `WebDriverWait`, `expected_conditions`)
- Verificar redirecciones y mensajes dinámicos

---

## ⚔️ Comparativa: Selenium vs Playwright

| Criterio                  | Selenium                              | Playwright                                  |
|---------------------------|---------------------------------------|---------------------------------------------|
| **Soporte de navegadores**| Chrome, Firefox, Safari, Edge, IE     | Chrome, Firefox, WebKit (Safari), Edge      |
| **Lenguajes**             | Java, Python, JS, C#, Ruby            | Python, JS/TS, Java, C#                     |
| **Velocidad**             | Media (depende de WebDriver externo)  | ⚡ Más rápido (protocolo CDP nativo)        |
| **Configuración**         | Requiere WebDriver por navegador      | ✅ `playwright install` lo hace todo        |
| **Selectores**            | By.ID, By.XPATH, By.CSS_SELECTOR      | CSS, XPath, texto, roles ARIA               |
| **Espera de elementos**   | Explicit/Implicit wait manual         | ✅ Auto-wait incorporado                    |
| **Modo headless**         | Requiere configuración manual         | ✅ Headless por defecto                     |
| **Capturas de pantalla**  | Manual con `save_screenshot`          | ✅ Integradas, incluyendo videos            |
| **Pruebas en paralelo**   | Complejo, requiere librerías externas | ✅ Soporte nativo                           |
| **Comunidad/Madurez**     | ✅ Muy madura, amplia documentación   | Creciente, mantenida por Microsoft          |
| **Soporte mobile**        | Limitado (Appium separado)            | Emulación de dispositivos integrada         |

### Conclusión de la comparativa

**Playwright** es más moderno, rápido y tiene mejor experiencia de desarrollo gracias al auto-wait y configuración simplificada. **Selenium** sigue siendo la opción estándar en empresas grandes con infraestructuras ya establecidas. Para proyectos nuevos, Playwright es la mejor elección; para proyectos legacy, Selenium sigue siendo relevante.

---

## 🛡️ Prueba de Seguridad — OWASP Top 10

### Herramienta utilizada: OWASP ZAP (Zed Attack Proxy)

OWASP ZAP es un escáner de seguridad gratuito y de código abierto que actúa como proxy entre el navegador y la app, interceptando y analizando el tráfico para detectar vulnerabilidades.

**Descarga:** https://www.zaproxy.org/download/

### Cómo ejecutar el análisis

1. Descargar e instalar OWASP ZAP
2. Abrir ZAP → **Quick Start** → **Automated Scan**
3. URL: `http://localhost:5000`
4. Clic en **Attack**
5. Revisar la pestaña **Alerts** al finalizar

---

## 📊 Informe de Hallazgos de Seguridad

A continuación se documentan las vulnerabilidades OWASP más relevantes, su estado en esta app y las medidas preventivas aplicadas.

---

### 🔴 OWASP A01 — Broken Access Control

**Descripción:** Usuarios no autorizados pueden acceder a recursos protegidos.

**Estado en la app:** ✅ MITIGADO

**Medida aplicada:**
```python
# Decorador que verifica sesión activa en cada ruta protegida
@login_required
def index():
    ...
```
Todas las rutas sensibles requieren sesión activa. Sin login, se redirige a `/login`.

**Evidencia de prueba (TC-06):** El test de Selenium verifica que `/` sin sesión redirige a `/login`.

---

### 🔴 OWASP A03 — Injection (SQL Injection)

**Descripción:** Datos maliciosos enviados al intérprete SQL para manipular consultas.

**Ejemplo de ataque:**
```
Usuario: admin' OR '1'='1
Contraseña: cualquier_cosa
```

**Estado en la app:** ✅ MITIGADO

**Medida aplicada:** Uso de consultas parametrizadas en todas las operaciones:
```python
# ✅ Seguro — parámetros separados de la consulta
conn.execute(
    "SELECT * FROM usuarios WHERE username = ? AND password = ?",
    (username, pw_hash)
)

# ❌ Vulnerable (NUNCA hacer esto)
# conn.execute(f"SELECT * FROM usuarios WHERE username = '{username}'")
```

**Cómo probarlo con ZAP:** ZAP → Alerts → buscar "SQL Injection". Si la app está bien protegida, no debe aparecer.

---

### 🔴 OWASP A07 — Cross-Site Scripting (XSS)

**Descripción:** Inyección de código JavaScript malicioso que se ejecuta en el navegador de otros usuarios.

**Ejemplo de ataque:**
```
Nombre: <script>alert('XSS')</script>
```

**Estado en la app:** ✅ MITIGADO

**Medida aplicada:** Jinja2 (motor de plantillas de Flask) **escapa automáticamente** el HTML en las variables `{{ variable }}`. El nombre se renderiza como texto plano, nunca como HTML ejecutable.

**Resultado visual:**
- Sin protección → Se ejecuta el `alert()`
- Con Jinja2 escape → Se muestra literalmente: `<script>alert('XSS')</script>`

**Cómo probarlo con ZAP:** ZAP → Alerts → buscar "Cross Site Scripting".

---

### 🟡 OWASP A02 — Cryptographic Failures (Contraseñas)

**Descripción:** Almacenamiento de contraseñas en texto plano.

**Estado en la app:** ⚠️ PARCIALMENTE MITIGADO (SHA-256, recomendable bcrypt)

**Medida aplicada:**
```python
import hashlib
pw_hash = hashlib.sha256(password.encode()).hexdigest()
```

**Mejora recomendada (producción):**
```python
import bcrypt
# Al guardar:
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# Al verificar:
bcrypt.checkpw(password.encode(), hashed)
```
bcrypt es preferible porque incluye "salt" automático y es computacionalmente costoso (dificulta ataques de fuerza bruta).

---

### 🟡 OWASP A05 — Security Misconfiguration

**Descripción:** Configuraciones inseguras por defecto exponen información sensible.

**Problemas comunes y estado:**

| Configuración                     | Estado          | Medida                              |
|-----------------------------------|-----------------|-------------------------------------|
| `debug=True` en producción        | ⚠️ Solo en dev  | Cambiar a `debug=False` en prod     |
| Headers de seguridad HTTP         | ⚠️ No aplicados | Usar Flask-Talisman o Helmet.js     |
| Clave secreta hardcodeada         | ✅ Generada con `secrets.token_hex(32)` | Mover a variable de entorno |

**Medida recomendada:**
```python
import os
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
```

---

### 🟡 OWASP A09 — Security Logging and Monitoring Failures

**Descripción:** Sin registros de auditoría, es imposible detectar ataques.

**Estado en la app:** ⚠️ No implementado (demo)

**Mejora recomendada:**
```python
import logging
logging.basicConfig(filename='security.log', level=logging.WARNING)

# En el login fallido:
logging.warning(f"Login fallido para usuario: {username} desde IP: {request.remote_addr}")
```

---

## 🎬 Guía para el video

### Estructura sugerida (grabación con cámara activa)

1. **Introducción** (1 min)
   - Presentarte, mencionar el objetivo de la tarea
   - Mostrar la estructura del proyecto

2. **Demo de la app** (2 min)
   - Abrir `http://localhost:5000`
   - Hacer login, agregar un estudiante, buscarlo

3. **Pruebas con Selenium** (3 min)
   - Mostrar el código de `test_selenium.py`
   - Ejecutarlo: `python tests/test_selenium.py`
   - Explicar cada caso de prueba mientras corre

4. **Pruebas de seguridad con OWASP ZAP** (3 min)
   - Abrir ZAP, configurar Quick Start con `http://localhost:5000`
   - Ejecutar el escaneo
   - Mostrar y explicar los Alerts

5. **Conclusiones** (2 min) — ver sección siguiente

---

## 📝 Conclusiones

### 1. Las pruebas automatizadas garantizan calidad sostenible
Automatizar pruebas funcionales con Selenium permite ejecutar decenas de verificaciones en segundos, detectando regresiones antes de que lleguen a producción. Sin automatización, cada cambio en el código requeriría pruebas manuales costosas y propensas a errores humanos.

### 2. La seguridad debe diseñarse desde el inicio, no añadirse después
El análisis con OWASP ZAP demostró que vulnerabilidades como SQL Injection o XSS son fáciles de introducir y difíciles de detectar sin herramientas especializadas. Implementar consultas parametrizadas y escapado de salida desde el primer día tiene un costo mínimo, pero previene brechas de seguridad graves.

### 3. OWASP Top 10 es una guía esencial para el desarrollo seguro
Las vulnerabilidades listadas por OWASP no son teóricas; son las más explotadas en aplicaciones reales. Conocerlas y revisarlas sistemáticamente convierte al desarrollador en un agente activo de seguridad, no solo un generador de funcionalidades.

### 4. Las herramientas de prueba complementan pero no reemplazan el juicio del desarrollador
Selenium y OWASP ZAP automatizan la detección de problemas conocidos, pero la lógica de negocio incorrecta, los errores de diseño y las vulnerabilidades de contexto específico requieren revisión humana y criterio técnico. Las pruebas son una red de seguridad, no una garantía absoluta.

---

## 🔗 Referencias

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Selenium Docs: https://www.selenium.dev/documentation/
- Playwright Docs: https://playwright.dev/python/docs/intro
- OWASP ZAP: https://www.zaproxy.org/
- Flask Security: https://flask.palletsprojects.com/en/3.0.x/security/
- Pruebas OWASP en español: https://www.softwaretestingbureau.com/pruebas-de-seguridad-owasp-top-10/
