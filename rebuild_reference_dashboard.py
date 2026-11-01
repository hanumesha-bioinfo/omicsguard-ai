from pathlib import Path
import ast
import re

path = Path("app.py")
source = path.read_text(encoding="utf-8")

# Create a new independent backup.
backup = Path("app.py.before_full_reference_rebuild")
if not backup.exists():
    backup.write_text(source, encoding="utf-8")

def section_position(text, name):
    pattern = (
        r"(?m)^# ={10,}\n# "
        + re.escape(name)
        + r"\n# ={10,}\s*$"
    )
    match = re.search(pattern, text)
    if not match:
        raise RuntimeError(f"Section not found: {name}")
    return match.start()

# Find section boundaries.
upload_start = section_position(source, "DATASET UPLOAD AND VALIDATION")
nav_start = section_position(source, "TOP NAVIGATION")
global_start = section_position(source, "GLOBAL TOP STRIP")
overview_start = section_position(source, "OVERVIEW")
integrity_start = section_position(source, "INTEGRITY AUDIT")

if not (
    upload_start < nav_start < global_start
    < overview_start < integrity_start
):
    raise RuntimeError("Unexpected app.py section order. No changes made.")

# Preserve the existing navigation code.
navigation = source[nav_start:global_start]

# Preserve the rest of the app after the Overview.
rest = source[integrity_start:]

# ----------------------------------------------------------
# CUSTOM HORIZONTAL UPLOAD TOOLBAR
# ----------------------------------------------------------

upload_code = r'''
# ==================================================
# DATASET UPLOAD AND VALIDATION
# ==================================================

if "original_expression" not in st.session_state:
    st.session_state["original_expression"] = expression.copy()
    st.session_state["original_metadata"] = metadata.copy()

st.markdown(
    """
    <div class="upload-toolbar">
        <div class="upload-icon">☁</div>
        <div class="upload-heading">
            <div class="upload-title">Upload Your Own Dataset</div>
            <div class="upload-subtitle">
                Upload expression matrix and metadata files to verify their quality.
            </div>
        </div>
        <div class="upload-format">SUPPORTED: CSV FILES</div>
    </div>
    """,
    unsafe_allow_html=True,
)

upload_expression_col, upload_metadata_col, verify_col = st.columns(
    [1.0, 1.0, 0.72],
    gap="medium",
)

with upload_expression_col:
    uploaded_expression = st.file_uploader(
        "Expression CSV",
        type=["csv"],
        key="reference_expression_upload",
        label_visibility="collapsed",
    )

with upload_metadata_col:
    uploaded_metadata = st.file_uploader(
        "Metadata CSV",
        type=["csv"],
        key="reference_metadata_upload",
        label_visibility="collapsed",
    )

with verify_col:
    st.markdown('<div class="verify-spacer"></div>', unsafe_allow_html=True)
    verify_clicked = st.button(
        "⌕  Verify Dataset",
        key="reference_verify_dataset",
        type="primary",
        use_container_width=True,
    )

if verify_clicked:
    if uploaded_expression is None:
        st.warning("Please select an expression CSV file first.")
    else:
        try:
            custom_expression = pd.read_csv(
                uploaded_expression,
                index_col=0,
            )
            custom_expression.index = custom_expression.index.astype(str)
            custom_expression.columns = custom_expression.columns.astype(str)
            custom_expression = custom_expression.apply(
                pd.to_numeric,
                errors="coerce",
            )

            if custom_expression.empty:
                raise ValueError("The expression matrix is empty.")

            if custom_expression.index.hasnans:
                raise ValueError("Missing sample IDs were detected.")

            if custom_expression.columns.hasnans:
                raise ValueError("Missing feature IDs were detected.")

            if uploaded_metadata is not None:
                custom_metadata = pd.read_csv(uploaded_metadata)

                if "sample_id" not in custom_metadata.columns:
                    raise ValueError(
                        "Metadata must contain a sample_id column."
                    )
            else:
                custom_metadata = pd.DataFrame({
                    "sample_id": custom_expression.index.astype(str)
                })

            st.session_state["custom_expression"] = custom_expression
            st.session_state["custom_metadata"] = custom_metadata
            st.session_state["active_dataset_name"] = uploaded_expression.name
            st.session_state["dataset_verified"] = True

            st.success(
                f"Dataset verified and loaded: {uploaded_expression.name}"
            )
            st.rerun()

        except Exception as error:
            st.session_state["dataset_verified"] = False
            st.error(f"Dataset validation failed: {error}")

if "custom_expression" in st.session_state:
    expression = st.session_state["custom_expression"]
    metadata = st.session_state["custom_metadata"]
    active_dataset_name = st.session_state.get(
        "active_dataset_name",
        "Custom dataset",
    )

    if st.session_state.get("dataset_verified", False):
        st.markdown(
            f"""
            <div class="dataset-status">
                <span>●</span>
                ACTIVE DATASET: <b>{active_dataset_name}</b>
                &nbsp; · &nbsp; {expression.shape[0]:,} samples
                &nbsp; · &nbsp; {expression.shape[1]:,} features
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("View uploaded dataset validation summary"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Samples", f"{expression.shape[0]:,}")
        c2.metric("Features", f"{expression.shape[1]:,}")
        c3.metric(
            "Missing values",
            f"{int(expression.isna().sum().sum()):,}",
        )
        c4.metric(
            "Duplicate sample IDs",
            f"{int(expression.index.duplicated().sum()):,}",
        )

        st.markdown("**Reference dataset comparison**")
        try:
            original_results = run_integrity_checks(
                st.session_state["original_expression"],
                st.session_state["original_metadata"],
            )
            custom_results = run_integrity_checks(
                expression,
                metadata,
            )

            comparison = pd.DataFrame([
                {
                    "Integrity check": old.get("check", "Check"),
                    "Reference dataset": old.get("status", "Unknown"),
                    "Uploaded dataset": new.get("status", "Unknown"),
                }
                for old, new in zip(original_results, custom_results)
            ])

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True,
            )
        except Exception as error:
            st.info(f"Comparison could not be generated: {error}")

else:
    active_dataset_name = "GSE10072"
    st.session_state["active_dataset_name"] = active_dataset_name
    st.session_state["dataset_verified"] = True

    st.markdown(
        f"""
        <div class="dataset-status">
            <span>●</span>
            ACTIVE DATASET: <b>GSE10072</b>
            &nbsp; · &nbsp; {expression.shape[0]:,} samples
            &nbsp; · &nbsp; {expression.shape[1]:,} features
        </div>
        """,
        unsafe_allow_html=True,
    )

'''

