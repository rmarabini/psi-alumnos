from django.test import TestCase
from .models import Player
from rest_framework.authtoken.models import Token
from rest_framework import status

# You may modoify this variables to match your project
BASE_URL = '/api/v1/'

# Do not modify the code below


class DjoserEndpointsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.test_user = Player.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.token = Token.objects.create(user=self.test_user)

    def test_000_user_creation(self):
        # User data for the new user
        new_username = 'new_user'
        new_email = 'new_user@example.com'
        new_password = 'new_password'

        # Send a POST request to create the user
        data = {
            'username': new_username,
            'email': new_email,
            'password': new_password,
        }
        response = self.client.post(BASE_URL + 'users/', data)

        # Check if the user has been created successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the user is in the database
        user_exists = Player.objects.filter(username=new_username).exists()
        self.assertTrue(user_exists)

    def test_001_users_me_authenticated(self):
        # Set token-based authentication for the test client
        auth_header = 'Token ' + self.token.key

        # Send a GET request to retrieve user details using "/users/me/"
        response = self.client.get(
            BASE_URL + "users/me/",
            HTTP_AUTHORIZATION=auth_header)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the returned data contains the expected user details
        self.assertEqual(response.data['username'], self.test_user.username)

    def test_002_users_me_unauthenticated(self):
        # Send a GET request to retrieve user details without authentication
        response = self.client.get(BASE_URL + "users/me/")

        # Check if the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_010_user_login(self):
        # Test the '/token/login/' endpoint (POST request)
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(BASE_URL + 'token/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assert that a token is returned in the response
        self.assertIn('auth_token', response.data)
        user = Token.objects.get(key=response.data['auth_token']).user
        self.assertEqual(user, self.test_user)

    def test_token_login_invalid_credentials(self):
        # Send a POST request with invalid login credentials
        data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }
        response = self.client.post(BASE_URL + 'token/login/', data)

        # Check if the response status code is 400
        # (Bad Request) or 401 (Unauthorized)
        self.assertIn(response.status_code,
                      [status.HTTP_400_BAD_REQUEST,
                       status.HTTP_401_UNAUTHORIZED])

        # Check if the response does not contain the authentication token
        self.assertNotIn('auth_token', response.data)

    def test_token_logout_authenticated(self):
        # Set token-based authentication for the test client
        auth_header = 'Token ' + self.token.key

        # Send a POST request to the "/token/logout/"
        # endpoint with authentication
        response = self.client.post(
            BASE_URL + 'token/logout/',
            HTTP_AUTHORIZATION=auth_header)

        # Send a GET request to retrieve user details without authentication
        response = self.client.get(BASE_URL + "users/me/")

        # Check if the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_logout_unauthenticated(self):
        # Set token-based authentication for the test client
        auth_header = ''
        # Send a POST request to the "/token/logout/"
        # endpoint without authentication
        response = self.client.post(
            BASE_URL + 'token/logout/',
            HTTP_AUTHORIZATION=auth_header)

        # Check if the response status code is 401 (Unauthorized)
        # error code may be status.HTTP_401_UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
