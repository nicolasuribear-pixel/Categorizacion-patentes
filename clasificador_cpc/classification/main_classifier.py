# main_classifier.py
"""
Sistema de Clasificación de Patentes de Palas Eólicas
Script principal con interfaz de línea de comandos
"""

import argparse
import sys
import os

from core.data_paths import data_dir
from core.data_paths import data_path
from core.cpc_taxonomy import get_all_categories, CPC_TAXONOMY, CATEGORY_ICONS
from classification.patent_categorizer import PatentCategorizer, analyze_single_patent
from classification.batch_classifier import (
    BatchPatentClassifier,
    classify_patent_list,
    classify_csv_file
)

_CPC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _apply_data_dir_config(mode: str | None = None, custom_path: str | None = None) -> None:
    """
    Configura la carpeta data para este proceso mediante PATENTES_DATA_DIR.
    - mode='shared': usa data general del repo (quita env var).
    - mode='local': usa clasificador_cpc/data
    - mode='custom': usa custom_path
    """
    if mode == "shared":
        os.environ.pop("PATENTES_DATA_DIR", None)
        return
    if mode == "local":
        os.environ["PATENTES_DATA_DIR"] = os.path.join(_CPC_ROOT, "data")
        return
    if mode == "custom" and custom_path:
        os.environ["PATENTES_DATA_DIR"] = os.path.abspath(custom_path)


def configure_data_dir_interactive() -> None:
    print("\n" + "=" * 60)
    print("  CONFIGURAR CARPETA DE DATOS (data/)")
    print("=" * 60)
    print(f"Carpeta de datos actual: {data_dir()}")
    print("\nOpciones:")
    print("  1. Usar data general del repo (recomendado)")
    print("  2. Usar data local de este subproyecto (clasificador_cpc/data)")
    print("  3. Usar una ruta personalizada")
    print("  0. Volver")
    opt = input("\nSeleccione opción (0-3): ").strip()

    if opt == "1":
        _apply_data_dir_config("shared")
        print(f"[OK] Usando data general: {data_dir()}")
    elif opt == "2":
        _apply_data_dir_config("local")
        print(f"[OK] Usando data local: {data_dir()}")
    elif opt == "3":
        path = input("Ruta a carpeta data (absoluta o relativa): ").strip()
        if path:
            _apply_data_dir_config("custom", path)
            print(f"[OK] Usando data personalizada: {data_dir()}")
    else:
        print("Volviendo al menú.\n")


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
            
            filename = data_path(f"results/{patent_id}_analysis.json")
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
    print("  5. Cargar IDs desde data general (data/raw/patents)")
    
    option = input("\nSeleccione opción (1-5): ").strip()
    
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

    elif option == "5":
        patents_dir = data_path("raw/patents")
        if not os.path.exists(patents_dir):
            print(f"❌ No existe la carpeta: {patents_dir}")
            return

        patent_ids = []
        for fname in os.listdir(patents_dir):
            # Solo patentes base; excluir derivados del flujo RFSL
            if not fname.endswith(".json") or fname.endswith("_rfsl.json"):
                continue
            patent_ids.append(os.path.splitext(fname)[0])

        if not patent_ids:
            print(f"❌ No se encontraron patentes JSON en: {patents_dir}")
            return

        patent_ids = sorted(set(patent_ids))
        classifier.load_patents_from_list(patent_ids)
        print(f"✓ Cargadas {len(patent_ids)} patentes desde data general")
        
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

    parser.add_argument(
        '--data-dir',
        type=str,
        default=None,
        help='Ruta a la carpeta data/ compartida (override). Si se omite, usa data general del repo.'
    )

    parser.add_argument(
        '--use-local-data',
        action='store_true',
        help='Usar clasificador_cpc/data en lugar de data/ general (solo para esta ejecución).'
    )
    
    args = parser.parse_args()

    # Aplicar config de data ANTES de ejecutar el flujo
    if args.data_dir:
        _apply_data_dir_config("custom", args.data_dir)
    elif args.use_local_data:
        _apply_data_dir_config("local")
    else:
        _apply_data_dir_config("shared")
    
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
        print("  4. Configurar carpeta de datos (data/)")
        print("  5. Salir")
        
        option = input("\nSeleccione opción (1-5): ").strip()
        
        if option == "1":
            analyze_patent_interactive()
        elif option == "2":
            batch_analysis_interactive()
        elif option == "3":
            show_categories()
        elif option == "4":
            configure_data_dir_interactive()
        elif option == "5":
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
