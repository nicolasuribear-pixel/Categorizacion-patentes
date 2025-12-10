import os
import json


def crear_estructura_carpetas():
    carpetas = [
        'data/raw/patents',
        'data/raw/images',
        'data/processed',
        'models',
        'results',
        'logs'
    ]

    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
        print(f"✓ Creada: {carpeta}")

def crear_plantilla_patent():
    patent_template = {
        "patent_id": "",
        "title": "",
        "abstract": "",
        "claims": [],
        "description": "",
        "images": [],
        "ipc_codes": [],
        "grant_date": "",
        "inventors": [],
        "assignee": ""  # Empresa/organización
    }


    with open('data/patent_template.json', 'w', encoding='utf-8') as f:
        json.dump(patent_template, f, indent=2, ensure_ascii=False)

    print("✓ Plantilla creada: data/patent_template.json")
    return patent_template



if __name__ == "__main__":
    crear_estructura_carpetas()
    crear_plantilla_patent()