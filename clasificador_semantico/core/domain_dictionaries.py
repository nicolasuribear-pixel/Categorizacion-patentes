# domain_dictionaries.py
"""
Diccionarios específicos para el dominio de aspas de aerogeneradores.
Estos diccionarios guían la extracción automática de entidades RFSL.

Convención (IMPORTANTE):
  - Todo el contenido de los diccionarios está en INGLÉS porque opera
    sobre texto de patentes en inglés (Google Patents).
  - Los comentarios y docstrings sí están en español.
  - Se evitan términos demasiado genéricos (p.ej. "beam", "core" aislado,
    "upper", "lower", "near", "between"): producen falsos positivos.
"""

# ═══════════════════════════════════════════════════════════════
# ESTRUCTURAS (S) - Componentes físicos del aspa
# Solo términos específicos del dominio. Nada de palabras sueltas
# que aparezcan fuera de contexto ("beam", "core", "web", "covering"...).
# ═══════════════════════════════════════════════════════════════

STRUCTURES = {
    # Componentes principales del aspa
    "blade": ["wind turbine blade", "rotor blade", "turbine blade"],
    "airfoil": ["airfoil", "aerofoil", "airfoil profile", "aerofoil profile"],
    "spar": ["spar", "main spar", "spar cap", "spar caps"],
    "shell": ["blade shell", "shell member", "blade skin", "outer shell"],
    "shear_web": ["shear web", "structural web", "web member"],
    "sandwich": ["sandwich structure", "sandwich panel", "sandwich core"],

    # Zonas del aspa
    "root": ["blade root", "root section", "root end", "root area", "root region", "root portion"],
    "tip": ["blade tip", "tip section", "tip end", "tip region", "tip portion"],
    "mid_span": ["mid-span", "mid span", "midspan", "middle section of the blade"],
    "leading_edge": ["leading edge", "blade leading edge"],
    "trailing_edge": ["trailing edge", "blade trailing edge", "blunt trailing edge", "pointed trailing edge"],
    "pressure_side": ["pressure side", "pressure surface"],
    "suction_side": ["suction side", "suction surface"],
    "transition_area": ["transition area", "transition region", "transition zone"],
    "airfoil_area": ["airfoil area", "airfoil region", "profiled area"],

    # Superficies aerodinámicas añadidas / modificadores de flujo
    "vortex_generator": ["vortex generator", "vortex generators"],
    "gurney_flap": ["gurney flap"],
    "winglet": ["winglet", "tip winglet"],
    "serration": ["serration", "serrated edge", "serrations", "trailing edge serrations"],
    "flap": ["trailing edge flap", "aerodynamic flap", "blade flap"],
    "slot": ["leading edge slot", "slotted airfoil"],
    "blade_element": ["blade element", "aerodynamic element", "flow element"],

    # Sistemas de control del rotor
    "pitch_system": ["pitch system", "pitch mechanism", "pitch control system", "pitch actuation system"],
    "pitch_bearing": ["pitch bearing", "pitch bearing assembly"],
    "actuator": ["actuator", "pitch actuator", "blade actuator", "drive mechanism"],
    "hub": ["rotor hub", "wind turbine hub"],
    "rotor": ["wind turbine rotor", "turbine rotor"],

    # Protección
    "lightning_receptor": ["lightning receptor", "lightning protection system",
                           "lightning conductor", "down conductor"],
    "de_icing_system": ["de-icing system", "anti-icing system", "ice protection system",
                        "ice mitigation system"],
    "heating_element": ["heating element", "heater mat", "electrical heater"],
    "protective_coating": ["protective coating", "erosion coating", "leading edge coating",
                           "protective layer", "erosion protection shield"],

    # Materiales
    "fiberglass": ["fiberglass", "glass fiber", "glass fibre", "fibre-reinforced polymer",
                   "fiber-reinforced polymer", "glass fiber reinforced"],
    "carbon_fiber": ["carbon fiber", "carbon fibre", "carbon fibre reinforced"],
    "epoxy_resin": ["epoxy resin", "epoxy matrix", "epoxy", "vinylester", "polyester resin"],
    "composite": ["composite material", "fibre composite", "fiber composite", "laminate composite"],
    "foam_core": ["foam core", "polymer foam", "foamed polymer", "structural foam"],
    "balsa": ["balsa wood", "balsa core"],
    "prepreg": ["prepreg", "pre-impregnated"],
    "laminate": ["laminate", "laminated structure", "laminate layer"],
    "reinforcement": ["structural reinforcement", "reinforcing layer", "reinforcing fibre"],

    # Elementos de unión y montaje
    "bolt": ["root bolt", "t-bolt", "through-bolt", "stud bolt"],
    "adhesive": ["structural adhesive", "bonding adhesive", "adhesive bond", "bonding agent"],
    "flange": ["root flange", "mounting flange"],
    "insert": ["structural insert", "threaded insert", "bushing", "root bushing"],
    "bonding_line": ["bonding line", "adhesive joint", "bond line"]
}

