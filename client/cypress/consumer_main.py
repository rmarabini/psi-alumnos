import json
import websockets
from models.models import ChessGame, ChessMove
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from models.consumers import ChessConsumer
from django.urls import path
from channels.routing import URLRouter

ws_url = "ws://localhost:8000/ws/play/"  # {gameID}/?{token_key}"
User = get_user_model()
application = URLRouter([
    path("ws/play/<int:gameID>/", ChessConsumer.as_asgi()),
])


def _init(consumerFirst=True):
    print("cleaning data base")
    ChessMove.objects.all().delete()
    ChessGame.objects.all().delete()
    User.objects.all().delete()

    # create user and get token
    print("creating user and token")
    user1 = User.objects.create_user(
                username='user1@example.com', password='sacacorchos')
    user2 = User.objects.create_user(
                username='user2@example.com', password='sacacorchos')
    user1_token, _ = Token.objects.get_or_create(
                user=user1)
    user1_token.save()

    # create game
    print("creating game with white user")
    if consumerFirst:
        game = ChessGame.objects.create(
                    whitePlayer=user1)
    else:
        game = ChessGame.objects.create(
                    blackPlayer=user1)
    game.save()  # single player
    return user1, user1_token, user2, game


async def _main(user, token, game, moves, consumerFirst=True):
    # 1) connect to websocket
    websocket = await websockets.connect(
        ws_url + f"{game.id}/?{token.key}")
    # 1.1) server should return a game message
    print("#### reading conecting message")
    message = await websocket.recv()
    messageD = json.loads(message)
    # 1.2) check everything went OK
    if (messageD['type'] != "game") or\
       (messageD["message"] != "OK") or\
       (messageD["status"] != ChessGame.PENDING):
        exit(1)
    else:
        print("    conecting message read")

    # 2) wait until second player joins
    # a connection message should be emitted by the server
    # with status=active
    print("#### wait for second player")
    message = await websocket.recv()
    messageD = json.loads(message)
    if (messageD['type'] != "game") or\
       (messageD["message"] != "OK") or\
       (messageD["status"] != ChessGame.ACTIVE):
        exit(1)
    else:
        print("    second player joined")

    # Now we can start playing
    for whiteMove, blackMove in zip(moves[0::2], moves[1::2]):
        print("#########PROCESING MOVE", whiteMove)
        if consumerFirst:
            _from = whiteMove[0]
            _to = whiteMove[1]
            _promotion = whiteMove[2]
        else:
            _from = blackMove[0]
            _to = blackMove[1]
            _promotion = blackMove[2]
        move_data = {
            "type": "move",
            "from": _from,
            "to": _to,
            "promotion": _promotion,
            "playerID": user.id
        }
        if consumerFirst:
            await websocket.send(json.dumps(move_data))
            print("####read my own move echo message")
        else:
            print("####read oponent move")
        message = await websocket.recv()
        messageD = json.loads(message)
        if messageD['type'] == "move":
            if (messageD["from"] != whiteMove[0]) or\
                 (messageD["to"] != whiteMove[1]):
                print(f"ERROR ({whiteMove}): ", messageD)
                exit(1)
            else:
                print(f"move echo for {whiteMove} received")
        else:
            print(f"ERROR ({whiteMove})", message)
            exit(1)

        if blackMove[0] == "xx":
            print("** skipping black move **")
            continue

        if not consumerFirst:
            print("####send my move", move_data)
            await websocket.send(json.dumps(move_data))
            print("####read my own move echo message")
        else:
            print("####read oponent move")
        message = await websocket.recv()
        messageD = json.loads(message)
        print("messageD", messageD)
        if messageD['type'] == "move":
            if (messageD["from"] != blackMove[0]) or\
                 (messageD["to"] != blackMove[1]):
                print(f"ERROR ({blackMove}): ", messageD)
                exit(1)
            else:
                print(f"move echo for {blackMove} received")
        else:
            print(f"ERROR ({whiteMove})", message)
            exit(1)

    # TODO: check game is finished
