import unittest
from copy import deepcopy
from busqueda import ejecutar, evaluar, referencia, heuristica, validar


def grafo(aristas):
    return dict(n=6, inicio=0, meta=5, aristas=aristas)

class Contrato(unittest.TestCase):
    def test_cadena(self):
        g = grafo([[0,1,2],[1,5,3]])
        copia = deepcopy(g)
        for datos in evaluar(g).values():
            r = datos['resultado']
            self.assertEqual(r, dict(estado='solucion', ruta=[0,1,5], costo=5, expansiones=2, error=None))
            self.assertFalse(datos['verificacion']['contraejemplo'])
        self.assertEqual(g, copia)
        self.assertEqual(referencia(g), dict(existe_ruta=True, distancia_minima_aristas=2, costo_minimo=5))
    def test_sin_ruta_y_ciclo(self):
        for g in (grafo([]), grafo([[0,1,1],[1,0,1]])):
            for a in ('B1','U1','A1'):
                self.assertEqual(ejecutar(a,g)['estado'], 'sin_solucion')
            self.assertIsNone(referencia(g)['costo_minimo'])
    def test_limite(self):
        for a in ('B1','U1','A1'):
            r = ejecutar(a,grafo([[0,5,1]]),0)
            self.assertEqual((r['estado'],r['expansiones']), ('limite',0))
    def test_heuristica(self):
        g = grafo([[0,1,2],[1,5,3],[2,0,1]])
        h = heuristica(g)
        self.assertEqual(h[5],0)
        for u,v,w in g['aristas']:
            self.assertLessEqual(h[u],w+h[v])
    def test_entradas_invalidas(self):
        for edges in ([[0,0,1]], [[0,1,0]], [[0,1,10]], [[0,1,1],[0,1,2]], [[True,1,2]], [[0,6,1]]):
            with self.assertRaises(ValueError): validar(grafo(edges))
            self.assertEqual(ejecutar('B1',grafo(edges))['estado'],'error')
        self.assertEqual(ejecutar('X',grafo([]))['estado'],'error')
    def test_determinismo(self):
        g = grafo([[1,5,2],[0,1,1]])
        self.assertEqual(evaluar(g), evaluar(grafo(list(reversed(g['aristas'])))))

if __name__ == '__main__': unittest.main()
