# Guía reservada al docente

**No distribuir esta carpeta ni el ZIP maestro a los estudiantes.** Entregar solamente `paquete_estudiantes.zip` que se encuentra en la raíz. El material no incluye un algoritmo genético, cromosoma ni función de aptitud resueltos.

## Defectos deliberados

| Agente | Defecto | Contraejemplo dirigido (u,v,costo) | Resultado incorrecto | Óptimo exigido |
|---|---|---|---|---|
| B1 | Usa extracción LIFO en lugar de FIFO | (0,1,1), (1,5,1), (0,2,1), (2,3,1), (3,5,1) | Ruta 0-2-3-5: 3 aristas | 0-1-5: 2 aristas |
| U1 | Devuelve la meta al generarla, antes de extraerla con prioridad mínima | (0,5,9), (0,1,1), (1,5,1) | Ruta 0-5: costo 9 | 0-1-5: costo 2 |
| A1 | No permite mejorar nodos ya descubiertos | (0,1,9), (0,2,1), (2,1,1), (1,5,1) | Ruta 0-1-5: costo 10 | 0-2-1-5: costo 3 |

Los tres contienen un defecto alcanzable. Los alumnos pueden descubrir otros grafos que activen el mismo defecto; los casos no tienen que ser exclusivos de un agente. La heurística nula permite aislar el error de implementación y evita inconsistencias introducidas por el proveedor. A* correcto con h=0 coincide en objetivo con UCS correcto; A1 y U1 pueden diferir por sus defectos.

## Validación antes de abrir el examen
Desde la raíz del paquete maestro descomprimido:

```bash
python docente/validar_docente.py
cd estudiantes
python -m unittest -v test_contrato
python -m busqueda ejemplo.json
```

La validación docente verifica los tres contraejemplos, falsos positivos y compara el evaluador de referencia (Floyd-Warshall) contra enumeración independiente de rutas simples en 1000 grafos con semilla fija. Con costos positivos, un camino óptimo puede elegirse simple, por lo que esta enumeración es válida. La validación no constituye una prueba exhaustiva de todos los grafos posibles.

## Decisiones pedagógicas
El código fuente se entrega como dependencia de Python legible. Esto permite inspección, aunque los equipos deben aportar evidencia obtenida y reproducida mediante su búsqueda genética. Si el examen exige caja negra estricta, hará falta ofrecer un servicio controlado por el docente; ocultar un archivo Python no impide su inspección. Este paquete no implementa ese servicio.

Se recomienda fijar 100 expansiones para todos los equipos. En estos agentes y este dominio alcanza para completar las ejecuciones normales. Los presupuestos menores permiten comprobar el contrato de límite pero no deben convertirse en una fuente artificial de puntos de aptitud.

El paquete detecta rutas inválidas y costos mal declarados además de los errores de optimalidad intencionales. No se ha insertado necesariamente un defecto por cada categoría del verificador. Los errores y límites son incidencias no concluyentes, no contraejemplos automáticos.

La referencia es pública: los equipos pueden consultar las métricas, pero diseñan cómo traducirlas a aptitud, selección, cruza, mutación y diversidad. El paquete deliberadamente no proporciona esas decisiones ni la representación genética.

Para preservar trazabilidad, conservar el ZIP original y su archivo SHA256SUMS.txt. Las pruebas docentes no se incluyen en el ZIP de estudiantes.
