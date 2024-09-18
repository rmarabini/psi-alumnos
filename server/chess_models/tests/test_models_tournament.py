from django.test import TransactionTestCase, tag
from chess_models.models import Player, Referee, Tournament, Game, Round
from chess_models.models import (TournamentSpeed, getGamesCount,
                                 TournamentType, TournamentBoardType,
                                 RankingSystem, getRanking, RankingSystemClass)
from chess_models.models import create_rounds, Scores
from chess_models.tests.constants import (
    lichess_usernames_6, lichess_usernames_8)


class TournamentModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        pass
        # reset_sequences()

    @tag("continua")
    def test_001_tournament_str_method(self):
        "create a tournament "
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        self.assertEqual(str(tournament), tournament_name)

    @tag("continua")
    def test_002_tournament_add_players(self):
        """add players to tournament,
           check tournament.players is a manytomany field
        """
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        players = []  # used for testing
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        for player in players:
            self.assertTrue(player in tournament.getPlayers())
        self.assertEqual(tournament.getPlayersCount(),
                         len(lichess_usernames_6))

    @tag("continua")
    def test_003_tournament_add_referee(self):
        "add referee to tournament"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        referee = Referee.objects.create(
            name='referee_01', refereeNumber='12345678')
        tournament.referee = referee
        self.assertEqual(tournament.referee, referee)

    @tag("continua")
    def test_0030_RankingSystemClass(self):
        "create a RankingSystemClass"
        rankingSystem = RankingSystem.BUCHHOLZ
        rankingSystemClass = RankingSystemClass.objects.create(
            value=rankingSystem)
        self.assertEqual(rankingSystemClass.value, rankingSystem)

    @tag("continua")
    def test_0035_tournament_rankingList(self):
        """add rankingList to tournament
        Ranking are saved as manytomany field in the model Tournament
        """
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        rankingSystem1 = RankingSystem.BUCHHOLZ
        rankingSystem2 = RankingSystem.SONNEBORN_BERGER
        tournament.addToRankingList(rankingSystem1)
        tournament.addToRankingList(rankingSystem2)
        rankingSystemList = [r.value for r in tournament.getRankingList()]
        self.assertEqual(tournament.rankingList.count(), 2)
        self.assertTrue(rankingSystem1 in rankingSystemList)
        self.assertTrue(rankingSystem2 in rankingSystemList)

    @tag("continua")
    def test_004_tournament_number_of_players(self):
        "check function getPlayersCount,  number of "
        "players in tournament"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        players = []
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        self.assertEqual(tournament.getPlayersCount(),
                         len(lichess_usernames_6))

    # ROB: getPlayers: needed
    @tag("suiza")
    def test_005_getSortedPlayers(self):
        """check function getSortedPlayers that
        returns a sorted  list of players. The sorted is done by
        rating. The choosed rating depends on the TournamentSpeed
        and board_type. First player is the one with the highest
        rating"""
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            board_type=TournamentBoardType.LICHESS,
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.RAPID)
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
        sorted_players = tournament.getPlayers(sorted=True)

        ranting = 9999999
        for player in sorted_players:
            self.assertTrue(ranting >= player.lichess_rating_rapid)
            ranting = player.lichess_rating_rapid

    # ROB  create_round method needed
    @tag("continua")
    def test_006_tournament_create_round_even(self):
        """create games for a round robin tournament
        Solution for 6 players:
            Rd 1: 1-6, 2-5, 3-4.
            Rd 2: 6-4, 5-3, 1-2.
            Rd 3: 2-6, 3-1, 4-5.
            Rd 4: 6-5, 1-4, 2-3.
            Rd 5: 3-6, 4-2, 5-1.
        from https://handbook.fide.com/chapter/C05Annex1
        """
        solution = [[[1, 6], [2, 5], [3, 4]],
                    [[6, 4], [5, 3], [1, 2]],
                    [[2, 6], [3, 1], [4, 5]],
                    [[6, 5], [1, 4], [2, 3]],
                    [[3, 6], [4, 2], [5, 1]]]

        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.RAPID)
        players = []
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        # list of participants
        participants = tournament.getPlayers(sorted=True)
        create_rounds(tournament)
        rounds = tournament.round_set.all()
        for i, round in enumerate(rounds):
            # print(round)
            for j, game in enumerate(round.game_set.all()):
                # print("    ", game)
                self.assertEqual(game.white, participants[solution[i][j][0]-1])
                self.assertEqual(game.black, participants[solution[i][j][1]-1])

    # Code written by studends in continuos mode 
    # does not need to satisfy the following tests
    # unless it is a resit
    @tag("odd")
    def test_007_tournament_create_round_odd(self):
        """create games for a round robin tournament
        Solution for 5 players:
            player 6 -> bye
            Rd 1: 1-6, 2-5, 3-4.
            Rd 2: 6-4, 5-3, 1-2.
            Rd 3: 2-6, 3-1, 4-5.
            Rd 4: 6-5, 1-4, 2-3.
            Rd 5: 3-6, 4-2, 5-1.
        from https://handbook.fide.com/chapter/C05Annex1
        """
        solution = [[[1, 6], [2, 5], [3, 4]],
                    [[6, 4], [5, 3], [1, 2]],
                    [[2, 6], [3, 1], [4, 5]],
                    [[6, 5], [1, 4], [2, 3]],
                    [[3, 6], [4, 2], [5, 1]]]
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.ROUNDROBIN,
            tournament_speed=TournamentSpeed.RAPID)
        players = []
        for lichess_username in lichess_usernames_6[:-1]:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        # list of participants
        participants = tournament.getPlayers(sorted=True)
        playerBYE = Player(name='BYE1')
        participants.append(playerBYE)

        create_rounds(tournament)
        rounds = tournament.round_set.all()
        for i, round in enumerate(rounds):
            # print(round)
            for j, game in enumerate(round.game_set.all()):
                # print("    ", game)
                if game.result == Scores.WHITE or\
                      game.result == Scores.BLACK:
                    self.assertEqual(
                        game.white, participants[solution[i][j][0]-1])
                    self.assertEqual(
                        game.black, participants[solution[i][j][1]-1])
                elif game.result == Scores.BYE_U:
                    if solution[i][j][0] == 6:
                        self.assertEqual(
                            game.white, participants[solution[i][j][1]-1])
                    else:
                        self.assertEqual(
                            game.white, participants[solution[i][j][0]-1])

    @tag("double")
    def test_0075_tournament_create_double_round_same_dayeven(self):
        """create games for a double round same day robin tournament
        Solution for 6 players:
            Rd 01: 1-6, 2-5, 3-4.
            Rd 02: 6-1, 5-2, 4-3.
            Rd 03: 6-4, 5-3, 1-2.
            Rd 04: 4-6, 3-5, 2-1.
            Rd 05: 2-6, 3-1, 4-5.
            Rd 06: 6-2, 1-3, 5-4.
            Rd 07: 6-5, 1-4, 2-3.
            Rd 08: 5-6, 4-1, 3-2.
            Rd 09: 3-6, 4-2, 5-1.
            Rd 10: 6-3, 2-4, 1-5.
        from https://handbook.fide.com/chapter/C05Annex1
        """
        solution = [[[1, 6], [2, 5], [3, 4]],
                    [[6, 1], [5, 2], [4, 3]],
                    [[6, 4], [5, 3], [1, 2]],
                    [[4, 6], [3, 5], [2, 1]],
                    [[2, 6], [3, 1], [4, 5]],
                    [[6, 2], [1, 3], [5, 4]],
                    [[6, 5], [1, 4], [2, 3]],
                    [[5, 6], [4, 1], [3, 2]],
                    [[3, 6], [4, 2], [5, 1]],
                    [[6, 3], [2, 4], [1, 5]]]

        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.DOUBLEROUNDROBINSAMEDAY,
            tournament_speed=TournamentSpeed.RAPID)
        players = []
        for lichess_username in lichess_usernames_6:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        # list of participants
        participants = tournament.getPlayers(sorted=True)
        create_rounds(tournament)
        rounds = tournament.round_set.all()
        for i, round in enumerate(rounds):
            # print(round)
            for j, game in enumerate(round.game_set.all()):
                # print("    ", game)
                self.assertEqual(game.white, participants[solution[i][j][0]-1])
                self.assertEqual(game.black, participants[solution[i][j][1]-1])

    @tag("double")
    def test_0076_tournament_create_round_odd(self):
        """create games for a double round robin same day tournament
        Solution for 5 players:
            player 6 -> bye
            Rd 1: 1-6, 2-5, 3-4.
            Rd 2: 6-1, 5-2, 4-3.
            Rd 3: 6-4, 5-3, 1-2.
            Rd 4: 4-6, 3-5, 2-1.
            Rd 5: 2-6, 3-1, 4-5.
            Rd 6: 6-2, 1-3, 5-4.
            Rd 7: 6-5, 1-4, 2-3.
            Rd 8: 5-6, 4-1, 3-2.
            Rd 9: 3-6, 4-2, 5-1.
            Rd 10: 6-3, 2-4, 1-5.
        from https://handbook.fide.com/chapter/C05Annex1
        """
        solution = [[[1, 6], [2, 5], [3, 4]],
                    [[6, 1], [5, 2], [4, 3]],
                    [[6, 4], [5, 3], [1, 2]],
                    [[4, 6], [3, 5], [2, 1]],
                    [[2, 6], [3, 1], [4, 5]],
                    [[6, 2], [1, 3], [5, 4]],
                    [[6, 5], [1, 4], [2, 3]],
                    [[5, 6], [4, 1], [3, 2]],
                    [[3, 6], [4, 2], [5, 1]],
                    [[6, 3], [2, 4], [1, 5]]]
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.DOUBLEROUNDROBINSAMEDAY,
            tournament_speed=TournamentSpeed.RAPID)
        players = []
        for lichess_username in lichess_usernames_6[:-1]:
            player = Player.objects.create(
                lichess_username=lichess_username)
            tournament.players.add(player)
            players.append(player)
        # list of participants
        participants = tournament.getPlayers(sorted=True)
        playerBYE = Player(name='BYE1')
        participants.append(playerBYE)

        create_rounds(tournament)
        rounds = tournament.round_set.all()
        for i, round in enumerate(rounds):
            # print(round)
            for j, game in enumerate(round.game_set.all()):
                # print("    ", game)
                if game.result == Scores.WHITE or\
                      game.result == Scores.BLACK:
                    self.assertEqual(
                        game.white, participants[solution[i][j][0]-1])
                    self.assertEqual(
                        game.black, participants[solution[i][j][1]-1])
                elif game.result == Scores.BYE_U:
                    if solution[i][j][0] == 6:
                        self.assertEqual(
                            game.white, participants[solution[i][j][1]-1])
                    else:
                        self.assertEqual(
                            game.white, participants[solution[i][j][0]-1])

    @tag("double")
    def test_008_tournament_create_double_round_even(self):
        """create games for a round robin tournament
        Solution for 8 players:
            R 1: 1-8, 2-7, 3-6, 4-5.
            R 2: 8-5, 6-4, 7-3, 1-2.
            R 3: 2-8, 3-1, 4-7, 5-6.
            R 4: 8-6, 7-5, 1-4, 2-3.
            R 5: 3-8, 4-2, 5-1, 6-7.
            R 6: 4-8, 5-3, 6-2, 7-1
            R 7: 8-7, 1-6, 2-5, 3-4.
            R 8: 8-1, 7-2, 6-3, 5-4.
            R 9: 5-8, 4-6, 3-7, 2-1.
            R 10: 8-2, 1-3, 7-4, 6-5.
            R 11: 6-8, 5-7, 4-1, 3-2.
            R 12: 8-3, 2-4, 1-5, 7-6.
            R 13: 8-4, 3-5, 2-6, 1-7
            R 14: 7-8, 6-1, 5-2, 4-3.
        From: https://www.englishchess.org.uk/wp-content/uploads/2010/04/roundRobinPairings.pdf # noqa: E501
    """
        solution = [
            [[1, 8], [2, 7], [3, 6], [4, 5]],
            [[8, 5], [6, 4], [7, 3], [1, 2]],
            [[2, 8], [3, 1], [4, 7], [5, 6]],
            [[8, 6], [7, 5], [1, 4], [2, 3]],
            [[3, 8], [4, 2], [5, 1], [6, 7]],
            [[4, 8], [5, 3], [6, 2], [7, 1]],
            [[8, 7], [1, 6], [2, 5], [3, 4]],
            [[8, 1], [7, 2], [6, 3], [5, 4]],
            [[5, 8], [4, 6], [3, 7], [2, 1]],
            [[8, 2], [1, 3], [7, 4], [6, 5]],
            [[6, 8], [5, 7], [4, 1], [3, 2]],
            [[8, 3], [2, 4], [1, 5], [7, 6]],
            [[8, 4], [3, 5], [2, 6], [1, 7]],
            [[7, 8], [6, 1], [5, 2], [4, 3]]
            ]

        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name,
            tournament_type=TournamentType.DOUBLEROUNDROBIN,
            tournament_speed=TournamentSpeed.RAPID)
        players = []
        for lichess_username in lichess_usernames_8:
            player = Player.objects.create(
                name=lichess_username)
            tournament.players.add(player)
            players.append(player)
        # list of participants
        participants = tournament.getPlayers(sorted=True)
        create_rounds(tournament)
        rounds = tournament.round_set.all()
        for i, round in enumerate(rounds):
            # print(round)
            for j, game in enumerate(round.game_set.all()):
                # print("    ", game)
                self.assertEqual(game.white, participants[solution[i][j][0]-1])
                self.assertEqual(game.black, participants[solution[i][j][1]-1])

    @tag("suiza")
    def test_010_tournament_create_swiss_tournament_round_0(self):
        """create games for a swiss tournament with 16 players
        first round. No half byes or unplayed byes"""
        # Create players
        playerD = {}
        playerD[ 1] = {'elo': 2200, 'name': 'Alyx'}  # noqa E201
        playerD[ 2] = {'elo': 2150, 'name': 'Bruno'}  # noqa E201
        playerD[ 3] = {'elo': 2100, 'name': 'Charline'}  # noqa E201
        playerD[ 4] = {'elo': 2050, 'name': 'David'}  # noqa E201
        playerD[ 5] = {'elo': 2000, 'name': 'Elene'}  # noqa E201
        playerD[ 6] = {'elo': 1950, 'name': 'Franck'}  # noqa E201
        playerD[ 7] = {'elo': 1900, 'name': 'Genevieve'}  # noqa E201
        playerD[ 8] = {'elo': 1850, 'name': 'Irina'}  # noqa E201
        playerD[ 9] = {'elo': 1800, 'name': 'Jessica'}  # noqa E201
        playerD[10] = {'elo': 1750, 'name': 'Lais'}
        playerD[11] = {'elo': 1700, 'name': 'Maria'}
        playerD[12] = {'elo': 1650, 'name': 'Nick (W)'}
        playerD[13] = {'elo': 1600, 'name': 'Opal'}
        playerD[14] = {'elo': 1550, 'name': 'Paul'}
        playerD[15] = {'elo': 1500, 'name': 'Reine'}
        playerD[16] = {'elo': 1450, 'name': 'Stephan'}

        solution = [[1, 9], [2, 10], [3, 11], [4, 12], [5, 13], [6, 14],
                    [7, 15], [8, 16]]

        # Tournament.objects.all().delete()
        # Player.objects.all().delete()
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB,
            name=tournament_name)
        tournament.addToRankingList(RankingSystem.PLAIN_SCORE)
        for key, value in playerD.items():
            player = Player.objects.create(
                id=key, lichess_username=None,
                name=value['name'],
                fide_rating_classical=value['elo'])
            tournament.players.add(player)
        # for p in Player.objects.all():
        #     print(p, f"({p.id})")

        create_rounds(tournament)
        round = tournament.round_set.first()
        for i, game in enumerate(round.game_set.all()):
            # print("    ", game)
            self.assertEqual(
                {game.white, game.black},
                {Player.objects.get(id=solution[i][0]),
                 Player.objects.get(id=solution[i][1])}
                 )

    @tag("suiza")
    def test_011_tournament_create_swiss_tournament_round_0_with_manual_bye(
            self):
        """create games for a swiss tournament with 16 players
        first round. One bye_h is given to the player Genevieve
        This implies an extra bye_u to the last player Stephan"""

        # Create players
        playerD = {}
        playerD[ 1] = {'rankAB':  1, 'elo': 2200, 'name': 'Alyx'}  # noqa E201
        playerD[ 2] = {'rankAB':  2, 'elo': 2150, 'name': 'Bruno'}  # noqa E201
        playerD[ 3] = {'rankAB':  3, 'elo': 2100, 'name': 'Charline'}  # noqa E201
        playerD[ 4] = {'rankAB':  4, 'elo': 2050, 'name': 'David'}  # noqa E201
        playerD[ 5] = {'rankAB':  5, 'elo': 2000, 'name': 'Elene'}  # noqa E201
        playerD[ 6] = {'rankAB':  6, 'elo': 1950, 'name': 'Franck'}  # noqa E201
        playerD[ 7] = {'rankAB':  7, 'elo': 1900, 'name': 'Genevieve'}  # noqa E201
        playerD[ 8] = {'rankAB':  8, 'elo': 1850, 'name': 'Irina'}  # noqa E201
        playerD[ 9] = {'rankAB':  9, 'elo': 1800, 'name': 'Jessica'}  # noqa E201
        playerD[10] = {'rankAB': 10, 'elo': 1750, 'name': 'Lais'}
        playerD[11] = {'rankAB': 11, 'elo': 1700, 'name': 'Maria'}
        playerD[12] = {'rankAB': 12, 'elo': 1650, 'name': 'Nick (W)'}
        playerD[13] = {'rankAB': 13, 'elo': 1600, 'name': 'Opal'}
        playerD[14] = {'rankAB': 14, 'elo': 1550, 'name': 'Paul'}
        playerD[15] = {'rankAB': 15, 'elo': 1500, 'name': 'Reine'}
        playerD[16] = {'rankAB': 16, 'elo': 1450, 'name': 'Stephan'}
        # solution in rankAB
        # solutionAB =[[1, 8], [2, 7], [3, 6], [4, 5], [9, 16], [10, 15],
        #            [11, 14], [12, 13]]
        # solution in rank
        solution = [[7, None], [16, None], [1, 9], [2, 10], [3, 11],
                    [4, 12], [5, 13], [6, 14], [8, 15]]

        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB,
            name=tournament_name)

        for key, value in playerD.items():
            player = Player.objects.create(
                id=key, lichess_username=None,
                name=value['name'],
                fide_rating_classical=value['elo'])
            tournament.players.add(player)
        byes = [7]
        # byes = []
        create_rounds(tournament, byes)
        round = tournament.round_set.first()
        for i, game in enumerate(round.game_set.all().order_by('id')):
            # print("    ", game)
            white = Player.objects.get(id=solution[i][0])
            if solution[i][1] is None:
                black = None
            else:
                black = Player.objects.get(id=solution[i][1])
            self.assertEqual(
                {game.white, game.black},
                {white, black}
                 )

    @tag("suiza")
    def test_012_tournament_create_swiss_tournament_round_0_with_umplayed_bye(
            self):
        """create games for a swiss tournament with 15 players
        and two byes. The bye is given to the player with the
        lowest rank and no previous bye."""
        # Create players
        playerD = {}
        playerD[ 1] = {'rankAB':  1, 'elo': 2200, 'name': 'Alyx'}  # noqa E201
        playerD[ 2] = {'rankAB':  2, 'elo': 2150, 'name': 'Bruno'}  # noqa E201
        playerD[ 3] = {'rankAB':  3, 'elo': 2100, 'name': 'Charline'}  # noqa E201
        playerD[ 4] = {'rankAB':  4, 'elo': 2050, 'name': 'David'}  # noqa E201
        playerD[ 5] = {'rankAB':  5, 'elo': 2000, 'name': 'Elene'}  # noqa E201
        playerD[ 6] = {'rankAB':  6, 'elo': 1950, 'name': 'Franck'}  # noqa E201
        playerD[ 7] = {'rankAB':  7, 'elo': 1900, 'name': 'Genevieve'}  # noqa E201
        playerD[ 8] = {'rankAB':  8, 'elo': 1850, 'name': 'Irina'}  # noqa E201
        playerD[ 9] = {'rankAB':  9, 'elo': 1800, 'name': 'Jessica'}  # noqa E201
        playerD[10] = {'rankAB': 10, 'elo': 1750, 'name': 'Lais'}
        playerD[11] = {'rankAB': 11, 'elo': 1700, 'name': 'Maria'}
        playerD[12] = {'rankAB': 12, 'elo': 1650, 'name': 'Nick (W)'}
        playerD[13] = {'rankAB': 13, 'elo': 1600, 'name': 'Opal'}
        playerD[14] = {'rankAB': 14, 'elo': 1550, 'name': 'Paul'}
        playerD[15] = {'rankAB': 15, 'elo': 1500, 'name': 'Reine'}
        # playerD[16] = {'rankAB': 14, 'elo': 1450, 'name': 'Stephan'}
        # Bye goes to Reine (15) since she is last
        # in the rankin with no previous bye
        solution = [[7, None], [8, None], [15, None], [1, 9], [2, 10],
                    [3, 11], [4, 12], [5, 13], [6, 14]]

        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB,
            name=tournament_name)

        for key, value in playerD.items():
            player = Player.objects.create(
                id=key, lichess_username=None,
                name=value['name'],
                fide_rating_classical=value['elo'])
            tournament.players.add(player)
        byes = [7, 8]
        create_rounds(tournament, byes)
        round = tournament.round_set.first()
        for i, game in enumerate(round.game_set.all().order_by('id')):
            # print("    > ", game)
            if i == 0 or i == 1:
                self.assertEqual(game.white,
                                 Player.objects.get(id=solution[i][0]))
                self.assertEqual(game.black, None)
                self.assertEqual(game.result, Scores.BYE_H)
            elif i == 2:
                self.assertEqual(game.white,
                                 Player.objects.get(id=solution[i][0]))
                self.assertEqual(game.black, None)
                self.assertEqual(game.result, Scores.BYE_U)
            else:
                self.assertEqual(
                    {game.white, game.black},
                    {Player.objects.get(id=solution[i][0]),
                     Player.objects.get(id=solution[i][1])}
                    )

        self.assertEqual(tournament.getPlayersCount(),
                         len(playerD))
        self.assertEqual(tournament.getRoundCount(), 1)
        self.assertEqual(
            getGamesCount(
                tournament,
                finished=False),
            len(solution))

    @tag("suiza")
    def test_013_tournament_create_swiss_tournament_round_1(self):
        # Create players
        playerD1 = {}
        playerD1[ 1] = {'elo': 2200, 'name': 'Alyx'}  # noqa E201
        playerD1[ 2] = {'elo': 2150, 'name': 'Bruno'}  # noqa E201
        playerD1[ 3] = {'elo': 2100, 'name': 'Charline'}  # noqa E201
        playerD1[ 4] = {'elo': 2050, 'name': 'David'}  # noqa E201
        playerD1[ 5] = {'elo': 2000, 'name': 'Elene'}  # noqa E201
        playerD1[ 6] = {'elo': 1950, 'name': 'Franck'}  # noqa E201
        playerD1[ 7] = {'elo': 1900, 'name': 'Genevieve'}  # noqa E201
        playerD1[ 8] = {'elo': 1850, 'name': 'Irina'}  # noqa E201
        playerD1[ 9] = {'elo': 1800, 'name': 'Jessica'}  # noqa E201
        playerD1[10] = {'elo': 1750, 'name': 'Lais'}
        playerD1[11] = {'elo': 1700, 'name': 'Maria'}
        playerD1[12] = {'elo': 1650, 'name': 'Nick (W)'}
        playerD1[13] = {'elo': 1600, 'name': 'Opal'}
        playerD1[14] = {'elo': 1550, 'name': 'Paul'}
        playerD1[15] = {'elo': 1500, 'name': 'Reine'}
        playerD1[16] = {'elo': 1450, 'name': 'Stephan'}
        # score = RankingSystem.PLAIN_SCORE.value
        # buchholz = RankingSystem.BUCHHOLZ.value
        solution1 = [[1, 9], [10, 2], [3, 11], [12, 4], [5, 13], [14, 6],
                     [7, 15], [16, 8]]
        # create tournamente
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            tournament_type=TournamentType.SWISS,
            tournament_speed=TournamentSpeed.CLASSICAL,
            board_type=TournamentBoardType.OTB,
            name=tournament_name)
        tournament.addToRankingList(RankingSystem.BUCHHOLZ)
        # create players and add to tournament
        for key, value in playerD1.items():
            player = Player.objects.create(
                id=key, lichess_username=None,
                name=value['name'],
                fide_rating_classical=value['elo'])
            tournament.players.add(player)

        # ROUND 1
        create_rounds(tournament)
        round = Round.objects.get(tournament=tournament, name='round_001')

        # print("ROUND 1")
        ###
        for i, game in enumerate(round.game_set.all().order_by('id')):
            # print("    ", game)
            self.assertEqual(
                {game.white, game.black},
                {Player.objects.get(id=solution1[i][0]),
                 Player.objects.get(id=solution1[i][1])}
                 )
        # save results in previous games
        games = {(1, 9): Scores.WHITE, (10, 2): Scores.BLACK,
                 (3, 11): Scores.DRAW, (12, 4): Scores.BLACK,
                 (5, 13): Scores.BLACK, (14, 6): Scores.WHITE,
                 (7, 15): Scores.WHITE, (16, 8): Scores.DRAW
                 }

        for game in games:
            white = Player.objects.get(id=game[0])
            black = Player.objects.get(id=game[1])
            g = Game.objects.get(white=white, black=black)
            g.result = games[game]
            g.finished = True
            g.save()

        # ####
        # for i, game in enumerate(round.game_set.all().order_by('id')):
        #     print("    ", game)
        results = getRanking(tournament)  # noqa F841
        # for k, v in results.items():
        #     print(k, f"({k.id})", v['rank'], v[score], v[buchholz])
        # ####
        # ROUND 2
        # print("ROUND 2")
        david_player = Player.objects.get(name='David')
        # print("David", david_player, david_player.id)
        create_rounds(tournament,
                      swissByes=[david_player.id])
        # print("games after play")
        # for i, game in enumerate(round.game_set.all().order_by('id')):
        #    print("    ", game)
        round2 = Round.objects.get(tournament=tournament,
                                   name='round_002')
        solution2 = [(4, None), (15, None), (13, 1), (2, 7), (3, 16), (11, 5),
                     (6, 10), (8, 14), (9, 12)]
        # for i, game in enumerate(round2.game_set.all().order_by('id')):
        #     print("    > ", game)
        for i, game in enumerate(round2.game_set.all().order_by('id')):
            # print("    > ", game)
            if i == 0:
                self.assertEqual(game.white,
                                 Player.objects.get(id=solution2[i][0]))
                self.assertEqual(game.black, None)
                self.assertEqual(game.result, Scores.BYE_H)
            elif i == 1:
                self.assertEqual(game.white,
                                 Player.objects.get(id=solution2[i][0]))
                self.assertEqual(game.black, None)
                self.assertEqual(game.result, Scores.BYE_U)
            else:
                self.assertEqual(
                    {game.white, game.black},
                    {Player.objects.get(id=solution2[i][0]),
                     Player.objects.get(id=solution2[i][1])}
                    )
        # save results in previous games
        games2 = {(4, None): Scores.BYE_H, (15, None): Scores.BYE_U,
                  (13, 1): Scores.DRAW,    (2, 7): Scores.BLACK,
                  (3, 16): Scores.BLACK, (11, 5): Scores.WHITE,
                  (6, 10): Scores.WHITE, (8, 14): Scores.DRAW,
                  (9, 12): Scores.DRAW
                  }

        for game in games2:
            white = Player.objects.get(id=game[0])
            if game[1] is None:
                black = None
            else:
                black = Player.objects.get(id=game[1])
            g = Game.objects.get(white=white, black=black)
            g.result = games2[game]
            g.finished = True
            g.save()
        # ####
        # for i, game in enumerate(round2.game_set.all().order_by('id')):
        #     print("    ", game)
        # ####
        # print("SCORES_2")
        # playersList = getRanking(
        #     tournament,
        #     rankingSystemList=[buchholz])
        ####
        # print("name rank score buchholz colordifference")
        # for i, (k, v) in enumerate(playersList.items(), start=1):
        #     print(k, f"({k.id} -> {i})", v['rank'], v[score], v[buchholz],
        #           v['colordifference'])
        # ####
        # print("ROUND_3==================", flush=True)
        solution3 = [(1, 7), (15, 2), (9, 3), (4, 13), (5, 10), (12, 6),
                     (8, 11), (16, 14)]

        create_rounds(tournament)  # , rankingSystem=[buchholz])
        round3 = Round.objects.get(tournament=tournament, name='round_003')
        for i, game in enumerate(round3.game_set.all().order_by('id')):
            # print("    ", game)
            self.assertEqual(
               {game.white, game.black},
               {Player.objects.get(id=solution3[i][0]),
                Player.objects.get(id=solution3[i][1])}
               )
