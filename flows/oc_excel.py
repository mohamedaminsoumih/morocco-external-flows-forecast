"""Read Office des Changes monthly Excel files (years x months tables)."""

from pathlib import Path

import pandas as pd

MONTHS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]
TOTAL_LABEL = "Total Année"


def _find_header_row(raw: pd.DataFrame) -> int:
    """Position of the row that contains the month names."""
    for position in range(len(raw)):
        if "Janvier" in raw.iloc[position].tolist():
            return position
    raise ValueError("No header row with month names found")


def _fill_missing_years(years: list) -> list[int]:
    """Rows go from newest to oldest; a missing year = year below + 1.

    Needed because the latest year is sometimes left blank in the file.
    """
    filled = list(years)
    for i in range(len(filled) - 2, -1, -1):
        if pd.isna(filled[i]):
            filled[i] = filled[i + 1] + 1
    return [int(year) for year in filled]


def read_monthly_table(path: Path) -> pd.DataFrame:
    """Return a long table: one row per month, with the yearly total."""
    raw = pd.read_excel(path, header=None)
    header_row = _find_header_row(raw)
    header = raw.iloc[header_row].tolist()

    month_cols = {month: header.index(month) for month in MONTHS}
    total_col = header.index(TOTAL_LABEL)
    year_col = month_cols["Janvier"] - 1

    body = raw.iloc[header_row + 1 :].dropna(how="all")
    years = _fill_missing_years(body.iloc[:, year_col].tolist())

    records = []
    for year, row in zip(years, body.itertuples(index=False)):
        for month_number, month in enumerate(MONTHS, start=1):
            records.append(
                {
                    "date": pd.Timestamp(year=year, month=month_number, day=1),
                    "value_mdh": row[month_cols[month]],
                    "year_total_mdh": row[total_col],
                }
            )

    # Months not published yet are empty in the file: drop them
    table = pd.DataFrame(records).dropna(subset=["value_mdh"])
    return table.sort_values("date").reset_index(drop=True)
