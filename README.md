# Categorizacion de Patentes

Sistema para la categorizacion y analisis de patentes.

## Requisitos

- Python 3.8 o superior
- Git

## Instalacion

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/Categorizacion-patentes.git
cd Categorizacion-patentes
```

### 2. Crear el entorno virtual

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la estructura de carpetas

Ejecutar el script `Estructura.py` para generar la estructura de directorios necesaria y la plantilla de patentes:

```bash
python Estructura.py
```

Este script creara las siguientes carpetas:

- `data/raw/patents` - Patentes en formato raw
- `data/raw/images` - Imagenes asociadas a las patentes
- `data/processed` - Datos procesados
- `models` - Modelos entrenados
- `results` - Resultados del analisis
- `logs` - Archivos de registro

Ademas, generara el archivo `data/patent_template.json` con la plantilla base para las patentes.

## Estructura del Proyecto

```
Categorizacion-patentes/
├── data/
│   ├── raw/
│   │   ├── patents/
│   │   └── images/
│   ├── processed/
│   └── patent_template.json
├── models/
├── results/
├── logs/
├── Estructura.py
├── requirements.txt
└── ...
```
