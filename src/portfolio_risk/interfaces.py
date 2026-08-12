"""Substitution points for market data and risk models."""

from collections.abc import Sequence
from typing import Protocol


class MarketDataProvider(Protocol):
    """Supplies current prices and aligned historical simple returns."""

    def current_price(self, symbol: str) -> float: ...

    def historical_returns(self, symbol: str) -> Sequence[float]: ...


class VaRModel(Protocol):
    def calculate(self, scenario_pnl: Sequence[float], confidence_level: float) -> float: ...


class ExpectedShortfallModel(Protocol):
    def calculate(self, scenario_pnl: Sequence[float], confidence_level: float) -> float: ...

