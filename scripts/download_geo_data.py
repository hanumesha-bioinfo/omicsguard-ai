from pathlib import Path
from urllib.request import urlretrieve

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

FILENAME = "GSE10072_series_matrix.txt.gz"
URL = (
    "https://ftp.ncbi.nlm.nih.gov/geo/series/"
    "GSE10nnn/GSE10072/matrix/"
    "GSE10072_series_matrix.txt.gz"
)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination = DATA_DIR / FILENAME

    if destination.exists():
        print(f"Dataset already exists: {destination}")
        return

    print("Downloading GSE10072 from NCBI GEO...")
    urlretrieve(URL, destination)

    print(f"Download complete: {destination}")
    print(f"File size: {destination.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
