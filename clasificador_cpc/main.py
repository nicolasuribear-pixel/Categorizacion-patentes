#!/usr/bin/env python
"""
Clasificador de Patentes por Códigos CPC/IPC
Ejecutable principal. Ejecutar desde la carpeta clasificador_cpc.

Uso:
  python main.py --help
  python main.py categorias
  python main.py analizar
  python main.py csv datos/patentes.csv
"""
import sys
import os

_raiz = os.path.dirname(os.path.abspath(__file__))
if _raiz not in sys.path:
    sys.path.insert(0, _raiz)

from classification.main_classifier import main

if __name__ == "__main__":
    main()
