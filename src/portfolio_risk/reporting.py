"""Risk report presentation adapters."""

from .models import RiskReport


class TextRiskReportRenderer:
    def render(self, report: RiskReport) -> str:
        confidence = report.confidence_level * 100
        lines = [
                f"Risk Report: {report.portfolio_name}",
        ]
        if report.trade_book_items:
            lines.extend(("", "Trading Book Items", self._format_trade_book_header()))
            lines.extend(self._format_trade_book_item(item) for item in report.trade_book_items)
            lines.extend(("", "Trading Book Summary"))
        lines.extend([
                f"Market value:       {report.market_value:,.2f}",
                f"Unrealized P&L:     {report.unrealized_pnl:,.2f}",
                f"Daily volatility:   {report.daily_volatility:,.2f}",
                f"Annual volatility:  {report.annualized_volatility:,.2f}",
                f"VaR ({confidence:g}%):          {report.value_at_risk:,.2f}",
                f"Expected Shortfall: {report.expected_shortfall:,.2f}",
                f"Scenarios:          {report.scenario_count}",
        ])
        if report.asset_symbols:
            lines.extend(
                (
                    "",
                    "Portfolio Analytics",
                    "Portfolio return calculation: "
                    + self._format_percent_series(report.portfolio_returns),
                    "Covariance matrix:",
                    *self._format_matrix(
                        report.asset_symbols, report.covariance_matrix, percent=False
                    ),
                    "Correlation matrix:",
                    *self._format_matrix(
                        report.asset_symbols, report.correlation_matrix, percent=False
                    ),
                    f"Annualized volatility (return): {report.return_annualized_volatility:.2%}",
                    "Cumulative returns: "
                    + self._format_percent_series(report.cumulative_returns),
                    "Drawdown: " + self._format_percent_series(report.drawdowns),
                    f"Maximum drawdown: {report.maximum_drawdown:.2%}",
                    f"Sharpe ratio: {report.sharpe_ratio:.4f}",
                    f"Historical VaR ({confidence:g}%): {report.historical_var:,.2f}",
                    "Historical Expected Shortfall: "
                    f"{report.historical_expected_shortfall:,.2f}",
                )
            )
        return "\n".join(lines)

    @staticmethod
    def _format_trade_book_header() -> str:
        return (
            f"{'Symbol':<8}{'Quantity':>12}{'Avg cost':>12}{'Price':>12}"
            f"{'Market value':>16}{'Unrealized P&L':>18}"
        )

    @staticmethod
    def _format_trade_book_item(item: object) -> str:
        return (
            f"{item.symbol:<8}{item.quantity:>12,.2f}{item.average_cost:>12,.2f}"
            f"{item.current_price:>12,.2f}{item.market_value:>16,.2f}"
            f"{item.unrealized_pnl:>18,.2f}"
        )

    @staticmethod
    def _format_percent_series(values: tuple[float, ...]) -> str:
        return "[" + ", ".join(f"{value:.2%}" for value in values) + "]"

    @staticmethod
    def _format_matrix(
        symbols: tuple[str, ...],
        matrix: tuple[tuple[float, ...], ...],
        percent: bool = False,
    ) -> list[str]:
        width = max(10, max(len(symbol) for symbol in symbols) + 2)
        lines = [" " * width + "".join(f"{symbol:>{width}}" for symbol in symbols)]
        for symbol, row in zip(symbols, matrix):
            formatted = "".join(
                f"{value:>{width}.2%}" if percent else f"{value:>{width}.6f}"
                for value in row
            )
            lines.append(f"{symbol:<{width}}{formatted}")
        return lines
