import streamlit as st
import pandas as pd
import plotly.express as px

def apply_dashboard_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html,body,[class*="css"]{font-family:Inter,sans-serif}
    .stApp{background:#f1f7fa;color:#102b49}
    .block-container{max-width:1500px;padding:1.4rem 2rem 4rem}
    [data-testid="stSidebar"]{display:none}
    .brand{display:flex;align-items:center;gap:13px;padding:5px 0 18px}
    .brand-logo{background:linear-gradient(135deg,#00cbb7,#087e9a);border-radius:15px;padding:12px;font-size:25px}
    .brand-name{font-size:22px;font-weight:800;color:#102b49}
    .brand-sub{font-size:10px;color:#607991;letter-spacing:1px}
    .workspace{background:#dcf8ef;color:#087c58;border-radius:25px;padding:10px;text-align:center;font-size:12px;font-weight:700;margin-top:8px}
    .hero{background:radial-gradient(circle at 85% 30%,#00c9bd66,transparent 30%),linear-gradient(110deg,#062b45,#00636b,#00a99f);border-radius:24px;padding:35px;color:white;margin:20px 0}
    .hero-tag{color:#6af5ec;font-size:11px;font-weight:700;border:1px solid #28e8e0;border-radius:20px;padding:7px 12px}
    .hero h1{font-size:34px;color:white;line-height:1.2;margin:20px 0 10px}
    .hero h1 span{color:#50f0e5}
    .hero p{font-size:13px;color:#e1f7fa;max-width:650px}
    .section-title{font-size:19px;font-weight:800;color:#102b49;margin:20px 0 3px}
    .section-subtitle{font-size:12px;color:#607991;margin-bottom:14px}
    .metric{background:white;border:1px solid #dcebf2;border-radius:18px;padding:17px;min-height:120px;box-shadow:0 5px 18px #183b5b10}
    .metric-icon{font-size:23px}.metric-label{font-size:12px;color:#526b84;font-weight:700}
    .metric-value{font-size:28px;font-weight:800;color:#102b49;margin:5px 0}
    .metric-note{font-size:10px;color:#6d8299}
    .quick{background:linear-gradient(145deg,#e2faf6,#d5f5f1);border:1px solid #c5eeea;border-radius:18px;padding:18px}
    .quick h3{color:#103b50;font-size:17px}
    .quick p{font-size:12px;color:#164b62;border-bottom:1px solid #c1e8e4;padding:8px 0}
    .stButton>button{border-radius:11px;border:1px solid #b8e6e5;color:#087c79;background:white;font-weight:700}
    .stButton>button:hover{background:#e5fbf8;border-color:#00aaa8}
    [data-testid="stFileUploaderDropzone"]{background:#f7ffff;border:1px solid #00aaa8;border-radius:12px;padding:5px}
    [data-testid="stFileUploaderDropzoneInstructions"],[data-testid="stFileUploaderDropzone"] svg{display:none!important}
    .footer{border-top:1px solid #d9e8ed;margin-top:30px;padding:15px;color:#58718c;font-size:11px}
    </style>
    """,unsafe_allow_html=True)

def render_dashboard_header():
    a,b=st.columns([4,1])
    with a:
        st.markdown('<div class="brand"><div class="brand-logo">🧬</div><div><div class="brand-name">OmicsGuard AI</div><div class="brand-sub">BIOINFORMATICS RESEARCH DATA AUDITOR</div></div></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="workspace">🟢 Local Analysis Workspace</div>',unsafe_allow_html=True)

def render_upload_toolbar():
    st.markdown('<div class="section-title">☁️ Upload Your Own Dataset</div><div class="section-subtitle">Upload expression matrix and metadata files to verify their quality.</div>',unsafe_allow_html=True)
    a,b,c=st.columns([1,1,.7])
    with a:
        expression_file=st.file_uploader("Expression CSV",type=["csv"],key="omicsguard_expression")
    with b:
        metadata_file=st.file_uploader("Metadata CSV",type=["csv"],key="omicsguard_metadata")
    with c:
        st.write("")
        verify=st.button("🔎 Verify Dataset",use_container_width=True)
    return expression_file,metadata_file,verify

def render_dashboard_overview(expression,metadata):
    if expression is None or expression.empty:
        st.warning("No expression dataset is loaded.")
        return
    if metadata is None:
        metadata=pd.DataFrame()
    samples=len(expression)
    features=len(expression.columns)
    fields=len(metadata.columns)
    missing=int(expression.isna().sum().sum())

    st.markdown("""
    <div class="hero">
    <span class="hero-tag">⚗ SCIENTIFIC DATA QUALITY PLATFORM</span>
    <h1>Trust your omics data.<br><span>Audit before you analyse.</span></h1>
    <p>An integrated bioinformatics platform to evaluate expression data integrity,
    explore unusual sample profiles, benchmark defect detection and screen ML leakage signals.</p>
    </div>
    """,unsafe_allow_html=True)

    st.markdown('<div class="section-title">Dataset Snapshot</div><div class="section-subtitle">Quick overview of your current dataset</div>',unsafe_allow_html=True)
    metrics=[("🛢️","Total Samples",samples,"Expression profiles"),("⚗️","Probe Features",features,"Measured features"),("▦","Metadata Fields",fields,"Sample annotations"),("⚠️","Missing Values",missing,"In expression matrix")]
    cols=st.columns(4)
    for col,(icon,label,value,note) in zip(cols,metrics):
        with col:
            st.markdown(f'<div class="metric"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div><div class="metric-value">{value:,}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">Biological Composition</div><div class="section-subtitle">Explore sample annotations and distributions</div>',unsafe_allow_html=True)
    tissue=next((x for x in metadata.columns if any(k in x.lower() for k in ["tissue","source_name","type"])),None)
    smoking=next((x for x in metadata.columns if "smok" in x.lower()),None)
    a,b,c=st.columns([1,1.15,.8])
    with a:
        st.markdown("**◉ Tissue Type Distribution**")
        if tissue:
            counts=metadata[tissue].fillna("Unknown").astype(str).value_counts()
            fig=px.pie(names=counts.index,values=counts.values,hole=.6)
            fig.update_layout(height=280,margin=dict(t=10,b=5,l=5,r=5))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("No tissue annotation column detected.")
    with b:
        st.markdown("**▥ Sample Category Distribution**")
        if smoking:
            counts=metadata[smoking].fillna("Unknown").astype(str).value_counts()
            fig=px.bar(x=counts.index,y=counts.values,text=counts.values)
            fig.update_traces(marker_color="#00aaa8")
            fig.update_layout(height=280,margin=dict(t=10,b=5,l=5,r=5))
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.info("No smoking annotation column detected.")
    with c:
        st.markdown('<div class="quick"><h3>⚡ Quick Actions</h3><p>🛡️ Integrity Audit</p><p>▥ Anomaly Analysis</p><p>▤ Fault-Injection Benchmark</p><p>⚗️ ML Leakage Audit</p><p>◷ Audit History</p></div>',unsafe_allow_html=True)
        for label,page in [("Integrity Audit","Integrity Audit"),("Anomaly Analysis","Anomaly Analysis"),("Run Benchmark","Fault-Injection Benchmark"),("Leakage Audit","ML Leakage Audit"),("Audit History","Audit History")]:
            if st.button(label,key="quick_"+page,use_container_width=True):
                st.session_state["page"]=page
                st.rerun()
    st.markdown('<div class="footer">🧬 OmicsGuard AI · Bioinformatics Research Data Auditor · 2026</div>',unsafe_allow_html=True)
