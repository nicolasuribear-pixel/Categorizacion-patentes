# rfsl_extractor.py
"""
Extractor automático de entidades RFSL de patentes
Versión mejorada con mejor detección de Functions y Requirements
"""

import json
import re
import os
from core.domain_dictionaries import (
    STRUCTURES, FUNCTION_VERBS, FUNCTION_NOUNS,
    LOCATION_TERMS, REQUIREMENT_VERBS, TARGET_REQUIREMENTS,
    STOP_CAPTURES, DOMAIN_RELEVANCE_TERMS
)


# ═══════════════════════════════════════════════════════════════
# HELPERS DE FILTRADO DE CALIDAD
# ═══════════════════════════════════════════════════════════════

def _is_trivial_capture(capture: str) -> bool:
    """True si la captura es demasiado corta, vacía o solo stop-words."""
    if not capture:
        return True
    text = capture.strip().lower()
    if len(text) < 3:
        return True
    tokens = [t for t in re.split(r"\W+", text) if t]
    if not tokens:
        return True
    # Si TODAS las palabras son stop-captures → trivial.
    if all(t in STOP_CAPTURES for t in tokens):
        return True
    # Si no queda ningún token con más de 2 letras no-stop → trivial.
    meaningful = [t for t in tokens if t not in STOP_CAPTURES and len(t) > 2]
    if not meaningful:
        return True
    return False


def _is_domain_relevant(text: str) -> bool:
    """True si el texto contiene al menos un término del dominio."""
    if not text:
        return False
    lower = text.lower()
    return any(term in lower for term in DOMAIN_RELEVANCE_TERMS)


def _verb_regex(verb: str) -> str:
    """
    Devuelve un patrón regex que captura el verbo y sus conjugaciones
    regulares más comunes (-s, -es, -ed, -ing, -d), manejando el caso
    de verbos terminados en -e (generate → generating, reduce → reducing).
    """
    v = verb.lower()
    if v.endswith("e"):
        stem = re.escape(v[:-1])
        # generate, generates, generated, generating
        return rf"(?:\b{stem}e(?:s|d)?\b|\b{stem}ing\b)"
    # control, controls, controlled, controlling (doble consonante incluida)
    base = re.escape(v)
    return rf"\b{base}(?:s|es|ed|ing|led|ling|ped|ping|ted|ting|ned|ning)?\b"


