import streamlit as st
from groq import Groq
from prompts import SYSTEM_PROMPT
from ml import load_model, predict_ml, format_ml_json

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

MODEL = "openai/gpt-oss-120b"
MIN_ML_CONFIDENCE = 0.55
MODEL_BUNDLE = load_model()

def classify_po(po_description: str, supplier: str = "Not provided"):
    ml_result = None
    if MODEL_BUNDLE is not None:
        ml_result = predict_ml(
            MODEL_BUNDLE,
            po_description=po_description,
            supplier=supplier,
            min_confidence=MIN_ML_CONFIDENCE,
        )

    if ml_result is not None:
        return format_ml_json(po_description, ml_result), "ml"

    user_prompt = f"""
PO Description:
{po_description}

Supplier:
{supplier}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content, "llm"
