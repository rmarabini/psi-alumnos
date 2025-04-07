from django.test import tag, TransactionTestCase
from rest_framework.test import APIClient
from rest_framework import status
# from django.contrib.auth.models import User
from chess_models.models import (Player, Game, RankingSystem,
                                 Round, Tournament, Scores,
                                 TournamentType, TournamentSpeed,
                                 TournamentBoardType, LICHESS_USERS
                                 )
from api.views import CustomPagination
from django.contrib.auth.models import User
from chess_models.management.commands.constants import (playerListCasita,
                                                        casitaResults)
from chess_models.models.game import create_rounds
# from django.db import connection
# from django.apps import apps
# from django.conf import settings

# from chess_models.models.other_models import LichessAPIError

# you may modify the following lines
URLTOURNAMENT = '/api/v1/tournaments/'
URLSEARCH = '/api/v1/searchTournaments/'
GETPLAYERS = '/api/v1/get_players/'
# do not modify the code below


class TournamentAPITest(TransactionTestCase):
    """Test the tournament API"""
    reset_sequences = True

    def setUp(self):
        # I do not think deleted is needed
        # since the system should reset the database
        # before each test
        Tournament.objects.all().delete()
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1',
                                              password='testpassword')

    @tag("continua")
    def test_000_create_tournament(self):  # OK
        """Create a new tournament """
        self.client.force_authenticate(user=self.user1)
        tournament_name = "tournament_1"
        data = {'name': tournament_name,
                'tournament_type': TournamentType.SWISS,
                'tournament_speed': TournamentSpeed.CLASSICAL,
                'board_type': TournamentBoardType.LICHESS,
                'players':
                'lichess_username\neaffelix\noliva21\nrmarabini\nzaragozana'
                }
        self.assertEqual(Tournament.objects.count(), 0)
        response = self.client.post(URLTOURNAMENT, data)
        # print("response", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 1)
        tournament = Tournament.objects.first()
        # result = (tournament.name == "tournament_1")
        # print("tournament.name", tournament.name)
        self.assertTrue(tournament_name in tournament.name)
        self.assertEqual(tournament.id, 1)

    @tag("continua")
    def test_001_create_tournament_nologin(self):  # OK
        """Try to create a new tournament without login
        The request should fail"""
        data = {'tournament_type': TournamentType.SWISS,
                'tournament_speed': TournamentSpeed.CLASSICAL,
                'board_type': TournamentBoardType.LICHESS}
        self.assertEqual(Tournament.objects.count(), 0)
        response = self.client.post(URLTOURNAMENT, data)
        # print("response", response.data)
        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tournament.objects.count(), 0)

    @tag("continua")
    def test_002_list_tournament(self):  # OK
        """List tournaments in a 10 pagination
        No login is required
        """
        NoItems = 50
        for i in range(1, NoItems+1):
            Tournament.objects.create(
                name=f"tournament_{i:02d}",
                tournament_type=TournamentType.SWISS,
                tournament_speed=TournamentSpeed.CLASSICAL,
                board_type=TournamentBoardType.LICHESS,
                start_date=f"2021-0{(i//10)+1}-{(i%10)+1:02d}")
        # for t in Tournament.objects.all():
        #     print(t.id, t.start_date, t.name)
        response = self.client.get(URLTOURNAMENT)
        data = response.json()
        page_size = CustomPagination.page_size
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['results']), page_size)
        self.assertEqual(data['count'], NoItems)

        URL2 = URLTOURNAMENT + '?page=2'
        response = self.client.get(URL2)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data['results']), page_size)
        self.assertEqual(data['results'][0]['name'],
                         f"tournament_{(NoItems - page_size):02d}")

    @tag("continua")
    def test_003_get_tournament_details(self):  # OK
        i = 1
        t = Tournament.objects.create(
            name=f"tournament_{i:02d}",
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS,
            start_date=f"2021-0{(i//10)+1}-{(i%10)+1:02d}")
        rankingSystem1 = RankingSystem.BUCHHOLZ
        rankingSystem2 = RankingSystem.SONNEBORN_BERGER
        t.addToRankingList(rankingSystem1)
        t.addToRankingList(rankingSystem2)

        URL = URLTOURNAMENT + f'?{t.id}/'
        response = self.client.get(URL)
        data = response.json()
        # rankingList': ['BU', 'SB']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['results'][0]['name'], f"tournament_{i:02d}")
        self.assertEqual(data['results'][0]['rankingList'][0],
                         RankingSystem.BUCHHOLZ.value)
        self.assertEqual(data['results'][0]['rankingList'][1],
                         RankingSystem.SONNEBORN_BERGER.value)

    @tag("continua")
    def test_004_SearchTournamentsAPIView(self):  # OK
        # test the search tournament API

        # create several tournaments
        NoItemsX = 5
        NoItemsY = 4
        for x in range(1, NoItemsX+1):
            for y in range(1, NoItemsY+1):
                Tournament.objects.create(
                    name=f"tournament_{x:02d}_{y:02d}",
                    tournament_type=TournamentType.SWISS,
                    tournament_speed=TournamentSpeed.CLASSICAL,
                    board_type=TournamentBoardType.LICHESS
                    )
        # call search with a POST
        data = {'search_string': "_01_"}
        response = self.client.post(URLSEARCH, data)
        data = response.json()

        # check returned tournaments
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), NoItemsY)
        size = len(data)

        for i, t in enumerate(data):
            self.assertEqual(t['name'], f"tournament_01_{(size-i):02d}")


