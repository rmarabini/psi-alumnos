"""
test_utils.py  -  Tests unitarios para el módulo utils.
"""

import unittest
from utils import crear_tarea, marcar_completada, filtrar_por_prioridad, ordenar_tareas, resumen


class TestCrearTarea(unittest.TestCase):

    def test_crea_tarea_con_titulo(self):
        t = crear_tarea("Estudiar Python")
        self.assertEqual(t["titulo"], "Estudiar Python")

    def test_prioridad_por_defecto(self):
        t = crear_tarea("Leer documentación")
        self.assertEqual(t["prioridad"], 1)

    def test_prioridad_personalizada(self):
        t = crear_tarea("Entregar práctica", prioridad=3)
        self.assertEqual(t["prioridad"], 3)

    def test_tarea_no_completada_por_defecto(self):
        t = crear_tarea("Revisar código")
        self.assertFalse(t["completada"])


class TestMarcarCompletada(unittest.TestCase):

    def test_marca_como_completada(self):
        t = crear_tarea("Hacer commit")
        marcar_completada(t)
        self.assertTrue(t["completada"])

    def test_devuelve_la_misma_tarea(self):
        t = crear_tarea("Escribir tests")
        resultado = marcar_completada(t)
        self.assertIs(resultado, t)


class TestFiltrarPorPrioridad(unittest.TestCase):

    def setUp(self):
        self.tareas = [
            crear_tarea("A", prioridad=1),
            crear_tarea("B", prioridad=2),
            crear_tarea("C", prioridad=1),
            crear_tarea("D", prioridad=3),
        ]

    def test_filtra_prioridad_1(self):
        resultado = filtrar_por_prioridad(self.tareas, 1)
        self.assertEqual(len(resultado), 2)

    def test_filtra_prioridad_inexistente(self):
        resultado = filtrar_por_prioridad(self.tareas, 5)
        self.assertEqual(resultado, [])


class TestOrdenarTareas(unittest.TestCase):

    def test_ordena_de_mayor_a_menor(self):
        tareas = [crear_tarea("X", 1), crear_tarea("Y", 3), crear_tarea("Z", 2)]
        ordenadas = ordenar_tareas(tareas)
        prioridades = [t["prioridad"] for t in ordenadas]
        self.assertEqual(prioridades, [3, 2, 1])

    def test_lista_vacia(self):
        self.assertEqual(ordenar_tareas([]), [])


class TestResumen(unittest.TestCase):

    def test_resumen_sin_completadas(self):
        tareas = [crear_tarea("A"), crear_tarea("B")]
        r = resumen(tareas)
        self.assertEqual(r["total"], 2)
        self.assertEqual(r["completadas"], 0)
        self.assertEqual(r["pendientes"], 2)

    def test_resumen_con_completadas(self):
        tareas = [crear_tarea("A"), crear_tarea("B")]
        marcar_completada(tareas[0])
        r = resumen(tareas)
        self.assertEqual(r["completadas"], 1)
        self.assertEqual(r["pendientes"], 1)

    def test_resumen_lista_vacia(self):
        r = resumen([])
        self.assertEqual(r["total"], 0)


if __name__ == "__main__":
    unittest.main()
