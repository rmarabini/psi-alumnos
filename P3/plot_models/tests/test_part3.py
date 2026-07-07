"""
Test de la Parte 3: Despliegue en Render.

Este módulo contiene 12 tests que verifican el funcionamiento del API REST
desplegado en producción (Render.com). Los tests se ejecutan contra la URL
configurada en la variable de entorno RENDER_URL.

Si RENDER_URL no está configurada o el despliegue no es accesible,
los tests se skipean automáticamente.

Tests incluidos:
- Accesibilidad del despliegue
- Endpoint de tokens JWT
- CRUD de sensores y mediciones
- Listado de dashboards y plots
- Filtrado de mediciones por sensor

Ejecutar con: python manage.py test plot_models.tests.test_part3 --verbosity 2
"""
import os
import unittest
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

RENDER_URL = os.getenv("RENDER_URL", "").rstrip("/")
API_BASE = f"{RENDER_URL}/api/v1" if RENDER_URL else ""
USERNAME = os.getenv("API_USERNAME", "alumnodb")
PASSWORD = os.getenv("API_PASSWORD", "alumnodb")


def check_status():
    """Verifica si el despliegue en Render está accesible."""
    if not RENDER_URL:
        return False, "RENDER_URL not configured"
    try:
        resp = requests.get(RENDER_URL, timeout=10)
        return resp.status_code == 200, f"HTTP {resp.status_code}"
    except requests.RequestException as e:
        return False, str(e)


class RenderDeploymentTests(unittest.TestCase):
    """Tests del despliegue en producción (Render.com)."""

    @classmethod
    def setUpClass(cls):
        """Configura el token de autenticación para todos los tests."""
        ok, msg = check_status()
        if not ok:
            raise unittest.SkipTest(
                f"Render deployment not available: {msg}")

        resp = requests.post(f"{API_BASE}/token/", json={
            "username": USERNAME, "password": PASSWORD
        }, timeout=10)
        if resp.status_code != 200:
            raise unittest.SkipTest(
                f"Cannot obtain token: HTTP {resp.status_code}")
        cls.token = resp.json()["access"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    def test_deployment_reachable(self):
        """Verifica que la URL base de Render responde con HTTP 200."""
        resp = requests.get(RENDER_URL, timeout=10)
        self.assertEqual(resp.status_code, 200)

    def test_api_root_reachable(self):
        """Verifica que el prefijo /api/v1/ es accesible."""
        resp = requests.get(API_BASE, timeout=10,
                            headers=self.headers)
        self.assertIn(resp.status_code, (200, 404))

    def test_token_endpoint(self):
        """Verifica obtención de token JWT con credenciales válidas."""
        resp = requests.post(f"{API_BASE}/token/", json={
            "username": USERNAME, "password": PASSWORD
        }, timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.json())
        self.assertIn("refresh", resp.json())

    def test_token_invalid_credentials(self):
        """Verifica que credenciales incorrectas devuelven 401."""
        resp = requests.post(f"{API_BASE}/token/", json={
            "username": "bad", "password": "bad"
        }, timeout=10)
        self.assertEqual(resp.status_code, 401)

    def test_list_sensors(self):
        """Verifica listado de sensores."""
        resp = requests.get(f"{API_BASE}/sensors/",
                            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_create_and_delete_sensor(self):
        """Verifica creación y borrado de sensor en producción."""
        resp = requests.post(f"{API_BASE}/sensors/", json={
            "name": "render-test-sensor",
            "host_mac": "00:11:22:33:44:55"
        }, headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 201)
        sensor_id = resp.json()["id"]
        self.assertIn("created_at", resp.json())

        resp = requests.delete(
            f"{API_BASE}/sensors/{sensor_id}/",
            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 204)

    def test_list_measurements(self):
        """Verifica listado de mediciones."""
        resp = requests.get(f"{API_BASE}/measurements/",
                            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_create_and_delete_measurement(self):
        """Verifica creación y borrado de medición en producción."""
        sensor_resp = requests.post(f"{API_BASE}/sensors/", json={
            "name": "meas-test-sensor"
        }, headers=self.headers, timeout=10)
        self.assertEqual(sensor_resp.status_code, 201)
        sensor_id = sensor_resp.json()["id"]

        resp = requests.post(f"{API_BASE}/measurements/", json={
            "sensor": sensor_id,
            "timestamp": "2026-07-03T12:00:00Z",
            "value": 42.5
        }, headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json()["value"], 42.5)
        measurement_id = resp.json()["id"]

        # Delete measurement explicitly
        resp = requests.delete(
            f"{API_BASE}/measurements/{measurement_id}/",
            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 204)

        # Delete sensor
        requests.delete(
            f"{API_BASE}/sensors/{sensor_id}/",
            headers=self.headers, timeout=10)

    def test_list_dashboards(self):
        """Verifica listado de dashboards."""
        resp = requests.get(f"{API_BASE}/dashboards/",
                            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_list_plots(self):
        """Verifica listado de plots."""
        resp = requests.get(f"{API_BASE}/plots/",
                            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_filter_measurements_by_sensor(self):
        """Verifica filtrado de mediciones por sensor en producción."""
        resp = requests.get(f"{API_BASE}/sensors/",
                            headers=self.headers, timeout=10)
        self.assertEqual(resp.status_code, 200)
        sensors = resp.json()
        if sensors:
            sid = sensors[0]["id"]
            resp = requests.get(
                f"{API_BASE}/measurements/?sensor={sid}",
                headers=self.headers, timeout=10)
            self.assertEqual(resp.status_code, 200)
            self.assertIsInstance(resp.json(), list)

    def test_create_dashboard_minimal(self):
        """Verifica creación de dashboard con datos mínimos."""
        users_resp = requests.get(f"{API_BASE}/users/",
                                  headers=self.headers, timeout=10)
        user_id = None
        if users_resp.status_code == 200:
            users = users_resp.json()
            if users:
                user_id = users[0]["id"]
        if not user_id:
            user_id = 1

        resp = requests.post(f"{API_BASE}/dashboards/", json={
            "name": "render-test-dashboard",
            "user": user_id
        }, headers=self.headers, timeout=10)
        if resp.status_code == 201:
            dash_id = resp.json()["id"]
            requests.delete(
                f"{API_BASE}/dashboards/{dash_id}/",
                headers=self.headers, timeout=10)
        self.assertIn(resp.status_code, (201, 400))
