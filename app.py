import streamlit as st
import json
import shutil
from storage import save_record
from taxonomy import TAXONOMY
from classifier import classify_po
import pandas as pd
from batch_processor import process_csv
from analytics import load_data, spend_by_category, not_sure_percentage
from storage import init_db

init_db()

st.divider()
st.header("📊 Analytics Dashboard")

df = load_data()

if df.empty:
    st.info("No classification data available yet.")
else:
    st.subheader("Spend Distribution by Category")
    category_df = spend_by_category(df)
    st.bar_chart(category_df.set_index("L2")["count"])

    st.subheader("Uncertain Classifications")
    pct = not_sure_percentage(df)
    st.metric("Not Sure %", f"{pct:.2f}%")

    st.subheader("Recent Classifications")
    st.dataframe(df.tail(10))


st.sidebar.header("⚙️ Admin: Taxonomy Control")

uploaded_taxonomy = st.sidebar.file_uploader(
    "Upload new taxonomy.json", type=["json"]
)

if uploaded_taxonomy:
    with open("taxonomy.json", "wb") as f:
        shutil.copyfileobj(uploaded_taxonomy, f)
    st.sidebar.success("Taxonomy updated. Restart app to apply.")


st.divider()
st.header("📂 Batch PO Classification")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

supplier_column = st.text_input(
    "Supplier column name (optional, must match CSV header)"
)

if uploaded_file:
    if st.button("Process File"):
        with st.spinner("Processing batch..."):
            result_df = process_csv(uploaded_file, supplier_column)

        st.success("Batch classification completed")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download classified CSV",
            csv,
            "classified_pos.csv",
            "text/csv"
        )


def get_taxonomy_options():
    options = {"L1": set(), "L2": set(), "L3": set()}
    lines = TAXONOMY.strip().splitlines()[2:]

    for line in lines:
        l1, l2, l3 = [p.strip() for p in line.split("|")]
        options["L1"].add(l1)
        options["L2"].add(l2)
        if l3 != "-":
            options["L3"].add(l3)

    return options


st.set_page_config(page_title="PO Category Classifier", layout="centered")

st.title("📦 PO L1–L2–L3 Classifier")

po_description = st.text_area("PO Description", height=120)
supplier = st.text_input("Supplier (optional)")

CONFIDENCE_THRESHOLD = 0.75

if st.button("Classify"):
    if not po_description.strip():
        st.warning("Please enter a PO description.")
    else:
        with st.spinner("Classifying..."):
            result = json.loads(classify_po(po_description, supplier))

        st.subheader("🔍 Classification Result")
        st.json(result)

        confidence = result["confidence"]
        st.progress(confidence)
        st.write(f"**Confidence:** {confidence:.2f}")
        st.write(f"**Reason:** {result['reason']}")

        taxonomy_options = get_taxonomy_options()

        if confidence < CONFIDENCE_THRESHOLD:
            st.warning("Low confidence result — manual review required")

            l1 = st.selectbox("L1", sorted(taxonomy_options["L1"]))
            l2 = st.selectbox("L2", sorted(taxonomy_options["L2"]))
            l3 = st.selectbox("L3", sorted(taxonomy_options["L3"]))

            if st.button("Override & Save"):
                overridden = result.copy()
                overridden.update({"L1": l1, "L2": l2, "L3": l3})

                save_record(po_description, supplier, overridden, "Overridden")
                st.success("Classification overridden and saved")

        else:
            if st.button("Approve"):
                save_record(po_description, supplier, result, "Approved")
                st.success("Classification approved and saved")


