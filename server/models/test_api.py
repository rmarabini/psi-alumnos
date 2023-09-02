from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
# from django.contrib.auth.models import User
from .models import ChessGame
from django.contrib.auth import get_user_model

# you may modify the following lines
URL = '/api/v1/games/'
# do not modify the code below

User = get_user_model()


class ChessGameAPITest(TestCase):

    def setUp(self):
        ChessGame.objects.all().delete()
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', password='testpassword')
        self.user2 = User.objects.create_user(
            username='user2', password='testpassword')

    def test_000_create_game(self):
        """Create a new game """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(URL, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChessGame.objects.count(), 1)
        chessgame = ChessGame.objects.first()
        result = (chessgame.whitePlayer == self.user1) or (
            chessgame.blackPlayer == self.user1)
        self.assertTrue(result)

    def test_005_update_game(self):
        """Update a game using the create method.
        That is, call create when an available game exists.
        whiteuser already exists"""
        game = ChessGame.objects.create(whitePlayer=self.user1)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'{URL}', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        game.refresh_from_db()
        self.assertEqual(game.blackPlayer, self.user2)

    def test_006_update_game(self):
        """Update a game using the create method.
        That is, call create when an available game exists.
        black user already exists"""
        game = ChessGame.objects.create(blackPlayer=self.user1)
        self.client.force_authenticate(
            user=self.user2)
        response = self.client.post(f'{URL}', {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        game.refresh_from_db()
        self.assertEqual(game.whitePlayer, self.user2)

    def test_007_update_active_game(self):
        """Update a game using the create method.
        when game.status is not 'pending.
        The update should fail"""
        game = ChessGame.objects.create(
            status=ChessGame.ACTIVE,
            whitePlayer=self.user1)
        game.save()
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'{URL}', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MyTokenCreateViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.token_url = '/api/v1/mytokenlogin/'

    def test_001_create_token(self):
        """ Redefine djoser serializer is such a way that the user.id and
        user.rating are returned in the response. By default only the token
        is returned."""
        response = self.client.post(self.token_url,
                                    {'username': 'testuser',
                                     'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('auth_token', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('rating', response.data)
