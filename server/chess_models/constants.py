from django.db import models
from django.utils.translation import gettext_lazy as _


class RankingSystem(models.TextChoices):
    """
    Método de clasificación utilizado en el torneo para determinar
    el ranking de los jugadores. Los sistemas de ranking son cruciales
    para desempatar y asignar posiciones basadas en el rendimiento.

    Opciones de sistemas de ranking:
    - Buchholz: Utiliza la suma de las puntuaciones de los oponentes
      para desempatar.
    - Buchholz Cut 1: Similar al Buchholz, pero excluyendo el peor oponente.
    - Buchholz Average: Promedio de las puntuaciones de los oponentes.
    - Sonneborn-Berger: Calcula el rendimiento ponderando los oponentes
    vencidos.
    - Plain Score: Clasificación basada únicamente en el número de puntos
    obtenidos.
    - Wins: Desempata por el número de victorias conseguidas.
    - Black Times: Prioriza a jugadores que han jugado más veces con las
    piezas negras.
    """
    
    # El sistema Buchholz suma las puntuaciones obtenidas por los oponentes 
    # de un jugador. Este método es útil para desempatar cuando varios 
    # jugadores tienen la misma cantidad de puntos.
    BUCHHOLZ = 'BU', _('Buchholz')
    
    # Buchholz Cut 1 es una variante del sistema Buchholz en el cual 
    # se excluye la puntuación del peor oponente para calcular el desempate.
    BUCHHOLZ_CUT1 = 'BC', _('Buchholz Cut 1')
    
    # El promedio de las puntuaciones de los oponentes se utiliza como 
    # criterio de desempate en el sistema Buchholz Average.
    BUCHHOLZ_AVERAGE = 'BA', _('Buchholz Average')
    
    # Sonneborn-Berger es un método de desempate que pondera las victorias 
    # frente a oponentes más fuertes, es decir, otorga mayor valor a 
    # las victorias contra jugadores con mejores resultados.
    SONNEBORN_BERGER = 'SB', _('Sonneborn-Berger')
    
    # Plain Score simplemente clasifica a los jugadores según 
    # la cantidad de puntos que hayan acumulado en el torneo, sin usar
    # desempates.
    PLAIN_SCORE = 'PS', _('Plain Score')
    
    # Este sistema de desempate clasifica a los jugadores según el número 
    # de victorias obtenidas en el torneo.
    WINS = 'WI', _('No. Wins')
    
    # Black Times desempata en favor de los jugadores que hayan 
    # jugado más partidas con las piezas negras, que normalmente se
    # considera una ligera desventaja.
    BLACKTIMES = 'BT', _('No. games played with Black')


class TournamentSpeed(models.TextChoices):
    """
    Define las categorías de 'velocidad' del torneo, que se refieren al 
    tiempo disponible para cada jugador. La elección del ritmo de juego 
    afecta significativamente la estrategia y estilo de las partidas.

    Opciones:
    - BU: Bullet (partidas extremadamente rápidas, no reconocidas por FIDE).
    - BL: Blitz (partidas rápidas).
    - RA: Rapid (ritmo intermedio entre Blitz y Clásico).
    - CL: Clásico (partidas con tiempos más largos,
    típicas de torneos formales).

    Nota: Lichess y FIDE usan definiciones ligeramente distintas para
    estos ritmos.
    """
    
    # El ritmo Bullet es un formato de partidas ultrarrápidas,
    # generalmente con menos de 3 minutos por jugador para toda la partida.
    # No está reconocido oficialmente por FIDE.
    BULLET = 'BU', _('Bullet')
    
    # El Blitz es un ritmo de juego rápido, donde cada jugador tiene entre
    # 3 y 10 minutos en total. Es reconocido tanto por FIDE como por
    # plataformas de ajedrez en línea.
    BLITZ = 'BL', _('Blitz')
    
    # En el ritmo Rapid, cada jugador dispone de entre 10 y 30 minutos 
    # para toda la partida. Es un ritmo intermedio que permite mayor
    # reflexión que Blitz, pero sigue siendo más rápido que el Clásico.
    RAPID = 'RA', _('Rápido')
    
    # El ritmo Clásico es el más largo y típico en competiciones oficiales.
    # Generalmente, cada jugador tiene más de 60 minutos para completar
    # la partida, lo que favorece el análisis profundo y la estrategia.
    CLASSICAL = 'CL', _('Clásico')


class TournamentType(models.TextChoices):
    """
    Define los tipos de torneos disponibles. Cada tipo representa una
    forma distinta de organizar los enfrentamientos entre los participantes.

    Opciones:
    - SR: Round Robin Simple (todos juegan contra todos una vez).
    - DR: Round Robin Doble (todos juegan dos veces, una con blancas y
    una con negras).
    - DD: Round Robin Doble en un solo día (ambas partidas consecutivas,
    una con cada color).
    - SW: Sistema Suizo (pares basados en el rendimiento actual).
    """
    
    # En un torneo Round Robin simple, cada participante juega
    # una vez contra cada uno de los demás participantes.
    ROUNDROBIN = 'SR', _('Round Robin Simple')
    
    # En un torneo Round Robin doble, cada participante juega dos veces
    # contra cada otro participante: una partida con blancas y otra con negras.
    DOUBLEROUNDROBIN = 'DR', _('Round Robin Doble')
    
    # En un torneo Round Robin doble en el mismo día, cada participante
    # juega dos veces consecutivas contra cada oponente, intercambiando colores
    # (blancas y negras), y ambas partidas se juegan el mismo día.
    DOUBLEROUNDROBINSAMEDAY = 'DD', _('Round Robin Doble (mismo día)')
    
    # En un torneo suizo, los participantes no juegan todos contra todos.
    # En su lugar, los emparejamientos se realizan basados en los resultados
    # previos, enfrentando a jugadores con puntuaciones similares en cada
    # ronda.
    SWISS = 'SW', _('Sistema Suizo')


