"""Compare the models on past data they never saw (rolling-origin backtest).

For each forecast origin (one per month from mid-2023 to mid-2025), each
model is trained on data up to that month, forecasts the next 12 months,
and is scored against what really happened.

Usage:
    python -m flows.backtest
"""

import numpy as np
import pandas as pd

from flows.config import REPORTS_DIR, SERIES
from flows.models import HORIZON, MODELS
from flows.series import load_series

FIRST_ORIGIN = "2023-06-01"


def percentage_error(actual: np.ndarray, forecast: np.ndarray) -> np.ndarray:
    return np.abs(forecast - actual) / actual * 100


def backtest_series(series: pd.Series) -> pd.DataFrame:
    """One row per model, origin and horizon, with the error in %."""
    last_origin = series.index[-1] - pd.DateOffset(months=HORIZON)
    origins = pd.date_range(FIRST_ORIGIN, last_origin, freq="MS")

    rows = []
    for origin in origins:
        history = series[:origin]
        actual = series[origin:].iloc[1 : HORIZON + 1].to_numpy()

        for model_name, model in MODELS.items():
            forecast = model(history)
            monthly = percentage_error(actual, forecast)
            yearly = percentage_error(
                np.array([actual.sum()]), np.array([forecast.sum()])
            )[0]
            for horizon, error in enumerate(monthly, start=1):
                rows.append((model_name, origin, horizon, error, yearly))

    return pd.DataFrame(
        rows,
        columns=["model", "origin", "horizon", "error_pct", "yearly_error_pct"],
    )


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    """Mean error per model: monthly, and on the 12-month total."""
    per_origin = results.drop_duplicates(["model", "origin"])
    return (
        pd.DataFrame(
            {
                "monthly_mape": results.groupby("model")["error_pct"].mean(),
                "yearly_mape": per_origin.groupby("model")["yearly_error_pct"].mean(),
            }
        )
        .round(1)
        .sort_values("yearly_mape")
    )


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    for name in SERIES:
        results = backtest_series(load_series(name))
        results.to_csv(REPORTS_DIR / f"backtest_{name}.csv", index=False)

        summary = summarize(results)
        summary.to_csv(REPORTS_DIR / f"backtest_summary_{name}.csv")
        print(f"\n{name}  (error in %, lower is better)")
        print(summary.to_string())


if __name__ == "__main__":
    main()
