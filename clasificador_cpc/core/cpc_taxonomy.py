# cpc_taxonomy.py
"""
Taxonomía de códigos CPC/IPC para clasificación de patentes de palas eólicas
Organizado por categorías funcionales y estructurales
"""

# ═══════════════════════════════════════════════════════════════
# TAXONOMÍA PRINCIPAL DE CÓDIGOS CPC/IPC
# ═══════════════════════════════════════════════════════════════

CPC_TAXONOMY = {
    
    "perfil_aerodinamico": {
        "nombre": "Perfil Aerodinámico",
        "descripcion": "Forma general, perfil y características aerodinámicas de la pala",
        "palabras_clave": ["aerodynamic", "airfoil", "profile", "lift", "drag", "rotor shape"],
        "codigos": {
            "F03D1/0608": {
                "descripcion": "Aerodynamic shape of the rotor",
                "peso": 1.0
            },
            "F03D1/0633": {
                "descripcion": "Aerodynamic shape of the blades",
                "peso": 1.0
            },
            "F03D1/0641": {
                "descripcion": "Aerodynamic profile (blade section profile)",
                "peso": 1.0
            },
            "F03D1/0625": {
                "descripcion": "Aerodynamic shape of the complete rotor",
                "peso": 0.9
            },
            "F03D1/06": {
                "descripcion": "Rotors characterised by their aerodynamic shape",
                "peso": 0.9
            },
            "F03D7/022": {
                "descripcion": "Adjusting aerodynamic properties of the blades",
                "peso": 0.8
            },
            "F05B2240/231": {
                "descripcion": "Blades driven by aerodynamic lift effects",
                "peso": 0.8
            },
            "F05B2240/232": {
                "descripcion": "Blades driven by drag",
                "peso": 0.7
            },
            "F05B2240/301": {
                "descripcion": "Cross-section characteristics",
                "peso": 0.9
            },
            "F05B2240/303": {
                "descripcion": "Details of the leading edge",
                "peso": 0.9
            },
            "F05B2240/304": {
                "descripcion": "Details of the trailing edge",
                "peso": 0.9
            },
            "F05B2240/3042": {
                "descripcion": "Serrated trailing edge",
                "peso": 0.8
            },
            "F05B2240/307": {
                "descripcion": "Blade tip (winglets)",
                "peso": 0.9
            },
        }
    },
    
    "geometria_2d": {
        "nombre": "Geometría 2D",
        "descripcion": "Características geométricas bidimensionales de secciones de pala",
        "palabras_clave": ["cross-section", "profile", "shape", "2D", "section"],
        "codigos": {
            "F05B2250/11": {
                "descripcion": "Triangular geometry",
                "peso": 1.0
            },
            "F05B2250/12": {
                "descripcion": "Rectangular geometry",
                "peso": 1.0
            },
            "F05B2250/121": {
                "descripcion": "Square geometry",
                "peso": 0.9
            },
            "F05B2250/13": {
                "descripcion": "Trapezoidal geometry",
                "peso": 1.0
            },
            "F05B2250/131": {
                "descripcion": "Polygonal geometry",
                "peso": 0.9
            },
            "F05B2250/14": {
                "descripcion": "Elliptical geometry",
                "peso": 1.0
            },
            "F05B2250/141": {
                "descripcion": "Circular geometry",
                "peso": 0.9
            },
            "F05B2250/15": {
                "descripcion": "Spiral geometry",
                "peso": 0.8
            },
            "F05B2250/16": {
                "descripcion": "Parabolic geometry",
                "peso": 0.9
            },
            "F05B2250/17": {
                "descripcion": "Hyperbolic geometry",
                "peso": 0.8
            },
            "F05B2250/181": {
                "descripcion": "Ridged pattern",
                "peso": 0.7
            },
            "F05B2250/182": {
                "descripcion": "Crenellated/notched pattern",
                "peso": 0.7
            },
            "F05B2250/183": {
                "descripcion": "Zigzag pattern",
                "peso": 0.7
            },
            "F05B2250/184": {
                "descripcion": "Sinusoidal pattern",
                "peso": 0.8
            },
            "F05B2250/191": {
                "descripcion": "Perforated",
                "peso": 0.6
            },
            "F05B2250/192": {
                "descripcion": "Beveled",
                "peso": 0.7
            },
        }
    },
    
    "geometria_3d": {
        "nombre": "Geometría 3D",
        "descripcion": "Características geométricas tridimensionales de la pala completa",
        "palabras_clave": ["3D", "volume", "shape", "twist", "taper", "span"],
        "codigos": {
            "F05B2250/21": {
                "descripcion": "Pyramidal shape",
                "peso": 0.7
            },
            "F05B2250/22": {
                "descripcion": "Parallelepipedic shape",
                "peso": 0.7
            },
            "F05B2250/23": {
                "descripcion": "Prismatic shape",
                "peso": 0.8
            },
            "F05B2250/231": {
                "descripcion": "Cylindrical shape",
                "peso": 0.8
            },
            "F05B2250/232": {
                "descripcion": "Conical shape",
                "peso": 0.8
            },
            "F05B2250/24": {
                "descripcion": "Ellipsoidal shape",
                "peso": 0.8
            },
            "F05B2250/241": {
                "descripcion": "Spherical shape",
                "peso": 0.7
            },
            "F05B2250/25": {
                "descripcion": "Helical shape",
                "peso": 0.9
            },
            "F05B2250/26": {
                "descripcion": "Paraboloidal shape",
                "peso": 0.8
            },
            "F05B2250/27": {
                "descripcion": "Hyperboloidal shape",
                "peso": 0.7
            },
            "F05B2250/291": {
                "descripcion": "Hollowed structure",
                "peso": 0.8
            },
            "F05B2250/292": {
                "descripcion": "Tapered structure",
                "peso": 0.9
            },
        }
    },
    
    "geometria_forma": {
        "nombre": "Características de Forma",
        "descripcion": "Propiedades generales de forma y curvatura",
        "palabras_clave": ["curved", "symmetric", "asymmetric", "shape", "form"],
        "codigos": {
            "F05B2250/70": {
                "descripcion": "General shape characteristics",
                "peso": 0.8
            },
            "F05B2250/71": {
                "descripcion": "Curved shape",
                "peso": 0.9
            },
            "F05B2250/711": {
                "descripcion": "Convex curvature",
                "peso": 0.8
            },
            "F05B2250/712": {
                "descripcion": "Concave curvature",
                "peso": 0.8
            },
            "F05B2250/713": {
                "descripcion": "Inflexed shape",
                "peso": 0.7
            },
            "F05B2250/72": {
                "descripcion": "Symmetric shape",
                "peso": 0.8
            },
            "F05B2250/73": {
                "descripcion": "Asymmetric shape",
                "peso": 0.8
            },
        }
    },
    
    "estructura_superficie": {
        "nombre": "Estructura y Superficie",
        "descripcion": "Elementos constructivos y características de superficie de la pala",
        "palabras_clave": ["structure", "surface", "texture", "shell", "spar", "web", "skin"],
        "codigos": {
            "F03D1/0675": {
                "descripcion": "Blade constructional elements",
                "peso": 1.0
            },
            "F03D1/0683": {
                "descripcion": "Blades with outer shell and inner structure (sandwich)",
                "peso": 1.0
            },
            "F03D1/0691": {
                "descripcion": "Segmented blades (longitudinal)",
                "peso": 0.9
            },
            "F03D7/0236": {
                "descripcion": "Change of active surface (folding)",
                "peso": 0.8
            },
            "F05B2240/32": {
                "descripcion": "Blades with rough surfaces",
                "peso": 0.7
            },
            "F05B2240/122": {
                "descripcion": "Turbulators/flow-altering devices",
                "peso": 0.8
            },
            "F05B2240/302": {
                "descripcion": "Segmented or sectional blades",
                "peso": 0.9
            },
            "F05B2240/305": {
                "descripcion": "Flaps, slats or spoilers",
                "peso": 0.9
            },
            "F05B2240/3052": {
                "descripcion": "Adjustable flaps/slats",
                "peso": 0.8
            },
            "F05B2240/306": {
                "descripcion": "Surface measures",
                "peso": 0.7
            },
            "F05B2240/3062": {
                "descripcion": "Vortex generators",
                "peso": 0.9
            },
            "F05B2250/60": {
                "descripcion": "Surface texture/structure",
                "peso": 0.8
            },
            "F05B2250/61": {
                "descripcion": "Corrugated surface",
                "peso": 0.7
            },
            "F05B2250/611": {
                "descripcion": "Undulated surface",
                "peso": 0.7
            },
            "F05B2250/62": {
                "descripcion": "Smooth surface",
                "peso": 0.6
            },
            "F05B2250/621": {
                "descripcion": "Polished surface",
                "peso": 0.6
            },
            "F05B2250/283": {
                "descripcion": "Honeycomb structure",
                "peso": 0.9
            },
        }
    },
    
    "materiales": {
        "nombre": "Materiales",
        "descripcion": "Materiales de fabricación de palas",
        "palabras_clave": ["material", "composite", "fiber", "carbon", "glass", "polymer", "resin"],
        "codigos": {
            "F05B2280/6003": {
                "descripcion": "Composites/fibre-reinforced materials",
                "peso": 1.0
            },
            "F05B2280/6013": {
                "descripcion": "Fibres",
                "peso": 0.9
            },
            "F05B2280/6001": {
                "descripcion": "Fabrics",
                "peso": 0.8
            },
            "F05B2280/6002": {
                "descripcion": "Woven fabrics",
                "peso": 0.8
            },
            "F05B2280/4003": {
                "descripcion": "Synthetic polymers/plastics",
                "peso": 0.8
            },
            "F05B2280/2006": {
                "descripcion": "Carbon/graphite",
                "peso": 1.0
            },
            "F05B2280/2001": {
                "descripcion": "Glass fiber",
                "peso": 1.0
            },
            "F05B2280/6011": {
                "descripcion": "Coating materials",
                "peso": 0.7
            },
            "F05B2280/6012": {
                "descripcion": "Foam materials",
                "peso": 0.7
            },
            "F05B2280/6015": {
                "descripcion": "Resin",
                "peso": 0.9
            },
            "F05B2280/4004": {
                "descripcion": "Rubber",
                "peso": 0.6
            },
            "F05B2280/10304": {
                "descripcion": "Titanium",
                "peso": 0.7
            },
            "F05B2280/1021": {
                "descripcion": "Aluminium",
                "peso": 0.7
            },
        }
    },
    
    "manufactura": {
        "nombre": "Manufactura",
        "descripcion": "Procesos de fabricación y ensamblaje de palas",
        "palabras_clave": ["manufacturing", "process", "assembly", "molding", "casting", "welding"],
        "codigos": {
            "F05B2230/21": {
                "descripcion": "Casting process",
                "peso": 0.8
            },
            "F05B2230/23": {
                "descripcion": "Permanently joining parts",
                "peso": 0.9
            },
            "F05B2230/232": {
                "descripcion": "Welding",
                "peso": 0.8
            },
            "F05B2230/234": {
                "descripcion": "Laser welding",
                "peso": 0.7
            },
            "F05B2230/237": {
                "descripcion": "Brazing",
                "peso": 0.6
            },
            "F05B2230/50": {
                "descripcion": "Building in particular ways",
                "peso": 0.8
            },
            "F05B2230/60": {
                "descripcion": "Assembly methods",
                "peso": 0.9
            },
            "F05B2230/80": {
                "descripcion": "Repairing/retrofitting/upgrading",
                "peso": 0.8
            },
            "F05B2230/90": {
                "descripcion": "Coating/Surface treatment",
                "peso": 0.7
            },
            "F05B2230/31": {
                "descripcion": "Layer deposition",
                "peso": 0.7
            },
        }
    },
    
    "control_ajuste": {
        "nombre": "Control y Ajuste",
        "descripcion": "Sistemas de control y ajuste de palas",
        "palabras_clave": ["control", "pitch", "adjustment", "actuator", "sensor", "feedback"],
        "codigos": {
            "F03D7/0224": {
                "descripcion": "Controlling blade pitch",
                "peso": 1.0
            },
            "F03D7/024": {
                "descripcion": "Individual blade control",
                "peso": 1.0
            },
            "F03D7/0232": {
                "descripcion": "Control of flaps/slats",
                "peso": 0.9
            },
            "F05B2260/70": {
                "descripcion": "Adjusting angle of incidence/attack",
                "peso": 0.9
            },
            "F05B2260/72": {
                "descripcion": "Turning around axis parallel to rotor",
                "peso": 0.8
            },
            "F05B2260/74": {
                "descripcion": "Turning around axis perpendicular to rotor",
                "peso": 0.8
            },
            "F05B2240/31": {
                "descripcion": "Blades of changeable form/shape",
                "peso": 0.9
            },
            "F05B2240/311": {
                "descripcion": "Flexible or elastic blades",
                "peso": 0.8
            },
            "F05B2240/312": {
                "descripcion": "Blades capable of being reefed",
                "peso": 0.7
            },
            "F05B2240/313": {
                "descripcion": "Adjustable flow intercepting area",
                "peso": 0.8
            },
            "F05B2270/328": {
                "descripcion": "Blade pitch angle (control parameter)",
                "peso": 0.9
            },
        }
    },
    
    "monitoreo_diagnostico": {
        "nombre": "Monitoreo y Diagnóstico",
        "descripcion": "Sistemas de monitoreo, diagnóstico y detección de fallas",
        "palabras_clave": ["monitoring", "sensor", "diagnostic", "detection", "measurement", "testing"],
        "codigos": {
            "F03D17/00": {
                "descripcion": "Monitoring or testing wind motors",
                "peso": 1.0
            },
            "F03D17/009": {
                "descripcion": "Fatigue/stress monitoring",
                "peso": 1.0
            },
            "F03D17/010": {
                "descripcion": "Wear/clearance monitoring",
                "peso": 0.9
            },
            "F03D17/012": {
                "descripcion": "Vibration monitoring",
                "peso": 0.9
            },
            "F03D17/027": {
                "descripcion": "Monitoring blades",
                "peso": 1.0
            },
            "F05B2260/80": {
                "descripcion": "Diagnostics",
                "peso": 0.9
            },
            "F05B2270/808": {
                "descripcion": "Strain gauges/load cells",
                "peso": 0.8
            },
            "F05B2270/334": {
                "descripcion": "Vibration measurements",
                "peso": 0.8
            },
        }
    },
    
    "ruido_vibraciones": {
        "nombre": "Reducción de Ruido y Vibraciones",
        "descripcion": "Tecnologías para reducir ruido y vibraciones",
        "palabras_clave": ["noise", "vibration", "damping", "acoustic", "sound", "reduction"],
        "codigos": {
            "F03D7/0296": {
                "descripcion": "Controlling to reduce noise",
                "peso": 1.0
            },
            "F03D80/30": {
                "descripcion": "Noise reduction accessories",
                "peso": 1.0
            },
            "F05B2260/96": {
                "descripcion": "Preventing/reducing vibration or noise",
                "peso": 1.0
            },
            "F05B2260/962": {
                "descripcion": "Anti-noise means",
                "peso": 0.9
            },
            "F05B2260/964": {
                "descripcion": "Damping means",
                "peso": 0.9
            },
            "F05B2260/966": {
                "descripcion": "Correcting static/dynamic imbalance",
                "peso": 0.8
            },
            "F05B2270/333": {
                "descripcion": "Noise/sound levels (parameter)",
                "peso": 0.8
            },
        }
    },
}


