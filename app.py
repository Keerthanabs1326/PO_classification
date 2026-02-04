import difflib
import json
import streamlit as st
from classifier import classify_po

st.set_page_config(page_title="Unstruct2Struct", layout="wide")

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Literata:wght@400;500;600&display=swap');

      :root {
        --bg-1: #0f172a;
        --bg-2: #0b1220;
        --card: #ffffff;
        --ink: #0f172a;
        --muted: #475569;
        --accent: #ff6b35;
        --accent-2: #3b82f6;
        --border: #e2e8f0;
      }

      .stApp {
        background:
          radial-gradient(900px circle at 12% -10%, rgba(255, 107, 53, 0.15) 0%, rgba(15, 23, 42, 0) 55%),
          radial-gradient(900px circle at 85% 0%, rgba(59, 130, 246, 0.18) 0%, rgba(15, 23, 42, 0) 60%),
          linear-gradient(180deg, #f8fafc 0%, #eef2ff 70%, #f8fafc 100%);
      }

      .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2.5rem;
        font-family: "Literata", serif;
      }

      .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.3rem;
      }

      .brand {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--ink);
        letter-spacing: 0.02em;
      }

      .tagline {
        font-size: 0.9rem;
        color: var(--muted);
      }

      .hero {
        border-radius: 22px;
        padding: 1.8rem 2rem;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.94) 0%, rgba(239, 246, 255, 0.95) 100%);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
        margin-bottom: 1.5rem;
      }

      .hero h1 {
        font-family: "Space Grotesk", sans-serif;
        font-size: 2.6rem;
        line-height: 1.1;
        margin-bottom: 0.6rem;
      }

      .hero p {
        margin: 0;
        color: var(--muted);
        font-size: 1.02rem;
      }

      .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border-radius: 999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.78rem;
        background: rgba(255, 107, 53, 0.12);
        color: #9a3412;
        border: 1px solid rgba(255, 107, 53, 0.3);
        font-family: "Space Grotesk", sans-serif;
      }

      .panel {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.25rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
      }

      .panel-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.7rem;
      }

      .metric-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin-bottom: 1rem;
      }

      .metric-card {
        border-radius: 14px;
        padding: 0.7rem 0.9rem;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
      }

      .metric-label {
        font-size: 0.75rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }

      .metric-value {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--ink);
      }

      .stButton > button {
        border-radius: 12px;
        padding: 0.55rem 1rem;
        font-weight: 600;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="topbar">
      <div>
        <div class="brand">Unstruct2Struct</div>
        <div class="tagline">PO classifier that makes messy text actionable</div>
      </div>
      <div class="chip">Unstructured -> Structured</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Turn free-form purchase orders into clean L1-L2-L3 categories.</h1>
      <p>See what the model changed, why it decided, and how the structured output compares to the original request.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "po_description" not in st.session_state:
    st.session_state.po_description = ""
if "supplier" not in st.session_state:
    st.session_state.supplier = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "source" not in st.session_state:
    st.session_state.source = None

sample_options = {
    "Office supplies order": "Purchase 50 boxes of A4 paper, 20 toner cartridges, and 10 desk organizers for Q2 restock.",
    "IT services": "Monthly cloud hosting and managed database services for production workloads.",
    "Maintenance request": "Replace HVAC filters and schedule preventative maintenance for Building B.",
    "Logistics": "Arrange expedited freight shipment for 12 pallets to the Denver warehouse.",
}

left_col, right_col = st.columns([1, 1.1], gap="large")

with left_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Input</div>', unsafe_allow_html=True)

    sample_choice = st.selectbox("Load sample", list(sample_options.keys()))
    if st.button("Use sample"):
        st.session_state.po_description = sample_options[sample_choice]
        st.session_state.supplier = "Acme Supplies"

    with st.form("po_form"):
        po_description = st.text_area(
            "Unstructured PO text",
            height=200,
            placeholder="Paste or type the PO description here...",
            value=st.session_state.po_description,
        )
        supplier = st.text_input(
            "Supplier (optional)",
            placeholder="Supplier name",
            value=st.session_state.supplier,
        )
        submitted = st.form_submit_button("Convert to structured")

    if submitted:
        if not po_description.strip():
            st.warning("Please enter a PO description.")
        else:
            with st.spinner("Structuring..."):
                result, source = classify_po(po_description, supplier)
            st.session_state.result = result
            st.session_state.source = source
            st.session_state.po_description = po_description
            st.session_state.supplier = supplier

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Output</div>', unsafe_allow_html=True)

    if st.session_state.result is None:
        st.info("Run the conversion to see structured output and the change log.")
    else:
        result_text = st.session_state.result
        source = (st.session_state.source or "unknown").upper()

        additions = 0
        removals = 0
        structured = None
        try:
            parsed = json.loads(result_text)
            structured = json.dumps(parsed, indent=2, sort_keys=True)
            input_lines = st.session_state.po_description.strip().splitlines() or [""]
            output_lines = structured.splitlines()
            for line in difflib.ndiff(input_lines, output_lines):
                if line.startswith("+ ") and not line.startswith("++"):
                    additions += 1
                elif line.startswith("- ") and not line.startswith("--"):
                    removals += 1
        except Exception:
            structured = None

        st.markdown(
            f"""
            <div class="metric-row">
              <div class="metric-card">
                <div class="metric-label">Adds</div>
                <div class="metric-value">{additions}</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">Removes</div>
                <div class="metric-value">{removals}</div>
              </div>
              <div class="metric-card">
                <div class="metric-label">Source</div>
                <div class="metric-value">{source}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["Structured", "Changes"])
        with tabs[0]:
            if structured is not None:
                st.code(structured, language="json")
            else:
                st.error("Invalid model response")
                st.code(result_text, language="text")

        with tabs[1]:
            if structured is not None:
                diff = "\n".join(
                    difflib.unified_diff(
                        st.session_state.po_description.strip().splitlines() or [""],
                        structured.splitlines(),
                        fromfile="input",
                        tofile="structured",
                        lineterm="",
                    )
                )
                if diff.strip():
                    st.code(diff, language="diff")
                else:
                    st.success("No changes detected.")
            else:
                st.warning("Changes view is unavailable because the output is not valid JSON.")

    st.markdown("</div>", unsafe_allow_html=True)
