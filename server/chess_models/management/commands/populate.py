# This script populates the database from a trf file
# import required modules and classes
# RTF file format available at:
# https://www.fide.com/FIDE/handbook/C04Annex2_TRF16.pdf 
# module description available at:
# https://github.com/sklangen/TRF?tab=readme-ov-file
import trf
from django.core.management.base import BaseCommand
from chess_models.models import Tournament, Player, Round, Game
from chess_models.models import (TournamentType, TournamentBoardType,
                                 Color, Scores, RankingSystem)


class Command(BaseCommand):
    # Help text displayed when running `python manage.py help populate`
    help = """populate database
           """

    def handle(self, *args, **kwargs):
        # Main method called when the command is executed
        self.cleanDataBase()  # Clean the database
        # READ a single file if you want to keep the IDs
        self.readInputFile(
            'chess_models/management/commands/tie-breaking-swiss.trf')
        self.insertData()      # Insert data into the database

    def cleanDataBase(self):
        # Delete all existing records from the database
        pass

    def readInputFile(self, filename):
        # Read the TRF file containing tournament information
        with open(filename) as f:
            self.tour = trf.load(f)

    def insertData(self):
        playersDict = {}  # Dictionary to hold players by their starting rank
        roundDict = {}    # Dictionary to hold rounds by their number

        # Create and save a new tournament


        # Create and save rounds for the tournament
        for i in range(1, self.tour.numrounds+1):
            pass

        # Create and save players for the tournament
        for player in self.tour.players:
            id = player.startrank
            pass

            # assign player to tournament

        # 0000 - U    14 - +
        # Create and save games for the tournament
        for player in self.tour.players:
            for game in player.games:

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

