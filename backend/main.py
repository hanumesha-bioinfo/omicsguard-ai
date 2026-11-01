from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from omicsguard.integrity_checks import run_integrity_checks
from omicsguard.anomaly_detection import run_anomaly_analysis
from omicsguard.reporting import save_anomaly_reports
from omicsguard.benchmark import run_fault_injection_benchmark
from omicsguard.audit_history import save_audit_history, get_audit_history
from omicsguard.leakage_audit import run_leakage_audit
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RESULTS_DIR = PROJECT_ROOT / "results"

EXPRESSION_FILE = PROCESSED_DIR / "GSE10072_expression.csv"
METADATA_FILE = PROCESSED_DIR / "GSE10072_metadata.csv"

app = FastAPI(
    title="OmicsGuard AI API",
    description="Bioinformatics Dataset Integrity and ML Reliability Auditor",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_current_dataset():
    """Load the existing processed GSE10072 expression and metadata files."""

    if not EXPRESSION_FILE.exists() or not METADATA_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Processed dataset files were not found.",
        )

    try:
        expression = pd.read_csv(EXPRESSION_FILE, index_col=0)
        metadata = pd.read_csv(METADATA_FILE)

        expression = expression.apply(pd.to_numeric, errors="coerce")

        return expression, metadata

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not load dataset: {str(exc)}",
        )


@app.get("/")
def root():
    return {
        "application": "OmicsGuard AI",
        "status": "online",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "message": "Backend connected successfully",
    }


@app.get("/api/dataset/summary")
def dataset_summary():
    expression, metadata = load_current_dataset()

    tissue_counts = {}

    if "source_name_ch1" in metadata.columns:
        tissue_counts = (
            metadata["source_name_ch1"]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .to_dict()
        )

    return {
        "dataset": "GSE10072",
        "expression": {
            "samples": int(expression.shape[0]),
            "probes": int(expression.shape[1]),
            "missing_values": int(expression.isna().sum().sum()),
            "duplicate_sample_ids": int(
                expression.index.duplicated().sum()
            ),
            "duplicate_probe_ids": int(
                expression.columns.duplicated().sum()
            ),
        },
        "metadata": {
            "samples": int(metadata.shape[0]),
            "columns": int(metadata.shape[1]),
            "column_names": metadata.columns.tolist(),
            "tissue_descriptions": tissue_counts,
        },
    }


