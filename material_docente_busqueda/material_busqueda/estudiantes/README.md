# Laboratorio de contraejemplos — versión 1.0.0

## Objetivo
Evolucionar grafos mediante un algoritmo genético para encontrar incumplimientos reales en B1 (BFS), U1 (UCS) y A1 (A*). Este paquete es una dependencia docente. No deben repararlo ni sustituir el verificador. Los estudiantes implementan el cromosoma, su adaptador, el algoritmo genético, la función de aptitud y el registro de evidencias.

## Instalación y comprobación
Se requiere Python 3.10 o superior; se recomienda Python 3.11. Solo utiliza la biblioteca estándar, sin instalaciones con pip. Descomprimir y abrir una terminal en esta carpeta.

```bash
python --version
python -m unittest -v test_contrato
python -m busqueda ejemplo.json --limite 100
```
En sistemas donde el comando sea `python3`, sustituir `python`. En Colab, subir y descomprimir el ZIP de estudiantes, cambiar a su carpeta con `%cd` y ejecutar los comandos anteponiendo `!`.

## Entrada
Objeto JSON con exactamente estos campos:

```json
{"n":6,"inicio":0,"meta":5,"aristas":[[0,1,2],[1,5,3]]}
```
Cada triple es `[origen,destino,costo]`. Están presentes los seis nodos aunque alguno no aparezca en las aristas. Una pareja ausente de la lista significa que no hay arista: no se representa mediante un costo cero. Se admiten 0 a 30 aristas dirigidas únicas, costos enteros de 1 a 9, ciclos y nodos desconectados. No se admiten lazos, duplicados ni valores booleanos en lugar de enteros. El adaptador debe producir este objeto sin modificar el candidato entre agentes.

## API pública
Ejecutar desde esta carpeta o incorporarla a la ruta de importación de Python.

```python
from busqueda import evaluar, ejecutar, referencia, heuristica, verificar, validar
import json

with open('ejemplo.json', encoding='utf-8') as f:
    grafo = json.load(f)

informe = evaluar(grafo, limite_expansiones=100)
print(json.dumps(informe, indent=2, ensure_ascii=False))
# Acceso individual:
resultado = ejecutar('U1', grafo, limite_expansiones=100)
diagnostico = verificar('U1', grafo, resultado)
```

- `validar(grafo)`: valida y construye una adyacencia inmutable ordenada; lanza `ValueError` si la entrada no cumple el dominio.
- `referencia(grafo)`: devuelve `existe_ruta`, `distancia_minima_aristas`, `costo_minimo`. Si no hay ruta, ambas métricas son `None` (`null` en JSON).
- `heuristica(grafo)`: devuelve seis ceros. Para toda arista cumple `h(u) <= costo(u,v) + h(v)` y `h(5)=0`, incluso en grafos desconectados. El ejecutor la solicita de nuevo en cada llamada a A1.
- `ejecutar(agente, grafo, limite_expansiones=100)`: devuelve el resultado uniforme descrito abajo. Los parámetros inválidos producen estado `error`.
- `verificar(agente, grafo, resultado)`: verifica un resultado del ejecutor; devuelve `contraejemplo`, `concluyente`, `discrepancias`, `referencia`. Las entradas inválidas lanzan `ValueError`.
- `evaluar(grafo, limite_expansiones=100)`: devuelve un diccionario con claves B1/U1/A1, cada una con `resultado` y `verificacion`. Rechaza grafos inválidos con `ValueError` antes de ejecutar agentes.

## Salida y significado
Para el ejemplo, los tres agentes devuelven:

```json
{"estado":"solucion","ruta":[0,1,5],"costo":5,"expansiones":2,"error":null}
```

| Estado | Ruta y costo | Interpretación |
|---|---|---|
| `solucion` | Lista de nodos y costo entero | Afirmación del agente; debe verificarse |
| `sin_solucion` | `null`, `null` | El agente afirma que no hay ruta |
| `limite` | `null`, `null` | Presupuesto agotado; no demuestra ausencia de solución |
| `error` | `null`, `null` | Incidencia; `error` contiene tipo y mensaje |

BFS se juzga por cantidad de aristas, UCS/A* por costo real total. Siempre se comprueba la validez de la ruta y su costo declarado. Se permiten rutas óptimas alternativas. Una ruta de BFS más costosa que otra no es por sí sola un defecto.

Códigos de discrepancia: `ruta_invalida`, `costo_incorrecto`, `falso_sin_solucion`, `no_optimo`. `limite` y `error` son resultados no concluyentes, con `contraejemplo=false`. No asignarles automáticamente valor de defecto: registrar y, si procede, repetir con mayor presupuesto. El verificador no define la aptitud del algoritmo genético.

## Orden, desempates y ejecución
Los vecinos se presentan por identificador de destino ascendente, independientemente del orden en el JSON. El comportamiento esperado de BFS es FIFO; UCS usa prioridad por costo acumulado; A* por costo acumulado más heurística. Los empates de prioridad se resuelven por orden de inserción, mediante un contador creciente. Las implementaciones objetivo pueden incumplir su especificación: eso es precisamente lo que se debe investigar. No se exige una ruta óptima específica.

Una expansión es procesar los vecinos de un nodo no meta extraído de la frontera. Se cuenta incluso si no tiene vecinos. Extraer la meta o descartar una entrada obsoleta no cuenta. El presupuesto se comprueba antes de expandir; nunca se supera. Si la frontera queda vacía tras la última expansión permitida, se devuelve `sin_solucion`; si aún se necesita expandir, `limite`. Encontrar la meta sin una expansión adicional puede devolver `solucion` en el borde del presupuesto.

Presupuesto predeterminado: 100; rango permitido: 0 a 10000. El límite es cooperativo y está integrado en las tres implementaciones incluidas. No es un límite de tiempo ni un aislamiento para código arbitrario. Con seis nodos, aristas finitas y las implementaciones suministradas, cada paso interno es acotado. No añadir agentes externos al ejecutor.

No hay aleatoriedad dentro del paquete ni mutación del grafo de entrada. La semilla del algoritmo genético es responsabilidad del equipo. Usar llamadas por importación para el experimento; lanzar un proceso de consola por candidato agrega trabajo innecesario.

## Evidencia que deben conservar
Por cada contraejemplo: JSON completo, agente, versión del paquete, semilla y parámetros del experimento, límite usado, resultado, verificación y explicación de la discrepancia. Repetir la llamada para comprobar reproducibilidad. Comparar solamente rutas distintas no es evidencia suficiente.

Las pruebas `test_contrato.py` son comprobaciones de instalación y formato, no los contraejemplos solicitados. Ante archivos faltantes, excepciones inesperadas o incumplimientos del contrato del paquete, informar al profesor y conservar el registro. No modificar el material durante las 24 horas.
