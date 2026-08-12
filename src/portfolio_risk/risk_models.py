"""Historical-simulation VaR and Expected Shortfall models."""

import math
from collections.abc import Sequence


def _validate(scenario_pnl: Sequence[float], confidence_level: float) -> list[float]:
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")
    if not scenario_pnl:
        raise ValueError("at least one P&L scenario is required")
    losses = [-float(value) for value in scenario_pnl]
    if not all(math.isfinite(loss) for loss in losses):
        raise ValueError("P&L scenarios must be finite")
    return sorted(losses)


class HistoricalVaR:
    """Historical VaR using a linearly interpolated empirical quantile."""

    def calculate(self, scenario_pnl: Sequence[float], confidence_level: float) -> float:
        losses = _validate(scenario_pnl, confidence_level)
        position = (len(losses) - 1) * confidence_level
        lower = math.floor(position)
        upper = math.ceil(position)
        if lower == upper:
            quantile = losses[lower]
        else:
            weight = position - lower
            quantile = losses[lower] * (1 - weight) + losses[upper] * weight
        return max(0.0, quantile)


class HistoricalExpectedShortfall:
    """Mean loss in the worst (1-confidence) fraction of observations.

    Fractional weighting at the tail boundary makes the estimate meaningful
    even when the requested tail contains fewer than one whole observation.
    """

    def calculate(self, scenario_pnl: Sequence[float], confidence_level: float) -> float:
        losses = _validate(scenario_pnl, confidence_level)
        descending = list(reversed(losses))
        tail_size = len(descending) * (1 - confidence_level)
        whole = math.floor(tail_size)
        fraction = tail_size - whole
        total = sum(descending[:whole])
        if fraction:
            total += descending[whole] * fraction
        expected_shortfall = total / tail_size
        return max(0.0, expected_shortfall)

