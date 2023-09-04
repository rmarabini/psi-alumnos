# play scholar check as white
import asyncio
from consumer_main import _main, _init


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
      ["h2", "g1", "q"],    # moves should be even, just reject the last one
      ["a2", "a3", ""],
      ["g1", "h2", ""],
    ]


# clean data base and create users and games
user1, user1_token, user2, game = _init()

# play game
asyncio.get_event_loop().run_until_complete(
    _main(user1, user1_token, game, moves))
