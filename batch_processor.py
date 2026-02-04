import pandas as pd
from classifier import classify_po
import json

def process_csv(file, supplier_column=None):
    """
    file: uploaded CSV file
    supplier_column: optional column name for supplier
    """

    df = pd.read_csv(file)

    results = []

    for _, row in df.iterrows():
        po_description = str(row["po_description"])

        supplier = (
            str(row[supplier_column])
            if supplier_column and supplier_column in df.columns
            else "Not provided"
        )

        classification = json.loads(classify_po(po_description, supplier))

        combined = {
            **row.to_dict(),
            "L1": classification["L1"],
            "L2": classification["L2"],
            "L3": classification["L3"],
            "confidence": classification["confidence"],
            "reason": classification["reason"],
        }

        results.append(combined)

    return pd.DataFrame(results)
