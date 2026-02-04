# rules_engine.py

RULES = [
    {
        "keywords": ["flight", "air ticket", "airfare"],
        "result": ("T&E", "Air", "Not sure"),
        "confidence": 0.95,
        "reason": "Flight-related keywords detected"
    },
    {
        "keywords": ["hotel", "accommodation", "stay"],
        "result": ("T&E", "Hotel", "Not sure"),
        "confidence": 0.9,
        "reason": "Hotel-related expense detected"
    },
    {
        "keywords": ["insurance", "policy premium"],
        "result": ("Banking & Financial", "Insurance", "Not sure"),
        "confidence": 0.95,
        "reason": "Insurance-related keywords detected"
    },
    {
        "keywords": ["laptop", "notebook", "macbook"],
        "result": ("IT", "Hardware", "Laptop"),
        "confidence": 0.9,
        "reason": "Hardware purchase keywords detected"
    },
]

RULE_CONFIDENCE_THRESHOLD = 0.9

def apply_rules(po_description: str):
    text = po_description.lower()

    for rule in RULES:
        if any(keyword in text for keyword in rule["keywords"]):
            return {
                "L1": rule["result"][0],
                "L2": rule["result"][1],
                "L3": rule["result"][2],
                "confidence": rule["confidence"],
                "reason": rule["reason"]
            }

    return None
