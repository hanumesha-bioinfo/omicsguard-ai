from pathlib import Path
import csv
import gzip

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = PROJECT_ROOT / "data/raw/GSE10072_series_matrix.txt.gz"
PROCESSED_DIR = PROJECT_ROOT / "data/processed"

EXPRESSION_OUTPUT = PROCESSED_DIR / "GSE10072_expression.csv"
METADATA_OUTPUT = PROCESSED_DIR / "GSE10072_metadata.csv"


def read_geo_metadata(file_path):
    """Extract sample-level metadata from a GEO Series Matrix file."""

    metadata_rows = {}

    with gzip.open(file_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("!series_matrix_table_begin"):
                break

            if not line.startswith("!Sample_"):
                continue

            fields = next(csv.reader([line], delimiter="\t"))
            key = fields[0].replace("!Sample_", "")
            values = [value.strip() for value in fields[1:]]

            metadata_rows.setdefault(key, []).append(values)

    sample_ids = metadata_rows["geo_accession"][0]

    metadata = pd.DataFrame(index=sample_ids)
    metadata.index.name = "sample_id"

    for key, rows in metadata_rows.items():
        if key == "geo_accession":
            continue

        if key == "characteristics_ch1":
            for row in rows:
                for i, value in enumerate(row):
                    if ":" in value:
                        characteristic, content = value.split(":", 1)
                        column = f"characteristic_{characteristic.strip()}"

                        if column not in metadata.columns:
                            metadata[column] = None

                        metadata.iloc[
                            i, metadata.columns.get_loc(column)
                        ] = content.strip()

        elif len(rows) == 1:
            metadata[key] = rows[0]

    return metadata.reset_index()


def load_geo_dataset(file_path):
    """Load GEO expression data and return sample-by-probe matrix."""

    if not file_path.exists():
        raise FileNotFoundError(f"GEO file not found: {file_path}")

    expression = pd.read_csv(
        file_path,
        sep="\t",
        compression="gzip",
        skiprows=85,
        comment="!",
    )

    if "ID_REF" not in expression.columns:
        raise ValueError("Expected ID_REF probe identifier column.")

    expression = expression.set_index("ID_REF")
    expression = expression.apply(pd.to_numeric, errors="coerce")
    expression = expression.T

    expression.index.name = "sample_id"
    expression.columns.name = "probe_id"

    metadata = read_geo_metadata(file_path)

    if set(expression.index) != set(metadata["sample_id"]):
        raise ValueError(
            "Sample IDs in expression matrix and metadata do not match."
        )

    return expression, metadata


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    expression, metadata = load_geo_dataset(RAW_FILE)

    expression.to_csv(EXPRESSION_OUTPUT)
    metadata.to_csv(METADATA_OUTPUT, index=False)

    print("\nOMICSGuard AI - DATA INGESTION")
    print("-" * 40)

    print("Expression matrix shape:", expression.shape)
    print("Metadata shape:", metadata.shape)
    print("Expression missing values:", expression.isna().sum().sum())
    print("Duplicate sample IDs:", expression.index.duplicated().sum())
    print("Duplicate probe IDs:", expression.columns.duplicated().sum())

    print("\nSaved files:")
    print(EXPRESSION_OUTPUT)
    print(METADATA_OUTPUT)


if __name__ == "__main__":
    main()
