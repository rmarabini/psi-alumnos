# play scholar check as white
import asyncio
from consumer_main import _main, _init


moves = [  # from to promoted_piece
      ["e2", "e4", ""],
      ["e7", "e5", ""],
      ["d1", "f3", ""],
      ["b8", "c6", ""],
      ["f1", "c4", ""],
      ["a8", "b8", ""],
      ["f3", "f7", ""],
      ["xx", "xx", ""]  # moves should be even, just reject the last one
    ]


# clean data base and create users and games
user1, user1_token, user2, game = _init()

# play game
asyncio.get_event_loop().run_until_complete(
    _main(user1, user1_token, game, moves))
