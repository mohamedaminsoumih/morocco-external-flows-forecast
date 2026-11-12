"""Machine learning model: gradient boosting on year-on-year growth."""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

from flows.calendar_features import calendar_features, covid_flag
from flows.models.common import HORIZON, future_index

FEATURES = ["month", "eid_al_fitr", "eid_al_adha"]


def _training_data(history: pd.Series) -> pd.DataFrame:
    """Calendar features + target, without COVID-affected months."""
    index = pd.DatetimeIndex(history.index)
    data = calendar_features(index)
    data["growth"] = np.log(history / history.shift(12))

    # A COVID month, or a month compared with a COVID month, isn't normal
    covid = covid_flag(index)
    abnormal = (covid == 1) | (covid.shift(12) == 1)
    return data[~abnormal].dropna()


def gradient_boosting(history: pd.Series) -> np.ndarray:
    """Learns the growth vs the same month last year, from calendar effects.

    Trees can't extrapolate a trend, but they can learn a growth rate,
    which is then applied to last year's value.
    """
    train = _training_data(history)
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=2,
        min_samples_leaf=8,
        random_state=0,
    ).fit(train[FEATURES], train["growth"])

    future = calendar_features(future_index(history))
    growth = model.predict(future[FEATURES])
    return history.iloc[-HORIZON:].to_numpy() * np.exp(growth)