class GameAPITest(TransactionTestCase):
    """Test the game API"""
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1',
                                              password='testpassword')
        self.URLGAME = '/api/v1/games/'

    @tag("continua")
    def test_000_create_Game_NO_LOG_should_fail(self):  # OK
        """Create a new game without login in. It should fail """
        tournament = Tournament.objects.create(name="tournament_1",)
        round = Round.objects.create(name="round_1", tournament=tournament)
        player1 = Player.objects.create(name="player_1")
        player2 = Player.objects.create(name="player_2")
        tournament.players.add(player1)
        tournament.players.add(player2)
        tournament.save()

        data = {'white': player1.id,
                'black': player2.id,
                'round': round.id}
        response = self.client.post(self.URLGAME, data)
        self.assertEqual(response.data['detail'],
                         'Authentication credentials were not provided.')

    @tag("continua")
    def test_001_create_game_log_should_work(self):  # OK
        """Create a new game after loggin in. It should work """
        self.client.force_authenticate(user=self.user1)

        tournament = Tournament.objects.create(name="tournament_1",)
        round = Round.objects.create(name="round_1", tournament=tournament)
        player1 = Player.objects.create(name="player_1")
        player2 = Player.objects.create(name="player_2")
        tournament.players.add(player1)
        tournament.players.add(player2)
        tournament.save()
        data = {'white': player1.id,
                'black': player2.id,
                'round': round.id}
        response = self.client.post(self.URLGAME, data)
        # print("response", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)
        game = Game.objects.first()
        # # result = (tournament.name == "tournament_1")
        self.assertEqual(game.white.id, player1.id)
        self.assertEqual(game.black.id, player2.id)
        self.assertEqual(game.round.id, round.id)
        self.assertEqual(round.tournament.id, tournament.id)
        self.assertEqual(game.id, 1)
        self.assertEqual(player1.id, 1)
        self.assertEqual(player2.id, 2)
        self.assertEqual(round.id, 1)

    @tag("continua")
    def test_002_update(self):  # OK
        """Update a game with login in (as admin) 
           and finished=True.
            It should work
            Note: this sgould not work if no login has been made
            """
        self.client.force_authenticate(user=self.user1)
        tournament = Tournament.objects.create(name="tournament_1", administrativeUser=self.user1)
        round = Round.objects.create(name="round_1", tournament=tournament)
        player1 = Player.objects.create(name="player_1")
        player2 = Player.objects.create(name="player_2")
        tournament.players.add(player1)
        tournament.players.add(player2)
        tournament.save()
        game = Game.objects.create(white=player1,
                                   black=player2,
                                   round=round,
                                   finished=True)
        game.save()

        URLGAME = f'/api/v1/games/{game.id}/'
        data = {'result': Scores.WHITE.value}
        response = self.client.patch(URLGAME, data)
        game2 = Game.objects.get(id=game.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(game2.finished, True)
        self.assertEqual(game2.result, Scores.WHITE.value)

    @tag("continua")
    def test_003_update(self):  # OK
        """Update a game withOUT login in and finished=True.
          It should fail """
        tournament = Tournament.objects.create(name="tournament_1",)
        round = Round.objects.create(name="round_1", tournament=tournament)
        player1 = Player.objects.create(name="player_1")
        player2 = Player.objects.create(name="player_2")
        tournament.players.add(player1)
        tournament.players.add(player2)
        tournament.save()
        game = Game.objects.create(white=player1,
                                   black=player2,
                                   round=round,
                                   finished=True)
        game.save()

        URLGAME = f'/api/v1/games/{game.id}/'
        data = {'result': Scores.WHITE.value}
        response = self.client.patch(URLGAME, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @tag("continua")
    def test_004_update(self):  # OK
        """Update a game withOUT login in and finished=False.
          It should work """
        # No need to login first
        # self.client.force_authenticate(user=self.user1)
        tournament = Tournament.objects.create(name="tournament_1",)
        round = Round.objects.create(name="round_1", tournament=tournament)
        player1 = Player.objects.create(name="player_1")
        player2 = Player.objects.create(name="player_2")
        tournament.players.add(player1)
        tournament.players.add(player2)
        tournament.save()
        game = Game.objects.create(white=player1,
                                   black=player2,
                                   round=round,
                                   finished=False)
        game.save()

        URLGAME = f'/api/v1/games/{game.id}/'
        data = {'result': Scores.WHITE.value}
        response = self.client.patch(URLGAME, data)
        game2 = Game.objects.get(id=game.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(game2.finished, True)
        self.assertEqual(game2.result, Scores.WHITE.value)


class CreateRoundAPIViewTest(TransactionTestCase):
    """Test the round API"""
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.create_round_url = '/api/v1/create_round/'
        # reset sequences used in primary keys

    @tag("continua")
    def test_001_create_round(self):  # OK
        """ check create_round method
        It should create a round with games and
        NO results.
        Input: tournament_id
        """
        # reset DB sequences
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        tournament_id = tournament.id
        tournament.addToRankingList(RankingSystem.WINS.value)
        # create players
        NoItems = 10
        for i in range(NoItems):
            player = Player.objects.create(
                lichess_username=LICHESS_USERS[i])
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        self.client.force_authenticate(user=self.user)
        data = {'tournament_id': tournament_id,
                # 'swissByes':  [1, 2, 3],
                }
        response = self.client.post(
            self.create_round_url, data)
        # print("response", response)
        data = response.json()
        self.assertEqual(data['result'], True)
        self.assertEqual(tournament.round_set.count(), NoItems-1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tournament.getPlayers()), NoItems)
        self.assertEqual(len(tournament.getGames()), (NoItems-1)*(NoItems)//2)

    # ROB this test is not needed for continuous mode
    @tag("suiza")
    def test_005_create_round_swissByes(self):
        """ check create_round method
        It should create a round with games and
        NO results.
        Input: tournament_id
        users in Swiss_byes should be ignored
        """
        # reset DB sequences
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        tournament_id = tournament.id
        tournament.addToRankingList(RankingSystem.WINS.value)
        # create players
        NoItems = 10
        for i in range(NoItems):
            player = Player.objects.create(
                lichess_username=LICHESS_USERS[i])
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        self.client.force_authenticate(user=self.user)
        results =[
            {'white': 'ertopo', 'black': 'jpvalle'},
            {'white': 'oliva21', 'black': 'soria49'},
            {'white': 'zaragozana', 'black': 'Philippe2020'},
            {'white': 'eaffelix', 'black': 'Clavada'},
            {'white': 'rmarabini', 'black': 'jrcuesta'},
        ]
        swissByes = []
        data = {'tournament_id': tournament_id,
                'swissByes':  swissByes,
                }
        response = self.client.post(
            self.create_round_url, data, format='json')
        # print("response", response)
        data = response.json()
        self.assertEqual(data['result'], True)
        self.assertEqual(tournament.round_set.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tournament.getPlayers()), NoItems)
        # NoItems -= len(swissByes)
        self.assertEqual(len(tournament.getGames()), NoItems//2)
        games = Game.objects.all()
        for game, result in zip(games, results):
            self.assertEqual(game.white.lichess_username, result['white'])
            self.assertEqual(game.black.lichess_username, result['black'])

    # ROB this test is not needed for continuous mode
    @tag("suiza")
    def test_006_create_round_swissByes(self):
        """ check create_round method
        It should create a round with games and
        NO results.
        Input: tournament_id
        users in Swiss_byes should be ignored
        """
        # reset DB sequences
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        tournament_id = tournament.id
        tournament.addToRankingList(RankingSystem.WINS.value)
        # create players
        NoItems = 10
        for i in range(NoItems):
            player = Player.objects.create(
                lichess_username=LICHESS_USERS[i])
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        self.client.force_authenticate(user=self.user)
        swissByes = [1, 2]
        data = {'tournament_id': tournament_id,
                'swissByes':  swissByes,
                }
        response = self.client.post(
            self.create_round_url, data, format='json')
        # print("response", response)
        data = response.json()
        self.assertEqual(data['result'], True)
        self.assertEqual(tournament.round_set.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tournament.getPlayers()), NoItems)
        NoItems -= len(swissByes)
        self.assertEqual(len(tournament.getGames()), NoItems//2+2)
        games = Game.objects.all()
        results = [
            {'white': 'ertopo', 'black': 'H'},
            {'white': 'soria49', 'black': 'H'},
            {'white': 'zaragozana', 'black': 'oliva21'},
            {'white': 'Philippe2020', 'black': 'Clavada'},
            {'white': 'rmarabini', 'black': 'eaffelix'},
            {'white': 'jrcuesta', 'black': 'jpvalle'},
        ]
        for game, result in zip(games, results):
            self.assertEqual(game.white.lichess_username, result['white'])
            if result['black'] == 'H':
                self.assertEqual(game.black, None)
            else:
                self.assertEqual(game.black.lichess_username, result['black'])

    # ROB this test is not needed for continuous mode
    @tag("suiza")
    def test_007_create_round_swissByes(self):
        """ check create_round method
        It should create a round with games and
        NO results.
        Input: tournament_id
        users in Swiss_byes should be ignored
        """
        # reset DB sequences
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        tournament_id = tournament.id
        tournament.addToRankingList(RankingSystem.WINS.value)
        # create players
        NoItems = 10
        for i in range(NoItems):
            player = Player.objects.create(
                lichess_username=LICHESS_USERS[i])
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        self.client.force_authenticate(user=self.user)
        swissByes = [1, 2, 3]
        data = {'tournament_id': tournament_id,
                'swissByes':  swissByes,
                }
        response = self.client.post(
            self.create_round_url, data, format='json')
        # print("response", response)
        data = response.json()
        self.assertEqual(data['result'], True)
        self.assertEqual(tournament.round_set.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tournament.getPlayers()), NoItems)
        NoItems -= len(swissByes)
        self.assertEqual(len(tournament.getGames()), 7)
        results = [
            {'white': 'jrcuesta', 'black': None, 'result': Scores.BYE_U.value},
            {'white': 'ertopo', 'black': None, 'result': Scores.BYE_H.value},
            {'white': 'soria49', 'black': None, 'result': Scores.BYE_H.value},
            {'white': 'zaragozana', 'black': None, 'result': Scores.BYE_H.value},
            {'white': 'Clavada', 'black': 'oliva21', 'result': Scores.NOAVAILABLE.value},
            {'white': 'Philippe2020', 'black': 'rmarabini', 'result': Scores.NOAVAILABLE.value},
            {'white': 'jpvalle', 'black': 'eaffelix', 'result': Scores.NOAVAILABLE.value},
        ]
        games = Game.objects.all()
        for game, result in zip(games, results):
            # print("game", game)
            self.assertEqual(game.white.lichess_username, result['white'])
            if result['result'] != Scores.NOAVAILABLE.value:
                self.assertEqual(game.black, None)
            else:
                self.assertEqual(game.black.lichess_username, result['black'])
            self.assertEqual(game.result, result['result'])

    # ROB this test is not needed for continuous mode
    @tag("suiza")
    def test_010_create_round_swissByes_with_extraplayers(self):
        """ check create_round method
        It should create a round with games and
        NO results.
        Input: tournament_id
        users in Swiss_byes should be ignored
        """
        # reset DB sequences
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        tournament_id = tournament.id
        tournament.addToRankingList(RankingSystem.WINS.value)
        # create players
        # "ertopo",
        # "soria49",
        # "zaragozana",
        # "Clavada",
        # "rmarabini",
        # "jpvalle",
        # "oliva21",
        # "Philippe2020",
        # "eaffelix",
        # "jrcuesta",

        NoItems = 10  # eaffelix, jrcuesta
        for i in range(NoItems - 2):  # skip last two players
            player = Player.objects.create(
                lichess_username=LICHESS_USERS[i])
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        self.client.force_authenticate(user=self.user)
        results = [
            {'white': 'ertopo', 'black': 'jpvalle'},
            {'white': 'oliva21', 'black': 'soria49'},
            {'white': 'zaragozana', 'black': 'Philippe2020'},
            {'white': 'eaffelix', 'black': 'Clavada'},
            {'white': 'rmarabini', 'black': 'jrcuesta'},
        ]
        swissByes = []
        extaPlayers = 'lichess_username\n eaffelix\n jrcuesta\n'
        data = {'tournament_id': tournament_id,
                'swissByes':  swissByes,
                'extraPlayers': extaPlayers
                }
        response = self.client.post(
            self.create_round_url, data, format='json')
        # print("response", response)
        data = response.json()
        self.assertEqual(data['result'], True)
        self.assertEqual(tournament.round_set.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tournament.getPlayers()), NoItems)
        # NoItems -= len(swissByes)
        self.assertEqual(len(tournament.getGames()), NoItems//2)
        games = Game.objects.all()
        for game, result in zip(games, results):
            self.assertEqual(game.white.lichess_username, result['white'])
            self.assertEqual(game.black.lichess_username, result['black'])

    @tag("continua")
    def test_090_create_round(self):  # OK
        """ check create_round method with no login
        It should fail
        """
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        tournament_id = tournament.id
        # create players
        NoItems = 10
        for i in range(NoItems):
            player = Player.objects.create(name=f"player_{i}")
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        # do NOT loginin
        # self.client.force_authenticate(user=self.user)
        data = {'tournament_id': tournament_id,
                'swissByes':  [1, 2, 3],
                'rankingSystem': RankingSystem.WINS}
        response = self.client.post(
            self.create_round_url, data)
        data = response.json()
        self.assertEqual(data['detail'],
                         'Authentication credentials were not provided.')
        self.assertEqual(tournament.round_set.count(), 0)
        count = Game.objects.filter(
            round__tournament=tournament).count()
        self.assertEqual(count, 0)


class UpdateLichessGameAPIView(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.update_lichess_game_url = '/api/v1/update_lichess_game/'

    @tag("continua")
    def test_001_updateLichessGames(self):  # OK
        """ update lichess game
        """
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        # create players
        for username, id in playerListCasita:
            player = Player.objects.create(id=id, lichess_username=username)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)
        # Now there is a problem, the algorithm use to create
        # the games is not the same as the one used in lichess
        # so we may need to swap some of the players

        # update games
        for game in tournament.getGames():
            white = game.white.lichess_username
            black = game.black.lichess_username
            game_id = game.id
            # print(white, black, game)
            try:
                (lichess_game_id, result) = casitaResults[(white, black)]
            # OK the created games are not like the ones
            # in lichess let us swap users
            except Exception:
                (lichess_game_id, result) = casitaResults[(black, white)]
                game.white, game.black = game.black, game.white
                game.save()

            data = {'game_id': game_id,
                    'lichess_game_id': lichess_game_id}

            url = self.update_lichess_game_url
            response = self.client.post(url, data)
            results = response.json()
            game2 = Game.objects.get(id=game_id)
            self.assertEqual(result, game2.result)
            self.assertEqual(results['result'], True)
            # time.sleep(1)

    @tag("continua")
    def test_002_updateUnexistingLichessGames(self):  # OK
        """ update lichess game that does not exist
        It should fail
        """
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        # create players
        for username, id in playerListCasita:
            player = Player.objects.create(id=id, lichess_username=username)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)
        # Now there is aproblem the algorithm use to create
        # the games is not the same as the one used in lichess
        # so we may need to swap some of the players

        # update games
        white, black = 'ertopo', 'soria49'
        white_player = Player.objects.get(lichess_username=white)
        black_player = Player.objects.get(lichess_username=black)
        game = Game.objects.get(white=white_player.id,
                                black=black_player.id)
        game_id = game.id

        data = {'game_id': game_id,
                'lichess_game_id': "invalidinvalid"}

        url = self.update_lichess_game_url
        # with self.assertRaises(LichessAPIError) as context:
        response = self.client.post(url, data)
        results = response.json()
        self.assertEqual(results['result'], False)
        self.assertIn("Failed to fetch data for game",
                      results['message'])
        # self.assertIn("Failed to fetch data for game",
        #               str(context.exception))

    @tag("continua")
    def test_003_updatewrongplayersLichessGames(self):  # OK
        """ update lichess game with wrong players
        It should fail
        """
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.LICHESS)
        # create players
        for username, id in playerListCasita:
            player = Player.objects.create(id=id, lichess_username=username)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)
        # Now there is aproblem the algorithm use to create
        # the games is not the same as the one used in lichess
        # so we may need to swap some of the players

        # update games
        white, black = 'ertopo', 'soria49'
        white_player = Player.objects.get(lichess_username=white)
        black_player = Player.objects.get(lichess_username=black)
        game = Game.objects.get(white=white_player.id,
                                black=black_player.id)
        game_id = game.id

        data = {'game_id': game_id,
                'lichess_game_id': "lvBzqq6r"}

        url = self.update_lichess_game_url
        # with self.assertRaises(LichessAPIError) as context:
        response = self.client.post(url, data)
        results = response.json()
        self.assertEqual(results['result'], False)
        self.assertIn("Players for game lvBzqq6r are different",
                      results['message'])
        # self.assertIn(f"Players for game lvBzqq6r are different ",
        #              str(context.exception))


class UpdateOTBGameAPIViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.update_otb_game_url = '/api/v1/update_otb_game/'

    @tag("continua")
    def test_001_updateOTBGames(self):  # OK
        """ update OTB game by white player
        """
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB)
        # create players
        for username, id in playerListCasita:
            name = username
            email = f"{username}@example.com"
            player = Player.objects.create(id=id,
                                           name=name,
                                           email=email)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)

        # update games
        for i, game in enumerate(tournament.getGames()):
            name = game.white.name
            email = game.white.email
            game_id = game.id
            if i % 2 == 0:
                result = Scores.BLACK.value
            else:
                result = Scores.WHITE.value

            data = {'game_id': game_id,
                    'name': name,
                    'email': email,
                    'otb_result': result
                    }

            url = self.update_otb_game_url
            response = self.client.post(url, data)
            results = response.json()
            game2 = Game.objects.get(id=game_id)
            self.assertEqual(result, game2.result)
            self.assertEqual(results['result'], True)

    @tag("continua")
    def test_0015_updateOTBGames(self):  # OK
        """ update OTB game by black player
        """
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB)
        # create players
        for username, id in playerListCasita:
            name = username
            email = f"{username}@example.com"
            player = Player.objects.create(id=id,
                                           name=name,
                                           email=email)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)

        # update games
        for i, game in enumerate(tournament.getGames()):
            name = game.black.name
            email = game.black.email
            game_id = game.id
            if i % 2 == 0:
                result = Scores.BLACK.value
            else:
                result = Scores.WHITE.value

            data = {'game_id': game_id,
                    'name': name,
                    'email': email,
                    'otb_result': result
                    }

            url = self.update_otb_game_url
            response = self.client.post(url, data)
            results = response.json()
            game2 = Game.objects.get(id=game_id)
            self.assertEqual(result, game2.result)
            self.assertEqual(results['result'], True)

    @tag("continua")
    def test_002_updateWrongEmailGames(self):  # OK
        """ update lichess game that does not exist
        It should fail
        """
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB)
        # create players
        for username, id in playerListCasita:
            name = username
            email = f"{username}@example.com"
            player = Player.objects.create(id=id,
                                           name=name,
                                           email=email)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)

        # update games
        for i, game in enumerate(tournament.getGames()):
            name = game.white.name
            email = "wrongemail@example.com"
            game_id = game.id
            if i % 2 == 0:
                result = Scores.BLACK.value
            else:
                result = Scores.WHITE.value

            data = {'game_id': game_id,
                    'name': name,
                    'email': email,
                    'otb_result': result
                    }

            url = self.update_otb_game_url
            response = self.client.post(url, data)
            results = response.json()
            # self.assertEqual(result, Scores.NOAVAILABLE.value)
            game = Game.objects.get(id=game_id)
            # print("game", game, game.result)
            self.assertEqual(results['result'], False)
            self.assertEqual(game.result, Scores.NOAVAILABLE.value)


class GetRankingAPIViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from chess_models.management.commands.populate import Command
        self.client = APIClient()
        self.create_get_ranking_url = '/api/v1/get_ranking/'
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        command.insertData()      # Insert data into the database
        self.tournament_name = 'tie-breaking exercises swiss'
        # read tournament frok database
        self.tournament =\
            Tournament.objects.get(name=self.tournament_name)

    @tag("continua")
    def test_001_getRanking(self):  # OK
        """ retrieve ranking
        rank by score, wins and blacktimes
        """
        tournament_id = self.tournament.id
        self.tournament.cleanRankingList()
        self.tournament.addToRankingList(RankingSystem.WINS.value)
        self.tournament.addToRankingList(RankingSystem.BLACKTIMES.value)
        # data = {'tournament_id': tournament_id}

        response = self.client.get(
            self.create_get_ranking_url + f'{tournament_id}/')
        data = response.json()
        # print("data", data)
        playerD = {}
        playerD[ 2] = {'name': 'Bruno',    'score': 4.0, 'wins': 3, # noqa E201
                       'blacktimes': 3, 'rank': 1}
        playerD[16] = {'name': 'Stephan',  'score': 3.5, 'wins': 3, # noqa E201
                       'blacktimes': 2, 'rank': 2}  # noqa E201
        playerD[ 1] = {'name': 'Alyx',     'score': 3.5, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 3}  # noqa E201
        playerD[ 3] = {'name': 'Charline', 'score': 3.5, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 4}  # noqa E201
        playerD[ 4] = {'name': 'David',    'score': 3.5, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 5}  # noqa E201
        playerD[ 6] = {'name': 'Franck',   'score': 3.0, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 6}  # noqa E201
        playerD[ 5] = {'name': 'Elene',    'score': 2.5, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 7}  # noqa E201
        playerD[ 8] = {'name': 'Irina',    'score': 2.5, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 8}  # noqa E201
        playerD[11] = {'name': 'Maria',    'score': 2.5, 'wins': 1, # noqa E201
                       'blacktimes': 2, 'rank': 9}  # noqa E201
        playerD[15] = {'name': 'Reine',    'score': 2.0, 'wins': 2, # noqa E201
                       'blacktimes': 3, 'rank': 10}  # noqa E201
        playerD[14] = {'name': 'Paul',     'score': 2.0, 'wins': 2, # noqa E201
                       'blacktimes': 2, 'rank': 11}  # noqa E201
        playerD[12] = {'name': 'Nick (W)', 'score': 2.0, 'wins': 0, # noqa E201
                       'blacktimes': 0, 'rank': 12}  # noqa E201
        playerD[ 7] = {'name': 'Genevieve','score': 1.5, 'wins': 1, # noqa E201
                       'blacktimes': 3, 'rank': 13}  # noqa E201
        playerD[13] = {'name': 'Opal',     'score': 1.5, 'wins': 1, # noqa E201
                       'blacktimes': 3, 'rank': 14}  # noqa E201
        playerD[ 9] = {'name': 'Jessica',  'score': 1.5, 'wins': 0, # noqa E201
                       'blacktimes': 1, 'rank': 15}  # noqa E201
        playerD[10] = {'name': 'Lais',     'score': 1.0, 'wins': 1, # noqa E201 
                       'blacktimes': 3, 'rank': 16}  # noqa E201

        for k, v in data.items():
            # print(k, v)
            self.assertEqual(v['score'],
                             playerD[v['id']]['score'])
            self.assertEqual(
                v[RankingSystem.WINS.value],
                playerD[v['id']]['wins'])
            self.assertEqual(
                v[RankingSystem.BLACKTIMES.value],
                playerD[v['id']]['blacktimes'])
            self.assertEqual(v['rank'], playerD[v['id']]['rank'])

    @tag("suiza")
    def test_002_getRanking_buchholz(self):  # NO
        """ retrieve ranking
        rank by score, wins and blacktimes
        """
        tournament_id = self.tournament.id
        self.tournament.cleanRankingList()
        self.tournament.addToRankingList(RankingSystem.BUCHHOLZ.value)
        self.tournament.addToRankingList(RankingSystem.BLACKTIMES.value)
        # data = {'tournament_id': tournament_id}

        response = self.client.get(
            self.create_get_ranking_url + f'{tournament_id}/')
        data = response.json()
        playerD = {}
        playerD[ 2] = {'name': 'Bruno',    'score': 4.0,  # noqa E201
        'buchholz': 13.0, 'blacktimes': 3, 'rank': 1}  # noqa E201
        playerD[ 3] = {'name': 'Charline', 'score': 3.5,  # noqa E201
        'buchholz': 15.5, 'blacktimes': 2, 'rank': 2}  # noqa E201
        playerD[ 4] = {'name': 'David',    'score': 3.5,  # noqa E201
        'buchholz': 15.0, 'blacktimes': 2, 'rank': 3}  # noqa E201
        playerD[ 1] = {'name': 'Alyx',     'score': 3.5,  # noqa E201
        'buchholz': 12.5, 'blacktimes': 2, 'rank': 4}  # noqa E201
        playerD[16] = {'name': 'Stephan',  'score': 3.5,  # noqa E201
        'buchholz': 12.5, 'blacktimes': 2, 'rank': 5}  # noqa E201
        playerD[ 6] = {'name': 'Franck',   'score': 3.0,  # noqa E201
        'buchholz': 12.0, 'blacktimes': 2, 'rank': 6}  # noqa E201
        playerD[ 8] = {'name': 'Irina',    'score': 2.5,  # noqa E201
        'buchholz': 13.5, 'blacktimes': 2, 'rank': 7}  # noqa E201
        playerD[11] = {'name': 'Maria',    'score': 2.5,  # noqa E201
        'buchholz': 13.5, 'blacktimes': 2, 'rank': 8}  # noqa E201
        playerD[ 5] = {'name': 'Elene',    'score': 2.5,  # noqa E201
        'buchholz':  8.5, 'blacktimes': 2, 'rank': 9}  # noqa E201
        playerD[15] = {'name': 'Reine',    'score': 2.0,  # noqa E201
        'buchholz': 12.0, 'blacktimes': 3, 'rank': 10}  # noqa E201
        playerD[12] = {'name': 'Nick (W)', 'score': 2.0,  # noqa E201
        'buchholz': 11.5, 'blacktimes': 0, 'rank': 11}  # noqa E201
        playerD[14] = {'name': 'Paul',     'score': 2.0,  # noqa E201
        'buchholz': 11.0, 'blacktimes': 2, 'rank': 12}  # noqa E201
        playerD[ 7] = {'name': 'Genevieve','score': 1.5,  # noqa E201
        'buchholz': 14.5, 'blacktimes': 3, 'rank': 13}  # noqa E201
        playerD[13] = {'name': 'Opal',     'score': 1.5,  # noqa E201
        'buchholz': 14.0, 'blacktimes': 3, 'rank': 14}  # noqa E201
        playerD[ 9] = {'name': 'Jessica',  'score': 1.5,  # noqa E201
        'buchholz':  9.0, 'blacktimes': 1, 'rank': 15}  # noqa E201
        playerD[10] = {'name': 'Lais',     'score': 1.0,  # noqa E201
        'buchholz': 13.0, 'blacktimes': 3, 'rank': 16}  # noqa E201
        for k, v in data.items():
            # print(k, v)
            self.assertEqual(v['score'], playerD[v['id']]['score'])
            self.assertEqual(v[RankingSystem.BLACKTIMES.value],
                             playerD[v['id']]['blacktimes'])
            self.assertEqual(v['rank'], playerD[v['id']]['rank'])
            self.assertEqual(v[RankingSystem.BUCHHOLZ.value],
                             playerD[v['id']]['buchholz'])


