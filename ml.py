import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import joblib

MODEL_PATH = Path("artifacts") / "po_model.joblib"


@dataclass
class MLResult:
    l1: str
    l2: str
    l3: str
    confidence: float


def _safe_float(value: Optional[float], default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def load_model() -> Optional[dict]:
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def _build_text(po_description: str, supplier: str) -> str:
    supplier_text = supplier.strip() if supplier else ""
    if supplier_text:
        return f"{po_description}\nSupplier: {supplier_text}"
    return po_description


def predict_ml(
    model_bundle: dict,
    po_description: str,
    supplier: str,
    min_confidence: float = 0.55,
) -> Optional[MLResult]:
    if not model_bundle:
        return None

    vectorizer = model_bundle["vectorizer"]
    clf_l1 = model_bundle["clf_l1"]
    clf_l2 = model_bundle["clf_l2"]
    clf_l3 = model_bundle["clf_l3"]

    text = _build_text(po_description, supplier)
    X = vectorizer.transform([text])

    l1_probs = clf_l1.predict_proba(X)[0]
    l2_probs = clf_l2.predict_proba(X)[0]
    l3_probs = clf_l3.predict_proba(X)[0]

    l1_idx = int(l1_probs.argmax())
    l2_idx = int(l2_probs.argmax())
    l3_idx = int(l3_probs.argmax())

    l1 = clf_l1.classes_[l1_idx]
    l2 = clf_l2.classes_[l2_idx]
    l3 = clf_l3.classes_[l3_idx]

    l1_conf = _safe_float(l1_probs[l1_idx])
    l2_conf = _safe_float(l2_probs[l2_idx])
    l3_conf = _safe_float(l3_probs[l3_idx])

    confidence = min(l1_conf, l2_conf, l3_conf)
    if confidence < min_confidence:
        return None

    return MLResult(l1=l1, l2=l2, l3=l3, confidence=confidence)


def format_ml_json(po_description: str, result: MLResult) -> str:
    payload = {
        "po_description": po_description,
        "L1": result.l1,
        "L2": result.l2,
        "L3": result.l3,
    }
    return json.dumps(payload, ensure_ascii=False)
