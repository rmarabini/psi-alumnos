"""
main.py  -  Interfaz de línea de comandos para la gestión de tareas.
"""

from utils import crear_tarea, marcar_completada, filtrar_por_prioridad, ordenar_tareas, resumen

# Lista global de tareas (en memoria)
tareas = []


def agregar_tarea(titulo, prioridad):
    """Pide los datos al usuario y añade una nueva tarea a la lista."""
    nueva = crear_tarea(titulo, prioridad)
    tareas.append(nueva)
    print(f"Tarea '{titulo}' añadida con prioridad {prioridad}.")


def completar_tarea(indice):
    """Marca como completada la tarea en la posición indicada."""
    tarea = tareas[indice]
    marcar_completada(tarea)
    print(f"Tarea '{tarea['titulo']}' marcada como completada.")


def listar_tareas():
    """Muestra todas las tareas ordenadas por prioridad."""
    ordenadas = ordenar_tareas(tareas)
    if not ordenadas:
        print("No hay tareas registradas.")
        return
    for i, t in enumerate(ordenadas):
        estado = "✓" if t["completada"] else "○"
        print(f"  [{estado}] ({t['prioridad']}) {t['titulo']}")


def mostrar_resumen():
    """Imprime un resumen del estado actual de las tareas."""
    datos = resumen(tareas)
    print(f"Total: {datos['total']}  |  Completadas: {datos['completadas']}  |  Pendientes: {datos['pendientes']}")


def menu():
    """Bucle principal del menú interactivo."""
    opciones = {
        "1": ("Añadir tarea", lambda: agregar_tarea(input("  Título: "), int(input("  Prioridad (1-3): ")))),
        "2": ("Completar tarea", lambda: completar_tarea(int(input("  Índice de tarea: ")))),
        "3": ("Listar tareas", listar_tareas),
        "4": ("Ver resumen", mostrar_resumen),
        "5": ("Salir", None),
    }

    while True:
        print("\n=== Gestor de Tareas ===")
        for clave, (desc, _) in opciones.items():
            print(f"  {clave}. {desc}")
        eleccion = input("Opción: ").strip()

        if eleccion == "5":
            print("¡Hasta luego!")
            break
        elif eleccion in opciones:
            _, accion = opciones[eleccion]
            accion()
        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    menu()