# ROB
class AdminUpdateGameAPIViewTest(TransactionTestCase):
    """ Update game by admin instead of player
    user need to be loged in
    """
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(
            username='testuser2', password='testpassword2')
        self.admin_update_game_url = '/api/v1/admin_update_game/'

    @tag("continua")
    def test_001_updateGamesAsAdmin(self):  # OK
        """ update  game by admin user
        """
        # login
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB,
            administrativeUser=self.user)
        self.client.force_authenticate(user=self.user)
        # create players
        for username, id in playerListCasita:
            name = username
            email = f"{username}@example.com"
            player = Player.objects.create(id=id,
                                           name=name,
                                           email=email)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)

        # update games, set result to Scores.BLACK
        for i, game in enumerate(tournament.getGames()):
            game.result = Scores.BLACK.value
            game.save()
            game_id = game.id
            result = Scores.WHITE.value

            data = {'game_id': game_id,
                    'otb_result': result
                    }

            url = self.admin_update_game_url
            response = self.client.post(url, data)
            results = response.json()
            game2 = Game.objects.get(id=game_id)
            self.assertEqual(result, game2.result)
            self.assertEqual(results['result'], True)

    @tag("continua")
    def test_002_updateGamesAsAdminCreatedByOtherUser(self):  # OK
        """ try to update games by a user diffrent from the
        una that created the tournament
        """
        # login
        self.client.force_authenticate(user=self.user)
        # create tournament
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB,
            administrativeUser=self.user)

        # create players
        for username, id in playerListCasita:
            name = username
            email = f"{username}@example.com"
            player = Player.objects.create(id=id,
                                           name=name,
                                           email=email)
            # add players to tournament
            tournament.players.add(player)
        # create rounds/games
        swissByes = []
        create_rounds(tournament, swissByes)

        self.client.force_authenticate(user=self.user2)
        # update games, set result to Scores.BLACK
        for i, game in enumerate(tournament.getGames()):
            game.result = Scores.BLACK.value
            game.save()
            game_id = game.id
            result = Scores.WHITE.value

            data = {'game_id': game_id,
                    'otb_result': result
                    }

            url = self.admin_update_game_url
            response = self.client.post(url, data)
            results = response.json()
            game2 = Game.objects.get(id=game_id)
            self.assertNotEqual(result, game2.result)
            self.assertEqual(results['result'], False)
            self.assertEqual(
                results['message'],
                'Only the user that create the tournament can update it')

