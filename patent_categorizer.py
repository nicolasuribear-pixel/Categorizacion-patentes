# patent_categorizer.py
"""
Categorizador de Patentes de Palas Eólicas
Integra descarga, extracción de códigos CPC/IPC y categorización automática
VERSIÓN UNIFICADA - Usa estructura de Google.py
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
from datetime import datetime
from collections import defaultdict

from cpc_taxonomy import (
    CPC_TAXONOMY, CODE_INDEX, ALL_CPC_CODES,
    categorize_patent_codes, get_category_for_code,
    CATEGORY_ICONS, CATEGORY_COLORS, normalize_code
)


class PatentCategorizer:
    """
    Categorizador completo de patentes
    Descarga, extrae códigos y categoriza automáticamente
    UNIFICADO con Google.py - usa data/raw/patents/
    """
    
    def __init__(self, patents_dir="data/raw/patents"):
        """
        Inicializa el categorizador
        
        Args:
            patents_dir: directorio donde se guardan las patentes (mismo que Google.py)
        """
        self.patents_dir = patents_dir
        os.makedirs(patents_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    # ═══════════════════════════════════════════════════════════════
    # CARGA DE PATENTES EXISTENTES
    # ═══════════════════════════════════════════════════════════════
    
    def load_patent_from_file(self, patent_id):
        """
        Carga una patente desde archivo JSON existente
        
        Args:
            patent_id: ID de la patente
            
        Returns:
            dict con datos de la patente o None si no existe
        """
        patent_file = os.path.join(self.patents_dir, f"{patent_id}.json")
        
        if os.path.exists(patent_file):
            with open(patent_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def list_downloaded_patents(self):
        """
        Lista todas las patentes descargadas
        
        Returns:
            lista de IDs de patentes
        """
        if not os.path.exists(self.patents_dir):
            return []
        
        patents = []
        for f in os.listdir(self.patents_dir):
            if f.endswith('.json'):
                patent_id = f.replace('.json', '')
                patents.append(patent_id)
        
        return patents
    
    # ═══════════════════════════════════════════════════════════════
    # DESCARGA DE PATENTES (misma lógica que Google.py)
    # ═══════════════════════════════════════════════════════════════
    
    def download_patent(self, patent_id, force_download=False):
        """
        Descarga datos de una patente desde Google Patents
        USA LA MISMA ESTRUCTURA QUE Google.py
        
        Args:
            patent_id: ID de la patente (ej: "US8550777B2")
            force_download: forzar descarga aunque exista en cache
        
        Returns:
            dict con datos de la patente
        """
        # Verificar si ya existe
        if not force_download:
            existing = self.load_patent_from_file(patent_id)
            if existing:
                print(f"📂 Usando patente existente: {patent_id}")
                return existing
        
        url = f"https://patents.google.com/patent/{patent_id}/en"
        
        print(f"📥 Descargando: {patent_id}")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Error: Status code {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ESTRUCTURA IGUAL A Google.py
            patent_data = {
                "patent_id": patent_id,
                "title": "",
                "abstract": "",
                "claims": [],
                "description": "",
                "images": [],
                "ipc_codes": []
            }
            
            # Título
            title_tag = soup.find('meta', {'name': 'DC.title'})
            if title_tag:
                patent_data["title"] = title_tag.get('content', '')
                print(f"   ✓ Título: {patent_data['title'][:50]}...")
            
            # Abstract
            abstract_tag = soup.find('meta', {'name': 'DC.description'})
            if abstract_tag:
                patent_data["abstract"] = abstract_tag.get('content', '')
                print(f"   ✓ Abstract: {len(patent_data['abstract'])} caracteres")
            
            # Claims
            claims_section = soup.find('section', {'itemprop': 'claims'})
            if claims_section:
                claim_divs = claims_section.find_all('div', {'class': 'claim'})
                for claim_div in claim_divs:
                    claim_text = claim_div.find('div', {'class': 'claim-text'})
                    if claim_text:
                        text = claim_text.get_text(strip=True)
                        patent_data["claims"].append(text)
                print(f"   ✓ Claims: {len(patent_data['claims'])} encontrados")
            
            # Descripción
            description_section = soup.find('section', {'itemprop': 'description'})
            if description_section:
                patent_data["description"] = description_section.get_text(strip=True)
                print(f"   ✓ Descripción: {len(patent_data['description'])} caracteres")
            
            # Imágenes
            figures = soup.find_all('meta', {'itemprop': 'full'})
            for idx, fig in enumerate(figures):
                img_url = fig.get('content', '')
                if img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    patent_data["images"].append({
                        "figure_num": idx + 1,
                        "url": img_url,
                    })
            print(f"   ✓ Imágenes: {len(patent_data['images'])} encontradas")
            
            # Códigos IPC/CPC
            ipc_section = soup.find_all('span', {'itemprop': 'Code'})
            for ipc in ipc_section:
                code = ipc.get_text(strip=True)
                if code:
                    patent_data["ipc_codes"].append(code)
            print(f"   ✓ IPC/CPC: {len(patent_data['ipc_codes'])} códigos")
            
            # Guardar en el mismo directorio que Google.py
            self._save_patent(patent_data)
            
            return patent_data
            
        except Exception as e:
            print(f"❌ Error descargando {patent_id}: {str(e)}")
            return None
    
    def _save_patent(self, patent_data):
        """Guarda patente en JSON (misma ubicación que Google.py)"""
        if not patent_data:
            return False
        
        filename = os.path.join(self.patents_dir, f"{patent_data['patent_id']}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(patent_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Guardado: {filename}")
        return True
    
    def download_list(self, patent_ids, delay=1.5, force_download=False):
        """
        Descarga una lista de patentes
        
        Args:
            patent_ids: lista de IDs de patentes
            delay: segundos entre descargas
            force_download: forzar descarga aunque existan
            
        Returns:
            dict con resultados
        """
        results = {
            "exitosas": 0,
            "fallidas": 0,
            "existentes": 0,
            "patents": []
        }
        
        for idx, patent_id in enumerate(patent_ids, 1):
            print(f"\n[{idx}/{len(patent_ids)}] Procesando {patent_id}")
            print("=" * 60)
            
            # Verificar si ya existe
            if not force_download and self.load_patent_from_file(patent_id):
                results["existentes"] += 1
                results["patents"].append(patent_id)
                print(f"📂 Ya existe en {self.patents_dir}")
            else:
                patent_data = self.download_patent(patent_id, force_download)
                
                if patent_data:
                    results["exitosas"] += 1
                    results["patents"].append(patent_id)
                else:
                    results["fallidas"] += 1
                
                # Delay solo si hubo descarga
                if idx < len(patent_ids):
                    print(f"⏳ Esperando {delay} segundos...")
                    time.sleep(delay)
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE DESCARGA")
        print("=" * 60)
        print(f"   ✅ Descargadas: {results['exitosas']}")
        print(f"   📂 Ya existían: {results['existentes']}")
        print(f"   ❌ Fallidas: {results['fallidas']}")
        print(f"   📊 Total: {len(patent_ids)}")
        
        return results
    
    # ═══════════════════════════════════════════════════════════════
    # CATEGORIZACIÓN
    # ═══════════════════════════════════════════════════════════════
    
    def categorize_patent(self, patent_data):
        """
        Categoriza una patente basándose en sus códigos IPC/CPC
        ADAPTADO para estructura de Google.py (solo ipc_codes)
        
        Args:
            patent_data: dict con datos de la patente
        
        Returns:
            dict con categorización completa
        """
        # En la estructura de Google.py, todos los códigos están en ipc_codes
        all_codes = patent_data.get("ipc_codes", [])
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        unique_codes = []
        for code in all_codes:
            normalized = normalize_code(code)
            if normalized not in seen:
                seen.add(normalized)
                unique_codes.append(normalized)
        
        # Categorizar
        categorization = categorize_patent_codes(unique_codes)
        
        # Añadir metadata
        categorization["patent_id"] = patent_data.get("patent_id", "")
        categorization["title"] = patent_data.get("title", "")
        categorization["all_codes"] = unique_codes
        
        # Calcular categoría principal
        if categorization["categorias"]:
            main_category = list(categorization["categorias"].keys())[0]
            categorization["categoria_principal"] = main_category
            categorization["categoria_principal_nombre"] = categorization["categorias"][main_category]["nombre"]
        else:
            categorization["categoria_principal"] = None
            categorization["categoria_principal_nombre"] = "Sin categoría"
        
        return categorization
    
    def analyze_patent(self, patent_id, verbose=True):
        """
        Análisis completo de una patente: carga/descarga + categorización
        
        Args:
            patent_id: ID de la patente
            verbose: mostrar información detallada
        
        Returns:
            dict con análisis completo
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"🔍 ANALIZANDO PATENTE: {patent_id}")
            print('='*60)
        
        # Intentar cargar primero desde archivo
        patent_data = self.load_patent_from_file(patent_id)
        
        if patent_data:
            if verbose:
                print(f"\n📂 Cargada desde: {self.patents_dir}/{patent_id}.json")
        else:
            if verbose:
                print("\n📥 No encontrada localmente, descargando...")
            patent_data = self.download_patent(patent_id)
        
        if not patent_data:
            return None
        
        if verbose:
            print(f"   ✓ Título: {patent_data['title'][:60]}...")
            print(f"   ✓ Códigos IPC/CPC: {len(patent_data.get('ipc_codes', []))}")
            print(f"   ✓ Claims: {len(patent_data.get('claims', []))}")
        
        # Categorizar
        if verbose:
            print("\n📊 Categorizando...")
        
        categorization = self.categorize_patent(patent_data)
        
        # Resultado completo
        result = {
            "patent_id": patent_id,
            "patent_data": patent_data,
            "categorization": categorization,
            "analysis_date": datetime.now().isoformat()
        }
        
        if verbose:
            self.print_categorization_report(result)
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # REPORTES
    # ═══════════════════════════════════════════════════════════════
    
    def print_categorization_report(self, result):
        """Imprime un reporte detallado de la categorización"""
        cat = result["categorization"]
        patent = result["patent_data"]
        
        print(f"\n{'─'*60}")
        print("📋 REPORTE DE CATEGORIZACIÓN")
        print('─'*60)
        
        print(f"\n📄 Patente: {result['patent_id']}")
        print(f"   Título: {patent['title'][:70]}...")
        
        print(f"\n📊 Códigos encontrados: {cat['total_codigos_matched']}/{cat['total_codigos_input']}")
        
        if cat["categorias"]:
            print(f"\n🏷️  CATEGORÍAS IDENTIFICADAS:")
            
            for cat_id, cat_data in cat["categorias"].items():
                icon = CATEGORY_ICONS.get(cat_id, "📁")
                score = cat_data["score"]
                
                # Barra visual de score
                bar_length = int(score * 10)
                bar = '█' * bar_length + '░' * (10 - bar_length)
                
                print(f"\n   {icon} {cat_data['nombre']}")
                print(f"      Score: [{bar}] {score:.2f}")
                print(f"      Códigos:")
                for cod in cat_data["codigos_encontrados"][:5]:
                    print(f"         • {cod['codigo']}: {cod['descripcion'][:40]}...")
                if len(cat_data["codigos_encontrados"]) > 5:
                    print(f"         ... y {len(cat_data['codigos_encontrados']) - 5} más")
        else:
            print("\n⚠️  No se encontraron categorías coincidentes")
            print("   Códigos de la patente no están en la taxonomía de palas eólicas")
        
        # Códigos no categorizados
        matched_codes = set(cat["codigos_matched"].keys())
        all_codes = set(cat.get("all_codes", []))
        unmatched = all_codes - matched_codes
        
        if unmatched:
            print(f"\n📝 Códigos no categorizados ({len(unmatched)}):")
            for code in list(unmatched)[:10]:
                print(f"      • {code}")
            if len(unmatched) > 10:
                print(f"      ... y {len(unmatched) - 10} más")
        
        print(f"\n{'─'*60}")
    
    def get_patent_characteristics(self, result):
        """
        Extrae características clave de una patente categorizada
        
        Args:
            result: resultado de analyze_patent()
        
        Returns:
            dict con características principales
        """
        cat = result["categorization"]
        patent = result["patent_data"]
        
        characteristics = {
            "patent_id": result["patent_id"],
            "title": patent["title"],
            "categoria_principal": cat.get("categoria_principal_nombre", "Sin categoría"),
            "categorias": [],
            "enfoque_tecnologico": [],
            "scores": {}
        }
        
        # Extraer categorías ordenadas por score
        for cat_id, cat_data in cat["categorias"].items():
            characteristics["categorias"].append(cat_data["nombre"])
            characteristics["scores"][cat_id] = cat_data["score"]
            
            # Determinar enfoque tecnológico basado en categorías
            if cat_id == "perfil_aerodinamico":
                characteristics["enfoque_tecnologico"].append("Optimización aerodinámica")
            elif cat_id in ["geometria_2d", "geometria_3d", "geometria_forma"]:
                characteristics["enfoque_tecnologico"].append("Diseño geométrico")
            elif cat_id == "estructura_superficie":
                characteristics["enfoque_tecnologico"].append("Ingeniería estructural")
            elif cat_id == "materiales":
                characteristics["enfoque_tecnologico"].append("Ciencia de materiales")
            elif cat_id == "manufactura":
                characteristics["enfoque_tecnologico"].append("Procesos de fabricación")
            elif cat_id == "control_ajuste":
                characteristics["enfoque_tecnologico"].append("Sistemas de control")
            elif cat_id == "monitoreo_diagnostico":
                characteristics["enfoque_tecnologico"].append("Monitoreo y diagnóstico")
            elif cat_id == "ruido_vibraciones":
                characteristics["enfoque_tecnologico"].append("Reducción de ruido/vibraciones")
        
        # Eliminar duplicados en enfoque
        characteristics["enfoque_tecnologico"] = list(set(characteristics["enfoque_tecnologico"]))
        
        return characteristics
    
    def generate_feature_vector(self, result):
        """
        Genera un vector de características para clustering
        
        Args:
            result: resultado de analyze_patent()
        
        Returns:
            dict con vector de características numéricas
        """
        cat = result["categorization"]
        
        # Vector con score por cada categoría
        feature_vector = {}
        
        for cat_id in CPC_TAXONOMY.keys():
            if cat_id in cat["categorias"]:
                feature_vector[cat_id] = cat["categorias"][cat_id]["score"]
            else:
                feature_vector[cat_id] = 0.0
        
        # Añadir métricas adicionales
        feature_vector["total_codes"] = cat["total_codigos_input"]
        feature_vector["matched_codes"] = cat["total_codigos_matched"]
        feature_vector["match_ratio"] = (
            cat["total_codigos_matched"] / cat["total_codigos_input"]
            if cat["total_codigos_input"] > 0 else 0
        )
        
        return feature_vector


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════

