# Exemple conceptuel
UOM_TEMPLATES = {
    "METRIC_WEIGHT": [
        {"type": "WEIGHT", "name": "Kilogramme", "code": "kg", "is_reference": True, "ratio": 1.0},
        {"type": "WEIGHT", "name": "Gramme", "code": "g", "is_reference": False, "ratio": 0.001},
    ],
    "METRIC_LENGTH": [
        {"type": "LENGTH", "name": "Mètre", "code": "m", "is_reference": True, "ratio": 1.0},
        {"type": "LENGTH", "name": "Centimètre", "code": "cm", "is_reference": False, "ratio": 0.01},
    ]
}
