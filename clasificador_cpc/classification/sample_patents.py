# classification/sample_patents.py
"""
Datos de ejemplo de patentes para demostración del clasificador.
Usado por demo_classifier.py.
"""

SAMPLE_PATENTS = {
    "US8550777B2": {
        "patent_id": "US8550777B2",
        "title": "Wind turbine blade with serrated trailing edge",
        "abstract": "A wind turbine blade with improved aerodynamic performance.",
        "ipc_codes": ["F03D1/06"],
        "cpc_codes": ["F03D1/0633", "F05B2240/3042", "F05B2280/6003"],
    },
    "EP2343432A1": {
        "patent_id": "EP2343432A1",
        "title": "Composite blade structure and manufacturing method",
        "abstract": "Method for manufacturing composite wind turbine blades.",
        "ipc_codes": ["F03D1/06"],
        "cpc_codes": ["F03D1/0675", "F05B2280/2001", "F05B2230/60"],
    },
    "WO2015123456A1": {
        "patent_id": "WO2015123456A1",
        "title": "Blade pitch control and monitoring system",
        "abstract": "System for controlling and monitoring pitch of wind turbine blades.",
        "ipc_codes": ["F03D7/02"],
        "cpc_codes": ["F03D7/0224", "F03D17/00", "F05B2270/328"],
    },
}


def get_all_sample_ids():
    """Devuelve la lista de IDs de patentes de ejemplo."""
    return list(SAMPLE_PATENTS.keys())
