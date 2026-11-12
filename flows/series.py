"""Load the clean monthly series produced by prepare_data."""

import pandas as pd

from flows.config import PROCESSED_DIR


def load_series(name: str) -> pd.Series:
    """Monthly series indexed by month start (freq MS), in MDH."""
    table = pd.read_csv(PROCESSED_DIR / f"{name}.csv", parse_dates=["date"])
    series = table.set_index("date")["value_mdh"].asfreq("MS")
    series.name = name
    return series
