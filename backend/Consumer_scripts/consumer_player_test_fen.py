# start from a non standard position
import asyncio
from consumer_main import _main, _init


# board with king's pawn in e4 and black king's pawn in e5
fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
moves = [
      ["d1", "f3", ""],
      ["b8", "c6", ""],
    ]

# clean data base and create users and games
user1, user1_token, user2, game = _init()
game.board_state = fen
game.save()

# play game
asyncio.get_event_loop().run_until_complete(
    _main(user1, user1_token, game, moves))
