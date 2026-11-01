from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results"


def save_anomaly_reports(results, contamination=0.05):
    """Save PCA coordinates, anomaly predictions and summary."""

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    pca = results["pca"]
    anomalies = results["anomalies"]
    explained_variance = results["explained_variance"]

    pca_path = RESULTS_DIR / "pca_coordinates.csv"
    anomaly_path = RESULTS_DIR / "anomaly_predictions.csv"
    summary_path = RESULTS_DIR / "anomaly_summary.json"

    pca.to_csv(pca_path)
    anomalies.to_csv(anomaly_path, index=False)

    summary = {
        "total_samples": int(len(anomalies)),
        "potential_anomalies": int(anomalies["is_anomaly"].sum()),
        "typical_profiles": int((~anomalies["is_anomaly"]).sum()),
        "flagged_percentage": round(
            float(anomalies["is_anomaly"].mean() * 100), 2
        ),
        "pca_explained_variance": [
            round(float(value), 6)
            for value in explained_variance
        ],
        "method": "Isolation Forest",
        "contamination_parameter": float(contamination),
        "random_state": 42,
        "interpretation": (
            "Potential anomalies require further investigation. "
            "They are not confirmed defective samples."
        ),
    }

    with open(summary_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    return {
        "pca": pca_path,
        "anomalies": anomaly_path,
        "summary": summary_path,
    }
