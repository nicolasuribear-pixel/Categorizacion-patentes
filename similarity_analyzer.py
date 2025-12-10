# similarity_analyzer.py
"""
Análisis de similitud entre patentes usando Patent Knowledge Graphs (PKG)
Versión 1.0 - Métricas de similitud básicas
"""

import pickle
import json
import os
import networkx as nx
from itertools import combinations
from collections import defaultdict
import numpy as np


class PatentSimilarityAnalyzer:
    """Calcula similitud entre patentes basándose en sus PKG"""

    def __init__(self, graph_file):
        """
        Inicializa el analizador

        Args:
            graph_file: ruta al archivo pickle con el PKG completo
        """
        with open(graph_file, 'rb') as f:
            self.full_graph = pickle.load(f)

        # Extraer lista de patentes
        self.patent_ids = self._extract_patent_ids()

        # Crear subgrafos por patente
        self.patent_subgraphs = {}
        for patent_id in self.patent_ids:
            self.patent_subgraphs[patent_id] = self._extract_patent_subgraph(patent_id)

    def _extract_patent_ids(self):
        """Extrae lista única de IDs de patentes del grafo"""
        patent_ids = set()
        for _, attrs in self.full_graph.nodes(data=True):
            patent_ids.add(attrs.get('patent_id'))
        return sorted(list(patent_ids))

    def _extract_patent_subgraph(self, patent_id):
        """Extrae el subgrafo de una patente específica"""
        patent_nodes = [
            n for n, attrs in self.full_graph.nodes(data=True)
            if attrs.get('patent_id') == patent_id
        ]
        return self.full_graph.subgraph(patent_nodes)

    def get_entity_labels(self, graph):
        """
        Extrae las etiquetas de las entidades de un grafo

        Returns:
            set de labels normalizados
        """
        labels = set()
        for _, attrs in graph.nodes(data=True):
            label = attrs.get('label', '').lower().strip()
            if label:
                labels.add(label)
        return labels

    def get_entity_types(self, graph):
        """Extrae los tipos de entidades (R, F, S, L) de un grafo"""
        types = defaultdict(int)
        for _, attrs in graph.nodes(data=True):
            entity_type = attrs.get('type', '')
            if entity_type:
                types[entity_type] += 1
        return types

    def get_relation_types(self, graph):
        """Extrae los tipos de relaciones de un grafo"""
        relations = defaultdict(int)
        for _, _, attrs in graph.edges(data=True):
            relation = attrs.get('relation', '')
            if relation:
                relations[relation] += 1
        return relations

    def jaccard_similarity(self, set1, set2):
        """
        Calcula similitud de Jaccard entre dos conjuntos

        Jaccard = |A ∩ B| / |A ∪ B|
        """
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        if union == 0:
            return 0.0

        return intersection / union

    def cosine_similarity(self, vec1, vec2):
        """Calcula similitud de coseno entre dos vectores"""
        dot_product = sum(vec1[k] * vec2.get(k, 0) for k in vec1.keys())

        magnitude1 = np.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = np.sqrt(sum(v ** 2 for v in vec2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def calculate_similarity(self, patent_id1, patent_id2):
        """
        Calcula similitud completa entre dos patentes

        Returns:
            diccionario con múltiples métricas de similitud
        """
        graph1 = self.patent_subgraphs[patent_id1]
        graph2 = self.patent_subgraphs[patent_id2]

        # 1. Similitud de entidades (labels)
        labels1 = self.get_entity_labels(graph1)
        labels2 = self.get_entity_labels(graph2)
        entity_similarity = self.jaccard_similarity(labels1, labels2)

        # 2. Similitud de estructura (tipos de entidades)
        types1 = self.get_entity_types(graph1)
        types2 = self.get_entity_types(graph2)
        structure_similarity = self.cosine_similarity(types1, types2)

        # 3. Similitud de relaciones
        relations1 = self.get_relation_types(graph1)
        relations2 = self.get_relation_types(graph2)
        relation_similarity = self.cosine_similarity(relations1, relations2)

        # 4. Similitud de grafo (simple)
        # Número de nodos y aristas
        nodes1 = graph1.number_of_nodes()
        nodes2 = graph2.number_of_nodes()
        edges1 = graph1.number_of_edges()
        edges2 = graph2.number_of_edges()

        node_diff = abs(nodes1 - nodes2) / max(nodes1, nodes2) if max(nodes1, nodes2) > 0 else 0
        edge_diff = abs(edges1 - edges2) / max(edges1, edges2) if max(edges1, edges2) > 0 else 0

        size_similarity = 1 - ((node_diff + edge_diff) / 2)

        # 5. Similitud promedio ponderada
        weights = {
            'entity': 0.4,  # Más importante: contenido semántico
            'structure': 0.2,  # Distribución de tipos
            'relation': 0.2,  # Tipos de relaciones
            'size': 0.2  # Tamaño del grafo
        }

        overall_similarity = (
                weights['entity'] * entity_similarity +
                weights['structure'] * structure_similarity +
                weights['relation'] * relation_similarity +
                weights['size'] * size_similarity
        )

        return {
            'patent1': patent_id1,
            'patent2': patent_id2,
            'overall_similarity': overall_similarity,
            'entity_similarity': entity_similarity,
            'structure_similarity': structure_similarity,
            'relation_similarity': relation_similarity,
            'size_similarity': size_similarity,
            'graph1_stats': {
                'nodes': nodes1,
                'edges': edges1,
                'entity_types': dict(types1),
                'relations': dict(relations1)
            },
            'graph2_stats': {
                'nodes': nodes2,
                'edges': edges2,
                'entity_types': dict(types2),
                'relations': dict(relations2)
            }
        }

    def analyze_all_pairs(self):
        """Calcula similitud entre todos los pares de patentes"""
        results = []

        # Generar todos los pares
        pairs = list(combinations(self.patent_ids, 2))

        print(f"Calculando similitud para {len(pairs)} pares de patentes...\n")

        for patent1, patent2 in pairs:
            similarity = self.calculate_similarity(patent1, patent2)
            results.append(similarity)

        # Ordenar por similitud descendente
        results.sort(key=lambda x: x['overall_similarity'], reverse=True)

        return results

    def print_similarity_report(self, results):
        """Imprime reporte de similitud"""
        print("=" * 80)
        print("📊 REPORTE DE SIMILITUD ENTRE PATENTES")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            print(f"\n{'─' * 80}")
            print(f"PAR #{i}: {result['patent1']} ↔ {result['patent2']}")
            print('─' * 80)

            # Similitud general con barra visual
            overall = result['overall_similarity']
            bar_length = int(overall * 50)
            bar = '█' * bar_length + '░' * (50 - bar_length)

            print(f"\n🎯 SIMILITUD GENERAL: {overall:.4f} ({overall * 100:.2f}%)")
            print(f"   [{bar}]")

            # Desglose de métricas
            print(f"\n📈 DESGLOSE DE MÉTRICAS:")
            print(
                f"   • Similitud de Entidades:  {result['entity_similarity']:.4f} ({result['entity_similarity'] * 100:.1f}%)")
            print(
                f"   • Similitud Estructural:   {result['structure_similarity']:.4f} ({result['structure_similarity'] * 100:.1f}%)")
            print(
                f"   • Similitud de Relaciones: {result['relation_similarity']:.4f} ({result['relation_similarity'] * 100:.1f}%)")
            print(
                f"   • Similitud de Tamaño:     {result['size_similarity']:.4f} ({result['size_similarity'] * 100:.1f}%)")

            # Estadísticas de grafos
            print(f"\n📊 ESTADÍSTICAS DE GRAFOS:")

            g1_stats = result['graph1_stats']
            g2_stats = result['graph2_stats']

            print(f"\n   {result['patent1']}:")
            print(f"      Nodos: {g1_stats['nodes']} | Aristas: {g1_stats['edges']}")
            print(f"      Entidades: R={g1_stats['entity_types'].get('R', 0)}, "
                  f"F={g1_stats['entity_types'].get('F', 0)}, "
                  f"S={g1_stats['entity_types'].get('S', 0)}, "
                  f"L={g1_stats['entity_types'].get('L', 0)}")

            print(f"\n   {result['patent2']}:")
            print(f"      Nodos: {g2_stats['nodes']} | Aristas: {g2_stats['edges']}")
            print(f"      Entidades: R={g2_stats['entity_types'].get('R', 0)}, "
                  f"F={g2_stats['entity_types'].get('F', 0)}, "
                  f"S={g2_stats['entity_types'].get('S', 0)}, "
                  f"L={g2_stats['entity_types'].get('L', 0)}")

        print("\n" + "=" * 80)

    def save_results(self, results, output_file):
        """Guarda resultados en JSON"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados guardados: {output_file}")


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def analyze_patent_similarity():
    """Analiza similitud entre todas las patentes"""
    graph_file = "data/processed/graphs/pkg_complete.pkl"
    output_file = "data/results/similarity/similarity_results.json"

    if not os.path.exists(graph_file):
        print("❌ No se encontró el archivo del grafo PKG")
        print(f"   Esperado: {graph_file}")
        print("   Ejecuta primero: python pkg_builder.py")
        return

    print("\n" + "=" * 80)
    print("🔬 ANÁLISIS DE SIMILITUD ENTRE PATENTES")
    print("=" * 80)

    # Crear analizador
    analyzer = PatentSimilarityAnalyzer(graph_file)

    print(f"\nPatentes encontradas: {len(analyzer.patent_ids)}")
    for patent_id in analyzer.patent_ids:
        graph = analyzer.patent_subgraphs[patent_id]
        print(f"   • {patent_id}: {graph.number_of_nodes()} nodos, {graph.number_of_edges()} aristas")

    # Calcular similitudes
    results = analyzer.analyze_all_pairs()

    # Imprimir reporte
    analyzer.print_similarity_report(results)

    # Guardar resultados
    analyzer.save_results(results, output_file)

    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)

    if results:
        avg_similarity = sum(r['overall_similarity'] for r in results) / len(results)
        max_similarity = max(results, key=lambda x: x['overall_similarity'])
        min_similarity = min(results, key=lambda x: x['overall_similarity'])

        print(f"\nSimilitud promedio: {avg_similarity:.4f} ({avg_similarity * 100:.2f}%)")
        print(f"\nPar más similar:")
        print(f"   {max_similarity['patent1']} ↔ {max_similarity['patent2']}")
        print(
            f"   Similitud: {max_similarity['overall_similarity']:.4f} ({max_similarity['overall_similarity'] * 100:.2f}%)")

        print(f"\nPar menos similar:")
        print(f"   {min_similarity['patent1']} ↔ {min_similarity['patent2']}")
        print(
            f"   Similitud: {min_similarity['overall_similarity']:.4f} ({min_similarity['overall_similarity'] * 100:.2f}%)")

    print("\n✅ Análisis completado!")

    return results


if __name__ == "__main__":
    analyze_patent_similarity()