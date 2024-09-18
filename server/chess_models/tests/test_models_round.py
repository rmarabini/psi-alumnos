from django.test import TestCase, tag
from chess_models.models import Tournament, Round


class RoundModelTest(TestCase):
    @tag("continua")
    def test_001_round_tournament(self):
        "assign round to tournament"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        round_name = 'round_01'
        round = Round.objects.create(
            name=round_name, tournament=tournament)
        self.assertEqual(round.tournament, tournament)
