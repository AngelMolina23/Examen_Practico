"""Representacion, validacion y operadores para grafos de seis nodos."""

import random
from collections.abc import Sequence


N_NODOS = 6
INICIO = 0
META = 5
COSTO_MAXIMO = 9
PROBABILIDAD_ARISTA_INICIAL = 0.2
PARES_DIRIGIDOS = tuple(
	(origen, destino)
	for origen in range(N_NODOS)
	for destino in range(N_NODOS)
	if origen != destino
)
TAMANO_CROMOSOMA = len(PARES_DIRIGIDOS)


def validar_cromosoma(cromosoma: Sequence[int]) -> tuple[int, ...]:
	if not isinstance(cromosoma, (tuple, list)):
		raise ValueError("El cromosoma debe ser una tupla o lista")
	if len(cromosoma) != TAMANO_CROMOSOMA:
		raise ValueError(f"El cromosoma debe contener {TAMANO_CROMOSOMA} genes")
	if any(type(gen) is not int or not 0 <= gen <= COSTO_MAXIMO for gen in cromosoma):
		raise ValueError("Cada gen debe ser un entero entre 0 y 9")
	return tuple(cromosoma)


def cromosoma_a_grafo(cromosoma: Sequence[int]) -> dict:
	genes = validar_cromosoma(cromosoma)
	aristas = [
		[origen, destino, costo]
		for (origen, destino), costo in zip(PARES_DIRIGIDOS, genes)
		if costo > 0
	]
	return {"n": N_NODOS, "inicio": INICIO, "meta": META, "aristas": aristas}


def grafo_a_cromosoma(grafo: dict) -> tuple[int, ...]:
	if not isinstance(grafo, dict) or set(grafo) != {"n", "inicio", "meta", "aristas"}:
		raise ValueError("El grafo debe contener exactamente n, inicio, meta y aristas")
	if any(type(grafo[campo]) is not int for campo in ("n", "inicio", "meta")):
		raise ValueError("n, inicio y meta deben ser enteros")
	if (grafo["n"], grafo["inicio"], grafo["meta"]) != (N_NODOS, INICIO, META):
		raise ValueError("El dominio requiere n=6, inicio=0 y meta=5")
	if not isinstance(grafo["aristas"], (list, tuple)) or len(grafo["aristas"]) > TAMANO_CROMOSOMA:
		raise ValueError("aristas debe ser una lista de hasta 30 aristas")

	indices = {par: indice for indice, par in enumerate(PARES_DIRIGIDOS)}
	genes = [0] * TAMANO_CROMOSOMA
	for arista in grafo["aristas"]:
		if not isinstance(arista, (list, tuple)) or len(arista) != 3:
			raise ValueError("Cada arista debe ser [origen, destino, costo]")
		origen, destino, costo = arista
		if any(type(valor) is not int for valor in arista):
			raise ValueError("Los valores de las aristas deben ser enteros")
		if (origen, destino) not in indices or not 1 <= costo <= COSTO_MAXIMO:
			raise ValueError("Arista fuera del dominio o costo fuera de 1..9")
		indice = indices[origen, destino]
		if genes[indice] != 0:
			raise ValueError("No se permiten aristas duplicadas")
		genes[indice] = costo
	return tuple(genes)


def generar_cromosoma(
	rng: random.Random,
	probabilidad_arista: float = PROBABILIDAD_ARISTA_INICIAL,
) -> tuple[int, ...]:
	if not 0.0 <= probabilidad_arista <= 1.0:
		raise ValueError("La probabilidad de arista debe estar entre 0 y 1")
	return tuple(
		rng.randint(1, COSTO_MAXIMO) if rng.random() < probabilidad_arista else 0
		for _ in PARES_DIRIGIDOS
	)


def cruzar_cromosomas(
	primero: Sequence[int], segundo: Sequence[int], rng: random.Random
) -> tuple[int, ...]:
	genes_primero = validar_cromosoma(primero)
	genes_segundo = validar_cromosoma(segundo)
	return tuple(
		rng.choice((gen_a, gen_b))
		for gen_a, gen_b in zip(genes_primero, genes_segundo)
	)


def mutar_cromosoma(
	cromosoma: Sequence[int], rng: random.Random, probabilidad_mutacion: float = 0.04
) -> tuple[int, ...]:
	genes = validar_cromosoma(cromosoma)
	if not 0.0 <= probabilidad_mutacion <= 1.0:
		raise ValueError("La probabilidad de mutacion debe estar entre 0 y 1")
	mutados = []
	for gen in genes:
		if rng.random() >= probabilidad_mutacion:
			mutados.append(gen)
		else:
			opciones = (0,) + tuple(range(1, COSTO_MAXIMO + 1))
			opciones = tuple(opcion for opcion in opciones if opcion != gen)
			mutados.append(rng.choice(opciones))
	return tuple(mutados)
