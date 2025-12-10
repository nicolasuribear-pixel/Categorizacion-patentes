# kmeans_classifier.py
"""
Clasificación de patentes usando K-Means Clustering
Agrupa patentes similares sin necesidad de etiquetas previas
"""

import pickle
import json
import os
import numpy as np
import networkx as nx
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib

matplotlib.use('Agg')  # Backend sin GUI
import matplotlib.pyplot as plt


class KMeansPatentClassifier:
    """Clasificador de patentes usando K-Means"""

    def __init__(self, graph_file):
        """
        Inicializa el clasificador

        Args:
            graph_file: ruta al archivo pickle con el PKG completo
        """
        with open(graph_file, 'rb') as f:
            self.full_graph = pickle.load(f)

        # Extraer patentes
        self.patent_ids = self._extract_patent_ids()
        self.patent_subgraphs = {}

        for patent_id in self.patent_ids:
            self.patent_subgraphs[patent_id] = self._extract_patent_subgraph(patent_id)

        self.feature_matrix = None
        self.feature_names = []
        self.scaler = StandardScaler()
        self.kmeans = None
        self.clusters = None

    def _extract_patent_ids(self):
        """Extrae lista única de IDs de patentes"""
        patent_ids = set()
        for _, attrs in self.full_graph.nodes(data=True):
            patent_ids.add(attrs.get('patent_id'))
        return sorted(list(patent_ids))

    def _extract_patent_subgraph(self, patent_id):
        """Extrae el subgrafo de una patente"""
        patent_nodes = [
            n for n, attrs in self.full_graph.nodes(data=True)
            if attrs.get('patent_id') == patent_id
        ]
        return self.full_graph.subgraph(patent_nodes)

    def extract_features(self):
        """
        Extrae características (features) de cada patente para clustering

        Features extraídas:
        - Número de nodos por tipo (R, F, S, L)
        - Ratios de tipos de nodos
        - Número de aristas por tipo de relación
        - Métricas topológicas del grafo
        """
        features = []

        print("Extrayendo features de patentes...\n")

        for patent_id in self.patent_ids:
            graph = self.patent_subgraphs[patent_id]
            patent_features = []

            # GRUPO 1: Conteos de nodos por tipo
            node_types = {'R': 0, 'F': 0, 'S': 0, 'L': 0}
            for _, attrs in graph.nodes(data=True):
                ntype = attrs.get('type', 'unknown')
                if ntype in node_types:
                    node_types[ntype] += 1

            patent_features.extend([
                node_types['R'],
                node_types['F'],
                node_types['S'],
                node_types['L']
            ])

            # GRUPO 2: Ratios de tipos
            total_nodes = sum(node_types.values())
            if total_nodes > 0:
                patent_features.extend([
                    node_types['R'] / total_nodes,
                    node_types['F'] / total_nodes,
                    node_types['S'] / total_nodes,
                    node_types['L'] / total_nodes
                ])
            else:
                patent_features.extend([0, 0, 0, 0])

            # GRUPO 3: Conteos de aristas por tipo de relación
            edge_types = {'addresses': 0, 'uses': 0, 'located_at': 0, 'occurs_at': 0}
            for _, _, attrs in graph.edges(data=True):
                etype = attrs.get('relation', 'unknown')
                if etype in edge_types:
                    edge_types[etype] += 1

            patent_features.extend([
                edge_types['addresses'],
                edge_types['uses'],
                edge_types['located_at'],
                edge_types['occurs_at']
            ])

            # GRUPO 4: Métricas topológicas del grafo
            num_nodes = graph.number_of_nodes()
            num_edges = graph.number_of_edges()

            patent_features.extend([
                num_nodes,
                num_edges,
                nx.density(graph) if num_nodes > 1 else 0
            ])

            # GRUPO 5: Grados
            if num_nodes > 0:
                degrees = [d for _, d in graph.degree()]
                patent_features.extend([
                    np.mean(degrees),
                    np.max(degrees),
                    np.std(degrees)
                ])
            else:
                patent_features.extend([0, 0, 0])

            # GRUPO 6: Conectividad
            undirected = graph.to_undirected()
            num_components = nx.number_connected_components(undirected)
            patent_features.append(num_components)

            # GRUPO 7: Centralización
            if num_nodes > 1:
                centrality = nx.degree_centrality(graph)
                centrality_values = list(centrality.values())
                max_centrality = max(centrality_values) if centrality_values else 0
                sum_diff = sum(max_centrality - c for c in centrality_values)
                max_possible = (num_nodes - 1) * (num_nodes - 2)
                centralization = sum_diff / max_possible if max_possible > 0 else 0
                patent_features.append(centralization)
            else:
                patent_features.append(0)

            features.append(patent_features)

        # Nombres de features
        self.feature_names = [
            # Conteos
            'count_R', 'count_F', 'count_S', 'count_L',
            # Ratios
            'ratio_R', 'ratio_F', 'ratio_S', 'ratio_L',
            # Relaciones
            'edges_addresses', 'edges_uses', 'edges_located_at', 'edges_occurs_at',
            # Topología
            'total_nodes', 'total_edges', 'density',
            # Grados
            'avg_degree', 'max_degree', 'std_degree',
            # Conectividad
            'num_components',
            # Centralización
            'centralization'
        ]

        self.feature_matrix = np.array(features)

        print(f"✓ Features extraídas: {self.feature_matrix.shape}")
        print(f"  - {len(self.patent_ids)} patentes")
        print(f"  - {len(self.feature_names)} features por patente\n")

        return self.feature_matrix

    def determine_optimal_k(self, max_k=None):
        """
        Determina el número óptimo de clusters usando el método del codo

        Args:
            max_k: número máximo de clusters a probar (default: n_patentes - 1)
        """
        if self.feature_matrix is None:
            print("❌ Primero debes extraer features")
            return

        if max_k is None:
            max_k = min(len(self.patent_ids) - 1, 5)

        # Normalizar features
        X_scaled = self.scaler.fit_transform(self.feature_matrix)

        inertias = []
        K_range = range(2, max_k + 1)

        print(f"Probando K de 2 a {max_k}...")

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
            print(f"  K={k}: inertia={kmeans.inertia_:.2f}")

        # Graficar método del codo
        plt.figure(figsize=(10, 6))
        plt.plot(list(K_range), inertias, 'bo-')
        plt.xlabel('Número de Clusters (K)', fontsize=12)
        plt.ylabel('Inertia (Within-cluster sum of squares)', fontsize=12)
        plt.title('Método del Codo para Determinar K Óptimo', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)

        output_file = "data/results/visualizations/elbow_method.png"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n📊 Gráfico del codo guardado: {output_file}")

        return inertias

    def fit_kmeans(self, n_clusters=3):
        """
        Entrena el modelo K-Means

        Args:
            n_clusters: número de clusters a crear
        """
        if self.feature_matrix is None:
            print("❌ Primero debes extraer features")
            return

        print(f"\n🔬 Entrenando K-Means con {n_clusters} clusters...")

        # Normalizar features
        X_scaled = self.scaler.fit_transform(self.feature_matrix)

        # Entrenar K-Means
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.clusters = self.kmeans.fit_predict(X_scaled)

        print(f"✓ Modelo entrenado!")
        print(f"  Inertia: {self.kmeans.inertia_:.2f}")

        # Mostrar distribución de clusters
        print(f"\n Distribución de patentes por cluster:")
        for cluster_id in range(n_clusters):
            patents_in_cluster = [self.patent_ids[i] for i in range(len(self.patent_ids))
                                  if self.clusters[i] == cluster_id]
            print(f"  Cluster {cluster_id}: {len(patents_in_cluster)} patentes")
            for patent_id in patents_in_cluster:
                print(f"    • {patent_id}")

        return self.clusters

    def visualize_clusters_pca(self):
        """Visualiza clusters usando PCA (reducción a 2D)"""
        if self.kmeans is None:
            print(" Primero debes entrenar el modelo")
            return

        print("\n Generando visualización PCA...")

        # Normalizar features
        X_scaled = self.scaler.transform(self.feature_matrix)

        # Reducir a 2D con PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)

        # Crear gráfico
        plt.figure(figsize=(14, 10))

        # PALETA DE COLORES MÁS DIFERENCIABLES
        # Usando colores con máxima separación en espacio HSV
        colors = [
            '#E63946',  # Rojo vibrante
            '#06FFA5',  # Verde neón
            '#4361EE',  # Azul eléctrico
            '#F77F00',  # Naranja brillante
            '#9D4EDD',  # Púrpura
            '#06D6A0',  # Verde agua
            '#FFB703',  # Amarillo dorado
            '#EF476F',  # Rosa fucsia
            '#118AB2',  # Azul océano
            '#8338EC',  # Violeta
        ]

        # Graficar puntos por cluster
        for cluster_id in range(self.kmeans.n_clusters):
            mask = self.clusters == cluster_id
            plt.scatter(X_pca[mask, 0], X_pca[mask, 1],
                        c=colors[cluster_id % len(colors)],
                        label=f'Cluster {cluster_id} ({np.sum(mask)} patentes)',
                        s=400, alpha=0.8, edgecolors='black', linewidth=2.5)

        # Añadir labels de patentes
        for i, patent_id in enumerate(self.patent_ids):
            plt.annotate(patent_id,
                         (X_pca[i, 0], X_pca[i, 1]),
                         fontsize=8, fontweight='bold',
                         ha='center', va='center',
                         color='white',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

        # Graficar centroides (X)
        centroids_pca = pca.transform(self.kmeans.cluster_centers_)
        plt.scatter(centroids_pca[:, 0], centroids_pca[:, 1],
                    marker='X', s=800, c='white',
                    edgecolors='black', linewidth=4,
                    label=' Centroides (centro de cada cluster)', zorder=10)

        # Añadir líneas desde patentes a sus centroides
        for cluster_id in range(self.kmeans.n_clusters):
            mask = self.clusters == cluster_id
            cluster_points = X_pca[mask]
            centroid = centroids_pca[cluster_id]

            for point in cluster_points:
                plt.plot([point[0], centroid[0]], [point[1], centroid[1]],
                         color=colors[cluster_id % len(colors)],
                         alpha=0.2, linewidth=1, linestyle='--')

        plt.xlabel(f'Componente Principal 1 ({pca.explained_variance_ratio_[0] * 100:.1f}% de varianza)',
                   fontsize=13, fontweight='bold')
        plt.ylabel(f'Componente Principal 2 ({pca.explained_variance_ratio_[1] * 100:.1f}% de varianza)',
                   fontsize=13, fontweight='bold')
        plt.title('K-Means Clustering de Patentes\n(Proyección 2D mediante PCA)',
                  fontsize=16, fontweight='bold', pad=20)

        # Leyenda mejorada
        plt.legend(fontsize=10, loc='best', framealpha=0.95, edgecolor='black', fancybox=True)
        plt.grid(True, alpha=0.3, linestyle=':', linewidth=1)

        # Añadir anotación explicativa
        plt.figtext(0.5, 0.02,
                    ' Centroides (X): Punto promedio de cada cluster | Líneas punteadas: Distancia al centroide',
                    ha='center', fontsize=10, style='italic',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))

        output_file = "data/results/visualizations/kmeans_clusters_pca.png"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ Visualización guardada: {output_file}")

        # Mostrar varianza explicada
        print(f"\n Varianza explicada por componentes principales:")
        print(f"  PC1 (eje X): {pca.explained_variance_ratio_[0] * 100:.2f}%")
        print(f"  PC2 (eje Y): {pca.explained_variance_ratio_[1] * 100:.2f}%")
        print(f"  Total capturado en 2D: {sum(pca.explained_variance_ratio_) * 100:.2f}%")
        print(f"\n Interpretación:")
        print(f"  • Puntos cercanos = patentes similares")
        print(f"  • X (centroides) = representante típico del cluster")
        print(f"  • Líneas punteadas = qué tan lejos está cada patente de su centroide")

    def analyze_cluster_characteristics(self):
        """Analiza las características de cada cluster"""
        if self.kmeans is None:
            print(" Primero debes entrenar el modelo")
            return

        print("\n" + "=" * 80)
        print("🔍 ANÁLISIS DE CARACTERÍSTICAS POR CLUSTER")
        print("=" * 80)

        for cluster_id in range(self.kmeans.n_clusters):
            print(f"\n{'─' * 80}")
            print(f" CLUSTER {cluster_id}")
            print('─' * 80)

            # Patentes en este cluster
            patents_in_cluster = [self.patent_ids[i] for i in range(len(self.patent_ids))
                                  if self.clusters[i] == cluster_id]

            print(f"\n Patentes ({len(patents_in_cluster)}):")
            for patent_id in patents_in_cluster:
                print(f"   • {patent_id}")

            # Características promedio del cluster
            cluster_features = self.feature_matrix[self.clusters == cluster_id]
            avg_features = np.mean(cluster_features, axis=0)

            print(f"\n Características promedio:")

            # Mostrar top 5 features más distintivas
            centroid = self.kmeans.cluster_centers_[cluster_id]

            # Calcular distancia de cada feature al promedio global
            global_mean = np.mean(self.feature_matrix, axis=0)
            feature_distinctiveness = np.abs(centroid - self.scaler.transform([global_mean])[0])

            top_features_idx = np.argsort(feature_distinctiveness)[-5:][::-1]

            print(f"\n   Top 5 características distintivas:")
            for idx in top_features_idx:
                feature_name = self.feature_names[idx]
                value = avg_features[idx]
                print(f"      • {feature_name}: {value:.2f}")

        print("\n" + "=" * 80)

    def save_results(self, output_file):
        """Guarda resultados del clustering"""
        if self.kmeans is None:
            print("❌ Primero debes entrenar el modelo")
            return

        results = {
            'n_clusters': self.kmeans.n_clusters,
            'inertia': float(self.kmeans.inertia_),
            'clusters': {}
        }

        for cluster_id in range(self.kmeans.n_clusters):
            patents_in_cluster = [self.patent_ids[i] for i in range(len(self.patent_ids))
                                  if self.clusters[i] == cluster_id]

            results['clusters'][f'cluster_{cluster_id}'] = {
                'patents': patents_in_cluster,
                'size': len(patents_in_cluster)
            }

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados guardados: {output_file}")


def main():
    """Función principal"""
    graph_file = "data/processed/graphs/pkg_complete.pkl"

    if not os.path.exists(graph_file):
        print("❌ No se encontró el archivo del grafo PKG")
        print(f"   Esperado: {graph_file}")
        return

    print("\n" + "=" * 80)
    print(" CLASIFICACIÓN DE PATENTES CON K-MEANS CLUSTERING")
    print("=" * 80)

    # Crear clasificador
    classifier = KMeansPatentClassifier(graph_file)

    # Extraer features
    classifier.extract_features()

    # Determinar K óptimo
    classifier.determine_optimal_k(max_k=min(len(classifier.patent_ids) - 1, 5))

    # Entrenar modelo (ajusta n_clusters según tus patentes)
    n_clusters = min(3, len(classifier.patent_ids) - 1)
    classifier.fit_kmeans(n_clusters=n_clusters)

    # Visualizar clusters
    try:
        classifier.visualize_clusters_pca()
    except Exception as e:
        print(f"⚠️  Error en visualización: {e}")

    # Analizar características
    classifier.analyze_cluster_characteristics()

    # Guardar resultados
    classifier.save_results("data/results/similarity/kmeans_results.json")

    print("\n Clustering completado!")


if __name__ == "__main__":
    main()