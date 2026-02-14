# Categorizacion de Patentes

Repositorio con **dos proyectos independientes** para trabajar con patentes de palas eólicas:

| Proyecto | Descripción | Ejecutable |
|----------|-------------|------------|
| **[clasificador_cpc/](clasificador_cpc/)** | Clasificación por **códigos CPC/IPC** (taxonomía temática) | `cd clasificador_cpc && python main.py` |
| **[analisis_rfsl/](analisis_rfsl/)** | Análisis por **RFSL** (entidades → grafo → similitud/clustering) | `cd analisis_rfsl && python main.py` |

Cada uno tiene su propio `main.py`, `requirements.txt` y `README.md`. Son independientes: puedes usar solo uno o ambos.

## Requisitos

- Python 3.8+
- Dependencias: instalar dentro de cada proyecto con `pip install -r requirements.txt`

## Uso rápido

**Clasificar patentes por códigos (CPC):**
```bash
cd clasificador_cpc
pip install -r requirements.txt
python main.py
```

**Análisis por texto (RFSL) y grafo:**
```bash
cd analisis_rfsl
pip install -r requirements.txt
python main.py
```

## Documentación de flujos

En **[FLUJOS.md](FLUJOS.md)** se explica en detalle cómo funciona cada enfoque (por códigos vs por RFSL).
