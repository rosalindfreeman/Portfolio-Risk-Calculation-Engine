"""Public API for the portfolio risk engine.

Use ``python -m portfolio_risk`` to run the example. Direct execution is also
accepted for compatibility with editor Run buttons.
"""

if __name__ == "__main__" and not __package__:
    from pathlib import Path
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from portfolio_risk.__main__ import main

    main()
    raise SystemExit

from .engine import PortfolioEngine
from .analytics import PortfolioAnalytics
from .interfaces import ExpectedShortfallModel, MarketDataProvider, VaRModel
from .market_data import InMemoryMarketDataProvider
from .models import Holding, Portfolio, RiskReport, TradeBookItem
from .reporting import TextRiskReportRenderer
from .risk_models import HistoricalExpectedShortfall, HistoricalVaR

__all__ = [
    "ExpectedShortfallModel",
    "HistoricalExpectedShortfall",
    "HistoricalVaR",
    "Holding",
    "InMemoryMarketDataProvider",
    "MarketDataProvider",
    "Portfolio",
    "PortfolioAnalytics",
    "PortfolioEngine",
    "RiskReport",
    "TextRiskReportRenderer",
    "TradeBookItem",
    "VaRModel",
]
