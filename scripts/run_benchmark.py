from pathlib import Path

from omicsguard.ingestion import load_geo_dataset
from omicsguard.benchmark import run_fault_injection_benchmark


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data/raw/GSE10072_series_matrix.txt.gz"
OUTPUT_DIR = PROJECT_ROOT / "results/benchmark"


def main():
    print("Loading GSE10072 dataset...")

    expression, metadata = load_geo_dataset(DATA_FILE)

    print("Expression shape:", expression.shape)
    print("Metadata shape:", metadata.shape)

    print("\nRunning fault-injection benchmark...")

    report, summary = run_fault_injection_benchmark(
        expression,
        metadata,
        OUTPUT_DIR,
    )

    print("\nBENCHMARK SUMMARY")
    for key, value in summary.items():
        if key != "per_check_metrics":
            print(f"{key}: {value}")

    print("\nPER-CHECK METRICS")
    for metric in summary["per_check_metrics"]:
        print(metric)

    print("\nEXPERIMENT RESULTS")
    print(report.to_string(index=False))

    print("\nBenchmark completed successfully.")


if __name__ == "__main__":
    main()