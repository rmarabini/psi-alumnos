from django.db import connection
from django.apps import apps
from django.conf import settings

def reset_sequences(tournament=True,
                    player=True,
                    game=True,
                    round=True,
                    verbose=False):
    def reset_sequence(app_name, model_name):
        # Get the model class
        Model = apps.get_model(app_name, model_name)

        # Get the table name and the primary key column
        table_name = Model._meta.db_table
        primary_key_column = Model._meta.pk.column

        with connection.cursor() as cursor:
            # Get the name of the sequence associated with the primary key column
            cursor.execute(f"SELECT pg_get_serial_sequence(\'{table_name}\', \'{primary_key_column}\');")
            sequence_name = cursor.fetchone()[0]

            if sequence_name:
                if verbose:
                    print(f"Resetting sequence {sequence_name} for {table_name}.{primary_key_column}")
                cursor.execute(f"SELECT setval(\'{sequence_name}\', 1, false) FROM {table_name};")
            else:
                print(f"No sequence found for {table_name}.{primary_key_column}")
    if tournament:
        reset_sequence('chess_models', 'Tournament')
    if player:
        reset_sequence('chess_models', 'Player')
    if game:
        reset_sequence('chess_models', 'Game')
    if round:
        reset_sequence('chess_models', 'Round')