# ═══════════════════════════════════════════════════════════════
# FUNCIONES (F) - Acciones y propósitos técnicos
# Verbos deliberadamente técnicos. Los verbos muy genéricos
# (improve/increase/reduce/control) se usan solo cuando se
# combinan con FUNCTION_NOUNS específicos (ver extractor).
# ═══════════════════════════════════════════════════════════════

FUNCTION_VERBS = {
    # Captura y conversión de energía
    "capture": ["capture", "harvest", "extract"],
    "convert": ["convert", "transform"],
    "generate": ["generate", "produce"],

    # Control aerodinámico
    "control": ["control", "regulate"],
    "adjust": ["adjust", "modify"],
    "stabilize": ["stabilize"],
    "optimize": ["optimize"],
    "redirect": ["redirect", "deflect", "divert", "guide"],

    # Resistencia estructural
    "support": ["support", "bear", "carry"],
    "resist": ["resist", "withstand"],
    "distribute": ["distribute", "transmit"],
    "absorb": ["absorb", "dissipate", "dampen"],

    # Protección
    "protect": ["protect", "shield"],
    "prevent": ["prevent", "avoid", "mitigate", "eliminate"],

    # Mejora (solo se usan si van con un noun técnico; ver extractor)
    "improve": ["improve", "enhance"],
    "increase": ["increase", "boost", "maximize"],
    "reduce": ["reduce", "decrease", "minimize"],

    # Detección / medida
    "detect": ["detect", "sense"],
    "monitor": ["monitor"],
    "measure": ["measure"],

    # Térmica / protección hielo
    "heat": ["heat"],
    "deice": ["de-ice", "defrost"]
}

# Sustantivos técnicos específicos del dominio de palas eólicas.
# Se usan como "target" de los verbos de función (verb + noun).
# Se agrupan para poder validar relevancia temática.
FUNCTION_NOUNS = [
    # Energía y potencia aerodinámica
    "wind energy", "kinetic energy", "aerodynamic torque", "rotor torque",
    "power output", "energy capture",

    # Aerodinámica
    "lift", "drag", "lift coefficient", "drag coefficient",
    "lift-to-drag ratio", "aerodynamic lift", "aerodynamic drag",
    "thrust", "airflow", "air flow", "boundary layer", "flow separation",
    "turbulence", "vortex", "vortices", "wake", "angle of attack",
    "aerodynamic efficiency", "aerodynamic performance", "aerodynamic profile",
    "chord length", "camber", "twist", "blade pitch", "pitch angle",

    # Estructural
    "structural load", "aerodynamic load", "fatigue load", "gust load",
    "stress", "strain", "deflection", "bending moment", "torsion",
    "vibration", "flutter", "fatigue life", "structural integrity", "blade stiffness",

    # Protección / ambiental
    "ice", "ice accretion", "icing", "lightning strike",
    "erosion", "leading edge erosion", "corrosion",

    # Ruido
    "aerodynamic noise", "acoustic emission", "noise emission"
]

