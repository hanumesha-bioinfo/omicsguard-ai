from pathlib import Path

path = Path("app.py")
source = path.read_text(encoding="utf-8")

start_marker = "# ==================================================\n# OVERVIEW"
end_marker = "# ==================================================\n# INTEGRITY AUDIT"

start = source.find(start_marker)
end = source.find(end_marker)

if start == -1 or end == -1 or end <= start:
    raise SystemExit("ERROR: Could not locate Overview section. No changes made.")

# Preserve the original file before this redesign.
backup = Path("app.py.before_overview_redesign")
if not backup.exists():
    backup.write_text(source, encoding="utf-8")

overview = r'''
# ==================================================
# OVERVIEW — SCIENTIFIC WORKSPACE
# ==================================================

import html

dataset_label = html.escape(
    str(st.session_state.get("active_dataset_name", "GSE10072"))
)

sample_count = expression.shape[0]
feature_count = expression.shape[1]
metadata_count = metadata.shape[1]
missing_count = int(expression.isna().sum().sum())

section_header(
    "RESEARCH WORKSPACE",
    "Dataset intelligence overview",
    "A unified workspace to inspect biological data quality, discover anomalies "
    "and evaluate machine-learning reliability."
)

# HERO
st.markdown(
    f"""
    <div class="og-hero">
        <div class="og-hero-content">
            <div class="og-eyebrow">🧬 BIOINFORMATICS · DATA QUALITY · AI</div>
            <div class="og-hero-title">
                Trust your omics data.<br>
                <span>Audit before you analyse.</span>
            </div>
            <div class="og-hero-description">
                A scientific dataset auditing platform for expression-data
                integrity, anomaly detection, benchmark validation and
                machine-learning reliability.
            </div>
            <div class="og-hero-tags">
                <span>● Research workspace active</span>
                <span>Dataset: {dataset_label}</span>
                <span>Reproducible analysis</span>
            </div>
        </div>
        <div class="og-dna-art">
            <div class="og-dna-symbol">🧬</div>
            <div class="og-dna-caption">OMICS DATA INTELLIGENCE</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# METRIC CARDS
st.markdown('<div class="og-section-label">DATASET SNAPSHOT</div>',
            unsafe_allow_html=True)

metric_columns = st.columns(4)

metric_items = [
    ("01", "TOTAL SAMPLES", f"{sample_count:,}", "Biological samples"),
    ("02", "FEATURES", f"{feature_count:,}", "Expression variables"),
    ("03", "METADATA FIELDS", f"{metadata_count:,}", "Annotation columns"),
    ("04", "MISSING VALUES", f"{missing_count:,}", "Expression matrix"),
]

for column, item in zip(metric_columns, metric_items):
    number, label, value, note = item
    with column:
        st.markdown(
            f"""
            <div class="og-metric">
                <div class="og-metric-top">
                    <span>{label}</span>
                    <span class="og-metric-number">{number}</span>
                </div>
                <div class="og-metric-value">{value}</div>
                <div class="og-metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

# MAIN DASHBOARD GRID
left, right = st.columns([1.65, 1], gap="large")

with left:
    st.markdown(
        """
        <div class="og-panel-heading">
            <div>
                <div class="og-section-label">BIOLOGICAL OVERVIEW</div>
                <div class="og-panel-title">Sample composition</div>
                <div class="og-panel-subtitle">
                    Explore the biological characteristics represented in the dataset.
                </div>
            </div>
            <div class="og-panel-icon">◉</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tissue_column = "source_name_ch1"
    smoking_column = "characteristic_Cigarette Smoking Status"

    chart_left, chart_right = st.columns(2, gap="medium")

    with chart_left:
        if tissue_column in metadata.columns:
            tissue_counts = (
                metadata[tissue_column]
                .fillna("Not specified")
                .astype(str)
                .value_counts()
                .reset_index()
            )
            tissue_counts.columns = ["Tissue", "Samples"]

            fig_tissue = px.pie(
                tissue_counts,
                names="Tissue",
                values="Samples",
                hole=0.62,
                title="Tissue distribution",
                color_discrete_sequence=[
                    "#087e79", "#18b6a5", "#79d4c6",
                    "#a8ddd5", "#d7eeea", "#e5b96b"
                ],
            )
            fig_tissue.update_layout(
                height=330,
                margin=dict(l=10, r=10, t=55, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(size=10)),
                font=dict(family="Arial", color="#173d43"),
            )
            st.plotly_chart(fig_tissue, use_container_width=True)
        else:
            st.info("Tissue annotation is not available in this dataset.")

    with chart_right:
        if smoking_column in metadata.columns:
            smoking_counts = (
                metadata[smoking_column]
                .fillna("Not specified")
                .astype(str)
                .value_counts()
                .reset_index()
            )
            smoking_counts.columns = ["Smoking status", "Samples"]

            fig_smoking = px.bar(
                smoking_counts,
                x="Smoking status",
                y="Samples",
                title="Smoking status",
                color="Samples",
                color_continuous_scale=["#b9e8df", "#087e79"],
                text="Samples",
            )
            fig_smoking.update_layout(
                height=330,
                margin=dict(l=10, r=10, t=55, b=55),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="Number of samples",
                font=dict(family="Arial", color="#173d43"),
            )
            fig_smoking.update_traces(textposition="outside")
            st.plotly_chart(fig_smoking, use_container_width=True)
        else:
            st.info("Smoking-status annotation is not available.")

    # Dataset preview
    with st.expander("Explore expression matrix preview"):
        st.dataframe(
            expression.head(10),
            use_container_width=True,
        )

    with st.expander("Explore sample metadata"):
        st.dataframe(
            metadata.head(10),
            use_container_width=True,
        )

with right:
    st.markdown(
        """
        <div class="og-section-label">WORKSPACE SHORTCUTS</div>
        <div class="og-panel-title">Quick actions</div>
        <div class="og-panel-subtitle">
            Jump directly into a scientific analysis module.
        </div>
        """,
        unsafe_allow_html=True,
    )

    actions = [
        ("01", "Integrity audit", "Check missing values, duplicates and consistency.",
         "Integrity Audit"),
        ("02", "Anomaly analysis", "Identify unusual biological samples.",
         "Anomaly Analysis"),
        ("03", "Fault benchmark", "Evaluate detection performance using injected defects.",
         "Fault-Injection Benchmark"),
        ("04", "ML leakage audit", "Screen training and test datasets for leakage.",
         "ML Leakage Audit"),
        ("05", "Audit history", "Review previously completed analysis runs.",
         "Audit History"),
    ]

    for number, title, description, page_name in actions:
        st.markdown(
            f"""
            <div class="og-action">
                <div class="og-action-number">{number}</div>
                <div class="og-action-copy">
                    <div class="og-action-title">{title}</div>
                    <div class="og-action-description">{description}</div>
                </div>
                <div class="og-action-arrow">↗</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"Open {title} →",
            key=f"og_action_{number}",
            use_container_width=True,
        ):
            st.session_state["page"] = page_name
            st.rerun()

    st.markdown(
        """
        <div class="og-note">
            <strong>Scientific reminder</strong>
            <p>
            An anomaly flag indicates a sample that deserves investigation.
            It does not independently establish a biological error or disease
            association.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# DATASET INFORMATION
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="og-section-label">DATASET INFORMATION</div>
    <div class="og-panel-title">Research dataset details</div>
    """,
    unsafe_allow_html=True,
)

info1, info2, info3, info4 = st.columns(4)

with info1:
    st.markdown(
        '<div class="og-info"><span>DATASET</span><strong>'
        + dataset_label + '</strong></div>',
        unsafe_allow_html=True,
    )

with info2:
    st.markdown(
        '<div class="og-info"><span>DATA TYPE</span>'
        '<strong>Gene expression</strong></div>',
        unsafe_allow_html=True,
    )

with info3:
    st.markdown(
        '<div class="og-info"><span>OBSERVATIONS</span>'
        f'<strong>{sample_count:,} samples</strong></div>',
        unsafe_allow_html=True,
    )

with info4:
    st.markdown(
        '<div class="og-info"><span>VARIABLES</span>'
        f'<strong>{feature_count:,} features</strong></div>',
        unsafe_allow_html=True,
    )

with st.expander("Scientific interpretation and limitations"):
    st.markdown(
        """
        - Expression-data integrity checks identify structural and numerical
          quality issues.
        - Anomaly detection identifies unusual observations, not confirmed
          biological errors.
        - Dataset composition describes the supplied annotations.
        - Machine-learning leakage checks depend on the supplied training,
          testing and label data.
        - Observational expression data alone cannot establish causation.
        """
    )

'''

