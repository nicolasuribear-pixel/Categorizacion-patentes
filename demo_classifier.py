# demo_classifier.py
"""
Demostración del Sistema de Clasificación de Patentes
Usa datos de ejemplo para mostrar todas las funcionalidades
"""

import json
import os
import numpy as np
from datetime import datetime

from cpc_taxonomy import (
    CPC_TAXONOMY, CATEGORY_ICONS, categorize_patent_codes,
    get_all_categories
)
from sample_patents import SAMPLE_PATENTS, get_all_sample_ids


class DemoPatentClassifier:
    """
    Clasificador de demostración usando datos de ejemplo
    """
    
    def __init__(self):
        self.patents = SAMPLE_PATENTS
        self.results = []
    
    def categorize_patent(self, patent_data):
        """Categoriza una patente basándose en sus códigos"""
        all_codes = []
        all_codes.extend(patent_data.get("ipc_codes", []))
        all_codes.extend(patent_data.get("cpc_codes", []))
        
        categorization = categorize_patent_codes(all_codes)
        
        categorization["patent_id"] = patent_data.get("patent_id", "")
        categorization["title"] = patent_data.get("title", "")
        categorization["all_codes"] = all_codes
        
        if categorization["categorias"]:
            main_category = list(categorization["categorias"].keys())[0]
            categorization["categoria_principal"] = main_category
            categorization["categoria_principal_nombre"] = categorization["categorias"][main_category]["nombre"]
        else:
            categorization["categoria_principal"] = None
            categorization["categoria_principal_nombre"] = "Sin categoría"
        
        return categorization
    
    def analyze_patent(self, patent_id):
        """Análisis completo de una patente"""
        if patent_id not in self.patents:
            print(f"❌ Patente {patent_id} no encontrada en datos de ejemplo")
            return None
        
        patent_data = self.patents[patent_id]
        categorization = self.categorize_patent(patent_data)
        
        return {
            "patent_id": patent_id,
            "patent_data": patent_data,
            "categorization": categorization
        }
    
    def process_all(self):
        """Procesa todas las patentes de ejemplo"""
        self.results = []
        
        for patent_id in self.patents:
            result = self.analyze_patent(patent_id)
            if result:
                self.results.append(result)
        
        return self.results
    
    def print_patent_report(self, result):
        """Imprime reporte de una patente"""
        cat = result["categorization"]
        patent = result["patent_data"]
        
        print(f"\n{'─'*60}")
        print(f"📄 {result['patent_id']}")
        print('─'*60)
        
        print(f"   Título: {patent['title']}")
        print(f"   Assignee: {patent.get('assignee', 'N/A')}")
        print(f"   Fecha: {patent.get('publication_date', 'N/A')}")
        
        print(f"\n   📊 Códigos: {cat['total_codigos_matched']}/{cat['total_codigos_input']} categorizados")
        
        if cat["categorias"]:
            print(f"\n   🏷️  Categorías:")
            for cat_id, cat_data in list(cat["categorias"].items())[:3]:
                icon = CATEGORY_ICONS.get(cat_id, "📁")
                print(f"      {icon} {cat_data['nombre']} (Score: {cat_data['score']:.2f})")
    
    def print_summary_report(self):
        """Imprime reporte resumen"""
        if not self.results:
            self.process_all()
        
        print("\n" + "="*70)
        print("📊 REPORTE DE CLASIFICACIÓN - DEMOSTRACIÓN")
        print("="*70)
        
        print(f"\n📄 Total patentes: {len(self.results)}")
        
        # Estadísticas por categoría
        category_counts = {}
        for result in self.results:
            main_cat = result["categorization"].get("categoria_principal")
            if main_cat:
                category_counts[main_cat] = category_counts.get(main_cat, 0) + 1
        
        print("\n🏷️  DISTRIBUCIÓN POR CATEGORÍA PRINCIPAL:")
        print("-"*50)
        
        for cat_id, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            cat_name = CPC_TAXONOMY[cat_id]["nombre"]
            icon = CATEGORY_ICONS.get(cat_id, "📁")
            pct = (count / len(self.results)) * 100
            bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
            print(f"   {icon} {cat_name}")
            print(f"      [{bar}] {count} patentes ({pct:.1f}%)")
        
        print("\n📋 DETALLE POR PATENTE:")
        print("-"*50)
        
        for result in self.results:
            self.print_patent_report(result)
        
        print("\n" + "="*70)
    
    def get_feature_matrix(self):
        """Genera matriz de características"""
        if not self.results:
            self.process_all()
        
        features = []
        patent_ids = []
        
        for result in self.results:
            cat = result["categorization"]
            
            feature_vector = []
            for cat_id in CPC_TAXONOMY.keys():
                cat_data = cat["categorias"].get(cat_id)
                feature_vector.append(cat_data["score"] if cat_data else 0)
            
            features.append(feature_vector)
            patent_ids.append(result["patent_id"])
        
        return np.array(features), patent_ids
    
    def find_similar_patents(self, patent_id, top_n=3):
        """Encuentra patentes similares"""
        features, ids = self.get_feature_matrix()
        
        if patent_id not in ids:
            return []
        
        idx = ids.index(patent_id)
        ref_vector = features[idx]
        
        similarities = []
        for i, other_id in enumerate(ids):
            if i == idx:
                continue
            
            other_vector = features[i]
            
            # Similitud coseno
            dot = np.dot(ref_vector, other_vector)
            norm1 = np.linalg.norm(ref_vector)
            norm2 = np.linalg.norm(other_vector)
            
            sim = dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0
            
            similarities.append({"patent_id": other_id, "similarity": sim})
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_n]
    
    def export_results(self, filename="demo_results.json"):
        """Exporta resultados a JSON"""
        if not self.results:
            self.process_all()
        
        output_dir = "data/results"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        export_data = {
            "metadata": {
                "date": datetime.now().isoformat(),
                "total_patents": len(self.results),
                "demo_mode": True
            },
            "patents": []
        }
        
        for result in self.results:
            patent = result["patent_data"]
            cat = result["categorization"]
            
            export_data["patents"].append({
                "patent_id": result["patent_id"],
                "title": patent["title"],
                "assignee": patent.get("assignee", ""),
                "categoria_principal": cat.get("categoria_principal_nombre", ""),
                "categorias": list(cat["categorias"].keys()),
                "scores": {k: v["score"] for k, v in cat["categorias"].items()},
                "codigos": cat.get("all_codes", [])
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados exportados: {filepath}")
        return filepath


def run_demo():
    """Ejecuta demostración completa"""
    print("\n" + "="*70)
    print("🌬️  DEMOSTRACIÓN DEL SISTEMA DE CLASIFICACIÓN DE PATENTES  🌬️")
    print("="*70)
    
    classifier = DemoPatentClassifier()
    
    # Mostrar categorías disponibles
    print("\n📂 CATEGORÍAS DISPONIBLES:")
    print("-"*50)
    
    for cat in get_all_categories():
        icon = CATEGORY_ICONS.get(cat["id"], "📁")
        print(f"   {icon} {cat['nombre']}: {cat['num_codigos']} códigos")
    
    # Procesar patentes
    print("\n\n🚀 PROCESANDO PATENTES DE EJEMPLO...")
    classifier.process_all()
    
    # Mostrar reporte
    classifier.print_summary_report()
    
    # Análisis de similitud
    print("\n" + "="*70)
    print("🔍 ANÁLISIS DE SIMILITUD")
    print("="*70)
    
    sample_ids = get_all_sample_ids()
    reference = sample_ids[0]
    
    print(f"\nPatentes similares a {reference}:")
    similar = classifier.find_similar_patents(reference)
    
    for s in similar:
        title = SAMPLE_PATENTS[s["patent_id"]]["title"][:40]
        print(f"   • {s['patent_id']}: {s['similarity']:.4f}")
        print(f"     {title}...")
    
    # Exportar resultados
    print("\n" + "="*70)
    print("💾 EXPORTANDO RESULTADOS")
    print("="*70)
    
    classifier.export_results()
    
    print("\n✅ Demostración completada!")
    
    return classifier


# ═══════════════════════════════════════════════════════════════
# EJEMPLO DE USO INDIVIDUAL
# ═══════════════════════════════════════════════════════════════

def analyze_single_demo(patent_id):
    """Analiza una patente individual de los datos de ejemplo"""
    classifier = DemoPatentClassifier()
    result = classifier.analyze_patent(patent_id)
    
    if result:
        print("\n" + "="*60)
        print(f"🔍 ANÁLISIS DE PATENTE: {patent_id}")
        print("="*60)
        
        classifier.print_patent_report(result)
        
        cat = result["categorization"]
        
        print("\n📊 CÓDIGOS CATEGORIZADOS:")
        for code, info in cat["codigos_matched"].items():
            print(f"   • {code}: {info['descripcion']}")
            print(f"     Categoría: {info['categoria_nombre']}")
    
    return result


if __name__ == "__main__":
    # Ejecutar demostración
    run_demo()
    
    # Ejemplo de análisis individual
    print("\n\n" + "="*70)
    print("📋 EJEMPLO: ANÁLISIS INDIVIDUAL")
    print("="*70)
    
    analyze_single_demo("US8834130B2")
