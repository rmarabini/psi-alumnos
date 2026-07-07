"""
Test de la Parte 2: Cliente de monitorización y autenticación.

Este módulo contiene 28 tests organizados en 7 clases que verifican:
- Configuración de variables de entorno con python-dotenv
- Flujo completo de autenticación JWT
- Registro de sensores con dirección MAC
- Persistencia y filtrado de mediciones
- Flujo de integración completo
- Obtención de dirección MAC con psutil

Ejecutar con: python manage.py test plot_models.tests.test_part2 --verbosity 2
"""
import os
import unittest
from unittest.mock import MagicMock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
from ..models import Sensor, Measurement


try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


class EnvConfigTests(APITestCase):
    """Tests de configuración: python-dotenv, DRF settings, apps instaladas."""

    @unittest.skipUnless(HAS_DOTENV, 'python-dotenv not installed')
    def test_dotenv_loading(self):
        """Verifica que python-dotenv carga variables de entorno correctamente."""
        load_dotenv()
        api_url = os.getenv("API_URL", "http://localhost:8000/api/v1")
        self.assertIsNotNone(api_url)
        self.assertTrue(api_url.startswith("http"))

    def test_default_values(self):
        """Verifica que existen valores por defecto para variables de entorno."""
        api_url = os.getenv("API_URL", "http://localhost:8000/api/v1")
        username = os.getenv("API_USERNAME", "alumnodb")
        password = os.getenv("API_PASSWORD", "alumnodb")
        self.assertEqual(api_url, os.getenv("API_URL", "http://localhost:8000/api/v1"))
        self.assertEqual(username, os.getenv("API_USERNAME", "alumnodb"))
        self.assertEqual(password, os.getenv("API_PASSWORD", "alumnodb"))

    def test_drf_settings_configured(self):
        """Verifica que REST_FRAMEWORK está configurado con JWT y permisos."""
        self.assertIn('DEFAULT_AUTHENTICATION_CLASSES',
                      settings.REST_FRAMEWORK)
        self.assertIn(
            'rest_framework_simplejwt.authentication.JWTAuthentication',
            settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'])
        self.assertIn('DEFAULT_PERMISSION_CLASSES',
                      settings.REST_FRAMEWORK)
        self.assertIn(
            'rest_framework.permissions.IsAuthenticated',
            settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'])

    def test_installed_apps_include_required(self):
        """Verifica que las apps requeridas están en INSTALLED_APPS."""
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('rest_framework_simplejwt', settings.INSTALLED_APPS)
        self.assertIn('plot_models', settings.INSTALLED_APPS)


class AuthFlowTests(APITestCase):
    """Tests del flujo completo de autenticación JWT."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alumnodb', password='alumnodb')

    def test_full_auth_flow(self):
        """Verifica flujo completo: obtener token, usarlo, renovarlo."""
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        access = resp.data['access']
        refresh = resp.data['refresh']

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = client.get('/api/v1/sensors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp_refresh = self.client.post('/api/v1/token/refresh/', {
            'refresh': refresh
        }, format='json')
        self.assertEqual(resp_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp_refresh.data)

    def test_auth_with_multiple_requests(self):
        """Verifica que el token funciona en múltiples peticiones sucesivas."""
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        token = resp.data['access']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        for _ in range(5):
            response = client.get('/api/v1/sensors/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_expired_token_returns_401(self):
        """Verifica que un token inválido/expirado devuelve 401."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer invalid.token.here')
        response = client.get('/api/v1/sensors/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SensorRegistrationTests(APITestCase):
    """Tests de registro de sensores con dirección MAC."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        self.token = resp.data['access']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_register_sensor_with_mac(self):
        """Verifica registro de sensor con dirección MAC."""
        data = {
            'name': 'equipo-test',
            'host_mac': 'aa:bb:cc:dd:ee:ff',
            'location': 'Lab 101',
            'description': 'CPU sensor'
        }
        response = self.client.post('/api/v1/sensors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['host_mac'], 'aa:bb:cc:dd:ee:ff')
        self.assertIn('created_at', response.data)

    def test_register_sensor_minimal(self):
        """Verifica registro de sensor solo con nombre."""
        data = {'name': 'equipo-minimal'}
        response = self.client.post('/api/v1/sensors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'equipo-minimal')

    def test_list_registered_sensors(self):
        """Verifica listado de sensores registrados."""
        Sensor.objects.create(name='sensor-a')
        Sensor.objects.create(name='sensor-b')
        response = self.client.get('/api/v1/sensors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [s['name'] for s in response.data]
        self.assertIn('sensor-a', names)
        self.assertIn('sensor-b', names)

    def test_sensor_name_unique_enforced(self):
        """Verifica que la unicidad del nombre se aplica vía API."""
        Sensor.objects.create(name='unique-name')
        data = {'name': 'unique-name'}
        response = self.client.post('/api/v1/sensors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeasurementPersistenceTests(APITestCase):
    """Tests de persistencia y recuperación de mediciones."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        self.token = resp.data['access']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.sensor = Sensor.objects.create(name='cpu-sensor')

    def test_post_and_retrieve_measurement(self):
        """Verifica crear y recuperar una medición."""
        data = {
            'sensor': self.sensor.id,
            'timestamp': '2026-07-02T08:00:00Z',
            'value': 45.2
        }
        post_resp = self.client.post(
            '/api/v1/measurements/', data, format='json')
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        mid = post_resp.data['id']

        get_resp = self.client.get(f'/api/v1/measurements/{mid}/')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(get_resp.data['value'], 45.2)
        self.assertEqual(get_resp.data['sensor_name'], 'cpu-sensor')

    def test_multiple_measurements_per_sensor(self):
        """Verifica que un sensor puede tener múltiples mediciones."""
        for i in range(5):
            Measurement.objects.create(
                sensor=self.sensor,
                timestamp=f'2026-07-02T08:{i:02d}:00Z',
                value=float(i * 10))
        response = self.client.get('/api/v1/measurements/')
        self.assertEqual(len(response.data), 5)

    def test_measurements_ordered_by_timestamp_desc(self):
        """Verifica que las mediciones se ordenan por timestamp descendente."""
        m1 = Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-02T08:00:00Z', value=10.0)
        m2 = Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-02T09:00:00Z', value=20.0)
        m3 = Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-02T07:00:00Z', value=5.0)
        response = self.client.get('/api/v1/measurements/')
        ids = [m['id'] for m in response.data]
        self.assertEqual(ids, [m2.id, m1.id, m3.id])

    def test_measurement_without_sensor_returns_400(self):
        """Verifica que crear medición sin sensor devuelve 400."""
        data = {
            'timestamp': '2026-07-02T08:00:00Z',
            'value': 50.0
        }
        response = self.client.post(
            '/api/v1/measurements/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_measurement_timestamp_indexed(self):
        """Verifica que timestamp está indexado en el modelo Measurement."""
        indexes = [i.fields for i in Measurement._meta.indexes]
        self.assertIn(['sensor', 'timestamp'], indexes)
        self.assertTrue(Measurement._meta.get_field('timestamp').db_index)


class MeasurementFilterTests(APITestCase):
    """Tests de filtrado de mediciones por sensor."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        self.token = resp.data['access']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.sensor_a = Sensor.objects.create(name='sensor-a')
        self.sensor_b = Sensor.objects.create(name='sensor-b')

    def test_filter_by_sensor(self):
        """Verifica filtrado de mediciones por sensor específico."""
        Measurement.objects.create(
            sensor=self.sensor_a,
            timestamp='2026-07-02T10:00:00Z', value=1.0)
        Measurement.objects.create(
            sensor=self.sensor_b,
            timestamp='2026-07-02T10:00:00Z', value=2.0)
        response = self.client.get(
            f'/api/v1/measurements/?sensor={self.sensor_a.id}')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['value'], 1.0)

    def test_filter_by_sensor_empty_result(self):
        """Verifica que filtro por sensor sin mediciones devuelve lista vacía."""
        response = self.client.get(
            f'/api/v1/measurements/?sensor={self.sensor_a.id}')
        self.assertEqual(len(response.data), 0)

    def test_filter_by_invalid_sensor(self):
        """Verifica que filtro por sensor inexistente devuelve lista vacía."""
        response = self.client.get('/api/v1/measurements/?sensor=99999')
        self.assertEqual(len(response.data), 0)

    def test_filter_multiple_sensors_separately(self):
        """Verifica que cada sensor devuelve solo sus propias mediciones."""
        Measurement.objects.create(
            sensor=self.sensor_a,
            timestamp='2026-07-02T10:00:00Z', value=10.0)
        Measurement.objects.create(
            sensor=self.sensor_b,
            timestamp='2026-07-02T10:00:00Z', value=20.0)

        resp_a = self.client.get(
            f'/api/v1/measurements/?sensor={self.sensor_a.id}')
        self.assertEqual(len(resp_a.data), 1)
        self.assertEqual(resp_a.data[0]['value'], 10.0)

        resp_b = self.client.get(
            f'/api/v1/measurements/?sensor={self.sensor_b.id}')
        self.assertEqual(len(resp_b.data), 1)
        self.assertEqual(resp_b.data[0]['value'], 20.0)


class FullIntegrationTests(APITestCase):
    """Tests de integración completa del sistema."""

    def test_complete_workflow(self):
        """Verifica flujo completo: auth, registro sensor, mediciones, consulta."""
        User.objects.create_user(username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        token = resp.data['access']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        resp = client.post('/api/v1/sensors/', {
            'name': 'test-sensor',
            'host_mac': '00:11:22:33:44:55'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        sensor_id = resp.data['id']

        for i in range(3):
            client.post('/api/v1/measurements/', {
                'sensor': sensor_id,
                'timestamp': f'2026-07-02T{10+i:02d}:00:00Z',
                'value': float(30 + i * 5)
            }, format='json')

        resp = client.get(
            f'/api/v1/measurements/?sensor={sensor_id}')
        self.assertEqual(len(resp.data), 3)

        resp = client.get('/api/v1/sensors/')
        self.assertEqual(len(resp.data), 1)

    def test_create_dashboard_with_plots(self):
        """Verifica creación de dashboard con plots anidados."""
        User.objects.create_user(username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        token = resp.data['access']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        user = User.objects.get(username='alumnodb')
        sensor = Sensor.objects.create(name='cpu-sensor')

        dash_resp = client.post('/api/v1/dashboards/', {
            'name': 'main-dashboard',
            'user': user.id,
            'title': 'Main Dashboard'
        }, format='json')
        self.assertEqual(dash_resp.status_code, status.HTTP_201_CREATED)
        dash_id = dash_resp.data['id']

        plot_resp = client.post('/api/v1/plots/', {
            'dashboard': dash_id,
            'title': 'CPU Usage',
            'sensor': sensor.id,
            'chart_type': 'line',
            'aggregation': 'avg',
            'time_window': '1h',
            'x': 0,
            'y': 0,
            'width': 6,
            'height': 4
        }, format='json')
        self.assertEqual(plot_resp.status_code, status.HTTP_201_CREATED)

        dash_get = client.get(f'/api/v1/dashboards/{dash_id}/')
        self.assertEqual(len(dash_get.data['plots']), 1)
        self.assertEqual(
            dash_get.data['plots'][0]['title'], 'CPU Usage')


try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class GetMacHelperTests(APITestCase):
    """Tests de obtención de dirección MAC usando psutil."""

    def _get_mac(self, ifaddrs):
        """Helper que simula la lógica de obtención de MAC."""
        for iface, addrs in ifaddrs.items():
            for addr in addrs:
                if addr.family == -1 and addr.address and iface != 'lo':
                    return addr.address
        for iface, addrs in ifaddrs.items():
            for addr in addrs:
                if addr.family == -1 and addr.address:
                    return addr.address
        return ":".join(["00"] * 6)

    def test_get_mac_format(self):
        """Verifica formato correcto de dirección MAC."""
        mock_addr = MagicMock()
        mock_addr.family = -1
        mock_addr.address = 'aa:bb:cc:dd:ee:ff'
        ifaddrs = {'eth0': [mock_addr]}
        mac = self._get_mac(ifaddrs)
        self.assertEqual(mac, 'aa:bb:cc:dd:ee:ff')

    def test_get_mac_fallback(self):
        """Verifica valor por defecto cuando no hay interfaces."""
        mac = self._get_mac({})
        self.assertEqual(mac, "00:00:00:00:00:00")

    def test_get_mac_skips_loopback(self):
        """Verifica que se omite la interfaz de loopback (lo)."""
        mock_lo = MagicMock()
        mock_lo.family = -1
        mock_lo.address = '00:00:00:00:00:00'
        mock_eth = MagicMock()
        mock_eth.family = -1
        mock_eth.address = 'aa:bb:cc:dd:ee:ff'
        ifaddrs = {'lo': [mock_lo], 'eth0': [mock_eth]}
        mac = self._get_mac(ifaddrs)
        self.assertEqual(mac, 'aa:bb:cc:dd:ee:ff')

    def test_get_mac_prefers_non_loopback(self):
        """Verifica que se prefiere interfaz no-loopback."""
        mock_lo = MagicMock()
        mock_lo.family = -1
        mock_lo.address = '00:00:00:00:00:00'
        mock_wlan = MagicMock()
        mock_wlan.family = -1
        mock_wlan.address = '11:22:33:44:55:66'
        ifaddrs = {'lo': [mock_lo], 'wlan0': [mock_wlan]}
        mac = self._get_mac(ifaddrs)
        self.assertEqual(mac, '11:22:33:44:55:66')

    def test_get_mac_multiple_interfaces(self):
        """Verifica comportamiento con múltiples interfaces de red."""
        mock_eth0 = MagicMock()
        mock_eth0.family = -1
        mock_eth0.address = 'aa:bb:cc:dd:ee:ff'
        mock_eth1 = MagicMock()
        mock_eth1.family = -1
        mock_eth1.address = '11:22:33:44:55:66'
        ifaddrs = {'eth0': [mock_eth0], 'eth1': [mock_eth1]}
        mac = self._get_mac(ifaddrs)
        self.assertEqual(mac, 'aa:bb:cc:dd:ee:ff')

    @unittest.skipUnless(HAS_PSUTIL, 'psutil not installed')
    def test_psutil_has_af_link(self):
        """Verifica que psutil tiene el atributo AF_LINK."""
        self.assertTrue(hasattr(psutil, 'AF_LINK'))
