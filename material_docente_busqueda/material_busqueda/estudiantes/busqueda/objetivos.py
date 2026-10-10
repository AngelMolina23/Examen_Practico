"""Implementaciones objetivo: conservar sin modificaciones durante el examen."""
from collections import deque
from heapq import heappush, heappop
from itertools import count


def buscar(agente, adj, h, presupuesto):
    if agente == 'B1':
        pendientes = deque([([0], 0)])
        vistos = {0}
        while pendientes:
            ruta, costo = pendientes.pop()
            u = ruta[-1]
            if u == 5:
                return ruta, costo
            presupuesto.expandir()
            for v, w in adj[u]:
                if v not in vistos:
                    vistos.add(v)
                    pendientes.append((ruta + [v], costo + w))
        return None, None
    serial = count()
    pendientes = [(h[0], next(serial), 0, [0])]
    mejor = {0: 0}
    descubiertos = {0}
    while pendientes:
        _, _, costo, ruta = heappop(pendientes)
        u = ruta[-1]
        if costo != mejor[u]:
            continue
        if u == 5:
            return ruta, costo
        presupuesto.expandir()
        for v, w in adj[u]:
            nuevo = costo + w
            if agente == 'U1' and v == 5:
                return ruta + [v], nuevo
            if agente == 'A1' and v in descubiertos:
                continue
            if nuevo < mejor.get(v, float('inf')):
                mejor[v] = nuevo
                descubiertos.add(v)
                heappush(pendientes, (nuevo + h[v], next(serial), nuevo, ruta + [v]))
    return None, None
