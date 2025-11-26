import unittest
import requests
from rest_framework import status

# replace by your URL in render.com
# BASE_URL = "https://song-54se.onrender.com/api/v1/"
BASE_URL = "http://localhost:8000/api/v1/"  # Adjust if your endpoint is different


class TestDjoserLogin(unittest.TestCase):
    def setUp(self):
        # Replace with valid test credentials
        self.username = "alumnodb"
        self.password = "alumnodb"

    def test_01_login_success(self):
        # Make sure the URL is correct and the server is running
        # You can also print the BASE_URL to debug if needed
        # Send POST request to the login endpoint
        data = {
            "username": self.username,
            "password": self.password
        }
        url = BASE_URL + 'token/login/'
        response = requests.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("auth_token", response.json())

    def test_02_login_failure(self):
        data = {
            "username": self.username,
            "password": "wrong_password"
        }
        url = BASE_URL + 'token/login/'
        response = requests.post(url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("non_field_errors", response.json())

    def test_05_users_me_authenticated(self):
        # First login to get the token
        data = {
            "username": self.username,
            "password": self.password
        }
        url = BASE_URL + 'token/login/'
        response = requests.post(url, data=data)
        token = response.json().get("auth_token")
        # then we get users/me
        url = BASE_URL + 'users/me/'
        headers = {
              'Authorization': f'Token {token}'
        }
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.json())

    def test_10_random_song(self):
        url = BASE_URL + 'songs/random/'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.json())
        self.assertIn("artist", response.json())

    def test_16_top_songs_with_n_parameter(self):
        url = BASE_URL + 'songs/top/?n=2'
        response = requests.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)

    def test_17_top_songs_invalid_n(self):
        url = BASE_URL + 'songs/top/?n=invalid'
        response = requests.get(url)
        data = response.json()
        self.assertNotEqual(len(data), 2)

    def test_20_search_song_by_title_success(self):
        url = BASE_URL + 'songs/search/?title=Here%20in%20the%20real%20wo'
        response = requests.get(url)
        data = response.json()
        self.assertEqual(data[0]['artist'], "Alan Jackson")

    def test_30_create_songuser(self):
        # First login to get the token
        data = {
            "username": self.username,
            "password": self.password
        }
        url = BASE_URL + 'token/login/'
        response = requests.post(url, data=data)
        token = response.json().get("auth_token")
        print("Token for user:", token)
        
        # then get users/me for the user id
        url = BASE_URL + 'users/me/'
        headers = {
            'Authorization': f'Token {token}'
        }
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        user_id = response.json().get("id")
        print("User ID:", user_id)
        
        # then we need a song to create a songuser
        url = BASE_URL + 'songs/'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
        song_id = response.json()['results'][0].get("id")
        print("Song to create songuser:", song_id)

        # then we create the songuser
        url = BASE_URL + 'songusers/'
        headers = {
              'Authorization': f'Token {token}'
        }
        data = {
            "song": song_id,
            # "user": user_id, get it from token
            "correct_guesses": 2,
            "wrong_guesses": 0
        }
        response = requests.post(url, headers=headers, json=data)
        self.assertEqual(response.status_code, 201)
        print("Created songuser:", response)

    def test_31_create_invalid_songuser(self):
        # First login to get the token
        data = {
            "username": self.username,
            "password": self.password
        }
        url = BASE_URL + 'token/login/'
        response = requests.post(url, data=data)
        token = response.json().get("auth_token")
        
        # then get users/me for the user id
        url = BASE_URL + 'users/me/'
        headers = {
            'Authorization': f'Token {token}'
        }
        response = requests.get(url, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        user_id = response.json().get("id")
        
        # then we need a song to create a songuser
        url = BASE_URL + 'songs/'
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
        song_id = response.json()['results'][0].get("id")

        # logout
        url = BASE_URL + 'token/logout/'
        headers = {
            'Authorization': f'Token {token}'
        }
        response = requests.post(url, headers=headers)
        self.assertEqual(response.status_code, 204)
        # then we create the songuser
        url = BASE_URL + 'songusers/'
        headers = {
              'Authorization': f'Token {token}'
        }
        data = {
            "song": song_id,
            # "user": user_id, get it from token
            "correct_guesses": 2,
            "wrong_guesses": 0
        }
        response = requests.post(url, headers=headers, json=data)
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
