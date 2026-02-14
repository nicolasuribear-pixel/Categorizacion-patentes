# main_classifier.py
"""
Sistema de Clasificación de Patentes de Palas Eólicas
Script principal con interfaz de línea de comandos
"""

import argparse
import sys
import os

from core.cpc_taxonomy import get_all_categories, CPC_TAXONOMY, CATEGORY_ICONS
from classification.patent_categorizer import PatentCategorizer, analyze_single_patent
from classification.batch_classifier import (
    BatchPatentClassifier,
    classify_patent_list,
    classify_csv_file
)


def print_banner():
    """Imprime banner del sistema"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🌬️  SISTEMA DE CLASIFICACIÓN DE PATENTES DE PALAS EÓLICAS  🌬️   ║
║                                                                   ║
║   Categorización automática basada en códigos CPC/IPC            ║
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


def analyze_patent_interactive():
    """Modo interactivo para analizar una patente"""
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DE PATENTE INDIVIDUAL")
    print("="*60)
    
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
            categorizer = PatentCategorizer()
            chars = categorizer.get_patent_characteristics(result)
            
            filename = f"data/results/{patent_id}_analysis.json"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chars, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Guardado en: {filename}")


def batch_analysis_interactive():
    """Modo interactivo para análisis por lotes"""
    print("\n" + "="*60)
    print("📊 ANÁLISIS POR LOTES")
    print("="*60)
    
    print("\nOpciones de entrada:")
    print("  1. Ingresar lista de IDs manualmente")
    print("  2. Cargar desde archivo CSV")
    print("  3. Cargar desde archivo JSON")
    print("  4. Usar lista de ejemplo")
    
    option = input("\nSeleccione opción (1-4): ").strip()
    
    classifier = BatchPatentClassifier()
    
    if option == "1":
        print("\nIngrese los IDs de patentes separados por coma:")
        ids_input = input("> ").strip()
        patent_ids = [pid.strip() for pid in ids_input.split(",") if pid.strip()]
        
        if not patent_ids:
            print("❌ No se ingresaron IDs válidos")
            return
        
        classifier.load_patents_from_list(patent_ids)
        
    elif option == "2":
        csv_path = input("\nRuta al archivo CSV: ").strip()
        if not os.path.exists(csv_path):
            print(f"❌ Archivo no encontrado: {csv_path}")
            return
        
        column = input("Nombre de columna con IDs (default: patent_id): ").strip()
        if not column:
            column = "patent_id"
        
        count = classifier.load_patents_from_csv(csv_path, column)
        print(f"✓ Cargadas {count} patentes")
        
    elif option == "3":
        json_path = input("\nRuta al archivo JSON: ").strip()
        if not os.path.exists(json_path):
            print(f"❌ Archivo no encontrado: {json_path}")
            return
        
        count = classifier.load_patents_from_json(json_path)
        print(f"✓ Cargadas {count} patentes")
        
    elif option == "4":
        # Lista de ejemplo
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


def quick_classify(patent_ids):
    """Clasificación rápida desde línea de comandos"""
    print_banner()
    
    if len(patent_ids) == 1:
        # Una sola patente
        analyze_single_patent(patent_ids[0])
    else:
        # Múltiples patentes
        classifier = classify_patent_list(
            patent_ids,
            output_name="quick_classification",
            delay=1.0
        )


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Sistema de Clasificación de Patentes de Palas Eólicas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main_classifier.py                      # Modo interactivo
  python main_classifier.py -p US8550777B2       # Analizar una patente
  python main_classifier.py -p US8550777B2 US8936435B2  # Múltiples patentes
  python main_classifier.py --csv patents.csv    # Desde archivo CSV
  python main_classifier.py --categories         # Ver categorías disponibles
        """
    )
    
    parser.add_argument(
        '-p', '--patents',
        nargs='+',
        help='ID(s) de patente(s) a analizar'
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
    
    # Modo interactivo
    if args.interactive:
        print("\n¿Qué desea hacer?")
        print("  1. Analizar una patente")
        print("  2. Análisis por lotes")
        print("  3. Ver categorías disponibles")
        print("  4. Salir")
        
        option = input("\nSeleccione opción (1-4): ").strip()
        
        if option == "1":
            analyze_patent_interactive()
        elif option == "2":
            batch_analysis_interactive()
        elif option == "3":
            show_categories()
        elif option == "4":
            print("\n👋 ¡Hasta luego!")
        else:
            print("❌ Opción no válida")
        
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
