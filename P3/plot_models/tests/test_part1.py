"""
Test de la Parte 1: Backend con Django y Django REST Framework.

Este módulo contiene 50 tests organizados en 7 clases que verifican:
- Modelos de datos (Sensor, Measurement, Dashboard, Plot)
- Autenticación JWT (obtención, renovación, uso de tokens)
- Endpoints REST sin autenticación (deben devolver 401)
- CRUD completo de sensores, mediciones, dashboards y plots
- Filtrado mediante query parameters

Ejecutar con: python manage.py test plot_models.tests.test_part1 --verbosity 2
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from ..models import Sensor, Measurement, Dashboard, Plot


class AuthMixin:
    """Mixin que configura autenticación JWT para tests que la requieren."""
    def setUp(self):
        self.user = User.objects.create_user(
            username='alumnodb', password='alumnodb'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


class ModelTests(APITestCase):
    """Tests de modelos: representación str, unicidad, ordenamiento, cascada."""

    def test_sensor_str(self):
        """Verifica que __str__ de Sensor devuelve su nombre."""
        sensor = Sensor.objects.create(name='Test Sensor')
        self.assertEqual(str(sensor), 'Test Sensor')

    def test_measurement_str(self):
        """Verifica que __str__ de Measurement incluye nombre del sensor y valor."""
        sensor = Sensor.objects.create(name='Temp Sensor')
        m = Measurement.objects.create(
            sensor=sensor,
            timestamp='2026-07-01T10:00:00Z',
            value=23.5
        )
        self.assertIn('Temp Sensor', str(m))
        self.assertIn('23.5', str(m))

    def test_dashboard_str(self):
        """Verifica que __str__ de Dashboard devuelve su nombre."""
        user = User.objects.create_user(username='u', password='p')
        d = Dashboard.objects.create(name='My Dashboard', user=user)
        self.assertEqual(str(d), 'My Dashboard')

    def test_measurement_ordering(self):
        """Verifica que Measurement se ordena por timestamp descendente."""
        sensor = Sensor.objects.create(name='S')
        m1 = Measurement.objects.create(
            sensor=sensor, timestamp='2026-07-01T10:00:00Z', value=1.0)
        m2 = Measurement.objects.create(
            sensor=sensor, timestamp='2026-07-01T11:00:00Z', value=2.0)
        qs = Measurement.objects.all()
        self.assertEqual(qs.first(), m2)
        self.assertEqual(qs.last(), m1)

    def test_sensor_unique_name(self):
        """Verifica que el nombre de Sensor debe ser único."""
        Sensor.objects.create(name='Unique')
        with self.assertRaises(Exception):
            Sensor.objects.create(name='Unique')

    def test_plot_defaults(self):
        """Verifica valores por defecto de Plot (chart_type, aggregation, etc.)."""
        user = User.objects.create_user(username='u', password='p')
        sensor = Sensor.objects.create(name='S')
        dashboard = Dashboard.objects.create(name='D', user=user)
        plot = Plot.objects.create(
            dashboard=dashboard, title='P', sensor=sensor)
        self.assertEqual(plot.chart_type, 'line')
        self.assertEqual(plot.aggregation, 'avg')
        self.assertEqual(plot.time_window, '1h')
        self.assertEqual(plot.refresh_interval, 5)
        self.assertEqual(plot.x, 0)
        self.assertEqual(plot.y, 0)
        self.assertEqual(plot.width, 6)
        self.assertEqual(plot.height, 4)
        self.assertEqual(plot.settings, {})

    def test_plot_ordering(self):
        """Verifica que Plot se ordena por (y, x) ascendente."""
        user = User.objects.create_user(username='u', password='p')
        sensor = Sensor.objects.create(name='S')
        dashboard = Dashboard.objects.create(name='D', user=user)
        p1 = Plot.objects.create(
            dashboard=dashboard, title='P1', sensor=sensor,
            y=0, x=1)
        p2 = Plot.objects.create(
            dashboard=dashboard, title='P2', sensor=sensor,
            y=0, x=0)
        qs = Plot.objects.all()
        self.assertEqual(qs.first(), p2)
        self.assertEqual(qs.last(), p1)

    def test_cascade_delete_sensor(self):
        """Verifica que al borrar Sensor se borran sus Measurements."""
        sensor = Sensor.objects.create(name='S')
        Measurement.objects.create(
            sensor=sensor, timestamp='2026-07-01T10:00:00Z', value=1.0)
        sensor.delete()
        self.assertEqual(Measurement.objects.count(), 0)

    def test_cascade_delete_dashboard(self):
        """Verifica que al borrar Dashboard se borran sus Plots."""
        user = User.objects.create_user(username='u', password='p')
        sensor = Sensor.objects.create(name='S')
        dashboard = Dashboard.objects.create(name='D', user=user)
        Plot.objects.create(dashboard=dashboard, title='P', sensor=sensor)
        dashboard.delete()
        self.assertEqual(Plot.objects.count(), 0)


class JWTTokenTests(APITestCase):
    """Tests de autenticación JWT: obtención, renovación y uso de tokens."""

    def test_obtain_token(self):
        """Verifica que credenciales válidas devuelven tokens access y refresh."""
        User.objects.create_user(username='alumnodb', password='alumnodb')
        response = self.client.post('/api/v1/token/', {
            'username': 'alumnodb',
            'password': 'alumnodb'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Verifica que credenciales inválidas devuelven 401."""
        response = self.client.post('/api/v1/token/', {
            'username': 'bad',
            'password': 'bad'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Verifica que el token refresh permite obtener un nuevo access token."""
        User.objects.create_user(username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        refresh = resp.data['refresh']
        response = self.client.post('/api/v1/token/refresh/', {
            'refresh': refresh
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_access_token_authenticates(self):
        """Verifica que el access token permite autenticar peticiones a la API."""
        User.objects.create_user(username='alumnodb', password='alumnodb')
        resp = self.client.post('/api/v1/token/', {
            'username': 'alumnodb', 'password': 'alumnodb'
        }, format='json')
        token = resp.data['access']
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = client.get('/api/v1/sensors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UnauthenticatedTests(APITestCase):
    """Tests que verifican que todos los endpoints requieren autenticación."""

    def test_sensor_list_requires_auth(self):
        """Verifica que GET /sensors/ sin auth devuelve 401."""
        response = self.client.get('/api/v1/sensors/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_measurement_list_requires_auth(self):
        """Verifica que GET /measurements/ sin auth devuelve 401."""
        response = self.client.get('/api/v1/measurements/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dashboard_list_requires_auth(self):
        """Verifica que GET /dashboards/ sin auth devuelve 401."""
        response = self.client.get('/api/v1/dashboards/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_plot_list_requires_auth(self):
        """Verifica que GET /plots/ sin auth devuelve 401."""
        response = self.client.get('/api/v1/plots/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_obtain_returns_json_error(self):
        """Verifica que credenciales inválidas devuelven error JSON estructurado."""
        response = self.client.post('/api/v1/token/', {
            'username': 'x', 'password': 'y'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertIn('No active account', response.data['detail'])


class SensorTests(AuthMixin, APITestCase):
    """Tests CRUD completo de sensores a través de la API REST."""

    def test_create_sensor(self):
        """Verifica creación de sensor con todos los campos."""
        data = {
            'name': 'Test Sensor',
            'description': 'A test sensor',
            'location': 'Lab 101',
            'host_mac': 'aa:bb:cc:dd:ee:ff'
        }
        response = self.client.post('/api/v1/sensors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Sensor')
        self.assertEqual(response.data['description'], 'A test sensor')
        self.assertEqual(response.data['location'], 'Lab 101')
        self.assertEqual(response.data['host_mac'], 'aa:bb:cc:dd:ee:ff')
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)

    def test_list_sensors(self):
        """Verifica listado de todos los sensores."""
        Sensor.objects.create(name='S1')
        Sensor.objects.create(name='S2')
        response = self.client.get('/api/v1/sensors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_sensor(self):
        """Verifica obtención de un sensor específico por ID."""
        sensor = Sensor.objects.create(name='Unique', description='Test')
        response = self.client.get(f'/api/v1/sensors/{sensor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Unique')

    def test_update_sensor(self):
        """Verifica actualización parcial (PATCH) de un sensor."""
        sensor = Sensor.objects.create(name='Old')
        response = self.client.patch(
            f'/api/v1/sensors/{sensor.id}/',
            {'description': 'Updated description'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description')

    def test_delete_sensor(self):
        """Verifica borrado de un sensor."""
        sensor = Sensor.objects.create(name='Delete Me')
        response = self.client.delete(f'/api/v1/sensors/{sensor.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Sensor.objects.count(), 0)

    def test_create_sensor_duplicate_name(self):
        """Verifica que no se puede crear un sensor con nombre duplicado."""
        Sensor.objects.create(name='Unique')
        data = {'name': 'Unique'}
        response = self.client.post('/api/v1/sensors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_sensor_not_found(self):
        """Verifica que obtener un sensor inexistente devuelve 404."""
        response = self.client.get('/api/v1/sensors/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_sensor_minimal(self):
        """Verifica creación de sensor solo con campos obligatorios."""
        data = {'name': 'Minimal'}
        response = self.client.post('/api/v1/sensors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_sensor_full_put(self):
        """Verifica actualización completa (PUT) de un sensor."""
        sensor = Sensor.objects.create(
            name='Original', description='Desc',
            location='Here', host_mac='aa:bb:cc:dd:ee:ff')
        response = self.client.put(
            f'/api/v1/sensors/{sensor.id}/',
            {'name': 'Changed', 'description': 'New',
             'location': 'There', 'host_mac': '11:22:33:44:55:66'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Changed')


class MeasurementTests(AuthMixin, APITestCase):
    """Tests CRUD de mediciones y filtrado por sensor."""

    def setUp(self):
        super().setUp()
        self.sensor = Sensor.objects.create(name='Test Sensor')

    def test_create_measurement(self):
        """Verifica creación de medición con todos los campos."""
        data = {
            'sensor': self.sensor.id,
            'timestamp': '2026-07-01T10:00:00Z',
            'value': 23.5
        }
        response = self.client.post(
            '/api/v1/measurements/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['value'], 23.5)
        self.assertEqual(response.data['sensor_name'], 'Test Sensor')

    def test_list_measurements(self):
        """Verifica listado de todas las mediciones."""
        Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-01T10:00:00Z',
            value=10.0)
        Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-01T11:00:00Z',
            value=20.0)
        response = self.client.get('/api/v1/measurements/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_measurements_by_sensor(self):
        """Verifica filtrado de mediciones por sensor mediante query param."""
        other = Sensor.objects.create(name='Other')
        m1 = Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-01T10:00:00Z',
            value=10.0)
        Measurement.objects.create(
            sensor=other,
            timestamp='2026-07-01T10:00:00Z',
            value=99.0)
        response = self.client.get(
            f'/api/v1/measurements/?sensor={self.sensor.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], m1.id)

    def test_retrieve_measurement(self):
        """Verifica obtención de una medición específica por ID."""
        m = Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-01T10:00:00Z',
            value=15.0)
        response = self.client.get(f'/api/v1/measurements/{m.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['value'], 15.0)

    def test_delete_measurement(self):
        """Verifica borrado de una medición."""
        m = Measurement.objects.create(
            sensor=self.sensor,
            timestamp='2026-07-01T10:00:00Z',
            value=5.0)
        response = self.client.delete(f'/api/v1/measurements/{m.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_measurement_missing_required(self):
        """Verifica que falta campo obligatorio (sensor) devuelve 400."""
        data = {'timestamp': '2026-07-01T10:00:00Z', 'value': 1.0}
        response = self.client.post(
            '/api/v1/measurements/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_measurement_invalid_sensor(self):
        """Verifica que sensor inexistente devuelve 400."""
        data = {
            'sensor': 9999,
            'timestamp': '2026-07-01T10:00:00Z',
            'value': 1.0
        }
        response = self.client.post(
            '/api/v1/measurements/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_measurements_no_match(self):
        """Verifica que filtro por sensor inexistente devuelve lista vacía."""
        response = self.client.get('/api/v1/measurements/?sensor=9999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class DashboardTests(AuthMixin, APITestCase):
    """Tests CRUD de dashboards y verificación de plots anidados."""

    def test_create_dashboard(self):
        """Verifica creación de dashboard con todos los campos."""
        data = {
            'name': 'My Dashboard',
            'user': self.user.id,
            'title': 'Main View',
            'description': 'Shows system metrics'
        }
        response = self.client.post('/api/v1/dashboards/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'My Dashboard')
        self.assertEqual(response.data['title'], 'Main View')
        self.assertEqual(response.data['username'], 'alumnodb')
        self.assertEqual(response.data['plots'], [])

    def test_list_dashboards(self):
        """Verifica listado de todos los dashboards."""
        Dashboard.objects.create(name='D1', user=self.user)
        Dashboard.objects.create(name='D2', user=self.user)
        response = self.client.get('/api/v1/dashboards/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_dashboard(self):
        """Verifica obtención de un dashboard específico por ID."""
        d = Dashboard.objects.create(
            name='D1', user=self.user, title='Title')
        response = self.client.get(f'/api/v1/dashboards/{d.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Title')

    def test_dashboard_includes_nested_plots(self):
        """Verifica que el dashboard incluye los plots anidados."""
        dashboard = Dashboard.objects.create(
            name='D1', user=self.user)
        sensor = Sensor.objects.create(name='S')
        Plot.objects.create(
            dashboard=dashboard, title='CPU', sensor=sensor)
        Plot.objects.create(
            dashboard=dashboard, title='RAM', sensor=sensor)
        response = self.client.get(
            f'/api/v1/dashboards/{dashboard.id}/')
        self.assertEqual(len(response.data['plots']), 2)

    def test_update_dashboard(self):
        """Verifica actualización parcial (PATCH) de un dashboard."""
        d = Dashboard.objects.create(
            name='Old', user=self.user)
        response = self.client.patch(
            f'/api/v1/dashboards/{d.id}/',
            {'name': 'Updated'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated')

    def test_delete_dashboard(self):
        """Verifica borrado de un dashboard."""
        d = Dashboard.objects.create(name='Del', user=self.user)
        response = self.client.delete(f'/api/v1/dashboards/{d.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_dashboard_minimal(self):
        """Verifica creación de dashboard solo con campos obligatorios."""
        data = {'name': 'Minimal', 'user': self.user.id}
        response = self.client.post('/api/v1/dashboards/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PlotTests(AuthMixin, APITestCase):
    """Tests CRUD de plots y filtrado por dashboard."""

    def setUp(self):
        super().setUp()
        self.sensor = Sensor.objects.create(name='Test Sensor')
        self.dashboard = Dashboard.objects.create(
            name='Test Dash', user=self.user)

    def test_create_plot(self):
        """Verifica creación de plot con campos mínimos."""
        data = {
            'dashboard': self.dashboard.id,
            'title': 'CPU Usage',
            'sensor': self.sensor.id
        }
        response = self.client.post('/api/v1/plots/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'CPU Usage')
        self.assertEqual(response.data['sensor_name'], 'Test Sensor')
        self.assertEqual(response.data['chart_type'], 'line')
        self.assertEqual(response.data['x'], 0)
        self.assertEqual(response.data['y'], 0)

    def test_list_plots(self):
        """Verifica listado de todos los plots."""
        Plot.objects.create(
            dashboard=self.dashboard, title='P1', sensor=self.sensor)
        Plot.objects.create(
            dashboard=self.dashboard, title='P2', sensor=self.sensor)
        response = self.client.get('/api/v1/plots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_plots_by_dashboard(self):
        """Verifica filtrado de plots por dashboard mediante query param."""
        other_dash = Dashboard.objects.create(
            name='Other', user=self.user)
        p1 = Plot.objects.create(
            dashboard=self.dashboard, title='P1',
            sensor=self.sensor)
        Plot.objects.create(
            dashboard=other_dash, title='P2',
            sensor=self.sensor)
        response = self.client.get(
            f'/api/v1/plots/?dashboard={self.dashboard.id}')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], p1.id)

    def test_retrieve_plot(self):
        """Verifica obtención de un plot específico por ID."""
        p = Plot.objects.create(
            dashboard=self.dashboard, title='P1', sensor=self.sensor)
        response = self.client.get(f'/api/v1/plots/{p.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_plot(self):
        """Verifica actualización parcial (PATCH) de un plot."""
        plot = Plot.objects.create(
            dashboard=self.dashboard, title='Old',
            sensor=self.sensor)
        response = self.client.patch(
            f'/api/v1/plots/{plot.id}/',
            {'title': 'Updated', 'x': 3, 'y': 5},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated')
        self.assertEqual(response.data['x'], 3)
        self.assertEqual(response.data['y'], 5)

    def test_delete_plot(self):
        """Verifica borrado de un plot."""
        plot = Plot.objects.create(
            dashboard=self.dashboard, title='Del',
            sensor=self.sensor)
        response = self.client.delete(f'/api/v1/plots/{plot.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_plot_with_all_fields(self):
        """Verifica creación de plot con todos los campos opcionales."""
        data = {
            'dashboard': self.dashboard.id,
            'title': 'Full Plot',
            'sensor': self.sensor.id,
            'chart_type': 'bar',
            'aggregation': 'max',
            'time_window': '6h',
            'refresh_interval': 10,
            'settings': {'color': 'red'},
            'x': 2,
            'y': 3,
            'width': 12,
            'height': 6
        }
        response = self.client.post('/api/v1/plots/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['chart_type'], 'bar')
        self.assertEqual(response.data['aggregation'], 'max')
        self.assertEqual(response.data['width'], 12)

    def test_filter_plots_no_match(self):
        """Verifica que filtro por dashboard inexistente devuelve lista vacía."""
        response = self.client.get('/api/v1/plots/?dashboard=9999')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
