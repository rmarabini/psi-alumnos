from channels.testing import ChannelsLiveServerTestCase
from rest_framework.authtoken.models import Token
from .consumers import ChessConsumer
from models.models import ChessGame, ChessMove
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from django.urls import path
from channels.routing import URLRouter
from channels.db import database_sync_to_async
import logging
import chess
from channels.layers import get_channel_layer

User = get_user_model()
application = URLRouter([
    path("ws/play/<int:gameID>/", ChessConsumer.as_asgi()),
])


class ChessConsumerTests(ChannelsLiveServerTestCase):
    """Test the chess consumer"""
    def setUp(self):
        self.white_user = User.objects.create_user(
            username='white', password='testpassword')
        self.black_user = User.objects.create_user(
            username='black', password='testpassword')
        self.white_token, _ = Token.objects.get_or_create(
            user=self.white_user)
        self.black_token, _ = Token.objects.get_or_create(
            user=self.black_user)
        self.white_token.save()
        self.black_token.save()

        self.white_token_key = self.white_token.key
        self.black_token_key = self.black_token.key

        self.game = ChessGame.objects.create(
            whitePlayer=self.white_user)
        self.game.save()  # single player
        self.game2 = ChessGame.objects.create(
            whitePlayer=self.white_user,
            blackPlayer=self.black_user,
            status='active')
        self.game2.save()  # two players

    async def connect_and_verify(self, gameID, token_key):
        communicator = WebsocketCommunicator(
            application, f"/ws/play/{gameID}/?{token_key}")
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        return response, communicator

    async def test_000_chess_consumer_connect(self):
        """Test that the consumer is able to connect to the websocket"""
        self.gameID = self.game.id  # Valid game ID

        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")

        await communicator.disconnect()

    async def test_001_chess_consumer_connect_invalid_token(self):
        """Test that the consumer is able to connect to the websocket
            but the connection fails because
            the token is not valid"""
        self.gameID = self.game.id  # INvalid game ID

        response, communicator = await self.connect_and_verify(
            self.gameID,
            'invalid token key')
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"],
                         "Invalid token. Connection not authorized.")
        await communicator.disconnect()

    async def test_002_chess_consumer_connect_invalid_game(self):
        """Test that the consumer is able to connect to the websocket
            but the connection fails because
            the gameID is not valid"""
        def getGame():
            return ChessGame.objects.filter(id=self.gameID).exists()

        self.gameID = self.game.id  # Valid game ID
        while await database_sync_to_async(getGame)():
            self.gameID += 1
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"],
                         f"Invalid game with id {self.gameID}")
        await communicator.disconnect()

    async def test_003_chess_consumer_connect_invalid_user(self):
        """Test that the consumer is able to connect to the websocket
            but the connection fails because
            the pair (user,game) is not valid"""

        self.gameID = self.game.id  # Valid game ID
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.black_token_key)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"],
                         f"Invalid game with id {self.gameID}")
        await communicator.disconnect()

    async def test_004_chess_consumer_connect_two_players(self):
        """Test that the consumer is able to connect to the websocket
           when the game has two joined players"""

        self.gameID = self.game2.id  # Valid game ID
        self.game.blackPlayer = self.black_user
        # await database_sync_to_async(saveGame)()
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.black_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        await communicator.disconnect()

    async def test_010_chess_consumer_receive_move(self):
        "send move to the websocket and check that it is received"
        def getLastMove(gameID):
            return ChessMove.objects.filter(game=gameID).order_by('id').last()

        def getWhiteUser(move):
            return move.player

        self.gameID = self.game2.id  # Valid game ID

        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        # self.assertEqual(response["type"], "game")
        # self.assertEqual(response["message"], "OK")
        await communicator.send_json_to({
            "type": "move",
            "from": "e2",
            "to": "e4",
            "playerID": self.white_user.id,
            "promotion": "",
        })

        try:
            response = await communicator.receive_json_from()
        except Exception as e:
            print("Exceptionn", e)
        print("response", response)
        self.assertEqual(response["type"], "move")
        self.assertEqual(response["from"], "e2")
        self.assertEqual(response['to'], "e4")
        self.assertEqual(response["playerID"], self.white_user.id)
        self.assertEqual(response["promotion"], "")

        await communicator.disconnect()

        # CHECK DATABASE
        move = await database_sync_to_async(getLastMove)(self.gameID)
        self.assertEqual(move.move_from, "e2")
        self.assertEqual(move.move_to, "e4")
        # if I do not call getWhiteUser, move.player returns an error
        # because it is a lazy object
        _ = await database_sync_to_async(getWhiteUser)(move)
        self.assertEqual(move.player, self.white_user)

    async def test_011_chess_consumer_receive_invalid_move(self):
        "send invalid move to the websocket and check"
        " that it is received and rejected"
        self.gameID = self.game2.id  # Valid game ID

        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        await communicator.send_json_to({
            "type": "move",
            "from": "e2",
            "to": "e5",
            "playerID": self.white_user.id,
            "promotion": "",
        })

        try:
            response = await communicator.receive_json_from()
        except Exception as e:
            print("Exceptionn", e)
        self.assertEqual(response["type"], "error")
        self.assertEqual(response["message"][:24], "Error: invalid move e2e5")
        await communicator.disconnect()

    async def test_012_chess_consumer_receive_wrong_status(self):
        "send move for a game that is finished"
        def saveGame(game):
            game.save()

        self.gameID = self.game2.id  # Valid game ID
        self.game2.status = 'finished'
        await database_sync_to_async(saveGame)(self.game2)
        response, communicator = await self.connect_and_verify(
            self.gameID,
            self.white_token_key)
        self.assertEqual(response["type"], "game")
        self.assertEqual(response["message"], "OK")
        await communicator.send_json_to({
            "type": "move",
            "from": "e2",
            "to": "e4",
            "playerID": self.white_user.id,
            "promotion": "",
        })

        try:
            response = await communicator.receive_json_from()
        except Exception as e:
            print("Exceptionn", e)
        logging.info(f"response: {response}")
        self.assertEqual(response["type"], "error")
        self.assertEqual(
            response["message"],
            "Error: invalid move (game is not active)")
        await communicator.disconnect()

    async def test_020_scholar_mate(self):
        # scholar's check
        moves = [  # from to promoted_piece
            ["e2", "e4", ""],
            ["e7", "e5", ""],
            ["d1", "f3", ""],
            ["b8", "c6", ""],
            ["f1", "c4", ""],
            ["a8", "b8", ""],
            ["f3", "f7", ""],
            ]
        await self.play_a_few_moves(moves)

    async def test_021_promotion(self):
        # promotion
        moves = [  # from to promoted_piece
            ["e2", "e4", ""],
            ["e7", "e5", ""],
            ["f2", "f4", ""],
            ["e5", "f4", ""],
            ["g2", "g3", ""],
            ["f4", "g3", ""],
            ["d1", "e2", ""],
            ["g3", "h2", ""],
            ["e2", "g4", ""],
            ["h2", "g1", "q"],
            ["a2", "a3", ""],
            ["g1", "h2", ""],
            ]

        await self.play_a_few_moves(moves)

    async def test_022_castle(self):
        # castle
        moves = [  # from to promoted_piece
            ["e2", "e4", ""],
            ["e7", "e5", ""],
            ["f1", "c4", ""],
            ["f8", "c5", ""],
            ["g1", "f3", ""],
            ["g8", "f6", ""],
            ["e1", "g1", ""],
            ["d7", "d6", ""],
            ["f1", "e1", ""],
            ]

        await self.play_a_few_moves(moves)

    async def play_a_few_moves(self, moves):
        """Play a few moves and check that the consumer works
        as it should
        """

        # When you try to run game.save()
        # you are trying to commit a transaction.
        # And this cannot happen until the end of the
        # test because TestCase wraps each test within
        # a transaction. It waits until the end of the
        # test to create this object. So you need to
        # use database_sync_to_async to run the save
        # method in the event loop but this seems to
        # conflict with the communicator open

        def saveGame(game):
            game.save()

        gameID = self.game.id
        response1, communicator1 = await self.connect_and_verify(
            gameID, self.white_token_key)
        # Check mensage sent back to the client
        self.assertEqual(response1["type"], "game")
        self.assertEqual(response1["message"], "OK")
        self.assertEqual(response1["status"], ChessGame.PENDING)
        print("status1", response1["status"])

        # close comunicator
        await communicator1.disconnect()

        # update game status
        self.game.blackPlayer = self.black_user
        self.game.status = 'active'
        await database_sync_to_async(saveGame)(self.game)

        # reopen comunicator
        response1, communicator1 = await self.connect_and_verify(
            gameID, self.white_token_key)

        print("saveGame", self.game, flush=True)

        response2, communicator2 = await self.connect_and_verify(
            gameID, self.black_token_key)
        # this second connection from communicator2 returns a message
        # for comunicator1
        response3 = await communicator1.receive_json_from()

        self.assertEqual(response2["type"], "game")
        self.assertEqual(response2["message"], "OK")
        self.assertEqual(response2["status"], ChessGame.ACTIVE)
        print("status2", response2["status"])

        self.assertEqual(response3["type"], "game")
        self.assertEqual(response3["message"], "OK")
        self.assertEqual(response3["status"], ChessGame.ACTIVE)
        print("status3", response3["status"])

        # Initialize the board state
        board_state = chess.STARTING_FEN

        # Play moves
        board = chess.Board(board_state)
        for move in moves:
            # Determine which player's turn it is
            current_communicator = communicator1 if board.turn == chess.WHITE\
                else communicator2
            current_playerID = self.white_user.id if board.turn == chess.WHITE\
                else self.black_user.id
            print("send move", move)
            move_data = {
                "type": "move",
                "from": move[0],
                "to": move[1],
                "playerID": current_playerID,
                "promotion": move[2],
            }

            # Send the move data
            await current_communicator.send_json_to(move_data)

            # Receive and validate the response
            response = await communicator1.receive_json_from()
            self.assertEqual(response["type"], "move")
            response = await communicator2.receive_json_from()
            self.assertEqual(response["type"], "move")
            board.push(chess.Move.from_uci(move[0] + move[1] + move[2]))

        # Disconnect both players
        await communicator1.disconnect()
        await communicator2.disconnect()

