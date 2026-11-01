import numpy as np
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def run_pca(expression, n_components=2):
    """Perform PCA on sample-by-probe expression data."""

    if expression.isna().any().any():
        raise ValueError("Expression data contains missing values.")

    if expression.shape[0] < n_components:
        raise ValueError("Not enough samples for requested PCA components.")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(expression)

    pca = PCA(n_components=n_components, svd_solver="full")
    coordinates = pca.fit_transform(scaled_data)

    results = pd.DataFrame(
        coordinates,
        index=expression.index,
        columns=[
            f"PC{i + 1}" for i in range(n_components)
        ],
    )

    results.index.name = "sample_id"

    return results, pca.explained_variance_ratio_


def detect_anomalies(expression, contamination=0.05, random_state=42):
    """Identify potentially unusual samples using Isolation Forest."""

    if expression.isna().any().any():
        raise ValueError("Expression data contains missing values.")

    if not 0 < contamination < 0.5:
        raise ValueError("Contamination must be between 0 and 0.5.")

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(expression)

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=200,
    )

    predictions = model.fit_predict(scaled_data)
    scores = model.decision_function(scaled_data)

    results = pd.DataFrame({
        "sample_id": expression.index,
        "anomaly_score": scores,
        "anomaly_prediction": predictions,
        "is_anomaly": predictions == -1,
    })

    results["anomaly_label"] = np.where(
        results["is_anomaly"],
        "Potential anomaly",
        "Typical profile",
    )

    return results


def run_anomaly_analysis(expression):
    """Run PCA and Isolation Forest analysis."""

    pca_results, explained_variance = run_pca(expression)

    anomaly_results = detect_anomalies(expression)

    return {
        "pca": pca_results,
        "explained_variance": explained_variance,
        "anomalies": anomaly_results,
    }