class RFSLExtractor:
    """Extrae entidades RFSL de texto de patentes"""

    def __init__(self):
        self.structures = STRUCTURES
        self.function_verbs = FUNCTION_VERBS
        self.function_nouns = FUNCTION_NOUNS
        self.location_terms = LOCATION_TERMS
        self.requirement_verbs = REQUIREMENT_VERBS
        self.target_requirements = TARGET_REQUIREMENTS
        # Pre-computa los patrones de requisitos a partir de los verbos base,
        # manejando conjugaciones y limitando la captura a 3 palabras.
        self._requirement_patterns = [
            (
                verb,
                re.compile(
                    rf"{_verb_regex(verb)}\s+(?:the\s+|a\s+|an\s+)?"
                    rf"([a-zA-Z][\w-]*(?:\s+[a-zA-Z][\w-]*){{0,2}})",
                    re.IGNORECASE,
                ),
            )
            for verb in REQUIREMENT_VERBS
        ]

    def extract_structures(self, text):
        """Extrae estructuras (S) del texto"""
        text_lower = text.lower()
        found_structures = []

        for structure_type, variants in self.structures.items():
            for variant in variants:
                if variant.lower() in text_lower:
                    # Encontrar todas las posiciones
                    matches = re.finditer(re.escape(variant.lower()), text_lower)
                    for match in matches:
                        found_structures.append({
                            "entity": variant,
                            "type": "Structure",
                            "category": structure_type,
                            "position": match.start()
                        })

        # Eliminar duplicados por posición
        seen = set()
        unique_structures = []
        for s in found_structures:
            key = (s['entity'].lower(), s['position'])
            if key not in seen:
                seen.add(key)
                unique_structures.append(s)

        return unique_structures

    def extract_functions(self, text):
        """
        Extrae funciones (F) del texto.

        Se eliminó el antiguo "MÉTODO 2" que buscaba verbo + cualquier palabra:
        generaba falsos positivos tipo "reduce the blade", "control the one",
        etc. Ahora una función solo se considera válida si:
          (a) combina un verbo de FUNCTION_VERBS con un sustantivo de
              FUNCTION_NOUNS (match estricto verbo+noun específico), o
          (b) sigue un patrón funcional estándar de patentes (configured to…,
              adapted to…, etc.) y la captura es relevante al dominio.
        """
        text_lower = text.lower()
        found_functions = []

        # MÉTODO 1: verbo de FUNCTION_VERBS (conjugado) + noun de FUNCTION_NOUNS
        for verb_type, verbs in self.function_verbs.items():
            for verb in verbs:
                verb_pat = _verb_regex(verb)
                for noun in self.function_nouns:
                    # verbo (cualquier conjugación) + hasta 3 palabras + noun
                    pattern = (
                        rf"{verb_pat}\s+(?:\w+\s+){{0,3}}?"
                        rf"{re.escape(noun)}\b"
                    )
                    for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                        found_functions.append({
                            "entity": match.group().strip(),
                            "type": "Function",
                            "verb": verb,
                            "noun": noun,
                            "position": match.start(),
                            "method": "verb+noun"
                        })

        # MÉTODO 2: frases funcionales estándar de patentes
        # Se exige que la captura sea no-trivial y relevante al dominio.
        functional_phrases = [
            r"configured to\s+(\w+(?:\s+\w+){0,2})",
            r"adapted to\s+(\w+(?:\s+\w+){0,2})",
            r"designed to\s+(\w+(?:\s+\w+){0,2})",
            r"operable to\s+(\w+(?:\s+\w+){0,2})",
            r"capable of\s+(\w+ing(?:\s+\w+){0,2})",
            r"for\s+(\w+ing(?:\s+\w+){0,2})"
        ]

        for pattern in functional_phrases:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                capture = match.group(1).strip() if match.lastindex else ""
                if _is_trivial_capture(capture):
                    continue
                if not _is_domain_relevant(capture):
                    continue
                found_functions.append({
                    "entity": match.group().strip(),
                    "type": "Function",
                    "verb": "functional_phrase",
                    "noun": capture,
                    "position": match.start(),
                    "method": "phrase_pattern"
                })

        # Eliminar duplicados por (entidad normalizada, posición)
        seen = set()
        unique_functions = []
        for f in found_functions:
            key = (f['entity'].lower(), f['position'])
            if key not in seen:
                seen.add(key)
                unique_functions.append(f)

        return unique_functions

    def extract_locations(self, text):
        """Extrae ubicaciones (L) del texto"""
        text_lower = text.lower()
        found_locations = []

        for location_type, terms in self.location_terms.items():
            for term in terms:
                if term.lower() in text_lower:
                    matches = re.finditer(re.escape(term.lower()), text_lower)
                    for match in matches:
                        found_locations.append({
                            "entity": term,
                            "type": "Location",
                            "category": location_type,
                            "position": match.start()
                        })

        # Eliminar duplicados
        seen = set()
        unique_locations = []
        for l in found_locations:
            key = (l['entity'].lower(), l['position'])
            if key not in seen:
                seen.add(key)
                unique_locations.append(l)

        return unique_locations

    def extract_requirements(self, text):
        """
        Extrae requisitos (R) del texto.

        Filosofía (tras refactor):
          - Un requirement es un OBJETIVO DE DISEÑO concreto del dominio
            (reducir ruido, aumentar resistencia a fatiga, mitigar hielo,
            mejorar eficiencia aerodinámica, etc.), no un fragmento
            arbitrario del texto.
          - Se eliminaron los métodos que capturaban 100-140 caracteres
            de contexto alrededor de cualquier palabra genérica — eran
            el origen de los "requirements muy amplios".
          - Cada captura pasa filtros: no-trivial + relevante al dominio.

        Métodos conservados:
          1. Patrones explícitos verbo+objetivo (improve/reduce/…+hasta 3 palabras).
          2. Frases introductorias de objeto/finalidad de la invención
             (in order to…, the object of the invention is to…).
          3. Mapeo directo de TARGET_REQUIREMENTS: si aparece uno de los
             objetivos de diseño canónicos (aerodynamic efficiency, fatigue
             life, ice accretion, etc.), se registra como requirement con
             su categoría asociada.
        """
        found_requirements = []

        # MÉTODO 1: patrones explícitos "verbo (conjugado) + hasta 3 palabras".
        for req_type, pattern in self._requirement_patterns:
            for match in pattern.finditer(text):
                capture = match.group(1).strip() if match.lastindex else ""
                if _is_trivial_capture(capture):
                    continue
                # Solo aceptamos si la captura contiene algo del dominio
                if not _is_domain_relevant(capture):
                    continue
                requirement_text = f"{req_type} {capture}".strip().lower()
                found_requirements.append({
                    "entity": requirement_text,
                    "type": "Requirement",
                    "action": req_type,
                    "position": match.start(),
                    "method": "explicit_pattern"
                })

        # MÉTODO 2: frases introductorias de objetivo/finalidad
        # (típicas del apartado "DISCLOSURE OF THE INVENTION").
        # Captura acotada a 15-80 chars para evitar fragmentos enormes.
        requirement_intro_patterns = [
            r"(?:the\s+)?(?:primary\s+|main\s+)?(?:object|objective|purpose|aim)"
            r"\s+(?:of\s+(?:the\s+)?(?:invention|disclosure))?\s*(?:is|includes)"
            r"(?:\s+to)?\s+(.{15,80}?)(?:\.|,|;)",
            r"(?:it is|there is)\s+(?:a|an)\s+(?:need|desire|requirement)"
            r"\s+(?:for|to)\s+(.{15,80}?)(?:\.|,|;)",
            r"\bin order to\s+(.{15,80}?)(?:\.|,|;)",
            r"\bso as to\s+(.{15,80}?)(?:\.|,|;)"
        ]
        for pattern in requirement_intro_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                capture = match.group(1).strip() if match.lastindex else ""
                if _is_trivial_capture(capture):
                    continue
                if not _is_domain_relevant(capture):
                    continue
                found_requirements.append({
                    "entity": capture.lower(),
                    "type": "Requirement",
                    "action": "intro_phrase",
                    "position": match.start(),
                    "method": "intro_pattern"
                })

        # MÉTODO 3: mapeo directo a TARGET_REQUIREMENTS
        # Si aparece textualmente uno de los objetivos canónicos,
        # se registra con su categoría. Sin captura de contexto.
        text_lower = text.lower()
        for req_category, keywords in self.target_requirements.items():
            for keyword in keywords:
                kw = keyword.lower()
                for match in re.finditer(rf"\b{re.escape(kw)}\b", text_lower):
                    found_requirements.append({
                        "entity": kw,
                        "type": "Requirement",
                        "action": req_category,
                        "position": match.start(),
                        "method": "target_keyword"
                    })

        # Eliminar duplicados por (entidad normalizada, acción).
        # Ya NO se usan primeros 40 chars como clave (era demasiado laxo
        # y colapsaba requirements distintos que empezaban igual).
        seen = set()
        unique_requirements = []
        for r in found_requirements:
            key = (r["entity"].strip().lower(), r["action"])
            if key not in seen:
                seen.add(key)
                unique_requirements.append(r)

        return unique_requirements

    def extract_from_patent(self, patent_data):
        """
        Extrae todas las entidades RFSL de una patente completa

        Args:
            patent_data: diccionario con datos de la patente

        Returns:
            diccionario con entidades organizadas por tipo
        """
        # Concatenar texto relevante
        text_sources = {
            "title": patent_data.get("title", ""),
            "abstract": patent_data.get("abstract", ""),
            "claims": " ".join(patent_data.get("claims", [])),
            "description": patent_data.get("description", "")[:10000]  # Primeros 10000 chars
        }

        full_text = " ".join(text_sources.values())

        # Extraer entidades sobre el texto completo (abstract+title+claims+description).
        # Antes extract_requirements se limitaba a abstract+title, lo que dejaba fuera
        # los objetivos de la invención que suelen estar en la descripción
        # ("DISCLOSURE OF THE INVENTION", "BACKGROUND", etc.).
        entities = {
            "R": self.extract_requirements(full_text),
            "F": self.extract_functions(full_text),
            "S": self.extract_structures(full_text),
            "L": self.extract_locations(full_text)
        }

        # Estadísticas
        stats = {
            "total_entities": sum(len(v) for v in entities.values()),
            "R_count": len(entities["R"]),
            "F_count": len(entities["F"]),
            "S_count": len(entities["S"]),
            "L_count": len(entities["L"])
        }

        return {
            "patent_id": patent_data.get("patent_id"),
            "entities": entities,
            "stats": stats,
            "text_sources": {k: len(v) for k, v in text_sources.items()}
        }

    def save_results(self, results, output_file):
        """Guarda resultados en JSON"""
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Resultados guardados: {output_file}")


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def procesar_patente(patent_file, output_dir="data/processed/rfsl"):
    """Procesa una patente y extrae entidades RFSL"""
    print(f"\n{'=' * 60}")
    print(f"📄 Procesando: {os.path.basename(patent_file)}")
    print('=' * 60)

    # Cargar patente
    with open(patent_file, 'r', encoding='utf-8') as f:
        patent_data = json.load(f)

    # Crear extractor
    extractor = RFSLExtractor()

    # Extraer entidades
    results = extractor.extract_from_patent(patent_data)

    # Mostrar resumen
    print(f"\n📊 RESUMEN DE EXTRACCIÓN:")
    print(f"   Patent ID: {results['patent_id']}")
    print(f"   Total entidades: {results['stats']['total_entities']}")
    print(f"   • Requirements (R): {results['stats']['R_count']}")
    print(f"   • Functions (F): {results['stats']['F_count']}")
    print(f"   • Structures (S): {results['stats']['S_count']}")
    print(f"   • Locations (L): {results['stats']['L_count']}")

    # Mostrar ejemplos
    print(f"\n🔍 EJEMPLOS DE ENTIDADES ENCONTRADAS:")

    if results['entities']['R']:
        print(f"\n   Requirements (primeros 3):")
        for r in results['entities']['R'][:3]:
            print(f"      • {r['entity'][:80]}..." if len(r['entity']) > 80 else f"      • {r['entity']}")

    if results['entities']['F']:
        print(f"\n   Functions (primeras 5):")
        for f in results['entities']['F'][:5]:
            print(f"      • {f['entity']}")

    if results['entities']['S']:
        print(f"\n   Structures (primeras 5):")
        for s in results['entities']['S'][:5]:
            print(f"      • {s['entity']} ({s['category']})")

    if results['entities']['L']:
        print(f"\n   Locations (primeras 3):")
        for l in results['entities']['L'][:3]:
            print(f"      • {l['entity']} ({l['category']})")

    # Guardar resultados
    patent_id = results['patent_id']
    output_file = os.path.join(output_dir, f"{patent_id}_rfsl.json")
    extractor.save_results(results, output_file)

    return results


