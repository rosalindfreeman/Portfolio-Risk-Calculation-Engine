import math
from pathlib import Path
import sys
import unittest

import pandas as pd

# Allow this file to be run directly from the tests directory without first
# installing the package. Normal installed-package and discovery runs continue
# to use the same source tree.
PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from portfolio_risk import (  # type: ignore[import-not-found]
    HistoricalExpectedShortfall,
    HistoricalVaR,
    Holding,
    InMemoryMarketDataProvider,
    Portfolio,
    PortfolioAnalytics,
    PortfolioEngine,
    TextRiskReportRenderer,
)


def make_engine() -> PortfolioEngine:
    provider = InMemoryMarketDataProvider(
        prices={"ABC": 110.0, "XYZ": 50.0},
        returns={
            "ABC": [-0.10, -0.02, 0.00, 0.03, 0.05],
            "XYZ": [0.02, -0.01, 0.00, 0.01, -0.02],
        },
    )
    return PortfolioEngine(provider, HistoricalVaR(), HistoricalExpectedShortfall())


def make_portfolio() -> Portfolio:
    return Portfolio(
        "Trading Book",
        (Holding("ABC", 10, 100), Holding("XYZ", -4, 55)),
    )


class RiskEngineTests(unittest.TestCase):
    def test_scenario_pnl_includes_long_and_short_exposure(self) -> None:
        actual = make_engine().scenario_pnl(make_portfolio())
        expected = (-114.0, -20.0, 0.0, 31.0, 59.0)
        for actual_value, expected_value in zip(actual, expected):
            self.assertAlmostEqual(actual_value, expected_value)

    def test_report_calculates_valuation_volatility_var_and_es(self) -> None:
        report = make_engine().generate_report(make_portfolio(), confidence_level=0.8)

        self.assertEqual(report.market_value, 900.0)
        self.assertEqual(report.unrealized_pnl, 120.0)
        self.assertAlmostEqual(report.daily_volatility, 66.05073807309044)
        self.assertAlmostEqual(
            report.annualized_volatility, 66.05073807309044 * math.sqrt(252), places=5
        )
        self.assertAlmostEqual(report.value_at_risk, 38.8)
        self.assertAlmostEqual(report.expected_shortfall, 114.0)
        self.assertEqual(report.scenario_count, 5)

    def test_models_report_zero_risk_if_every_scenario_is_profitable(self) -> None:
        scenarios = [1.0, 2.0, 3.0]
        self.assertEqual(HistoricalVaR().calculate(scenarios, 0.95), 0.0)
        self.assertEqual(HistoricalExpectedShortfall().calculate(scenarios, 0.95), 0.0)

    def test_engine_rejects_misaligned_history(self) -> None:
        provider = InMemoryMarketDataProvider(
            {"ABC": 1, "XYZ": 1}, {"ABC": [0.1], "XYZ": [0.1, 0.2]}
        )
        engine = PortfolioEngine(provider, HistoricalVaR(), HistoricalExpectedShortfall())
        with self.assertRaisesRegex(ValueError, "aligned"):
            engine.scenario_pnl(make_portfolio())

    def test_text_report_is_renderable(self) -> None:
        rendered = TextRiskReportRenderer().render(
            make_engine().generate_report(make_portfolio(), 0.8)
        )
        self.assertIn("Risk Report: Trading Book", rendered)
        self.assertIn("Trading Book Items", rendered)
        self.assertIn("ABC", rendered)
        self.assertIn("XYZ", rendered)
        self.assertIn("Trading Book Summary", rendered)
        self.assertIn("VaR (80%)", rendered)
        self.assertIn("Portfolio return calculation", rendered)
        self.assertIn("Covariance matrix", rendered)
        self.assertIn("Correlation matrix", rendered)
        self.assertIn("Annualized volatility (return)", rendered)
        self.assertIn("Cumulative returns", rendered)
        self.assertIn("Maximum drawdown", rendered)
        self.assertIn("Sharpe ratio", rendered)
        self.assertIn("Historical Expected Shortfall", rendered)


class PortfolioAnalyticsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analytics = PortfolioAnalytics(
            pd.DataFrame(
                {
                    "ABC": [-0.10, -0.02, 0.00, 0.03, 0.05],
                    "XYZ": [0.02, -0.01, 0.00, 0.01, -0.02],
                }
            )
        )
        self.weights = {"ABC": 1.1, "XYZ": -0.2}

    def test_portfolio_returns_covariance_and_correlation(self) -> None:
        expected = [-0.114, -0.020, 0.0, 0.031, 0.059]
        self.assertEqual(self.analytics.portfolio_returns(self.weights).round(3).tolist(), expected)
        self.assertEqual(self.analytics.covariance().shape, (2, 2))
        self.assertEqual(self.analytics.correlation().shape, (2, 2))

    def test_risk_and_performance_metrics(self) -> None:
        self.assertAlmostEqual(self.analytics.annualized_volatility(self.weights), 1.04852, places=5)
        self.assertAlmostEqual(self.analytics.historical_var(self.weights, 0.95, 1000), 95.2)
        self.assertAlmostEqual(self.analytics.historical_expected_shortfall(self.weights, 0.95, 1000), 114.0)
        self.assertAlmostEqual(self.analytics.maximum_drawdown(self.weights), 0.13172)
        self.assertTrue(math.isfinite(self.analytics.sharpe_ratio(self.weights)))


if __name__ == "__main__":
    unittest.main()
