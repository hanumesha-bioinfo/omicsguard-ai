import pandas as pd

from omicsguard.leakage_audit import (
    check_sample_overlap,
    check_duplicate_profiles,
    check_target_feature_association,
    run_leakage_audit,
)


def test_sample_overlap_detected():
    train = pd.DataFrame(
        [[1, 2], [3, 4]],
        index=["S1", "S2"],
        columns=["P1", "P2"],
    )

    test = pd.DataFrame(
        [[5, 6], [7, 8]],
        index=["S2", "S3"],
        columns=["P1", "P2"],
    )

    result = check_sample_overlap(train, test)

    assert result["status"] == "FAIL"
    assert result["overlap_count"] == 1


def test_duplicate_profiles_detected():
    train = pd.DataFrame(
        [[1, 2], [3, 4]],
        index=["S1", "S2"],
        columns=["P1", "P2"],
    )

    test = pd.DataFrame(
        [[1, 2], [8, 9]],
        index=["S3", "S4"],
        columns=["P1", "P2"],
    )

    result = check_duplicate_profiles(train, test)

    assert result["duplicate_profile_count"] == 1
    assert result["status"] == "WARNING"


def test_target_feature_association_detected():
    train = pd.DataFrame({
        "P1": [0, 1, 0, 1, 0, 1],
        "P2": [2, 3, 5, 4, 1, 6],
    })

    labels = pd.Series([0, 1, 0, 1, 0, 1])

    result = check_target_feature_association(
        train,
        labels,
        correlation_threshold=0.95,
    )

    assert result["flagged_feature_count"] >= 1
    assert result["status"] == "WARNING"


def test_clean_split_passes_overlap_and_duplicate_checks():
    train = pd.DataFrame(
        [[1, 2], [3, 4]],
        index=["S1", "S2"],
        columns=["P1", "P2"],
    )

    test = pd.DataFrame(
        [[5, 6], [7, 8]],
        index=["S3", "S4"],
        columns=["P1", "P2"],
    )

    labels = pd.Series([0, 1], index=train.index)

    results = run_leakage_audit(train, test, labels)

    assert results[0]["status"] == "PASS"
    assert results[1]["status"] == "PASS"