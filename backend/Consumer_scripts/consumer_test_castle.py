# play scholar check as white
import asyncio
from consumer_main import _main, _init


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
    ["xx", "xx", ""],
    ]


# clean data base and create users and games
user1, user1_token, user2, game = _init()

# play game
asyncio.get_event_loop().run_until_complete(
    _main(user1, user1_token, game, moves))
