"""NumPy and pandas based portfolio analytics."""

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd


class PortfolioAnalytics:
    """Analyse aligned asset-return observations held in a DataFrame."""

    def __init__(
        self,
        returns: pd.DataFrame | Mapping[str, Sequence[float]],
        trading_days_per_year: int = 252,
    ) -> None:
        frame = pd.DataFrame(returns, dtype=float)
        if frame.empty or frame.shape[1] == 0:
            raise ValueError("returns must contain at least one asset and observation")
        if frame.columns.has_duplicates:
            raise ValueError("asset names must be unique")
        values = frame.to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError("returns must contain only finite values")
        if trading_days_per_year <= 0:
            raise ValueError("trading_days_per_year must be positive")
        self._returns = frame.copy()
        self._trading_days = trading_days_per_year

    @property
    def returns(self) -> pd.DataFrame:
        """Return a defensive copy of the asset return table."""
        return self._returns.copy()

    def covariance(self, annualized: bool = False) -> pd.DataFrame:
        """Return the sample covariance matrix."""
        result = self._returns.cov()
        return result * self._trading_days if annualized else result

    def correlation(self) -> pd.DataFrame:
        """Return the Pearson correlation matrix."""
        return self._returns.corr()

    def portfolio_returns(self, weights: Mapping[str, float] | Sequence[float]) -> pd.Series:
        """Calculate portfolio returns from asset weights."""
        if isinstance(weights, Mapping):
            missing = set(self._returns.columns) - set(weights)
            extra = set(weights) - set(self._returns.columns)
            if missing or extra:
                raise ValueError(f"weights must match assets; missing={missing}, extra={extra}")
            vector = np.array([weights[name] for name in self._returns.columns], dtype=float)
        else:
            vector = np.asarray(weights, dtype=float)
        if vector.ndim != 1 or len(vector) != self._returns.shape[1]:
            raise ValueError("one weight is required for each asset")
        if not np.isfinite(vector).all():
            raise ValueError("weights must be finite")
        return pd.Series(
            self._returns.to_numpy() @ vector,
            index=self._returns.index,
            name="portfolio_return",
        )

    def annualized_volatility(self, weights: Mapping[str, float] | Sequence[float]) -> float:
        """Return annualized sample volatility of portfolio returns."""
        daily = self.portfolio_returns(weights)
        return float(daily.std(ddof=1) * np.sqrt(self._trading_days))

    def cumulative_returns(self, weights: Mapping[str, float] | Sequence[float]) -> pd.Series:
        """Compound portfolio simple returns into a cumulative return series."""
        return (1.0 + self.portfolio_returns(weights)).cumprod() - 1.0

    def drawdown(self, weights: Mapping[str, float] | Sequence[float]) -> pd.Series:
        """Return the portfolio drawdown series from its running peak."""
        wealth = 1.0 + self.cumulative_returns(weights)
        running_peak = wealth.cummax().clip(lower=1.0)
        return wealth / running_peak - 1.0

    def maximum_drawdown(self, weights: Mapping[str, float] | Sequence[float]) -> float:
        """Return maximum drawdown as a non-negative magnitude."""
        return float(-self.drawdown(weights).min())

    def sharpe_ratio(
        self,
        weights: Mapping[str, float] | Sequence[float],
        annual_risk_free_rate: float = 0.0,
    ) -> float:
        """Return the annualized Sharpe ratio using daily simple returns."""
        daily = self.portfolio_returns(weights)
        excess = daily - annual_risk_free_rate / self._trading_days
        volatility = float(excess.std(ddof=1))
        if volatility == 0:
            return 0.0
        return float(excess.mean() / volatility * np.sqrt(self._trading_days))

    def historical_var(
        self,
        weights: Mapping[str, float] | Sequence[float],
        confidence_level: float = 0.95,
        portfolio_value: float = 1.0,
    ) -> float:
        """Return historical VaR as a non-negative currency or proportion loss."""
        self._validate_risk_inputs(confidence_level, portfolio_value)
        quantile = np.quantile(self.portfolio_returns(weights), 1 - confidence_level)
        return max(0.0, float(-quantile * portfolio_value))

    def historical_expected_shortfall(
        self,
        weights: Mapping[str, float] | Sequence[float],
        confidence_level: float = 0.95,
        portfolio_value: float = 1.0,
    ) -> float:
        """Return mean loss at or below the historical VaR return threshold."""
        self._validate_risk_inputs(confidence_level, portfolio_value)
        returns = self.portfolio_returns(weights).to_numpy()
        threshold = np.quantile(returns, 1 - confidence_level)
        return max(0.0, float(-returns[returns <= threshold].mean() * portfolio_value))

    @staticmethod
    def _validate_risk_inputs(confidence_level: float, portfolio_value: float) -> None:
        if not 0 < confidence_level < 1:
            raise ValueError("confidence_level must be between 0 and 1")
        if not np.isfinite(portfolio_value) or portfolio_value < 0:
            raise ValueError("portfolio_value must be finite and non-negative")