# Add scoped styling for the rebuilt overview.
css = r"""
/* OMICSGUARD STRUCTURAL OVERVIEW */
.og-hero {
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 270px;
    padding: 38px 42px;
    margin: 14px 0 28px;
    border-radius: 23px;
    color: white;
    background:
        radial-gradient(circle at 80% 40%, rgba(40,220,194,.23), transparent 24%),
        linear-gradient(115deg,#062f38,#07565b 60%,#087e79);
    box-shadow: 0 16px 36px rgba(4,63,68,.17);
}
.og-hero-content { max-width: 790px; z-index: 1; }
.og-eyebrow {
    color: #7ce8d7;
    font-size: .73rem;
    font-weight: 800;
    letter-spacing: .16em;
    margin-bottom: 15px;
}
.og-hero-title {
    color: white;
    font-size: clamp(2rem,3.4vw,3.05rem);
    font-weight: 850;
    line-height: 1.12;
    letter-spacing: -.04em;
}
.og-hero-title span { color: #74e1d1; }
.og-hero-description {
    color: #d2eeeb;
    line-height: 1.7;
    max-width: 680px;
    margin-top: 13px;
    font-size: .96rem;
}
.og-hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 22px;
}
.og-hero-tags span {
    color: #eafffb;
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.22);
    padding: 7px 11px;
    border-radius: 30px;
    font-size: .72rem;
}
.og-dna-art {
    min-width: 190px;
    text-align: center;
    opacity: .85;
}
.og-dna-symbol { font-size: 105px; filter: drop-shadow(0 8px 20px #032c35); }
.og-dna-caption {
    color: #a5e8df;
    font-size: .65rem;
    font-weight: 800;
    letter-spacing: .16em;
}
.og-section-label {
    color: #0b9188;
    font-size: .69rem;
    font-weight: 850;
    letter-spacing: .15em;
    margin-bottom: 7px;
}
.og-metric {
    background: white;
    border: 1px solid #dce9e9;
    border-radius: 17px;
    padding: 19px;
    min-height: 132px;
    box-shadow: 0 5px 18px rgba(16,45,53,.045);
}
.og-metric-top { display:flex; justify-content:space-between; align-items:center; }
.og-metric-top span:first-child {
    color:#71858b; font-size:.68rem; font-weight:800; letter-spacing:.08em;
}
.og-metric-number {
    color:#a3c8c4; font-size:.75rem; font-weight:800;
}
.og-metric-value {
    color:#073c43; font-size:2.05rem; font-weight:850; margin-top:10px;
}
.og-metric-note { color:#819398; font-size:.76rem; }
.og-panel-heading { display:flex; justify-content:space-between; align-items:center; }
.og-panel-title { color:#103c43; font-size:1.27rem; font-weight:850; }
.og-panel-subtitle { color:#819398; font-size:.8rem; margin:4px 0 15px; }
.og-panel-icon {
    width:38px;height:38px;display:flex;align-items:center;justify-content:center;
    border-radius:12px;background:#e4f6f2;color:#087e79;font-size:1.25rem;
}
.og-action {
    display:flex; align-items:center; gap:12px;
    background:white; border:1px solid #dce9e9; border-radius:13px;
    padding:12px; margin:12px 0 5px;
}
.og-action-number {
    width:34px;height:34px;flex-shrink:0;border-radius:10px;
    display:flex;align-items:center;justify-content:center;
    background:#e6f6f3;color:#087e79;font-weight:850;font-size:.72rem;
}
.og-action-copy { flex:1; }
.og-action-title { color:#103c43;font-size:.86rem;font-weight:800; }
.og-action-description { color:#819398;font-size:.71rem;margin-top:3px; }
.og-action-arrow { color:#0b9188;font-size:1.1rem; }
.og-note {
    background:#eaf7f4;border:1px solid #cce9e2;border-radius:13px;
    padding:15px;margin-top:20px;
}
.og-note strong { color:#087e79;font-size:.82rem; }
.og-note p { color:#577a79;font-size:.76rem;line-height:1.6;margin:6px 0 0; }
.og-info {
    background:white;border:1px solid #dce9e9;border-radius:13px;
    padding:15px;min-height:78px;
}
.og-info span { display:block;color:#819398;font-size:.65rem;font-weight:800;letter-spacing:.1em; }
.og-info strong { display:block;color:#103c43;font-size:.88rem;margin-top:8px;overflow-wrap:anywhere; }
@media(max-width:850px) {
    .og-hero { padding:25px; }
    .og-dna-art { display:none; }
}
"""

if "/* OMICSGUARD STRUCTURAL OVERVIEW */" not in source:
    css_end = source.find("</style>")
    if css_end == -1:
        raise SystemExit("ERROR: Existing CSS block not found. No changes made.")
    source = source[:css_end] + "\n" + css + "\n" + source[css_end:]

source = source[:start] + overview + "\n\n" + source[end:]

path.write_text(source, encoding="utf-8")
print("SUCCESS: Overview page structurally redesigned.")
print("Backup: app.py.before_overview_redesign")
print("All six existing analysis modules remain in app.py.")
