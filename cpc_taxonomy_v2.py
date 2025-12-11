# cpc_taxonomy_v2.py
"""
Taxonomía CPC/IPC v2.0 para Clasificación de Patentes de Palas Eólicas
Organizada por características MORFOLÓGICAS y FUNCIONALES
Basada en análisis empírico de 30 patentes reales
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TAXONOMÍA PRINCIPAL - 7 CATEGORÍAS MORFOLÓGICAS
# ═══════════════════════════════════════════════════════════════════════════════

CPC_TAXONOMY = {
    
    # ───────────────────────────────────────────────────────────────────────────
    # 1. PERFIL AERODINÁMICO
    # Características relacionadas con la forma aerodinámica de la pala
    # ───────────────────────────────────────────────────────────────────────────
    "aerodinamico": {
        "nombre": "Perfil Aerodinámico",
        "descripcion": "Forma aerodinámica, perfiles de sustentación, winglets y optimización de flujo",
        "palabras_clave": [
            "aerodynamic", "airfoil", "profile", "lift", "drag", "flow",
            "shape", "winglet", "tip", "leading edge", "trailing edge"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS (peso 1.0) - Alta especificidad ===
            "F03D1/0608": {"descripcion": "Aerodynamic shape of rotor", "peso": 1.0},
            "F03D1/0633": {"descripcion": "Aerodynamic shape of blades", "peso": 1.0},
            "F03D1/0641": {"descripcion": "Aerodynamic profile (section)", "peso": 1.0},
            "F03D1/06": {"descripcion": "Rotors with aerodynamic shape", "peso": 1.0},
            "F05B2240/301": {"descripcion": "Cross-section characteristics", "peso": 1.0},
            "F05B2240/303": {"descripcion": "Leading edge details", "peso": 1.0},
            "F05B2240/304": {"descripcion": "Trailing edge details", "peso": 1.0},
            "F05B2240/307": {"descripcion": "Blade tip / winglets", "peso": 1.0},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) ===
            "F03D1/0625": {"descripcion": "Aerodynamic shape complete rotor", "peso": 0.8},
            "F03D7/022": {"descripcion": "Adjusting aerodynamic properties", "peso": 0.8},
            "F05B2240/231": {"descripcion": "Blades driven by lift", "peso": 0.8},
            "F05B2240/232": {"descripcion": "Blades driven by drag", "peso": 0.8},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "F05B2250/71": {"descripcion": "Curved shape", "peso": 0.6},
            "F05B2250/72": {"descripcion": "Symmetric shape", "peso": 0.6},
            "F05B2250/73": {"descripcion": "Asymmetric shape", "peso": 0.6},
        }
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # 2. GEOMETRÍA Y ESTRUCTURA
    # Características geométricas y elementos estructurales de la pala
    # ───────────────────────────────────────────────────────────────────────────
    "estructura": {
        "nombre": "Geometría / Estructura",
        "descripcion": "Elementos estructurales, geometría de secciones, segmentación y componentes internos",
        "palabras_clave": [
            "structure", "spar", "web", "shell", "segment", "section",
            "geometry", "cross-section", "internal", "cap", "beam"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS (peso 1.0) ===
            "F03D1/0675": {"descripcion": "Blade constructional elements", "peso": 1.0},
            "F03D1/0683": {"descripcion": "Shell + inner structure (sandwich)", "peso": 1.0},
            "F03D1/0691": {"descripcion": "Segmented blades (longitudinal)", "peso": 1.0},
            "F05B2240/302": {"descripcion": "Segmented/sectional blades", "peso": 1.0},
            "F05B2240/20": {"descripcion": "Rotors with blades", "peso": 1.0},
            "F05B2240/21": {"descripcion": "Blade details", "peso": 1.0},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) - Geometría 2D/3D ===
            "F05B2250/11": {"descripcion": "Triangular geometry", "peso": 0.8},
            "F05B2250/12": {"descripcion": "Rectangular geometry", "peso": 0.8},
            "F05B2250/13": {"descripcion": "Trapezoidal geometry", "peso": 0.8},
            "F05B2250/14": {"descripcion": "Elliptical geometry", "peso": 0.8},
            "F05B2250/23": {"descripcion": "Prismatic 3D shape", "peso": 0.8},
            "F05B2250/25": {"descripcion": "Helical 3D shape", "peso": 0.8},
            "F05B2250/292": {"descripcion": "Tapered structure", "peso": 0.8},
            "F05B2250/283": {"descripcion": "Honeycomb structure", "peso": 0.8},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "F05B2250/70": {"descripcion": "General shape characteristics", "peso": 0.6},
            "F05B2250/291": {"descripcion": "Hollowed structure", "peso": 0.6},
        }
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # 3. GENERADORES DE VÓRTICE
    # Dispositivos para control de flujo mediante generación de vórtices
    # ───────────────────────────────────────────────────────────────────────────
    "vortex": {
        "nombre": "Generadores de Vórtice",
        "descripcion": "Dispositivos para generar vórtices y controlar el flujo en la capa límite",
        "palabras_clave": [
            "vortex generator", "vg", "flow control", "boundary layer",
            "turbulator", "fin", "tab", "spoiler"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS (peso 1.0) ===
            "F05B2240/3062": {"descripcion": "Vortex generators", "peso": 1.0},
            "F05B2240/122": {"descripcion": "Turbulators / flow-altering devices", "peso": 1.0},
            "F03D1/0633": {"descripcion": "Aerodynamic shape (VG context)", "peso": 0.9},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) ===
            "F05B2240/305": {"descripcion": "Flaps, slats or spoilers", "peso": 0.8},
            "F05B2240/3052": {"descripcion": "Adjustable flaps/slats", "peso": 0.8},
            "F05B2240/306": {"descripcion": "Surface measures", "peso": 0.8},
            "F03D7/0236": {"descripcion": "Change of active surface", "peso": 0.8},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "F05B2250/60": {"descripcion": "Surface texture/structure", "peso": 0.6},
            "F05B2240/32": {"descripcion": "Rough surfaces", "peso": 0.6},
        }
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # 4. REDUCCIÓN DE RUIDO
    # Tecnologías para minimizar emisiones acústicas
    # ───────────────────────────────────────────────────────────────────────────
    "ruido": {
        "nombre": "Reducción de Ruido",
        "descripcion": "Serrations, tratamientos de borde y tecnologías de reducción acústica",
        "palabras_clave": [
            "noise", "acoustic", "sound", "serration", "trailing edge",
            "reduction", "silent", "quiet", "damping"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS (peso 1.0) ===
            "F03D80/30": {"descripcion": "Noise reduction accessories", "peso": 1.0},
            "F03D7/0296": {"descripcion": "Controlling to reduce noise", "peso": 1.0},
            "F05B2260/96": {"descripcion": "Preventing/reducing noise", "peso": 1.0},
            "F05B2260/962": {"descripcion": "Anti-noise means", "peso": 1.0},
            "F05B2240/3042": {"descripcion": "Serrated trailing edge", "peso": 1.0},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) ===
            "F05B2260/964": {"descripcion": "Damping means", "peso": 0.8},
            "F05B2270/333": {"descripcion": "Noise/sound levels (parameter)", "peso": 0.8},
            "F05B2240/304": {"descripcion": "Trailing edge details (noise)", "peso": 0.7},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "F05B2260/966": {"descripcion": "Correcting imbalance", "peso": 0.6},
        }
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # 5. CONTROL DE PITCH
    # Sistemas de control de paso de pala
    # ───────────────────────────────────────────────────────────────────────────
    "control": {
        "nombre": "Control de Pitch",
        "descripcion": "Sistemas de control de paso, actuadores y mecanismos de ajuste de pala",
        "palabras_clave": [
            "pitch", "control", "actuator", "angle", "adjustment",
            "mechanism", "hydraulic", "electric", "bearing"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS (peso 1.0) ===
            "F03D7/0224": {"descripcion": "Controlling blade pitch", "peso": 1.0},
            "F03D7/024": {"descripcion": "Individual blade control", "peso": 1.0},
            "F03D7/0232": {"descripcion": "Control of flaps/slats", "peso": 1.0},
            "F03D7/02": {"descripcion": "Controlling rotor by varying pitch", "peso": 1.0},
            "F05B2260/70": {"descripcion": "Adjusting angle of attack", "peso": 1.0},
            "F05B2270/328": {"descripcion": "Blade pitch angle (parameter)", "peso": 1.0},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) ===
            "F05B2260/72": {"descripcion": "Turning parallel to rotor axis", "peso": 0.8},
            "F05B2260/74": {"descripcion": "Turning perpendicular to rotor", "peso": 0.8},
            "F05B2240/31": {"descripcion": "Blades of changeable form", "peso": 0.8},
            "F05B2240/311": {"descripcion": "Flexible/elastic blades", "peso": 0.8},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "F05B2240/312": {"descripcion": "Blades capable of reefing", "peso": 0.6},
            "F05B2240/313": {"descripcion": "Adjustable flow area", "peso": 0.6},
        }
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # 6. MONITOREO Y SENSORES
    # Sistemas de monitoreo, diagnóstico y sensores en palas
    # ───────────────────────────────────────────────────────────────────────────
    "monitoreo": {
        "nombre": "Monitoreo / Sensores",
        "descripcion": "Sistemas de monitoreo estructural, sensores de carga, vibración y diagnóstico",
        "palabras_clave": [
            "sensor", "monitoring", "strain", "load", "vibration",
            "measurement", "detection", "diagnostic", "health"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS (peso 1.0) ===
            "F03D17/00": {"descripcion": "Monitoring/testing wind motors", "peso": 1.0},
            "F03D17/027": {"descripcion": "Monitoring blades", "peso": 1.0},
            "F03D17/009": {"descripcion": "Fatigue/stress monitoring", "peso": 1.0},
            "F03D17/010": {"descripcion": "Wear/clearance monitoring", "peso": 1.0},
            "F03D17/012": {"descripcion": "Vibration monitoring", "peso": 1.0},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) ===
            "F05B2260/80": {"descripcion": "Diagnostics", "peso": 0.8},
            "F05B2270/808": {"descripcion": "Strain gauges/load cells", "peso": 0.8},
            "F05B2270/334": {"descripcion": "Vibration measurements", "peso": 0.8},
            "G01M5/00": {"descripcion": "Testing structural integrity", "peso": 0.8},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "G01L1/00": {"descripcion": "Measuring force/stress", "peso": 0.6},
            "G01H1/00": {"descripcion": "Measuring vibrations", "peso": 0.6},
        }
    },
    
    # ───────────────────────────────────────────────────────────────────────────
    # 7. MATERIALES Y MANUFACTURA
    # Materiales de construcción y procesos de fabricación
    # ───────────────────────────────────────────────────────────────────────────
    "materiales": {
        "nombre": "Materiales / Manufactura",
        "descripcion": "Materiales compuestos, procesos de fabricación y técnicas de ensamblaje",
        "palabras_clave": [
            "composite", "fiber", "carbon", "glass", "resin", "epoxy",
            "manufacturing", "molding", "pultrusion", "infusion"
        ],
        "codigos": {
            # === CÓDIGOS PRIMARIOS - MATERIALES (peso 1.0) ===
            "F05B2280/6003": {"descripcion": "Composites/fibre-reinforced", "peso": 1.0},
            "F05B2280/6013": {"descripcion": "Fibres", "peso": 1.0},
            "F05B2280/2006": {"descripcion": "Carbon/graphite", "peso": 1.0},
            "F05B2280/2001": {"descripcion": "Glass fiber", "peso": 1.0},
            "F05B2280/6015": {"descripcion": "Resin", "peso": 1.0},
            
            # === CÓDIGOS PRIMARIOS - MANUFACTURA (peso 1.0) ===
            "F05B2230/60": {"descripcion": "Assembly methods", "peso": 1.0},
            "F05B2230/50": {"descripcion": "Building in particular ways", "peso": 1.0},
            "B29C70/00": {"descripcion": "Shaping composites", "peso": 1.0},
            "B29D99/00": {"descripcion": "Manufacturing blades", "peso": 1.0},
            
            # === CÓDIGOS SECUNDARIOS (peso 0.8) ===
            "F05B2280/6001": {"descripcion": "Fabrics", "peso": 0.8},
            "F05B2280/6002": {"descripcion": "Woven fabrics", "peso": 0.8},
            "F05B2280/4003": {"descripcion": "Synthetic polymers", "peso": 0.8},
            "F05B2230/23": {"descripcion": "Permanently joining parts", "peso": 0.8},
            "F05B2230/80": {"descripcion": "Repairing/retrofitting", "peso": 0.8},
            "F05B2230/90": {"descripcion": "Coating/Surface treatment", "peso": 0.8},
            
            # === CÓDIGOS TERCIARIOS (peso 0.6) ===
            "F05B2280/6011": {"descripcion": "Coating materials", "peso": 0.6},
            "F05B2280/6012": {"descripcion": "Foam materials", "peso": 0.6},
            "F05B2230/21": {"descripcion": "Casting process", "peso": 0.6},
            "F05B2230/232": {"descripcion": "Welding", "peso": 0.6},
        }
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# ÍNDICE INVERSO: CÓDIGO -> CATEGORÍA
# ═══════════════════════════════════════════════════════════════════════════════

def build_code_index():
    """Construye un índice inverso de código a categoría"""
    index = {}
    for categoria, datos in CPC_TAXONOMY.items():
        for codigo, info in datos["codigos"].items():
            index[codigo] = {
                "categoria": categoria,
                "categoria_nombre": datos["nombre"],
                "descripcion": info["descripcion"],
                "peso": info["peso"]
            }
    return index

CODE_INDEX = build_code_index()
ALL_CPC_CODES = list(CODE_INDEX.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN VISUAL
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_ICONS = {
    "aerodinamico": "🌊",
    "estructura": "🏗️",
    "vortex": "🌀",
    "ruido": "🔇",
    "control": "🎛️",
    "monitoreo": "📡",
    "materiales": "🧪",
}

CATEGORY_COLORS = {
    "aerodinamico": "#3498DB",  # Azul
    "estructura": "#E74C3C",     # Rojo
    "vortex": "#9B59B6",         # Púrpura
    "ruido": "#1ABC9C",          # Turquesa
    "control": "#F39C12",        # Naranja
    "monitoreo": "#2ECC71",      # Verde
    "materiales": "#95A5A6",     # Gris
}


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_code(code):
    """Normaliza un código CPC/IPC para comparación"""
    return code.strip().upper().replace(" ", "")


def get_category_for_code(code):
    """Obtiene la categoría para un código CPC/IPC"""
    normalized = normalize_code(code)
    
    # Buscar coincidencia exacta
    if normalized in CODE_INDEX:
        return CODE_INDEX[normalized]
    
    # Buscar coincidencia por prefijo (códigos más específicos)
    for known_code in CODE_INDEX:
        if normalized.startswith(known_code) or known_code.startswith(normalized):
            return CODE_INDEX[known_code]
    
    return None


def get_codes_for_category(category_id):
    """Obtiene todos los códigos de una categoría"""
    if category_id in CPC_TAXONOMY:
        return CPC_TAXONOMY[category_id]["codigos"]
    return {}


def get_all_categories():
    """Retorna lista de todas las categorías disponibles"""
    return [
        {
            "id": cat_id,
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"],
            "num_codigos": len(datos["codigos"]),
            "icon": CATEGORY_ICONS.get(cat_id, "📁"),
            "color": CATEGORY_COLORS.get(cat_id, "#CCCCCC")
        }
        for cat_id, datos in CPC_TAXONOMY.items()
    ]


def categorize_patent_codes(patent_codes):
    """
    Categoriza una lista de códigos de patente
    
    Args:
        patent_codes: lista de códigos IPC/CPC
    
    Returns:
        dict con categorías encontradas y puntuación
    """
    category_scores = {}
    matched_codes = {}
    
    for code in patent_codes:
        normalized = normalize_code(code)
        match = get_category_for_code(normalized)
        
        if match:
            cat_id = match["categoria"]
            
            if cat_id not in category_scores:
                category_scores[cat_id] = {
                    "nombre": match["categoria_nombre"],
                    "score": 0,
                    "codigos_encontrados": []
                }
            
            category_scores[cat_id]["score"] += match["peso"]
            category_scores[cat_id]["codigos_encontrados"].append({
                "codigo": normalized,
                "descripcion": match["descripcion"],
                "peso": match["peso"]
            })
            
            matched_codes[normalized] = match
    
    # Ordenar por score descendente
    sorted_categories = dict(
        sorted(category_scores.items(), key=lambda x: x[1]["score"], reverse=True)
    )
    
    return {
        "categorias": sorted_categories,
        "codigos_matched": matched_codes,
        "total_codigos_input": len(patent_codes),
        "total_codigos_matched": len(matched_codes)
    }


def find_matching_codes(patent_codes):
    """Encuentra códigos coincidentes en la taxonomía"""
    matches = {}
    for code in patent_codes:
        normalized = normalize_code(code)
        if normalized in CODE_INDEX:
            matches[normalized] = CODE_INDEX[normalized]
        else:
            for known_code in CODE_INDEX:
                if normalized.startswith(known_code) or known_code.startswith(normalized):
                    matches[normalized] = CODE_INDEX[known_code]
                    break
    return matches


# ═══════════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS DE LA TAXONOMÍA
# ═══════════════════════════════════════════════════════════════════════════════

def print_taxonomy_stats():
    """Imprime estadísticas de la taxonomía"""
    print("=" * 70)
    print("📊 TAXONOMÍA CPC/IPC v2.0 - ESTADÍSTICAS")
    print("=" * 70)
    
    total_codes = 0
    
    for cat in get_all_categories():
        icon = cat["icon"]
        nombre = cat["nombre"]
        num = cat["num_codigos"]
        total_codes += num
        
        # Contar por peso
        codigos = CPC_TAXONOMY[cat["id"]]["codigos"]
        peso_1 = sum(1 for c in codigos.values() if c["peso"] == 1.0)
        peso_08 = sum(1 for c in codigos.values() if 0.7 <= c["peso"] < 1.0)
        peso_06 = sum(1 for c in codigos.values() if c["peso"] < 0.7)
        
        print(f"\n{icon} {nombre}")
        print(f"   Total códigos: {num}")
        print(f"   • Primarios (1.0): {peso_1}")
        print(f"   • Secundarios (0.7-0.9): {peso_08}")
        print(f"   • Terciarios (<0.7): {peso_06}")
    
    print(f"\n{'─' * 70}")
    print(f"📈 Total categorías: {len(CPC_TAXONOMY)}")
    print(f"📈 Total códigos únicos: {total_codes}")
    print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_taxonomy_stats()
    
    # Test con patentes de ejemplo
    print("\n\n" + "=" * 70)
    print("🧪 TEST DE CATEGORIZACIÓN")
    print("=" * 70)
    
    # Simular códigos de una patente de generadores de vórtice
    test_codes_vg = ["F05B2240/3062", "F03D1/0633", "F05B2240/122"]
    print(f"\nTest VG: {test_codes_vg}")
    result = categorize_patent_codes(test_codes_vg)
    for cat_id, data in result["categorias"].items():
        print(f"   → {CATEGORY_ICONS[cat_id]} {data['nombre']}: {data['score']:.2f}")
    
    # Simular códigos de una patente de ruido
    test_codes_noise = ["F03D80/30", "F05B2240/3042", "F05B2260/96"]
    print(f"\nTest Ruido: {test_codes_noise}")
    result = categorize_patent_codes(test_codes_noise)
    for cat_id, data in result["categorias"].items():
        print(f"   → {CATEGORY_ICONS[cat_id]} {data['nombre']}: {data['score']:.2f}")
    
    # Simular códigos de una patente de control
    test_codes_control = ["F03D7/0224", "F03D7/024", "F05B2270/328"]
    print(f"\nTest Control: {test_codes_control}")
    result = categorize_patent_codes(test_codes_control)
    for cat_id, data in result["categorias"].items():
        print(f"   → {CATEGORY_ICONS[cat_id]} {data['nombre']}: {data['score']:.2f}")