# class GetCrossTableAPIViewTest(TestCase):

#     def setUp(self):
#         from chess_models.management.commands.populate import Command
#         self.client = APIClient()
#         self.get_cross_table = '/api/v1/get_cross_table/'
#         command = Command()
#         command.cleanDataBase()
#         command.readInputFile(
#             'chess_models/management/commands/tie-breaking-swiss.trf')
#         command.insertData()      # Insert data into the database
#         self.tournament_name = 'tie-breaking exercises swiss'
#         # read tournament frok database
#         self.tournament =\
#             Tournament.objects.get(name=self.tournament_name)

#     def test_001_getCrossTable(self):
#         tournament_id = self.tournament.id
#         self.tournament.addToRankingList(RankingSystem.BUCHHOLZ.value)
#         self.tournament.addToRankingList(RankingSystem.BLACKTIMES.value)
#         # data = {'tournament_id': tournament_id}

#         # response = self.client.post(
#         #     self.get_cross_table, data)
#         response = self.client.get(
#             self.get_cross_table + f'{tournament_id}/')
#         data = response.json()
#         for dat in data:
#             game = Game.objects.get(id=dat['gameId'])
#             self.assertEqual(game.white.id, dat['white'])
#             if dat['black'] != -1:
#                 self.assertEqual(game.black.id, dat['black'])
#             self.assertEqual(game.result, dat['result'])