# ═══════════════════════════════════════════════════════════════
# ÍNDICE INVERSO: CÓDIGO -> CATEGORÍA
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# LISTA PLANA DE TODOS LOS CÓDIGOS
# ═══════════════════════════════════════════════════════════════

ALL_CPC_CODES = list(CODE_INDEX.keys())


# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE UTILIDAD
# ═══════════════════════════════════════════════════════════════

def get_category_for_code(code):
    """
    Obtiene la categoría para un código CPC/IPC
    
    Args:
        code: código CPC/IPC (ej: "F03D1/0608")
    
    Returns:
        dict con información de la categoría o None si no se encuentra
    """
    # Buscar coincidencia exacta
    if code in CODE_INDEX:
        return CODE_INDEX[code]
    
    # Buscar coincidencia parcial (para códigos más específicos)
    for known_code in CODE_INDEX:
        if code.startswith(known_code) or known_code.startswith(code):
            return CODE_INDEX[known_code]
    
    return None


def get_codes_for_category(category_id):
    """
    Obtiene todos los códigos de una categoría
    
    Args:
        category_id: ID de la categoría (ej: "perfil_aerodinamico")
    
    Returns:
        dict con códigos y sus descripciones
    """
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
            "num_codigos": len(datos["codigos"])
        }
        for cat_id, datos in CPC_TAXONOMY.items()
    ]


