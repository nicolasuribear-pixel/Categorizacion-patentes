# rfsl_extractor.py
"""
Extractor automático de entidades RFSL de patentes
Versión mejorada con mejor detección de Functions y Requirements
"""

import json
import re
import os
from domain_dictionaries import (
    STRUCTURES, FUNCTION_VERBS, FUNCTION_NOUNS,
    LOCATION_TERMS, REQUIREMENT_PATTERNS, TARGET_REQUIREMENTS
)


class RFSLExtractor:
    """Extrae entidades RFSL de texto de patentes"""

    def __init__(self):
        self.structures = STRUCTURES
        self.function_verbs = FUNCTION_VERBS
        self.function_nouns = FUNCTION_NOUNS
        self.location_terms = LOCATION_TERMS
        self.requirement_patterns = REQUIREMENT_PATTERNS
        self.target_requirements = TARGET_REQUIREMENTS

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
        """Extrae funciones (F) del texto - VERSIÓN MEJORADA"""
        text_lower = text.lower()
        found_functions = []

        # MÉTODO 1: Buscar combinaciones verbo + sustantivo
        for verb_type, verbs in self.function_verbs.items():
            for verb in verbs:
                for noun in self.function_nouns:
                    # Patrón más flexible: verbo + palabras opcionales + sustantivo
                    pattern = rf"\b{re.escape(verb)}\s+(?:\w+\s+){{0,3}}?{re.escape(noun)}\b"
                    matches = re.finditer(pattern, text_lower, re.IGNORECASE)

                    for match in matches:
                        found_functions.append({
                            "entity": match.group().strip(),
                            "type": "Function",
                            "verb": verb,
                            "noun": noun,
                            "position": match.start(),
                            "method": "verb+noun"
                        })

        # MÉTODO 2: Buscar verbos solos cerca de sustantivos técnicos
        for verb_type, verbs in self.function_verbs.items():
            for verb in verbs:
                # Buscar el verbo seguido de cualquier palabra técnica
                pattern = rf"\b{re.escape(verb)}\s+(?:the\s+|a\s+)?(\w+(?:\s+\w+){{0,2}})"
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)

                for match in matches:
                    found_functions.append({
                        "entity": match.group().strip(),
                        "type": "Function",
                        "verb": verb,
                        "noun": match.group(1),
                        "position": match.start(),
                        "method": "verb_flexible"
                    })

        # MÉTODO 3: Buscar frases funcionales comunes
        functional_phrases = [
            r"configured to\s+(\w+(?:\s+\w+){0,2})",
            r"adapted to\s+(\w+(?:\s+\w+){0,2})",
            r"designed to\s+(\w+(?:\s+\w+){0,2})",
            r"operable to\s+(\w+(?:\s+\w+){0,2})",
            r"capable of\s+(\w+(?:\s+\w+){0,2})",
            r"for\s+(\w+ing(?:\s+\w+){0,2})"
        ]

        for pattern in functional_phrases:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                found_functions.append({
                    "entity": match.group().strip(),
                    "type": "Function",
                    "verb": "functional_phrase",
                    "noun": match.group(1),
                    "position": match.start(),
                    "method": "phrase_pattern"
                })

        # Eliminar duplicados
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
        """Extrae requisitos (R) del texto - VERSIÓN MEJORADA V3"""
        found_requirements = []
        text_lower = text.lower()

        # MÉTODO 1: Patrones de requisitos explícitos
        for req_type, patterns in self.requirement_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    requirement_text = match.group().strip()
                    found_requirements.append({
                        "entity": requirement_text,
                        "type": "Requirement",
                        "action": req_type,
                        "position": match.start(),
                        "method": "explicit_pattern"
                    })

        # MÉTODO 2: Frases introductorias de requisitos
        requirement_intro_patterns = [
            r"(?:the |a |an )?(?:present )?(?:invention|disclosure|method|system|apparatus) (?:provides|relates to|is directed to|concerns|addresses|describes|includes)\s+(.{15,120}?)(?:\.|,|;)",
            r"(?:the |a |an )?(?:primary |main )?(?:object|objective|purpose|goal|aim) (?:is|of|includes)(?:\s+to)?\s+(.{15,120}?)(?:\.|,|;)",
            r"(?:it is|there is) (?:a|an) (?:need|desire|requirement) (?:for|to)\s+(.{15,120}?)(?:\.|,|;)",
            r"in order to\s+(.{15,100}?)(?:\.|,|;)",
            r"so as to\s+(.{15,100}?)(?:\.|,|;)",
            r"configured to\s+(.{15,100}?)(?:\.|,|;)",
            r"adapted to\s+(.{15,100}?)(?:\.|,|;)",
            r"designed to\s+(.{15,100}?)(?:\.|,|;)"
        ]

        for pattern in requirement_intro_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                requirement_text = match.group(1).strip() if match.lastindex >= 1 else match.group(0).strip()
                found_requirements.append({
                    "entity": requirement_text,
                    "type": "Requirement",
                    "action": "intro_phrase",
                    "position": match.start(),
                    "method": "intro_pattern"
                })

        # MÉTODO 3: Requisitos implícitos - verbos de acción técnicos
        implicit_requirement_patterns = [
            r"(?:method|system|apparatus|device) (?:for|to)\s+(\w+ing\s+.{10,80}?)(?:\.|,|;)",
            r"(?:includes|comprises|has)\s+(\w+ing\s+.{10,80}?)(?:\.|,|;)",
            r"(?:determining|measuring|controlling|providing|calculating|monitoring|adjusting|optimizing)\s+(.{10,80}?)(?:\.|,|;)"
        ]

        for pattern in implicit_requirement_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                requirement_text = match.group(1).strip() if match.lastindex >= 1 else match.group(0).strip()
                found_requirements.append({
                    "entity": requirement_text,
                    "type": "Requirement",
                    "action": "implicit_action",
                    "position": match.start(),
                    "method": "implicit_pattern"
                })

        # MÉTODO 4: Palabras clave de mejora en contexto
        improvement_keywords = [
            "improve", "increase", "reduce", "minimize", "maximize", "enhance",
            "optimize", "control", "prevent", "avoid", "eliminate", "mitigate"
        ]

        for keyword in improvement_keywords:
            pattern = rf"\b{keyword}\w*\s+(?:the\s+)?(.{{10,60}}?)(?:\.|,|;|\s+of|\s+by)"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                requirement_text = f"{keyword} {match.group(1).strip()}"
                found_requirements.append({
                    "entity": requirement_text,
                    "type": "Requirement",
                    "action": keyword,
                    "position": match.start(),
                    "method": "improvement_keyword"
                })

        # MÉTODO 5: Buscar palabras objetivo en todo el texto (no solo primeros 500 chars)
        for req_category, keywords in self.target_requirements.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    # Buscar contexto más amplio alrededor de la palabra
                    keyword_pattern = rf".{{0,70}}{re.escape(keyword.lower())}.{{0,70}}"
                    matches = re.finditer(keyword_pattern, text_lower)
                    for match in matches:
                        context = match.group().strip()
                        # Verificar que hay verbos de acción cerca
                        if any(verb in context for verb in
                               ["improve", "increase", "reduce", "control", "optimize", "enhance"]):
                            found_requirements.append({
                                "entity": context,
                                "type": "Requirement",
                                "action": req_category,
                                "position": match.start(),
                                "method": "target_keyword_context"
                            })

        # Eliminar duplicados (más agresivo)
        seen = set()
        unique_requirements = []
        for r in found_requirements:
            # Normalizar el texto para comparación
            normalized = r['entity'].lower().strip()
            # Usar primeros 40 caracteres como clave
            key = normalized[:40]
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

        # Extraer entidades
        entities = {
            "R": self.extract_requirements(text_sources["abstract"] + " " + text_sources["title"]),
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
        print("   Asegúrate de haber ejecutado Google.py primero")
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