# ROB NO needed this ttest swiss games
class GetRoundResultsAPIViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from chess_models.management.commands.populate import Command
        self.client = APIClient()
        self.get_round_results = '/api/v1/get_round_results/'
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        command.insertData()      # Insert data into the database
        self.tournament_name = 'tie-breaking exercises swiss'
        # read tournament frok database
        self.tournament =\
            Tournament.objects.get(name=self.tournament_name)

    @tag("suiza")
    def test_001_getRoundResults(self):
        tournament_id = self.tournament.id
        self.tournament.addToRankingList(RankingSystem.BUCHHOLZ.value)
        self.tournament.addToRankingList(RankingSystem.BLACKTIMES.value)

        response = self.client.get(
            self.get_round_results + f'{tournament_id}/')
        data = response.json()
        # print("data", data)
        for round in data.values():
            id = int(round['round_id'])
            _round = Round.objects.get(id=id)
            self.assertEqual(_round.name, round['round_name'])
            for gameK, gameV in round['games'].items():
                _game = Game.objects.get(id=gameV['id'])
                self.assertEqual(_game.white.id, gameV['white'])
                if gameV['black'] is not None:
                    self.assertEqual(_game.black.id, gameV['black'])
                self.assertEqual(_game.result, gameV['result'])
                self.assertEqual(_game.round.id, id)
                self.assertEqual(_game.round.tournament.id, tournament_id)


class GetPlayers(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # I do not think delete is needed
        Tournament.objects.all().delete()
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1',
                                              password='testpassword')

    @tag("continua")
    def test_000_get_Players(self):  # OK
        """Create a new tournament """
        self.client.force_authenticate(user=self.user1)
        tournament_name = "tournament_1"
        data = {'name': tournament_name,
                'tournament_type': TournamentType.SWISS,
                'tournament_speed': TournamentSpeed.CLASSICAL,
                'board_type': TournamentBoardType.LICHESS,
                'players':
                'lichess_username\neaffelix\noliva21\nrmarabini\nzaragozana'
                }
        response = self.client.post(URLTOURNAMENT, data)
        tournament_id = response.data['id']
        response = self.client.get(
            GETPLAYERS + f'{tournament_id}/')
        for (username, answer) in zip(['eaffelix',
                                       'oliva21',
                                       'rmarabini',
                                       'zaragozana'],
                                      response.data):
            self.assertIn(username, answer['lichess_username'])