def normalize_code(code):
    """
    Normaliza un código CPC/IPC para comparación
    Elimina espacios y convierte a mayúsculas
    """
    return code.strip().upper().replace(" ", "")


def find_matching_codes(patent_codes):
    """
    Encuentra códigos coincidentes en la taxonomía
    
    Args:
        patent_codes: lista de códigos IPC/CPC de una patente
    
    Returns:
        dict con códigos encontrados y sus categorías
    """
    matches = {}
    
    for code in patent_codes:
        normalized = normalize_code(code)
        
        # Buscar en índice
        if normalized in CODE_INDEX:
            matches[normalized] = CODE_INDEX[normalized]
        else:
            # Buscar coincidencias parciales
            for known_code in CODE_INDEX:
                if normalized.startswith(known_code) or known_code.startswith(normalized):
                    matches[normalized] = CODE_INDEX[known_code]
                    break
    
    return matches


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


# ═══════════════════════════════════════════════════════════════
# INFORMACIÓN DE CATEGORÍAS PARA REPORTES
# ═══════════════════════════════════════════════════════════════

CATEGORY_COLORS = {
    "perfil_aerodinamico": "#FF6B6B",
    "geometria_2d": "#4ECDC4",
    "geometria_3d": "#45B7D1",
    "geometria_forma": "#96CEB4",
    "estructura_superficie": "#FFEAA7",
    "materiales": "#DDA0DD",
    "manufactura": "#98D8C8",
    "control_ajuste": "#F7DC6F",
    "monitoreo_diagnostico": "#BB8FCE",
    "ruido_vibraciones": "#85C1E9",
}