# ═══════════════════════════════════════════════════════════════
# PROCESAR TODAS LAS PATENTES
# ═══════════════════════════════════════════════════════════════

def procesar_todas_las_patentes():
    """Procesa todas las patentes descargadas"""
    patents_dir = "data/raw/patents"
    output_dir = "data/processed/rfsl"

    if not os.path.exists(patents_dir):
        print("❌ No existe la carpeta de patentes")
        print(f"   Esperada: {patents_dir}")
        return

    # Obtener lista de patentes
    patent_files = [
        os.path.join(patents_dir, f)
        for f in os.listdir(patents_dir)
        if f.endswith('.json') and not f.endswith('_rfsl.json')
    ]

    if not patent_files:
        print(f"❌ No se encontraron patentes en {patents_dir}")
        print("   Ejecuta antes: python main.py → opción 2 (Descargar patentes)")
        return

    print(f"\n{'=' * 60}")
    print(f"🚀 PROCESANDO {len(patent_files)} PATENTES")
    print('=' * 60)

    resultados_totales = []

    for patent_file in patent_files:
        try:
            results = procesar_patente(patent_file, output_dir)
            resultados_totales.append(results)
        except Exception as e:
            print(f"❌ Error procesando {patent_file}: {e}")
            import traceback
            traceback.print_exc()

    # Resumen global
    print(f"\n{'=' * 60}")
    print("📊 RESUMEN GLOBAL")
    print('=' * 60)
    print(f"Patentes procesadas exitosamente: {len(resultados_totales)}/{len(patent_files)}")

    if resultados_totales:
        total_R = sum(r['stats']['R_count'] for r in resultados_totales)
        total_F = sum(r['stats']['F_count'] for r in resultados_totales)
        total_S = sum(r['stats']['S_count'] for r in resultados_totales)
        total_L = sum(r['stats']['L_count'] for r in resultados_totales)

        print(f"\nEntidades totales extraídas:")
        print(f"   • Requirements (R): {total_R}")
        print(f"   • Functions (F): {total_F}")
        print(f"   • Structures (S): {total_S}")
        print(f"   • Locations (L): {total_L}")
        print(f"   {'─' * 30}")
        print(f"   TOTAL: {total_R + total_F + total_S + total_L}")

        print(f"\n✅ Resultados guardados en: {output_dir}/")
        print(f"   Formato: [PATENT_ID]_rfsl.json")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔬 EXTRACTOR DE ENTIDADES RFSL - VERSIÓN MEJORADA")
    print("=" * 60)
    procesar_todas_las_patentes()