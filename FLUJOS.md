# Cómo funciona el sistema: dos enfoques

El proyecto permite analizar patentes de palas eólicas de **dos maneras**:

1. **Por códigos CPC/IPC** → clasificación según la taxonomía oficial.
2. **Por RFSL** → extracción de entidades del texto y grafo de conocimiento (similitud y clustering).

---

## 1. Flujo por códigos CPC/IPC

**Objetivo:** Asignar a cada patente una o varias categorías temáticas (perfil aerodinámico, materiales, control, etc.) usando los **códigos de clasificación** que ya trae la patente en Google Patents.

### Resumen del flujo

```
Patente (ID o CSV/JSON)
    → Descarga desde Google Patents (o cache)
    → Extracción de códigos IPC/CPC de la página
    → Comparación con taxonomía (core/cpc_taxonomy.py)
    → Categorías asignadas + scores
```

### Paso a paso

| Paso | Dónde | Qué hace |
|------|--------|----------|
| 1 | `classification/patent_categorizer.py` | **Descarga** la patente desde Google Patents (o lee de `data/cache/`). Del HTML extrae título, abstract, claims, descripción y, sobre todo, **todos los códigos IPC/CPC** (etiquetas `<span itemprop="Code">`). |
| 2 | `core/cpc_taxonomy.py` | **Taxonomía**: diccionario que mapea cada código CPC/IPC relevante a una categoría de palas eólicas (ej. `F03D1/0633` → "Perfil Aerodinámico"). Cada código tiene un peso. |
| 3 | `patent_categorizer.categorize_patent()` | Junta `ipc_codes` y `cpc_codes` de la patente, normaliza y llama a `categorize_patent_codes()`. Suma los pesos por categoría y ordena por score. |
| 4 | Salida | Un dict con `categorias` (nombre, score, códigos que matchearon), `categoria_principal`, etc. Se puede guardar en `data/results/`. |

### Qué entra y qué sale

- **Entrada:** ID de patente (ej. `US8550777B2`), o lista/CSV/JSON de IDs.
- **Salida:** Categorías temáticas (Perfil Aerodinámico, Materiales, Control y Ajuste, etc.) con puntuación y lista de códigos que las sustentan.

### Cómo ejecutarlo

Desde la carpeta **`clasificador_cpc/`** (proyecto independiente):

```bash
cd clasificador_cpc
python main.py
```

Luego: menú interactivo, o `python main.py categorias`, `python main.py analizar`, `python main.py csv datos/patentes.csv`, etc.

**Archivos clave:** `core/cpc_taxonomy.py`, `classification/patent_categorizer.py`, `classification/batch_classifier.py`, `main.py`.

---

## 2. Flujo por RFSL (Requirements, Functions, Structures, Locations)

**Objetivo:** No usar códigos, sino el **texto** de la patente. Se extraen entidades RFSL, se construye un **grafo de conocimiento (PKG)** y sobre ese grafo se hace **similitud entre patentes** o **clustering (K-Means)**.

### Resumen del flujo

```
Patentes en JSON (data/raw/patents)
    → Extracción RFSL (título, abstract, claims, descripción)
    → Archivos *_rfsl.json (data/processed/rfsl)
    → Construcción del grafo PKG (nodos = entidades, aristas = relaciones)
    → data/processed/graphs/pkg_complete.pkl
    → Similitud entre patentes O clustering K-Means
```

### Qué es RFSL

- **R**equirements: requisitos o problemas que la patente aborda (ej. “reduce noise”, “improve efficiency”).
- **F**unctions: acciones o funciones técnicas (ej. “increase lift”, “support load”).
- **S**tructures: componentes físicos (blade, spar, skin, leading edge, etc.).
- **L**ocations: ubicaciones en el aspa (at the root, trailing edge, pressure side, etc.).

