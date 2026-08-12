"""Executable demonstration for the portfolio risk package."""

# Running this file by path does not give it a package context. Support that
# editor/IDE execution mode in addition to the preferred ``python -m`` mode.
if __package__:
    from .engine import PortfolioEngine
    from .market_data import InMemoryMarketDataProvider
    from .models import Holding, Portfolio
    from .reporting import TextRiskReportRenderer
    from .risk_models import HistoricalExpectedShortfall, HistoricalVaR
else:
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

    from portfolio_risk.engine import PortfolioEngine
    from portfolio_risk.market_data import InMemoryMarketDataProvider
    from portfolio_risk.models import Holding, Portfolio
    from portfolio_risk.reporting import TextRiskReportRenderer
    from portfolio_risk.risk_models import HistoricalExpectedShortfall, HistoricalVaR


def main() -> None:
    """Calculate and print a risk report using the example portfolio."""
    market_data = InMemoryMarketDataProvider(
        prices={"ABC": 110.0, "XYZ": 50.0},
        returns={
            "ABC": [-0.10, -0.02, 0.00, 0.03, 0.05],
            "XYZ": [0.02, -0.01, 0.00, 0.01, -0.02],
        },
    )
    portfolio = Portfolio(
        "Trading Book",
        (
            Holding("ABC", quantity=10, average_cost=100.0),
            Holding("XYZ", quantity=-4, average_cost=55.0),
        ),
    )
    engine = PortfolioEngine(
        market_data,
        HistoricalVaR(),
        HistoricalExpectedShortfall(),
    )
    report = engine.generate_report(portfolio, confidence_level=0.95)
    print(TextRiskReportRenderer().render(report))


if __name__ == "__main__":
    main()
