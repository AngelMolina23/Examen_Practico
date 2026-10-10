"""CLI para ejecuciones individuales, comparacion y reproduccion."""

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from aleatorio import ejecutar_aleatorio
from genetico import CONFIGURACION, ejecutar_genetico
from oraculo import VERSION, evaluar_grafo
from utilidades import grafo_a_cromosoma


RAIZ = Path(__file__).resolve().parents[1]
CARPETA_RESULTADOS = RAIZ / "resultados"
CARPETA_CASOS = RAIZ / "contraejemplos"
SEMILLAS_PRINCIPALES = (11, 22, 33, 44, 55)
AGENTES = ("B1", "U1", "A1")


def _escribir_json(ruta: Path, contenido):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(contenido, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _resumen_metodo(corridas):
    resumen = {}
    for agente in AGENTES:
        evaluaciones_exito = [
            corrida["primer_hallazgo"][agente]
            for corrida in corridas
            if agente in corrida["primer_hallazgo"]
        ]
        resumen[agente] = {
            "ejecuciones_con_hallazgo": len(evaluaciones_exito),
            "ejecuciones_sin_hallazgo": len(corridas) - len(evaluaciones_exito),
            "mediana_evaluaciones_hasta_hallazgo": (
                statistics.median(evaluaciones_exito) if evaluaciones_exito else None
            ),
        }
    claves_unicas = {
        clave
        for corrida in corridas
        for clave in corrida["grafos_distintos_claves"]
    }
    return {
        "objetivos": resumen,
        "grafos_distintos_entre_semillas": len(claves_unicas),
        "incidencias_limite": sum(corrida["incidencias"]["limite"] for corrida in corridas),
        "incidencias_error": sum(corrida["incidencias"]["error"] for corrida in corridas),
        "tiempo_total_segundos": sum(corrida["tiempo_segundos"] for corrida in corridas),
    }


def _guardar_progreso(corridas, ruta, metodo):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(
            ["metodo", "semilla", "generacion", "evaluaciones", "mejor_aptitud",
             "primer_hallazgo", "hallazgos_acumulados"]
        )
        for corrida in corridas:
            for punto in corrida["progreso"]:
                escritor.writerow(
                    [
                        metodo,
                        corrida["semilla"],
                        punto.get("generacion", ""),
                        punto["evaluaciones"],
                        json.dumps(punto["mejor_aptitud"], separators=(",", ":")),
                        json.dumps(punto["primer_hallazgo"], separators=(",", ":")),
                        json.dumps(punto["hallazgos_acumulados"], separators=(",", ":")),
                    ]
                )


def _guardar_casos(corridas, limite_expansiones):
    nombres = {"B1": "caso_bfs_falla.json", "U1": "caso_ucs_falla.json", "A1": "caso_astar_falla.json"}
    grafos_guardados = set()
    for agente in AGENTES:
        candidatos = [
            corrida["primeros_casos"][agente]
            for corrida in corridas
            if agente in corrida["primeros_casos"]
        ]
        candidatos.sort(key=lambda caso: (caso["evaluacion"], caso["semilla"], caso["metodo"]))
        caso = next(
            (
                candidato
                for candidato in candidatos
                if json.dumps(candidato["grafo"], sort_keys=True) not in grafos_guardados
            ),
            None,
        )
        if caso is None:
            continue
        grafos_guardados.add(json.dumps(caso["grafo"], sort_keys=True))
        grafo_a_cromosoma(caso["grafo"])
        reproduccion = evaluar_grafo(caso["grafo"], limite_expansiones)
        caso_entrega = dict(caso)
        caso_entrega["version_paquete"] = VERSION
        caso_entrega["limite_expansiones"] = limite_expansiones
        caso_entrega["reproduccion_fuera_del_ciclo"] = reproduccion
        explicaciones = {
            "ruta_invalida": "La ruta no respeta el inicio, la meta o las aristas existentes.",
            "costo_incorrecto": "El costo declarado por el agente no coincide con la suma de las aristas recorridas.",
            "falso_sin_solucion": "El agente afirma que no existe ruta aunque la referencia encuentra una.",
            "no_optimo": (
                "El agente devuelve una ruta válida, pero no alcanza la cantidad minima de aristas "
                "(BFS) o el costo minimo (UCS/A*) de la referencia."
            ),
        }
        caso_entrega["incumplimiento"] = "; ".join(
            explicaciones[codigo] for codigo in caso["discrepancias"]
        )
        _escribir_json(CARPETA_CASOS / nombres[agente], caso_entrega)

    indice = ["# Indice de contraejemplos", ""]
    encontrados = [agente for agente in AGENTES if any(agente in c["primeros_casos"] for c in corridas)]
    if encontrados:
        etiquetas = {"B1": "BFS", "U1": "UCS", "A1": "A*"}
        indice.extend(f"- {etiquetas[a]}: `{nombres[a]}`" for a in encontrados)
        indice.extend(["", "Cada caso incluye la repeticion fuera del ciclo evolutivo."])
    else:
        indice.extend(["No se encontraron discrepancias semanticas confirmadas en estas ejecuciones.",
                       "Los archivos de resultados contienen los registros que sustentan esta conclusion."])
    (CARPETA_CASOS / "indice_casos.md").write_text("\n".join(indice) + "\n", encoding="utf-8")


def ejecutar_comparacion(presupuesto=1000):
    config = dict(CONFIGURACION)
    geneticos = [
        ejecutar_genetico(semilla, presupuesto=presupuesto, configuracion=config)
        for semilla in SEMILLAS_PRINCIPALES
    ]
    aleatorios = [
        ejecutar_aleatorio(
            semilla,
            presupuesto=presupuesto,
            intervalo_registro=config["poblacion"],
            limite_expansiones=config["limite_expansiones"],
            probabilidad_arista=config["probabilidad_arista_inicial"],
        )
        for semilla in SEMILLAS_PRINCIPALES
    ]
    resumen = {
        "presupuesto_por_metodo_y_semilla": presupuesto,
        "semillas": list(SEMILLAS_PRINCIPALES),
        "version_paquete": VERSION,
        "genetico": _resumen_metodo(geneticos),
        "aleatorio": _resumen_metodo(aleatorios),
    }
    _escribir_json(
        CARPETA_RESULTADOS / "parametros.json",
        {
            "version_python_requerida": ">=3.10",
            "version_paquete_docente": VERSION,
            "semillas": list(SEMILLAS_PRINCIPALES),
            "presupuesto_por_ejecucion": presupuesto,
            "configuracion_genetica": config,
            "distribucion_inicial_compartida": {
                "probabilidad_de_arista": config["probabilidad_arista_inicial"],
                "costo_uniforme": [1, 9],
            },
        },
    )
    _escribir_json(CARPETA_RESULTADOS / "resumen_comparacion.json", resumen)
    _escribir_json(
        CARPETA_RESULTADOS / "ejecuciones_principales.json",
        {"genetico": geneticos, "aleatorio": aleatorios},
    )
    _guardar_progreso(geneticos, CARPETA_RESULTADOS / "progreso_semillas_GA.csv", "genetico")
    _guardar_progreso(
        aleatorios,
        CARPETA_RESULTADOS / "progreso_semillas_aleatorio.csv",
        "aleatorio",
    )
    _guardar_casos(geneticos + aleatorios, config["limite_expansiones"])
    return resumen


def main():
    parser = argparse.ArgumentParser(description="Ejecucion del cazador genetico de grafos")
    subcomandos = parser.add_subparsers(dest="comando", required=True)
    comparar = subcomandos.add_parser("comparar", help="Ejecuta las diez corridas principales")
    comparar.add_argument("--presupuesto", type=int, default=1000)
    for nombre in ("genetico", "aleatorio"):
        individual = subcomandos.add_parser(nombre, help=f"Ejecuta una corrida {nombre}")
        individual.add_argument("--semilla", type=int, required=True)
        individual.add_argument("--presupuesto", type=int, default=1000)
    reproducir = subcomandos.add_parser("reproducir", help="Reevalua un caso JSON guardado")
    reproducir.add_argument("archivo")
    reproducir.add_argument("--limite", type=int, default=100)
    args = parser.parse_args()

    if args.comando == "comparar":
        resultado = ejecutar_comparacion(args.presupuesto)
    elif args.comando == "genetico":
        resultado = ejecutar_genetico(args.semilla, args.presupuesto)
    elif args.comando == "aleatorio":
        resultado = ejecutar_aleatorio(args.semilla, args.presupuesto)
    else:
        datos = json.loads(Path(args.archivo).read_text(encoding="utf-8"))
        resultado = evaluar_grafo(datos["grafo"], args.limite)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()