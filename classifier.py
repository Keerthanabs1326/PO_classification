import streamlit as st
import json
from taxonomy import TAXONOMY
from groq import Groq
from prompts import SYSTEM_PROMPT
from cache import get_cached, set_cache
from supplier_knowledge import get_supplier_hint
from rules_engine import apply_rules, RULE_CONFIDENCE_THRESHOLD
import json




client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

MODEL = "openai/gpt-oss-120b"

def parse_taxonomy():
    valid = set()
    lines = TAXONOMY.strip().splitlines()[2:]  # skip header lines
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            valid.add(tuple(parts))
    return valid


VALID_TAXONOMY = parse_taxonomy()

REQUIRED_KEYS = {"po_description", "L1", "L2", "L3", "confidence", "reason"}

def validate_response(response_text: str):
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        return False, None

    if not REQUIRED_KEYS.issubset(data.keys()):
        return False, None

    # Validate confidence
    confidence = data["confidence"]
    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
        return False, None

    l1, l2, l3 = data["L1"], data["L2"], data["L3"]

    if "Not sure" in (l1, l2, l3):
        return True, data

    if (l1, l2, l3) in VALID_TAXONOMY:
        return True, data

    return False, None


def classify_po(po_description: str, supplier: str = "Not provided"):
    # 1️⃣ RULE ENGINE (fastest, cheapest)
    rule_result = apply_rules(po_description)
    if rule_result and rule_result["confidence"] >= RULE_CONFIDENCE_THRESHOLD:
        result = {
            "po_description": po_description,
            **rule_result
        }
        set_cache(po_description, supplier, result)
        return json.dumps(result)

    # 2️⃣ SUPPLIER INTELLIGENCE
    supplier_hint = get_supplier_hint(supplier)
    if supplier_hint:
        result = {
            "po_description": po_description,
            **supplier_hint
        }
        set_cache(po_description, supplier, result)
        return json.dumps(result)

    # 3️⃣ CACHE CHECK
    cached = get_cached(po_description, supplier)
    if cached:
        return json.dumps(cached)

    # 4️⃣ LLM (fallback)
    user_prompt = f"""
PO Description:
{po_description}

Supplier:
{supplier}
"""

    for _ in range(2):
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        content = response.choices[0].message.content
        is_valid, parsed = validate_response(content)

        if is_valid:
            set_cache(po_description, supplier, parsed)
            return json.dumps(parsed)

    fallback = {
        "po_description": po_description,
        "L1": "Not sure",
        "L2": "Not sure",
        "L3": "Not sure",
        "confidence": 0.0,
        "reason": "Fallback after rule, supplier, and LLM failure"
    }

    set_cache(po_description, supplier, fallback)
    result["taxonomy_version"] = TAXONOMY_VERSION
    return json.dumps(fallback)
    


def load_taxonomy():
    with open("taxonomy.json", "r", encoding="utf-8") as f:
        return json.load(f)

TAXONOMY_DATA = load_taxonomy()
TAXONOMY_VERSION = TAXONOMY_DATA["version"]
VALID_TAXONOMY = {
    (c["L1"], c["L2"], c["L3"]) for c in TAXONOMY_DATA["categories"]
}





