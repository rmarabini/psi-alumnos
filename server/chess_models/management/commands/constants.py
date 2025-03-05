from chess_models.models import Scores
playerListCasita = [['ertopo', 1000],
                    ['soria49', 1001],
                    ['zaragozana', 1002],
                    ['Clavada', 1003],
                    ['rmarabini', 1004],
                    ['jpvalle', 1005],
                    ['oliva21', 1006],
                    ['Philippe2020', 1007],
                    ['eaffelix', 1008],
                    ['jrcuesta', 1009],
                    ]


####################
w = Scores.WHITE.value
b = Scores.BLACK.value
d = Scores.DRAW.value
casitaResults = {('ertopo', 'soria49'): ('VrAvmsHj', w),
                 ('zaragozana', 'ertopo'): ('d4iJwwx6', w),
                 ('ertopo', 'Clavada'): ('imtdajQ7', w),
                 ('rmarabini', 'ertopo'): ('HSZmXbAl', w),
                 ('ertopo', 'jpvalle'): ('TLBzPZi1', d),
                 ('oliva21', 'ertopo'): ('4dUXjjwz', b),
                 ('ertopo', 'Philippe2020'): ('zkTJkfSN', b),
                 ('eaffelix', 'ertopo'): ('hHq30XSt', d),
                 ('ertopo', 'jrcuesta'): ('tfjv7FIV', w),
                 ('soria49', 'zaragozana'): ('FvfbbxVz', w),
                 ('Clavada', 'soria49'): ('lvBzqq6r', w),
                 ('soria49', 'rmarabini'): ('oBJQXI1k', w),
                 ('jpvalle', 'soria49'): ('7cmUKdFn', b),
                 ('soria49', 'oliva21'): ('u3HmV0BJ', w),
                 ('Philippe2020', 'soria49'): ('FG72LOJK', b),
                 ('soria49', 'eaffelix'): ('1e3OdSDN', w),
                 ('soria49', 'jrcuesta'): ('1ZqpLQNZ', b),
                 ('zaragozana', 'Clavada'): ('Ayq4y0g9', b),
                 ('rmarabini', 'zaragozana'): ('fqjchXvi', d),
                 ('zaragozana', 'jpvalle'): ('Wsr9W01S', b),
                 ('oliva21', 'zaragozana'): ('TQDfnlrS', b),
                 ('zaragozana', 'Philippe2020'): ('6wDHDmoG', b),
                 ('eaffelix', 'zaragozana'): ('Sh4NsnZL', w),
                 ('zaragozana', 'jrcuesta'): ('ovdcpXi9', b),
                 ('Clavada', 'rmarabini'): ('XT3URyTm', b),
                 ('jpvalle', 'Clavada'): ('jk4IezIi', w),
                 ('Clavada', 'oliva21'): ('FfxogVAC', w),
                 ('Philippe2020', 'Clavada'): ('rC3obSqS', b),
                 ('Clavada', 'eaffelix'): ('5c9O1o1n', b),
                 ('Clavada', 'jrcuesta'): ('ngssXIs2', w),
                 ('rmarabini', 'jpvalle'): ('55ig1Unu', w),
                 ('oliva21', 'rmarabini'): ('AR5pzMCh', b),
                 ('rmarabini', 'Philippe2020'): ('nCTZTPLJ', w),
                 ('eaffelix', 'rmarabini'): ('MixjLiYJ', w), ##
                 ('rmarabini', 'jrcuesta'): ('TfRfymzv', w),
                 ('jpvalle', 'oliva21'): ('8sNzS9Gd', w),
                 ('Philippe2020', 'jpvalle'): ('Mwz7JDfV', w),
                 ('jpvalle', 'eaffelix'): ('cGOSnA1m', b),
                 ('jrcuesta', 'jpvalle'): ('9utalUJp', w),
                 ('oliva21', 'Philippe2020'): ('7AMLRY6O', b),
                 ('eaffelix', 'oliva21'): ('SqsAyCqy', w),
                 ('jrcuesta', 'oliva21'): ('zWQ9AkhW', w),
                 ('Philippe2020', 'eaffelix'): ('ztrkA9Z0', b),
                 ('jrcuesta', 'Philippe2020'): ('c6nEuUKV', b),
                 ('jrcuesta', 'eaffelix'): ('vOOoBeE4', b)
                 }

# [Site &quot;https://lichess.org/VrAvmsHj&quot;]
# [Date &quot;2024.05.30&quot;]
# [White &quot;ertopo&quot;]
# [Black &quot;soria49&quot;]
# [Result &quot;1-0&quot;]
# =============================
# [Site &quot;https://lichess.org/d4iJwwx6&quot;]
# [Date &quot;2024.05.24&quot;]
# [White &quot;zaragozana&quot;]
# [Black &quot;ertopo&quot;]
# [Result &quot;1-0&quot;]
# ===========================
# [Site &quot;https://lichess.org/TLBzPZi1&quot;]
# [Date &quot;2024.07.15&quot;]
# [White &quot;ertopo&quot;]
# [Black &quot;jpvalle&quot;]
# [Result &quot;1/2-1/2&quot;]
# =========================
# [Site &quot;https://lichess.org/4dUXjjwz&quot;]
# [Date &quot;2024.06.12&quot;]
# [White &quot;oliva21&quot;]
# [Black &quot;ertopo&quot;]
# [Result &quot;0-1&quot;]
