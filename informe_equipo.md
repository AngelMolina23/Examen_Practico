# Informe del proyecto: búsqueda genética de contraejemplos
# Contribuciones y recursos
# Contribuciones del equipo

Angel Yael Molina Diaz: Implementación de la representación del cromosoma y validadores (utilidades.py), diseño de los operadores de cruce y mutación, desarrollo del motor del algoritmo genético (genetico.py) y creación de las pruebas unitarias para asegurar el cumplimiento del dominio (test_propios.py).

Sebastián Villarreal Morán: Desarrollo del adaptador al evaluador docente y clasificación de resultados (oraculo.py), definición de la función de aptitud lexicográfica, integración del sistema de captura de incidencias (límites y errores) y diseño de la estructura del diccionario de reportes.

Manuel Alberto Manzano Calixto: Programación de la línea base aleatoria estricta (aleatorio.py), desarrollo del orquestador CLI para la ejecución automatizada de semillas (experimentos.py), y automatización de la exportación de métricas (CSV) y extracción de contraejemplos (JSON).

# Revisión cruzada

Todos los integrantes participaron de manera conjunta en la integración de los módulos, la revisión cruzada de los contraejemplos (verificando manualmente que las discrepancias matemáticas fueran reales y no falsos positivos) y la discusión conceptual para la redacción 
de este informe.

## Planteamiento y representación

El objetivo fue generar grafos dirigidos de seis nodos que permitan observar incumplimientos de B1 (BFS), U1 (UCS) o A1 (A*). La evolución no busca una ruta desde el nodo inicial hasta la meta: busca una entrada, es decir, un grafo que provoque una diferencia verificable entre el comportamiento de un agente y la especificación. Cada agente sí realiza búsqueda de rutas dentro del grafo que recibe. Son, por tanto, dos espacios de búsqueda distintos: el algoritmo genético explora grafos candidatos y cada agente explora estados y caminos de un grafo fijo.

El cromosoma contiene 30 posiciones, una por cada par ordenado de nodos distintos. Un cero indica que la arista no existe y un entero de 1 a 9 indica su costo. El orden fijo permite convertir sin ambigüedad entre cromosoma y el formato del paquete docente, que requiere `n=6`, inicio 0, meta 5 y triples `[origen, destino, costo]`. La conversión rechaza longitud o valores fuera de dominio, lazos y duplicados; los grafos sin camino a la meta siguen siendo candidatos válidos. Así se evita confundir una entrada válida insoluble con un cromosoma mal formado.

## Evaluación y algoritmo genético

El adaptador usa la API pública del paquete docente 1.0.0 y envía cada grafo a B1, U1 y A1 con límite de 100 expansiones. La referencia del paquete calcula si existe ruta, la menor cantidad de aristas y el costo mínimo. La verificación semántica comprueba ruta, aristas y costo declarado; para BFS contrasta cantidad de aristas y para UCS/A* contrasta el costo real. Por eso una ruta alternativa de igual calidad es aceptada. Los estados `limite` y `error` se registran aparte y no se consideran contraejemplos.

La aptitud es lexicográfica: primero maximiza cuántos objetivos distintos presentan una discrepancia confirmada; a igualdad, maximiza el total de discrepancias verificadas y, finalmente, favorece menos aristas. El tiempo no participa en la aptitud. Los candidatos con límites o errores no obtienen crédito como fallos. Esta prioridad centra la evolución en evidencia real y usa simplicidad solo como desempate.

La población inicial contiene 30 grafos. Para cada posible arista se decide su presencia independientemente con probabilidad 0.2; cuando existe, su costo se elige uniformemente entre 1 y 9. La selección es torneo de tamaño tres y depende de la aptitud. Cada posición del hijo se hereda al azar de uno de los dos progenitores; el cruce se intenta con probabilidad 0.8. Cada gen muta con probabilidad 0.04, cambiando entre ausencia y otro costo válido. El reemplazo conserva los 30 mejores de padres e hijos, por lo que incluye elitismo. Los empates se ordenan de forma determinista por cromosoma. No se filtran duplicados: cada vez que se vuelve a evaluar un candidato consume presupuesto. Python `random.Random(semilla)` controla la aleatoriedad del método.

La línea base genera candidatos independientes con la misma distribución y semilla, y usa el mismo adaptador y clasificación, pero no selecciona ni reproduce individuos. Su progreso se registra cada 30 evaluaciones, intervalo equivalente al tamaño de la población genética. Para cada ejecución se guardan configuración, semilla, consumo, progreso, objetivos detectados, incidencias, tiempo y grafos distintos.

## Resultados

La comparación principal ejecutó cinco semillas (11, 22, 33, 44 y 55) con 1000 evaluaciones por método y semilla. Por tanto, se hicieron 5000 evaluaciones genéticas y 5000 aleatorias. La población inicial contó en el presupuesto y los candidatos repetidos también. Las comprobaciones posteriores de los casos guardados se hicieron fuera de ese presupuesto. No se observaron estados de límite ni errores en las 10 000 evaluaciones reportadas.

