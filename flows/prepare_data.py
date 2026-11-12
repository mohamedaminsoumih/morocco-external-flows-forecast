"""Turn the Office des Changes Excel files into clean CSV files.

Usage:
    python -m flows.prepare_data
"""

from pathlib import Path

from flows.config import PROCESSED_DIR, RAW_DIR, SERIES
from flows.oc_excel import read_monthly_table
from flows.validate import validate


def find_raw_file(pattern: str) -> Path:
    """The single raw file matching the pattern (e.g. Evol_MRE_*)."""
    matches = sorted(RAW_DIR.glob(pattern))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected 1 file matching {pattern} in {RAW_DIR}, " f"found {len(matches)}"
        )
    return matches[0]


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    for name, pattern in SERIES.items():
        table = read_monthly_table(find_raw_file(pattern))
        validate(table)

        output = PROCESSED_DIR / f"{name}.csv"
        # Round to 0.1 MDH: removes float noise like 5106.900000000015
        clean = table[["date", "value_mdh"]].round({"value_mdh": 1})
        clean.to_csv(output, index=False)

        first, last = table["date"].min(), table["date"].max()
        print(
            f"{name}: {len(table)} months "
            f"({first:%Y-%m} to {last:%Y-%m}) → {output.name}"
        )


if __name__ == "__main__":
    main()