Los diccionarios que guían la extracción están en **`core/domain_dictionaries.py`** (STRUCTURES, FUNCTION_VERBS, FUNCTION_NOUNS, LOCATION_TERMS, REQUIREMENT_PATTERNS, etc.).

### Paso a paso

| Paso | Módulo | Qué hace |
|------|--------|----------|
| 1 | `scripts/Google.py` | Descarga patentes y guarda JSON en `data/raw/patents/`. (Opcional: puedes tener ya los JSON por otro medio.) |
| 2 | `knowledge_graph/rfsl_extractor.py` | Lee cada JSON de patente, concatena título, abstract, claims y descripción. Con regex y diccionarios extrae entidades **R, F, S, L** y guarda un JSON por patente en `data/processed/rfsl/` (ej. `US8550777B2_rfsl.json`). |
| 3 | `knowledge_graph/pkg_builder.py` | Lee todos los `*_rfsl.json`, crea un **grafo dirigido** (NetworkX): nodos = entidades (con tipo R/F/S/L y patent_id), aristas = relaciones por **proximidad en el texto** (R→F “addresses”, F→S “uses”, S→L “located_at”, F→L “occurs_at”). Guarda el grafo en `data/processed/graphs/pkg_complete.pkl` (y opcionalmente JSON). |
| 4a | `knowledge_graph/similarity_analyzer.py` | Carga el PKG (.pkl), para cada patente extrae su subgrafo. Calcula **similitud entre pares** (Jaccard en entidades, coseno en vectores de tipos, similitud estructural). Lista patentes similares a una dada. |
| 4b | `knowledge_graph/kmeans_classifier.py` | Carga el PKG, extrae **features** por patente (conteos R/F/S/L, ratios, aristas por tipo, densidad, etc.), aplica **K-Means** (y opcionalmente PCA) y agrupa patentes sin etiquetas previas. |

### Qué entra y qué sale (por etapa)

- **RFSL:** Entrada = JSON de patentes (con title, abstract, claims, description). Salida = `*_rfsl.json` con entidades y conteos.
- **PKG:** Entrada = todos los `*_rfsl.json`. Salida = grafo único `pkg_complete.pkl`.
- **Similitud:** Entrada = PKG. Salida = rankings de patentes similares y/o reportes guardados.
- **K-Means:** Entrada = PKG. Salida = clusters asignados y visualizaciones (ej. PCA).

### Cómo ejecutarlo

Desde la carpeta **`analisis_rfsl/`** (proyecto independiente):

```bash
cd analisis_rfsl
python main.py
```

Menú: 1) Crear estructura, 2) Descargar patentes, 3) Extraer RFSL, 4) Construir PKG, 5) Similitud, 6) K-Means. Orden recomendado la primera vez: 1 → 2 → 3 → 4, luego 5 o 6.

**Archivos clave:** `core/domain_dictionaries.py`, `knowledge_graph/rfsl_extractor.py`, `knowledge_graph/pkg_builder.py`, `similarity_analyzer.py`, `kmeans_classifier.py`, `main.py`.

---

## Comparación rápida

| | Por códigos CPC/IPC | Por RFSL |
|---|---------------------|----------|
| **Fuente de información** | Códigos IPC/CPC de la ficha de la patente | Texto (título, abstract, claims, descripción) |
| **Lógica** | Mapear códigos a categorías de la taxonomía | Extraer entidades RFSL → grafo → similitud/clustering |
| **Salida típica** | Categorías temáticas con score (ej. “Perfil aerodinámico 2.5”) | Similitud entre patentes o grupos (clusters) |
| **Entrada** | ID(s) de patente (descarga o cache) | JSON de patentes en `data/raw/patents` (previo paso Google.py o manual) |
| **Dependencias de datos** | Solo descarga/cache por patente | Pipeline: raw → RFSL → PKG; similitud/K-Means usan el PKG |

Los dos enfoques son **complementarios**: códigos para clasificación temática estándar, RFSL para análisis basado en el contenido textual y en el grafo de conocimiento.
