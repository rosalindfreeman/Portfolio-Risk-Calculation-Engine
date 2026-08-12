"""Portfolio valuation and risk orchestration."""

import math
import statistics

from .analytics import PortfolioAnalytics
from .interfaces import ExpectedShortfallModel, MarketDataProvider, VaRModel
from .models import Portfolio, RiskReport, TradeBookItem


class PortfolioEngine:
    def __init__(
        self,
        market_data: MarketDataProvider,
        var_model: VaRModel,
        es_model: ExpectedShortfallModel,
        trading_days_per_year: int = 252,
    ) -> None:
        if trading_days_per_year <= 0:
            raise ValueError("trading_days_per_year must be positive")
        self._market_data = market_data
        self._var_model = var_model
        self._es_model = es_model
        self._trading_days = trading_days_per_year

    def scenario_pnl(self, portfolio: Portfolio) -> tuple[float, ...]:
        series = [self._market_data.historical_returns(h.symbol) for h in portfolio.holdings]
        lengths = {len(values) for values in series}
        if len(lengths) != 1:
            raise ValueError("historical return series must be aligned and have equal length")
        scenario_count = lengths.pop()
        if scenario_count == 0:
            raise ValueError("historical return series must not be empty")

        exposures = [
            holding.quantity * self._market_data.current_price(holding.symbol)
            for holding in portfolio.holdings
        ]
        return tuple(
            sum(exposure * returns[index] for exposure, returns in zip(exposures, series))
            for index in range(scenario_count)
        )

    def generate_report(self, portfolio: Portfolio, confidence_level: float = 0.95) -> RiskReport:
        prices = {
            holding.symbol: self._market_data.current_price(holding.symbol)
            for holding in portfolio.holdings
        }
        market_value = sum(h.quantity * prices[h.symbol] for h in portfolio.holdings)
        pnl = sum(
            h.quantity * (prices[h.symbol] - h.average_cost) for h in portfolio.holdings
        )
        trade_book_items = tuple(
            TradeBookItem(
                symbol=holding.symbol,
                quantity=holding.quantity,
                average_cost=holding.average_cost,
                current_price=prices[holding.symbol],
                market_value=holding.quantity * prices[holding.symbol],
                unrealized_pnl=holding.quantity
                * (prices[holding.symbol] - holding.average_cost),
            )
            for holding in portfolio.holdings
        )
        scenarios = self.scenario_pnl(portfolio)
        daily_volatility = statistics.stdev(scenarios) if len(scenarios) > 1 else 0.0
        symbols = tuple(holding.symbol for holding in portfolio.holdings)
        exposures = {
            holding.symbol: holding.quantity * prices[holding.symbol]
            for holding in portfolio.holdings
        }
        gross_exposure = sum(abs(exposure) for exposure in exposures.values())
        weights = {
            symbol: exposure / gross_exposure for symbol, exposure in exposures.items()
        }
        analytics = PortfolioAnalytics(
            {
                symbol: self._market_data.historical_returns(symbol)
                for symbol in symbols
            },
            self._trading_days,
        )
        portfolio_returns = analytics.portfolio_returns(weights)
        covariance = analytics.covariance()
        correlation = analytics.correlation()
        cumulative_returns = analytics.cumulative_returns(weights)
        drawdowns = analytics.drawdown(weights)

        return RiskReport(
            portfolio_name=portfolio.name,
            market_value=market_value,
            unrealized_pnl=pnl,
            daily_volatility=daily_volatility,
            annualized_volatility=daily_volatility * math.sqrt(self._trading_days),
            value_at_risk=self._var_model.calculate(scenarios, confidence_level),
            expected_shortfall=self._es_model.calculate(scenarios, confidence_level),
            confidence_level=confidence_level,
            scenario_count=len(scenarios),
            trade_book_items=trade_book_items,
            asset_symbols=symbols,
            portfolio_returns=tuple(float(value) for value in portfolio_returns),
            covariance_matrix=tuple(
                tuple(float(value) for value in row) for row in covariance.to_numpy()
            ),
            correlation_matrix=tuple(
                tuple(float(value) for value in row) for row in correlation.to_numpy()
            ),
            return_annualized_volatility=analytics.annualized_volatility(weights),
            cumulative_returns=tuple(float(value) for value in cumulative_returns),
            drawdowns=tuple(float(value) for value in drawdowns),
            maximum_drawdown=analytics.maximum_drawdown(weights),
            sharpe_ratio=analytics.sharpe_ratio(weights),
            historical_var=analytics.historical_var(
                weights, confidence_level, gross_exposure
            ),
            historical_expected_shortfall=analytics.historical_expected_shortfall(
                weights, confidence_level, gross_exposure
            ),
        )
