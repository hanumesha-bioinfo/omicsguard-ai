import pandas as pd
import pytest

from omicsguard.anomaly_detection import (
    run_pca,
    detect_anomalies,
    run_anomaly_analysis,
)


@pytest.fixture
def expression():
    return pd.DataFrame(
        [
            [1, 5, 9],
            [2, 4, 8],
            [3, 7, 6],
            [4, 6, 5],
            [5, 8, 4],
            [6, 3, 7],
        ],
        index=[f"S{i}" for i in range(1, 7)],
        columns=["P1", "P2", "P3"],
    )


def test_pca_returns_two_components(expression):
    coordinates, variance = run_pca(expression)

    assert coordinates.shape == (6, 2)
    assert list(coordinates.columns) == ["PC1", "PC2"]
    assert len(variance) == 2


def test_pca_preserves_sample_ids(expression):
    coordinates, _ = run_pca(expression)

    assert list(coordinates.index) == list(expression.index)
    assert coordinates.index.name == "sample_id"


def test_pca_rejects_missing_values(expression):
    expression.iloc[0, 0] = float("nan")

    with pytest.raises(ValueError, match="missing values"):
        run_pca(expression)


def test_pca_rejects_too_few_samples(expression):
    with pytest.raises(ValueError, match="Not enough samples"):
        run_pca(expression.iloc[:1], n_components=2)


def test_anomaly_detection_returns_expected_columns(expression):
    result = detect_anomalies(expression, contamination=0.25)

    expected = {
        "sample_id",
        "anomaly_score",
        "anomaly_prediction",
        "is_anomaly",
        "anomaly_label",
    }

    assert expected.issubset(result.columns)
    assert len(result) == len(expression)
    assert result["is_anomaly"].dtype == bool


def test_anomaly_detection_is_reproducible(expression):
    first = detect_anomalies(
        expression, contamination=0.25, random_state=42
    )
    second = detect_anomalies(
        expression, contamination=0.25, random_state=42
    )

    assert first["anomaly_prediction"].tolist() == (
        second["anomaly_prediction"].tolist()
    )


def test_anomaly_detection_rejects_missing_values(expression):
    expression.iloc[0, 0] = float("nan")

    with pytest.raises(ValueError, match="missing values"):
        detect_anomalies(expression)


@pytest.mark.parametrize("contamination", [0, 0.5, 1, -0.1])
def test_anomaly_detection_rejects_invalid_contamination(
    expression, contamination
):
    with pytest.raises(ValueError, match="Contamination"):
        detect_anomalies(expression, contamination=contamination)


def test_complete_anomaly_analysis(expression):
    results = run_anomaly_analysis(expression)

    assert set(results) == {
        "pca", "explained_variance", "anomalies"
    }
    assert len(results["anomalies"]) == len(expression)


def test_pca_is_reproducible(expression):
    first_coordinates, first_variance = run_pca(expression)
    second_coordinates, second_variance = run_pca(expression)

    pd.testing.assert_frame_equal(first_coordinates, second_coordinates)
    assert first_variance.tolist() == pytest.approx(
        second_variance.tolist()
    )
