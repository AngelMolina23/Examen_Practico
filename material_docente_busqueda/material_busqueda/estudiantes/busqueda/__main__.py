import argparse
import json
from . import evaluar

parser = argparse.ArgumentParser(description='Evalúa un grafo con B1, U1 y A1')
parser.add_argument('archivo', help='Grafo JSON UTF-8')
parser.add_argument('--limite', type=int, default=100)
args = parser.parse_args()
try:
    with open(args.archivo, encoding='utf-8') as f:
        g = json.load(f)
    print(json.dumps(evaluar(g, args.limite), indent=2, ensure_ascii=False))
except (ValueError, OSError) as exc:
    parser.exit(2, f'Entrada rechazada: {exc}\n')
