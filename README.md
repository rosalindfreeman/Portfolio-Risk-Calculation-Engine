# Portfolio Risk Calculation Engine

A Python component for portfolio valuation, historical P&L simulation,
volatility, Value at Risk (VaR), Expected Shortfall (ES), and NumPy/pandas
portfolio analytics.


## Math:

1. Market value: The portfolio’s current net value: long positions minus short positions. A net value of 900 means the portfolio has 900 more long exposure than short exposure.
2. Unrealized P&L:
3. P&L measures profit or loss.
4. Volatility measures variability, including gains and losses.
5. VaR estimates a loss threshold.
6. Expected Shortfall estimates loss severity beyond that threshold.
7. Covariance measures joint movement in raw return units.
8. Correlation standardizes joint movement between −1 and +1.
9. Scenarios are historical “what-if” outcomes, not forecasts.
10. Market value: 900.00, The portfolio’s current net value: long positions minus short positions. A net value of 900 means the portfolio has 900 more long exposure than short exposure. 
11. Unrealized P&L: 120.00 The profit currently showing on open positions. It is “unrealized” because the positions have not yet been closed. If closed at the stated prices, the portfolio would realize approximately 120 profit, ignoring costs. 
12. Daily volatility: 66.05 The estimated standard deviation of the portfolio’s one-day P&L. In plain terms, historical daily P&L has typically varied by roughly 66 around its average. It is a risk measure, not a guaranteed maximum loss. 
13. Annual volatility: 1,048.52** Daily P&L volatility scaled to approximately one trading year using 252 trading days. It expresses annual risk in currency units. It does not mean the portfolio is expected to lose 1,048.52.
14. VaR (95%): 95.20**  The estimated one-period loss threshold at 95% confidence. Under the historical model, losses should be no greater than 95.20 in roughly 95% of comparable periods—and could exceed it in the worst 5%. 
15. Expected Shortfall: 114.00** The estimated average loss when the loss exceeds the 95% VaR boundary. It describes the severity of the worst 5% of outcomes. Here, the limited data make it equal to the worst observed loss. 
16. Scenarios: 5** Five historical return combinations were used. Each combination represents what would happen to today’s portfolio if those historical asset movements occurred again. 




## Design

```text
MarketDataProvider
         |
PortfolioEngine link to VaRModel
         |
 ExpectedShortfallModel
        |
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
