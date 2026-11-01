import pandas as pd
import pytest

from omicsguard.benchmark import (
    inject_missing_values,
    inject_duplicate_sample_id,
    inject_duplicate_probe_id,
    inject_constant_feature,
    inject_metadata_mismatch,
    evaluate_check,
    run_fault_injection_benchmark,
)


@pytest.fixture
def expression():
    return pd.DataFrame(
        [
            [1, 4, 8],
            [2, 7, 5],
            [3, 5, 9],
            [4, 8, 6],
        ],
        index=["S1", "S2", "S3", "S4"],
        columns=["P1", "P2", "P3"],
    )


@pytest.fixture
def metadata():
    return pd.DataFrame({"sample_id": ["S1", "S2", "S3", "S4"]})


def test_missing_value_injection(expression):
    corrupted = inject_missing_values(expression)

    assert pd.isna(corrupted.iloc[0, 0])
    assert not pd.isna(expression.iloc[0, 0])


def test_duplicate_sample_injection(expression):
    corrupted = inject_duplicate_sample_id(expression)

    assert corrupted.index.duplicated().any()
    assert not expression.index.duplicated().any()


def test_duplicate_probe_injection(expression):
    corrupted = inject_duplicate_probe_id(expression)

    assert corrupted.columns.duplicated().any()
    assert not expression.columns.duplicated().any()


def test_constant_feature_injection(expression):
    corrupted = inject_constant_feature(expression)

    assert corrupted["SYNTHETIC_CONSTANT_PROBE"].nunique() == 1


def test_metadata_mismatch_injection(expression, metadata):
    corrupted_expression, corrupted_metadata = (
        inject_metadata_mismatch(expression, metadata)
    )

    assert len(corrupted_metadata) == len(metadata) - 1
    assert len(corrupted_expression) == len(expression)


def test_sample_injection_requires_two_samples():
    small = pd.DataFrame({"P1": [1]}, index=["S1"])

    with pytest.raises(ValueError, match="At least two samples"):
        inject_duplicate_sample_id(small)


def test_evaluate_check_finds_expected_defect():
    checks = [
        {"check": "Missing values", "status": "WARNING"}
    ]

    detected, details = evaluate_check(checks, "Missing values")

    assert detected is True
    assert details["status"] == "WARNING"


def test_evaluate_check_rejects_unknown_check():
    with pytest.raises(ValueError, match="Check not found"):
        evaluate_check([], "Unknown check")


def test_complete_fault_injection_benchmark(
    expression, metadata, tmp_path
):
    report, summary = run_fault_injection_benchmark(
        expression, metadata, tmp_path
    )

    assert len(report) == 6
    assert summary["total_experiments"] == 6
    assert summary["injected_defect_experiments"] == 5
    assert summary["detected_defects"] == 5
    assert summary["missed_defects"] == 0
    assert summary["clean_baseline_passed"] is True

    assert (tmp_path / "fault_injection_results.csv").exists()
    assert (tmp_path / "fault_injection_summary.json").exists()
