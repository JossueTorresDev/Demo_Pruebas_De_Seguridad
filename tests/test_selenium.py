"""
Pruebas Funcionales Automatizadas con Selenium
================================================
App bajo prueba : Sistema Maestro (Flask) en http://localhost:5000
Ejecutar        : python tests/test_selenium.py
Requisito       : pip install selenium webdriver-manager
                  La app debe estar corriendo antes de ejecutar.
"""

import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:5000"
USUARIO  = "admin"
PASSWORD = "admin123"


def crear_driver():
    """Inicializa ChromeDriver de forma automática."""
    options = webdriver.ChromeOptions()
    # Descomenta la siguiente línea para modo headless (sin ventana)
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


class TestLogin(unittest.TestCase):
    """TC-01 y TC-02: Pruebas de inicio de sesión."""

    def setUp(self):
        self.driver = crear_driver()
        self.wait   = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_01_login_exitoso(self):
        """TC-01: Login con credenciales válidas redirige al dashboard."""
        print("\n[TC-01] Login exitoso...")
        d = self.driver
        d.get(f"{BASE_URL}/login")

        d.find_element(By.ID, "username").send_keys(USUARIO)
        d.find_element(By.ID, "password").send_keys(PASSWORD)
        d.find_element(By.ID, "btnLogin").click()

        self.wait.until(EC.url_contains("/"))
        self.assertIn("Lista de Estudiantes", d.title)
        print("  ✅ Login exitoso — título:", d.title)

    def test_02_login_fallido(self):
        """TC-02: Login con credenciales inválidas muestra error."""
        print("\n[TC-02] Login fallido...")
        d = self.driver
        d.get(f"{BASE_URL}/login")

        d.find_element(By.ID, "username").send_keys("usuario_falso")
        d.find_element(By.ID, "password").send_keys("clave_incorrecta")
        d.find_element(By.ID, "btnLogin").click()

        error_msg = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("incorrectas", error_msg.text.lower())
        print("  ✅ Mensaje de error mostrado:", error_msg.text)


class TestAgregarEstudiante(unittest.TestCase):
    """TC-03 y TC-04: Agregar estudiante."""

    def setUp(self):
        self.driver = crear_driver()
        self.wait   = WebDriverWait(self.driver, 10)
        self._hacer_login()

    def tearDown(self):
        self.driver.quit()

    def _hacer_login(self):
        d = self.driver
        d.get(f"{BASE_URL}/login")
        d.find_element(By.ID, "username").send_keys(USUARIO)
        d.find_element(By.ID, "password").send_keys(PASSWORD)
        d.find_element(By.ID, "btnLogin").click()
        self.wait.until(EC.url_contains("/"))

    def test_03_agregar_estudiante_valido(self):
        """TC-03: Agregar estudiante con datos válidos."""
        print("\n[TC-03] Agregar estudiante válido...")
        d = self.driver

        d.find_element(By.ID, "btnAgregar").click()
        self.wait.until(EC.presence_of_element_located((By.ID, "formAgregar")))

        # Llenar formulario
        nombre_campo = d.find_element(By.ID, "nombre")
        nombre_campo.clear()
        nombre_campo.send_keys("Ana García Test")

        carnet_campo = d.find_element(By.ID, "carnet")
        carnet_campo.clear()
        carnet_campo.send_keys(f"TEST-{int(time.time())}")  # carnet único

        nota_campo = d.find_element(By.ID, "nota")
        nota_campo.clear()
        nota_campo.send_keys("8.5")

        d.find_element(By.ID, "btnGuardar").click()

        # Verificar mensaje de éxito
        alerta = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        self.assertIn("agregado", alerta.text.lower())
        print("  ✅ Estudiante agregado:", alerta.text)

    def test_04_agregar_estudiante_sin_nombre(self):
        """TC-04: Formulario rechaza envío si el nombre está vacío (validación HTML5)."""
        print("\n[TC-04] Validación: nombre vacío...")
        d = self.driver

        d.get(f"{BASE_URL}/agregar")
        self.wait.until(EC.presence_of_element_located((By.ID, "formAgregar")))

        # Dejar nombre vacío, llenar resto
        d.find_element(By.ID, "carnet").send_keys("CARNET-VACIO")
        d.find_element(By.ID, "nota").clear()
        d.find_element(By.ID, "nota").send_keys("7")
        d.find_element(By.ID, "btnGuardar").click()

        # La página no debe redirigir (validación nativa del navegador)
        self.assertIn("/agregar", d.current_url)
        print("  ✅ Formulario no enviado — sigue en /agregar")


class TestBusqueda(unittest.TestCase):
    """TC-05: Buscar estudiante."""

    def setUp(self):
        self.driver = crear_driver()
        self.wait   = WebDriverWait(self.driver, 10)
        self._hacer_login()

    def tearDown(self):
        self.driver.quit()

    def _hacer_login(self):
        d = self.driver
        d.get(f"{BASE_URL}/login")
        d.find_element(By.ID, "username").send_keys(USUARIO)
        d.find_element(By.ID, "password").send_keys(PASSWORD)
        d.find_element(By.ID, "btnLogin").click()
        self.wait.until(EC.url_contains("/"))

    def test_05_busqueda_sin_resultados(self):
        """TC-05: Búsqueda de texto inexistente muestra aviso."""
        print("\n[TC-05] Búsqueda sin resultados...")
        d = self.driver

        d.get(f"{BASE_URL}/buscar")
        self.wait.until(EC.presence_of_element_located((By.ID, "campoBusqueda")))

        campo = d.find_element(By.ID, "campoBusqueda")
        campo.send_keys("xzxzxzxz_no_existe")
        d.find_element(By.ID, "btnBuscar").click()

        aviso = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-warning"))
        )
        self.assertIn("no se encontraron", aviso.text.lower())
        print("  ✅ Mensaje sin resultados:", aviso.text)


class TestSesion(unittest.TestCase):
    """TC-06: Acceso sin sesión activa redirige a login."""

    def setUp(self):
        self.driver = crear_driver()
        self.wait   = WebDriverWait(self.driver, 10)

    def tearDown(self):
        self.driver.quit()

    def test_06_redireccion_sin_sesion(self):
        """TC-06: Intentar acceder al index sin login redirige a /login."""
        print("\n[TC-06] Redirección sin sesión...")
        d = self.driver
        d.get(f"{BASE_URL}/")
        self.wait.until(EC.url_contains("/login"))
        self.assertIn("/login", d.current_url)
        print("  ✅ Redirigido a:", d.current_url)


# ─── Punto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(" PRUEBAS FUNCIONALES AUTOMATIZADAS — Sistema Maestro")
    print("=" * 60)
    print(f" URL base: {BASE_URL}")
    print(" Asegúrate de que la app Flask esté corriendo.")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # Agregar todos los test cases en orden
    for cls in [TestLogin, TestAgregarEstudiante, TestBusqueda, TestSesion]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    total  = result.testsRun
    fallos = len(result.failures) + len(result.errors)
    print(f" Total: {total} pruebas | Exitosas: {total - fallos} | Fallidas: {fallos}")
    print("=" * 60)
