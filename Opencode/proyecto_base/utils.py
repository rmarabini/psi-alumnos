"""
utils.py  -  Funciones de utilidad para la gestión de una lista de tareas.
"""


def crear_tarea(titulo, prioridad=1):
    """Crea y devuelve un diccionario que representa una tarea."""
    return {
        "titulo": titulo,
        "prioridad": prioridad,
        "completada": False,
    }


def marcar_completada(tarea):
    """Marca una tarea como completada."""
    tarea["completada"] = True
    return tarea


def filtrar_por_prioridad(tareas, prioridad):
    """Devuelve las tareas cuya prioridad coincide con el valor indicado."""
    return [t for t in tareas if t["prioridad"] == prioridad]


def ordenar_tareas(tareas):
    """Ordena la lista de tareas de mayor a menor prioridad."""
    return sorted(tareas, key=lambda t: t["prioridad"], reverse=True)


def resumen(tareas):
    """Devuelve un diccionario con estadísticas básicas de la lista de tareas."""
    total = len(tareas)
    completadas = sum(1 for t in tareas if t["completada"])
    return {
        "total": total,
        "completadas": completadas,
        "pendientes": total - completadas,
    }
