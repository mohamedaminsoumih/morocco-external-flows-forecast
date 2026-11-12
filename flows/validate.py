"""Data quality checks on a monthly series."""

import pandas as pd

# Values are rounded in the file, so allow a small gap (in MDH)
TOTAL_TOLERANCE_MDH = 1.0


def check_yearly_totals(table: pd.DataFrame) -> None:
    """Months of each complete year must add up to the yearly total."""
    by_year = table.groupby(table["date"].dt.year).agg(
        months=("value_mdh", "size"),
        month_sum=("value_mdh", "sum"),
        year_total=("year_total_mdh", "first"),
    )
    complete = by_year[by_year["months"] == 12]
    gap = (complete["month_sum"] - complete["year_total"]).abs()
    wrong = complete[gap > TOTAL_TOLERANCE_MDH]
    if not wrong.empty:
        raise ValueError(f"Monthly values don't match totals:\n{wrong}")


def check_no_gaps(table: pd.DataFrame) -> None:
    """Every month between the first and last date must be present."""
    expected = pd.date_range(table["date"].min(), table["date"].max(), freq="MS")
    missing = expected.difference(pd.DatetimeIndex(table["date"]))
    if len(missing) > 0:
        raise ValueError(f"Missing months: {list(missing)}")


def check_positive(table: pd.DataFrame) -> None:
    """Receipts can't be zero or negative."""
    bad = table[table["value_mdh"] <= 0]
    if not bad.empty:
        raise ValueError(f"Non-positive values:\n{bad}")


def validate(table: pd.DataFrame) -> None:
    check_yearly_totals(table)
    check_no_gaps(table)
    check_positive(table)
