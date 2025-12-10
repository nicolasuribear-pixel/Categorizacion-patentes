# batch_classifier.py
"""
Clasificador por Lotes de Patentes
Procesa múltiples patentes, las categoriza y las agrupa por características
"""

import json
import os
import csv
import time
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict

from cpc_taxonomy import (
    CPC_TAXONOMY, CATEGORY_ICONS, CATEGORY_COLORS,
    get_all_categories
)
from patent_categorizer import PatentCategorizer


class BatchPatentClassifier:
    """
    Clasificador por lotes de patentes
    Procesa listas de patentes y genera análisis agregados
    """
    
    def __init__(self, output_dir="data/results/batch"):
        """
        Inicializa el clasificador por lotes
        
        Args:
            output_dir: directorio para guardar resultados
        """
        self.categorizer = PatentCategorizer()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.results = []
        self.feature_matrix = None
        self.patent_ids = []
    
    # ═══════════════════════════════════════════════════════════════
    # CARGA DE DATOS
    # ═══════════════════════════════════════════════════════════════
    
    def load_patents_from_list(self, patent_ids):
        """
        Carga patentes desde una lista de IDs
        
        Args:
            patent_ids: lista de IDs de patentes
        """
        self.patent_ids = patent_ids
        return len(patent_ids)
    
    def load_patents_from_csv(self, csv_file, column="patent_id"):
        """
        Carga patentes desde un archivo CSV
        
        Args:
            csv_file: ruta al archivo CSV
            column: nombre de la columna con IDs de patentes
        
        Returns:
            número de patentes cargadas
        """
        patent_ids = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if column in row:
                    patent_ids.append(row[column].strip())
        
        self.patent_ids = patent_ids
        return len(patent_ids)
    
    def load_patents_from_json(self, json_file):
        """
        Carga patentes desde un archivo JSON
        
        Args:
            json_file: ruta al archivo JSON (lista de IDs o lista de objetos)
        
        Returns:
            número de patentes cargadas
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            if all(isinstance(item, str) for item in data):
                # Lista simple de IDs
                self.patent_ids = data
            else:
                # Lista de objetos con campo patent_id
                self.patent_ids = [
                    item.get("patent_id", item.get("id", ""))
                    for item in data
                    if item.get("patent_id") or item.get("id")
                ]
        elif isinstance(data, dict):
            # Diccionario con lista de patentes
            self.patent_ids = data.get("patents", data.get("patent_ids", []))
        
        return len(self.patent_ids)
    
    # ═══════════════════════════════════════════════════════════════
    # PROCESAMIENTO
    # ═══════════════════════════════════════════════════════════════
    
    def process_all(self, delay=1.0, verbose=True):
        """
        Procesa todas las patentes cargadas
        
        Args:
            delay: segundos entre cada descarga (para evitar bloqueos)
            verbose: mostrar progreso
        
        Returns:
            lista de resultados
        """
        if not self.patent_ids:
            print("❌ No hay patentes cargadas")
            return []
        
        total = len(self.patent_ids)
        
        if verbose:
            print("\n" + "="*60)
            print("🚀 PROCESAMIENTO POR LOTES")
            print("="*60)
            print(f"   Patentes a procesar: {total}")
            print(f"   Delay entre descargas: {delay}s")
            print("="*60 + "\n")
        
        self.results = []
        successful = 0
        failed = 0
        
        for idx, patent_id in enumerate(self.patent_ids, 1):
            if verbose:
                print(f"[{idx}/{total}] Procesando {patent_id}...", end=" ")
            
            try:
                result = self.categorizer.analyze_patent(patent_id, verbose=False)
                
                if result:
                    self.results.append(result)
                    successful += 1
                    
                    if verbose:
                        cat = result["categorization"]
                        main_cat = cat.get("categoria_principal_nombre", "N/A")
                        matched = cat["total_codigos_matched"]
                        print(f"✓ {main_cat} ({matched} códigos)")
                else:
                    failed += 1
                    if verbose:
                        print("❌ Error")
                        
            except Exception as e:
                failed += 1
                if verbose:
                    print(f"❌ Error: {str(e)[:50]}")
            
            # Delay entre descargas
            if idx < total and delay > 0:
                time.sleep(delay)
        
        if verbose:
            print("\n" + "="*60)
            print("📊 RESUMEN DE PROCESAMIENTO")
            print("="*60)
            print(f"   ✅ Exitosas: {successful}")
            print(f"   ❌ Fallidas: {failed}")
            print(f"   📊 Total: {total}")
        
        return self.results
    
    # ═══════════════════════════════════════════════════════════════
    # ANÁLISIS Y AGRUPACIÓN
    # ═══════════════════════════════════════════════════════════════
    
    def build_feature_matrix(self):
        """
        Construye matriz de características para clustering
        
        Returns:
            numpy array con características
        """
        if not self.results:
            print("❌ No hay resultados procesados")
            return None
        
        features = []
        patent_ids = []
        
        for result in self.results:
            vector = self.categorizer.generate_feature_vector(result)
            
            # Convertir a lista ordenada
            feature_list = [
                vector.get(cat_id, 0.0)
                for cat_id in CPC_TAXONOMY.keys()
            ]
            
            # Añadir métricas adicionales
            feature_list.extend([
                vector.get("total_codes", 0),
                vector.get("matched_codes", 0),
                vector.get("match_ratio", 0)
            ])
            
            features.append(feature_list)
            patent_ids.append(result["patent_id"])
        
        self.feature_matrix = np.array(features)
        self.processed_patent_ids = patent_ids
        
        return self.feature_matrix
    
    def group_by_category(self):
        """
        Agrupa patentes por categoría principal
        
        Returns:
            dict con patentes agrupadas
        """
        if not self.results:
            print("❌ No hay resultados procesados")
            return {}
        
        groups = defaultdict(list)
        
        for result in self.results:
            cat = result["categorization"]
            main_cat = cat.get("categoria_principal", "sin_categoria")
            
            groups[main_cat].append({
                "patent_id": result["patent_id"],
                "title": result["patent_data"]["title"],
                "score": cat["categorias"].get(main_cat, {}).get("score", 0),
                "all_categories": list(cat["categorias"].keys())
            })
        
        # Ordenar cada grupo por score
        for cat_id in groups:
            groups[cat_id].sort(key=lambda x: x["score"], reverse=True)
        
        return dict(groups)
    
    def get_category_statistics(self):
        """
        Calcula estadísticas por categoría
        
        Returns:
            dict con estadísticas
        """
        if not self.results:
            return {}
        
        stats = {}
        
        for cat_id, cat_info in CPC_TAXONOMY.items():
            scores = []
            count = 0
            
            for result in self.results:
                cat_data = result["categorization"]["categorias"].get(cat_id)
                if cat_data:
                    scores.append(cat_data["score"])
                    count += 1
            
            stats[cat_id] = {
                "nombre": cat_info["nombre"],
                "icon": CATEGORY_ICONS.get(cat_id, "📁"),
                "patentes": count,
                "porcentaje": (count / len(self.results)) * 100 if self.results else 0,
                "score_promedio": np.mean(scores) if scores else 0,
                "score_max": max(scores) if scores else 0,
                "score_min": min(scores) if scores else 0
            }
        
        # Ordenar por número de patentes
        stats = dict(sorted(
            stats.items(),
            key=lambda x: x[1]["patentes"],
            reverse=True
        ))
        
        return stats
    
    def find_similar_patents(self, patent_id, top_n=5):
        """
        Encuentra patentes similares a una dada
        
        Args:
            patent_id: ID de la patente de referencia
            top_n: número de patentes similares a retornar
        
        Returns:
            lista de patentes similares con scores
        """
        if self.feature_matrix is None:
            self.build_feature_matrix()
        
        if patent_id not in self.processed_patent_ids:
            print(f"❌ Patente {patent_id} no encontrada en resultados")
            return []
        
        idx = self.processed_patent_ids.index(patent_id)
        reference_vector = self.feature_matrix[idx]
        
        similarities = []
        
        for i, other_id in enumerate(self.processed_patent_ids):
            if i == idx:
                continue
            
            other_vector = self.feature_matrix[i]
            
            # Similitud coseno
            dot_product = np.dot(reference_vector, other_vector)
            norm1 = np.linalg.norm(reference_vector)
            norm2 = np.linalg.norm(other_vector)
            
            if norm1 > 0 and norm2 > 0:
                similarity = dot_product / (norm1 * norm2)
            else:
                similarity = 0
            
            similarities.append({
                "patent_id": other_id,
                "similarity": similarity
            })
        
        # Ordenar por similitud
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similarities[:top_n]
    
    # ═══════════════════════════════════════════════════════════════
    # REPORTES Y EXPORTACIÓN
    # ═══════════════════════════════════════════════════════════════
    
    def print_summary_report(self):
        """Imprime un reporte resumen del análisis"""
        if not self.results:
            print("❌ No hay resultados para reportar")
            return
        
        print("\n" + "="*70)
        print("📊 REPORTE RESUMEN DE CLASIFICACIÓN POR LOTES")
        print("="*70)
        
        print(f"\n📄 Total patentes procesadas: {len(self.results)}")
        
        # Estadísticas por categoría
        stats = self.get_category_statistics()
        
        print("\n🏷️  DISTRIBUCIÓN POR CATEGORÍAS:")
        print("-"*70)
        
        for cat_id, cat_stats in stats.items():
            if cat_stats["patentes"] > 0:
                icon = cat_stats["icon"]
                nombre = cat_stats["nombre"]
                count = cat_stats["patentes"]
                pct = cat_stats["porcentaje"]
                avg_score = cat_stats["score_promedio"]
                
                bar_length = int(pct / 5)
                bar = '█' * bar_length + '░' * (20 - bar_length)
                
                print(f"\n   {icon} {nombre}")
                print(f"      Patentes: {count} [{bar}] {pct:.1f}%")
                print(f"      Score promedio: {avg_score:.2f}")
        
        # Grupos por categoría principal
        groups = self.group_by_category()
        
        print("\n\n📂 PATENTES POR CATEGORÍA PRINCIPAL:")
        print("-"*70)
        
        for cat_id, patents in groups.items():
            cat_name = CPC_TAXONOMY.get(cat_id, {}).get("nombre", cat_id)
            icon = CATEGORY_ICONS.get(cat_id, "📁")
            
            print(f"\n{icon} {cat_name} ({len(patents)} patentes)")
            
            for p in patents[:5]:
                print(f"   • {p['patent_id']}: {p['title'][:50]}...")
            
            if len(patents) > 5:
                print(f"   ... y {len(patents) - 5} más")
        
        print("\n" + "="*70)
    
    def export_to_csv(self, filename=None):
        """
        Exporta resultados a CSV
        
        Args:
            filename: nombre del archivo (default: timestamp)
        
        Returns:
            ruta al archivo creado
        """
        if not self.results:
            print("❌ No hay resultados para exportar")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"patent_classification_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        rows = []
        
        for result in self.results:
            patent = result["patent_data"]
            cat = result["categorization"]
            
            row = {
                "patent_id": result["patent_id"],
                "title": patent["title"],
                "assignee": patent.get("assignee", ""),
                "publication_date": patent.get("publication_date", ""),
                "categoria_principal": cat.get("categoria_principal_nombre", ""),
                "total_codigos": cat["total_codigos_input"],
                "codigos_matched": cat["total_codigos_matched"],
                "match_ratio": cat["total_codigos_matched"] / cat["total_codigos_input"] if cat["total_codigos_input"] > 0 else 0
            }
            
            # Añadir scores por categoría
            for cat_id in CPC_TAXONOMY.keys():
                cat_data = cat["categorias"].get(cat_id)
                row[f"score_{cat_id}"] = cat_data["score"] if cat_data else 0
            
            rows.append(row)
        
        # Escribir CSV
        if rows:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"💾 Exportado a CSV: {filepath}")
        return filepath
    
    def export_to_json(self, filename=None):
        """
        Exporta resultados completos a JSON
        
        Args:
            filename: nombre del archivo
        
        Returns:
            ruta al archivo creado
        """
        if not self.results:
            print("❌ No hay resultados para exportar")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"patent_classification_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        export_data = {
            "metadata": {
                "total_patents": len(self.results),
                "analysis_date": datetime.now().isoformat(),
                "categories_used": list(CPC_TAXONOMY.keys())
            },
            "statistics": self.get_category_statistics(),
            "groups": self.group_by_category(),
            "patents": []
        }
        
        for result in self.results:
            chars = self.categorizer.get_patent_characteristics(result)
            chars["all_codes"] = result["categorization"].get("all_codes", [])
            export_data["patents"].append(chars)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Exportado a JSON: {filepath}")
        return filepath
    
    def save_feature_matrix(self, filename="feature_matrix.npz"):
        """
        Guarda la matriz de características para uso posterior
        
        Args:
            filename: nombre del archivo
        
        Returns:
            ruta al archivo creado
        """
        if self.feature_matrix is None:
            self.build_feature_matrix()
        
        filepath = os.path.join(self.output_dir, filename)
        
        np.savez(
            filepath,
            features=self.feature_matrix,
            patent_ids=self.processed_patent_ids,
            category_names=list(CPC_TAXONOMY.keys())
        )
        
        print(f"💾 Matriz guardada: {filepath}")
        return filepath


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE CONVENIENCIA
# ═══════════════════════════════════════════════════════════════

def classify_patent_list(patent_ids, output_name=None, delay=1.0):
    """
    Función de conveniencia para clasificar una lista de patentes
    
    Args:
        patent_ids: lista de IDs de patentes
        output_name: nombre base para archivos de salida
        delay: delay entre descargas
    
    Returns:
        BatchPatentClassifier con resultados
    """
    classifier = BatchPatentClassifier()
    classifier.load_patents_from_list(patent_ids)
    classifier.process_all(delay=delay, verbose=True)
    classifier.print_summary_report()
    
    if output_name:
        classifier.export_to_csv(f"{output_name}.csv")
        classifier.export_to_json(f"{output_name}.json")
    
    return classifier


def classify_csv_file(csv_file, column="patent_id", output_name=None, delay=1.0):
    """
    Función de conveniencia para clasificar patentes desde CSV
    
    Args:
        csv_file: ruta al archivo CSV
        column: columna con IDs
        output_name: nombre base para archivos de salida
        delay: delay entre descargas
    
    Returns:
        BatchPatentClassifier con resultados
    """
    classifier = BatchPatentClassifier()
    count = classifier.load_patents_from_csv(csv_file, column)
    print(f"📄 Cargadas {count} patentes desde {csv_file}")
    
    classifier.process_all(delay=delay, verbose=True)
    classifier.print_summary_report()
    
    if output_name:
        classifier.export_to_csv(f"{output_name}.csv")
        classifier.export_to_json(f"{output_name}.json")
    
    return classifier


# ═══════════════════════════════════════════════════════════════
# MAIN - TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔬 BATCH PATENT CLASSIFIER - TEST")
    print("="*70)
    
    # Lista de patentes de prueba
    test_patents = [
        "US8550777B2",
        "US8936435B2",
        "US8834130B2",
        "US7927078B2",
        "US7927070B2",
    ]
    
    print(f"\n📋 Patentes de prueba: {len(test_patents)}")
    
    # Clasificar
    classifier = classify_patent_list(
        test_patents,
        output_name="test_classification",
        delay=1.5
    )
    
    # Mostrar patentes similares
    if classifier.results:
        print("\n" + "="*70)
        print("🔍 ANÁLISIS DE SIMILITUD")
        print("="*70)
        
        reference = test_patents[0]
        print(f"\nPatentes similares a {reference}:")
        
        similar = classifier.find_similar_patents(reference, top_n=3)
        for s in similar:
            print(f"   • {s['patent_id']}: {s['similarity']:.4f}")
    
    print("\n✅ Test completado!")