# check that the game is finished
# check winning player

    async def test_030_disconnect_removes_user_from_group(self):
        print("get_channel_layer()-1", get_channel_layer().groups)
        gameID = self.game2.id
        response, communicator = await self.connect_and_verify(
            gameID, self.white_token_key)
        print("get_channel_layer()-2", get_channel_layer().groups.keys())
        # Disconnect the user
        self.assertTrue(str(gameID) in get_channel_layer().groups.keys())
        await communicator.disconnect()
        self.assertFalse(str(gameID) in get_channel_layer().groups.keys())
        print("get_channel_layer()-3", get_channel_layer().groups.keys())
        # Check that the user is no longer in the group
        channel_layer = get_channel_layer()
        self.assertTrue(channel_layer.groups == {})

    async def test_031_after_disconnect_no_messages(self):
        gameID = self.game2.id
        response, communicator = await self.connect_and_verify(
            gameID, self.white_token_key)
        # Disconnect the user
        await communicator.disconnect()
        # check that is not possible to send messages after disconnection
        move_data = {
            "type": "move",
            "from": 'e2',
            "to": 'e4',
            "playerID": self.white_user.id,
            "promotion": "",
        }
        # Send the move data
        await communicator.send_json_to(move_data)

        # Ensure no message is received after trying to send
        import asyncio
        with self.assertRaises(asyncio.TimeoutError):
            _ = await communicator.receive_json_from()
