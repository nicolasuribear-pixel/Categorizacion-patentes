
import requests
from bs4 import BeautifulSoup
import json
import time
import re


def descargar_patent_google(patent_id):

    url = f"https://patents.google.com/patent/{patent_id}/en"

    print(f"Descargando: {patent_id}")
    print(f"URL: {url}")

    try:

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"❌ Error: Status code {response.status_code}")
            return None


        soup = BeautifulSoup(response.content, 'html.parser')


        patent_data = {
            "patent_id": patent_id,
            "title": "",
            "abstract": "",
            "claims": [],
            "description": "",
            "images": [],
            "ipc_codes": []
        }


        title_tag = soup.find('meta', {'name': 'DC.title'})
        if title_tag:
            patent_data["title"] = title_tag.get('content', '')
            print(f"  ✓ Título: {patent_data['title'][:50]}...")


        abstract_tag = soup.find('meta', {'name': 'DC.description'})
        if abstract_tag:
            patent_data["abstract"] = abstract_tag.get('content', '')
            print(f"  ✓ Abstract: {len(patent_data['abstract'])} caracteres")


        claims_section = soup.find('section', {'itemprop': 'claims'})
        if claims_section:
            # Buscar todos los divs de claims
            claim_divs = claims_section.find_all('div', {'class': 'claim'})
            for claim_div in claim_divs:
                # Número del claim
                claim_num = claim_div.find('div', {'class': 'claim-number'})
                # Texto del claim
                claim_text = claim_div.find('div', {'class': 'claim-text'})

                if claim_text:
                    text = claim_text.get_text(strip=True)
                    patent_data["claims"].append(text)

            print(f"  ✓ Claims: {len(patent_data['claims'])} encontrados")


        description_section = soup.find('section', {'itemprop': 'description'})
        if description_section:
            patent_data["description"] = description_section.get_text(strip=True)
            print(f"  ✓ Descripción: {len(patent_data['description'])} caracteres")

        # CÓDIGO CORREGIDO
        figures = soup.find_all('meta', {'itemprop': 'full'})
        for idx, fig in enumerate(figures):
            img_url = fig.get('content', '')
            if img_url:
                # Asegurar que la URL sea completa
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url

                patent_data["images"].append({
                    "figure_num": idx + 1,
                    "url": img_url,
                })
        print(f"  ✓ Imágenes: {len(patent_data['images'])} encontradas")


        ipc_section = soup.find_all('span', {'itemprop': 'Code'})
        for ipc in ipc_section:
            code = ipc.get_text(strip=True)
            if code:
                patent_data["ipc_codes"].append(code)

        print(f"  ✓ IPC: {patent_data['ipc_codes']}")

        return patent_data

    except Exception as e:
        print(f"❌ Error descargando {patent_id}: {str(e)}")
        return None


def guardar_patent(patent_data, directorio='data/raw/patents'):
    """Guarda datos de patente en JSON"""
    if not patent_data:
        return False

    filename = f"{directorio}/{patent_data['patent_id']}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(patent_data, f, indent=2, ensure_ascii=False)

    print(f" Guardado: {filename}\n")
    return True


def descargar_lista_patents(patent_ids, delay=0.5):

    resultados = {
        "exitosas": 0,
        "fallidas": 0,
        "patents": []
    }

    for idx, patent_id in enumerate(patent_ids, 1):
        print(f"\n[{idx}/{len(patent_ids)}] Procesando {patent_id}")
        print("=" * 60)

        patent_data = descargar_patent_google(patent_id)

        if patent_data:
            if guardar_patent(patent_data):
                resultados["exitosas"] += 1
                resultados["patents"].append(patent_id)
        else:
            resultados["fallidas"] += 1


        if idx < len(patent_ids):
            print(f" Esperando {delay} segundos...")
            time.sleep(delay)


    print("\n" + "=" * 60)
    print("RESUMEN DE DESCARGA")
    print("=" * 60)
    print(f" Exitosas: {resultados['exitosas']}")
    print(f" Fallidas: {resultados['fallidas']}")
    print(f" Total: {len(patent_ids)}")


    with open('logs/descarga_log.json', 'w') as f:
        json.dump(resultados, f, indent=2)

    return resultados



if __name__ == "__main__":

    patents_to_download = [
        "US8550777B2",
        "US8936435B2",
        "US8834130B2",
        "US8932024B2",
        "US10400744B2",
        "US9581133B2",
        "US7927078B2",
        "CN113982840A",
        "US7927070B2",
        "CN107110110B",
]

    print(" Iniciando descarga de patentes desde Google Patents")
    print(f"Total a descargar: {len(patents_to_download)}")
    print("=" * 60 + "\n")

    resultados = descargar_lista_patents(patents_to_download, delay=3)

    print("\n Proceso completado!")
    print(" Revisa la carpeta 'data/raw/patents' para ver los archivos JSON")