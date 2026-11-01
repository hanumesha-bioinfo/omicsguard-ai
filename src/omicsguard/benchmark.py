from pathlib import Path
import json
import time

import pandas as pd

from omicsguard.integrity_checks import run_integrity_checks


def inject_missing_values(expression):
    """Create a copy containing one deliberately missing value."""
    if expression.empty:
        raise ValueError("Expression matrix is empty.")

    corrupted = expression.copy()
    corrupted.iloc[0, 0] = float("nan")
    return corrupted


def inject_duplicate_sample_id(expression):
    """Create a duplicate sample identifier."""
    if len(expression) < 2:
        raise ValueError("At least two samples are required.")

    corrupted = expression.copy()
    ids = corrupted.index.astype(str).tolist()
    ids[0] = ids[1]
    corrupted.index = pd.Index(ids, name=expression.index.name)
    return corrupted


def inject_duplicate_probe_id(expression):
    """Create a duplicate probe identifier."""
    if expression.shape[1] == 0:
        raise ValueError("At least one probe is required.")

    corrupted = expression.copy()
    duplicated_column = corrupted.iloc[:, [0]].copy()
    duplicated_column.columns = [corrupted.columns[0]]
    return pd.concat([corrupted, duplicated_column], axis=1)


def inject_constant_feature(expression):
    """Add a feature with the same value in every sample."""
    corrupted = expression.copy()
    corrupted["SYNTHETIC_CONSTANT_PROBE"] = 1.0
    return corrupted


def inject_metadata_mismatch(expression, metadata):
    """Remove one metadata record to create a sample mismatch."""
    if len(metadata) == 0:
        raise ValueError("Metadata is empty.")

    return expression.copy(), metadata.iloc[1:].copy()


def evaluate_check(check_results, expected_check):
    """Find whether the expected integrity check detects a defect."""
    for result in check_results:
        if result["check"] == expected_check:
            detected = result["status"] in ("FAIL", "WARNING")
            return detected, result

    raise ValueError(f"Check not found: {expected_check}")


def _calculate_metrics(rows, check_name):
    """Calculate defect-level binary metrics for one integrity check."""
    tp = fp = tn = fn = 0

    for row in rows:
        expected_positive = row["expected_check"] == check_name
        predicted_positive = check_name in row["detected_checks"]

        if expected_positive and predicted_positive:
            tp += 1
        elif not expected_positive and predicted_positive:
            fp += 1
        elif not expected_positive and not predicted_positive:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "check": check_name,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
    }


def run_fault_injection_benchmark(expression, metadata, output_dir):
    """
    Run independent controlled corruption experiments.

    Metrics are calculated at the integrity-check level across
    this small set of controlled experiments. They are not estimates
    of general performance on unseen datasets.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    experiments = [
        ("clean_baseline", "None", "None", expression.copy(), metadata.copy()),
        (
            "missing_values",
            "Missing values",
            "Missing values",
            inject_missing_values(expression),
            metadata.copy(),
        ),
        (
            "duplicate_sample_ids",
            "Duplicate sample IDs",
            "Duplicate sample IDs",
            inject_duplicate_sample_id(expression),
            metadata.copy(),
        ),
        (
            "duplicate_probe_ids",
            "Duplicate probe IDs",
            "Duplicate probe IDs",
            inject_duplicate_probe_id(expression),
            metadata.copy(),
        ),
        (
            "constant_features",
            "Constant features",
            "Constant features",
            inject_constant_feature(expression),
            metadata.copy(),
        ),
    ]

    corrupted_expression, corrupted_metadata = inject_metadata_mismatch(
        expression, metadata
    )
    experiments.append((
        "metadata_mismatch",
        "Expression-metadata mismatch",
        "Metadata consistency",
        corrupted_expression,
        corrupted_metadata,
    ))

    rows = []
    check_names = [
        "Missing values",
        "Duplicate sample IDs",
        "Duplicate probe IDs",
        "Constant features",
        "Metadata consistency",
    ]

    for name, defect, expected_check, exp, meta in experiments:
        start = time.perf_counter()
        results = run_integrity_checks(exp, meta)
        runtime = time.perf_counter() - start

        detected_checks = [
    result["check"]
    for result in results
    if result["status"] in ("FAIL", "WARNING")
]

        expected_detected = (
            expected_check in detected_checks
            if expected_check != "None"
            else False
        )

        unexpected_flags = [
            check for check in detected_checks
            if check != expected_check
        ]

        if expected_check == "None":
            result_label = (
                "UNEXPECTED_WARNING" if detected_checks else "PASS"
            )
        else:
            result_label = (
                "DETECTED" if expected_detected else "NOT DETECTED"
            )

        rows.append({
            "experiment": name,
            "injected_defect": defect,
            "expected_check": expected_check,
            "detected": expected_detected,
            "result": result_label,
            "runtime_seconds": round(runtime, 6),
            "detected_checks": detected_checks,
            "unexpected_flags": len(unexpected_flags),
            "unexpected_check_names": unexpected_flags,
        })

    report = pd.DataFrame(rows)

    defect_rows = report[report["injected_defect"] != "None"]
    clean_row = report[report["experiment"] == "clean_baseline"].iloc[0]

    detected_count = int(defect_rows["detected"].sum())
    total_defects = len(defect_rows)

    per_check_metrics = [
        _calculate_metrics(rows, check_name)
        for check_name in check_names
    ]

    summary = {
        "total_experiments": len(report),
        "injected_defect_experiments": total_defects,
        "detected_defects": detected_count,
        "missed_defects": total_defects - detected_count,
        "detection_rate": round(
            detected_count / total_defects, 4
        ) if total_defects else 0.0,
        "clean_baseline_passed": (
            clean_row["result"] == "PASS"
        ),
        "clean_baseline_unexpected_flags": int(
            clean_row["unexpected_flags"]
        ),
        "total_unexpected_flags": int(
            report["unexpected_flags"].sum()
        ),
        "mean_runtime_seconds": round(
            float(report["runtime_seconds"].mean()), 6
        ),
        "per_check_metrics": per_check_metrics,
        "note": (
            "Metrics describe only these controlled experiments. "
            "There is one injected example per defect type and one "
            "clean baseline. They are not statistically generalizable "
            "estimates of performance on unseen datasets."
        ),
    }

    report.to_csv(
        output_dir / "fault_injection_results.csv",
        index=False,
    )

    metrics_df = pd.DataFrame(per_check_metrics)
    metrics_df.to_csv(
        output_dir / "fault_injection_metrics.csv",
        index=False,
    )

    with open(
        output_dir / "fault_injection_summary.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(summary, file, indent=4)

    return report, summary
