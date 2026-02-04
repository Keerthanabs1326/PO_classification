from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import joblib
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


MODEL_PATH = Path("artifacts") / "po_model.joblib"
DEFAULT_DATASET = "shubhammurtadak/po_extract_classification_exp1"


def _normalize(name: str) -> str:
    return name.strip().lower().replace(" ", "").replace("_", "")


def _find_column(columns: Iterable[str], candidates: Iterable[str]) -> Optional[str]:
    normalized = {_normalize(c): c for c in columns}
    for candidate in candidates:
        key = _normalize(candidate)
        if key in normalized:
            return normalized[key]
    # fall back to substring match
    for column in columns:
        col_norm = _normalize(column)
        for candidate in candidates:
            if _normalize(candidate) in col_norm:
                return column
    return None


def _pick_split(dataset) -> str:
    if hasattr(dataset, "keys"):
        for name in ("train", "training", "default"):
            if name in dataset:
                return name
        return list(dataset.keys())[0]
    return "train"


def _build_text(description: str, supplier: str) -> str:
    supplier_text = supplier.strip() if supplier else ""
    if supplier_text:
        return f"{description}\nSupplier: {supplier_text}"
    return description


def _prepare_rows(dataset, text_col: str, supplier_col: Optional[str], l1_col: str, l2_col: str, l3_col: Optional[str]):
    rows = []
    for row in dataset:
        description = str(row.get(text_col, "")).strip()
        if not description:
            continue

        supplier = str(row.get(supplier_col, "")).strip() if supplier_col else ""

        l1 = str(row.get(l1_col, "")).strip()
        l2 = str(row.get(l2_col, "")).strip()
        l3 = str(row.get(l3_col, "")).strip() if l3_col else ""

        if not l1 or not l2:
            continue

        if not l3:
            l3 = "Not sure"

        rows.append((_build_text(description, supplier), l1, l2, l3))
    return rows


def train(dataset_id: str) -> Dict:
    dataset = load_dataset(dataset_id)
    split = _pick_split(dataset)
    ds = dataset[split] if hasattr(dataset, "__getitem__") else dataset
    columns = ds.column_names

    text_col = _find_column(columns, ["po_description", "description", "item_description", "text", "po_text", "po_desc"])
    supplier_col = _find_column(columns, ["supplier", "vendor", "supplier_name", "vendor_name"])
    l1_col = _find_column(columns, ["l1", "level1", "category_l1"])
    l2_col = _find_column(columns, ["l2", "level2", "category_l2"])
    l3_col = _find_column(columns, ["l3", "level3", "category_l3"])

    if not text_col or not l1_col or not l2_col:
        raise ValueError(
            "Could not detect required columns. "
            f"Found columns: {columns}. "
            "Expected at least text + L1 + L2."
        )

    rows = _prepare_rows(ds, text_col, supplier_col, l1_col, l2_col, l3_col)
    if not rows:
        raise ValueError("No usable rows found after filtering.")

    texts, l1_labels, l2_labels, l3_labels = zip(*rows)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    X = vectorizer.fit_transform(texts)

    clf_l1 = LogisticRegression(max_iter=1000)
    clf_l2 = LogisticRegression(max_iter=1000)
    clf_l3 = LogisticRegression(max_iter=1000)

    clf_l1.fit(X, l1_labels)
    clf_l2.fit(X, l2_labels)
    clf_l3.fit(X, l3_labels)

    model_bundle = {
        "vectorizer": vectorizer,
        "clf_l1": clf_l1,
        "clf_l2": clf_l2,
        "clf_l3": clf_l3,
        "metadata": {
            "dataset_id": dataset_id,
            "text_col": text_col,
            "supplier_col": supplier_col,
            "l1_col": l1_col,
            "l2_col": l2_col,
            "l3_col": l3_col,
            "rows_used": len(rows),
        },
    }
    return model_bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--output", default=str(MODEL_PATH))
    args = parser.parse_args()

    model_bundle = train(args.dataset)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_bundle, output_path)

    metadata = model_bundle["metadata"]
    print(f"Model saved to {output_path}")
    print(f"Rows used: {metadata['rows_used']}")
    print(
        "Columns: "
        f"text={metadata['text_col']}, supplier={metadata['supplier_col']}, "
        f"L1={metadata['l1_col']}, L2={metadata['l2_col']}, L3={metadata['l3_col']}"
    )


if __name__ == "__main__":
    main()
