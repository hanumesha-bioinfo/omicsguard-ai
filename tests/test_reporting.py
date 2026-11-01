import json

import pandas as pd

import omicsguard.reporting as reporting


def test_anomaly_report_saves_selected_contamination(tmp_path, monkeypatch):
    monkeypatch.setattr(reporting, "RESULTS_DIR", tmp_path)

    results = {
        "pca": pd.DataFrame(
            {"PC1": [1.0, 2.0], "PC2": [0.5, 1.5]},
            index=pd.Index(["S1", "S2"], name="sample_id"),
        ),
        "anomalies": pd.DataFrame({
            "sample_id": ["S1", "S2"],
            "is_anomaly": [True, False],
        }),
        "explained_variance": [0.6, 0.3],
    }

    paths = reporting.save_anomaly_reports(
        results, contamination=0.07
    )

    with open(paths["summary"], encoding="utf-8") as file:
        summary = json.load(file)

    assert summary["contamination_parameter"] == 0.07
    assert summary["total_samples"] == 2
    assert summary["potential_anomalies"] == 1
