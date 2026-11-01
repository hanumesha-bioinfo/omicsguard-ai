# OmicsGuard AI

### Bioinformatics Dataset Integrity and Machine-Learning Reliability Auditor

OmicsGuard AI is a research-support tool designed to assess the technical quality of bioinformatics datasets and screen machine-learning workflows for potential reliability issues.

It combines dataset integrity validation, anomaly detection, machine-learning leakage screening, and controlled fault-injection benchmarking in an interactive Streamlit dashboard.

## Project Objectives

- Identify common structural and data-quality problems in biological expression datasets.
- Detect samples with unusual expression profiles for further investigation.
- Screen machine-learning datasets for potential data leakage.
- Evaluate implemented integrity checks using deliberately injected defects.
- Generate reports that support reproducible dataset assessment.

## Key Features

### 1. Dataset Integrity Audit

Five checks are implemented:

- Missing-value detection.
- Duplicate sample ID detection.
- Duplicate probe ID detection.
- Constant-feature detection.
- Expression and metadata consistency.

### 2. Anomaly Detection

- Principal Component Analysis (PCA) for dimensionality reduction.
- Isolation Forest for identifying potentially unusual samples.
- Configurable contamination parameter.
- Anomaly reports and visual summaries.

An anomaly flag indicates a sample that deserves investigation. It does not prove that the sample is defective.

### 3. Fault-Injection Benchmark

The benchmark evaluates the integrity checks using a clean baseline and five deliberately injected defect scenarios:

- Missing values.
- Duplicate sample IDs.
- Duplicate probe IDs.
- Constant features.
- Metadata mismatch.

**Observed benchmark results:**

| Metric | Result |
|---|---:|
| Total experiments | 6 |
| Injected-defect experiments | 5 |
| Detected defects | 5 |
| Missed defects | 0 |
| Detection rate | 100% |
| Clean baseline passed | Yes |
| Unexpected baseline flags | 0 |

These results describe the implemented test scenarios only. They do not establish universal detection performance.

### 4. Machine-Learning Leakage Audit

The leakage screening module checks:

- Overlapping sample IDs between training and testing data.
- Identical expression profiles.
- Strong target-feature correlations.

These checks are screening methods, not proof that a complete machine-learning workflow is free from leakage.

### 5. Interactive Dashboard

The Streamlit application provides six sections:

- Overview
- Integrity Audit
- Anomaly Analysis
- Fault-Injection Benchmark
- ML Leakage Audit
- Audit History

### 6. Audit History and Reporting

- Saves audit summaries in JSON format.
- Supports review of previous audit runs.
- Generates anomaly analysis reports.
- Stores benchmark outputs for further inspection.

## Dataset

The project uses the NCBI Gene Expression Omnibus (GEO) dataset:

- **Accession:** GSE10072
- **Platform:** GPL96 (Affymetrix Human Genome U133A Array)
- **Final samples:** 107
- **Tumour samples:** 58
- **Non-tumour samples:** 49
- **Expression matrix:** 107 samples × 22,283 probes

The dataset concerns gene-expression signatures associated with cigarette smoking and lung adenocarcinoma.

Source: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE10072

## Technology Stack

- **Programming:** Python
- **Data processing:** Pandas, NumPy
- **Machine learning:** Scikit-learn
- **Statistical analysis:** SciPy
- **Visualization:** Matplotlib, Plotly
- **Dashboard:** Streamlit
- **Testing:** Pytest
- **Data source:** NCBI GEO
- **Development environment:** Linux, Git

## Project Structure

```text
omicsguard-ai/
├── app.py
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   ├── processed/
│   └── benchmark/
├── docs/
│   ├── methodology.md
│   ├── limitations.md
│   └── reproducibility.md
├── results/
│   ├── figures/
│   └── benchmark/
├── scripts/
│   ├── download_geo_data.py
│   ├── prepare_geo_data.py
│   └── run_benchmark.py
├── src/
│   └── omicsguard/
│       ├── __init__.py
│       ├── anomaly_detection.py
│       ├── audit_history.py
│       ├── benchmark.py
│       ├── ingestion.py
│       ├── integrity_checks.py
│       ├── leakage_audit.py
│       └── reporting.py
└── tests/
    ├── test_anomaly.py
    ├── test_benchmark.py
    ├── test_ingestion.py
    ├── test_integrity.py
    ├── test_leakage.py
    └── test_reporting.py
```

## Installation

Clone the repository:

```bash
git clone https://github.com/hanumesha-bioinfo/omicsguard-ai.git
cd omicsguard-ai
```

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Download and Prepare the Dataset

Download the GEO dataset:

```bash
python scripts/download_geo_data.py
```

Prepare the expression matrix and metadata:

```bash
PYTHONPATH=src python scripts/prepare_geo_data.py
```

## Run the Dashboard

```bash
PYTHONPATH=src streamlit run app.py
```

## Run the Fault-Injection Benchmark

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```

## Run Tests

```bash
PYTHONPATH=src pytest -v
```

## Documentation

Additional project documentation:

- [Methodology](docs/methodology.md)
- [Limitations](docs/limitations.md)
- [Reproducibility](docs/reproducibility.md)

## Scientific Limitations

OmicsGuard AI is a research-support prototype, not a clinical diagnostic system or a replacement for expert bioinformatics review.

- Anomaly detection does not establish that a biological sample is erroneous.
- Integrity checks cover only the conditions they are designed to detect.
- Leakage screening cannot guarantee that an entire ML workflow is leakage-free.
- Benchmark results are based on a limited set of controlled fault-injection scenarios.
- Technical validation does not guarantee biological validity or reproducibility of scientific conclusions.

Please consult the documentation before interpreting results.

## Project Status

Research and development prototype.

## Author

**Hanumesha**

MSc Bioinformatics Student | Aspiring Bioinformatics and Data Analyst

GitHub: https://github.com/hanumesha-bioinfo