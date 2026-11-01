# OmicsGuard AI — Reproducibility Guide

## 1. Purpose

This document explains how to set up, execute, and test OmicsGuard AI.

The goal is to make the demonstration workflow repeatable on another compatible Linux system.

## 2. Project Requirements

Recommended environment:

- Operating system: Linux
- Python: 3.12
- Git
- Internet connection for downloading the GEO dataset

The project uses Python libraries for data processing, machine learning, visualization, and testing.

## 3. Clone the Repository

Clone the GitHub repository:

```bash
git clone https://github.com/hanumesha-bioinfo/omicsguard-ai.git
cd omicsguard-ai
```

## 4. Create a Virtual Environment

Create and activate a Python virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

## 5. Install Dependencies

Install the project dependencies:

```bash
pip install -r requirements.txt
```

## 6. Download the GEO Dataset

The demonstration uses GSE10072 from NCBI GEO.

Run:

```bash
python scripts/download_geo_data.py
```

The downloaded Series Matrix file is stored in:

`data/raw/GSE10072_series_matrix.txt.gz`

The original dataset is excluded from Git version control so that it can be downloaded separately.

## 7. Prepare the Dataset

Run:

```bash
PYTHONPATH=src python scripts/prepare_geo_data.py
```

This prepares the expression matrix and metadata under:

`data/processed/`

The expected demonstration dataset dimensions are:

- Expression matrix: 107 samples × 22,283 probes.
- Metadata: 107 sample records.

These dimensions describe the current GSE10072 input and should be verified after preparation.

## 8. Launch the Dashboard

Start the Streamlit application:

```bash
PYTHONPATH=src streamlit run app.py
```

Open the local address displayed by Streamlit in your browser.

## 9. Run the Fault-Injection Benchmark

Execute:

```bash
PYTHONPATH=src python scripts/run_benchmark.py
```

The benchmark generates result files under:

`results/benchmark/`

It evaluates a clean baseline and five controlled defect-injection scenarios.

## 10. Run Automated Tests

Execute:

```bash
PYTHONPATH=src pytest -v
```

The test suite covers:

- Data ingestion.
- Integrity checks.
- Anomaly detection.
- Fault-injection benchmarking.
- Machine-learning leakage screening.
- Reporting.

## 11. Reproducibility Considerations

For repeatable results:

1. Use the documented Python environment.
2. Install the pinned dependencies from `requirements.txt`.
3. Use the same source dataset.
4. Avoid modifying the original downloaded GEO file.
5. Record changes to model parameters and preprocessing.
6. Run the test suite after code changes.

The anomaly detection implementation uses a fixed random state of 42. PCA uses the full SVD solver.

The Isolation Forest contamination parameter is configurable and should be recorded when comparing runs.

## 12. Dataset Provenance

Dataset: GSE10072

Provider: NCBI Gene Expression Omnibus

Accession page:

https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE10072

The raw Series Matrix file used in the current demonstration has this SHA-256 checksum:

`68fc224d6c23b1802ddc2223a0433c8cf25f11cdb9606e33736f4a0c098496af`

A checksum can be calculated using:

```bash
sha256sum data/raw/GSE10072_series_matrix.txt.gz
```

The calculated checksum should match the recorded value before using the file as the same dataset version.

## 13. Important Notes

Reproducibility of software execution does not guarantee reproducibility of biological conclusions.

Results may depend on dataset versions, preprocessing choices, model parameters, software versions, and experimental context.

OmicsGuard AI is a research-support prototype. Its outputs require scientific interpretation and independent validation.