from django.test import TestCase, tag
from chess_models.models import Referee
# import requests


class RefereeModelTest(TestCase):

    @tag("continua")
    def test_001_referee(self):
        "create a referee "
        referee_name = 'referee_01'
        referee_number = '12345678'
        referee = Referee.objects.create(
            name=referee_name, refereeNumber=referee_number)
        self.assertEqual(referee.name, referee_name)
        self.assertEqual(referee.refereeNumber, referee_number)

    @tag("continua")
    def test_002_referee_str_method(self):
        "create a referee and print it "
        referee_name = 'referee_01'
        referee_number = '12345678'
        referee = Referee.objects.create(
            name=referee_name, refereeNumber=referee_number)
        self.assertEqual(
            referee.__str__(), f'{referee_name} ({referee_number})')
