"""Charts saved as PNG files for the README and the presentation."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save files only, no window

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

TITLES = {
    "mre_remittances": "MRE remittances (million MAD per month)",
    "travel_receipts": "Travel receipts (million MAD per month)",
}
HISTORY_START = "2019-01-01"


def plot_forecast(history: pd.Series, forecast: pd.DataFrame, path: Path) -> None:
    """Recent history, the forecast, and its uncertainty band."""
    recent = history[HISTORY_START:]
    fig, ax = plt.subplots(figsize=(11, 4.5))

    ax.plot(recent.index, recent.to_numpy(), color="#1f4e79", label="Actual")
    ax.plot(
        forecast["date"].to_numpy(),
        forecast["forecast_mdh"].to_numpy(),
        color="#c0504d",
        label=f"Forecast ({forecast['model'].iloc[0]})",
    )
    ax.fill_between(
        forecast["date"].to_numpy(),
        forecast["low_mdh"].to_numpy(),
        forecast["high_mdh"].to_numpy(),
        color="#c0504d",
        alpha=0.2,
        label="80% band from past errors",
    )

    ax.set_title(TITLES.get(str(history.name), str(history.name)))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)


def plot_backtest(name: str, summary: pd.DataFrame, path: Path) -> None:
    """Error on 12-month totals per model (lower is better)."""
    ordered = summary.sort_values("yearly_mape", ascending=False)
    fig, ax = plt.subplots(figsize=(7, 3.5))

    ax.barh(
        ordered["model"].to_numpy(),
        ordered["yearly_mape"].to_numpy(),
        color="#1f4e79",
    )
    for y, value in enumerate(ordered["yearly_mape"]):
        ax.text(value + 0.2, y, f"{value:.1f}%", va="center")

    ax.set_xlabel("Average error on the 12-month total (%)")
    ax.set_title(f"Backtest: {TITLES.get(name, name).split(' (')[0]}")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(str(path), dpi=150)
    plt.close(fig)
