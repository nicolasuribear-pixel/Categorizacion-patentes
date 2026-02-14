#!/usr/bin/env python
"""
Análisis de Patentes por RFSL (Requirements, Functions, Structures, Locations)
Ejecutable principal. Ejecutar desde la carpeta analisis_rfsl.

Menú para: crear estructura, descargar patentes, extraer RFSL, construir PKG,
análisis de similitud y clustering K-Means.
"""
import sys
import os

_raiz = os.path.dirname(os.path.abspath(__file__))
if _raiz not in sys.path:
    sys.path.insert(0, _raiz)


def menu():
    print("\n" + "=" * 60)
    print("  ANÁLISIS DE PATENTES POR RFSL")
    print("=" * 60)
    print("  1. Crear estructura de carpetas")
    print("  2. Descargar patentes (Google Patents)")
    print("  3. Extraer entidades RFSL")
    print("  4. Construir grafo PKG")
    print("  5. Análisis de similitud entre patentes")
    print("  6. Clustering K-Means")
    print("  0. Salir")
    print("=" * 60)
    return input("Seleccione opción (0-6): ").strip()


def run_estructura():
    from scripts.Estructura import crear_estructura_carpetas, crear_plantilla_patent
    crear_estructura_carpetas()
    crear_plantilla_patent()
    print("✓ Estructura creada.\n")


def run_descargar():
    from scripts.Google import run_descarga
    run_descarga(delay=3)


def run_rfsl():
    from knowledge_graph.rfsl_extractor import procesar_todas_las_patentes
    procesar_todas_las_patentes()


def run_pkg():
    from knowledge_graph.pkg_builder import build_pkg_from_all_patents
    build_pkg_from_all_patents()


def run_similitud():
    from knowledge_graph.similarity_analyzer import analyze_patent_similarity
    analyze_patent_similarity()


def run_kmeans():
    from knowledge_graph.kmeans_classifier import main as kmeans_main
    kmeans_main()


def main():
    while True:
        op = menu()
        if op == "0":
            print("Hasta luego.")
            break
        if op == "1":
            run_estructura()
        elif op == "2":
            run_descargar()
        elif op == "3":
            run_rfsl()
        elif op == "4":
            run_pkg()
        elif op == "5":
            run_similitud()
        elif op == "6":
            run_kmeans()
        else:
            print("Opción no válida.\n")


if __name__ == "__main__":
    main()
