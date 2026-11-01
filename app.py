from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from omicsguard.ingestion import load_geo_dataset
from omicsguard.integrity_checks import run_integrity_checks
from omicsguard.anomaly_detection import run_pca, detect_anomalies
from omicsguard.reporting import save_anomaly_reports
from omicsguard.benchmark import run_fault_injection_benchmark
from omicsguard.leakage_audit import run_leakage_audit
from omicsguard.audit_history import save_audit_history, get_audit_history


# ==================================================
# PAGE CONFIGURATION + VISUAL SYSTEM
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent
RAW_FILE = PROJECT_ROOT / "data/raw/GSE10072_series_matrix.txt.gz"
PROCESSED_DIR = PROJECT_ROOT / "data/processed"
EXPRESSION_FILE = PROCESSED_DIR / "GSE10072_expression.csv"
METADATA_FILE = PROCESSED_DIR / "GSE10072_metadata.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
BENCHMARK_DIR = RESULTS_DIR / "benchmark"


from dashboard_ui import (
    apply_dashboard_style,
    render_dashboard_header,
    render_upload_toolbar,
    render_dashboard_overview,
)
st.set_page_config(
    page_title="OmicsGuard AI | Research Auditor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_dashboard_style()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --ink: #17243a;
        --muted: #718096;
        --teal: #12a89d;
        --teal-dark: #087e79;
        --line: #e4eaf0;
        --surface: #ffffff;
        --canvas: #f4f7fa;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--canvas);
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(244,247,250,0.88);
    }

    [data-testid="stSidebar"] {
        background: #101d31;
        border-right: 1px solid #20314a;
    }
    [data-testid="stSidebar"] * {
        color: #e8f0f7 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.055);
        padding: 0.55rem 0.7rem;
        border-radius: 10px;
        margin: 0.12rem 0;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(18,168,157,0.16);
        border-color: rgba(18,168,157,0.35);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-weight: 600;
        font-size: 0.88rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.13);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2.1rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        color: var(--ink);
        letter-spacing: -0.035em;
    }
    h1 { font-weight: 800 !important; }
    h2 { font-weight: 750 !important; }
    h3 { font-weight: 700 !important; }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 0.25rem 0 1.15rem 0;
    }
    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 13px;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg,#16c6b6,#087e79);
        color: white;
        font-size: 1.45rem;
        box-shadow: 0 8px 22px rgba(18,168,157,.22);
    }
    .brand-name {
        color: #ffffff;
        font: 800 1.13rem 'Manrope',sans-serif;
        letter-spacing: -0.04em;
    }
    .brand-sub {
        color: #9aacc1;
        font-size: .68rem;
        margin-top: 1px;
        letter-spacing: .08em;
        text-transform: uppercase;
    }
    .sidebar-label {
        color: #7f93aa !important;
        font-size: .68rem;
        font-weight: 700;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin: .6rem 0 .45rem 0;
    }
    .sidebar-dataset {
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.09);
        border-radius: 13px;
        padding: 13px;
        margin-top: 1.1rem;
    }
    .sidebar-dataset .small {
        color: #9aacc1 !important;
        font-size: .72rem;
    }
    .sidebar-dataset .value {
        color: #ffffff !important;
        font-size: .92rem;
        font-weight: 700;
        margin: 3px 0 9px;
    }

    .hero {
        background: linear-gradient(115deg,#10223a 0%,#173653 58%,#087e79 130%);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 22px;
        padding: 30px 34px;
        color: white;
        margin: 0 0 1.4rem 0;
        box-shadow: 0 15px 38px rgba(20,45,70,.12);
        position: relative;
        overflow: hidden;
    }
    .hero:after {
        content: " ";
        position: absolute;
        width: 250px;
        height: 250px;
        right: -65px;
        top: -115px;
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 50%;
        box-shadow: 0 0 0 28px rgba(255,255,255,.025),
                    0 0 0 58px rgba(255,255,255,.02);
    }
    .hero-kicker {
        color: #75e2d6;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .7rem;
    }
    .hero-title {
        color: white;
        font: 800 clamp(1.65rem,3vw,2.45rem) 'Manrope',sans-serif;
        line-height: 1.13;
        letter-spacing: -.045em;
        max-width: 800px;
    }
    .hero-copy {
        color: #c6d5e4;
        max-width: 760px;
        font-size: .94rem;
        line-height: 1.65;
        margin-top: .8rem;
    }
    .hero-tag {
        display: inline-block;
        margin-top: 1.1rem;
        padding: 6px 10px;
        border: 1px solid rgba(117,226,214,.35);
        border-radius: 999px;
        color: #a6f1e8;
        font-size: .72rem;
        font-weight: 600;
    }

    .section-eyebrow {
        color: var(--teal-dark);
        font-size: .7rem;
        font-weight: 800;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .25rem;
    }
    .section-heading {
        color: var(--ink);
        font: 750 1.35rem 'Manrope',sans-serif;
        letter-spacing: -.035em;
        margin-bottom: .2rem;
    }
    .section-copy {
        color: var(--muted);
        font-size: .88rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 16px 17px;
        min-height: 105px;
        box-shadow: 0 3px 12px rgba(23,36,58,.025);
    }
    .metric-label {
        color: var(--muted);
        font-size: .75rem;
        font-weight: 600;
        margin-bottom: 9px;
    }
    .metric-value {
        color: var(--ink);
        font: 800 1.55rem 'Manrope',sans-serif;
        letter-spacing: -.045em;
    }
    .metric-note {
        color: #8a98a9;
        font-size: .69rem;
        margin-top: 3px;
    }

    .module-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 17px 18px;
        min-height: 150px;
        box-shadow: 0 3px 12px rgba(23,36,58,.025);
    }
    .module-icon {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 10px;
        background: #e8f8f6;
        color: #087e79;
        font-size: 1.05rem;
        margin-bottom: 11px;
    }
    .module-title {
        color: var(--ink);
        font: 700 .96rem 'Manrope',sans-serif;
        margin-bottom: 5px;
    }
    .module-copy {
        color: var(--muted);
        font-size: .78rem;
        line-height: 1.5;
    }

    .info-strip {
        border-left: 3px solid var(--teal);
        background: #eaf7f6;
        border-radius: 0 10px 10px 0;
        padding: 12px 15px;
        color: #315b61;
        font-size: .82rem;
        line-height: 1.55;
        margin: .7rem 0 1rem;
    }
    .subtle-panel {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 17px 18px;
    }
    .status-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        font-size: .68rem;
        font-weight: 800;
        letter-spacing: .04em;
    }
    .status-pass { background: #e7f7ef; color: #18794e; }
    .status-warn { background: #fff5df; color: #996400; }
    .status-fail { background: #ffebeb; color: #b42318; }
    .status-skip { background: #edf1f6; color: #596579; }

    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700;
        min-height: 2.65rem;
        border: 1px solid #d6e2e9;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(100deg,#0c9d93,#087e79);
        border: none;
        color: white;
        box-shadow: 0 5px 14px rgba(8,126,121,.18);
    }
    .stButton > button[kind="primary"]:hover {
        background: #086e6a;
        border: none;
        color: white;
    }
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px dashed #bdcbd6;
        border-radius: 12px;
        padding: 10px;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 11px;
        overflow: hidden;
    }
    div[data-testid="stAlert"] {
        border-radius: 11px;
    }
    .footer {
        color: #8a98a9;
        font-size: .72rem;
        border-top: 1px solid var(--line);
        padding-top: 1rem;
        margin-top: 2rem;
    }
    
    /* Reference dashboard layout overrides */
    [data-testid="stSidebar"] {display:none !important;}
    [data-testid="stHeader"] {background:transparent;}
    .block-container {max-width:1500px;padding-top:1.2rem;padding-bottom:3rem;}

    .reference-brand {
        display:flex;align-items:center;gap:13px;
        padding:5px 0 15px 0;
    }
    .reference-brand-mark {
        width:48px;height:48px;border-radius:14px;
        display:grid;place-items:center;
        color:white;font-size:25px;
        background:linear-gradient(135deg,#16c6b6,#087e79);
        box-shadow:0 8px 22px rgba(18,168,157,.22);
    }
    .reference-brand-name {
        color:#17243a;font:800 1.25rem 'Manrope',sans-serif;
    }
    .reference-brand-sub {
        color:#718096;font-size:.65rem;
        letter-spacing:.09em;text-transform:uppercase;
    }
    .reference-workspace {
        background:#e7f7f4;color:#087e79;
        padding:9px 13px;border-radius:999px;
        font-size:.7rem;font-weight:800;text-align:center;
        margin-top:5px;
    }
    .hero {
        background:
          radial-gradient(circle at 85% 35%,rgba(18,200,185,.25),transparent 28%),
          linear-gradient(110deg,#092b45 0%,#075565 65%,#087e79 120%);
        min-height:205px;
    }
    .hero:after {
        content:"🧬";position:absolute;
        width:auto;height:auto;right:7%;top:12px;
        border:0;border-radius:0;box-shadow:none;
        font-size:120px;opacity:.20;
    }
    .upload-card {
        border:1px solid #b9e6e4;
        box-shadow:0 5px 18px rgba(23,36,58,.05);
    }
    [data-testid="stFileUploaderDropzone"] {
        background:#f7ffff;border:1px solid #b8e6e5;
        border-radius:11px;padding:5px;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {display:none;}
    [data-testid="stFileUploaderDropzone"] svg {display:none;}
    .metric-card {
        border-radius:17px;min-height:125px;
        box-shadow:0 5px 18px rgba(23,36,58,.045);
    }
    .module-card,.quick-actions-card {
        border-radius:17px;
        box-shadow:0 5px 18px rgba(23,36,58,.04);
    }
    .stButton>button {
        border-radius:11px;
        transition:all .15s ease;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SHARED UI HELPERS
# ==================================================

def section_header(kicker, title, description):
    st.markdown(
        f"""
        <div style="margin: .25rem 0 1rem;">
            <div class="section-eyebrow">{kicker}</div>
            <div class="section-heading">{title}</div>
            <div class="section-copy">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_card(icon, title, description):
    st.markdown(
        f"""
        <div class="module-card">
            <div class="module-icon">{icon}</div>
            <div class="module-title">{title}</div>
            <div class="module-copy">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_status(result):
    status = result.get("status", "WARNING")
    label = result.get("check", "Audit check")
    css_class = {
        "PASS": "status-pass",
        "WARNING": "status-warn",
        "FAIL": "status-fail",
        "SKIPPED": "status-skip",
    }.get(status, "status-warn")
    st.markdown(
        f'<span class="status-pill {css_class}">{status}</span>'
        f'<span style="font-weight:700;color:#17243a;margin-left:9px">{label}</span>',
        unsafe_allow_html=True,
    )


# ==================================================
# DATA LOADING
# ==================================================

@st.cache_data(show_spinner="Loading GSE10072 dataset...")
def load_dataset():
    if EXPRESSION_FILE.exists() and METADATA_FILE.exists():
        expression = pd.read_csv(EXPRESSION_FILE, index_col=0)
        metadata = pd.read_csv(METADATA_FILE)
        expression.index = expression.index.astype(str)
        expression.columns = expression.columns.astype(str)
        return expression, metadata
    if RAW_FILE.exists():
        return load_geo_dataset(RAW_FILE)
    raise FileNotFoundError(
        "Processed CSV files or data/raw/GSE10072_series_matrix.txt.gz "
        "were not found."
    )


try:
    expression, metadata = load_dataset()
except Exception as error:
    st.error(f"Could not load the GSE10072 dataset: {error}")
    st.info(
        "Check the data/processed folder for the expression and metadata CSVs, "
        "or place the original GEO Series Matrix file in data/raw."
    )
    st.stop()


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-mark">🧬</div>
            <div>
                <div class="brand-name">OmicsGuard AI</div>
                <div class="brand-sub">Research data auditor</div>
            </div>
        </div>
        <div class="sidebar-label">Workspace</div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Integrity Audit",
            "Anomaly Analysis",
            "Fault-Injection Benchmark",
            "ML Leakage Audit",
            "Audit History",
        ],
        key="page",
        label_visibility="collapsed",
    )

    st.markdown(
        f"""
        <div class="sidebar-dataset">
            <div class="sidebar-label">Active dataset</div>
            <div class="value">GSE10072</div>
            <div class="small">NCBI Gene Expression Omnibus</div>
            <hr style="border-color:rgba(255,255,255,.12);margin:12px 0">
            <div class="small">SAMPLES</div>
            <div class="value">{expression.shape[0]:,}</div>
            <div class="small">PROBE FEATURES</div>
            <div class="value">{expression.shape[1]:,}</div>
            <div class="small">METADATA FIELDS</div>
            <div class="value" style="margin-bottom:0">{metadata.shape[1]:,}</div>
        </div>
        <div style="color:#7f93aa;font-size:.68rem;margin-top:1.2rem;line-height:1.5">
            SCIENCE FAIR EDITION · 2026<br>
            Local dataset mode
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# GLOBAL TOP STRIP
# ==================================================

st.markdown(
    """
    <div style="display:flex;justify-content:space-between;align-items:center;
                gap:12px;margin-bottom:1rem;flex-wrap:wrap">
        <div style="color:#718096;font-size:.76rem;font-weight:600;
                    letter-spacing:.07em;text-transform:uppercase">
            BIOINFORMATICS · DATA QUALITY · MODEL RELIABILITY
        </div>
        <div style="background:#e7f7f4;color:#087e79;padding:6px 11px;
                    border-radius:999px;font-size:.7rem;font-weight:800">
            ● LOCAL ANALYSIS WORKSPACE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



# ==================================================
# OVERVIEW
# ==================================================

if page == "Overview":

    # ----------------------------------------------
    # METADATA SUMMARY
    # ----------------------------------------------

    tissue_column = "source_name_ch1"
    smoking_column = "characteristic_Cigarette Smoking Status"

    tissue_counts = (
        metadata[tissue_column].fillna("Unknown").value_counts()
        if tissue_column in metadata.columns
        else pd.Series(dtype=int)
    )

    smoking_counts = (
        metadata[smoking_column].fillna("Unknown").value_counts()
        if smoking_column in metadata.columns
        else pd.Series(dtype=int)
    )

    total_samples = len(expression)
    total_features = expression.shape[1]
    missing_values = int(expression.isna().sum().sum())

    unique_sample_ids = (
        metadata["sample_id"].nunique()
        if "sample_id" in metadata.columns
        else 0
    )

    tissue_labelled = (
        int(metadata[tissue_column].notna().sum())
        if tissue_column in metadata.columns
        else 0
    )

    # ----------------------------------------------
    # HERO
    # ----------------------------------------------

    
    st.markdown(
        """
<div class="hero">
    <div class="hero-kicker">Scientific data quality platform</div>
    <div class="hero-title">Trust your omics data.<br>Audit before you analyse.</div>
    <div class="hero-copy">
        An integrated bioinformatics platform to evaluate
        expression data integrity, explore unusual sample
        profiles, benchmark defect detection and screen
        machine-learning leakage signals.
    </div>
    <div class="hero-tag">
        GSE10072 · LUNG ADENOCARCINOMA EXPRESSION DATA
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


    # ----------------------------------------------
    # DATASET SNAPSHOT
    # ----------------------------------------------

    section_header(
        "Dataset snapshot",
        "Your analysis workspace",
        "Verified information from the currently loaded GSE10072 dataset.",
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total samples",
            f"{total_samples:,}",
            "Expression profiles",
        )

    with c2:
        metric_card(
            "Probe features",
            f"{total_features:,}",
            "Measured features",
        )

    with c3:
        metric_card(
            "Metadata fields",
            f"{metadata.shape[1]:,}",
            "Sample annotations",
        )

    with c4:
        metric_card(
            "Missing expression values",
            f"{missing_values:,}",
            "In expression matrix",
        )

    st.write("")

    # ----------------------------------------------
    # SAMPLE QUALITY INDICATORS
    # ----------------------------------------------

    section_header(
        "Metadata quality",
        "Sample annotation checks",
        "Basic descriptive checks on the loaded sample metadata.",
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        metric_card(
            "Unique sample IDs",
            f"{unique_sample_ids:,}/{len(metadata):,}",
            "Metadata identifier uniqueness",
        )

    with q2:
        metric_card(
            "Tissue labels available",
            f"{tissue_labelled:,}/{len(metadata):,}",
            "Samples with tissue annotations",
        )

    with q3:
        smoking_labelled = (
            int(metadata[smoking_column].notna().sum())
            if smoking_column in metadata.columns
            else 0
        )

        metric_card(
            "Smoking labels available",
            f"{smoking_labelled:,}/{len(metadata):,}",
            "Samples with smoking annotations",
        )

    # ----------------------------------------------
    # BIOLOGICAL SAMPLE DISTRIBUTION
    # ----------------------------------------------

    st.write("")

    section_header(
        "Biological composition",
        "Understand the sample population",
        "Explore the tissue categories and smoking-status annotations reported in GEO.",
    )

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        st.markdown("**Tissue type distribution**")

        if not tissue_counts.empty:

            tissue_df = tissue_counts.rename_axis(
                "Tissue type"
            ).reset_index(name="Samples")

            tissue_fig = px.pie(
                tissue_df,
                names="Tissue type",
                values="Samples",
                hole=0.58,
                color="Tissue type",
                color_discrete_map={
                    "Adenocarcinoma of the Lung": "#0b8f87",
                    "Normal Lung Tissue": "#e5a34b",
                    "Unknown": "#9aa7b5",
                },
            )

            tissue_fig.update_traces(
                textposition="inside",
                textinfo="percent+value",
                marker=dict(
                    line=dict(color="white", width=3)
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Samples: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                ),
            )

            tissue_fig.update_layout(
                height=370,
                showlegend=True,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=20, b=10),
                legend_title_text="Tissue category",
            )

            st.plotly_chart(
                tissue_fig,
                use_container_width=True,
            )

            st.dataframe(
                tissue_df,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.warning(
                "Tissue type metadata column was not found."
            )

    with chart_right:
        st.markdown("**Smoking-status distribution**")

        if not smoking_counts.empty:

            smoking_df = smoking_counts.rename_axis(
                "Smoking status"
            ).reset_index(name="Samples")

            smoking_fig = px.bar(
                smoking_df,
                x="Smoking status",
                y="Samples",
                color="Smoking status",
                text="Samples",
                color_discrete_map={
                    "Current Smoker": "#0b8f87",
                    "Former Smoker": "#e5a34b",
                    "Never Smoked": "#5279a8",
                    "Unknown": "#9aa7b5",
                },
            )

            smoking_fig.update_traces(
                textposition="outside",
                marker_line_width=0,
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    "Samples: %{y}"
                    "<extra></extra>"
                ),
            )

            smoking_fig.update_layout(
                height=370,
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#fbfcfd",
                margin=dict(l=10, r=10, t=25, b=10),
                xaxis_title="Smoking status",
                yaxis_title="Number of samples",
                yaxis=dict(
                    rangemode="tozero",
                    gridcolor="#e8edf2",
                ),
            )

            st.plotly_chart(
                smoking_fig,
                use_container_width=True,
            )

            st.dataframe(
                smoking_df,
                use_container_width=True,
                hide_index=True,
            )

        else:
            st.warning(
                "Smoking-status metadata column was not found."
            )

    # ----------------------------------------------
    # PLATFORM MODULES
    # ----------------------------------------------

    st.write("")

    section_header(
        "Platform modules",
        "Five ways to inspect data reliability",
        "Select a module from the navigation panel to start an analysis.",
    )

    cards = st.columns(5, gap="medium")

    modules = [
        (
            "✓",
            "Integrity audit",
            "Check missing values, duplicate IDs, constant features and metadata consistency.",
            "Integrity Audit",
        ),
        (
            "◉",
            "Anomaly analysis",
            "Explore sample variation using PCA and Isolation Forest.",
            "Anomaly Analysis",
        ),
        (
            "⌁",
            "Fault benchmark",
            "Evaluate checks against deliberately injected defects.",
            "Fault-Injection Benchmark",
        ),
        (
            "⇄",
            "Leakage screening",
            "Screen train/test overlap and selected leakage signals.",
            "ML Leakage Audit",
        ),
        (
            "▤",
            "Audit history",
            "Review previous analysis runs and recorded summaries.",
            "Audit History",
        ),
    ]

    for column, (icon, title, description, target_page) in zip(cards, modules):
        with column:
            module_card(icon, title, description)

            st.button(
                f"Open {title} →",
                key=f"open_{target_page}",
                use_container_width=True,
                on_click=lambda target=target_page: st.session_state.update(
                    page=target
                ),
            )

    # ----------------------------------------------
    # DATA PREVIEW
    # ----------------------------------------------

    st.write("")

    left, right = st.columns([1.25, 1], gap="large")

    with left:
        section_header(
            "Data preview",
            "Expression matrix",
            "First eight samples and eight probe features.",
        )

        st.dataframe(
            expression.iloc[:8, :8],
            use_container_width=True,
            height=285,
        )

    with right:
        section_header(
            "Sample annotations",
            "Metadata preview",
            "First eight records from the GEO sample annotations.",
        )

        st.dataframe(
            metadata.head(8),
            use_container_width=True,
            height=285,
        )

    # ----------------------------------------------
    # DATASET INFORMATION
    # ----------------------------------------------

    st.write("")

    with st.expander("Dataset information and scientific context"):

        st.markdown(
            """
            **Dataset accession:** GSE10072

            **Source:** NCBI Gene Expression Omnibus (GEO)

            **Organism:** Homo sapiens

            **Platform:** GPL96 — Affymetrix Human Genome U133A Array

            **Expression features:** 22,283 probes

            **Samples:** 107

            **Tissue categories:** Lung adenocarcinoma and normal lung tissue

            **Expression processing:** Robust Multi-array Average (RMA),
            as described in the GEO metadata.
            """
        )

    # ----------------------------------------------
    # SCIENTIFIC INTERPRETATION
    # ----------------------------------------------

    st.markdown(
        """
        <div class="info-strip">
            <strong>Scientific interpretation:</strong>
            These charts describe the available dataset annotations.
            They do not establish causal relationships between smoking
            and cancer. An anomaly flag is a model-generated screening
            result, not proof of a defective biological sample.
            Further statistical and biological validation is required.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# INTEGRITY AUDIT
# ==================================================

elif page == "Integrity Audit":
    section_header(
        "Module 01 · Data validation",
        "Dataset integrity audit",
        "Run five rule-based checks against the loaded expression matrix and metadata.",
    )
    left, right = st.columns([1.3, 1], gap="large")
    with left:
        st.markdown(
            """
            <div class="subtle-panel">
                <strong style="color:#17243a">Checks included</strong>
                <ul style="color:#718096;font-size:.86rem;line-height:1.9;margin-bottom:0">
                    <li>Missing expression values</li>
                    <li>Duplicate sample identifiers</li>
                    <li>Duplicate probe identifiers</li>
                    <li>Constant expression features</li>
                    <li>Expression-to-metadata sample consistency</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="subtle-panel">
                <div class="section-eyebrow">Input dataset</div>
                <div style="font-size:1.5rem;font-weight:800;color:#17243a">GSE10072</div>
                <div style="font-size:.8rem;color:#718096">
                    Sample-by-feature expression matrix
                </div>
                <hr style="border-color:#e4eaf0">
                <div style="font-size:.82rem;color:#526174">
                    <b>Matrix:</b> {:,} × {:,}<br>
                    <b>Metadata:</b> {:,} rows
                </div>
            </div>
            """.format(expression.shape[0], expression.shape[1], len(metadata)),
            unsafe_allow_html=True,
        )

    st.write("")
    run_integrity = st.button("▶  Run integrity checks", type="primary")
    if run_integrity:
        with st.spinner("Inspecting expression matrix and metadata..."):
            results = run_integrity_checks(expression, metadata)

        counts = {
            status: sum(item["status"] == status for item in results)
            for status in ["PASS", "WARNING", "FAIL", "SKIPPED"]
        }

        save_audit_history(
            "Integrity Audit",
            {
                "dataset": "GSE10072",
                "total_samples": int(expression.shape[0]),
                "total_features": int(expression.shape[1]),
                "passed": counts["PASS"],
                "warnings": counts["WARNING"],
                "failed": counts["FAIL"],
                "skipped": counts["SKIPPED"],
            },
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Passed", counts["PASS"], "Checks without detected issue")
        with c2:
            metric_card("Warnings", counts["WARNING"], "Review recommended")
        with c3:
            metric_card("Failed", counts["FAIL"], "Integrity issue detected")
        with c4:
            metric_card("Skipped", counts["SKIPPED"], "Could not evaluate")

        st.write("")
        section_header(
            "Audit output",
            "Detailed check results",
            "Expand each result to inspect the evidence returned by the check.",
        )
        for result in results:
            with st.container(border=True):
                show_status(result)
                with st.expander("View diagnostic details"):
                    st.json(result)

        results_df = pd.DataFrame(results)
        st.download_button(
            "⬇  Download integrity report",
            results_df.to_csv(index=False),
            "integrity_audit_results.csv",
            "text/csv",
        )
    else:
        st.markdown(
            """
            <div class="info-strip">
                Select <strong>Run integrity checks</strong> to generate the
                dataset quality report. The checks do not modify the source data.
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==================================================
# ANOMALY ANALYSIS
# ==================================================

elif page == "Anomaly Analysis":
    section_header(
        "Module 02 · Sample exploration",
        "Anomaly analysis",
        "Use PCA to explore sample profiles and Isolation Forest to flag potentially unusual observations.",
    )

    with st.container(border=True):
        st.markdown("**Model configuration**")
        config_left, config_right = st.columns([1, 1])
        with config_left:
            contamination = st.slider(
                "Isolation Forest contamination",
                min_value=0.01,
                max_value=0.20,
                value=0.05,
                step=0.01,
                help="Expected fraction of potential anomalies used by the model.",
            )
        with config_right:
            st.markdown(
                """
                <div style="padding-top:1.2rem;color:#718096;font-size:.82rem">
                    <b style="color:#17243a">Methods</b><br>
                    StandardScaler → PCA (2 components)<br>
                    StandardScaler → Isolation Forest (200 trees)
                </div>
                """,
                unsafe_allow_html=True,
            )
        run_anomaly = st.button("▶  Run anomaly analysis", type="primary")

    if run_anomaly:
        try:
            with st.spinner("Running PCA and Isolation Forest..."):
                pca_coordinates, explained_variance = run_pca(expression)
                anomaly_results = detect_anomalies(
                    expression,
                    contamination=contamination,
                    random_state=42,
                )
                results = {
                    "pca": pca_coordinates,
                    "explained_variance": explained_variance,
                    "anomalies": anomaly_results,
                }

            flagged = int(anomaly_results["is_anomaly"].sum())
            total = len(anomaly_results)

            save_audit_history(
                "Anomaly Analysis",
                {
                    "dataset": "GSE10072",
                    "total_samples": int(total),
                    "potential_anomalies": int(flagged),
                    "typical_profiles": int(total - flagged),
                    "contamination": float(contamination),
                    "pca_variance_explained_percent": float(
                        sum(explained_variance) * 100
                    ),
                },
            )

            saved_paths = save_anomaly_reports(results, contamination=contamination)

            flagged = int(anomaly_results["is_anomaly"].sum())
            total = len(anomaly_results)
            typical = total - flagged
            c1, c2, c3 = st.columns(3)
            with c1:
                metric_card("Samples analysed", f"{total:,}", "All loaded profiles")
            with c2:
                metric_card("Potential anomalies", f"{flagged:,}", "Isolation Forest flags")
            with c3:
                metric_card("Typical profiles", f"{typical:,}", "Not flagged by model")

            st.write("")
            section_header(
                "Dimensionality reduction",
                "PCA sample map",
                "Each point represents one sample. Hover over a point to inspect its sample identifier.",
            )
            plot_df = pca_coordinates.reset_index().merge(
                anomaly_results[["sample_id", "anomaly_label"]],
                on="sample_id",
                how="left",
            )
            variance_pct = [float(value) * 100 for value in explained_variance]
            fig = px.scatter(
                plot_df,
                x="PC1",
                y="PC2",
                color="anomaly_label",
                hover_name="sample_id",
                color_discrete_map={
                    "Typical profile": "#18a999",
                    "Potential anomaly": "#e59a43",
                },
                labels={"PC1": "PC1", "PC2": "PC2", "anomaly_label": "Model label"},
            )
            fig.update_traces(marker=dict(size=10, opacity=.82, line=dict(width=1, color="white")))
            fig.update_layout(
                height=480,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#fbfcfd",
                margin=dict(l=10, r=10, t=20, b=10),
                legend_title_text="Isolation Forest",
                xaxis_title=f"PC1 ({variance_pct[0]:.2f}% variance)",
                yaxis_title=f"PC2 ({variance_pct[1]:.2f}% variance)",
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(
                f"""
                <div class="info-strip">
                    The first two principal components explain
                    <strong>{sum(variance_pct):.2f}%</strong> of the variance
                    in this scaled expression matrix.
                </div>
                """,
                unsafe_allow_html=True,
            )

            section_header(
                "Model output",
                "Sample-level predictions",
                "Lowest anomaly scores are shown first.",
            )
            st.dataframe(
                anomaly_results.sort_values("anomaly_score", ascending=True),
                use_container_width=True,
                hide_index=True,
            )
            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "⬇  PCA coordinates",
                    pca_coordinates.to_csv(),
                    "pca_coordinates.csv",
                    "text/csv",
                    use_container_width=True,
                )
            with d2:
                st.download_button(
                    "⬇  Anomaly predictions",
                    anomaly_results.to_csv(index=False),
                    "anomaly_predictions.csv",
                    "text/csv",
                    use_container_width=True,
                )
            st.caption(
                "Saved report files: "
                + ", ".join(str(path) for path in saved_paths.values())
            )
            st.warning(
                "Potential anomalies are not confirmed defective samples. "
                "They may reflect biological variation, technical variation, "
                "or other factors and require further investigation."
            )
        except Exception as error:
            st.error(f"Anomaly analysis failed: {error}")


# ==================================================
# FAULT-INJECTION BENCHMARK
# ==================================================

elif page == "Fault-Injection Benchmark":
    section_header(
        "Module 03 · Controlled validation",
        "Fault-injection benchmark",
        "Evaluate whether integrity checks detect known defects introduced into copies of the dataset.",
    )
    st.markdown(
        """
        <div class="info-strip">
            This benchmark uses five controlled defect types and one clean baseline.
            The source expression matrix is not intentionally modified.
        </div>
        """,
        unsafe_allow_html=True,
    )

    run_benchmark = st.button("▶  Run controlled benchmark", type="primary")
    if run_benchmark:
        try:
            with st.spinner("Injecting controlled defects and evaluating checks..."):
                report, summary = run_fault_injection_benchmark(
                    expression, metadata, BENCHMARK_DIR
                )

            save_audit_history(
                "Fault-Injection Benchmark",
                {
                    "dataset": "GSE10072",
                    "total_experiments": int(summary.get("total_experiments", 0)),
                    "injected_defect_experiments": int(
                        summary.get("injected_defect_experiments", 0)
                    ),
                    "detected_defects": int(summary.get("detected_defects", 0)),
                    "missed_defects": int(summary.get("missed_defects", 0)),
                    "detection_rate": float(summary.get("detection_rate", 0)),
                    "clean_baseline_passed": bool(
                        summary.get("clean_baseline_passed", False)
                    ),
                    "unexpected_flags": int(
                        summary.get("total_unexpected_flags", 0)
                    ),
                    "mean_runtime_seconds": float(
                        summary.get("mean_runtime_seconds", 0)
                    ),
                },
            )

            st.success("Benchmark completed successfully.")

            section_header(
                "Overall performance",
                "Benchmark summary",
                "Results from the controlled experiments in this run.",
            )
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                metric_card(
                    "Detection rate",
                    f"{summary.get('detection_rate', 0) * 100:.1f}%",
                    "Injected defects detected",
                )
            with c2:
                metric_card(
                    "Defects detected",
                    f"{summary.get('detected_defects', 0)}/"
                    f"{summary.get('injected_defect_experiments', 0)}",
                    "Controlled defect experiments",
                )
            with c3:
                metric_card(
                    "Missed defects",
                    summary.get("missed_defects", 0),
                    "Injected defects not detected",
                )
            with c4:
                metric_card(
                    "Mean runtime",
                    f"{summary.get('mean_runtime_seconds', 0):.3f} s",
                    "Average experiment runtime",
                )

            c5, c6 = st.columns(2)
            with c5:
                metric_card(
                    "Clean baseline",
                    "Passed" if summary.get("clean_baseline_passed") else "Not passed",
                    "Expected no-defect control",
                )
            with c6:
                metric_card(
                    "Unexpected flags",
                    summary.get("total_unexpected_flags", "Not reported"),
                    "Flags in non-target checks",
                )

            metrics_df = pd.DataFrame(summary.get("per_check_metrics", []))
            if not metrics_df.empty:
                st.write("")
                section_header(
                    "Detection quality",
                    "Precision, recall and F1-score",
                    "Per-check metrics for the injected defect experiments.",
                )
                metric_columns = [
                    col for col in ["precision", "recall", "f1_score"]
                    if col in metrics_df.columns
                ]
                if "check" in metrics_df.columns and metric_columns:
                    chart_df = metrics_df.melt(
                        id_vars="check",
                        value_vars=metric_columns,
                        var_name="Metric",
                        value_name="Score",
                    )
                    fig = px.bar(
                        chart_df,
                        x="check",
                        y="Score",
                        color="Metric",
                        barmode="group",
                        range_y=[0, 1.05],
                        color_discrete_sequence=["#0b8f87", "#58b7aa", "#e5a34b"],
                    )
                    fig.update_layout(
                        height=410,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="#fbfcfd",
                        margin=dict(l=10, r=10, t=25, b=10),
                        xaxis_tickangle=-22,
                        yaxis_title="Score",
                        xaxis_title="Integrity check",
                        legend_title_text="Metric",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)

            section_header(
                "Experiment log",
                "Individual experiment results",
                "Inspect each clean or corrupted dataset scenario.",
            )
            st.dataframe(report, use_container_width=True, hide_index=True)

            st.write("")
            section_header(
                "Export",
                "Download benchmark evidence",
                "Save the experiment table, per-check metrics and summary for reporting.",
            )
            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button(
                    "⬇  Experiment results",
                    report.to_csv(index=False),
                    "fault_injection_results.csv",
                    "text/csv",
                    use_container_width=True,
                )
            with d2:
                if not metrics_df.empty:
                    st.download_button(
                        "⬇  Metrics table",
                        metrics_df.to_csv(index=False),
                        "fault_injection_metrics.csv",
                        "text/csv",
                        use_container_width=True,
                    )
            with d3:
                st.download_button(
                    "⬇  Summary JSON",
                    json.dumps(summary, indent=4),
                    "fault_injection_summary.json",
                    "application/json",
                    use_container_width=True,
                )

            with st.expander("How to interpret the benchmark"):
                st.markdown(
                    """
                    - **True Positive (TP):** An injected defect correctly detected.
                    - **False Positive (FP):** A check flags an experiment where
                      that defect was not injected.
                    - **True Negative (TN):** A check correctly does not flag an
                      experiment without that defect.
                    - **False Negative (FN):** An injected defect that the
                      expected check misses.
                    """
                )
            if summary.get("note"):
                st.warning(summary["note"])
            st.caption(
                "The benchmark contains a small number of controlled experiments. "
                "These results are not statistically generalizable estimates of "
                "performance on unseen datasets."
            )
        except Exception as error:
            st.error(f"Benchmark failed: {error}")


# ==================================================
# ML LEAKAGE AUDIT
# ==================================================

elif page == "ML Leakage Audit":
    section_header(
        "Module 04 · Model reliability",
        "Machine-learning leakage screening",
        "Upload training and testing matrices with sample IDs, plus a training-label file, to screen selected leakage signals.",
    )

    st.markdown(
        """
        <div class="info-strip">
            <strong>File format:</strong> The first column of each expression CSV
            should contain sample IDs. Training and testing files must use matching
            feature columns. The labels CSV must include a sample ID column and a
            target label column.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Upload analysis files")
    up1, up2 = st.columns(2, gap="large")
    with up1:
        st.markdown(
            '<div class="subtle-panel"><b>01 · Training matrix</b><br>'
            '<span style="color:#718096;font-size:.78rem">Samples × features</span></div>',
            unsafe_allow_html=True,
        )
        train_file = st.file_uploader(
            "Training expression CSV",
            type=["csv"],
            key="train",
            label_visibility="collapsed",
        )
    with up2:
        st.markdown(
            '<div class="subtle-panel"><b>02 · Testing matrix</b><br>'
            '<span style="color:#718096;font-size:.78rem">Held-out samples × features</span></div>',
            unsafe_allow_html=True,
        )
        test_file = st.file_uploader(
            "Testing expression CSV",
            type=["csv"],
            key="test",
            label_visibility="collapsed",
        )

    st.markdown(
        '<div class="subtle-panel"><b>03 · Training labels</b><br>'
        '<span style="color:#718096;font-size:.78rem">Sample identifier and target label columns</span></div>',
        unsafe_allow_html=True,
    )
    label_file = st.file_uploader(
        "Training labels CSV",
        type=["csv"],
        key="labels",
        label_visibility="collapsed",
    )

    uploaded_count = sum(file is not None for file in [train_file, test_file, label_file])
    st.progress(uploaded_count / 3, text=f"{uploaded_count} of 3 files uploaded")

    if train_file and test_file and label_file:
        try:
            train = pd.read_csv(train_file, index_col=0)
            test = pd.read_csv(test_file, index_col=0)
            labels_df = pd.read_csv(label_file)

            st.write("")
            section_header(
                "Input verification",
                "Uploaded data dimensions",
                "Confirm the files and columns before running the screening checks.",
            )
            c1, c2, c3 = st.columns(3)
            with c1:
                metric_card("Training samples", f"{train.shape[0]:,}", f"{train.shape[1]:,} features")
            with c2:
                metric_card("Testing samples", f"{test.shape[0]:,}", f"{test.shape[1]:,} features")
            with c3:
                metric_card("Label records", f"{len(labels_df):,}", f"{labels_df.shape[1]:,} columns")

            label_left, label_right = st.columns(2)
            with label_left:
                label_column = st.selectbox(
                    "Select target label column",
                    labels_df.columns.tolist(),
                )
            with label_right:
                label_id_column = st.selectbox(
                    "Select sample ID column in labels",
                    labels_df.columns.tolist(),
                )

            if st.button("▶  Run leakage audit", type="primary"):
                if label_column == label_id_column:
                    st.error("Choose different columns for sample IDs and labels.")
                else:
                    labels = labels_df.set_index(label_id_column)[label_column]
                    labels = labels.reindex(train.index)

                    if labels.isna().any():
                        st.error("Some training samples have no matching labels.")
                    else:
                        results = run_leakage_audit(train, test, labels)
                        section_header(
                            "Screening output",
                            "Leakage audit results",
                            "Review the status and diagnostic evidence for each check.",
                        )
                        for result in results:
                            with st.container(border=True):
                                show_status(result)
                                with st.expander("View diagnostic details"):
                                    st.json(result)

                        st.markdown(
                            """
                            <div class="info-strip">
                                These checks screen for selected leakage signals.
                                They cannot prove that an entire machine-learning
                                pipeline is leakage-free. High target-feature
                                association is a warning for investigation, not
                                proof of leakage.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
        except Exception as error:
            st.error(f"Could not process uploaded files: {error}")
    else:
        st.caption("Upload all three CSV files to enable the leakage screening workflow.")


# ==================================================

elif page == "Audit History":
    section_header(
        "Module 05 · Run tracking",
        "Audit history",
        "Review previous dataset audits and download recorded results.",
    )

    history = get_audit_history()

    if not history:
        st.info("No audit history yet. Run an audit to create your first record.")
    else:
        history_df = pd.DataFrame([
            {
                "Run ID": item.get("run_id", ""),
                "Analysis": item.get("analysis_type", "Unknown"),
                "Timestamp (UTC)": item.get("timestamp", ""),
            }
            for item in history
        ])

        c1, c2 = st.columns(2)
        with c1:
            metric_card("Total audit runs", len(history), "Recorded executions")
        with c2:
            metric_card(
                "Analysis types",
                history_df["Analysis"].nunique(),
                "Different workflows",
            )

        st.write("")
        section_header(
            "Run register",
            "Previous audit executions",
            "Newest records appear first.",
        )
        st.dataframe(history_df, use_container_width=True, hide_index=True)

        st.write("")
        section_header(
            "Run details",
            "Inspect an individual audit",
            "Choose a run to view its saved summary.",
        )

        options = {
            f"{item.get('analysis_type', 'Unknown')} | "
            f"{item.get('timestamp', '')} | {item.get('run_id', '')[:8]}": item
            for item in history
        }

        selected_label = st.selectbox("Select an audit run", list(options.keys()))
        selected = options[selected_label]

        st.json(selected.get("summary", {}))
        st.caption(f"Run ID: {selected.get('run_id', '')}")

        st.download_button(
            "Download selected run (JSON)",
            data=json.dumps(selected, indent=4),
            file_name="selected_audit_run.json",
            mime="application/json",
        )

        st.download_button(
            "Download all history (JSON)",
            data=json.dumps(history, indent=4),
            file_name="audit_history.json",
            mime="application/json",
        )

        csv_rows = [
            {
                "run_id": item.get("run_id", ""),
                "analysis_type": item.get("analysis_type", ""),
                "timestamp": item.get("timestamp", ""),
                **item.get("summary", {}),
            }
            for item in history
        ]

        st.download_button(
            "Download all history (CSV)",
            data=pd.DataFrame(csv_rows).to_csv(index=False),
            file_name="audit_history.csv",
            mime="text/csv",
        )

        st.caption("History is stored locally in results/audit_history.json.")

# FOOTER
# ==================================================

st.markdown(
    """
    <div class="footer">
        <b style="color:#526174">OmicsGuard AI</b> · MSc Bioinformatics Science Fair Project · 2026
        <span style="float:right">Reproducible · Explainable · Research-focused</span>
    </div>
    """,
    unsafe_allow_html=True,
)