CATEGORY_ICONS = {
    "perfil_aerodinamico": "🌊",
    "geometria_2d": "📐",
    "geometria_3d": "📦",
    "geometria_forma": "🔷",
    "estructura_superficie": "🏗️",
    "materiales": "🧪",
    "manufactura": "🔧",
    "control_ajuste": "🎛️",
    "monitoreo_diagnostico": "📊",
    "ruido_vibraciones": "🔇",
}


# ═══════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 CPC TAXONOMY - TEST")
    print("=" * 60)
    
    # Mostrar categorías
    print("\n📂 CATEGORÍAS DISPONIBLES:")
    for cat in get_all_categories():
        icon = CATEGORY_ICONS.get(cat["id"], "📁")
        print(f"   {icon} {cat['nombre']}: {cat['num_codigos']} códigos")
    
    print(f"\n📊 Total de códigos en taxonomía: {len(ALL_CPC_CODES)}")
    
    # Test de categorización
    print("\n" + "=" * 60)
    print("🧪 TEST DE CATEGORIZACIÓN")
    print("=" * 60)
    
    test_codes = [
        "F03D1/0633",
        "F05B2280/6003",
        "F03D17/00",
        "F05B2250/25",
        "F03D7/0224"
    ]
    
    print(f"\nCódigos de prueba: {test_codes}")
    
    result = categorize_patent_codes(test_codes)
    
    print(f"\n✅ Códigos matched: {result['total_codigos_matched']}/{result['total_codigos_input']}")
    
    print("\n📊 Categorías encontradas:")
    for cat_id, cat_data in result["categorias"].items():
        icon = CATEGORY_ICONS.get(cat_id, "📁")
        print(f"\n   {icon} {cat_data['nombre']} (Score: {cat_data['score']:.2f})")
        for cod in cat_data["codigos_encontrados"]:
            print(f"      • {cod['codigo']}: {cod['descripcion']}")
