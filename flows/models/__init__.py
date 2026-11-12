"""All forecasting models, by name."""

from flows.models.baseline import seasonal_naive
from flows.models.common import HORIZON, Model, future_index
from flows.models.machine_learning import gradient_boosting
from flows.models.statistical import holt_winters, sarima

MODELS: dict[str, Model] = {
    "seasonal_naive": seasonal_naive,
    "holt_winters": holt_winters,
    "sarima": sarima,
    "gradient_boosting": gradient_boosting,
}

__all__ = ["HORIZON", "MODELS", "Model", "future_index"]
