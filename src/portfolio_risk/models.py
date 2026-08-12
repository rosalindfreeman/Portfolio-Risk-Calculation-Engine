"""Domain objects used by the risk engine."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Holding:
    symbol: str
    quantity: float
    average_cost: float

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("holding symbol must not be blank")
        if self.average_cost < 0:
            raise ValueError("average_cost must be non-negative")


@dataclass(frozen=True, slots=True)
class Portfolio:
    name: str
    holdings: tuple[Holding, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("portfolio name must not be blank")
        if not self.holdings:
            raise ValueError("portfolio must contain at least one holding")
        symbols = [holding.symbol for holding in self.holdings]
        if len(symbols) != len(set(symbols)):
            raise ValueError("portfolio symbols must be unique")


@dataclass(frozen=True, slots=True)
class TradeBookItem:
    symbol: str
    quantity: float
    average_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float


@dataclass(frozen=True, slots=True)
class RiskReport:
    portfolio_name: str
    market_value: float
    unrealized_pnl: float
    daily_volatility: float
    annualized_volatility: float
    value_at_risk: float
    expected_shortfall: float
    confidence_level: float
    scenario_count: int
    trade_book_items: tuple[TradeBookItem, ...] = ()
    asset_symbols: tuple[str, ...] = ()
    portfolio_returns: tuple[float, ...] = ()
    covariance_matrix: tuple[tuple[float, ...], ...] = ()
    correlation_matrix: tuple[tuple[float, ...], ...] = ()
    return_annualized_volatility: float = 0.0
    cumulative_returns: tuple[float, ...] = ()
    drawdowns: tuple[float, ...] = ()
    maximum_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    historical_var: float = 0.0
    historical_expected_shortfall: float = 0.0