class TournamentBoardType(models.TextChoices):
    """
    Define el tipo de tablero donde se juega el torneo, es decir,
    si el torneo se lleva a cabo en línea o de manera presencial.

    Opciones:
    - LICHESS: Torneos jugados en línea en la plataforma lichess.org.
    - OTB: (Over The Board) Partidas jugadas de forma presencial,
           con un tablero físico.

    Cada tipo de tablero influye en la dinámica y logística del torneo, 
    desde la interacción de los jugadores hasta la modalidad de organización.
    """
    
    # Torneos que se juegan en línea en la plataforma lichess.org.
    # Estos torneos permiten a jugadores de todo el mundo competir 
    # de manera remota.
    LICHESS = 'LIC', _('lichess')
    
    # "Over The Board" (OTB) se refiere a torneos presenciales donde 
    # los jugadores se enfrentan físicamente en un tablero real. 
    # Son el formato tradicional de torneos, común en clubes y eventos
    # oficiales.
    OTB = 'OTB', _('over the board')


class Color(models.TextChoices):
    """
    Color asignado a un jugador en una partida de ajedrez.
    Este campo se utiliza para indicar si un jugador juega con
      piezas blancas, negras, o si no se asigna color en casos
      especiales como victorias por incomparecencia o bye.

    Opciones de color:
    - White: El jugador juega con las piezas blancas.
    - Black: El jugador juega con las piezas negras.
    - No Color: Sin asignación de color, generalmente usado para victorias por
    default o bye.
    """
    WHITE = 'w', _('White')   # Piezas blancas asignadas al jugador.
    BLACK = 'b', _('Black')   # Piezas negras asignadas al jugador.
    # Sin color, en casos de victoria por incomparecencia o bye.
    NOCOLOR = '-', _('No Color')


class Scores(models.TextChoices):
    """
    Posibles resultados de una partida de ajedrez, siguiendo la notación
    oficial de la FIDE.
    Referencia: https://www.fide.com/FIDE/handbook/C04Annex2_TRF16.pdf

    Resultados estándar:
    - White: Victoria para las piezas blancas.
    - Black: Victoria para las piezas negras.
    - Draw: Partida empatada.

    Casos especiales:
    - Forfeit win: Victoria por incomparecencia del oponente.
    - Forfeit loss: Derrota por incomparecencia.
    - Bye: Cuando un jugador no tiene oponente en una ronda,
           o recibe un descanso, se le otorga un "bye",
             que puede variar en el puntaje asignado.
    - No available: Partida no finalizada o sin resultado disponible.
    """
    # Resultados estándar
    WHITE = 'w', _('White')    # Victoria para las piezas blancas
    BLACK = 'b', _('Black')    # Victoria para las piezas negras
    DRAW = '=', _('Draw')      # Partida empatada

    # Casos especiales
    FORFEITWIN = '+', _('Forfeit win')    # Victoria por incomparecencia
    FORFEITLOSS = '-', _('Forfeit loss')  # Derrota por incomparecencia

    # Tipos de 'bye' (punto asignado cuando un jugador no tiene oponente)
    BYE_H = 'H', _('Half point bye')      # Medio punto asignado
    BYE_F = 'F', _('Full point bye')      # Punto completo asignado
    BYE_U = 'U', _('Unpaired game point bye')  # Punto por juego no emparejado
    BYE_Z = 'Z', _('Zero point bye')      # Cero puntos, ausencia conocida (no se califica)

    # Partida no finalizada o sin resultado disponible
    NOAVAILABLE = '*', _('No available')


# Dictionary to convert the value of the Scores class to the label
ScoresFromValue = {
    Scores.WHITE.value: Scores.WHITE.label,
    Scores.BLACK.value: Scores.BLACK.label,
    Scores.DRAW.value: Scores.DRAW.label,
    Scores.FORFEITWIN.value: Scores.FORFEITWIN.label,
    Scores.FORFEITLOSS.value: Scores.FORFEITLOSS.label,
    Scores.BYE_H.value: Scores.BYE_H.label,
    Scores.BYE_F.value: Scores.BYE_F.label,
    Scores.BYE_U.value: Scores.BYE_U.label,
    Scores.BYE_Z.value: Scores.BYE_Z.label,
    Scores.NOAVAILABLE.value: Scores.NOAVAILABLE.label
}

VERYLARGENUMBER = 100000000

# valid lichess users used mainly for testing
LICHESS_USERS = [
    "ertopo",
    "soria49",
    "zaragozana",
    "Clavada",
    "rmarabini",
    "jpvalle",
    "oliva21",
    "Philippe2020",
    "eaffelix",
    "jrcuesta",
]
