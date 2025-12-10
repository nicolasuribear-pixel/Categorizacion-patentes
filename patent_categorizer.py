# patent_categorizer.py
"""
Categorizador de Patentes de Palas Eólicas
Integra descarga, extracción de códigos CPC/IPC y categorización automática
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
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
    """
    
    def __init__(self, cache_dir="data/cache"):
        """
        Inicializa el categorizador
        
        Args:
            cache_dir: directorio para cache de patentes descargadas
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    # ═══════════════════════════════════════════════════════════════
    # DESCARGA DE PATENTES
    # ═══════════════════════════════════════════════════════════════
    
    def download_patent(self, patent_id, use_cache=True):
        """
        Descarga datos de una patente desde Google Patents
        
        Args:
            patent_id: ID de la patente (ej: "US8550777B2")
            use_cache: usar cache si existe
        
        Returns:
            dict con datos de la patente
        """
        # Verificar cache
        cache_file = os.path.join(self.cache_dir, f"{patent_id}.json")
        if use_cache and os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        url = f"https://patents.google.com/patent/{patent_id}/en"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ Error descargando {patent_id}: Status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            patent_data = {
                "patent_id": patent_id,
                "url": url,
                "download_date": datetime.now().isoformat(),
                "title": "",
                "abstract": "",
                "claims": [],
                "description": "",
                "ipc_codes": [],
                "cpc_codes": [],
                "inventors": [],
                "assignee": "",
                "priority_date": "",
                "filing_date": "",
                "publication_date": "",
                "images": []
            }
            
            # Título
            title_tag = soup.find('meta', {'name': 'DC.title'})
            if title_tag:
                patent_data["title"] = title_tag.get('content', '')
            
            # Abstract
            abstract_tag = soup.find('meta', {'name': 'DC.description'})
            if abstract_tag:
                patent_data["abstract"] = abstract_tag.get('content', '')
            
            # Claims
            claims_section = soup.find('section', {'itemprop': 'claims'})
            if claims_section:
                claim_divs = claims_section.find_all('div', {'class': 'claim'})
                for claim_div in claim_divs:
                    claim_text = claim_div.find('div', {'class': 'claim-text'})
                    if claim_text:
                        patent_data["claims"].append(claim_text.get_text(strip=True))
            
            # Descripción (primeros 15000 caracteres)
            description_section = soup.find('section', {'itemprop': 'description'})
            if description_section:
                patent_data["description"] = description_section.get_text(strip=True)[:15000]
            
            # Códigos IPC/CPC - MÉTODO MEJORADO
            # Buscar todos los códigos de clasificación
            code_elements = soup.find_all('span', {'itemprop': 'Code'})
            for code_elem in code_elements:
                code = code_elem.get_text(strip=True)
                if code:
                    # Determinar si es IPC o CPC basándose en el patrón
                    if code.startswith(('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')):
                        if 'Y02' in code or '2' in code[:4]:
                            patent_data["cpc_codes"].append(code)
                        else:
                            patent_data["ipc_codes"].append(code)
            
            # Buscar códigos adicionales en metadatos
            classification_items = soup.find_all('li', {'itemprop': 'cpcs'})
            for item in classification_items:
                code_span = item.find('span', {'itemprop': 'Code'})
                if code_span:
                    code = code_span.get_text(strip=True)
                    if code and code not in patent_data["cpc_codes"]:
                        patent_data["cpc_codes"].append(code)
            
            # Inventores
            inventor_elements = soup.find_all('dd', {'itemprop': 'inventor'})
            for inv in inventor_elements:
                patent_data["inventors"].append(inv.get_text(strip=True))
            
            # Assignee
            assignee_elem = soup.find('dd', {'itemprop': 'assigneeOriginal'})
            if assignee_elem:
                patent_data["assignee"] = assignee_elem.get_text(strip=True)
            
            # Fechas
            dates = {
                'priority_date': 'priorityDate',
                'filing_date': 'filingDate',
                'publication_date': 'publicationDate'
            }
            for field, itemprop in dates.items():
                date_elem = soup.find('time', {'itemprop': itemprop})
                if date_elem:
                    patent_data[field] = date_elem.get_text(strip=True)
            
            # Imágenes
            figures = soup.find_all('meta', {'itemprop': 'full'})
            for idx, fig in enumerate(figures):
                img_url = fig.get('content', '')
                if img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    patent_data["images"].append({
                        "figure_num": idx + 1,
                        "url": img_url
                    })
            
            # Guardar en cache
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(patent_data, f, indent=2, ensure_ascii=False)
            
            return patent_data
            
        except Exception as e:
            print(f"❌ Error descargando {patent_id}: {str(e)}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # CATEGORIZACIÓN
    # ═══════════════════════════════════════════════════════════════
    
    def categorize_patent(self, patent_data):
        """
        Categoriza una patente basándose en sus códigos IPC/CPC
        
        Args:
            patent_data: dict con datos de la patente (debe incluir ipc_codes y/o cpc_codes)
        
        Returns:
            dict con categorización completa
        """
        # Combinar todos los códigos
        all_codes = []
        all_codes.extend(patent_data.get("ipc_codes", []))
        all_codes.extend(patent_data.get("cpc_codes", []))
        
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
        Análisis completo de una patente: descarga + categorización
        
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
        
        # Descargar
        if verbose:
            print("\n📥 Descargando datos...")
        
        patent_data = self.download_patent(patent_id)
        
        if not patent_data:
            return None
        
        if verbose:
            print(f"   ✓ Título: {patent_data['title'][:60]}...")
            print(f"   ✓ Códigos IPC: {len(patent_data['ipc_codes'])}")
            print(f"   ✓ Códigos CPC: {len(patent_data['cpc_codes'])}")
            print(f"   ✓ Claims: {len(patent_data['claims'])}")
        
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
        print(f"   Assignee: {patent.get('assignee', 'N/A')}")
        print(f"   Fecha publicación: {patent.get('publication_date', 'N/A')}")
        
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
                for cod in cat_data["codigos_encontrados"]:
                    print(f"         • {cod['codigo']}: {cod['descripcion']}")
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
    print("🔬 PATENT CATEGORIZER - TEST")
    print("="*60)
    
    # Test con una patente de ejemplo
    test_patents = [
        "US8550777B2",  # Wind turbine blade
        "US7927078B2",  # Otra patente de palas
    ]
    
    categorizer = PatentCategorizer()
    
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
            
            print("\n" + "="*60)
            print("🔢 VECTOR DE CARACTERÍSTICAS")
            print("="*60)
            
            vector = categorizer.generate_feature_vector(result)
            for key, value in vector.items():
                if value > 0:
                    print(f"   • {key}: {value:.2f}")
        
        print("\n")