def analyze_single_patent(patent_id):
    """Función de conveniencia para analizar una sola patente"""
    categorizer = PatentCategorizer()
    return categorizer.analyze_patent(patent_id, verbose=True)


def get_patent_summary(patent_id):
    """Obtiene un resumen rápido de una patente"""
    categorizer = PatentCategorizer()
    result = categorizer.analyze_patent(patent_id, verbose=False)
    
    if not result:
        return None
    
    return categorizer.get_patent_characteristics(result)


# ═══════════════════════════════════════════════════════════════
# MAIN - TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔬 PATENT CATEGORIZER - TEST (VERSIÓN UNIFICADA)")
    print("="*60)
    
    categorizer = PatentCategorizer()
    
    # Mostrar patentes disponibles
    available = categorizer.list_downloaded_patents()
    print(f"\n📂 Patentes disponibles en {categorizer.patents_dir}: {len(available)}")
    for p in available[:5]:
        print(f"   • {p}")
    if len(available) > 5:
        print(f"   ... y {len(available) - 5} más")
    
    # Test con una patente existente o nueva
    test_patents = ["US8550777B2", "US7927078B2"]
    
    for patent_id in test_patents:
        result = categorizer.analyze_patent(patent_id, verbose=True)
        
        if result:
            print("\n" + "="*60)
            print("📊 CARACTERÍSTICAS EXTRAÍDAS")
            print("="*60)
            
            chars = categorizer.get_patent_characteristics(result)
            
            print(f"\n🏷️  Categoría principal: {chars['categoria_principal']}")
            print(f"🔧 Enfoque tecnológico: {', '.join(chars['enfoque_tecnologico'])}")
            print(f"📊 Categorías ({len(chars['categorias'])}): {', '.join(chars['categorias'][:5])}")
        
        print("\n")
