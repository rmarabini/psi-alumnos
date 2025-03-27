from django.test import TransactionTestCase, tag
from chess_models.models import Tournament, Round, Game
# from chess_models.models import (
#    LichessAPIError, TournamentType, Scores)
from chess_models.models import (getScores, getRanking,
                                 getBlackWins)
try:
    from chess_models.models import (getMediamBuchholz, getSonnebornBerger,
                                     getBuchholzCutMinusOne,  getBuchholz,
                                    getOpponents, getAdjustedScores, getPlayers
                                     )
except ImportError:
    pass

from chess_models.models.constants import (TournamentSpeed, TournamentType,
                                           TournamentBoardType, RankingSystem)


class TournamentModelTestExtension(TransactionTestCase):
    """ test related with tournaments that
    involve the creation of games"""
    reset_sequences = True

    def setUp(self):
        from chess_models.management.commands.populate import Command
        self.command = Command()
        self.command.cleanDataBase()
        self.players = ['Alyx', 'Bruno', 'Charline', 'David', 'Elene',
                        'Franck', 'Genevieve', 'Irina', 'Jessica', 'Lais',
                        'Maria', 'Nick (W)', 'Opal', 'Paul', 'Reine',
                        'Stephan']

    @tag("continuadelete")
    def test_009_tournament_getPlayers(self):
        """Test function getPlayers that returns a list of
        players"""
        # This are the results we should get
        resultsDict = {}
        resultsDict['Alyx'] = [1]
        resultsDict['Bruno'] = [2]
        resultsDict['Charline'] = [3]
        resultsDict['David'] = [4]
        resultsDict['Elene'] = [5]
        resultsDict['Franck'] = [6]
        resultsDict['Genevieve'] = [7]
        resultsDict['Irina'] = [8]
        resultsDict['Jessica'] = [9]
        resultsDict['Lais'] = [10]
        resultsDict['Maria'] = [11]
        resultsDict['Nick (W)'] = [12]
        resultsDict['Opal'] = [13]
        resultsDict['Paul'] = [14]
        resultsDict['Reine'] = [15]
        resultsDict['Stephan'] = [16]

        # red file with unput data
        self.command.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        self.command.insertData()      # Insert data into the database
        tournament_name = 'tie-breaking exercises swiss'
        # read tournament frok database
        tournament = Tournament.objects.get(name=tournament_name)
        # update some tournament fields
        tournament.tournament_speed = TournamentSpeed.CLASSICAL
        tournament.tournament_type = TournamentType.SWISS
        tournament.board_type = TournamentBoardType.OTB
        # clean tournament ranking list
        tournament.cleanRankingList()  # ROB
        tournament.save()
        # No ranking system defined
        # tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)
        # assign the rating to the players
        playersList = tournament.getPlayers()  # ROB
        for player in playersList:
            player.fide_rating_classical = resultsDict[player.name][0]
            player.save()
        # get List of player in tournament
        playersList = getPlayers(tournament)
        for playerK, playerV in playersList.items():
            self.assertEqual(playerV['rank'], resultsDict[playerK.name][0])
        self.assertEqual(len(playersList), len(resultsDict))

        playersList = getRanking(tournament)  # get ranking
        # print("user (id) rank PS", flush=True)
        for playerK, playerV in playersList.items():
            # print(playerK.name, f"({playerK.id})", playerV['rank'], playerV['PS'], flush=True)
            self.assertEqual(playerV['rank'], resultsDict[playerK.name][0])
        self.assertEqual(len(playersList), len(resultsDict))

    @tag("continuadelete")
    def test_010_tournament_getPoints(self):
        """Test function getPoints that returns a list of
        players and their score. win=1 pt, draw=0.5 pt, loss=0 pt.
        for a swiss tournament"""
        results = {}
        results['Alyx'] = [3.5, 3.5]
        results['Bruno'] = [4.0, 4.0]
        results['Charline'] = [3.5, 3.5]
        results['David'] = [3.5, 3.5]
        results['Elene'] = [2.5, 2.5]
        results['Franck'] = [3.0, 3.0]
        results['Genevieve'] = [1.5, 1.5]
        results['Irina'] = [2.5, 2.5]
        results['Jessica'] = [1.5, 1.5]
        results['Lais'] = [1.0, 1.0]
        results['Maria'] = [2.5, 2.5]
        results['Nick (W)'] = [2.0, 3]
        results['Opal'] = [1.5, 1.5]
        results['Paul'] = [2.0, 2.0]
        results['Reine'] = [2.0, 2.0]
        results['Stephan'] = [3.5, 3.5]
        from chess_models.management.commands.populate import Command
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        command.insertData()      # Insert data into the database
        score = RankingSystem.PLAIN_SCORE
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.addToRankingList(RankingSystem.PLAIN_SCORE.value)  # ROB
        playersList = getScores(tournament)  #  ROB
        for player, points in playersList.items():
            self.assertEqual(points[score], results[player.name][0])
        playersList = getRanking(tournament)
        # print("PlayerList", playersList, flush=True)
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #       playerK.name,
            #       playerK.id, playerV[score],
            #       flush=True)
            self.assertEqual(playerV[score], results[playerK.name][0])
        self.assertEqual(len(playersList), len(results))

    @tag("continua")
    def test_011_tournament_getScores(self):
        """Test function getScores that returns a list of
        players and their score. win=3 pt, draw=2 pt, loss=1 pt
        for a swiss tournament"""
        results = {}
        results['Alyx'] = [12, 12]
        results['Bruno'] = [13, 13]
        results['Charline'] = [12, 12]
        results['David'] = [12, 12]
        results['Elene'] = [10, 10]
        results['Franck'] = [11, 11]
        results['Genevieve'] = [8, 8]
        results['Irina'] = [10, 10]
        results['Jessica'] = [7, 7]
        results['Lais'] = [7, 7]
        results['Maria'] = [10, 10]
        results['Nick (W)'] = [7, 11]
        results['Opal'] = [8, 8]
        results['Paul'] = [7, 7]
        results['Reine'] = [9, 9]
        results['Stephan'] = [12, 12]
        from chess_models.management.commands.populate import Command
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        command.insertData()      # Insert data into the database
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.win_points = 3
        tournament.draw_points = 2
        tournament.lose_points = 1
        tournament.save()
        playersList = getScores(tournament)
        score = RankingSystem.PLAIN_SCORE
        for player, points in playersList.items():
            # print(player.name, points, flush=True)
            self.assertEqual(points[score], results[player.name][0])
            # self.assertEqual(points['points_buchholt'],
            #                 results[player.name][1])

    @tag("continua")
    def test_012_tournament_getScores(self):
        """Test function getPoints that returns a list of
        players for a robin tournament"""
        results = {}
        results['Alyx'] = 3.5
        results['Bruno'] = 3.5
        results['Charline'] = 3.5
        results['David'] = 1.5
        results['Franck'] = 1.5
        results['Elene'] = 1.5
        from chess_models.management.commands.populate import Command
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/tie-breaking-robin.trf')
        command.insertData()      # Insert data into the database
        tournament_name = 'tie-breaking exercises robin'
        tournament = Tournament.objects.get(name=tournament_name)

        playersList = getScores(tournament)
        score = RankingSystem.PLAIN_SCORE
        for player, points in playersList.items():
            self.assertEqual(points[score], results[player.name])

    @tag("suizo")
    def test_013_tournament_getOpponents(self): # ROB no
        """Test function getPoints that returns a list of
        players"""
        # games between XXXX and [x,y,z,...]
        oponents = {}
        oponents['Alyx'] = [9, 13, 2, 15, 4]  #
        oponents['Jessica'] = [1, 10, 9, 9, 9]  # [1, 10, 9, 11, 9]
        oponents['Charline'] = [11, 6, 8, 4, 2]  #
        oponents['Maria'] = [3, 16, 5, 11, 7]  # [3, 16, 5, 9, 7]
        oponents['Elene'] = [13, 15, 11, 7, 10]
        oponents['Opal'] = [5, 1, 4, 8, 14]
        oponents['Genevieve'] = [15, 2, 16, 5, 11]
        oponents['Reine'] = [7, 5, 10, 1, 16]
        oponents['Lais'] = [2, 9, 15, 5, 6]
        oponents['Bruno'] = [10, 7, 1, 16, 3]  #
        oponents['Nick (W)'] = [4, 12, 12, 12, 12]  # [4, 12, 14]
        oponents['David'] = [12, 4, 13, 3, 1]  #
        oponents['Paul'] = [6, 8, 12, 14, 13]  # [6, 8, 12, 13]
        oponents['Franck'] = [14, 3, 6, 10, 8]  #
        oponents['Stephan'] = [8, 11, 7, 2, 15]
        oponents['Irina'] = [16, 14, 3, 13, 6]
        # games that has been payled (no forfeits or byes)
        OTBoponents = {}
        OTBoponents['Alyx'] = [9, 13, 2, 15, 4]  #
        OTBoponents['Jessica'] = [1, 10]  # [1, 10, 9, 11, 9]
        OTBoponents['Charline'] = [11, 6, 8, 4, 2]  #
        OTBoponents['Maria'] = [3, 16, 5, 7]  # [3, 16, 5, 9, 7]
        OTBoponents['Elene'] = [13, 15, 11, 7, 10]
        OTBoponents['Opal'] = [5, 1, 4, 8, 14]
        OTBoponents['Genevieve'] = [15, 2, 16, 5, 11]
        OTBoponents['Reine'] = [7, 5, 10, 1, 16]
        OTBoponents['Lais'] = [2, 9, 15, 5, 6]
        OTBoponents['Bruno'] = [10, 7, 1, 16, 3]  #
        OTBoponents['Nick (W)'] = [4]  # [4, 12, 14]
        OTBoponents['David'] = [12, 13, 3, 1]  #
        OTBoponents['Paul'] = [6, 8, 13]  # [6, 8, 12, 13]
        OTBoponents['Franck'] = [14, 3, 10, 8]  #
        OTBoponents['Stephan'] = [8, 11, 7, 2, 15]
        OTBoponents['Irina'] = [16, 14, 3, 13, 6]

        # color difference at the begining
        # colordifference = {}
        # colordifference['Alyx'] = 0
        # colordifference['Jessica'] = 0
        # colordifference['Charline'] = 0
        # colordifference['Maria'] = 0
        # colordifference['Elene'] = 0
        # colordifference['Opal'] = 0
        # colordifference['Genevieve'] = 0
        # colordifference['Reine'] = 0
        # colordifference['Lais'] = 0
        # colordifference['Bruno'] = 0
        # colordifference['Nick (W)'] = 0
        # colordifference['David'] = 0
        # colordifference['Paul'] = 0
        # colordifference['Franck'] = 0
        # colordifference['Stephan'] = 0
        # colordifference['Irina'] = 0

        # color different at the end
        colordifference = {}
        colordifference['Alyx'] = 1
        colordifference['Jessica'] = 0
        colordifference['Charline'] = 1
        colordifference['Maria'] = 0
        colordifference['Elene'] = 1
        colordifference['Opal'] = -1
        colordifference['Genevieve'] = -1
        colordifference['Reine'] = -1
        colordifference['Lais'] = -1
        colordifference['Bruno'] = -1
        colordifference['Nick (W)'] = 1
        colordifference['David'] = 0
        colordifference['Paul'] = -1
        colordifference['Franck'] = 0
        colordifference['Stephan'] = 1
        colordifference['Irina'] = 1

        # gameResult
        gameResult = {}
        gameResult['Alyx'] = [1., .5, .5, 1., .5]
        gameResult['Bruno'] = [1., 1., .5, 1., .5]
        gameResult['Charline'] = [.5, 1., 1., .5, .5]
        gameResult['David'] = [1., .5, 1., .5, .5]
        gameResult['Franck'] = [0., 0., 1., 1., 1.]
        gameResult['Genevieve'] = [1., 0., 0., .5, 0.]
        gameResult['Elene'] = [0., 0., 1., .5, 1.]
        gameResult['Irina'] = [.5, 1., 0., 1., 0.]
        gameResult['Jessica'] = [0., 0., .5, 0., 1.]
        gameResult['Lais'] = [0., 1., 0., 0., 0.]
        gameResult['Maria'] = [.5, 0., 0., 1., 1.]
        gameResult['Nick (W)'] = [0., 1., 1., 0., 0.]
        gameResult['Opal'] = [1., .5, 0., 0., 0.]
        gameResult['Paul'] = [1., 0., 0., 0., 1.]
        gameResult['Reine'] = [0, 1., 1., 0., 0.]
        gameResult['Stephan'] = [.5, 1., 1., 0., 1.]

        voluntarellyUmplayed = {}  # games not played voluntarelly
        voluntarellyUmplayed['David'] = [9]
        voluntarellyUmplayed['Jessica'] = [24, 29]
        voluntarellyUmplayed['Nick (W)'] = [34, 35]
        voluntarellyUmplayed['Paul'] = [33, 39]
        from chess_models.management.commands.populate import Command
        command = Command()
        command.cleanDataBase()
        command.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        command.insertData()      # Insert data into the database

        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)

        resultsPoints = getScores(tournament)
        playersList = getOpponents(tournament, resultsPoints)  # get oponents
        for k, v in playersList.items():
            for localRe, remoteRe in zip(v['result'], gameResult[k.name]):
                # print(localRe, remoteRe, flush=True)
                self.assertEqual(localRe, remoteRe)
            self.assertEqual(len(v['result']), len(gameResult[k.name]))
        for k, v in playersList.items():
            for oppo in v['opponents']:
                # print(oppo.id, results[k.name], flush=True)
                self.assertTrue(oppo.id in oponents[k.name])
            self.assertEqual(len(v['opponents']), len(oponents[k.name]))
        for k, v in playersList.items():
            for oppo in v['OTBopponents']:
                # print(oppo.id, results[k.name], flush=True)
                self.assertTrue(oppo.id in OTBoponents[k.name])
            self.assertEqual(len(v['OTBopponents']), len(OTBoponents[k.name]))
        for k, v in playersList.items():
            if v['voluntarellyUmplayed'] == []:
                continue
            # do not compare game.id since these are different
            # in different executions
            # for game in v['voluntarellyUmplayed']:
            #     print(game.id, voluntarellyUmplayed[k.name], flush=True)
            #     self.assertTrue(game.id in voluntarellyUmplayed[k.name])
            self.assertEqual(len(v['voluntarellyUmplayed']),
                             len(voluntarellyUmplayed[k.name]))

        for k, v in playersList.items():
            self.assertEqual(v['colordifference'],
                             colordifference[k.name])

    @tag("suizo")
    def test_014_tournament_getAdjustedScores(self):  # ROB no
        """Test function getPoints that returns a list of
        players"""
        results = {}
        results['Bruno'] = [4, 4]  # pp [10, 7, 1, 16, 3]
        results['Alyx'] = [3.5, 3.5]  # pp [9, 13, 2, 15, 4]
        results['Charline'] = [3.5, 3.5]  # pp [11, 5, 8, 4, 2]
        results['David'] = [3.5, 3.5]  # p [12, 13, 3, 1]
        results['Stephan'] = [3.5, 3.5]  # pp [8, 11, 7, 2, 15]
        results['Franck'] = [3, 3]  # [14, 3, 10, 8]
        results['Elene'] = [2.5, 2.5]  # pp [13, 15, 11, 7, 10]
        results['Irina'] = [2.5, 2.5]  # pp [16, 14, 3, 13, 5]
        results['Maria'] = [2.5, 2.5]  # pp [3, 16, 6, 7], 11
        results['Nick (W)'] = [2, 3]  # [4]
        results['Paul'] = [2, 2]  # [5, 8, 13]
        results['Reine'] = [2.0, 2.0]  # m [7, 6, 10, 1, 16]
        results['Genevieve'] = [1.5, 1.5]  # [15, 2, 16, 6, 11]
        results['Jessica'] = [1.5, 1.5]  # [1, 10]
        results['Opal'] = [1.5, 1.5]  # [6, 1, 4, 8, 14]
        results['Lais'] = [1.0, 1.0]  # [2, 9, 15, 5, 6]

        from chess_models.management.commands.populate import Command
        command = Command()
        command.handle()
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)

        resultsPoints = getScores(tournament)
        playersList = getOpponents(tournament, resultsPoints)
        getAdjustedScoresList = getAdjustedScores(tournament, playersList)  # ROB
        score = RankingSystem.PLAIN_SCORE
        for k, v in getAdjustedScoresList.items():
            # print(k.name, v[score], v['adjustedScore'])
            self.assertEqual(v[score], results[k.name][0])
            self.assertEqual(v['adjustedScore'], results[k.name][1])

    @tag("suizo")
    def test_015_tournament_getBuchholz(self):  # no ROB
        """Test function getPoints that returns a list of
        players"""
        results = {}
        results['Bruno'] = [4, 13]  # pp [10, 7, 1, 16, 3]
        results['Alyx'] = [3.5, 12.5]  # pp [9, 13, 2, 15, 4]
        results['Charline'] = [3.5, 15.5]  # pp [11, 5, 8, 4, 2]
        results['David'] = [3.5, 15.]  # p [12, 13, 3, 1]
        results['Stephan'] = [3.5, 12.5]  # pp [8, 11, 7, 2, 15]
        results['Franck'] = [3, 12]  # [14, 3, 10, 8]
        results['Elene'] = [2.5, 8.5]  # pp [13, 15, 11, 7, 10]
        results['Irina'] = [2.5, 13.5]  # pp [16, 14, 3, 13, 5]
        results['Maria'] = [2.5, 13.5]  # pp [3, 16, 5, 9, 7], 11
        results['Nick (W)'] = [2, 11.5]  # [4]
        results['Paul'] = [2, 11]  # [5, 8, 13]
        results['Reine'] = [2.0, 12.0]  # m [7, 6, 10, 1, 16]
        results['Genevieve'] = [1.5, 14.5]  # [15, 2, 16, 6, 11]
        results['Jessica'] = [1.5, 9]  # [1, 10]
        results['Opal'] = [1.5, 14.0]  # [6, 1, 4, 8, 14]
        results['Lais'] = [1.0, 13.0]  # [2, 9, 15, 5, 6]

        from chess_models.management.commands.populate import Command
        command = Command()
        command.handle()
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.addToRankingList(RankingSystem.BUCHHOLZ.value)

        resultsPoints = getScores(tournament)
        playersList = getOpponents(tournament, resultsPoints)
        getAdjustedScoresList = getAdjustedScores(tournament, playersList)
        getBuchholzList = getBuchholz(tournament, getAdjustedScoresList)
        buchholz = RankingSystem.BUCHHOLZ
        for k, v in getBuchholzList.items():
            self.assertEqual(v[buchholz], results[k.name][1])
        playersList = getRanking(tournament)
        buchholz = RankingSystem.BUCHHOLZ
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #      playerK.name,
            #      playerV[buchholz], playerV['rank'],
            #      flush=True)
            self.assertEqual(playerV[buchholz], results[playerK.name][1])
        self.assertEqual(len(playersList), len(results))

    @tag("suizo")
    def test_016_tournament_getBuchholzCutMinusOne(self):  # no ROB
        """Test function getPoints that returns a list of
        players"""
        results = {}
        results['Bruno'] = [4, 12.]  # pp [10, 7, 1, 16, 3]
        results['Alyx'] = [3.5, 11.]  # pp [9, 13, 2, 15, 4]
        results['Charline'] = [3.5, 13.]  # pp [11, 5, 8, 4, 2]
        results['David'] = [3.5, 11.5]  # p [12, 13, 3, 1]
        results['Stephan'] = [3.5, 11.0]  # pp [8, 11, 7, 2, 15]
        results['Franck'] = [3, 11]  # [14, 3, 10, 8]
        results['Elene'] = [2.5, 7.5]  # pp [13, 15, 11, 7, 10]
        results['Irina'] = [2.5, 12.0]  # pp [16, 14, 3, 13, 5]
        results['Maria'] = [2.5, 12.0]  # pp [3, 16, 5, 9, 7], 11
        results['Nick (W)'] = [2, 9.5]  # [4]
        results['Paul'] = [2, 9.0]  # [5, 8, 13]
        results['Reine'] = [2.0, 11.0]  # m [7, 6, 10, 1, 16]
        results['Genevieve'] = [1.5, 12.5]  # [15, 2, 16, 6, 11]
        results['Jessica'] = [1.5, 7.5]  # [1, 10]
        results['Opal'] = [1.5, 12.0]  # [6, 1, 4, 8, 14]
        results['Lais'] = [1.0, 11.5]  # [2, 9, 15, 5, 6]

        from chess_models.management.commands.populate import Command
        command = Command()
        command.handle()
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.addToRankingList(RankingSystem.BUCHHOLZ_CUT1.value)

        resultsPoints = getScores(tournament)
        playersList = getOpponents(tournament, resultsPoints)
        getAdjustedScoresList = getAdjustedScores(tournament, playersList)
        getBuchholzList = getBuchholzCutMinusOne(tournament,
                                                 getAdjustedScoresList)
        buchholzcut1 = RankingSystem.BUCHHOLZ_CUT1
        for k, v in getBuchholzList.items():
            # print(k.name)
            self.assertEqual(v[buchholzcut1], results[k.name][1])
        playersList = getRanking(tournament)
        # score = RankingSystem.PLAIN_SCORE
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #       playerK.name,
            #       playerV[score], playerV['rank'],
            #       flush=True)
            self.assertEqual(playerV[buchholzcut1], results[playerK.name][1])
        self.assertEqual(len(playersList), len(results))

    @tag("suizo")
    def test_017_tournament_getMediamBuchholz(self):  # no ROB
        """Test function getPoints that returns a list of
        players"""
        results = {}
        results['Bruno'] = [4, 13.6]  # pp [10, 7, 1, 16, 3]
        results['Alyx'] = [3.5, 12.6]  # pp [9, 13, 2, 15, 4]
        results['Charline'] = [3.5, 13.4]  # pp [11, 5, 8, 4, 2]
        results['David'] = [3.5, 13.375]  # p [12, 13, 3, 1]
        results['Stephan'] = [3.5, 13.3]  # pp [8, 11, 7, 2, 15]
        results['Franck'] = [3, 13.25]  # [14, 3, 10, 8]
        results['Elene'] = [2.5, 13.4]  # pp [13, 15, 11, 7, 10]
        results['Irina'] = [2.5, 13.0]  # pp [16, 14, 3, 13, 5]
        results['Maria'] = [2.5, 12.75]  # pp [3, 16, 5, 9, 7], 11
        results['Nick (W)'] = [2, 15.0]  # [4]
        results['Paul'] = [2, 13.167]  # [5, 8, 13]
        results['Reine'] = [2.0, 12.20]  # m [7, 6, 10, 1, 16]
        results['Genevieve'] = [1.5, 11.9]  # [15, 2, 16, 6, 11]
        results['Jessica'] = [1.5, 12.75]  # [1, 10]
        results['Opal'] = [1.5, 12.1]  # [6, 1, 4, 8, 14]
        results['Lais'] = [1.0, 10.9]  # [2, 9, 15, 5, 6]

        from chess_models.management.commands.populate import Command
        command = Command()
        command.handle()
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.addToRankingList(RankingSystem.BUCHHOLZ_AVERAGE.value)

        resultsPoints = getScores(tournament)
        playersList = getOpponents(tournament, resultsPoints)
        getAdjustedScoresList = getAdjustedScores(tournament, playersList)
        getBuchholzList = getBuchholz(tournament, getAdjustedScoresList)
        getBuchholzListMediam = getMediamBuchholz(
            tournament, getBuchholzList)
        averagebuchholz = RankingSystem.BUCHHOLZ_AVERAGE
        for k, v in getBuchholzListMediam.items():
            self.assertAlmostEqual(v[averagebuchholz], results[k.name][1],
                                   delta=0.001)
        playersList = getRanking(tournament)
        # score = RankingSystem.PLAIN_SCORE
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #       playerK.name,
            #       playerV[score], playerV['rank'],
            #       flush=True)
            self.assertAlmostEqual(playerV[averagebuchholz],
                                   results[playerK.name][1],
                                   delta=0.001)
        self.assertEqual(len(playersList), len(results))

    @tag("suizo")
    def test_018_tournament_getSonnebornBerger(self):  # no ROB
        """Test function getPoints that returns a list of
        players"""
        results = {}
        results['Bruno'] = [4, 9.5]  # pp [10, 7, 1, 16, 3]
        results['Alyx'] = [3.5, 8]  # pp [9, 13, 2, 15, 4]
        results['Charline'] = [3.5, 10.5]  # pp [11, 5, 8, 4, 2]
        results['David'] = [3.5, 9.75]  # p [12, 13, 3, 1]
        results['Stephan'] = [3.5, 7.25]  # pp [8, 11, 7, 2, 15]
        results['Franck'] = [3, 6.5]  # [14, 3, 10, 8]
        results['Elene'] = [2.5, 4.25]  # pp [13, 15, 11, 7, 10]
        results['Irina'] = [2.5, 5.25]  # pp [16, 14, 3, 13, 5]
        results['Maria'] = [2.5, 5.75]  # pp [3, 16, 5, 9, 7], 11
        results['Nick (W)'] = [2, 4.00]  # [4]
        results['Paul'] = [2, 4.50]  # [5, 8, 13]
        results['Reine'] = [2.0, 3.50]  # m [7, 6, 10, 1, 16]
        results['Genevieve'] = [1.5, 3.25]  # [15, 2, 16, 6, 11]
        results['Jessica'] = [1.5, 2.25]  # [1, 10]
        results['Opal'] = [1.5, 4.25]  # [6, 1, 4, 8, 14]
        results['Lais'] = [1.0, 1.50]  # [2, 9, 15, 5, 6]

        from chess_models.management.commands.populate import Command
        command = Command()
        command.handle()
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.addToRankingList(RankingSystem.SONNEBORN_BERGER.value)

        resultsPoints = getScores(tournament)
        playersList = getOpponents(tournament, resultsPoints)
        getAdjustedScoresList = getAdjustedScores(tournament, playersList)
        sonnebornbergerList = getSonnebornBerger(
            tournament, getAdjustedScoresList)
        sonnebornberger = RankingSystem.SONNEBORN_BERGER
        for k, v in sonnebornbergerList.items():
            self.assertAlmostEqual(v[sonnebornberger],
                                   results[k.name][1],
                                   places=2)
        playersList = getRanking(tournament)
        # buchholz = RankingSystem.BUCHHOLZ
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #      playerK.name,
            #      playerV[buchholz], playerV['rank'],
            #      flush=True)
            self.assertEqual(playerV[sonnebornberger],
                             results[playerK.name][1])
        self.assertEqual(len(playersList), len(results))

    @tag("continua")
    def test_019_tournament_getBlackWins(self):  # ROB yes
        """Test function getPoints that returns a list of
        players"""
        results = {}  # score, win, played with blacks
        results['Bruno'] = [4, 3, 3]  # pp [10, 7, 1, 16, 3]
        results['Alyx'] = [3.5, 2, 2]  # pp [9, 13, 2, 15, 4]
        results['Charline'] = [3.5, 2, 2]  # pp [11, 5, 8, 4, 2]
        results['David'] = [3.5, 2, 2]  # p [12, 13, 3, 1]
        results['Stephan'] = [3.5, 3, 2]  # pp [8, 11, 7, 2, 15]
        results['Franck'] = [3, 2, 2]  # [14, 3, 10, 8]
        results['Elene'] = [2.5, 2, 2]  # pp [13, 15, 11, 7, 10]
        results['Irina'] = [2.5, 2, 2]  # pp [16, 14, 3, 13, 5]
        results['Maria'] = [2.5, 1, 2]  # pp [3, 16, 5, 9, 7], 11
        results['Nick (W)'] = [2, 0, 0]  # [4]
        results['Paul'] = [2, 2, 2]  # [5, 8, 13]
        results['Reine'] = [2.0, 2, 3]  # m [7, 6, 10, 1, 16]
        results['Genevieve'] = [1.5, 1, 3]  # [15, 2, 16, 6, 11]
        results['Jessica'] = [1.5, 0, 1]  # [1, 10]
        results['Opal'] = [1.5, 1, 3]  # [6, 1, 4, 8, 14]
        results['Lais'] = [1.0, 1, 3]  # [2, 9, 15, 5, 6]

        from chess_models.management.commands.populate import Command
        command = Command()
        command.handle()
        tournament_name = 'tie-breaking exercises swiss'
        tournament = Tournament.objects.get(name=tournament_name)
        tournament.addToRankingList(RankingSystem.BLACKTIMES.value)

        resultsPoints = getScores(tournament)
        winsblackList = getBlackWins(tournament, resultsPoints)
        # winsblackList = []*len(result)
        # print("resultsPoints", resultsPoints)
        # print("winsblackList", winsblackList)

        blacktimes = RankingSystem.BLACKTIMES
        for k, v in resultsPoints.items():
            # print(k, v)
            self.assertEqual(v[blacktimes],
                             results[k.name][2])
        playersList = getRanking(tournament)
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #       playerK.name,
            #       playerV[blacktimes],
            #       flush=True)
            self.assertEqual(playerV[blacktimes],
                             results[playerK.name][2])
        self.assertEqual(len(playersList), len(results))
        tournament.removeFromRankingList(RankingSystem.BLACKTIMES.value)
        tournament.addToRankingList(RankingSystem.WINS.value)
        wins = RankingSystem.WINS
        for k, v in winsblackList.items():
            # print(k, v)
            self.assertEqual(v[wins],
                             results[k.name][1])  # what [1] is here
        playersList = getRanking(tournament)
        # buchholz = RankingSystem.BUCHHOLZ
        for i, (playerK, playerV) in enumerate(playersList.items()):
            # print(f"{i+1:02d}",
            #      playerK.name,
            #      playerV[buchholz], playerV['rank'],
            #      flush=True)
            self.assertEqual(playerV[wins], results[playerK.name][1])
        self.assertEqual(len(playersList), len(results))

    @tag("continua")
    def test_020_check_getRoundCount(self):  # ROB yes
        "check function getRoundCount and similars"
        tournament_name = 'tournament_01'
        tournament = Tournament.objects.create(
            name=tournament_name)
        self.assertEqual(tournament.getRoundCount(), 0)
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 0)
        self.assertIsNone(tournament.get_latest_round_with_games())

        round = Round.objects.create(
            name='round_01', tournament=tournament)
        self.assertEqual(tournament.getRoundCount(), 1)
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 0)
        num = tournament.get_latest_round_with_games()
        self.assertIsNone(num)

        game = Game(round=round, finished=True)  # noqa F841
        game.save()
        self.assertEqual(tournament.getRoundCount(), 1)
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 1)
        self.assertEqual(tournament.get_latest_round_with_games().id, round.id)

        round2 = Round.objects.create(  # noqa F841
            name='round_02', tournament=tournament)
        game2 = Game(round=round, finished=True)  # noqa F841
        game2.save()
        self.assertEqual(tournament.getRoundCount(), 2)
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 1)
        self.assertEqual(tournament.get_latest_round_with_games().id, round.id)

        self.assertEqual(tournament.getRoundCount(), 2)
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 1)
        self.assertEqual(tournament.get_latest_round_with_games().id, round.id)

        game3 = Game(round=round2, finished=True)
        game3.save()
        self.assertEqual(tournament.getRoundCount(), 2)
        self.assertEqual(tournament.get_number_of_rounds_with_games(), 2)
        self.assertEqual(
            tournament.get_latest_round_with_games().id, round2.id)
