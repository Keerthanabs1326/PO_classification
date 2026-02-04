# supplier_knowledge.py

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
}

def get_supplier_hint(supplier: str):
    if not supplier:
        return None

    supplier = supplier.lower()

    for key, (l1, l2, l3) in SUPPLIER_HINTS.items():
        if key in supplier:
            return {
                "L1": l1,
                "L2": l2,
                "L3": l3,
                "confidence": 0.9,
                "reason": f"Supplier '{supplier}' strongly associated with this category"
            }

    return None
