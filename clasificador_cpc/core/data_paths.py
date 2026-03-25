"""
Resolver de rutas de datos compartidas.

Objetivo: que `clasificador_cpc` use la carpeta `data/` del repo (raíz),
sin depender del directorio de ejecución actual.

Override opcional:
  - PATENTES_DATA_DIR=/ruta/a/data
"""

from __future__ import annotations

import os
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / ".git").exists():
            return p
    return start.parents[-1] if start.parents else start


def data_dir() -> Path:
    env = os.getenv("PATENTES_DATA_DIR")
    if env:
        return Path(env).expanduser().resolve()

    here = Path(__file__).resolve()
    root = _find_repo_root(here.parent)
    return (root / "data").resolve()


def data_path(*parts: str) -> str:
    """Devuelve una ruta absoluta (str) dentro de la carpeta data/ compartida."""
    return str(data_dir().joinpath(*parts))

