# supplier_knowledge.py

SUPPLIER_HINTS = {
    "microsoft": ("IT", "Software", "Subscription"),
    "google": ("IT", "Software", "Subscription"),
    "amazon web services": ("IT", "Software", "Subscription"),
    "aws": ("IT", "Software", "Subscription"),
    "dell": ("IT", "Hardware", "Laptop"),
    "hp": ("IT", "Hardware", "Laptop"),
    "indigo": ("T&E", "Air", "Not sure"),
    "air india": ("T&E", "Air", "Not sure"),
    "taj hotels": ("T&E", "Hotel", "Not sure"),
    "deloitte": ("Professional Services", "Consulting Services", "Not sure"),
    "ey": ("Professional Services", "Consulting Services", "Not sure"),
    "pwc": ("Professional Services", "Consulting Services", "Not sure"),
}

def get_supplier_hint(supplier: str):
    if not supplier:
        return None

    supplier_lower = supplier.lower()

    for key, category in SUPPLIER_HINTS.items():
        if key in supplier_lower:
            return {
                "L1": category[0],
                "L2": category[1],
                "L3": category[2],
                "confidence": 0.9,
                "reason": f"Supplier '{supplier}' strongly associated with this category"
            }

    return None
