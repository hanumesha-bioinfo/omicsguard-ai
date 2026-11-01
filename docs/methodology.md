# OmicsGuard AI — Methodology

## 1. Project Overview

OmicsGuard AI is a bioinformatics dataset integrity and machine-learning reliability auditing tool. It evaluates gene-expression data quality, identifies potential anomalous samples, performs controlled fault-injection experiments, and screens selected machine-learning leakage risks.

The tool supports dataset quality assessment. It does not replace biological interpretation or expert scientific review.

## 2. Dataset

The demonstration dataset is GSE10072 from the NCBI Gene Expression Omnibus (GEO).

- **GEO accession:** GSE10072
- **Organism:** Homo sapiens
- **Platform:** GPL96
- **Samples:** 107
- **Expression features/probes:** 22,283
- **Metadata records:** 107

**Source:** https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE10072

## 3. Data Ingestion and Preparation

The ingestion module reads the GEO Series Matrix file and extracts the expression matrix and sample metadata.

The expression matrix uses samples as rows and probes as columns. Metadata is aligned using sample identifiers.

Processed files are saved under `data/processed/`.

OmicsGuard does not perform a new biological normalization procedure during ingestion. It uses expression values as supplied in the GEO Series Matrix.

## 4. Dataset Integrity Checks

The integrity module performs five checks:

1. **Missing values:** Identifies missing expression values.
2. **Duplicate sample IDs:** Detects repeated sample identifiers.
3. **Duplicate probe IDs:** Detects repeated feature identifiers.
4. **Constant features:** Identifies features with no variation.
5. **Metadata consistency:** Checks whether expression and metadata sample identifiers match.

Each check returns a status and supporting information. Possible statuses include `PASS`, `WARNING`, `FAIL`, and `SKIPPED`.

## 5. Anomaly Detection

### 5.1 Principal Component Analysis

PCA reduces the expression data to two dimensions for exploratory visualization.

Processing steps:

1. Standardize expression features using `StandardScaler`.
2. Apply PCA with two components.
3. Use the full SVD solver.
4. Return sample coordinates and explained variance.

Explained variance indicates how much variation in the standardized dataset is represented by each principal component.

### 5.2 Isolation Forest

Isolation Forest identifies samples with unusual expression profiles.

Current implementation settings:

- StandardScaler preprocessing.
- 200 estimators.
- Random state: 42.
- Default contamination: 0.05.

The contamination parameter is configurable. It represents the assumed proportion of potential outliers, not the known proportion of defective biological samples.

Detected samples are labelled as potential anomalies and should be reviewed before drawing biological conclusions.

## 6. Fault-Injection Benchmark

The benchmark evaluates whether integrity checks detect deliberately introduced data defects.

Five defect types are tested:

1. Missing values.
2. Duplicate sample IDs.
3. Duplicate probe IDs.
4. Constant features.
5. Metadata mismatch.

A clean baseline experiment is also performed. Each defect is introduced independently into a copy of the input data.

The benchmark records detection outcomes, runtime, and metrics such as precision, recall, F1-score, and detection rate where applicable.

The current demonstration contains one clean baseline and one injected example for each defect type. These results demonstrate behaviour on controlled examples; they are not generalizable estimates of real-world detection performance.

## 7. Machine-Learning Leakage Screening

The leakage audit currently includes three checks:

### 7.1 Sample Overlap

Checks whether sample identifiers occur in both training and testing expression datasets.

### 7.2 Duplicate Profiles

Compares hashes of sample expression profiles to identify identical profiles across datasets.

### 7.3 Target-Feature Association

Screens numeric target labels for unusually high absolute feature correlations using a configurable threshold.

A high association is a warning for further investigation. It is not proof of data leakage or an invalid model.

These checks are screening procedures. They do not inspect every possible source of leakage in model-training code or experimental design.

## 8. Reporting and Audit History

The reporting module saves anomaly analysis results and summary information.

The audit history module records selected analysis runs with:

- Run identifier.
- Analysis type.
- UTC timestamp.
- Summary information.

The Streamlit dashboard provides access to available audit results and history.

## 9. Software Testing

The project uses pytest to test ingestion, integrity checks, anomaly detection, fault injection, leakage screening, and reporting.

Run the test suite using:

```bash
PYTHONPATH=src pytest -v
```

## 10. Interpretation

A `PASS` result means that a particular implemented check did not identify its target condition. It does not establish that the dataset is biologically valid, unbiased, or suitable for every research question.

All findings should be interpreted in the context of study design, sample metadata, experimental methods, and biological knowledge.