# domain_dictionaries.py
"""
Diccionarios específicos para el dominio de aspas de aerogeneradores
Estos diccionarios guían la extracción automática de entidades RFSL
"""

# ═══════════════════════════════════════════════════════════════
# ESTRUCTURAS (S) - Componentes físicos del aspa
# ═══════════════════════════════════════════════════════════════

STRUCTURES = {
    # Componentes principales
    "blade": ["blade", "aspa", "pala", "rotor blade", "wind turbine blade"],
    "airfoil": ["airfoil", "perfil aerodinámico", "aerodynamic profile", "aerofoil"],
    "spar": ["spar", "viga principal", "main spar", "spar cap", "larguero", "beam"],
    "skin": ["skin", "shell", "revestimiento", "carcasa", "cubierta", "covering"],
    "web": ["web", "shear web", "alma", "structural web"],
    "core": ["core", "núcleo", "foam core", "structural core"],

    # Zonas del aspa
    "root": ["root", "raíz", "blade root", "root section", "root end"],
    "tip": ["tip", "punta", "blade tip", "tip section", "tip end"],
    "mid_span": ["mid-span", "mid span", "sección media", "middle section", "midspan"],
    "leading_edge": ["leading edge", "borde de ataque", "front edge", "forward edge"],
    "trailing_edge": ["trailing edge", "borde de salida", "rear edge", "aft edge"],
    "pressure_side": ["pressure side", "lado de presión", "intrados", "lower surface"],
    "suction_side": ["suction side", "lado de succión", "extrados", "upper surface"],

    # Sistemas de control
    "pitch_system": ["pitch system", "sistema de pitch", "pitch mechanism", "pitch control"],
    "pitch_bearing": ["pitch bearing", "rodamiento de pitch", "pitch bearing assembly"],
    "actuator": ["actuator", "actuador", "drive mechanism"],

    # Protección
    "lightning_receptor": ["lightning receptor", "receptor de rayos", "lightning protection", "lightning conductor"],
    "de_icing_system": ["de-icing system", "anti-icing", "sistema anti-hielo", "ice protection"],
    "heating_element": ["heating element", "elemento calefactor", "resistencia", "heater"],
    "protective_coating": ["protective coating", "recubrimiento protector", "coating", "protective layer"],

    # Materiales
    "fiberglass": ["fiberglass", "glass fiber", "fibra de vidrio", "glass fibre"],
    "carbon_fiber": ["carbon fiber", "fibra de carbono", "carbon fibre"],
    "epoxy_resin": ["epoxy", "epoxy resin", "resina epoxi", "resin"],
    "composite": ["composite", "composite material", "material compuesto"],
    "foam": ["foam", "espuma", "foam material"],
    "reinforcement": ["reinforcement", "refuerzo", "reinforcing"],

    # Elementos de unión
    "bolt": ["bolt", "perno", "tornillo", "fastener"],
    "adhesive": ["adhesive", "adhesivo", "bonding agent", "glue"],
    "flange": ["flange", "brida"],
    "insert": ["insert", "inserto", "bushing"]
}

# ═══════════════════════════════════════════════════════════════
# FUNCIONES (F) - Acciones y propósitos
# ═══════════════════════════════════════════════════════════════

FUNCTION_VERBS = {
    # Captura de energía
    "capture": ["capture", "capturar", "catch", "harvest"],
    "convert": ["convert", "convertir", "transform"],
    "generate": ["generate", "generar", "produce"],

    # Control aerodinámico
    "control": ["control", "controlar", "regulate"],
    "adjust": ["adjust", "ajustar", "modify"],
    "stabilize": ["stabilize", "estabilizar"],
    "optimize": ["optimize", "optimizar"],

    # Resistencia estructural
    "support": ["support", "soportar", "bear"],
    "resist": ["resist", "resistir", "withstand"],
    "distribute": ["distribute", "distribuir"],
    "absorb": ["absorb", "absorber"],

    # Protección
    "protect": ["protect", "proteger"],
    "prevent": ["prevent", "prevenir", "avoid"],
    "deflect": ["deflect", "desviar"],

    # Mejora
    "improve": ["improve", "mejorar", "enhance"],
    "increase": ["increase", "aumentar", "boost"],
    "reduce": ["reduce", "reducir", "decrease", "minimize"],

    # Detección
    "detect": ["detect", "detectar", "sense"],
    "monitor": ["monitor", "monitorear"],
    "measure": ["measure", "medir"]
}

