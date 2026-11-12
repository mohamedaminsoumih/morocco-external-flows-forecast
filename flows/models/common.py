"""Shared by all models: forecast horizon and future dates."""

from collections.abc import Callable

import numpy as np
import pandas as pd

HORIZON = 12

# Every model: history in, HORIZON forecasts out
Model = Callable[[pd.Series], np.ndarray]


def future_index(history: pd.Series) -> pd.DatetimeIndex:
    """The HORIZON months right after the end of the history."""
    start = history.index[-1] + pd.offsets.MonthBegin(1)
    return pd.date_range(start, periods=HORIZON, freq="MS")
