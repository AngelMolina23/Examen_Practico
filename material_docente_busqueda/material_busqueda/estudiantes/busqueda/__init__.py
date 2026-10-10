"""Paquete docente 1.0.0. API pública determinista."""
from collections import deque
from heapq import heappush, heappop
from itertools import count

VERSION = '1.0.0'

def validar(g):
    if not isinstance(g, dict) or set(g) != {'n', 'inicio', 'meta', 'aristas'}:
        raise ValueError('Se requieren exactamente n, inicio, meta y aristas')
    if any(type(g[k]) is not int for k in ('n', 'inicio', 'meta')) or (g['n'], g['inicio'], g['meta']) != (6, 0, 5):
        raise ValueError('Dominio obligatorio: n=6, inicio=0, meta=5')
    if not isinstance(g['aristas'], (list, tuple)):
        raise ValueError('aristas debe ser una lista')
    adj = [[] for _ in range(6)]
    vistos = set()
    for e in g['aristas']:
        if not isinstance(e, (list, tuple)) or len(e) != 3 or any(type(x) is not int for x in e):
            raise ValueError('Arista esperada: [origen, destino, costo], enteros')
        u, v, w = e
        if not (0 <= u < 6 and 0 <= v < 6 and u != v and 1 <= w <= 9) or (u, v) in vistos:
            raise ValueError('Arista fuera del dominio o duplicada')
        vistos.add((u, v))
        adj[u].append((v, w))
    return tuple(tuple(sorted(row)) for row in adj)

def heuristica(g):
    validar(g)
    return (0, 0, 0, 0, 0, 0)

def referencia(g):
    adj = validar(g)
    # Floyd-Warshall: independiente de las implementaciones objetivo.
    d = [[float('inf')] * 6 for _ in range(6)]
    c = [[float('inf')] * 6 for _ in range(6)]
    for u in range(6):
        d[u][u] = c[u][u] = 0
        for v, w in adj[u]:
            d[u][v], c[u][v] = 1, w
    for k in range(6):
        for u in range(6):
            for v in range(6):
                d[u][v] = min(d[u][v], d[u][k] + d[k][v])
                c[u][v] = min(c[u][v], c[u][k] + c[k][v])
    existe = d[0][5] != float('inf')
    return dict(existe_ruta=existe, distancia_minima_aristas=d[0][5] if existe else None,
                costo_minimo=c[0][5] if existe else None)

def _salida(estado, expansiones, ruta=None, costo=None, error=None):
    return dict(estado=estado, ruta=ruta, costo=costo, expansiones=expansiones, error=error)

class _Limite(Exception):
    pass

class _Presupuesto:
    def __init__(self, limite):
        self.limite, self.n = limite, 0
    def expandir(self):
        if self.n >= self.limite:
            raise _Limite()
        self.n += 1

def ejecutar(agente, g, limite_expansiones=100):
    """Ejecuta exclusivamente B1/U1/A1; no es un sandbox para código externo."""
    p = _Presupuesto(0)
    try:
        if type(limite_expansiones) is not int or not 0 <= limite_expansiones <= 10000:
            raise ValueError('limite_expansiones debe ser entero entre 0 y 10000')
        p = _Presupuesto(limite_expansiones)
        adj = validar(g)
        if agente not in ('B1', 'U1', 'A1'):
            raise ValueError('Agente desconocido')
        h = heuristica(g) if agente == 'A1' else (0,) * 6
        from .objetivos import buscar
        ruta, costo = buscar(agente, adj, h, p)
        return _salida('solucion' if ruta is not None else 'sin_solucion', p.n, ruta, costo)
    except _Limite:
        return _salida('limite', p.n)
    except Exception as exc:
        return _salida('error', p.n, error=f'{type(exc).__name__}: {exc}')

def verificar(agente, g, resultado):
    """Valora evidencia, no diferencias entre agentes. No asigna fitness."""
    if agente not in ('B1', 'U1', 'A1'):
        raise ValueError('Agente desconocido')
    adj, ref = validar(g), referencia(g)
    fallos = []
    estado = resultado.get('estado')
    if estado in ('limite', 'error'):
        return dict(contraejemplo=False, concluyente=False, discrepancias=[], referencia=ref)
    if estado == 'sin_solucion':
        if ref['existe_ruta']:
            fallos.append('falso_sin_solucion')
    elif estado == 'solucion':
        ruta = resultado.get('ruta')
        valida = (isinstance(ruta, list) and len(ruta) >= 2 and
                  all(type(u) is int and 0 <= u < 6 for u in ruta) and ruta[0] == 0 and ruta[-1] == 5)
        pesos = {(u, v): w for u in range(6) for v, w in adj[u]}
        if valida:
            valida = all((u, v) in pesos for u, v in zip(ruta, ruta[1:]))
        if not valida:
            fallos.append('ruta_invalida')
        else:
            real = sum(pesos[u, v] for u, v in zip(ruta, ruta[1:]))
            if type(resultado.get('costo')) is not int or resultado['costo'] != real:
                fallos.append('costo_incorrecto')
            optimo = ref['distancia_minima_aristas'] if agente == 'B1' else ref['costo_minimo']
            observado = len(ruta) - 1 if agente == 'B1' else real
            if observado != optimo:
                fallos.append('no_optimo')
    else:
        raise ValueError('Estado de resultado desconocido')
    return dict(contraejemplo=bool(fallos), concluyente=True, discrepancias=fallos, referencia=ref)

def evaluar(g, limite_expansiones=100):
    validar(g)
    salida = {}
    for agente in ('B1', 'U1', 'A1'):
        r = ejecutar(agente, g, limite_expansiones)
        salida[agente] = dict(resultado=r, verificacion=verificar(agente, g, r))
    return salida
