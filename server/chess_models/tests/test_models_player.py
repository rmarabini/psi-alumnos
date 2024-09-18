from chess_models.tests.constants import (
    lichess_usernames_6)
from chess_models.models import Player, LichessAPIError
from django.test import TransactionTestCase, tag
import requests
import uuid


class PlayerModelTest(TransactionTestCase):
    """Test the Player model"""
    # reset_sequences is used in the father class
    reset_sequences = True  # noqa E301

    def test_001_player_str_method(self):
        "create user and test str method"
        lichess_username = lichess_usernames_6[0]
        player = Player.objects.create(
            lichess_username=lichess_username)
        self.assertEqual(str(player), lichess_username)

    @tag("continua")
    def test_002_player_update_model(self):
        """create two users with the same lichess_username
        The result should be: First created a user
        and then update the user. Note that objects.create
        does a force_create so Django will not first check
         if it can update in the database.
        """
        lichess_username = lichess_usernames_6[0]
        player = Player.objects.create(
            lichess_username=lichess_username)
        self.assertEqual(str(player), lichess_username)
        player2 = Player(
            lichess_username=lichess_username,
            name='new_name')
        player2.save()
        self.assertEqual(str(player2), lichess_username)
        self.assertEqual(player2.name, 'new_name')
        self.assertEqual(player.id, player2.id)

    @tag("continua")
    def test_003_player_get_lichess_user_ranting(self):
        "Player should get user rating from lichess API"
        "if lichess_username is defined"
        lichess_username = lichess_usernames_6[0]
        player = Player.objects.create(
            lichess_username=lichess_username)
        player.get_lichess_user_ratings()
        url = f"https://lichess.org/api/user/{lichess_username}"
        response = requests.get(url)
        data = response.json()
        self.assertEqual(
            data['perfs']['bullet']['rating'],
            player.lichess_rating_bullet)
        self.assertEqual(
            data['perfs']['blitz']['rating'],
            player.lichess_rating_blitz)
        self.assertEqual(
            data['perfs']['rapid']['rating'],
            player.lichess_rating_rapid)
        self.assertEqual(
            data['perfs']['classical']['rating'],
            player.lichess_rating_classical)

    @tag("continua")
    def test_004_player_get_lichess_user_ranting_exception(self):
        """Player should has a method to get lichess user rating
        and raise exception if user does not exist.
        Check the exception is raised when the user does not exist"""
        # invalid username
        player = Player(lichess_username=str(uuid.uuid4()))
        with self.assertRaises(LichessAPIError):
            player.get_lichess_user_ratings()

    # ROB check_lichess_user_exists
    @tag("continua")
    def test_005_player_invalid_lichess_user(self):
        "Check if function check_lichess_user_exists exits"
        lichess_username = lichess_usernames_6[0]
        player = Player(lichess_username=str(uuid.uuid4()))
        self.assertFalse(player.check_lichess_user_exists())
        # valid username
        player = Player(lichess_username=lichess_username)
        self.assertTrue(player.check_lichess_user_exists())

    @tag("continua")
    def test_006_create_no_lichess_user(self):
        "Create player without lichess username"
        name = 'user1'
        email = 'user1@gmail.com'
        player = Player.objects.create(fide_id='123456',
                                       name=name,
                                       email=email
                                       )
        player.save()
        self.assertEqual(player.lichess_rating_bullet, 0)

    @tag("continua")
    def test_007_player_update_model_no_lichess_user(self):
        """create two users with the same pair
        (name, email)
        The result should be: First created a user
        and then update the user. Note that objects.create
        does a force_create so Django will not first check
         if it can update in the database.
        """
        name = 'user1'
        email = 'user1@gmail.com'
        player = Player.objects.create(
            name=name, email=email)
        self.assertEqual(str(player), name)
        player2 = Player(
            name=name, email=email,
            country='ES')
        player2.save()
        self.assertEqual(str(player2), name)
        self.assertEqual(player2.country, 'ES')
        self.assertEqual(player.id, player2.id)
