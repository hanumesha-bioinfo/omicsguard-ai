import streamlit as st
import pandas as pd
import plotly.express as px


def apply_dashboard_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: Inter, sans-serif;
    }

    .stApp {
        background:
          radial-gradient(ellipse at 5% 5%, #e4f7f8 0%, transparent 30%),
          linear-gradient(135deg, #f5f9fd, #edf5fa);
        color: #102b49;
    }

    .block-container {
        max-width: 1550px;
        padding: 1.1rem 2rem 5rem;
    }

    [data-testid="stSidebar"] {display:none !important;}
    [data-testid="stHeader"] {background:transparent;}

    .brand {
        display:flex;
        align-items:center;
        gap:14px;
        padding:5px 0 17px;
    }

    .brand-logo {
        width:52px;
        height:52px;
        display:grid;
        place-items:center;
        border-radius:16px;
        background:linear-gradient(135deg,#00cbb7,#087e9a);
        font-size:27px;
        box-shadow:0 8px 22px #00a99f35;
    }

    .brand-name {
        font-size:22px;
        font-weight:800;
        color:#102b49;
    }

    .brand-sub {
        font-size:10px;
        color:#607991;
        letter-spacing:1px;
    }

    .workspace {
        background:#dcf8ef;
        color:#087c58;
        border:1px solid #c6eee0;
        border-radius:25px;
        padding:10px 15px;
        text-align:center;
        font-size:12px;
        font-weight:700;
        margin-top:8px;
    }

    /* Navigation */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display:flex;
        flex-direction:row;
        flex-wrap:nowrap;
        gap:10px;
        width:100%;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background:#ffffff;
        border:1px solid #e0ebf2;
        border-radius:16px;
        padding:11px 15px;
        box-shadow:0 5px 15px #183b5b0b;
        transition:all .2s ease;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background:#e9faf8;
        border-color:#00aaa8;
        transform:translateY(-2px);
    }

    div[data-testid="stRadio"] div[role="radiogroup"] p {
        color:#173b56;
        font-size:12px;
        font-weight:750;
        white-space:nowrap;
    }

    /* Upload toolbar */
    .upload-heading {
        font-size:17px;
        font-weight:800;
        color:#102b49;
    }

    .upload-caption {
        color:#607991;
        font-size:11px;
        margin-top:4px;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color:#cce9ed !important;
        border-radius:19px !important;
        background:rgba(255,255,255,.82);
        box-shadow:0 7px 24px #183b5b0b;
    }

    [data-testid="stFileUploader"] {
        background:#f5ffff;
        border:1px dashed #8ed8d3;
        border-radius:13px;
        padding:8px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background:#f5ffff;
        border:0;
        padding:5px;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        font-size:11px;
    }

    /* Hero banner */
    .hero {
        position:relative;
        overflow:hidden;
        min-height:220px;
        border-radius:25px;
        padding:32px 36px;
        margin:15px 0 23px;
        color:#ffffff;
        background:
          radial-gradient(circle at 78% 25%,#00d7c75c,transparent 27%),
          radial-gradient(circle at 92% 95%,#24e8ce45,transparent 32%),
          linear-gradient(112deg,#062d48 0%,#07536a 57%,#009b91 115%);
        box-shadow:0 13px 30px #075b7730;
    }

    .hero:before {
        content:"";
        position:absolute;
        width:360px;
        height:360px;
        right:4%;
        top:-80px;
        border-radius:50%;
        border:1px solid #6af5ec38;
        box-shadow:
          0 0 0 35px #ffffff08,
          0 0 0 75px #ffffff07,
          0 0 0 115px #ffffff05;
    }

    .hero:after {
        content:"🧬";
        position:absolute;
        right:9%;
        top:22px;
        font-size:130px;
        opacity:.34;
        filter:drop-shadow(0 0 20px #44f5e7);
    }

    .hero-tag {
        display:inline-block;
        color:#75f6eb;
        border:1px solid #36e4d4;
        border-radius:30px;
        padding:7px 13px;
        font-size:11px;
        font-weight:800;
        letter-spacing:.4px;
    }

    .hero h1 {
        position:relative;
        z-index:1;
        color:#ffffff !important;
        font-size:clamp(27px,3vw,38px);
        line-height:1.18;
        font-weight:800;
        margin:17px 0 10px;
        max-width:700px;
    }

    .hero h1 span {color:#51eee4;}

    .hero p {
        position:relative;
        z-index:1;
        color:#e1f7fa;
        font-size:13px;
        line-height:1.6;
        max-width:700px;
    }

    /* Section headings */
    .section-title {
        color:#102b49;
        font-size:19px;
        font-weight:800;
        margin:18px 0 3px;
    }

    .section-subtitle {
        color:#607991;
        font-size:12px;
        margin-bottom:13px;
    }

    /* Metric cards */
    .metric {
        position:relative;
        overflow:hidden;
        display:flex;
        align-items:center;
        gap:13px;
        background:linear-gradient(120deg,#ffffff,#f9fdff);
        border:1px solid #e0edf4;
        border-radius:19px;
        padding:17px 15px;
        min-height:116px;
        box-shadow:0 7px 20px #183b5b0c;
        transition:transform .2s ease,box-shadow .2s ease;
    }

    .metric:hover {
        transform:translateY(-3px);
        box-shadow:0 12px 24px #183b5b16;
    }

    .metric-icon {
        width:49px;
        height:49px;
        min-width:49px;
        display:grid;
        place-items:center;
        border-radius:50%;
        background:#ddf8f4;
        font-size:23px;
    }

    .metric-body {min-width:0;}

    .metric-label {
        color:#526b84;
        font-size:11px;
        font-weight:700;
    }

    .metric-value {
        color:#102b49;
        font-size:27px;
        font-weight:800;
        margin:3px 0;
    }

    .metric-note {
        color:#71879b;
        font-size:10px;
    }

    /* Chart and quick-action panels */
    .chart-panel {
        background:#ffffff;
        border:1px solid #dfedf3;
        border-radius:19px;
        padding:13px 15px 5px;
        box-shadow:0 6px 20px #183b5b0b;
        min-height:330px;
    }

    .quick {
        background:linear-gradient(145deg,#e0faf6,#d1f3f0);
        border:1px solid #bcece5;
        border-radius:20px;
        padding:17px;
        box-shadow:0 7px 20px #087e7912;
    }

    .quick h3 {
        color:#103b50;
        font-size:17px;
        font-weight:800;
    }

    .quick p {
        font-size:11px;
        color:#164b62;
        padding:7px 0;
        border-bottom:1px solid #bfe8e3;
    }

    .stButton>button, .stDownloadButton>button {
        border-radius:12px;
        border:1px solid #b8e6e5;
        color:#087c79;
        background:#ffffff;
        font-weight:750;
        min-height:40px;
        transition:all .2s ease;
    }

    .stButton>button:hover, .stDownloadButton>button:hover {
        background:#e5fbf8;
        border-color:#00aaa8;
        color:#075c5a;
    }

    .footer {
        border-top:1px solid #d5e7ed;
        margin-top:30px;
        padding:15px 5px;
        color:#58718c;
        font-size:11px;
        display:flex;
        justify-content:space-between;
    }

    @media(max-width:900px) {
        .block-container {padding-left:1rem;padding-right:1rem;}
        div[data-testid="stRadio"] div[role="radiogroup"] {
            flex-wrap:wrap;
        }
        .hero {padding:24px;}
        .hero:after {right:0;font-size:85px;}
    }
    </style>
    """, unsafe_allow_html=True)


def render_dashboard_header():
    a, b = st.columns([4, 1])
    with a:
        st.markdown(
            '<div class="brand">'
            '<div class="brand-logo">🧬</div>'
            '<div><div class="brand-name">OmicsGuard AI</div>'
            '<div class="brand-sub">BIOINFORMATICS RESEARCH DATA AUDITOR</div>'
            '</div></div>',
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            '<div class="workspace">🟢 Local Analysis Workspace</div>',
            unsafe_allow_html=True,
        )


def render_upload_toolbar():
    with st.container(border=True):
        a, b, c, d = st.columns([1.15, 1.15, 1.15, .85])

        with a:
            st.markdown(
                '<div style="padding-top:8px">'
                '<div style="font-size:28px">☁️</div>'
                '<div class="upload-heading">Upload Your Dataset</div>'
                '<div class="upload-caption">'
                'Expression and metadata files'
                '</div></div>',
                unsafe_allow_html=True,
            )

        with b:
            expression_file = st.file_uploader(
                "Expression CSV",
                type=["csv"],
                key="omicsguard_expression",
            )

        with c:
            metadata_file = st.file_uploader(
                "Metadata CSV",
                type=["csv"],
                key="omicsguard_metadata",
            )

        with d:
            st.write("")
            st.write("")
            verify = st.button(
                "🔎 Verify Dataset",
                type="primary",
                use_container_width=True,
            )

    st.caption(
        "Supported: CSV files | Expression: one row per sample | "
        "Metadata: sample_id column required"
    )

    return expression_file, metadata_file, verify


def render_dashboard_overview(expression, metadata):
    if expression is None or expression.empty:
        st.warning("No expression dataset is loaded.")
        return

    if metadata is None:
        metadata = pd.DataFrame()

    samples = len(expression)
    features = len(expression.columns)
    fields = len(metadata.columns)
    missing = int(expression.isna().sum().sum())

    st.markdown("""
    <div class="hero">
      <span class="hero-tag">⚗ SCIENTIFIC DATA QUALITY PLATFORM</span>
      <h1>Trust your omics data.<br>
      <span>Audit before you analyse.</span></h1>
      <p>An integrated bioinformatics platform to evaluate expression data
      integrity, explore unusual sample profiles, benchmark defect detection
      and screen ML leakage signals.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Dataset Snapshot</div>'
        '<div class="section-subtitle">'
        'Quick overview of your current dataset'
        '</div>',
        unsafe_allow_html=True,
    )

    metrics = [
        ("🛢️", "Total Samples", samples, "Expression profiles"),
        ("⚗️", "Probe Features", features, "Measured features"),
        ("▦", "Metadata Fields", fields, "Sample annotations"),
        ("⚠️", "Missing Values", missing, "In expression matrix"),
    ]

    cols = st.columns(4)
    for col, (icon, label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric">'
                f'<div class="metric-icon">{icon}</div>'
                f'<div class="metric-body">'
                f'<div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value:,}</div>'
                f'<div class="metric-note">{note}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-title">Biological Composition</div>'
        '<div class="section-subtitle">'
        'Explore tissue types and sample annotation distributions'
        '</div>',
        unsafe_allow_html=True,
    )

    tissue = next(
        (x for x in metadata.columns
         if any(k in x.lower() for k in ["tissue", "source_name", "type"])),
        None,
    )
    smoking = next(
        (x for x in metadata.columns if "smok" in x.lower()),
        None,
    )

    a, b, c = st.columns([1, 1.25, .78])

    with a:
        with st.container(border=True):
            st.markdown("**◉ Tissue Type Distribution**")
            if tissue:
                counts = (
                    metadata[tissue].fillna("Unknown")
                    .astype(str).value_counts()
                )
                fig = px.pie(
                    names=counts.index,
                    values=counts.values,
                    hole=.63,
                    color_discrete_sequence=[
                        "#00A99D", "#FF9B42", "#638AD8",
                        "#9270DB", "#7FC8A9"
                    ],
                )
                fig.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hole=.63,
                    marker=dict(line=dict(color="white", width=3)),
                )
                fig.update_layout(
                    height=275,
                    margin=dict(t=12, b=5, l=5, r=5),
                    showlegend=True,
                    legend=dict(font=dict(size=10)),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(
                    fig, use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.info("No tissue annotation column detected.")

    with b:
        with st.container(border=True):
            st.markdown("**▥ Smoking Status Distribution**")
            if smoking:
                counts = (
                    metadata[smoking].fillna("Unknown")
                    .astype(str).value_counts()
                )
                fig = px.bar(
                    x=counts.index,
                    y=counts.values,
                    text=counts.values,
                    color=counts.index,
                    color_discrete_sequence=[
                        "#00A99D", "#FF9B42", "#638AD8",
                        "#9270DB", "#7FC8A9"
                    ],
                )
                fig.update_traces(
                    textposition="outside",
                    marker_line_width=0,
                )
                fig.update_layout(
                    height=275,
                    margin=dict(t=20, b=5, l=5, r=5),
                    showlegend=False,
                    xaxis_title=None,
                    yaxis_title="Number of samples",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#38546b", size=10),
                    yaxis=dict(gridcolor="#e8f0f5"),
                )
                st.plotly_chart(
                    fig, use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.info("No smoking annotation column detected.")

    with c:
        st.markdown(
            '<div class="quick"><h3>⚡ Quick Actions</h3>'
            '<p>🛡️ Run Integrity Audit</p>'
            '<p>📊 Run Anomaly Analysis</p>'
            '<p>🧪 Run Benchmark</p>'
            '<p>⚗️ Run Leakage Audit</p>'
            '<p>◷ View Audit History</p></div>',
            unsafe_allow_html=True,
        )

        actions = [
            ("Run Integrity Audit", "Integrity Audit"),
            ("Run Anomaly Analysis", "Anomaly Analysis"),
            ("Run Benchmark", "Fault-Injection Benchmark"),
            ("Run Leakage Audit", "ML Leakage Audit"),
            ("View Audit History", "Audit History"),
        ]

        for label, target in actions:
            if st.button(label, key="quick_" + target, use_container_width=True):
                st.session_state["page"] = target
                st.rerun()

    st.markdown(
        '<div class="footer">'
        '<span>🧬 OmicsGuard AI · MSc Bioinformatics Science Fair Project · 2026</span>'
        '<span>Reproducible · Explainable · Research-Focused</span>'
        '</div>',
        unsafe_allow_html=True,
    )