FUNCTION_NOUNS = [
    # Energía
    "wind energy", "energía eólica", "kinetic energy", "energy",
    "power", "potencia", "torque", "momento",

    # Aerodinámico
    "lift", "sustentación", "drag", "arrastre",
    "thrust", "empuje", "airflow", "flujo de aire",
    "aerodynamic efficiency", "eficiencia aerodinámica",

    # Estructural
    "load", "carga", "stress", "esfuerzo",
    "strain", "deformación", "vibration", "vibración",
    "fatigue", "fatiga", "structural integrity",

    # Protección
    "ice", "hielo", "lightning", "rayo",
    "erosion", "erosión", "corrosion", "corrosión",
    "damage", "daño",

    # Otros
    "noise", "ruido", "efficiency", "eficiencia",
    "performance", "rendimiento", "stability", "estabilidad"
]

# ═══════════════════════════════════════════════════════════════
# UBICACIONES (L) - Términos de posición
# ═══════════════════════════════════════════════════════════════

LOCATION_TERMS = {
    # Spanwise (a lo largo del aspa)
    "spanwise": [
        "at the root", "en la raíz", "root portion", "root region",
        "at the tip", "en la punta", "tip region", "tip portion",
        "mid-span", "at mid-span", "en la sección media",
        "inboard", "outboard", "inboard section", "outboard section"
    ],

    # Chordwise (a lo largo de la cuerda)
    "chordwise": [
        "at the leading edge", "en el borde de ataque", "leading edge region",
        "at the trailing edge", "en el borde de salida", "trailing edge region",
        "at quarter chord", "al cuarto de cuerda"
    ],

    # Lados
    "sides": [
        "pressure side", "lado de presión",
        "suction side", "lado de succión",
        "upper surface", "superficie superior",
        "lower surface", "superficie inferior"
    ],

    # Vertical
    "vertical": [
        "upper", "superior", "top",
        "lower", "inferior", "bottom",
        "middle", "medio"
    ],

    # Profundidad
    "depth": [
        "outer surface", "superficie exterior",
        "inner surface", "superficie interior",
        "outer layer", "capa exterior",
        "inner layer", "capa interior",
        "within", "dentro de", "inside"
    ],

    # Relaciones espaciales
    "relations": [
        "adjacent to", "adyacente a",
        "between", "entre",
        "along", "a lo largo de",
        "through", "a través de",
        "parallel to", "paralelo a",
        "perpendicular to", "perpendicular a",
        "near", "cerca de", "proximate to"
    ]
}

# ═══════════════════════════════════════════════════════════════
# REQUISITOS (R) - Problemas a resolver
# ═══════════════════════════════════════════════════════════════

REQUIREMENT_PATTERNS = {
    "improve": [
        r"improve(?:s|d|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"mejorar\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ],
    "increase": [
        r"increase(?:s|d|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"aumentar\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ],
    "reduce": [
        r"reduce(?:s|d|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"reducir\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ],
    "prevent": [
        r"prevent(?:s|ed|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"prevenir\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ],
    "avoid": [
        r"avoid(?:s|ed|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"evitar\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ],
    "enhance": [
        r"enhance(?:s|d|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"mejorar\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ],
    "minimize": [
        r"minimize(?:s|d|ing)?\s+(?:the\s+)?(\w+(?:\s+\w+){0,3})",
        r"minimizar\s+(?:la|el|los|las)?\s*(\w+(?:\s+\w+){0,3})"
    ]
}

# Categorías de requisitos comunes
TARGET_REQUIREMENTS = {
    "efficiency": ["efficiency", "eficiencia", "performance", "rendimiento"],
    "strength": ["strength", "resistencia", "durability", "durabilidad"],
    "weight": ["weight", "peso", "mass", "masa"],
    "noise": ["noise", "ruido", "acoustic", "acústico"],
    "ice": ["ice", "hielo", "icing", "formación de hielo"],
    "lightning": ["lightning", "rayo", "electrical discharge"],
    "fatigue": ["fatigue", "fatiga", "life", "vida útil"],
    "cost": ["cost", "costo", "manufacturing", "fabricación"],
    "erosion": ["erosion", "erosión", "wear", "desgaste"]
}

if __name__ == "__main__":
    print("=" * 60)
    print(" DICCIONARIOS DEL DOMINIO CARGADOS")
    print("=" * 60)
    print(f"✓ Estructuras: {len(STRUCTURES)} categorías")
    print(f"✓ Verbos de función: {len(FUNCTION_VERBS)} categorías")
    print(f"✓ Sustantivos de función: {len(FUNCTION_NOUNS)} términos")
    print(f"✓ Términos de ubicación: {sum(len(v) for v in LOCATION_TERMS.values())} términos")
    print(f"✓ Patrones de requisitos: {len(REQUIREMENT_PATTERNS)} tipos")
    print(f"✓ Requisitos objetivo: {len(TARGET_REQUIREMENTS)} categorías")
    print("=" * 60)