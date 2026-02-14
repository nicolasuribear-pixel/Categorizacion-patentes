# Clasificador de Patentes por Códigos CPC/IPC

Clasificación de patentes de palas eólicas usando los **códigos CPC/IPC** de la ficha de la patente (Google Patents) y una taxonomía propia.

## Instalación

```bash
cd clasificador_cpc
pip install -r requirements.txt
```

## Ejecución

Siempre desde la carpeta `clasificador_cpc`:

```bash
python main.py
```

Sin argumentos abre el menú interactivo. Con argumentos:

- `python main.py --help` — Ayuda
- `python main.py categorias` — Ver categorías disponibles
- `python main.py analizar` — Analizar una patente (pide ID)
- `python main.py csv ruta/patentes.csv` — Clasificar desde CSV
- `python main.py json ruta/patentes.json` — Clasificar desde JSON

## Estructura

- `core/` — Taxonomía CPC (`cpc_taxonomy.py`)
- `classification/` — Descarga, categorización y lotes
- `data/cache/` — Cache de patentes descargadas
- `data/results/` — Resultados de clasificación

## Flujo

1. Descarga la patente desde Google Patents (o usa cache).
2. Extrae los códigos IPC/CPC de la página.
3. Los compara con la taxonomía en `core/cpc_taxonomy.py`.
4. Asigna categorías (Perfil aerodinámico, Materiales, Control, etc.) con puntuación.