# ----------------------------------------------------------
# REBUILT OVERVIEW PAGE
# ----------------------------------------------------------

overview_code = r'''
# ==================================================
# OVERVIEW
# ==================================================

import html

dataset_label = html.escape(
    str(st.session_state.get("active_dataset_name", "GSE10072"))
)

sample_count = expression.shape[0]
feature_count = expression.shape[1]
metadata_count = metadata.shape[1]
missing_count = int(expression.isna().sum().sum())

# SCIENTIFIC HERO
st.markdown(
    f"""
    <div class="reference-hero">
        <div class="hero-content">
            <div class="hero-kicker">
                ⚗ SCIENTIFIC DATA QUALITY PLATFORM
            </div>
            <div class="hero-title">
                Trust your omics data.<br>
                <span>Audit before you analyse.</span>
            </div>
            <div class="hero-description">
                An integrated bioinformatics platform to evaluate expression
                data integrity, explore unusual sample profiles, benchmark
                defect detection and screen ML leakage signals.
            </div>
            <div class="hero-explore">Explore Modules →</div>
        </div>
        <div class="hero-dna-art">
            <div class="hero-dna">🧬</div>
            <div class="hero-dna-label">BIOLOGICAL DATA INTELLIGENCE</div>
        </div>
        <div class="hero-dataset">
            ● {dataset_label}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# DATASET METRICS
st.markdown(
    """
    <div class="reference-section-title">
        <span class="section-accent"></span>
        Dataset Snapshot
    </div>
    <div class="reference-section-subtitle">
        Quick overview of your current dataset
    </div>
    """,
    unsafe_allow_html=True,
)

metric_data = [
    ("▤", "Total Samples", f"{sample_count:,}", "Expression profiles", "teal"),
    ("⚗", "Probe Features", f"{feature_count:,}", "Measured features", "purple"),
    ("▦", "Metadata Fields", f"{metadata_count:,}", "Sample annotations", "green"),
    ("⚠", "Missing Values", f"{missing_count:,}", "In expression matrix", "orange"),
]

metric_columns = st.columns(4, gap="medium")

for col, item in zip(metric_columns, metric_data):
    icon, label, value, note, colour = item
    with col:
        st.markdown(
            f"""
            <div class="reference-metric">
                <div class="metric-icon {colour}">{icon}</div>
                <div class="metric-copy">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                <div class="metric-spark">
                    <svg viewBox="0 0 100 36" preserveAspectRatio="none">
                        <path d="M0 29 C12 28 15 10 27 17 S44 28 57 15 S77 20 100 3"
                        fill="none" stroke="currentColor" stroke-width="2"/>
                    </svg>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:17px'></div>", unsafe_allow_html=True)

# BIOLOGICAL CHARTS AND QUICK ACTIONS
chart_area, action_area = st.columns([4.8, 1.12], gap="medium")

with chart_area:
    st.markdown(
        """
        <div class="reference-section-title">
            <span class="section-accent"></span>
            Biological Composition
        </div>
        <div class="reference-section-subtitle">
            Explore tissue types and smoking status distribution
        </div>
        """,
        unsafe_allow_html=True,
    )

    tissue_column = "source_name_ch1"
    smoking_column = "characteristic_Cigarette Smoking Status"

    tissue_chart, smoking_chart = st.columns([1, 1.3], gap="medium")

    with tissue_chart:
        st.markdown('<div class="chart-heading">◕ &nbsp; Tissue Type Distribution</div>',
                    unsafe_allow_html=True)

        if tissue_column in metadata.columns:
            tissue_counts = (
                metadata[tissue_column]
                .fillna("Not specified")
                .astype(str)
                .value_counts()
                .reset_index()
            )
            tissue_counts.columns = ["Tissue", "Samples"]

            fig = px.pie(
                tissue_counts,
                names="Tissue",
                values="Samples",
                hole=.64,
                color_discrete_sequence=["#00a99d", "#f49a32", "#5284c8"],
            )
            fig.update_layout(
                height=285,
                margin=dict(l=5, r=5, t=15, b=5),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tissue information is not available.")

    with smoking_chart:
        st.markdown('<div class="chart-heading">▥ &nbsp; Smoking Status Distribution</div>',
                    unsafe_allow_html=True)

        if smoking_column in metadata.columns:
            smoking_counts = (
                metadata[smoking_column]
                .fillna("Not specified")
                .astype(str)
                .value_counts()
                .reset_index()
            )
            smoking_counts.columns = ["Smoking status", "Samples"]

            fig = px.bar(
                smoking_counts,
                x="Smoking status",
                y="Samples",
                color="Smoking status",
                text="Samples",
                color_discrete_sequence=["#009f9f", "#f49a32", "#5284c8"],
            )
            fig.update_layout(
                height=285,
                margin=dict(l=10, r=10, t=15, b=65),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="",
                yaxis_title="Samples",
                font=dict(size=10),
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Smoking status information is not available.")

with action_area:
    st.markdown(
        """
        <div class="quick-actions-panel">
            <div class="quick-actions-title">⚡ &nbsp; Quick Actions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    shortcuts = [
        ("🛡", "Run Integrity Audit", "Integrity Audit"),
        ("▥", "Run Anomaly Analysis", "Anomaly Analysis"),
        ("▤", "Run Benchmark", "Fault-Injection Benchmark"),
        ("⚗", "Run Leakage Audit", "ML Leakage Audit"),
        ("◷", "View Audit History", "Audit History"),
    ]

    for i, (icon, label, page_name) in enumerate(shortcuts):
        if st.button(
            f"{icon}   {label}   ›",
            key=f"reference_shortcut_{i}",
            use_container_width=True,
        ):
            st.session_state["page"] = page_name
            st.rerun()

# DATA PREVIEW
with st.expander("Explore expression matrix and sample metadata"):
    preview1, preview2 = st.tabs(["Expression matrix", "Sample metadata"])
    with preview1:
        st.dataframe(expression.head(10), use_container_width=True)
    with preview2:
        st.dataframe(metadata.head(10), use_container_width=True)

with st.expander("Scientific interpretation and limitations"):
    st.markdown(
        """
        - Anomaly flags identify samples that deserve investigation.
        - Anomaly detection does not independently prove biological error.
        - Observational expression data cannot establish causation by itself.
        - Machine-learning leakage checks depend on the supplied datasets.
        """
    )

'''