# ═══════════════════════════════════════════════════════════════
# UBICACIONES (L) - Términos de posición específicos del aspa
# Se eliminaron preposiciones y direcciones genéricas
# ("upper", "lower", "top", "bottom", "near", "between", "along")
# que producían demasiado ruido.
# ═══════════════════════════════════════════════════════════════

LOCATION_TERMS = {
    # Spanwise (a lo largo del aspa)
    "spanwise": [
        "at the root", "root portion", "root region", "near the root",
        "at the tip", "tip region", "tip portion", "near the tip",
        "at mid-span", "mid-span region",
        "inboard section", "outboard section", "inboard of", "outboard of",
        "radially inward", "radially outward", "along the span", "spanwise direction"
    ],

    # Chordwise (a lo largo de la cuerda)
    "chordwise": [
        "at the leading edge", "leading edge region", "near the leading edge",
        "at the trailing edge", "trailing edge region", "near the trailing edge",
        "at quarter chord", "at the quarter-chord", "chordwise position",
        "along the chord"
    ],

    # Lados aerodinámicos
    "sides": [
        "on the pressure side", "on the suction side",
        "pressure side of the blade", "suction side of the blade",
        "upper surface of the blade", "lower surface of the blade"
    ],

    # Capas / profundidad
    "depth": [
        "outer surface of the blade", "inner surface of the blade",
        "outer layer", "inner layer", "outer skin", "inner skin",
        "within the blade", "inside the blade", "within the shell"
    ],

    # Ubicaciones estructurales específicas
    "structural_zones": [
        "spar cap region", "shear web region", "bonding line region",
        "root bolt circle", "airfoil area", "transition area"
    ]
}

# ═══════════════════════════════════════════════════════════════
# REQUISITOS (R) - Problemas a resolver / objetivos
# Se listan los verbos base. El extractor genera el patrón completo
# manejando conjugaciones (improve → improves/improved/improving) y
# limitando la captura a 3 palabras para evitar fragmentos amplios.
# ═══════════════════════════════════════════════════════════════

REQUIREMENT_VERBS = [
    "improve", "increase", "reduce", "prevent", "avoid",
    "enhance", "minimize", "maximize", "mitigate", "eliminate",
    "optimize"
]

# Categorías de requisitos comunes (objetivos de diseño).
# Solo términos específicos y no ambiguos.
TARGET_REQUIREMENTS = {
    "aerodynamic_efficiency": ["aerodynamic efficiency", "aerodynamic performance",
                                "lift-to-drag ratio", "power output", "energy capture"],
    "structural_strength": ["structural strength", "blade stiffness", "structural integrity",
                             "load capacity", "bending strength"],
    "weight": ["blade weight", "structural weight", "blade mass"],
    "noise": ["aerodynamic noise", "acoustic emission", "noise emission"],
    "ice": ["ice accretion", "icing", "ice formation", "ice buildup"],
    "lightning": ["lightning strike", "lightning protection"],
    "fatigue": ["fatigue life", "fatigue damage", "service life", "fatigue strength"],
    "manufacturing_cost": ["manufacturing cost", "production cost", "tooling cost"],
    "erosion": ["leading edge erosion", "blade erosion", "rain erosion"],
    "flow_control": ["flow separation", "stall", "turbulence", "boundary layer separation"],
    "loads": ["fatigue load", "gust load", "aerodynamic load", "structural load"]
}

# ═══════════════════════════════════════════════════════════════
# FILTROS DE CALIDAD
# Se usan en el extractor para descartar entidades triviales
# (p.ej. "improve the blade", "reduce the one", "enhance its").
# ═══════════════════════════════════════════════════════════════

