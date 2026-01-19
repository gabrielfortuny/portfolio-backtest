"""Tests for portfolio.engine module."""

from datetime import date

import pandas as pd
import pytest

from portfolio.engine import (
    build_holdings_history,
    calculate_portfolio_value,
    get_benchmark_series,
    get_current_holdings,
    normalize_series,
    process_transactions,
)


class TestProcessTransactions:
    """Tests for process_transactions function."""

    def test_process_transactions_buy(self):
        """Calculate shares for buy transactions."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [float("nan")],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0]},
            index=[date(2023, 1, 3)],
        )

        result = process_transactions(transactions, prices)

        assert result["shares"].iloc[0] == 10.0  # 1000 / 100 = 10 shares

    def test_process_transactions_sell(self):
        """Calculate negative shares for sell transactions."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [500.0],
                "type": ["sell"],
                "shares": [float("nan")],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0]},
            index=[date(2023, 1, 3)],
        )

        result = process_transactions(transactions, prices)

        assert result["shares"].iloc[0] == -5.0  # -500 / 100 = -5 shares

    def test_process_transactions_invalid_date(self):
        """Raise error for transaction on non-trading day."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 7)],  # Saturday - not in prices index
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [float("nan")],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0]},
            index=[date(2023, 1, 6)],  # Friday
        )

        with pytest.raises(ValueError, match="No trading data for"):
            process_transactions(transactions, prices)

    def test_process_transactions_does_not_modify_original(self):
        """Original DataFrame should not be modified."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [float("nan")],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0]},
            index=[date(2023, 1, 3)],
        )

        original_shares = transactions["shares"].iloc[0]
        process_transactions(transactions, prices)

        assert pd.isna(original_shares)
        assert pd.isna(transactions["shares"].iloc[0])


