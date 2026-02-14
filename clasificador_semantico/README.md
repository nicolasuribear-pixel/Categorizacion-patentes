# Análisis de Patentes por RFSL

Análisis de patentes de palas eólicas mediante extracción de entidades **RFSL** (Requirements, Functions, Structures, Locations), construcción de un **grafo de conocimiento (PKG)** y análisis de similitud o clustering.

## Instalación

```bash
cd clasificador_sematico
pip install -r requirements.txt
```

## Ejecución

Siempre desde la carpeta `clasificador_sematico`:

```bash
python main.py
```

Menú:

1. **Crear estructura de carpetas** — Crea `data/raw`, `data/processed`, etc.
2. **Descargar patentes** — Descarga desde Google Patents a `data/raw/patents`.
3. **Extraer entidades RFSL** — Lee patentes en JSON y genera `data/processed/rfsl/*_rfsl.json`.
4. **Construir grafo PKG** — Construye el grafo y guarda `data/processed/graphs/pkg_complete.pkl`.
5. **Análisis de similitud** — Compara patentes usando el PKG.
6. **Clustering K-Means** — Agrupa patentes sin etiquetas usando el PKG.

Orden recomendado la primera vez: 1 → 2 → 3 → 4, luego 5 o 6 según necesites.

## Estructura

- `core/` — Diccionarios de dominio (`domain_dictionaries.py`) para RFSL
- `knowledge_graph/` — Extractor RFSL, constructor PKG, similitud, K-Means
- `scripts/` — Estructura de carpetas y descarga desde Google
- `data/raw/patents/` — Patentes en JSON
- `data/processed/rfsl/` — Salida del extractor RFSL
- `data/processed/graphs/` — Grafo PKG (`.pkl`, `.json`)
- `data/results/` — Resultados de similitud y clustering

## Flujo

1. Descargar patentes (opción 2) o colocar JSON en `data/raw/patents/`.
2. Extraer RFSL (opción 3): entidades R, F, S, L del texto.
3. Construir PKG (opción 4): grafo con nodos entidades y aristas por proximidad.
4. Similitud (opción 5) o K-Means (opción 6) usando el grafo.
