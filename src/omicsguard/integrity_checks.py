
def check_missing_values(expression):
    """Check for missing values in the expression matrix."""
    total_missing = int(expression.isna().sum().sum())

    return {
        "check": "Missing values",
        "status": "WARNING" if total_missing > 0 else "PASS",
        "total_missing": total_missing,
    }


def check_duplicate_sample_ids(expression):
    """Check for duplicate sample IDs."""
    duplicate_count = int(expression.index.duplicated().sum())

    return {
        "check": "Duplicate sample IDs",
        "status": "FAIL" if duplicate_count > 0 else "PASS",
        "duplicate_count": duplicate_count,
    }


def check_duplicate_probe_ids(expression):
    """Check for duplicate probe IDs."""
    duplicate_count = int(expression.columns.duplicated().sum())

    return {
        "check": "Duplicate probe IDs",
        "status": "FAIL" if duplicate_count > 0 else "PASS",
        "duplicate_count": duplicate_count,
    }


def check_constant_features(expression):
    """Identify features with constant values."""
    constant_features = expression.columns[
        expression.nunique(dropna=False) <= 1
    ].tolist()

    return {
        "check": "Constant features",
        "status": "WARNING" if constant_features else "PASS",
        "constant_probe_count": len(constant_features),
        "constant_probes": constant_features,
    }


def check_metadata_consistency(expression, metadata):
    """Check sample alignment between expression and metadata."""

    if "sample_id" not in metadata.columns:
        return {
            "check": "Metadata consistency",
            "status": "FAIL",
            "message": "Metadata does not contain sample_id.",
        }

    # Avoid cascading metadata warnings when expression IDs are duplicated.
    if expression.index.duplicated().any():
        return {
            "check": "Metadata consistency",
            "status": "SKIPPED",
            "message": (
                "Metadata alignment was not evaluated because "
                "duplicate expression sample IDs were detected."
            ),
        }

    expression_ids = set(expression.index.astype(str))
    metadata_ids = set(metadata["sample_id"].astype(str))

    missing_metadata = sorted(expression_ids - metadata_ids)
    extra_metadata = sorted(metadata_ids - expression_ids)

    duplicate_metadata_ids = int(
        metadata["sample_id"].duplicated().sum()
    )

    passed = (
        len(missing_metadata) == 0
        and len(extra_metadata) == 0
        and duplicate_metadata_ids == 0
    )

    return {
        "check": "Metadata consistency",
        "status": "PASS" if passed else "FAIL",
        "missing_metadata_samples": missing_metadata,
        "extra_metadata_samples": extra_metadata,
        "duplicate_metadata_ids": duplicate_metadata_ids,
    }


def run_integrity_checks(expression, metadata):
    """Run all five dataset integrity checks."""

    results = [
        check_missing_values(expression),
        check_duplicate_sample_ids(expression),
        check_duplicate_probe_ids(expression),
        check_constant_features(expression),
        check_metadata_consistency(expression, metadata),
    ]

    return results
