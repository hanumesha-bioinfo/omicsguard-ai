from pathlib import Path

path = Path("app.py")
source = path.read_text(encoding="utf-8")

# Locate the existing upload section and navigation.
upload_start = source.find(
    "# ==================================================\n# DATASET UPLOAD AND VALIDATION"
)
nav_start = source.find(
    "# ==================================================\n# TOP NAVIGATION"
)
global_start = source.find(
    "# ==================================================\n# GLOBAL TOP STRIP"
)

if min(upload_start, nav_start, global_start) < 0:
    raise SystemExit("Required sections not found. No changes made.")

if not upload_start < nav_start < global_start:
    raise SystemExit(
        "Unexpected section order. No changes made."
    )

# Move the complete existing upload/validation section.
upload_block = source[upload_start:nav_start]
source = source[:upload_start] + source[nav_start:]

# Find the global strip again after removing the upload section.
global_start = source.find(
    "# ==================================================\n# GLOBAL TOP STRIP"
)

# Put upload directly after navigation.
source = (
    source[:global_start]
    + upload_block
    + "\n"
    + source[global_start:]
)

# Keep the upload panel visible, immediately below navigation.
source = source.replace(
    'st.expander("📂 Upload your own expression dataset — CSV files", expanded=False)',
    'st.expander("📂 Upload your own dataset — CSV files", expanded=True)',
)
source = source.replace(
    'st.expander("📂 Upload your own expression dataset", expanded=False)',
    'st.expander("📂 Upload your own dataset — CSV files", expanded=True)',
)

# Add the reference-inspired design overrides.
reference_css = r"""
/* =====================================================
   REFERENCE DASHBOARD LAYOUT — OMICSGUARD AI
   ===================================================== */

.stApp {
    background:
        radial-gradient(ellipse at 5% 20%, #e1f8f5 0%, transparent 30%),
        linear-gradient(135deg, #f5f9ff 0%, #eef8f8 100%);
}

.block-container {
    max-width: 1500px !important;
    padding: 1.0rem 2rem 3.5rem !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

/* Brand */
.brand-lockup {
    display: flex;
    align-items: center;
    gap: 13px;
    margin-bottom: 10px !important;
}

.brand-mark {
    width: 51px;
    height: 51px;
    border-radius: 15px;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(145deg,#08b9ad,#087e91);
    color: white;
    box-shadow: 0 5px 15px #0caaa433;
}

/* Navigation */
[data-testid="stRadio"] > div {
    display: flex;
    flex-wrap: nowrap;
    gap: 10px;
    padding: 7px 0 12px;
}

[data-testid="stRadio"] label {
    flex: 1;
    justify-content: center;
    text-align: center;
    white-space: nowrap;
    background: white;
    border: 1px solid #e1ebf3;
    border-radius: 15px;
    padding: 9px 12px;
    box-shadow: 0 4px 12px #12384b0c;
    font-weight: 750;
}

[data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(100deg,#009b9d,#08c4a5);
    border-color: #08bda9;
    color: white !important;
    box-shadow: 0 5px 16px #00a99b40;
}

[data-testid="stRadio"] label:has(input:checked) p {
    color: white !important;
}

/* Upload area */
[data-testid="stExpander"] {
    background: linear-gradient(105deg,#ffffff,#e9fbf8) !important;
    border: 1px solid #8be3d9 !important;
    border-radius: 19px !important;
    box-shadow: 0 5px 18px #0b99991a;
    margin: 3px 0 16px;
}

[data-testid="stExpander"] summary {
    color: #075c65;
    font-weight: 800;
    padding: 12px 15px;
}

[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #63cfc5;
    border-radius: 13px;
    padding: 9px;
}

/* Hero banner */
.hero {
    position: relative;
    overflow: hidden;
    isolation: isolate;
    min-height: 220px;
    padding: 30px 35px !important;
    border-radius: 22px;
    background:
        radial-gradient(circle at 78% 50%,#0bc8b2aa 0%,transparent 27%),
        linear-gradient(110deg,#032e43 0%,#00556a 58%,#00a99e 100%);
    box-shadow: 0 12px 28px #034d6330;
    color: white !important;
}

.hero::after {
    content: "🧬";
    position: absolute;
    right: 7%;
    top: -17px;
    z-index: -1;
    font-size: 160px;
    opacity: .25;
    transform: rotate(-20deg);
}

.hero-kicker {
    color: #58f4e7 !important;
    font-weight: 800;
    letter-spacing: .1em;
}

.hero-title {
    color: white !important;
    font-size: clamp(2rem,3vw,2.7rem) !important;
    font-weight: 850;
    line-height: 1.12;
}

.hero-copy {
    color: #e0f6f8 !important;
    max-width: 720px;
    line-height: 1.55;
}

.hero-tag {
    display: inline-block;
    background: #003d527a;
    border: 1px solid #52dcd2;
    color: white !important;
    border-radius: 25px;
    padding: 7px 12px;
}

/* Section headings */
.section-heading {
    color: #092e4b;
    font-weight: 850;
}

/* Four dashboard metric cards */
.metric-card {
    background: linear-gradient(140deg,#ffffff,#f7fcff);
    border: 1px solid #dcebf4;
    border-radius: 19px;
    padding: 18px 19px;
    min-height: 115px;
    box-shadow: 0 5px 17px #123d5a0c;
}

.metric-card .metric-label {
    color: #496579;
    font-size: .75rem;
    font-weight: 750;
}

.metric-card .metric-value {
    color: #092f52;
    font-size: 2rem;
    font-weight: 900;
}

.metric-card .metric-note {
    color: #71879b;
    font-size: .75rem;
}

/* Quick action cards */
.module-card {
    background: linear-gradient(145deg,#ffffff,#f1fbfa);
    border: 1px solid #d9efed;
    border-radius: 15px;
    padding: 17px;
    box-shadow: 0 5px 14px #0a66740c;
}

.module-card:hover {
    border-color: #44c9bd;
    transform: translateY(-2px);
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    font-weight: 750;
    min-height: 40px;
    border-color: #b9e5df;
}

.stButton > button[kind="primary"] {
    color: white;
    background: linear-gradient(100deg,#009c9c,#08c5a5);
    border: none;
}

/* Tables and charts */
[data-testid="stDataFrame"] {
    border: 1px solid #dfebf1;
    border-radius: 13px;
    overflow: hidden;
}

/* Footer */
.og-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    display: flex;
    justify-content: space-between;
    padding: 11px 25px;
    background: #f4f9ffed;
    border-top: 1px solid #dce8ef;
    color: #31546b;
    font-size: .72rem;
    font-weight: 650;
    backdrop-filter: blur(12px);
}

@media(max-width:1000px) {
    [data-testid="stRadio"] > div {
        flex-wrap: wrap;
    }
    [data-testid="stRadio"] label {
        flex: 1 1 28%;
    }
    .hero::after {
        right: 0;
        font-size: 100px;
    }
}
"""

if "REFERENCE DASHBOARD LAYOUT — OMICSGUARD AI" not in source:
    css_end = source.find("</style>")
    if css_end == -1:
        raise SystemExit("CSS closing tag not found. No changes made.")
    source = source[:css_end] + reference_css + "\n" + source[css_end:]

# Ensure changes are syntactically valid before saving.
import ast
ast.parse(source)

path.write_text(source, encoding="utf-8")
print("Reference-inspired layout applied successfully.")
print("Upload section moved below navigation.")
print("Existing analysis code preserved.")
