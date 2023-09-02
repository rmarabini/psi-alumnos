from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Player, ChessGame, ChessMove

User = get_user_model()


class PlayerModelTest(TestCase):
    def test_001_player_str_method(self):
        "str method should return username and rating"
        player = Player.objects.create(username='testuser', rating=1200)
        self.assertEqual(str(player), 'testuser (1200)')

    def test_002_player_str_method_2(self):
        "default rating value should be -1"
        player = Player.objects.create(username='testuser2')
        self.assertEqual(str(player), 'testuser2 (-1)')


class ChessGameModelTest(TestCase):
    def setUp(self):
        "Create two players and an empty  game"
        self.player1 = Player.objects.create(username='player1', rating=1500)
        self.player2 = Player.objects.create(username='player2', rating=1600)
        self.game = ChessGame.objects.create(
            # whitePlayer=self.player1,
            # blackPlayer=self.player2,
            # status='pending',
            # board_state=ChessGame.DEFAULT_BOARD_STATE,
            # timeControl='10+5'
        )

    def test_001_chessgame_str_method(self):
        """str method should return game id and player names,
        or 'unknown' if no player is assigned"""
        white = 'unknown'
        black = 'unknown'
        # no players
        self.assertEqual(
            str(self.game),
            f'GameID=({self.game.id}) {white} vs {black}'
        )
        # only white player
        self.game.whitePlayer = self.player1
        white = self.player1
        self.assertEqual(
            str(self.game),
            f'GameID=({self.game.id}) {white} vs {black}'
        )
        # only black player
        self.game.whitePlayer = None
        self.game.blackPlayer = self.player2
        white = 'unknown'
        black = self.player2
        self.assertEqual(
            str(self.game),
            f'GameID=({self.game.id}) {white} vs {black}'
        )
        # both players
        self.game.whitePlayer = self.player1
        self.game.blackPlayer = self.player2
        white = self.player1
        black = self.player2
        self.assertEqual(
            str(self.game),
            f'GameID=({self.game.id}) {white} vs {black}'
        )

    def test_005_chessgame_default_status(self):
        """default status should be 'pending'
        and default board_state should be ChessGame.DEFAULT_BOARD_STATE
        """
        new_game = ChessGame.objects.create(
        )
        self.assertEqual(new_game.status, 'pending')
        self.assertEqual(new_game.board_state, ChessGame.DEFAULT_BOARD_STATE)
        # self.assertEqual(new_game.next_player, new_game.whitePlayer)


class ChessMoveModelTest(TestCase):
    def setUp(self):
        self.player1 = Player.objects.create(username='player1', rating=1500)
        self.player2 = Player.objects.create(username='player2', rating=1600)
        self.game = ChessGame.objects.create(
            whitePlayer=self.player1,
            blackPlayer=self.player2,
            status='active',
            board_state=ChessGame.DEFAULT_BOARD_STATE,
            timeControl='10+5'
        )

    def test_001_chessmove_str_method(self):
        move = ChessMove.objects.create(
            game=self.game,
            player=self.player1,
            move_from='e2',
            move_to='e4'
        )
        self.assertEqual(
            str(move),
            'player1 (1500): e2 -> e4'
        )

    def test_005_valid_chess_move(self):
        # Valid move from 'e2' to 'e4'
        move = ChessMove(
            game=self.game,
            player=self.player1,
            move_from='e2',
            move_to='e4'
        )
        move.save()

        updated_game = ChessGame.objects.get(id=self.game.id)
        self.assertEqual(
            updated_game.board_state,
            'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1'
        )

    def test_010_invalid_chess_move(self):
        # Invalid move (e2 to e7, not a valid pawn move)
        move = ChessMove(
            game=self.game,
            player=self.player1,
            move_from='e2',
            move_to='e7'
        )
        with self.assertRaises(ValueError):
            move.save()

        # The board state should not have been updated
        updated_game = ChessGame.objects.get(id=self.game.id)
        self.assertEqual(
            updated_game.board_state,
            ChessGame.DEFAULT_BOARD_STATE
        )

    def test_015_save_move_in_non_active_game(self):
        # Try to save a move for a non-active game
        self.game.status = 'finished'
        self.game.save()
        move = ChessMove(
            game=self.game,
            player=self.player1,
            move_from='e2',
            move_to='e4'
        )
        with self.assertRaises(Exception):
            move.save()

        # The board state should not have been updated
        updated_game = ChessGame.objects.get(id=self.game.id)
        self.assertEqual(
            updated_game.board_state,
            ChessGame.DEFAULT_BOARD_STATE
        )

    def test_020_promotion(self):
        fen = "rnbqkbnr/Pppppppp/p7/8/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1"
        self.game.board_state = fen
        self.game.save()
        move = ChessMove(
            game=self.game,
            player=self.player1,
            move_from='a7',
            move_to='b8',
            promotion='q'
        )
        move.save()
        updated_game = ChessGame.objects.get(id=self.game.id)
        self.assertEqual(
            updated_game.board_state,
            "rQbqkbnr/1ppppppp/p7/8/8/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
        )

    def test_025_castle(self):
        fen = "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R"\
              " w KQkq - 0 1"
        self.game.board_state = fen
        self.game.save()
        move = ChessMove(
            game=self.game,
            player=self.player1,
            move_from='e1',
            move_to='g1',
            promotion=''
        )
        move.save()
        updated_game = ChessGame.objects.get(id=self.game.id)
        self.assertEqual(
            updated_game.board_state,
            "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1"
            " b kq - 1 1"
        )