# ----------------------------------------------------------
# COMPLETE REFERENCE CSS
# ----------------------------------------------------------

reference_css = r"""
/* OMICS GUARD REFERENCE DESIGN */
.reference-hero {
    position:relative;
    overflow:hidden;
    isolation:isolate;
    min-height:218px;
    padding:29px 34px;
    margin:12px 0 21px;
    border-radius:22px;
    background:
        radial-gradient(circle at 82% 50%,#00e5d455,transparent 26%),
        linear-gradient(110deg,#032c43,#00566a 58%,#00a99e);
    box-shadow:0 12px 28px #034d6330;
    color:white;
}
.hero-content { position:relative; z-index:2; max-width:760px; }
.hero-kicker {
    color:#58f4e7;
    font-size:.73rem;
    font-weight:850;
    letter-spacing:.09em;
    margin-bottom:12px;
}
.hero-title {
    color:white;
    font-size:clamp(2rem,3vw,2.6rem);
    line-height:1.1;
    font-weight:900;
    letter-spacing:-.035em;
}
.hero-title span { color:#58eee3; }
.hero-description {
    color:#e0f6f8;
    font-size:.9rem;
    line-height:1.55;
    max-width:710px;
    margin-top:10px;
}
.hero-explore {
    display:inline-block;
    margin-top:12px;
    border:1px solid #37e5dc;
    color:#b5fff8;
    padding:6px 13px;
    border-radius:25px;
    font-size:.76rem;
    font-weight:750;
}
.hero-dna-art {
    position:absolute;
    right:8%;
    top:12px;
    width:230px;
    height:180px;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    opacity:.8;
}
.hero-dna { font-size:115px; filter:drop-shadow(0 5px 20px #00fff588); }
.hero-dna-label {
    color:#aafff7;
    font-size:.6rem;
    font-weight:800;
    letter-spacing:.15em;
}
.hero-dataset {
    position:absolute;
    bottom:14px;
    right:18px;
    z-index:3;
    background:#003f508c;
    border:1px solid #55ddd1;
    border-radius:25px;
    color:#e9fffc;
    padding:7px 12px;
    font-size:.67rem;
}
.reference-section-title {
    display:flex;
    align-items:center;
    gap:10px;
    color:#102f4c;
    font-size:1.03rem;
    font-weight:900;
}
.section-accent {
    width:23px;
    height:5px;
    border-radius:8px;
    background:#00b9ae;
}
.reference-section-subtitle {
    color:#688099;
    font-size:.77rem;
    margin:4px 0 12px 32px;
}
.reference-metric {
    position:relative;
    display:flex;
    align-items:center;
    gap:12px;
    min-height:88px;
    padding:13px 12px;
    overflow:hidden;
    background:#ffffffed;
    border:1px solid #dcebf4;
    border-radius:19px;
    box-shadow:0 5px 16px #123d5a0c;
}
.metric-icon {
    flex-shrink:0;
    display:flex;
    justify-content:center;
    align-items:center;
    width:53px;
    height:53px;
    border-radius:50%;
    font-size:1.5rem;
    font-weight:900;
}
.metric-icon.teal { background:#dcf8f5;color:#00a99d; }
.metric-icon.purple { background:#f0eaff;color:#9060e8; }
.metric-icon.green { background:#e0f9e7;color:#22b76b; }
.metric-icon.orange { background:#fff0e2;color:#f58a2d; }
.metric-copy { min-width:0;z-index:1; }
.metric-label { color:#415b77;font-size:.69rem;font-weight:800; }
.metric-value { color:#092f52;font-size:1.5rem;font-weight:900;line-height:1.3; }
.metric-note { color:#71879b;font-size:.65rem; }
.metric-spark {
    position:absolute;
    right:7px;
    bottom:10px;
    width:85px;
    color:#00b9ae;
    opacity:.55;
}
.metric-spark svg { width:100%;height:35px; }
.chart-heading {
    color:#163e5c;
    font-size:.78rem;
    font-weight:850;
    padding:12px 12px 0;
}
.quick-actions-panel {
    background:linear-gradient(145deg,#e2f9f6,#c8f2ec);
    border:1px solid #c1eee7;
    border-radius:17px;
    padding:14px 13px 5px;
    margin-top:1px;
}
.quick-actions-title {
    color:#103d53;
    font-size:.9rem;
    font-weight:900;
}
.upload-toolbar {
    display:flex;
    align-items:center;
    gap:15px;
    padding:10px 17px;
    margin:3px 0 0;
    border:1px solid #a0e3dc;
    border-radius:17px 17px 0 0;
    background:linear-gradient(105deg,#ffffff,#e8fbf8);
}
.upload-icon {
    width:54px;
    height:48px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#00a99d;
    font-size:2.3rem;
}
.upload-heading { flex:1; }
.upload-title { color:#12334c;font-size:.9rem;font-weight:900; }
.upload-subtitle { color:#668094;font-size:.7rem; }
.upload-format {
    color:#0a8f8a;
    font-size:.62rem;
    font-weight:850;
    letter-spacing:.08em;
}
.verify-spacer { height:4px; }
.dataset-status {
    background:#e5f8f4;
    border:1px solid #c5ebe3;
    border-radius:10px;
    padding:8px 13px;
    color:#087e79;
    font-size:.72rem;
    margin:7px 0 14px;
}
[data-testid="stFileUploader"] {
    background:transparent !important;
    border:0 !important;
    padding:0 !important;
    margin:0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    min-height:48px !important;
    padding:4px 8px !important;
    background:#fff !important;
    border:1px solid #77d4cb !important;
    border-radius:12px !important;
}
[data-testid="stFileUploaderDropzone"] > div {
    gap:3px !important;
}
[data-testid="stFileUploaderDropzone"] svg {
    display:none !important;
}
[data-testid="stFileUploaderDropzone"] small {
    display:none !important;
}
[data-testid="stFileUploaderDropzone"] button {
    border-radius:9px !important;
    border:1px solid #8ddbd2 !important;
    color:#087e79 !important;
    font-weight:800 !important;
}
.stButton > button[kind="primary"] {
    min-height:48px;
    border-radius:12px;
    background:linear-gradient(100deg,#009c9d,#08c5a5);
    color:white;
    font-weight:850;
    border:0;
    box-shadow:0 5px 14px #00a99b35;
}
.og-footer {
    position:fixed;
    left:0;right:0;bottom:0;
    z-index:999;
    display:flex;
    justify-content:space-between;
    padding:10px 20px;
    background:#f4f9ffed;
    border-top:1px solid #dce8ef;
    color:#31546b;
    font-size:.68rem;
    font-weight:700;
    backdrop-filter:blur(10px);
}
@media(max-width:1000px) {
    .hero-dna-art { display:none; }
    .reference-metric { min-height:100px; }
    .og-footer { position:static; }
}
"""

