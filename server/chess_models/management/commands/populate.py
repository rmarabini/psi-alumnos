# This script populates the database from a trf file
# import required modules and classes
# RTF file format available at:
# https://www.fide.com/FIDE/handbook/C04Annex2_TRF16.pdf
import trf
from django.core.management.base import BaseCommand
from chess_models.models import Tournament, Player, Round, Game
from chess_models.models import (TournamentType, TournamentBoardType,
                                 Color, Scores, RankingSystem)
# from django.utils.text import slugify
from django.db import connection
from django.core.management.color import no_style


class Command(BaseCommand):
    # Help text displayed when running `python manage.py help populate`
    help = """populate database
           """

    def handle(self, *args, **kwargs):
        # Main method called when the command is executed
        self.cleanDataBase()  # Clean the database
        # READ a single file if you want to keep the IDs
        # self.readInputFile(
        #    'chess_models/management/commands/tie-breaking-robin.trf')
        # self.insertData()      # Insert data into the database
        #
        self.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        self.insertData()      # Insert data into the database

    def cleanDataBase(self):
        # Delete all existing records from the database
        Game.objects.all().delete()
        Round.objects.all().delete()
        Player.objects.all().delete()
        Tournament.objects.all().delete()
    
    def update_sequence(self):
        # since I have used the ID from the TRF file
        # I need to update the sequence to the last ID
        # since now the sequence is 1 (at least for players)

        sequence_sql = connection.ops.sequence_reset_sql(
            no_style(), [Player])
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)

    def readInputFile(self, filename):
        # Read the TRF file containing tournament information
        with open(filename) as f:
            self.tour = trf.load(f)

    def insertData(self):
        playersDict = {}  # Dictionary to hold players by their starting rank
        roundDict = {}    # Dictionary to hold rounds by their number

        # Create and save a new tournament
        tour = Tournament(name=self.tour.name,
                          board_type=TournamentBoardType.OTB.value,
                          tournament_type=TournamentType.SWISS.value,)
        tour.save()
        tour.addToRankingList(RankingSystem.BUCHHOLZ_AVERAGE)
        tour.addToRankingList(RankingSystem.BUCHHOLZ_CUT1)
        tour.addToRankingList(RankingSystem.BUCHHOLZ)
        tour.save()

        # Create and save rounds for the tournament
        for i in range(1, self.tour.numrounds+1):
            r = Round(name=f"round_{i:02d}", tournament=tour)
            r.save()
            roundDict[i] = r

        # Create and save players for the tournament
        for player in self.tour.players:
            id = player.startrank
            name = player.name
            _players = Player.objects.filter(name=name)
            if _players.exists():
                print(f"Player {name} already exists================")
                _player = _players.first()
            else:
                _player = Player(id=id, name=name)
                _player.fide_rating_classical = player.rating
                _player.save()

            # assign player to tournament
            tour.players.add(_player)
            playersDict[player.startrank] = _player
        tour.save()
        # 0000 - U    14 - +
        # Create and save games for the tournament
        for player in self.tour.players:
            for game in player.games:
                if game.color == Color.NOCOLOR:
                    r = game.result
                    if r == Scores.FORFEITWIN:  # this is a bye
                        white = playersDict[player.startrank]
                        black = playersDict[game.startrank]
                    elif r == Scores.FORFEITLOSS:
                        if game.startrank == 0:
                            white = playersDict[player.startrank]
                            black = None
                        else:
                            continue
                    elif r == Scores.BYE_F or r == Scores.BYE_H or\
                            r == Scores.BYE_U or r == Scores.BYE_Z:
                        white = playersDict[player.startrank]
                        black = None
                # Check if the player is playing white
                elif game.color == Color.WHITE:
                    white = playersDict[player.startrank]
                    black = playersDict[game.startrank]
                else:
                    # Skip if the player is playing black
                    # skip if no color and player lost ( --)
                    # since the game is already processed
                    continue
                round = roundDict[game.round]
                if game.result == '1':
                    result = Scores.WHITE
                elif game.result == '0':
                    result = Scores.BLACK
                elif game.result == '=':
                    result = Scores.DRAW
                elif game.result == '+':
                    result = Scores.FORFEITWIN
                elif game.result == '-':
                    result = Scores.FORFEITLOSS
                elif game.result == 'H':
                    result = Scores.BYE_H
                elif game.result == 'F':
                    result = Scores.BYE_F
                elif game.result == 'U':
                    result = Scores.BYE_U
                elif game.result == 'Z':
                    result = Scores.BYE_Z
                else:
                    result = Scores.NOAVAILABLE

                g = Game(white=white, black=black,
                         round=round, finished=True,
                         result=result)
                g.save()
        # By default seq=1, find las ID and
        # set the sequence to the last ID
        self.update_sequence()
        all_games = Game.objects.all()
        # for game in all_games:
        #     print("game", game,  game.round.tournament.id)
