"""Market-data provider implementations."""

from collections.abc import Mapping, Sequence


class InMemoryMarketDataProvider:
    """Deterministic provider useful for tests, examples, and batch input."""

    def __init__(
        self,
        prices: Mapping[str, float],
        returns: Mapping[str, Sequence[float]],
    ) -> None:
        self._prices = dict(prices)
        self._returns = {symbol: tuple(values) for symbol, values in returns.items()}

    def current_price(self, symbol: str) -> float:
        try:
            price = self._prices[symbol]
        except KeyError as exc:
            raise KeyError(f"no current price for {symbol}") from exc
        if price < 0:
            raise ValueError(f"current price for {symbol} must be non-negative")
        return float(price)

    def historical_returns(self, symbol: str) -> tuple[float, ...]:
        try:
            values = self._returns[symbol]
        except KeyError as exc:
            raise KeyError(f"no historical returns for {symbol}") from exc
        return values

