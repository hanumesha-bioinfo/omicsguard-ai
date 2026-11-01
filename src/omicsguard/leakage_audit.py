import numpy as np
import pandas as pd


def check_sample_overlap(train_expression, test_expression):
    """Identify sample IDs present in both training and testing data."""

    overlap = sorted(
        set(train_expression.index.astype(str))
        & set(test_expression.index.astype(str))
    )

    return {
        "check": "Sample overlap",
        "status": "FAIL" if overlap else "PASS",
        "overlap_count": len(overlap),
        "overlapping_samples": overlap[:20],
    }


def check_duplicate_profiles(train_expression, test_expression):
    """
    Identify identical expression profiles across train and test splits.

    Profiles are compared using their values and shared feature columns.
    """

    shared_features = train_expression.columns.intersection(
        test_expression.columns
    )

    if len(shared_features) == 0:
        return {
            "check": "Duplicate profiles across splits",
            "status": "WARNING",
            "duplicate_profile_count": 0,
            "message": "No shared expression features available.",
        }

    train = train_expression.loc[:, shared_features]
    test = test_expression.loc[:, shared_features]

    train_hashes = pd.util.hash_pandas_object(
        train, index=False
    )

    test_hashes = pd.util.hash_pandas_object(
        test, index=False
    )

    train_hash_set = set(train_hashes)
    matching = test_hashes.isin(train_hash_set)

    return {
        "check": "Duplicate profiles across splits",
        "status": "WARNING" if matching.any() else "PASS",
        "duplicate_profile_count": int(matching.sum()),
        "message": (
            "Identical profiles found across splits."
            if matching.any()
            else "No identical profiles found across splits."
        ),
    }


def check_target_feature_association(
    train_expression,
    train_labels,
    correlation_threshold=0.95,
):
    """
    Flag features strongly correlated with numeric target labels.

    This is a screening signal, not proof of target leakage.
    """

    if not 0 < correlation_threshold <= 1:
        raise ValueError(
            "correlation_threshold must be greater than 0 and at most 1."
        )

    labels = pd.Series(train_labels, index=train_expression.index)

    numeric_labels = pd.to_numeric(labels, errors="coerce")

    if numeric_labels.isna().any():
        return {
            "check": "Target-feature association",
            "status": "WARNING",
            "flagged_feature_count": 0,
            "flagged_features": [],
            "message": (
                "Target labels are not fully numeric. "
                "Correlation screening was skipped."
            ),
        }

    if numeric_labels.nunique() < 2:
        return {
            "check": "Target-feature association",
            "status": "WARNING",
            "flagged_feature_count": 0,
            "flagged_features": [],
            "message": "Target labels contain fewer than two classes.",
        }

    correlations = train_expression.corrwith(numeric_labels).abs()
    correlations = correlations.replace(
        [np.inf, -np.inf], np.nan
    ).dropna()

    flagged = correlations[
        correlations >= correlation_threshold
    ].sort_values(ascending=False)

    return {
        "check": "Target-feature association",
        "status": "WARNING" if not flagged.empty else "PASS",
        "flagged_feature_count": int(len(flagged)),
        "flagged_features": [
            {
                "feature": str(feature),
                "absolute_correlation": float(value),
            }
            for feature, value in flagged.head(20).items()
        ],
        "message": (
            "Strong target associations require investigation."
            if not flagged.empty
            else "No features exceeded the configured threshold."
        ),
        "correlation_threshold": correlation_threshold,
    }


def run_leakage_audit(
    train_expression,
    test_expression,
    train_labels,
    correlation_threshold=0.95,
):
    """Run the available training/testing leakage screening checks."""

    if not train_expression.columns.equals(test_expression.columns):
        raise ValueError(
            "Training and testing matrices must have identical "
            "feature columns in the same order."
        )

    results = [
        check_sample_overlap(train_expression, test_expression),
        check_duplicate_profiles(train_expression, test_expression),
        check_target_feature_association(
            train_expression,
            train_labels,
            correlation_threshold,
        ),
    ]

    return results