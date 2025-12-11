# hybrid_classifier.py
"""
Sistema Híbrido de Clasificación de Patentes v1.0
Integra análisis semántico (PKG) con taxonomía CPC/IPC

Estrategias de fusión:
1. Votación ponderada
2. Ensemble con reglas
3. Stacking (meta-clasificador)
4. KNN híbrido
"""

import json
import os
import numpy as np
from collections import defaultdict
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# Importar taxonomía v2
from cpc_taxonomy_v2 import (
    CPC_TAXONOMY, CODE_INDEX, CATEGORY_ICONS, CATEGORY_COLORS,
    categorize_patent_codes, get_all_categories, normalize_code
)


# ═══════════════════════════════════════════════════════════════════════════════
# CLASE PRINCIPAL: CLASIFICADOR HÍBRIDO
# ═══════════════════════════════════════════════════════════════════════════════

class HybridPatentClassifier:
    """
    Clasificador híbrido que combina:
    - Pipeline PKG: análisis semántico del abstract (RFSL)
    - Main Classifier: taxonomía CPC/IPC estructurada
    
    Métodos de fusión disponibles:
    - 'weighted_voting': Votación ponderada simple
    - 'ensemble_rules': Reglas de decisión basadas en confianza
    - 'knn_hybrid': K-Nearest Neighbors con features combinadas
    - 'stacking': Meta-clasificador que aprende de ambos
    """
    
    def __init__(self, fusion_method='weighted_voting', weights=None):
        """
        Inicializa el clasificador híbrido
        
        Args:
            fusion_method: Método de fusión ('weighted_voting', 'ensemble_rules', 
                          'knn_hybrid', 'stacking')
            weights: Dict con pesos para cada sistema {'semantic': 0.4, 'cpc': 0.6}
        """
        self.fusion_method = fusion_method
        self.weights = weights or {'semantic': 0.4, 'cpc': 0.6}
        
        # Componentes
        self.semantic_classifier = SemanticClassifier()
        self.cpc_classifier = CPCClassifier()
        
        # Para KNN híbrido
        self.knn_model = None
        self.feature_matrix = None
        self.patent_labels = []
        self.scaler = StandardScaler()
        
        # Categorías disponibles
        self.categories = list(CPC_TAXONOMY.keys())
    
    # ───────────────────────────────────────────────────────────────────────────
    # MÉTODO 1: VOTACIÓN PONDERADA
    # ───────────────────────────────────────────────────────────────────────────
    
    def weighted_voting(self, semantic_scores, cpc_scores):
        """
        Combina scores mediante votación ponderada
        
        Formula: score_final = w_sem * score_sem + w_cpc * score_cpc
        
        Args:
            semantic_scores: dict {categoria: score} del análisis semántico
            cpc_scores: dict {categoria: score} del análisis CPC
        
        Returns:
            dict con scores combinados y categoría ganadora
        """
        combined_scores = {}
        w_sem = self.weights['semantic']
        w_cpc = self.weights['cpc']
        
        # Normalizar scores a [0, 1] para cada sistema
        sem_max = max(semantic_scores.values()) if semantic_scores else 1
        cpc_max = max(cpc_scores.values()) if cpc_scores else 1
        
        for cat in self.categories:
            sem_norm = semantic_scores.get(cat, 0) / sem_max if sem_max > 0 else 0
            cpc_norm = cpc_scores.get(cat, 0) / cpc_max if cpc_max > 0 else 0
            
            combined_scores[cat] = (w_sem * sem_norm) + (w_cpc * cpc_norm)
        
        # Determinar categoría ganadora
        winner = max(combined_scores, key=combined_scores.get)
        
        return {
            'categoria_principal': winner,
            'scores': combined_scores,
            'confianza': combined_scores[winner],
            'metodo': 'weighted_voting'
        }
    
    # ───────────────────────────────────────────────────────────────────────────
    # MÉTODO 2: ENSEMBLE CON REGLAS
    # ───────────────────────────────────────────────────────────────────────────
    
    def ensemble_rules(self, semantic_result, cpc_result, patent_data):
        """
        Aplica reglas de decisión basadas en confianza y características
        
        Reglas:
        1. Si ambos sistemas coinciden → alta confianza
        2. Si CPC tiene códigos específicos (peso 1.0) → priorizar CPC
        3. Si semántico tiene keywords fuertes → considerar semántico
        4. En caso de conflicto → usar heurísticas de desempate
        
        Args:
            semantic_result: resultado del clasificador semántico
            cpc_result: resultado del clasificador CPC
            patent_data: datos originales de la patente
        
        Returns:
            dict con clasificación final y justificación
        """
        sem_cat = semantic_result.get('categoria_principal')
        cpc_cat = cpc_result.get('categoria_principal')
        
        sem_conf = semantic_result.get('confianza', 0)
        cpc_conf = cpc_result.get('confianza', 0)
        
        # Regla 1: Coincidencia → alta confianza
        if sem_cat == cpc_cat:
            return {
                'categoria_principal': sem_cat,
                'confianza': min(1.0, (sem_conf + cpc_conf) / 2 + 0.2),
                'justificacion': 'Ambos sistemas coinciden',
                'concordancia': True,
                'metodo': 'ensemble_rules'
            }
        
        # Regla 2: CPC tiene códigos de peso 1.0
        cpc_primary_codes = self._count_primary_codes(cpc_result)
        if cpc_primary_codes >= 2:
            return {
                'categoria_principal': cpc_cat,
                'confianza': cpc_conf,
                'justificacion': f'CPC tiene {cpc_primary_codes} códigos primarios',
                'concordancia': False,
                'metodo': 'ensemble_rules'
            }
        
        # Regla 3: Semántico tiene keywords muy específicos
        sem_keyword_score = self._evaluate_keyword_strength(semantic_result)
        if sem_keyword_score > 0.8:
            return {
                'categoria_principal': sem_cat,
                'confianza': sem_conf,
                'justificacion': 'Keywords semánticos muy específicos',
                'concordancia': False,
                'metodo': 'ensemble_rules'
            }
        
        # Regla 4: Desempate por confianza ponderada
        final_cat = cpc_cat if cpc_conf * 0.6 > sem_conf * 0.4 else sem_cat
        return {
            'categoria_principal': final_cat,
            'confianza': max(sem_conf, cpc_conf) * 0.8,
            'justificacion': 'Desempate por confianza ponderada',
            'concordancia': False,
            'metodo': 'ensemble_rules'
        }
    
    def _count_primary_codes(self, cpc_result):
        """Cuenta códigos con peso 1.0 en el resultado CPC"""
        count = 0
        for cat_data in cpc_result.get('categorias', {}).values():
            for code_info in cat_data.get('codigos_encontrados', []):
                if code_info.get('peso', 0) >= 1.0:
                    count += 1
        return count
    
    def _evaluate_keyword_strength(self, semantic_result):
        """Evalúa la fuerza de los keywords encontrados"""
        # Simplificado: basado en número de matches
        matches = semantic_result.get('keyword_matches', 0)
        return min(1.0, matches / 10)
    
    # ───────────────────────────────────────────────────────────────────────────
    # MÉTODO 3: KNN HÍBRIDO
    # ───────────────────────────────────────────────────────────────────────────
    
    def build_hybrid_features(self, patent_data, semantic_result, cpc_result):
        """
        Construye vector de características híbrido
        
        Features:
        - 7 scores de categorías (semántico)
        - 7 scores de categorías (CPC)
        - Métricas adicionales (códigos matched, keywords, etc.)
        
        Args:
            patent_data: datos de la patente
            semantic_result: resultado semántico
            cpc_result: resultado CPC
        
        Returns:
            numpy array con features
        """
        features = []
        
        # Features semánticas (7 categorías)
        sem_scores = semantic_result.get('scores', {})
        for cat in self.categories:
            features.append(sem_scores.get(cat, 0))
        
        # Features CPC (7 categorías)
        cpc_scores = {}
        for cat_id, cat_data in cpc_result.get('categorias', {}).items():
            cpc_scores[cat_id] = cat_data.get('score', 0)
        for cat in self.categories:
            features.append(cpc_scores.get(cat, 0))
        
        # Features adicionales
        features.extend([
            cpc_result.get('total_codigos_matched', 0) / 20,  # Normalizado
            cpc_result.get('total_codigos_input', 0) / 50,
            semantic_result.get('keyword_matches', 0) / 10,
            semantic_result.get('confianza', 0),
        ])
        
        return np.array(features)
    
    def fit_knn(self, training_patents, n_neighbors=5):
        """
        Entrena el modelo KNN con patentes etiquetadas
        
        Args:
            training_patents: lista de dicts con 'patent_data', 'label'
            n_neighbors: número de vecinos
        """
        features = []
        labels = []
        
        for patent in training_patents:
            patent_data = patent['patent_data']
            label = patent['label']
            
            # Clasificar con ambos sistemas
            sem_result = self.semantic_classifier.classify(patent_data)
            cpc_result = self.cpc_classifier.classify(patent_data)
            
            # Construir features
            feat_vector = self.build_hybrid_features(patent_data, sem_result, cpc_result)
            features.append(feat_vector)
            labels.append(label)
        
        # Normalizar y entrenar KNN
        self.feature_matrix = np.array(features)
        self.feature_matrix = self.scaler.fit_transform(self.feature_matrix)
        self.patent_labels = labels
        
        self.knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.knn_model.fit(self.feature_matrix)
        
        print(f"✓ KNN entrenado con {len(labels)} patentes")
    
    def knn_classify(self, patent_data, semantic_result, cpc_result):
        """
        Clasifica usando KNN con features híbridas
        
        Args:
            patent_data: datos de la patente
            semantic_result: resultado semántico
            cpc_result: resultado CPC
        
        Returns:
            dict con clasificación basada en vecinos
        """
        if self.knn_model is None:
            raise ValueError("KNN no entrenado. Ejecute fit_knn() primero.")
        
        # Construir features
        feat_vector = self.build_hybrid_features(patent_data, semantic_result, cpc_result)
        feat_vector = self.scaler.transform([feat_vector])
        
        # Encontrar vecinos
        distances, indices = self.knn_model.kneighbors(feat_vector)
        
        # Votar por categoría
        neighbor_labels = [self.patent_labels[i] for i in indices[0]]
        neighbor_distances = distances[0]
        
        # Votación ponderada por distancia
        votes = defaultdict(float)
        for label, dist in zip(neighbor_labels, neighbor_distances):
            weight = 1 / (dist + 0.01)  # Evitar división por cero
            votes[label] += weight
        
        winner = max(votes, key=votes.get)
        total_weight = sum(votes.values())
        
        return {
            'categoria_principal': winner,
            'confianza': votes[winner] / total_weight if total_weight > 0 else 0,
            'vecinos': neighbor_labels,
            'distancias': neighbor_distances.tolist(),
            'metodo': 'knn_hybrid'
        }
    
    # ───────────────────────────────────────────────────────────────────────────
    # MÉTODO PRINCIPAL: CLASIFICAR
    # ───────────────────────────────────────────────────────────────────────────
    
    def classify(self, patent_data, verbose=False):
        """
        Clasificación híbrida de una patente
        
        Args:
            patent_data: dict con datos de la patente (abstract, códigos CPC, etc.)
            verbose: mostrar detalles
        
        Returns:
            dict con clasificación completa
        """
        # 1. Clasificación semántica (PKG)
        semantic_result = self.semantic_classifier.classify(patent_data)
        
        # 2. Clasificación CPC
        cpc_result = self.cpc_classifier.classify(patent_data)
        
        # 3. Fusión según método seleccionado
        if self.fusion_method == 'weighted_voting':
            sem_scores = semantic_result.get('scores', {})
            cpc_scores = {
                cat_id: cat_data['score'] 
                for cat_id, cat_data in cpc_result.get('categorias', {}).items()
            }
            fusion_result = self.weighted_voting(sem_scores, cpc_scores)
            
        elif self.fusion_method == 'ensemble_rules':
            fusion_result = self.ensemble_rules(semantic_result, cpc_result, patent_data)
            
        elif self.fusion_method == 'knn_hybrid':
            fusion_result = self.knn_classify(patent_data, semantic_result, cpc_result)
            
        else:
            # Default: votación ponderada
            sem_scores = semantic_result.get('scores', {})
            cpc_scores = {
                cat_id: cat_data['score'] 
                for cat_id, cat_data in cpc_result.get('categorias', {}).items()
            }
            fusion_result = self.weighted_voting(sem_scores, cpc_scores)
        
        # Resultado completo
        result = {
            'patent_id': patent_data.get('patent_id', ''),
            'title': patent_data.get('title', ''),
            'clasificacion_final': fusion_result,
            'clasificacion_semantica': semantic_result,
            'clasificacion_cpc': cpc_result,
            'timestamp': datetime.now().isoformat()
        }
        
        if verbose:
            self._print_classification_report(result)
        
        return result
    
    def _print_classification_report(self, result):
        """Imprime reporte de clasificación"""
        print("\n" + "=" * 70)
        print(f"📋 CLASIFICACIÓN HÍBRIDA: {result['patent_id']}")
        print("=" * 70)
        
        print(f"\n📄 Título: {result['title'][:60]}...")
        
        # Resultado final
        final = result['clasificacion_final']
        cat = final['categoria_principal']
        icon = CATEGORY_ICONS.get(cat, '📁')
        
        print(f"\n🎯 CATEGORÍA FINAL: {icon} {CPC_TAXONOMY[cat]['nombre']}")
        print(f"   Confianza: {final['confianza']:.2%}")
        print(f"   Método: {final['metodo']}")
        
        # Comparación de sistemas
        sem = result['clasificacion_semantica']
        cpc = result['clasificacion_cpc']
        
        sem_cat = sem.get('categoria_principal', 'N/A')
        cpc_cat = cpc.get('categoria_principal', 'N/A')
        
        print(f"\n📊 COMPARACIÓN DE SISTEMAS:")
        print(f"   • Semántico (PKG): {CATEGORY_ICONS.get(sem_cat, '📁')} {sem_cat}")
        print(f"   • CPC/IPC:         {CATEGORY_ICONS.get(cpc_cat, '📁')} {cpc_cat}")
        
        concordancia = "✅ Coinciden" if sem_cat == cpc_cat else "⚠️ Difieren"
        print(f"   → {concordancia}")
        
        print("\n" + "=" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# CLASIFICADOR SEMÁNTICO (PKG)
# ═══════════════════════════════════════════════════════════════════════════════

class SemanticClassifier:
    """
    Clasificador basado en análisis semántico del texto
    Usa keywords de dominio y patrones RFSL
    """
    
    def __init__(self):
        # Keywords por categoría (derivados de domain_dictionaries.py)
        self.category_keywords = {
            'aerodinamico': [
                'aerodynamic', 'airfoil', 'lift', 'drag', 'flow', 'profile',
                'winglet', 'leading edge', 'trailing edge', 'shape', 'streamline',
                'boundary layer', 'separation', 'stall', 'angle of attack'
            ],
            'estructura': [
                'spar', 'web', 'shell', 'segment', 'section', 'structure',
                'cap', 'sandwich', 'beam', 'rib', 'skin', 'root', 'joint',
                'longitudinal', 'cross-section', 'internal'
            ],
            'vortex': [
                'vortex generator', 'vortex', 'turbulator', 'flow control',
                'boundary layer', 'fin', 'tab', 'protrusion', 'vg', 'delta'
            ],
            'ruido': [
                'noise', 'acoustic', 'sound', 'serration', 'silent', 'quiet',
                'reduction', 'damping', 'trailing edge noise', 'aeroacoustic'
            ],
            'control': [
                'pitch', 'control', 'actuator', 'angle', 'adjustment', 'mechanism',
                'hydraulic', 'electric', 'bearing', 'rotation', 'variable'
            ],
            'monitoreo': [
                'sensor', 'monitoring', 'strain', 'load', 'vibration', 'measurement',
                'detection', 'diagnostic', 'health', 'gauge', 'fatigue', 'crack'
            ],
            'materiales': [
                'composite', 'fiber', 'carbon', 'glass', 'resin', 'epoxy',
                'manufacturing', 'molding', 'pultrusion', 'infusion', 'layup',
                'fabric', 'laminate', 'polymer'
            ]
        }
    
    def classify(self, patent_data):
        """
        Clasifica patente basándose en análisis semántico
        
        Args:
            patent_data: dict con 'abstract', 'title', 'claims', etc.
        
        Returns:
            dict con scores por categoría
        """
        # Concatenar texto relevante
        text = ' '.join([
            patent_data.get('title', ''),
            patent_data.get('abstract', ''),
            ' '.join(patent_data.get('claims', [])[:3])  # Primeros 3 claims
        ]).lower()
        
        # Calcular scores por categoría
        scores = {}
        total_matches = 0
        
        for cat_id, keywords in self.category_keywords.items():
            matches = 0
            for keyword in keywords:
                if keyword in text:
                    # Contar ocurrencias
                    count = text.count(keyword)
                    matches += count
            
            scores[cat_id] = matches
            total_matches += matches
        
        # Normalizar scores
        if total_matches > 0:
            for cat in scores:
                scores[cat] = scores[cat] / total_matches
        
        # Determinar categoría principal
        if scores:
            main_cat = max(scores, key=scores.get)
            confidence = scores[main_cat]
        else:
            main_cat = None
            confidence = 0
        
        return {
            'categoria_principal': main_cat,
            'scores': scores,
            'confianza': confidence,
            'keyword_matches': total_matches,
            'metodo': 'semantic'
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLASIFICADOR CPC/IPC
# ═══════════════════════════════════════════════════════════════════════════════

class CPCClassifier:
    """
    Clasificador basado en taxonomía CPC/IPC v2
    """
    
    def classify(self, patent_data):
        """
        Clasifica patente basándose en códigos CPC/IPC
        
        Args:
            patent_data: dict con 'ipc_codes', 'cpc_codes'
        
        Returns:
            dict con categorización
        """
        # Combinar todos los códigos
        all_codes = []
        all_codes.extend(patent_data.get('ipc_codes', []))
        all_codes.extend(patent_data.get('cpc_codes', []))
        
        # Usar función de taxonomía v2
        result = categorize_patent_codes(all_codes)
        
        # Determinar categoría principal
        if result['categorias']:
            main_cat = list(result['categorias'].keys())[0]
            main_score = result['categorias'][main_cat]['score']
        else:
            main_cat = None
            main_score = 0
        
        result['categoria_principal'] = main_cat
        result['confianza'] = main_score / 5 if main_score > 0 else 0  # Normalizar
        result['metodo'] = 'cpc'
        
        return result


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN DE CONVENIENCIA
# ═══════════════════════════════════════════════════════════════════════════════

def classify_patent_hybrid(patent_data, method='weighted_voting', weights=None, verbose=True):
    """
    Función de conveniencia para clasificación híbrida
    
    Args:
        patent_data: dict con datos de la patente
        method: 'weighted_voting', 'ensemble_rules', 'knn_hybrid'
        weights: pesos para votación ponderada
        verbose: mostrar reporte
    
    Returns:
        resultado de clasificación
    """
    classifier = HybridPatentClassifier(fusion_method=method, weights=weights)
    return classifier.classify(patent_data, verbose=verbose)


def compare_classification_methods(patent_data):
    """
    Compara todos los métodos de clasificación para una patente
    
    Args:
        patent_data: dict con datos de la patente
    
    Returns:
        dict con comparación de métodos
    """
    methods = ['weighted_voting', 'ensemble_rules']
    results = {}
    
    print("\n" + "=" * 70)
    print("🔬 COMPARACIÓN DE MÉTODOS DE CLASIFICACIÓN")
    print("=" * 70)
    print(f"\n📄 Patente: {patent_data.get('patent_id', 'N/A')}")
    
    for method in methods:
        classifier = HybridPatentClassifier(fusion_method=method)
        result = classifier.classify(patent_data, verbose=False)
        results[method] = result
        
        final = result['clasificacion_final']
        cat = final['categoria_principal']
        icon = CATEGORY_ICONS.get(cat, '📁')
        
        print(f"\n📊 {method.upper()}:")
        print(f"   → {icon} {CPC_TAXONOMY[cat]['nombre']}")
        print(f"   Confianza: {final['confianza']:.2%}")
    
    # Verificar consenso
    categories = [r['clasificacion_final']['categoria_principal'] for r in results.values()]
    if len(set(categories)) == 1:
        print(f"\n✅ CONSENSO: Todos los métodos coinciden")
    else:
        print(f"\n⚠️ DIVERGENCIA: Los métodos difieren")
    
    print("\n" + "=" * 70)
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔬 HYBRID PATENT CLASSIFIER - TEST")
    print("=" * 70)
    
    # Patente de prueba: Generador de vórtices
    test_patent_vg = {
        "patent_id": "US9759186B2",
        "title": "Vortex generator unit with airfoil base for wind turbine blade",
        "abstract": "A vortex generator unit comprising an airfoil-shaped base and multiple delta-shaped fins. The vortex generators are positioned on the suction side of the wind turbine blade to control boundary layer separation and improve aerodynamic efficiency.",
        "ipc_codes": ["F03D1/06", "F05B2240/3062"],
        "cpc_codes": ["F03D1/0633", "F05B2240/122", "F05B2240/3062"]
    }
    
    print("\n🧪 TEST 1: Patente de Generadores de Vórtice")
    compare_classification_methods(test_patent_vg)
    
    # Patente de prueba: Reducción de ruido
    test_patent_noise = {
        "patent_id": "US11204015B2",
        "title": "Serrated trailing edge panel for wind turbine blade noise reduction",
        "abstract": "A trailing edge panel with serrations designed to reduce aeroacoustic noise generated by wind turbine blades. The serration pattern is optimized for low-frequency noise attenuation.",
        "ipc_codes": ["F03D80/30", "F05B2260/96"],
        "cpc_codes": ["F03D80/30", "F05B2240/3042", "F05B2260/962"]
    }
    
    print("\n🧪 TEST 2: Patente de Reducción de Ruido")
    compare_classification_methods(test_patent_noise)
    
    # Patente de prueba: Control de pitch
    test_patent_control = {
        "patent_id": "US8430632B2",
        "title": "System for pitching rotor blade with hydraulic actuator",
        "abstract": "A pitch control system for wind turbine rotor blades using hydraulic actuators. The system enables individual blade pitch adjustment for optimized power capture and load reduction.",
        "ipc_codes": ["F03D7/02", "F03D7/0224"],
        "cpc_codes": ["F03D7/0224", "F03D7/024", "F05B2270/328"]
    }
    
    print("\n🧪 TEST 3: Patente de Control de Pitch")
    compare_classification_methods(test_patent_control)
    
    print("\n✅ Tests completados!")
