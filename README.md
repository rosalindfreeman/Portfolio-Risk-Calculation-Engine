# Portfolio Risk Calculation Engine

A Python component for portfolio valuation, historical P&L simulation,
volatility, Value at Risk (VaR), Expected Shortfall (ES), and NumPy/pandas
portfolio analytics.

## Design

```text
MarketDataProvider
        |
        v
PortfolioEngine ----> VaRModel
        |
        +-----------> ExpectedShortfallModel
        |
        v
    RiskReport -----> renderer / API / persistence
```

Each boundary is an interface (`Protocol`). A live feed can replace the in-memory
provider, and parametric or Monte Carlo models can replace the historical models
without changing the portfolio engine.

## Quick start

Run the included example from the project root:

```shell
python -m portfolio_risk
```

When using the repository without installing it first, run that command from
the `src` directory. Do not execute `portfolio_risk/__init__.py` directly;
it is the package initializer, not a script.

Or use the API in your own code:

```python
from portfolio_risk import (
    HistoricalExpectedShortfall, HistoricalVaR, Holding,
    InMemoryMarketDataProvider, Portfolio, PortfolioEngine,
    TextRiskReportRenderer,
)

market_data = InMemoryMarketDataProvider(
    prices={"ABC": 110.0, "XYZ": 50.0},
    returns={
        "ABC": [-0.10, -0.02, 0.00, 0.03, 0.05],
        "XYZ": [0.02, -0.01, 0.00, 0.01, -0.02],
    },
)
portfolio = Portfolio("Trading Book", (
    Holding("ABC", quantity=10, average_cost=100.0),
    Holding("XYZ", quantity=-4, average_cost=55.0),
))
engine = PortfolioEngine(
    market_data, HistoricalVaR(), HistoricalExpectedShortfall()
)
report = engine.generate_report(portfolio, confidence_level=0.95)
print(TextRiskReportRenderer().render(report))
```

## NumPy and pandas analytics

```python
import pandas as pd
from portfolio_risk import PortfolioAnalytics

returns = pd.DataFrame({
    "ABC": [-0.10, -0.02, 0.00, 0.03, 0.05],
    "XYZ": [0.02, -0.01, 0.00, 0.01, -0.02],
})
analytics = PortfolioAnalytics(returns)
weights = {"ABC": 1.1, "XYZ": -0.2}

print(analytics.correlation())
print(analytics.annualized_volatility(weights))
print(analytics.maximum_drawdown(weights))
print(analytics.sharpe_ratio(weights))
print(analytics.historical_var(weights, 0.95, portfolio_value=1000))
```

Historical return arrays must refer to the same observation dates and have the
same length. Scenario P&L is calculated as `quantity × current price × return`.
Daily volatility is sample standard deviation; annual volatility uses the square
root of 252. VaR and ES are non-negative loss amounts. ES uses fractional
weighting when the empirical tail boundary falls between observations.

## Development

```shell
python -m pip install -e .
python -m unittest discover -s tests
```
