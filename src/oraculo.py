"""Adaptador al evaluador docente y clasificacion semantica de candidatos."""

import sys
from pathlib import Path


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_PAQUETE = (
	RAIZ_PROYECTO
	/ "material_docente_busqueda"
	/ "material_busqueda"
	/ "estudiantes"
)
if str(RUTA_PAQUETE) not in sys.path:
	sys.path.insert(0, str(RUTA_PAQUETE))

try:
	from busqueda import VERSION, evaluar, heuristica
except ImportError as exc:
	raise ImportError(
		"No se encontro el paquete docente para estudiantes en "
		f"{RUTA_PAQUETE}. Conserva su estructura original."
	) from exc


AGENTES = ("B1", "U1", "A1")


def evaluar_grafo(grafo: dict, limite_expansiones: int = 100) -> dict:
	"""Devuelve los resultados comunes y su clasificacion, sin ocultar incidencias."""
	informe = evaluar(grafo, limite_expansiones=limite_expansiones)
	contraejemplos = {
		agente: datos["verificacion"]["discrepancias"]
		for agente, datos in informe.items()
		if datos["verificacion"]["contraejemplo"]
	}
	incidencias = {
		agente: datos["resultado"]
		for agente, datos in informe.items()
		if datos["resultado"]["estado"] in ("limite", "error")
	}
	return {
		"version_paquete": VERSION,
		"heuristica": list(heuristica(grafo)),
		"resultados": informe,
		"contraejemplos": contraejemplos,
		"incidencias": incidencias,
		"concluyentes": all(
			datos["verificacion"]["concluyente"] for datos in informe.values()
		),
	}


def aptitud(clasificacion: dict, grafo: dict) -> tuple[int, int, int]:
	"""Orden lexicografico: objetivos detectados, hallazgos, menos aristas."""
	hallazgos = clasificacion["contraejemplos"]
	objetivos_detectados = len(hallazgos)
	cantidad_hallazgos = sum(len(discrepancias) for discrepancias in hallazgos.values())
	cantidad_aristas = len(grafo["aristas"])
	return objetivos_detectados, cantidad_hallazgos, -cantidad_aristas