# Palabras aisladas que, si son la única cosa capturada tras el verbo,
# indican un match trivial y deben descartarse.
STOP_CAPTURES = {
    "the", "a", "an", "its", "their", "this", "that", "these", "those",
    "one", "two", "some", "any", "each", "every", "such", "said",
    "first", "second", "third", "fourth",
    "invention", "disclosure", "embodiment", "aspect", "present",
    "method", "system", "apparatus", "device", "means",
    "it", "them", "which", "who", "whose", "whereby",
    "thereof", "thereto", "therein", "hereof", "above", "below",
    "is", "are", "be", "been", "being", "of", "to", "for", "with",
    "and", "or", "but", "as", "at", "by", "in", "on", "so",
    "part", "portion", "section", "area"
}

# Términos que indican relevancia de dominio (aerogeneradores/palas eólicas).
# Estrategia: para evitar que palabras sueltas ambiguas ("mounting", "bonding",
# "heating", etc. — que vienen de frases como "mounting flange" o "heating
# element") hagan pasar fragmentos genéricos como "mounting on a", se aceptan:
#   - FRASES MULTI-PALABRA completas de los diccionarios (muy específicas).
#   - Un set curado de palabras mono-palabra realmente distintivas del dominio.

# Frases multi-palabra extraídas de los diccionarios (nada genérico).
def _build_domain_phrases():
    phrases = set()
    for variants in STRUCTURES.values():
        for v in variants:
            if " " in v or "-" in v:
                phrases.add(v.lower())
    for n in FUNCTION_NOUNS:
        if " " in n or "-" in n:
            phrases.add(n.lower())
    for variants in TARGET_REQUIREMENTS.values():
        for v in variants:
            if " " in v or "-" in v:
                phrases.add(v.lower())
    return phrases


# Palabras mono-palabra que, por sí solas, ya indican claramente el dominio.
# Se incluyen términos que en el contexto de patentes de palas eólicas
# casi siempre refieren al dominio (load, gust, noise, ice…).
STRICT_DOMAIN_WORDS = {
    # Componentes y geometría
    "blade", "airfoil", "aerofoil", "rotor", "turbine", "hub",
    "spar", "shell", "skin", "winglet", "serration", "gurney",
    "pitch", "chord", "twist", "camber",
    "inboard", "outboard", "spanwise", "chordwise",

    # Aerodinámica
    "lift", "drag", "thrust", "torque",
    "airflow", "turbulence", "vortex", "wake", "stall",

    # Cargas y estructura
    "load", "loads", "gust", "gusts", "stress", "strain",
    "fatigue", "vibration", "flutter", "bending", "deflection",

    # Ambiental / protección
    "ice", "icing", "erosion", "lightning", "noise",

    # Materiales
    "fiberglass", "fibreglass", "composite", "epoxy", "laminate", "prepreg",
}

DOMAIN_PHRASES = _build_domain_phrases()

# Se mantiene el nombre para compatibilidad, ahora = phrases + strict words.
DOMAIN_RELEVANCE_TERMS = DOMAIN_PHRASES | STRICT_DOMAIN_WORDS


if __name__ == "__main__":
    print("=" * 60)
    print(" DICCIONARIOS DEL DOMINIO CARGADOS")
    print("=" * 60)
    print(f"✓ Estructuras: {len(STRUCTURES)} categorías, "
          f"{sum(len(v) for v in STRUCTURES.values())} variantes")
    print(f"✓ Verbos de función: {len(FUNCTION_VERBS)} categorías, "
          f"{sum(len(v) for v in FUNCTION_VERBS.values())} variantes")
    print(f"✓ Sustantivos de función: {len(FUNCTION_NOUNS)} términos")
    print(f"✓ Términos de ubicación: "
          f"{sum(len(v) for v in LOCATION_TERMS.values())} términos")
    print(f"✓ Verbos de requisito: {len(REQUIREMENT_VERBS)} base")
    print(f"✓ Requisitos objetivo: {len(TARGET_REQUIREMENTS)} categorías")
    print(f"✓ Términos de relevancia de dominio: {len(DOMAIN_RELEVANCE_TERMS)}")
    print(f"✓ Stop-captures: {len(STOP_CAPTURES)}")
    print("=" * 60)
