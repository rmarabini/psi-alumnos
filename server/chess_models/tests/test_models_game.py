from django.test import TransactionTestCase, tag
from chess_models.models import Player, Tournament, Round, Game
from chess_models.models import (
    LichessAPIError, TournamentType, Scores)
# from chess_models.models import getPoints, getRanking


class GameModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # create Tournament
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.DOUBLEROUNDROBIN)
        # create round
        round_name = 'round_01'
        self.round = Round.objects.create(
            name=round_name, tournament=tournament)
        # create two players
        self.players = []
        player = Player.objects.create(
            lichess_username='alpega')
        tournament.players.add(player)
        self.players.append(player)
        player = Player.objects.create(
            lichess_username='fernanfer')
        tournament.players.add(player)
        self.players.append(player)
        tournament.save()

    @tag("continua")
    def test_001_game_str_method(self):
        "create a game and test str method"
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.result = Scores.WHITE
        game.save()
        white = self.players[0]
        black = self.players[1]
        self.assertIn(
            f'{str(white)}({white.id}) vs {str(black)}({black.id}) ='
            f' {Scores.WHITE.label}',
            str(game)
            )

    # ROB: get_lichess_game_result needed
    @tag("continua")
    def test_002_game_get_result_from_lichess(self):
        """given a lichess game_id get the result of the game
        This function should connect to the lichess API
        """
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        winner, white, black = game.get_lichess_game_result('HsdNrFxG')
        self.assertEqual(white, self.players[0].lichess_username)
        self.assertEqual(black, self.players[1].lichess_username)
        self.assertEqual(winner.lower(), Scores.WHITE.value)

    @tag("continua")
    def test_003_game_get_result_from_lichess_invalid_game_id(self):
        """given a lichess game_id get the result of the game.
        gameID points to a game that has not been 
        played by the players 'white.lichess_username' and 
        'black.lichess_username". A exception should be raised
        """
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        with self.assertRaises(LichessAPIError):
            winner, white, black = game.get_lichess_game_result('kJfWZqUL')

    @tag("continua")
    def test_004_game_get_result_from_lichess_invalid_game_id(self):
        """given a lichess game_id get the result of the game.
        gameID is invalid thererefore a exception occurs.
        In this test the game does not exist.
        """
        game = Game.objects.create(round=self.round)
        game.white = self.players[0]
        game.black = self.players[1]
        game.save()
        with self.assertRaises(LichessAPIError):
            winner, white, black = game.get_lichess_game_result(
                'AAAAAAAAAAAAAAAAAAAAA')

    def test_010_getcross_table(self):
        "test get_cross_table"
        pass
