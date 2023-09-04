# test stalemate
import asyncio
from consumer_main import _main, _init

# board with king's pawn in e4 and black king's pawn in e5
fen = "1k6/8/PK6/8/8/8/8/8 w - - 0 1"
moves = [
      ["a6", "a7", ""],
      ["b8", "a8", ""],
      ["b6", "a6", ""],
      ["xx", "xx", ""],
    ]

# clean data base and create users and games
user1, user1_token, user2, game = _init()
game.board_state = fen
game.save()

# play game
asyncio.get_event_loop().run_until_complete(
    _main(user1, user1_token, game, moves))
