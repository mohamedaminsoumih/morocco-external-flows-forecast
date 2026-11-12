"""Forecast the next 12 months with the best model of each series.

The best model is the one with the lowest error on 12-month totals in the
backtest. The uncertainty band comes from that model's past errors at
each horizon: "in 80% of past cases, the error was below X%".

Usage:
    python -m flows.backtest   (run first)
    python -m flows.forecast
"""

import pandas as pd

from flows.config import REPORTS_DIR, SERIES
from flows.models import MODELS, future_index
from flows.plots import plot_backtest, plot_forecast
from flows.series import load_series

BAND_QUANTILE = 0.8


def best_model(name: str) -> str:
    summary = pd.read_csv(REPORTS_DIR / f"backtest_summary_{name}.csv")
    return str(summary.sort_values("yearly_mape")["model"].iloc[0])


def error_band(name: str, model_name: str) -> pd.Series:
    """80th percentile of past errors (in %) for each horizon 1..12."""
    results = pd.read_csv(REPORTS_DIR / f"backtest_{name}.csv")
    errors = results[results["model"] == model_name]
    return errors.groupby("horizon")["error_pct"].quantile(BAND_QUANTILE)


def forecast_series(name: str) -> pd.DataFrame:
    history = load_series(name)
    model_name = best_model(name)
    values = MODELS[model_name](history)
    band = error_band(name, model_name).to_numpy() / 100

    return pd.DataFrame(
        {
            "date": future_index(history),
            "forecast_mdh": values.round(0),
            "low_mdh": (values * (1 - band)).round(0),
            "high_mdh": (values * (1 + band)).round(0),
            "model": model_name,
        }
    )


def main() -> None:
    figures = REPORTS_DIR / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    for name in SERIES:
        forecast = forecast_series(name)
        forecast.to_csv(REPORTS_DIR / f"forecast_{name}.csv", index=False)

        history = load_series(name)
        plot_forecast(history, forecast, figures / f"forecast_{name}.png")
        summary = pd.read_csv(REPORTS_DIR / f"backtest_summary_{name}.csv")
        plot_backtest(name, summary, figures / f"backtest_{name}.png")

        first, last = forecast["date"].iloc[0], forecast["date"].iloc[-1]
        total = forecast["forecast_mdh"].sum() / 1000
        print(
            f"{name}: {forecast['model'].iloc[0]} → "
            f"{total:.1f} billion MAD from {first:%Y-%m} to {last:%Y-%m}"
        )


if __name__ == "__main__":
    main()
