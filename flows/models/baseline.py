"""Baseline model: the simplest forecast every model must beat."""

import numpy as np
import pandas as pd

from flows.models.common import HORIZON


def seasonal_naive(history: pd.Series) -> np.ndarray:
    """Each month = the same month last year."""
    return history.iloc[-HORIZON:].to_numpy()
