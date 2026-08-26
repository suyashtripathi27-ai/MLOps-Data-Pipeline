"""
streamlit_app.py

Live, interactive demo of the MLOps Data Pipeline's LOCAL, deterministic layer:
industry classification, data cleaning, KPI generation, and governance/
confidence scoring — all running instantly in the browser, at zero API cost,
because none of it calls an LLM.

Deliberately does NOT call the AI report-generation step. Wiring a public demo
to a personal Gemini/Groq API key means any visitor's upload could burn your
quota or run up cost with no control. Instead, this shows a curated set of
real, previously-generated executive reports as examples of the final output.

This split is not a workaround for a missing feature — it's the actual point
of this pipeline's architecture: the parts that matter for security and
correctness (what industry is this, what are the real numbers, what's missing
or unreliable) run entirely without AI, and only the narrative writing stage
ever touches a model.

Deploy: push this to your repo root, connect the repo at
share.streamlit.io, set the main file to streamlit_app.py. No secrets needed —
this app never calls an external API.
"""

import streamlit as st
import pandas as pd
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bootstrap  # noqa: F401

from utils.cleaner import load_and_clean, universal_clean
from utils.profiler import generate_payload
from main import detect_industry

st.set_page_config(page_title="MLOps Data Pipeline — Live Demo", layout="wide")

st.title("MLOps Data Pipeline")
st.caption(
    "Upload a CSV, Excel, or ZIP file and watch the fully local, deterministic part of "
    "this pipeline run live: industry classification, data cleaning, KPI "
    "generation, and governance scoring — with zero AI calls, zero API cost, "
    "and your file never leaving this session."
)

tab_demo, tab_examples, tab_about = st.tabs(["Try it live", "Example reports", "How this works"])

# ---------------------------------------------------------------------------
with tab_demo:
    uploaded = st.file_uploader("Upload a CSV, Excel, or ZIP file", type=["csv", "xlsx", "xls", "zip"])

    if uploaded is not None:
        tmp_path = os.path.join("/tmp", uploaded.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())

        with st.spinner("Cleaning and mapping schema..."):
            try:
                df = load_and_clean(tmp_path)
                df = universal_clean(df)
            except Exception as e:
                st.error(f"Couldn't load this file: {e}")
                st.stop()

        st.success(f"Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")

        with st.spinner("Classifying industry (local keyword scoring, no AI)..."):
            industry = detect_industry(df.columns.tolist(), uploaded.name)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Detected Industry", industry.upper())
        with col2:
            payload = generate_payload(df, industry_context=industry)
            score = payload.get("data_reliability_score", "N/A")
            st.metric("Data Reliability Score", f"{score}/100" if score != "N/A" else "N/A")

        if payload.get("system_warnings"):
            with st.expander("⚠️ Data integrity warnings"):
                for w in payload["system_warnings"]:
                    st.write(f"- {w}")

        st.subheader("KPI Generation")
        try:
            import importlib
            ROUTER_MAP = {
                "logistics": "industries.logistics.pipeline",
                "retail": "industries.retail.pipeline",
                "banking": "industries.banking.pipeline",
                "pharma": "industries.pharma.pipeline",
                "finance": "industries.finance.pipeline",
                "manufacturing": "industries.manufacturing.pipeline",
                "ecommerce": "industries.ecommerce.pipeline",
                "hr": "industries.hr.pipeline",
            }
            mod = importlib.import_module(ROUTER_MAP[industry])
            kpis = mod.generate_dynamic_kpis(df)

            kpi_df = pd.DataFrame(kpis)
            if not kpi_df.empty:
                display_cols = [c for c in ["category", "name", "value", "confidence", "warnings"] if c in kpi_df.columns]
                st.dataframe(kpi_df[display_cols], use_container_width=True, height=400)
                st.caption(f"{len(kpi_df)} KPIs generated — entirely locally, no AI involved in this step.")
            else:
                st.info("No KPIs generated for this schema.")
        except Exception as e:
            st.warning(f"KPI generation hit an issue: {e}")

        st.info(
            "This is as far as the live demo goes on purpose — see the "
            "**Example reports** tab for what the AI-written executive summary "
            "looks like once these KPIs are handed to it.",
            icon="ℹ️",
        )

# ---------------------------------------------------------------------------
with tab_examples:
    st.write("Real reports generated by this pipeline from real datasets — not fabricated for this demo.")
    report_files = sorted(glob.glob("data/outputs/reports/*.md"))
    if report_files:
        chosen = st.selectbox("Pick a report to view", report_files, format_func=lambda p: os.path.basename(p))
        with open(chosen, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.write("No example reports bundled with this deployment yet.")

# ---------------------------------------------------------------------------
with tab_about:
    st.markdown("""
    ### Why this demo doesn't call AI live

    Classification, cleaning, KPI computation, and governance scoring are all
    deterministic Python running against a curated schema library — no model,
    no API call, no cost, and no data ever leaves this session. That's also
    the actual security property of the underlying pipeline: your raw file is
    never sent anywhere for the analysis that matters most.

    The only step that uses an LLM is turning the KPIs above into an
    executive-readable narrative — see the **Example reports** tab for real
    output from that stage.

    [Full source & architecture on GitHub](https://github.com/suyashtripathi27-ai/MLOps-Data-Pipeline)
    """)