@app.post("/api/audit/integrity")
def integrity_audit():
    expression, metadata = load_current_dataset()

    try:
        results = run_integrity_checks(expression, metadata)

        summary = {
            "total_checks": len(results),
            "passed": sum(r["status"] == "PASS" for r in results),
            "warnings": sum(r["status"] == "WARNING" for r in results),
            "failed": sum(r["status"] == "FAIL" for r in results),
            "skipped": sum(r["status"] == "SKIPPED" for r in results),
        }

        save_audit_history("integrity", summary)

        return {
            "analysis": "integrity",
            "summary": summary,
            "results": results,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/audit/anomaly")
def anomaly_audit():
    expression, _ = load_current_dataset()

    try:
        if expression.isna().any().any():
            raise HTTPException(
                status_code=422,
                detail=(
                    "Anomaly detection requires expression data "
                    "without missing values. Run integrity checks first."
                ),
            )

        results = run_anomaly_analysis(expression)

        report_paths = save_anomaly_reports(results)

        pca = results["pca"].reset_index()
        anomalies = results["anomalies"]

        summary = {
            "total_samples": int(len(anomalies)),
            "potential_anomalies": int(anomalies["is_anomaly"].sum()),
            "typical_profiles": int((~anomalies["is_anomaly"]).sum()),
            "flagged_percentage": round(
                float(anomalies["is_anomaly"].mean() * 100), 2
            ),
            "pca_explained_variance": [
                float(value)
                for value in results["explained_variance"]
            ],
            "method": "Isolation Forest",
            "interpretation": (
                "Potential anomalies require investigation; "
                "they are not confirmed defective samples."
            ),
        }

        save_audit_history("anomaly", summary)

        return {
            "analysis": "anomaly",
            "summary": summary,
            "pca": pca.to_dict(orient="records"),
            "anomalies": anomalies.to_dict(orient="records"),
            "reports": {
                name: str(path.relative_to(PROJECT_ROOT))
                for name, path in report_paths.items()
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/audit/benchmark")
def benchmark_audit():
    expression, metadata = load_current_dataset()

    try:
        output_dir = RESULTS_DIR / "benchmark"

        report, summary = run_fault_injection_benchmark(
            expression,
            metadata,
            output_dir,
        )

        save_audit_history("benchmark", summary)

        return {
            "analysis": "benchmark",
            "summary": summary,
            "experiments": report.to_dict(orient="records"),
            "metrics": summary["per_check_metrics"],
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/audit/history")
def audit_history():
    return {
        "records": get_audit_history(),
    }



@app.post("/api/audit/leakage")
def leakage_audit():
    expression, metadata = load_current_dataset()

    try:
        required_columns = {"sample_id", "source_name_ch1"}
        missing_columns = required_columns - set(metadata.columns)

        if missing_columns:
            raise HTTPException(
                status_code=422,
                detail=f"Missing metadata columns: {sorted(missing_columns)}",
            )

        # Map the actual tissue descriptions to binary labels.
        label_mapping = {
            "adenocarcinoma of the lung": 1,
            "normal lung tissue": 0,
        }

        metadata = metadata.copy()
        metadata["sample_id"] = metadata["sample_id"].astype(str).str.strip()
        metadata["source_name_ch1"] = (
            metadata["source_name_ch1"].astype(str).str.strip().str.lower()
        )

        if metadata["sample_id"].duplicated().any():
            raise HTTPException(
                status_code=422,
                detail="Duplicate sample IDs found in metadata. Resolve them before the leakage audit.",
            )

        metadata = metadata.set_index("sample_id")
        metadata["target"] = metadata["source_name_ch1"].map(label_mapping)

        # Match metadata and expression samples by their IDs.
        expression.index = expression.index.astype(str).str.strip()
        common_ids = expression.index.intersection(metadata.index)

        if len(common_ids) == 0:
            raise HTTPException(
                status_code=422,
                detail="No matching sample IDs between expression data and metadata.",
            )

        matched_expression = expression.loc[common_ids].copy()
        matched_labels = metadata.loc[common_ids, "target"]

        valid = matched_labels.notna()
        matched_expression = matched_expression.loc[valid]
        matched_labels = matched_labels.loc[valid].astype(int)

        if matched_labels.nunique() != 2:
            raise HTTPException(
                status_code=422,
                detail="Both tumor and normal classes are required for a stratified split.",
            )

        if matched_labels.value_counts().min() < 2:
            raise HTTPException(
                status_code=422,
                detail="Not enough samples in each class to create a stratified split.",
            )

        if matched_expression.isna().any().any():
            raise HTTPException(
                status_code=422,
                detail="Missing expression values detected. Resolve them before leakage screening.",
            )

        # Reproducible, stratified 80/20 split.
        train_ids, test_ids = train_test_split(
            matched_expression.index.tolist(),
            test_size=0.20,
            random_state=42,
            stratify=matched_labels.to_numpy(),
        )

        train_expression = matched_expression.loc[train_ids]
        test_expression = matched_expression.loc[test_ids]
        train_labels = matched_labels.loc[train_ids]

        results = run_leakage_audit(
            train_expression=train_expression,
            test_expression=test_expression,
            train_labels=train_labels,
            correlation_threshold=0.95,
        )

        summary = {
            "dataset": "GSE10072",
            "total_samples": int(len(matched_expression)),
            "training_samples": int(len(train_expression)),
            "testing_samples": int(len(test_expression)),
            "training_class_counts": {
                "normal": int((train_labels == 0).sum()),
                "tumor": int((train_labels == 1).sum()),
            },
            "testing_class_counts": {
                "normal": int((matched_labels.loc[test_ids] == 0).sum()),
                "tumor": int((matched_labels.loc[test_ids] == 1).sum()),
            },
            "split": "Stratified 80/20",
            "random_state": 42,
            "total_checks": len(results),
            "passed": sum(r["status"] == "PASS" for r in results),
            "warnings": sum(r["status"] == "WARNING" for r in results),
            "failed": sum(r["status"] == "FAIL" for r in results),
        }

        save_audit_history("leakage", summary)

        return {
            "analysis": "leakage",
            "summary": summary,
            "results": results,
            "interpretation": (
                "This is a leakage screening audit. Strong target-feature "
                "associations and duplicate profiles require investigation; "
                "they do not independently prove data leakage."
            ),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
