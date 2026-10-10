import random
import sys
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(
	0,
	str(RAIZ / "material_docente_busqueda" / "material_busqueda" / "estudiantes"),
)

from aleatorio import ejecutar_aleatorio
from busqueda import ejecutar, evaluar, verificar
from genetico import ejecutar_genetico
from utilidades import (
	PARES_DIRIGIDOS,
	cromosoma_a_grafo,
	cruzar_cromosomas,
	generar_cromosoma,
	grafo_a_cromosoma,
	mutar_cromosoma,
	validar_cromosoma,
)


class PruebasProyecto(unittest.TestCase):
	def test_conversion_de_grafo_y_cromosoma(self):
		grafo = {"n": 6, "inicio": 0, "meta": 5, "aristas": [[0, 1, 4], [1, 5, 2]]}
		cromosoma = grafo_a_cromosoma(grafo)
		self.assertEqual(len(cromosoma), len(PARES_DIRIGIDOS))
		self.assertEqual(cromosoma_a_grafo(cromosoma), grafo)
		with self.assertRaises(ValueError):
			validar_cromosoma([0, 1])

	def test_operadores_preservan_dominio_y_son_reproducibles(self):
		primero = generar_cromosoma(random.Random(11))
		segundo = generar_cromosoma(random.Random(22))
		hijo_a = cruzar_cromosomas(primero, segundo, random.Random(33))
		hijo_b = cruzar_cromosomas(primero, segundo, random.Random(33))
		mutado_a = mutar_cromosoma(hijo_a, random.Random(44))
		mutado_b = mutar_cromosoma(hijo_a, random.Random(44))
		self.assertEqual(hijo_a, hijo_b)
		self.assertEqual(mutado_a, mutado_b)
		validar_cromosoma(mutado_a)
		self.assertLessEqual(len(cromosoma_a_grafo(mutado_a)["aristas"]), 30)

	def test_grafo_sin_ruta_no_es_error_de_formato(self):
		grafo = {"n": 6, "inicio": 0, "meta": 5, "aristas": []}
		self.assertTrue(evaluar(grafo)["B1"]["verificacion"]["concluyente"])
		for agente in ("B1", "U1", "A1"):
			self.assertEqual(ejecutar(agente, grafo)["estado"], "sin_solucion")

	def test_acepta_rutas_alternativas_de_igual_calidad(self):
		grafo = {
			"n": 6,
			"inicio": 0,
			"meta": 5,
			"aristas": [[0, 1, 1], [1, 5, 1], [0, 2, 1], [2, 5, 1]],
		}
		ruta_alternativa = {"estado": "solucion", "ruta": [0, 2, 5], "costo": 2}
		self.assertFalse(verificar("B1", grafo, ruta_alternativa)["contraejemplo"])
		self.assertFalse(verificar("U1", grafo, ruta_alternativa)["contraejemplo"])

	def test_costo_declarado_incorrecto_se_detecta(self):
		grafo = {"n": 6, "inicio": 0, "meta": 5, "aristas": [[0, 1, 2], [1, 5, 3]]}
		resultado = {"estado": "solucion", "ruta": [0, 1, 5], "costo": 99}
		verificacion = verificar("U1", grafo, resultado)
		self.assertTrue(verificacion["contraejemplo"])
		self.assertIn("costo_incorrecto", verificacion["discrepancias"])

	def test_presupuesto_aleatorio_y_genetico(self):
		presupuesto = 9
		aleatorio = ejecutar_aleatorio(11, presupuesto, intervalo_registro=4)
		genetico = ejecutar_genetico(11, presupuesto, {"poblacion": 4})
		self.assertEqual(aleatorio["evaluaciones"], presupuesto)
		self.assertEqual(genetico["evaluaciones"], presupuesto)
		self.assertEqual(aleatorio["progreso"][-1]["evaluaciones"], presupuesto)
		self.assertEqual(genetico["progreso"][-1]["evaluaciones"], presupuesto)

	def test_repeticion_de_semilla_genetica(self):
		configuracion = {"poblacion": 4}
		primera = ejecutar_genetico(55, 8, configuracion)
		segunda = ejecutar_genetico(55, 8, configuracion)
		self.assertEqual(primera["primer_hallazgo"], segunda["primer_hallazgo"])
		self.assertEqual(primera["grafos_distintos_claves"], segunda["grafos_distintos_claves"])
		self.assertEqual(primera["progreso"], segunda["progreso"])


if __name__ == "__main__":
	unittest.main()
