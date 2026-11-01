import gzip

import pandas as pd
import pytest

from omicsguard.ingestion import (
    read_geo_metadata,
    load_geo_dataset,
)


def create_test_geo_file(path):
    lines = [
        '!Sample_geo_accession\tGSM1\tGSM2\n',
        '!Sample_title\tSample one\tSample two\n',
        '!Sample_characteristics_ch1\t tissue: tumor\t tissue: normal\n',
        '!series_matrix_table_begin\n',
    ]

    # The loader currently expects the expression header at line 86.
    while len(lines) < 85:
        lines.append("!test_padding\tvalue\n")

    lines.extend([
        "ID_REF\tGSM1\tGSM2\n",
        "P1\t1.5\t2.5\n",
        "P2\t3.5\t4.5\n",
        "!series_matrix_table_end\n",
    ])

    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.writelines(lines)


def test_read_geo_metadata(tmp_path):
    path = tmp_path / "test_series_matrix.txt.gz"
    create_test_geo_file(path)

    metadata = read_geo_metadata(path)

    assert list(metadata["sample_id"]) == ["GSM1", "GSM2"]
    assert "title" in metadata.columns
    assert "characteristic_tissue" in metadata.columns


def test_load_geo_dataset(tmp_path):
    path = tmp_path / "test_series_matrix.txt.gz"
    create_test_geo_file(path)

    expression, metadata = load_geo_dataset(path)

    assert expression.shape == (2, 2)
    assert list(expression.index) == ["GSM1", "GSM2"]
    assert list(expression.columns) == ["P1", "P2"]
    assert expression.loc["GSM1", "P1"] == 1.5
    assert len(metadata) == 2


def test_missing_file_raises_error(tmp_path):
    missing = tmp_path / "does_not_exist.txt.gz"

    with pytest.raises(FileNotFoundError):
        load_geo_dataset(missing)


def test_invalid_matrix_header_raises_error(tmp_path):
    path = tmp_path / "invalid.txt.gz"

    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.writelines(["!padding\n"] * 85)
        handle.write("WRONG_COLUMN\tGSM1\n")
        handle.write("P1\t1.0\n")

    with pytest.raises(ValueError, match="ID_REF"):
        load_geo_dataset(path)
