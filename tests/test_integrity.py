import pandas as pd

from omicsguard.integrity_checks import (
    check_missing_values,
    check_duplicate_sample_ids,
    check_duplicate_probe_ids,
    check_constant_features,
    check_metadata_consistency,
    run_integrity_checks,
)


def sample_expression():
    return pd.DataFrame(
        [[1, 4, 7], [2, 5, 8], [3, 6, 9]],
        index=["S1", "S2", "S3"],
        columns=["P1", "P2", "P3"],
    )


def sample_metadata():
    return pd.DataFrame({"sample_id": ["S1", "S2", "S3"]})


def test_missing_values_detected():
    data = sample_expression()
    data.iloc[0, 0] = float("nan")

    result = check_missing_values(data)

    assert result["status"] == "WARNING"
    assert result["total_missing"] == 1


def test_clean_data_has_no_missing_values():
    result = check_missing_values(sample_expression())

    assert result["status"] == "PASS"
    assert result["total_missing"] == 0


def test_duplicate_sample_ids_detected():
    data = sample_expression()
    data.index = ["S1", "S1", "S3"]

    result = check_duplicate_sample_ids(data)

    assert result["status"] == "FAIL"
    assert result["duplicate_count"] == 1


def test_duplicate_probe_ids_detected():
    data = sample_expression()
    data.columns = ["P1", "P1", "P3"]

    result = check_duplicate_probe_ids(data)

    assert result["status"] == "FAIL"
    assert result["duplicate_count"] == 1


def test_constant_features_detected():
    data = sample_expression()
    data["P4"] = 5

    result = check_constant_features(data)

    assert result["status"] == "WARNING"
    assert result["constant_probe_count"] == 1


def test_metadata_mismatch_detected():
    metadata = pd.DataFrame({"sample_id": ["S1", "S2"]})

    result = check_metadata_consistency(
        sample_expression(), metadata
    )

    assert result["status"] == "FAIL"
    assert result["missing_metadata_samples"] == ["S3"]


def test_missing_sample_id_column_fails():
    metadata = pd.DataFrame({"id": ["S1", "S2", "S3"]})

    result = check_metadata_consistency(
        sample_expression(), metadata
    )

    assert result["status"] == "FAIL"


def test_all_integrity_checks_run():
    results = run_integrity_checks(
        sample_expression(), sample_metadata()
    )

    assert len(results) == 5
    assert all(result["status"] == "PASS" for result in results)
