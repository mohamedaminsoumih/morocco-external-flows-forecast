"""Classic time-series models: Holt-Winters and SARIMA."""

import warnings
from typing import cast

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX, SARIMAXResults

from flows.calendar_features import calendar_features
from flows.models.common import HORIZON, future_index

EXOG_COLUMNS = ["eid_al_fitr", "eid_al_adha", "covid"]


def holt_winters(history: pd.Series) -> np.ndarray:
    """Exponential smoothing: damped trend x monthly seasonal pattern.

    Trained from 2012: older years have a different seasonal pattern.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fitted = ExponentialSmoothing(
            history["2012":],
            trend="add",
            damped_trend=True,
            seasonal="mul",
            seasonal_periods=12,
        ).fit()
    return fitted.forecast(HORIZON).to_numpy()


def sarima(history: pd.Series) -> np.ndarray:
    """Seasonal ARIMA on log values, with Eid and COVID as extra inputs."""
    index = pd.DatetimeIndex(history.index)
    exog = calendar_features(index)[EXOG_COLUMNS]
    exog_future = calendar_features(future_index(history))[EXOG_COLUMNS]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = SARIMAX(
            np.log(history),
            exog=exog,
            order=(1, 0, 0),
            seasonal_order=(0, 1, 1, 12),
            trend="c",
        )
        fitted = cast(SARIMAXResults, model.fit(disp=False))
    return np.exp(fitted.forecast(HORIZON, exog=exog_future)).to_numpy()
