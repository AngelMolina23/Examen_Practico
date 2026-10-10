# Cazador genético de contraejemplos

## Equipo

Integrantes: COMPLETAR con los cuatro nombres del equipo.

## Requisitos

- Python 3.10 o superior; se recomienda Python 3.11.
- Biblioteca estándar de Python. No requiere instalaciones con `pip`.
- Paquete docente para estudiantes 1.0.0, conservado en `material_docente_busqueda/material_busqueda/estudiantes/`.

No mover ni modificar los archivos del paquete docente. El adaptador de `src/oraculo.py` busca el paquete en esa ubicación relativa al proyecto.

## Estructura

- `src/utilidades.py`: cromosoma de 30 genes y conversiones/operadores.
- `src/oraculo.py`: adaptador al evaluador y aptitud basada en discrepancias confirmadas.
- `src/genetico.py`: algoritmo genético propio.
- `src/aleatorio.py`: línea base aleatoria independiente.
- `src/experimentos.py`: ejecución, comparación, registros y reproducción.
- `tests/test_propios.py`: pruebas del código del equipo.
- `resultados/`: parámetros, corridas completas y progreso CSV.
- `contraejemplos/`: casos reproducibles e índice.

Cada cromosoma representa las 30 aristas dirigidas posibles entre seis nodos sin lazos, en orden fijo. El valor `0` indica que la arista no existe; `1..9` representa su costo. El grafo exportado usa inicio 0, meta 5 y el formato JSON requerido por el paquete.

## Comandos

Ejecutar desde la raíz `Examen_Practico`:

```powershell
python --version
python -m unittest discover -s tests -v
python src/experimentos.py genetico --semilla 11 --presupuesto 1000
python src/experimentos.py aleatorio --semilla 11 --presupuesto 1000
python src/experimentos.py comparar
python src/experimentos.py reproducir contraejemplos/caso_bfs_falla.json
python src/experimentos.py reproducir contraejemplos/caso_ucs_falla.json
python src/experimentos.py reproducir contraejemplos/caso_astar_falla.json
```

La comparación principal usa las semillas 11, 22, 33, 44 y 55, con 1000 candidatos evaluados por método y semilla. La población inicial está incluida en ese conteo. Las comprobaciones de reproducción de contraejemplos se hacen aparte. Las ejecuciones individuales son de desarrollo si se lanzan adicionalmente; no deben mezclarse con la comparación principal.

La comparación escribe `resultados/parametros.json`, `resultados/ejecuciones_principales.json`, `resultados/resumen_comparacion.json` y los CSV de progreso. Los casos se guardan en `contraejemplos/`. Cada repetición cuenta como evaluación, aunque el grafo ya hubiese aparecido antes.

## Resultados medidos

En la comparación registrada, el GA encontró discrepancias en 2/5 ejecuciones para cada agente; la búsqueda aleatoria, en 5/5. Medianas de evaluaciones hasta el primer hallazgo, calculadas solo entre ejecuciones exitosas: GA, B1 89, U1 20.5 y A1 20.5; aleatorio, B1 204, U1 53 y A1 53. En todos los objetivos quedaron respectivamente 3/5 y 0/5 ejecuciones sin hallazgo. Se registraron cero límites y cero errores.

El tiempo total medido fue aproximadamente 4.08 s para las cinco corridas genéticas y 3.07 s para las cinco aleatorias, para 10 000 evaluaciones totales en el equipo usado al generar estos archivos. El tiempo depende del equipo y no se usa como medida de corrección. Consulta los JSON de resultados para los valores exactos y las claves de grafos distintos.

## Pendiente antes de entregar

Completar los nombres del equipo y verificar en el equipo propio la versión de Python y el tiempo de ejecución. Revisar las contribuciones y revisiones cruzadas en el informe; no se infieren automáticamente. Confirmar que los archivos de resultados entregados corresponden a la ejecución que el equipo desea reportar.
kdn