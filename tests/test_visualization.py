"""Tests for portfolio.visualization module."""

from datetime import date

import pandas as pd
import pytest
from matplotlib.figure import Figure

from portfolio.visualization import (
    create_benchmark_comparison_chart,
    create_holdings_pie_chart,
    create_portfolio_value_chart,
)


class TestCreatePortfolioValueChart:
    """Tests for create_portfolio_value_chart function."""

    def test_create_portfolio_value_chart(self):
        """Create chart and return Figure object."""
        portfolio_value = pd.Series(
            [1000.0, 1100.0, 1050.0, 1200.0],
            index=[
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
            name="portfolio_value",
        )

        fig = create_portfolio_value_chart(portfolio_value)

        assert isinstance(fig, Figure)
        assert len(fig.axes) == 1
        # Chart should have a line
        ax = fig.axes[0]
        assert len(ax.lines) >= 1

    def test_create_portfolio_value_chart_has_labels(self):
        """Chart should have axis labels and title."""
        portfolio_value = pd.Series(
            [1000.0, 1100.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
            name="portfolio_value",
        )

        fig = create_portfolio_value_chart(portfolio_value)
        ax = fig.axes[0]

        assert ax.get_xlabel() != ""
        assert ax.get_ylabel() != ""
        assert ax.get_title() != ""


class TestCreateHoldingsPieChart:
    """Tests for create_holdings_pie_chart function."""

    def test_create_holdings_pie_chart(self):
        """Create pie chart and return Figure object."""
        holdings = pd.DataFrame(
            {
                "ticker": ["AAPL", "MSFT"],
                "shares": [10.0, 5.0],
                "current_price": [150.0, 300.0],
                "position_value": [1500.0, 1500.0],
                "portfolio_pct": [50.0, 50.0],
            }
        )

        fig = create_holdings_pie_chart(holdings)

        assert isinstance(fig, Figure)
        assert len(fig.axes) == 1

    def test_create_holdings_pie_chart_empty(self):
        """Handle empty holdings DataFrame."""
        holdings = pd.DataFrame(
            columns=[
                "ticker",
                "shares",
                "current_price",
                "position_value",
                "portfolio_pct",
            ]
        )

        fig = create_holdings_pie_chart(holdings)

        assert isinstance(fig, Figure)

    def test_create_holdings_pie_chart_small_positions(self):
        """Small positions should be grouped into 'Other'."""
        holdings = pd.DataFrame(
            {
                "ticker": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
                "shares": [100.0, 50.0, 1.0, 1.0, 1.0],
                "current_price": [150.0, 300.0, 100.0, 100.0, 100.0],
                "position_value": [15000.0, 15000.0, 100.0, 100.0, 100.0],
                "portfolio_pct": [49.5, 49.5, 0.33, 0.33, 0.34],
            }
        )

        fig = create_holdings_pie_chart(holdings)

        assert isinstance(fig, Figure)
        # The small positions (< 3%) should be grouped


class TestCreateBenchmarkComparisonChart:
    """Tests for create_benchmark_comparison_chart function."""

    def test_create_benchmark_comparison_chart(self):
        """Create comparison chart and return Figure object."""
        portfolio_indexed = pd.Series(
            [100.0, 110.0, 105.0, 120.0],
            index=[
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
            name="portfolio_normalized",
        )
        benchmark_indexed = pd.Series(
            [100.0, 102.0, 101.0, 108.0],
            index=[
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
            name="SPY_normalized",
        )

        fig = create_benchmark_comparison_chart(
            portfolio_indexed, benchmark_indexed, "SPY"
        )

        assert isinstance(fig, Figure)
        assert len(fig.axes) == 1
        ax = fig.axes[0]
        # Should have two lines (portfolio and benchmark)
        assert len(ax.lines) >= 2

    def test_create_benchmark_comparison_chart_has_legend(self):
        """Chart should have a legend."""
        portfolio_indexed = pd.Series(
            [100.0, 110.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )
        benchmark_indexed = pd.Series(
            [100.0, 105.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        fig = create_benchmark_comparison_chart(
            portfolio_indexed, benchmark_indexed, "SPY"
        )
        ax = fig.axes[0]

        legend = ax.get_legend()
        assert legend is not None

    def test_create_benchmark_comparison_chart_title_includes_benchmark(self):
        """Chart title should include benchmark name."""
        portfolio_indexed = pd.Series(
            [100.0, 110.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )
        benchmark_indexed = pd.Series(
            [100.0, 105.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        fig = create_benchmark_comparison_chart(
            portfolio_indexed, benchmark_indexed, "VT"
        )
        ax = fig.axes[0]

        assert "VT" in ax.get_title()