class TestBuildHoldingsHistory:
    """Tests for build_holdings_history function."""

    def test_build_holdings_history_single_buy(self):
        """Simple case with single buy transaction."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 101.0, 102.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4), date(2023, 1, 5)],
        )

        holdings = build_holdings_history(transactions, prices)

        # All dates should have 10 shares
        assert holdings["AAPL"].iloc[0] == 10.0
        assert holdings["AAPL"].iloc[-1] == 10.0

    def test_build_holdings_history_multiple_buys(self):
        """Accumulate shares from multiple buy transactions."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 1, 5)],
                "ticker": ["AAPL", "AAPL"],
                "amount": [1000.0, 500.0],
                "type": ["buy", "buy"],
                "shares": [10.0, 5.0],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 101.0, 102.0, 103.0]},
            index=[
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
        )

        holdings = build_holdings_history(transactions, prices)

        assert holdings["AAPL"].iloc[0] == 10.0  # After first buy
        assert holdings["AAPL"].iloc[1] == 10.0  # Still 10
        assert holdings["AAPL"].iloc[2] == 15.0  # After second buy
        assert holdings["AAPL"].iloc[3] == 15.0  # Still 15

    def test_build_holdings_history_buy_then_sell(self):
        """Position reduction from sell after buy."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 1, 5)],
                "ticker": ["AAPL", "AAPL"],
                "amount": [1000.0, 300.0],
                "type": ["buy", "sell"],
                "shares": [10.0, -3.0],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 101.0, 102.0, 103.0]},
            index=[
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
        )

        holdings = build_holdings_history(transactions, prices)

        assert holdings["AAPL"].iloc[0] == 10.0  # After buy
        assert holdings["AAPL"].iloc[2] == 7.0  # After sell
        assert holdings["AAPL"].iloc[3] == 7.0  # Still 7

    def test_build_holdings_history_oversell(self):
        """Raise error when selling more shares than held."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 1, 5)],
                "ticker": ["AAPL", "AAPL"],
                "amount": [1000.0, 1500.0],
                "type": ["buy", "sell"],
                "shares": [10.0, -15.0],  # Selling 15 when only 10 held
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 101.0, 102.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4), date(2023, 1, 5)],
        )

        with pytest.raises(ValueError, match="Cannot sell"):
            build_holdings_history(transactions, prices)

    def test_build_holdings_history_multiple_tickers(self):
        """Track holdings for multiple tickers."""
        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 1, 3)],
                "ticker": ["AAPL", "MSFT"],
                "amount": [1000.0, 2000.0],
                "type": ["buy", "buy"],
                "shares": [10.0, 8.0],
            }
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 101.0], "MSFT": [250.0, 252.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        holdings = build_holdings_history(transactions, prices)

        assert "AAPL" in holdings.columns
        assert "MSFT" in holdings.columns
        assert holdings["AAPL"].iloc[0] == 10.0
        assert holdings["MSFT"].iloc[0] == 8.0


class TestCalculatePortfolioValue:
    """Tests for calculate_portfolio_value function."""

    def test_calculate_portfolio_value(self):
        """Calculate portfolio value from holdings and prices."""
        holdings = pd.DataFrame(
            {"AAPL": [10.0, 10.0], "MSFT": [5.0, 5.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 105.0], "MSFT": [200.0, 210.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        portfolio_value = calculate_portfolio_value(holdings, prices)

        # Day 1: 10*100 + 5*200 = 2000
        assert portfolio_value.iloc[0] == 2000.0
        # Day 2: 10*105 + 5*210 = 2100
        assert portfolio_value.iloc[1] == 2100.0

    def test_calculate_portfolio_value_partial_holdings(self):
        """Handle case where holdings don't span full price range."""
        holdings = pd.DataFrame(
            {"AAPL": [0.0, 10.0, 10.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4), date(2023, 1, 5)],
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 102.0, 105.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4), date(2023, 1, 5)],
        )

        portfolio_value = calculate_portfolio_value(holdings, prices)

        assert portfolio_value.iloc[0] == 0.0  # No holdings yet
        assert portfolio_value.iloc[1] == 1020.0  # 10 * 102
        assert portfolio_value.iloc[2] == 1050.0  # 10 * 105


class TestGetCurrentHoldings:
    """Tests for get_current_holdings function."""

    def test_get_current_holdings(self):
        """Get current holdings snapshot with values."""
        holdings = pd.DataFrame(
            {"AAPL": [10.0, 15.0], "MSFT": [5.0, 5.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0, 110.0], "MSFT": [200.0, 220.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        current = get_current_holdings(holdings, prices)

        assert len(current) == 2
        assert "ticker" in current.columns
        assert "shares" in current.columns
        assert "current_price" in current.columns
        assert "position_value" in current.columns
        assert "portfolio_pct" in current.columns

        # Check AAPL values (15 shares * $110 = $1650)
        aapl_row = current[current["ticker"] == "AAPL"].iloc[0]
        assert aapl_row["shares"] == 15.0
        assert aapl_row["current_price"] == 110.0
        assert aapl_row["position_value"] == 1650.0

    def test_get_current_holdings_empty(self):
        """Return empty DataFrame for empty holdings."""
        holdings = pd.DataFrame(columns=["AAPL"])
        holdings.index = pd.Index([], name="date")
        prices = pd.DataFrame(columns=["AAPL"])
        prices.index = pd.Index([], name="date")

        current = get_current_holdings(holdings, prices)

        assert current.empty
        assert list(current.columns) == [
            "ticker",
            "shares",
            "current_price",
            "position_value",
            "portfolio_pct",
        ]

    def test_get_current_holdings_excludes_zero_positions(self):
        """Exclude tickers with zero shares."""
        holdings = pd.DataFrame(
            {"AAPL": [10.0], "MSFT": [0.0]},  # MSFT sold completely
            index=[date(2023, 1, 4)],
        )
        prices = pd.DataFrame(
            {"AAPL": [110.0], "MSFT": [220.0]},
            index=[date(2023, 1, 4)],
        )

        current = get_current_holdings(holdings, prices)

        assert len(current) == 1
        assert current["ticker"].iloc[0] == "AAPL"

    def test_get_current_holdings_portfolio_pct(self):
        """Portfolio percentage should sum to 100."""
        holdings = pd.DataFrame(
            {"AAPL": [10.0], "MSFT": [5.0]},
            index=[date(2023, 1, 4)],
        )
        prices = pd.DataFrame(
            {"AAPL": [100.0], "MSFT": [200.0]},  # AAPL: 1000, MSFT: 1000
            index=[date(2023, 1, 4)],
        )

        current = get_current_holdings(holdings, prices)

        assert abs(current["portfolio_pct"].sum() - 100.0) < 0.01


class TestNormalizeSeries:
    """Tests for normalize_series function."""

    def test_normalize_series(self):
        """Normalize series to start at 100."""
        series = pd.Series(
            [1000.0, 1100.0, 1050.0],
            index=[date(2023, 1, 3), date(2023, 1, 4), date(2023, 1, 5)],
            name="portfolio_value",
        )

        normalized = normalize_series(series, date(2023, 1, 3))

        assert normalized.iloc[0] == pytest.approx(100.0)
        assert normalized.iloc[1] == pytest.approx(110.0)
        assert normalized.iloc[2] == pytest.approx(105.0)

    def test_normalize_series_from_later_date(self):
        """Normalize from a date after the series start."""
        series = pd.Series(
            [1000.0, 1100.0, 1050.0, 1200.0],
            index=[
                date(2023, 1, 3),
                date(2023, 1, 4),
                date(2023, 1, 5),
                date(2023, 1, 6),
            ],
            name="portfolio_value",
        )

        normalized = normalize_series(series, date(2023, 1, 5))

        # Should start from 1050 as base
        assert len(normalized) == 2
        assert normalized.iloc[0] == 100.0  # 1050 -> 100
        assert abs(normalized.iloc[1] - 114.29) < 0.01  # 1200/1050 * 100

    def test_normalize_series_zero_base(self):
        """Return empty series if base value is zero."""
        series = pd.Series(
            [0.0, 100.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        normalized = normalize_series(series, date(2023, 1, 3))

        assert normalized.empty

    def test_normalize_series_empty_after_filter(self):
        """Return empty series if no data after start date."""
        series = pd.Series(
            [1000.0, 1100.0],
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        normalized = normalize_series(series, date(2023, 1, 10))

        assert normalized.empty


class TestGetBenchmarkSeries:
    """Tests for get_benchmark_series function."""

    def test_get_benchmark_series(self):
        """Extract benchmark series from prices DataFrame."""
        prices = pd.DataFrame(
            {"AAPL": [100.0, 105.0], "SPY": [400.0, 410.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        benchmark = get_benchmark_series(prices, "SPY")

        assert benchmark.name == "SPY"
        assert len(benchmark) == 2
        assert benchmark.iloc[0] == 400.0
        assert benchmark.iloc[1] == 410.0

    def test_get_benchmark_series_missing_ticker(self):
        """Raise error for missing benchmark ticker."""
        prices = pd.DataFrame(
            {"AAPL": [100.0, 105.0]},
            index=[date(2023, 1, 3), date(2023, 1, 4)],
        )

        with pytest.raises(ValueError, match="Benchmark ticker .* not found"):
            get_benchmark_series(prices, "SPY")
