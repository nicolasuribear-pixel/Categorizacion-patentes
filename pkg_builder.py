# pkg_builder.py
"""
Construcción de Patent Knowledge Graph (PKG) desde entidades RFSL
Versión 1.0 - Construcción básica con NetworkX
"""

import json
import os
import networkx as nx
import pickle
from collections import defaultdict


class PKGBuilder:
    """Constructor de Patent Knowledge Graph"""

    def __init__(self):
        self.graph = nx.DiGraph()  # Grafo dirigido
        self.entity_counter = defaultdict(int)

    def load_rfsl_file(self, rfsl_file):
        """Carga un archivo RFSL JSON"""
        with open(rfsl_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def add_entity_node(self, entity, entity_type, patent_id):
        """
        Añade un nodo de entidad al grafo

        Args:
            entity: diccionario con información de la entidad
            entity_type: tipo de entidad (R, F, S, L)
            patent_id: ID de la patente origen
        """
        # Crear ID único para el nodo
        entity_text = entity['entity'].lower().strip()
        node_id = f"{patent_id}_{entity_type}_{self.entity_counter[entity_text]}"
        self.entity_counter[entity_text] += 1

        # Añadir nodo con atributos
        self.graph.add_node(
            node_id,
            label=entity_text,
            type=entity_type,
            patent_id=patent_id,
            category=entity.get('category', ''),
            position=entity.get('position', -1)
        )

        return node_id

    def extract_relations(self, entities, patent_id):
        """
        Extrae relaciones entre entidades basándose en proximidad

        Args:
            entities: diccionario con entidades RFSL
            patent_id: ID de la patente

        Returns:
            lista de tuplas (source_id, target_id, relation_type)
        """
        relations = []

        # Añadir todos los nodos primero
        nodes = {
            'R': [],
            'F': [],
            'S': [],
            'L': []
        }

        for entity_type in ['R', 'F', 'S', 'L']:
            for entity in entities[entity_type]:
                node_id = self.add_entity_node(entity, entity_type, patent_id)
                nodes[entity_type].append({
                    'id': node_id,
                    'position': entity.get('position', -1),
                    'entity': entity
                })

        # REGLA 1: Requirements (R) -> Functions (F)
        # Un requisito se relaciona con funciones que lo resuelven
        for r_node in nodes['R']:
            for f_node in nodes['F']:
                # Si están cerca en el texto (dentro de 200 caracteres)
                if abs(r_node['position'] - f_node['position']) < 200:
                    relations.append((r_node['id'], f_node['id'], 'addresses'))

        # REGLA 2: Functions (F) -> Structures (S)
        # Una función usa o modifica estructuras
        for f_node in nodes['F']:
            for s_node in nodes['S']:
                # Si están cerca en el texto (dentro de 100 caracteres)
                if abs(f_node['position'] - s_node['position']) < 100:
                    relations.append((f_node['id'], s_node['id'], 'uses'))

        # REGLA 3: Structures (S) -> Locations (L)
        # Una estructura está ubicada en un lugar
        for s_node in nodes['S']:
            for l_node in nodes['L']:
                # Si están cerca en el texto (dentro de 50 caracteres)
                if abs(s_node['position'] - l_node['position']) < 50:
                    relations.append((s_node['id'], l_node['id'], 'located_at'))

        # REGLA 4: Functions (F) -> Locations (L)
        # Una función puede ocurrir en una ubicación específica
        for f_node in nodes['F']:
            for l_node in nodes['L']:
                if abs(f_node['position'] - l_node['position']) < 80:
                    relations.append((f_node['id'], l_node['id'], 'occurs_at'))

        return relations

    def build_graph_from_rfsl(self, rfsl_file):
        """
        Construye un grafo desde un archivo RFSL

        Args:
            rfsl_file: ruta al archivo RFSL JSON
        """
        print(f"\n📄 Procesando: {os.path.basename(rfsl_file)}")

        # Cargar datos
        rfsl_data = self.load_rfsl_file(rfsl_file)
        patent_id = rfsl_data['patent_id']
        entities = rfsl_data['entities']

        # Extraer relaciones
        relations = self.extract_relations(entities, patent_id)

        # Añadir aristas al grafo
        for source, target, rel_type in relations:
            self.graph.add_edge(source, target, relation=rel_type)

        # Estadísticas
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()

        print(f"   ✓ Nodos: {num_nodes}")
        print(f"   ✓ Aristas: {num_edges}")

        return {
            'patent_id': patent_id,
            'nodes': num_nodes,
            'edges': num_edges
        }

    def save_graph(self, output_file):
        """Guarda el grafo en formato pickle"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'wb') as f:
            pickle.dump(self.graph, f)

        print(f"\n💾 Grafo guardado: {output_file}")

    def save_graph_json(self, output_file):
        """Guarda el grafo en formato JSON para visualización"""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Convertir a formato JSON serializable
        graph_data = {
            'nodes': [],
            'edges': []
        }

        # Añadir nodos
        for node_id, attrs in self.graph.nodes(data=True):
            graph_data['nodes'].append({
                'id': node_id,
                **attrs
            })

        # Añadir aristas
        for source, target, attrs in self.graph.edges(data=True):
            graph_data['edges'].append({
                'source': source,
                'target': target,
                **attrs
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Grafo JSON guardado: {output_file}")

    def get_statistics(self):
        """Obtiene estadísticas del grafo"""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'nodes_by_type': defaultdict(int),
            'edges_by_relation': defaultdict(int)
        }

        # Contar nodos por tipo
        for node_id, attrs in self.graph.nodes(data=True):
            stats['nodes_by_type'][attrs['type']] += 1

        # Contar aristas por relación
        for source, target, attrs in self.graph.edges(data=True):
            stats['edges_by_relation'][attrs['relation']] += 1

        return stats


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def build_pkg_from_all_patents():
    """Construye PKG desde todas las patentes procesadas"""
    rfsl_dir = "data/processed/rfsl"
    output_dir = "data/processed/graphs"

    if not os.path.exists(rfsl_dir):
        print("❌ No existe la carpeta de archivos RFSL")
        print(f"   Esperada: {rfsl_dir}")
        print("   Ejecuta primero: python rfsl_extractor.py")
        return

    # Obtener lista de archivos RFSL
    rfsl_files = [
        os.path.join(rfsl_dir, f)
        for f in os.listdir(rfsl_dir)
        if f.endswith('_rfsl.json')
    ]

    if not rfsl_files:
        print(f"❌ No se encontraron archivos RFSL en {rfsl_dir}")
        return

    print("=" * 60)
    print("🔨 CONSTRUCCIÓN DE PATENT KNOWLEDGE GRAPH (PKG)")
    print("=" * 60)
    print(f"Archivos RFSL encontrados: {len(rfsl_files)}\n")

    # Crear builder
    builder = PKGBuilder()

    # Procesar cada archivo
    patent_stats = []
    for rfsl_file in rfsl_files:
        try:
            stats = builder.build_graph_from_rfsl(rfsl_file)
            patent_stats.append(stats)
        except Exception as e:
            print(f"❌ Error procesando {rfsl_file}: {e}")
            import traceback
            traceback.print_exc()

    # Obtener estadísticas globales
    global_stats = builder.get_statistics()

    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL GRAFO PKG")
    print("=" * 60)
    print(f"Patentes procesadas: {len(patent_stats)}")
    print(f"\nNodos totales: {global_stats['total_nodes']}")
    print(f"   • Requirements (R): {global_stats['nodes_by_type']['R']}")
    print(f"   • Functions (F): {global_stats['nodes_by_type']['F']}")
    print(f"   • Structures (S): {global_stats['nodes_by_type']['S']}")
    print(f"   • Locations (L): {global_stats['nodes_by_type']['L']}")

    print(f"\nAristas totales: {global_stats['total_edges']}")
    for relation, count in global_stats['edges_by_relation'].items():
        print(f"   • {relation}: {count}")

    # Calcular densidad del grafo
    n = global_stats['total_nodes']
    if n > 1:
        max_edges = n * (n - 1)  # Grafo dirigido
        density = global_stats['total_edges'] / max_edges
        print(f"\nDensidad del grafo: {density:.4f}")

    # Guardar grafos
    print("\n" + "=" * 60)
    print("💾 GUARDANDO GRAFOS")
    print("=" * 60)

    # Guardar en formato pickle (para procesamiento)
    output_pickle = os.path.join(output_dir, "pkg_complete.pkl")
    builder.save_graph(output_pickle)

    # Guardar en formato JSON (para visualización)
    output_json = os.path.join(output_dir, "pkg_complete.json")
    builder.save_graph_json(output_json)

    print("\n✅ PKG construido exitosamente!")
    print(f"   📂 Archivos guardados en: {output_dir}/")

    return builder


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PARA VISUALIZAR GRAFO
# ═══════════════════════════════════════════════════════════════

def visualize_patent_subgraph(patent_id, graph_file="data/processed/graphs/pkg_complete.pkl"):
    """
    Visualiza el subgrafo de una patente específica

    Args:
        patent_id: ID de la patente a visualizar
        graph_file: archivo pickle con el grafo completo
    """
    import matplotlib.pyplot as plt

    # Cargar grafo
    with open(graph_file, 'rb') as f:
        graph = pickle.load(f)

    # Extraer subgrafo de la patente
    patent_nodes = [n for n, attrs in graph.nodes(data=True)
                    if attrs.get('patent_id') == patent_id]

    subgraph = graph.subgraph(patent_nodes)

    # Configurar colores por tipo
    color_map = {
        'R': '#FF6B6B',  # Rojo para Requirements
        'F': '#4ECDC4',  # Turquesa para Functions
        'S': '#95E1D3',  # Verde para Structures
        'L': '#FFE66D'  # Amarillo para Locations
    }

    node_colors = [color_map.get(attrs['type'], '#CCCCCC')
                   for _, attrs in subgraph.nodes(data=True)]

    # Crear layout
    pos = nx.spring_layout(subgraph, k=2, iterations=50)

    # Dibujar grafo
    plt.figure(figsize=(16, 12))

    nx.draw_networkx_nodes(subgraph, pos,
                           node_color=node_colors,
                           node_size=800,
                           alpha=0.9)

    nx.draw_networkx_edges(subgraph, pos,
                           edge_color='#BBBBBB',
                           arrows=True,
                           arrowsize=20,
                           alpha=0.6)

    # Labels abreviados
    labels = {n: attrs['label'][:30] + '...' if len(attrs['label']) > 30 else attrs['label']
              for n, attrs in subgraph.nodes(data=True)}

    nx.draw_networkx_labels(subgraph, pos, labels,
                            font_size=8,
                            font_weight='bold')

    # Título y leyenda
    plt.title(f"Patent Knowledge Graph - {patent_id}",
              fontsize=16, fontweight='bold')

    # Añadir leyenda
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='#FF6B6B', markersize=10, label='Requirements'),
        plt.Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='#4ECDC4', markersize=10, label='Functions'),
        plt.Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='#95E1D3', markersize=10, label='Structures'),
        plt.Line2D([0], [0], marker='o', color='w',
                   markerfacecolor='#FFE66D', markersize=10, label='Locations')
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.axis('off')
    plt.tight_layout()

    # Guardar
    output_file = f"data/results/visualizations/{patent_id}_graph.png"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"📊 Visualización guardada: {output_file}")

    plt.close()


if __name__ == "__main__":
    builder = build_pkg_from_all_patents()

    # Opcional: Visualizar grafo de la primera patente
    if builder:
        print("\n" + "=" * 60)
        print("🎨 GENERANDO VISUALIZACIONES")
        print("=" * 60)

        try:
            visualize_patent_subgraph("US8025476B2")
            visualize_patent_subgraph("US7821148B2")
            visualize_patent_subgraph("US8738192B2")
            print("\n Visualizaciones generadas!")
        except Exception as e:
            print(f"  Error generando visualizaciones: {e}")
            print("   (Esto es opcional, el PKG ya está construido)")