# Rebuild the page in the order shown in the reference.
before_upload = source[:upload_start]
global_block_start = source.find(
    "# ==================================================\n# GLOBAL TOP STRIP"
)
if global_block_start < 0:
    raise RuntimeError("Global strip section disappeared.")

global_end = source.find(
    "# ==================================================\n# OVERVIEW",
    global_block_start,
)
if global_end < 0:
    raise RuntimeError("Overview boundary disappeared.")

global_block = source[global_block_start:global_end]

# Remove old upload, navigation, global strip and overview blocks.
# Reinsert them in the intended order.
rebuilt = (
    before_upload
    + navigation
    + upload_code
    + global_block
    + overview_code
    + rest
)

# Add design CSS to the existing style block.
if "OMICS GUARD REFERENCE DESIGN" not in rebuilt:
    css_end = rebuilt.find("</style>")
    if css_end < 0:
        raise RuntimeError("CSS closing tag not found.")
    rebuilt = rebuilt[:css_end] + reference_css + "\n" + rebuilt[css_end:]

# Replace footer with the fixed reference-style footer.
footer_pattern = re.compile(
    r"(?ms)^# ={10,}\n# FOOTER\n# ={10,}.*\Z"
)
footer = r'''
# ==================================================
# FOOTER
# ==================================================

st.markdown(
    """
    <div class="og-footer">
        <span>🧬 &nbsp; OmicsGuard AI &nbsp; · &nbsp; MSc Bioinformatics Science Fair Project · 2026</span>
        <span>Reproducible &nbsp; · &nbsp; Explainable &nbsp; · &nbsp; Research-focused</span>
    </div>
    """,
    unsafe_allow_html=True,
)
'''

if footer_pattern.search(rebuilt):
    rebuilt = footer_pattern.sub(footer, rebuilt)

# Compile-check before writing anything.
ast.parse(rebuilt)
path.write_text(rebuilt, encoding="utf-8")

print("FULL REFERENCE DASHBOARD REBUILT.")
print("Navigation → horizontal upload toolbar → hero → metrics → charts + quick actions.")
print("Existing scientific modules preserved.")
print(f"Backup: {backup}")
