# main_classifier.py
"""
Sistema de Clasificación de Patentes de Palas Eólicas
Clasificación basada en códigos CPC/IPC

Este script unifica:
- Descarga de patentes desde Google Patents
- Clasificación por códigos CPC/IPC
- Análisis por lotes
"""

import argparse
import sys
import os
import json

from cpc_taxonomy import get_all_categories, CPC_TAXONOMY, CATEGORY_ICONS
from patent_categorizer import PatentCategorizer, analyze_single_patent
from batch_classifier import (
    BatchPatentClassifier, 
    classify_patent_list, 
    classify_csv_file
)


# ═══════════════════════════════════════════════════════════════
# BANNER Y UI
# ═══════════════════════════════════════════════════════════════

def print_banner():
    """Imprime banner del sistema"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🌬️  SISTEMA DE CLASIFICACIÓN DE PATENTES DE PALAS EÓLICAS  🌬️   ║
║                                                                   ║
║   Clasificación basada en códigos CPC/IPC                         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_categories():
    """Muestra las categorías disponibles"""
    print("\n" + "="*60)
    print("📂 CATEGORÍAS DISPONIBLES PARA CLASIFICACIÓN")
    print("="*60)
    
    categories = get_all_categories()
    
    for cat in categories:
        icon = CATEGORY_ICONS.get(cat["id"], "📁")
        print(f"\n{icon} {cat['nombre']}")
        print(f"   ID: {cat['id']}")
        print(f"   Descripción: {cat['descripcion']}")
        print(f"   Códigos CPC: {cat['num_codigos']}")
    
    print("\n" + "="*60)
    print(f"Total categorías: {len(categories)}")
    total_codes = sum(cat['num_codigos'] for cat in categories)
    print(f"Total códigos CPC/IPC: {total_codes}")
    print("="*60)


def show_downloaded_patents():
    """Muestra las patentes ya descargadas"""
    categorizer = PatentCategorizer()
    patents = categorizer.list_downloaded_patents()
    
    print("\n" + "="*60)
    print("📂 PATENTES DESCARGADAS")
    print("="*60)
    print(f"   Directorio: {categorizer.patents_dir}")
    print(f"   Total: {len(patents)}")
    print("-"*60)
    
    if patents:
        for p in patents:
            # Cargar para mostrar título
            data = categorizer.load_patent_from_file(p)
            title = data.get("title", "Sin título")[:50] if data else "Error al cargar"
            print(f"   • {p}: {title}...")
    else:
        print("   No hay patentes descargadas aún.")
        print("   Usa la opción de descarga para agregar patentes.")
    
    print("="*60)
    return patents


# ═══════════════════════════════════════════════════════════════
# DESCARGA DE PATENTES
# ═══════════════════════════════════════════════════════════════

def download_patents_interactive():
    """Modo interactivo para descargar patentes"""
    print("\n" + "="*60)
    print("📥 DESCARGA DE PATENTES")
    print("="*60)
    
    print("\nOpciones de entrada:")
    print("  1. Ingresar lista de IDs manualmente")
    print("  2. Cargar desde archivo CSV")
    print("  3. Cargar desde archivo JSON")
    print("  4. Usar lista de ejemplo")
    
    option = input("\nSeleccione opción (1-4): ").strip()
    
    categorizer = PatentCategorizer()
    patent_ids = []
    
    if option == "1":
        print("\nIngrese los IDs de patentes separados por coma:")
        print("Ejemplo: US8550777B2, US8936435B2, US8834130B2")
        ids_input = input("> ").strip()
        patent_ids = [pid.strip() for pid in ids_input.split(",") if pid.strip()]
        
    elif option == "2":
        csv_path = input("\nRuta al archivo CSV: ").strip()
        if not os.path.exists(csv_path):
            print(f"❌ Archivo no encontrado: {csv_path}")
            return
        
        column = input("Nombre de columna con IDs (default: patent_id): ").strip()
        if not column:
            column = "patent_id"
        
        import csv
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if column in row:
                    patent_ids.append(row[column].strip())
        
    elif option == "3":
        json_path = input("\nRuta al archivo JSON: ").strip()
        if not os.path.exists(json_path):
            print(f"❌ Archivo no encontrado: {json_path}")
            return
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            patent_ids = [p if isinstance(p, str) else p.get("patent_id", "") for p in data]
        elif isinstance(data, dict):
            patent_ids = data.get("patents", data.get("patent_ids", []))
        
    elif option == "4":
        patent_ids = [
            "US8550777B2",
            "US8936435B2",
            "US8834130B2",
            "US8932024B2",
            "US7927078B2",
            "US10400744B2",
            "US9581133B2",
            "US7927070B2",
            "CN113982840A",
            "CN107110110B",
        ]
        print(f"✓ Usando lista de ejemplo: {len(patent_ids)} patentes")
    else:
        print("❌ Opción no válida")
        return
    
    if not patent_ids:
        print("❌ No se encontraron IDs de patentes")
        return
    
    # Configurar delay
    delay_input = input(f"\nDelay entre descargas en segundos (default: 1.5): ").strip()
    delay = float(delay_input) if delay_input else 1.5
    
    # Descargar
    print(f"\n🚀 Iniciando descarga de {len(patent_ids)} patentes...")
    results = categorizer.download_list(patent_ids, delay=delay)
    
    print("\n✅ Descarga completada!")
    print(f"   Patentes disponibles en: {categorizer.patents_dir}")


# ═══════════════════════════════════════════════════════════════
# ANÁLISIS DE PATENTES
# ═══════════════════════════════════════════════════════════════

def analyze_patent_interactive():
    """Modo interactivo para analizar una patente"""
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DE PATENTE INDIVIDUAL")
    print("="*60)
    
    categorizer = PatentCategorizer()
    
    # Mostrar patentes disponibles
    available = categorizer.list_downloaded_patents()
    if available:
        print(f"\n📂 Patentes disponibles ({len(available)}):")
        for p in available[:10]:
            print(f"   • {p}")
        if len(available) > 10:
            print(f"   ... y {len(available) - 10} más")
    
    patent_id = input("\nIngrese el ID de la patente (ej: US8550777B2): ").strip()
    
    if not patent_id:
        print("❌ ID de patente vacío")
        return
    
    print(f"\n🔄 Analizando {patent_id}...")
    
    result = analyze_single_patent(patent_id)
    
    if result:
        # Preguntar si guardar
        save = input("\n¿Desea guardar los resultados? (s/n): ").strip().lower()
        if save == 's':
            chars = categorizer.get_patent_characteristics(result)
            
            filename = f"data/results/{patent_id}_analysis.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chars, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Guardado en: {filename}")


def batch_analysis_interactive():
    """Modo interactivo para análisis por lotes"""
    print("\n" + "="*60)
    print("📊 ANÁLISIS POR LOTES")
    print("="*60)
    
    categorizer = PatentCategorizer()
    available = categorizer.list_downloaded_patents()
    
    print("\nOpciones de entrada:")
    print("  1. Analizar TODAS las patentes descargadas")
    print("  2. Ingresar lista de IDs manualmente")
    print("  3. Cargar desde archivo CSV")
    print("  4. Cargar desde archivo JSON")
    print("  5. Usar lista de ejemplo")
    
    option = input("\nSeleccione opción (1-5): ").strip()
    
    classifier = BatchPatentClassifier()
    
    if option == "1":
        if not available:
            print("❌ No hay patentes descargadas")
            print("   Use primero la opción de descarga")
            return
        classifier.load_patents_from_list(available)
        print(f"✓ Usando {len(available)} patentes descargadas")
        
    elif option == "2":
        print("\nIngrese los IDs de patentes separados por coma:")
        ids_input = input("> ").strip()
        patent_ids = [pid.strip() for pid in ids_input.split(",") if pid.strip()]
        
        if not patent_ids:
            print("❌ No se ingresaron IDs válidos")
            return
        
        classifier.load_patents_from_list(patent_ids)
        
    elif option == "3":
        csv_path = input("\nRuta al archivo CSV: ").strip()
        if not os.path.exists(csv_path):
            print(f"❌ Archivo no encontrado: {csv_path}")
            return
        
        column = input("Nombre de columna con IDs (default: patent_id): ").strip()
        if not column:
            column = "patent_id"
        
        count = classifier.load_patents_from_csv(csv_path, column)
        print(f"✓ Cargadas {count} patentes")
        
    elif option == "4":
        json_path = input("\nRuta al archivo JSON: ").strip()
        if not os.path.exists(json_path):
            print(f"❌ Archivo no encontrado: {json_path}")
            return
        
        count = classifier.load_patents_from_json(json_path)
        print(f"✓ Cargadas {count} patentes")
        
    elif option == "5":
        example_patents = [
            "US8550777B2",
            "US8936435B2",
            "US8834130B2",
            "US8932024B2",
            "US7927078B2",
        ]
        classifier.load_patents_from_list(example_patents)
        print(f"✓ Cargadas {len(example_patents)} patentes de ejemplo")
        
    else:
        print("❌ Opción no válida")
        return
    
    # Configurar delay
    delay_input = input("\nDelay entre descargas en segundos (default: 1.5): ").strip()
    delay = float(delay_input) if delay_input else 1.5
    
    # Procesar
    print(f"\n🚀 Iniciando procesamiento de {len(classifier.patent_ids)} patentes...")
    classifier.process_all(delay=delay, verbose=True)
    
    # Mostrar reporte
    classifier.print_summary_report()
    
    # Exportar
    export = input("\n¿Desea exportar los resultados? (s/n): ").strip().lower()
    if export == 's':
        name = input("Nombre base para archivos (sin extensión): ").strip()
        if not name:
            name = "clasificacion_patentes"
        
        classifier.export_to_csv(f"{name}.csv")
        classifier.export_to_json(f"{name}.json")
        classifier.save_feature_matrix(f"{name}_features.npz")


# ═══════════════════════════════════════════════════════════════
# CLASIFICACIÓN RÁPIDA (CLI)
# ═══════════════════════════════════════════════════════════════

def quick_classify(patent_ids):
    """Clasificación rápida desde línea de comandos"""
    print_banner()
    
    if len(patent_ids) == 1:
        analyze_single_patent(patent_ids[0])
    else:
        classifier = classify_patent_list(
            patent_ids,
            output_name="quick_classification",
            delay=1.0
        )


# ═══════════════════════════════════════════════════════════════
# MENÚ PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def interactive_menu():
    """Menú interactivo principal"""
    while True:
        print("\n" + "="*60)
        print("📋 MENÚ PRINCIPAL")
        print("="*60)
        print("\n  DESCARGA:")
        print("    1. Descargar patentes")
        print("    2. Ver patentes descargadas")
        
        print("\n  ANÁLISIS CPC/IPC:")
        print("    3. Analizar una patente")
        print("    4. Análisis por lotes")
        
        print("\n  INFORMACIÓN:")
        print("    5. Ver categorías CPC disponibles")
        print("    0. Salir")
        
        option = input("\nSeleccione opción (0-5): ").strip()
        
        if option == "1":
            download_patents_interactive()
        elif option == "2":
            show_downloaded_patents()
        elif option == "3":
            analyze_patent_interactive()
        elif option == "4":
            batch_analysis_interactive()
        elif option == "5":
            show_categories()
        elif option == "0":
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción no válida")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Sistema de Clasificación de Patentes de Palas Eólicas (CPC/IPC)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main_classifier.py                      # Modo interactivo
  python main_classifier.py -p US8550777B2       # Analizar una patente
  python main_classifier.py -p US8550777B2 US8936435B2  # Múltiples patentes
  python main_classifier.py --download US8550777B2      # Solo descargar
  python main_classifier.py --csv patents.csv           # Desde archivo CSV
  python main_classifier.py --categories                # Ver categorías disponibles
  python main_classifier.py --list                      # Ver patentes descargadas
        """
    )
    
    parser.add_argument(
        '-p', '--patents',
        nargs='+',
        help='ID(s) de patente(s) a analizar'
    )
    
    parser.add_argument(
        '--download',
        nargs='+',
        help='ID(s) de patente(s) a descargar (sin analizar)'
    )
    
    parser.add_argument(
        '--csv',
        type=str,
        help='Archivo CSV con lista de patentes'
    )
    
    parser.add_argument(
        '--json',
        type=str,
        help='Archivo JSON con lista de patentes'
    )
    
    parser.add_argument(
        '--column',
        type=str,
        default='patent_id',
        help='Nombre de columna en CSV (default: patent_id)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='Delay entre descargas en segundos (default: 1.5)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Nombre base para archivos de salida'
    )
    
    parser.add_argument(
        '--categories',
        action='store_true',
        help='Mostrar categorías disponibles'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Listar patentes descargadas'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Modo interactivo'
    )
    
    args = parser.parse_args()
    
    # Si no hay argumentos, modo interactivo
    if len(sys.argv) == 1:
        args.interactive = True
    
    print_banner()
    
    # Mostrar categorías
    if args.categories:
        show_categories()
        return
    
    # Listar patentes
    if args.list:
        show_downloaded_patents()
        return
    
    # Solo descargar
    if args.download:
        categorizer = PatentCategorizer()
        categorizer.download_list(args.download, delay=args.delay)
        return
    
    # Modo interactivo
    if args.interactive:
        interactive_menu()
        return
    
    # Análisis desde argumentos
    if args.patents:
        quick_classify(args.patents)
        
    elif args.csv:
        if not os.path.exists(args.csv):
            print(f"❌ Archivo no encontrado: {args.csv}")
            return
        
        output_name = args.output or os.path.splitext(os.path.basename(args.csv))[0]
        classify_csv_file(
            args.csv,
            column=args.column,
            output_name=output_name,
            delay=args.delay
        )
        
    elif args.json:
        if not os.path.exists(args.json):
            print(f"❌ Archivo no encontrado: {args.json}")
            return
        
        classifier = BatchPatentClassifier()
        classifier.load_patents_from_json(args.json)
        classifier.process_all(delay=args.delay, verbose=True)
        classifier.print_summary_report()
        
        if args.output:
            classifier.export_to_csv(f"{args.output}.csv")
            classifier.export_to_json(f"{args.output}.json")


if __name__ == "__main__":
    main()
