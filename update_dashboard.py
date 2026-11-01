from pathlib import Path

path = Path("app.py")
source = path.read_text(encoding="utf-8")

# --------------------------------------------------
# 1. Replace sidebar navigation with top navigation
# --------------------------------------------------

start = source.index("# ==================================================\n# SIDEBAR")
end = source.index("# ==================================================\n# GLOBAL TOP STRIP")

new_navigation = '''# ==================================================
# TOP NAVIGATION
# ==================================================

pages = [
    "Overview",
    "Integrity Audit",
    "Anomaly Analysis",
    "Fault-Injection Benchmark",
    "ML Leakage Audit",
    "Audit History",
]

if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

st.markdown(
    """
    <div class="brand-lockup" style="margin-bottom:.3rem">
        <div class="brand-mark">🧬</div>
        <div>
            <div style="font-size:1.25rem;font-weight:800;color:#17243a">
                OmicsGuard AI
            </div>
            <div style="font-size:.7rem;color:#718096;letter-spacing:.1em">
                BIOINFORMATICS RESEARCH DATA AUDITOR
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "Dashboard navigation",
    pages,
    key="page",
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown(
    f"""
    <div style="padding:9px 14px;margin:8px 0 20px;
                background:#e7f7f4;border:1px solid #c8ece6;
                border-radius:10px;color:#087e79;font-size:.78rem">
        ● ACTIVE DATASET: <b>{st.session_state.get("active_dataset_name", "GSE10072")}</b>
        &nbsp; · &nbsp; {expression.shape[0]:,} samples
        &nbsp; · &nbsp; {expression.shape[1]:,} features
    </div>
    """,
    unsafe_allow_html=True,
)


'''

source = source[:start] + new_navigation + source[end:]

# --------------------------------------------------
# 2. Add upload and before/after audit functionality
# --------------------------------------------------

anchor = "# ==================================================\n# TOP NAVIGATION"

upload_code = '''# ==================================================
# DATASET UPLOAD AND VALIDATION
# ==================================================

if "original_expression" not in st.session_state:
    st.session_state["original_expression"] = expression.copy()
    st.session_state["original_metadata"] = metadata.copy()

with st.expander("📂 Upload your own expression dataset", expanded=False):
    st.write(
        "Upload a CSV expression matrix. Rows must represent samples "
        "and columns must represent features. The first column should "
        "contain sample IDs."
    )

    uploaded_expression = st.file_uploader(
        "Expression matrix CSV",
        type=["csv"],
        key="custom_expression_upload",
    )

    uploaded_metadata = st.file_uploader(
        "Metadata CSV (optional)",
        type=["csv"],
        key="custom_metadata_upload",
    )

    if uploaded_expression is not None:
        try:
            custom_expression = pd.read_csv(
                uploaded_expression,
                index_col=0,
            )

            custom_expression.index = custom_expression.index.astype(str)
            custom_expression.columns = custom_expression.columns.astype(str)
            custom_expression = custom_expression.apply(
                pd.to_numeric, errors="coerce"
            )

            if custom_expression.empty:
                raise ValueError("The uploaded expression matrix is empty.")

            if custom_expression.index.hasnans:
                raise ValueError("Sample IDs contain missing values.")

            if custom_expression.columns.hasnans:
                raise ValueError("Feature IDs contain missing values.")

            if uploaded_metadata is not None:
                custom_metadata = pd.read_csv(uploaded_metadata)

                if "sample_id" not in custom_metadata.columns:
                    raise ValueError(
                        "Metadata CSV must contain a column named sample_id."
                    )
            else:
                custom_metadata = pd.DataFrame({
                    "sample_id": custom_expression.index.astype(str)
                })

            st.session_state["custom_expression"] = custom_expression
            st.session_state["custom_metadata"] = custom_metadata
            st.session_state["active_dataset_name"] = uploaded_expression.name

            expression = custom_expression
            metadata = custom_metadata

            st.success("Expression dataset loaded successfully.")

            st.markdown("**Uploaded dataset snapshot**")
            a, b, c, d = st.columns(4)
            a.metric("Samples", f"{expression.shape[0]:,}")
            b.metric("Features", f"{expression.shape[1]:,}")
            c.metric("Missing values", f"{int(expression.isna().sum().sum()):,}")
            d.metric("Duplicate sample IDs", f"{int(expression.index.duplicated().sum()):,}")

            if uploaded_metadata is None:
                st.info(
                    "No metadata file supplied. Sample IDs were used to "
                    "create basic metadata. Metadata-dependent checks will "
                    "therefore be limited."
                )

            st.markdown("**Before and after: integrity comparison**")

            original_results = run_integrity_checks(
                st.session_state["original_expression"],
                st.session_state["original_metadata"],
            )
            custom_results = run_integrity_checks(
                custom_expression,
                custom_metadata,
            )

            comparison = pd.DataFrame([
                {
                    "Integrity check": old["check"],
                    "Original GSE10072": old["status"],
                    "Uploaded dataset": new["status"],
                }
                for old, new in zip(original_results, custom_results)
            ])

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "The original GSE10072 dataset is retained as the reference. "
                "Uploading a file does not modify the original data."
            )

            with st.expander("Preview uploaded expression data"):
                st.dataframe(custom_expression.head(8), use_container_width=True)

            with st.expander("Preview uploaded metadata"):
                st.dataframe(custom_metadata.head(8), use_container_width=True)

        except Exception as error:
            st.error(f"Could not validate uploaded files: {error}")
            st.info(
                "Check that the expression CSV has sample IDs in its first "
                "column and numeric expression values in the remaining columns."
            )

    elif "custom_expression" in st.session_state:
        expression = st.session_state["custom_expression"]
        metadata = st.session_state["custom_metadata"]
    else:
        st.caption("No custom dataset uploaded. GSE10072 remains active.")


'''

if upload_code not in source:
    source = source.replace(anchor, upload_code + anchor, 1)

# --------------------------------------------------
# 3. Hide sidebar and style horizontal navigation
# --------------------------------------------------

css_anchor = "</style>"
extra_css = """
    /* Top navigation dashboard */
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stRadio"] > div {
        gap: 8px;
        flex-wrap: wrap;
    }
    [data-testid="stRadio"] label {
        background: #ffffff;
        border: 1px solid #dce5ed;
        border-radius: 10px;
        padding: 8px 13px;
        font-weight: 650;
    }
    [data-testid="stRadio"] label:hover {
        border-color: #12a89d;
        background: #eaf8f6;
    }
    [data-testid="stRadio"] label:has(input:checked) {
        background: #e7f7f4;
        border-color: #12a89d;
        color: #087e79;
    }
    .block-container {
        max-width: 1500px;
        padding-top: 1.5rem;
    }
"""

if extra_css not in source:
    source = source.replace(css_anchor, extra_css + "\n    " + css_anchor, 1)

# --------------------------------------------------
# 4. Update page configuration
# --------------------------------------------------

source = source.replace(
    "initial_sidebar_state=\"expanded\"",
    "initial_sidebar_state=\"collapsed\"",
    1,
)

# --------------------------------------------------
# Save safely
# --------------------------------------------------

backup = Path("app.py.before_top_navigation")
backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
path.write_text(source, encoding="utf-8")

print("Dashboard update applied.")
print(f"Backup saved as: {backup}")
