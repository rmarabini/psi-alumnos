# test draw for insuficient material
import asyncio
from consumer_main import _main, _init


# board with king's pawn in e4 and black king's pawn in e5
fen = "8/8/3k4/8/4p3/3K4/8/8 w - - 0 1"
moves = [  # from to promoted piece
      ["d3", "e4", ""],
      ["xx", "xx", ""],
    ]

# clean data base and create users and games
user1, user1_token, user2, game = _init()
game.board_state = fen
game.save()

# play game
asyncio.get_event_loop().run_until_complete(
    _main(user1, user1_token, game, moves))
