"""Algoritmo genetico propio para buscar grafos contraejemplo."""

import random
import time

from aleatorio import registrar_evaluacion
from oraculo import aptitud, evaluar_grafo
from utilidades import (
	PROBABILIDAD_ARISTA_INICIAL,
	cromosoma_a_grafo,
	cruzar_cromosomas,
	generar_cromosoma,
	mutar_cromosoma,
	validar_cromosoma,
)


CONFIGURACION = {
	"poblacion": 30,
	"seleccion": "torneo de tamano 3",
	"probabilidad_cruce": 0.8,
	"probabilidad_mutacion_por_gen": 0.04,
	"reemplazo": "elitista: mejores 30 de padres e hijos",
	"probabilidad_arista_inicial": PROBABILIDAD_ARISTA_INICIAL,
	"limite_expansiones": 100,
}


def _seleccionar_torneo(poblacion, rng: random.Random, tamano: int = 3):
	participantes = rng.sample(poblacion, k=min(tamano, len(poblacion)))
	return max(participantes, key=lambda individuo: (individuo["aptitud"], individuo["cromosoma"]))


def _evaluar_individuo(
	cromosoma, limite_expansiones, contador, primeras, incidencias, acumulados,
	casos, semilla
):
	grafo = cromosoma_a_grafo(cromosoma)
	clasificacion = evaluar_grafo(grafo, limite_expansiones)
	contador["evaluaciones"] += 1
	registrar_evaluacion(
		clasificacion,
		contador["evaluaciones"],
		primeras,
		incidencias,
		acumulados,
		casos,
		grafo,
		"genetico",
		semilla,
	)
	return {
		"cromosoma": validar_cromosoma(cromosoma),
		"grafo": grafo,
		"clasificacion": clasificacion,
		"aptitud": aptitud(clasificacion, grafo),
	}


def ejecutar_genetico(
	semilla: int,
	presupuesto: int = 1000,
	configuracion: dict | None = None,
) -> dict:
	config = dict(CONFIGURACION)
	if configuracion:
		config.update(configuracion)
	poblacion_tamano = config["poblacion"]
	if type(semilla) is not int or type(presupuesto) is not int or presupuesto <= 0:
		raise ValueError("semilla y presupuesto deben ser enteros; presupuesto debe ser positivo")
	if type(poblacion_tamano) is not int or not 1 <= poblacion_tamano <= presupuesto:
		raise ValueError("La poblacion debe estar entre 1 y el presupuesto")
	if not 0 <= config["probabilidad_cruce"] <= 1:
		raise ValueError("probabilidad_cruce debe estar entre 0 y 1")
	if not 0 <= config["probabilidad_mutacion_por_gen"] <= 1:
		raise ValueError("probabilidad_mutacion_por_gen debe estar entre 0 y 1")

	rng = random.Random(semilla)
	contador = {"evaluaciones": 0}
	primeras = {}
	incidencias = {"limite": 0, "error": 0}
	acumulados = {"B1": 0, "U1": 0, "A1": 0}
	casos = {}
	evaluados = set()
	progreso = []
	inicio_tiempo = time.perf_counter()

	poblacion = []
	for _ in range(poblacion_tamano):
		cromosoma = generar_cromosoma(rng, config["probabilidad_arista_inicial"])
		individuo = _evaluar_individuo(
			cromosoma, config["limite_expansiones"], contador, primeras,
			incidencias, acumulados, casos, semilla
		)
		poblacion.append(individuo)
		evaluados.add(individuo["cromosoma"])
	poblacion.sort(key=lambda individuo: (individuo["aptitud"], individuo["cromosoma"]), reverse=True)
	progreso.append(_resumen_generacion(0, contador, poblacion, primeras, acumulados))

	generacion = 0
	hijos_generacion = 0
	while contador["evaluaciones"] < presupuesto:
		padre_a = _seleccionar_torneo(poblacion, rng)
		padre_b = _seleccionar_torneo(poblacion, rng)
		if rng.random() < config["probabilidad_cruce"]:
			hijo = cruzar_cromosomas(padre_a["cromosoma"], padre_b["cromosoma"], rng)
		else:
			hijo = padre_a["cromosoma"]
		hijo = mutar_cromosoma(hijo, rng, config["probabilidad_mutacion_por_gen"])
		individuo = _evaluar_individuo(
			hijo, config["limite_expansiones"], contador, primeras,
			incidencias, acumulados, casos, semilla
		)
		evaluados.add(individuo["cromosoma"])
		poblacion = sorted(
			poblacion + [individuo],
			key=lambda miembro: (miembro["aptitud"], miembro["cromosoma"]),
			reverse=True,
		)[:poblacion_tamano]
		hijos_generacion += 1
		if hijos_generacion == poblacion_tamano or contador["evaluaciones"] == presupuesto:
			generacion += 1
			progreso.append(
				_resumen_generacion(generacion, contador, poblacion, primeras, acumulados)
			)
			hijos_generacion = 0

	mejor = poblacion[0]
	return {
		"metodo": "genetico",
		"semilla": semilla,
		"configuracion": config,
		"presupuesto": presupuesto,
		"evaluaciones": contador["evaluaciones"],
		"grafos_distintos": len(evaluados),
		"grafos_distintos_claves": sorted("".join(map(str, cromosoma)) for cromosoma in evaluados),
		"primer_hallazgo": primeras,
		"primeros_casos": casos,
		"incidencias": incidencias,
		"hallazgos_acumulados": dict(acumulados),
		"mejor": {
			"cromosoma": list(mejor["cromosoma"]),
			"grafo": mejor["grafo"],
			"aptitud": list(mejor["aptitud"]),
			"clasificacion": mejor["clasificacion"],
		},
		"progreso": progreso,
		"tiempo_segundos": time.perf_counter() - inicio_tiempo,
	}


def _resumen_generacion(generacion, contador, poblacion, primeras, acumulados):
	return {
		"generacion": generacion,
		"evaluaciones": contador["evaluaciones"],
		"mejor_aptitud": list(poblacion[0]["aptitud"]),
		"primer_hallazgo": dict(primeras),
		"hallazgos_acumulados": dict(acumulados),
	}
