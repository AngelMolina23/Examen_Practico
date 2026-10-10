"""Linea base de grafos aleatorios independientes."""

import random
import time

from oraculo import aptitud, evaluar_grafo
from utilidades import PROBABILIDAD_ARISTA_INICIAL, cromosoma_a_grafo, generar_cromosoma


def registrar_evaluacion(
	clasificacion, numero, primeras, incidencias, acumulados, casos, grafo, metodo, semilla
):
	for agente, discrepancias in clasificacion["contraejemplos"].items():
		if discrepancias:
			primeras.setdefault(agente, numero)
			acumulados[agente] += 1
			if agente not in casos:
				evidencia = clasificacion["resultados"][agente]
				caso = {
					"metodo": metodo,
					"semilla": semilla,
					"evaluacion": numero,
					"agente": agente,
					"grafo": grafo,
					"referencia": evidencia["verificacion"]["referencia"],
					"resultado": evidencia["resultado"],
					"discrepancias": discrepancias,
				}
				if agente == "A1":
					caso["heuristica"] = clasificacion["heuristica"]
				casos[agente] = caso
	for agente, resultado in clasificacion["incidencias"].items():
		estado = resultado["estado"]
		incidencias[estado] = incidencias.get(estado, 0) + 1


def ejecutar_aleatorio(
	semilla: int,
	presupuesto: int = 1000,
	intervalo_registro: int = 30,
	limite_expansiones: int = 100,
	probabilidad_arista: float = PROBABILIDAD_ARISTA_INICIAL,
) -> dict:
	if type(semilla) is not int or type(presupuesto) is not int or presupuesto <= 0:
		raise ValueError("semilla y presupuesto deben ser enteros; presupuesto debe ser positivo")
	if type(intervalo_registro) is not int or intervalo_registro <= 0:
		raise ValueError("intervalo_registro debe ser entero positivo")

	rng = random.Random(semilla)
	primeras = {}
	incidencias = {"limite": 0, "error": 0}
	acumulados = {"B1": 0, "U1": 0, "A1": 0}
	casos = {}
	evaluados = set()
	progreso = []
	mejor = None
	inicio_tiempo = time.perf_counter()

	for numero in range(1, presupuesto + 1):
		cromosoma = generar_cromosoma(rng, probabilidad_arista)
		grafo = cromosoma_a_grafo(cromosoma)
		clasificacion = evaluar_grafo(grafo, limite_expansiones)
		registrar_evaluacion(
			clasificacion, numero, primeras, incidencias, acumulados, casos,
			grafo, "aleatorio", semilla
		)
		evaluados.add(cromosoma)
		individuo = {
			"cromosoma": cromosoma,
			"grafo": grafo,
			"clasificacion": clasificacion,
			"aptitud": aptitud(clasificacion, grafo),
		}
		if mejor is None or (individuo["aptitud"], individuo["cromosoma"]) > (
			mejor["aptitud"], mejor["cromosoma"]
		):
			mejor = individuo
		if numero % intervalo_registro == 0 or numero == presupuesto:
			progreso.append(
				{
					"evaluaciones": numero,
					"mejor_aptitud": list(mejor["aptitud"]),
					"primer_hallazgo": dict(primeras),
					"hallazgos_acumulados": dict(acumulados),
				}
			)

	return {
		"metodo": "aleatorio",
		"semilla": semilla,
		"configuracion": {
			"distribucion": f"Bernoulli(p={probabilidad_arista}) por arista; costo uniforme 1..9",
			"probabilidad_arista_inicial": probabilidad_arista,
			"limite_expansiones": limite_expansiones,
			"intervalo_registro": intervalo_registro,
		},
		"presupuesto": presupuesto,
		"evaluaciones": presupuesto,
		"grafos_distintos": len(evaluados),
		"grafos_distintos_claves": sorted("".join(map(str, cromosoma)) for cromosoma in evaluados),
		"primer_hallazgo": primeras,
		"primeros_casos": casos,
		"incidencias": incidencias,
		"hallazgos_acumulados": acumulados,
		"mejor": {
			"cromosoma": list(mejor["cromosoma"]),
			"grafo": mejor["grafo"],
			"aptitud": list(mejor["aptitud"]),
			"clasificacion": mejor["clasificacion"],
		},
		"progreso": progreso,
		"tiempo_segundos": time.perf_counter() - inicio_tiempo,
	}
