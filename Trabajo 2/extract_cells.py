import json, sys, os

path = os.path.join(os.path.dirname(__file__), "Proyecto_ML_Básico.ipynb")
nb = json.load(open(path, 'r', encoding='utf-8'))

for i, c in enumerate(nb['cells']):
    ct = c['cell_type']
    if ct == 'code':
        src = ''.join(c['source'])
        if 'fit' in src.lower() or 'grid' in src.lower() or 'cross_val' in src.lower() or 'kfold' in src.lower():
            print(f"=== Cell {i} (code) ===")
            print(src)
            print()
