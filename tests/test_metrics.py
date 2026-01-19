"""Tests for portfolio.metrics module."""

from datetime import date

import pandas as pd
import pytest

from portfolio.metrics import calculate_metrics


class TestCalculateMetrics:
    """Tests for calculate_metrics function."""

    def test_calculate_metrics_contributions(self):
        """Calculate total contributions from buy transactions."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 3, 1)],
                "ticker": ["AAPL", "MSFT"],
                "amount": [2000.0, 3000.0],
                "type": ["buy", "buy"],
                "shares": [10.0, 12.0],
            }
        )
        portfolio_value = pd.Series(
            [2000.0, 5500.0],
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["total_contributions"] == 5000.0

    def test_calculate_metrics_withdrawals(self):
        """Calculate total withdrawals from sell transactions."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 6, 1)],
                "ticker": ["AAPL", "AAPL"],
                "amount": [2000.0, 500.0],
                "type": ["buy", "sell"],
                "shares": [10.0, -2.5],
            }
        )
        portfolio_value = pd.Series(
            [2000.0, 1800.0],
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["total_withdrawals"] == 500.0
        assert metrics["net_contributions"] == 1500.0  # 2000 - 500

    def test_calculate_metrics_gain_loss(self):
        """Calculate absolute and percentage gain/loss."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1200.0],
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["current_value"] == 1200.0
        assert metrics["gain_loss"] == 200.0  # 1200 - 1000
        assert metrics["gain_loss_pct"] == 20.0  # 200/1000 * 100

    def test_calculate_metrics_cagr(self):
        """Calculate compound annual growth rate."""
        transactions = pd.DataFrame(
            {
                "date": [date(2021, 1, 4)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1210.0],  # 21% total return
            index=[date(2021, 1, 4), date(2023, 1, 4)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 1, 4)
        )

        # CAGR for 21% return over 2 years should be ~10%
        # (1.21)^(1/2) - 1 = 0.10 = 10%
        assert metrics["years_elapsed"] == pytest.approx(2.0, abs=0.01)
        assert metrics["cagr"] == pytest.approx(10.0, abs=0.5)

    def test_calculate_metrics_with_benchmark(self):
        """Calculate alpha relative to benchmark."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1300.0],  # 30% return
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )
        # Benchmark series (already normalized to 100)
        benchmark_series = pd.Series(
            [100.0, 120.0],  # 20% return
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions,
            portfolio_value,
            end_date=date(2023, 12, 29),
            benchmark_series=benchmark_series,
            benchmark_name="SPY",
        )

        assert "benchmark_return" in metrics
        assert "benchmark_cagr" in metrics
        assert "alpha" in metrics
        assert metrics["benchmark_name"] == "SPY"
        assert metrics["benchmark_return"] == pytest.approx(20.0, abs=0.1)
        # Alpha = portfolio CAGR - benchmark CAGR
        assert metrics["alpha"] > 0  # Portfolio outperformed

    def test_calculate_metrics_short_period(self):
        """Handle period less than 1 year."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 10, 2)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1050.0],  # 5% return in ~3 months
            index=[date(2023, 10, 2), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["years_elapsed"] < 1.0
        assert metrics["years_elapsed"] > 0
        # CAGR and simple annualized should still be calculated
        assert metrics["cagr"] != 0
        assert metrics["simple_annualized_return"] != 0

    def test_calculate_metrics_long_period(self):
        """Handle multi-year period."""
        transactions = pd.DataFrame(
            {
                "date": [date(2018, 1, 2)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 2000.0],  # 100% return over 5 years
            index=[date(2018, 1, 2), date(2023, 1, 2)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 1, 2)
        )

        assert metrics["years_elapsed"] == pytest.approx(5.0, abs=0.01)
        # CAGR for 100% return over 5 years: (2)^(1/5) - 1 = 14.87%
        assert metrics["cagr"] == pytest.approx(14.87, abs=0.5)

    def test_calculate_metrics_zero_gain(self):
        """Handle break-even case with no gain/loss."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1000.0],  # No change
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["gain_loss"] == 0.0
        assert metrics["gain_loss_pct"] == 0.0
        assert metrics["cagr"] == 0.0

    def test_calculate_metrics_negative_return(self):
        """Handle negative returns (loss)."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 800.0],  # 20% loss
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["gain_loss"] == -200.0
        assert metrics["gain_loss_pct"] == -20.0
        assert metrics["cagr"] < 0

    def test_calculate_metrics_default_end_date(self):
        """Use today as default end date."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1100.0],
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )

        metrics = calculate_metrics(transactions, portfolio_value)

        # Should have an end_date set to today
        assert "end_date" in metrics
        assert metrics["end_date"] == date.today()

    def test_calculate_metrics_empty_portfolio(self):
        """Handle empty portfolio value."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series([], dtype=float)

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 12, 29)
        )

        assert metrics["current_value"] == 0.0

    def test_calculate_metrics_no_withdrawals(self):
        """Total withdrawals should be 0 when no sells."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0],
            index=[date(2023, 1, 3)],
        )

        metrics = calculate_metrics(
            transactions, portfolio_value, end_date=date(2023, 1, 3)
        )

        assert metrics["total_withdrawals"] == 0.0

    def test_calculate_metrics_benchmark_empty(self):
        """Skip benchmark metrics if benchmark series is empty."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        portfolio_value = pd.Series(
            [1000.0, 1100.0],
            index=[date(2023, 1, 3), date(2023, 12, 29)],
        )
        empty_benchmark = pd.Series([], dtype=float)

        metrics = calculate_metrics(
            transactions,
            portfolio_value,
            end_date=date(2023, 12, 29),
            benchmark_series=empty_benchmark,
            benchmark_name="SPY",
        )

        assert "benchmark_return" not in metrics
        assert "alpha" not in metrics
