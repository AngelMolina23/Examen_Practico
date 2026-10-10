"""Ejecutar desde la raíz del paquete: python docente/validar_docente.py"""
import sys
from pathlib import Path
import random
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'estudiantes'))
from busqueda import evaluar, referencia, verificar, heuristica, ejecutar

def g(edges): return dict(n=6,inicio=0,meta=5,aristas=edges)
CASOS = {
    'B1': g([[0,1,1],[1,5,1],[0,2,1],[2,3,1],[3,5,1]]),
    'U1': g([[0,5,9],[0,1,1],[1,5,1]]),
    'A1': g([[0,1,9],[0,2,1],[2,1,1],[1,5,1]])
}

def oraculo_enumeracion(graph):
    adj = [[] for _ in range(6)]
    for u,v,w in graph['aristas']: adj[u].append((v,w))
    rutas = []
    def visitar(u, vistos, costo):
        if u == 5:
            rutas.append((len(vistos)-1,costo))
            return
        for v,w in adj[u]:
            if v not in vistos: visitar(v,vistos+[v],costo+w)
    visitar(0,[0],0)
    return dict(existe_ruta=bool(rutas), distancia_minima_aristas=min((x[0] for x in rutas),default=None), costo_minimo=min((x[1] for x in rutas),default=None))

class Docente(unittest.TestCase):
    def test_defectos(self):
        for a,graph in CASOS.items():
            self.assertIn('no_optimo',evaluar(graph)[a]['verificacion']['discrepancias'])
    def test_referencia_independiente(self):
        rng = random.Random(20261009)
        for _ in range(1000):
            graph = g([[u,v,rng.randint(1,9)] for u in range(6) for v in range(6) if u != v and rng.random() < .3])
            self.assertEqual(referencia(graph),oraculo_enumeracion(graph))
            for a,item in evaluar(graph).items():
                self.assertIn(item['resultado']['estado'],('solucion','sin_solucion'))
                self.assertLessEqual(item['resultado']['expansiones'],100)
    def test_evidencias(self):
        graph=g([[0,1,9],[1,5,9],[0,2,1],[2,5,1]])
        r=dict(estado='solucion',ruta=[0,1,5],costo=18)
        self.assertFalse(verificar('B1',graph,r)['contraejemplo'])
        self.assertTrue(verificar('U1',graph,r)['contraejemplo'])
        r=dict(estado='solucion',ruta=[0,2,5],costo=2)
        self.assertFalse(verificar('B1',graph,r)['contraejemplo'])
        r['costo']=3
        self.assertIn('costo_incorrecto',verificar('U1',graph,r)['discrepancias'])
        r['ruta']=[0,4,5]
        self.assertIn('ruta_invalida',verificar('U1',graph,r)['discrepancias'])
        self.assertIn('falso_sin_solucion',verificar('U1',graph,dict(estado='sin_solucion'))['discrepancias'])
        for estado in ('limite','error'):
            self.assertFalse(verificar('U1',graph,dict(estado=estado))['concluyente'])

if __name__ == '__main__': unittest.main()