| Método | B1: hallazgos / sin hallazgo; mediana entre éxitos | U1: hallazgos / sin hallazgo; mediana entre éxitos | A1: hallazgos / sin hallazgo; mediana entre éxitos | Grafos distintos entre semillas |
|---|---|---|---|---:|
| Genético | 2/5; 3; 89 evaluaciones | 2/5; 3; 20.5 evaluaciones | 2/5; 3; 20.5 evaluaciones | 3004 |
| Aleatorio | 5/5; 0; 204 evaluaciones | 5/5; 0; 53 evaluaciones | 5/5; 0; 53 evaluaciones | 4995 |

Las medianas se calcularon únicamente sobre las ejecuciones que encontraron cada objetivo; las ejecuciones sin hallazgo aparecen por separado. En esta configuración y presupuesto, la línea base aleatoria encontró más discrepancias. Esto no demuestra que la búsqueda aleatoria sea siempre mejor: el resultado describe estas cinco semillas, este dominio y estos parámetros. El tiempo medido para las cinco corridas fue 4.08 segundos para el GA y 3.07 para la línea base en el equipo usado. Es un dato complementario dependiente del equipo, no evidencia de corrección ni de calidad por sí mismo.

## Contraejemplos y límites

Se conservaron tres grafos distintos y se verificaron fuera del ciclo. En el caso BFS, semilla 11, evaluación 83, la referencia encuentra una ruta con tres aristas, mientras B1 devuelve una ruta de cuatro aristas; para BFS, esa longitud incumple el criterio aun cuando el camino devuelto use aristas válidas. En el caso UCS, semilla 44, evaluación 19, el agente devuelve una ruta válida de costo 18 cuando el mínimo es 12. En A*, semilla 22, evaluación 22, devuelve costo 21 frente al mínimo 13; se registra explícitamente la heurística de seis ceros empleada por el paquete. Las repeticiones fuera del ciclo confirmaron las discrepancias. Los casos no se afirman mínimos globales; solo son ejemplos reproducibles hallados por los experimentos.

La ausencia de hallazgos del GA en tres semillas por objetivo muestra un límite práctico: una población finita, operadores estocásticos y un presupuesto fijo no garantizan descubrir cada defecto. La aptitud también guía únicamente con base en fallos ya confirmados; no ofrece crédito gradual a grafos “cercanos” a un fallo. La línea base cubrió más grafos distintos en estas ejecuciones. Sería posible explorar otras distribuciones o parámetros en trabajos opcionales, pero no se mezclan con la comparación principal.

## Interpretación conceptual

El método es evolutivo porque representa candidatos, evalúa aptitud, selecciona progenitores, recombina y muta, y reemplaza parte de la población. Una búsqueda lógica podría verificar consecuencias mediante reglas; un enfoque probabilístico modelaría incertidumbre y actualizaría creencias; uno de aprendizaje ajustaría un modelo a ejemplos. Aquí no se implementan esos paradigmas: los resultados dependen del evaluador determinista y del muestreo evolutivo.

La propuesta de McCarthy y sus colegas para el proyecto de Dartmouth planteó estudiar si aspectos del aprendizaje y la inteligencia podían describirse con precisión para simularlos en máquinas. Encontrar entradas que expongan fallos de búsqueda demuestra capacidad de prueba y optimización bajo una métrica, pero no demuestra por sí solo comprensión. Turing propuso valorar la inteligencia mediante el comportamiento conversacional observable; Searle objetó que manipular símbolos conforme a reglas no implica necesariamente comprensión semántica. Este experimento no resuelve ese debate: mide incumplimientos concretos en agentes y no atribuye entendimiento a la herramienta.

## Contribuciones y recursos

Completar esta sección con los nombres reales, aportaciones verificables, archivos o registros correspondientes y revisión cruzada efectuada por cada integrante. No se atribuyen tareas por defecto.

El paquete docente de estudiantes 1.0.0 es dependencia externa y se mantuvo sin modificaciones. La implementación del cromosoma, operadores, algoritmo genético, línea base, adaptador y registro experimental corresponde al equipo.

## Referencias

- Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems*. University of Michigan Press.
- McCarthy, J., Minsky, M. L., Rochester, N. y Shannon, C. E. (1955). *A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence*.
- Russell, S. y Norvig, P. (2021). *Artificial Intelligence: A Modern Approach*, 4.ª ed. Pearson.
- Searle, J. R. (1980). “Minds, Brains, and Programs”. *Behavioral and Brain Sciences*, 3(3), 417–457.
- Turing, A. M. (1950). “Computing Machinery and Intelligence”. *Mind*, 59(236), 433–460.
- Paquete docente de búsqueda, versión 1.0.0: `material_docente_busqueda/material_busqueda/estudiantes/README.md`.
