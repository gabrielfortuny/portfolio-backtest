"""Tests for portfolio.data module."""

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from portfolio.data import fetch_prices, load_transactions


class TestLoadTransactions:
    """Tests for load_transactions function."""

    def test_load_transactions_valid(self, temp_csv, valid_csv_content):
        """Load valid CSV file with expected columns."""
        csv_path = temp_csv(valid_csv_content)
        df = load_transactions(csv_path)

        assert len(df) == 3
        assert list(df.columns) == ["date", "ticker", "amount", "type", "shares"]
        assert df["ticker"].tolist() == ["AAPL", "MSFT", "AAPL"]
        assert df["amount"].tolist() == [2000.0, 3000.0, 1500.0]
        assert df["type"].tolist() == ["buy", "buy", "buy"]

    def test_load_transactions_missing_file(self, tmp_path):
        """Raise FileNotFoundError for missing file."""
        missing_path = tmp_path / "nonexistent.csv"

        with pytest.raises(FileNotFoundError, match="Transactions file not found"):
            load_transactions(missing_path)

    def test_load_transactions_missing_columns(self, temp_csv):
        """Raise ValueError when required columns are missing."""
        content = """date,ticker
2023-01-03,AAPL"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="CSV missing required columns"):
            load_transactions(csv_path)

    def test_load_transactions_zero_amount(self, temp_csv):
        """Raise ValueError for zero or negative amounts."""
        content = """date,ticker,amount
2023-01-03,AAPL,0"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="Amount must be positive"):
            load_transactions(csv_path)

    def test_load_transactions_negative_amount(self, temp_csv):
        """Raise ValueError for negative amounts."""
        content = """date,ticker,amount
2023-01-03,AAPL,-100"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="Amount must be positive"):
            load_transactions(csv_path)

    def test_load_transactions_invalid_ticker(self, temp_csv):
        """Raise ValueError for invalid ticker symbols."""
        content = """date,ticker,amount
2023-01-03,!!!,2000"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="Invalid ticker symbol"):
            load_transactions(csv_path)

    def test_load_transactions_invalid_date(self, temp_csv):
        """Raise ValueError for invalid date format."""
        content = """date,ticker,amount
not-a-date,AAPL,2000"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="Invalid date"):
            load_transactions(csv_path)

    def test_load_transactions_lowercase_ticker(self, temp_csv):
        """Normalize lowercase tickers to uppercase."""
        content = """date,ticker,amount
2023-01-03,aapl,2000"""
        csv_path = temp_csv(content)
        df = load_transactions(csv_path)

        assert df["ticker"].iloc[0] == "AAPL"

    def test_load_transactions_sell_type(self, temp_csv):
        """Handle sell transaction type."""
        content = """date,ticker,amount,type
2023-01-03,AAPL,2000,buy
2023-06-01,AAPL,1000,sell"""
        csv_path = temp_csv(content)
        df = load_transactions(csv_path)

        assert df["type"].tolist() == ["buy", "sell"]

    def test_load_transactions_default_buy_type(self, temp_csv):
        """Default to buy type when type column is missing."""
        content = """date,ticker,amount
2023-01-03,AAPL,2000"""
        csv_path = temp_csv(content)
        df = load_transactions(csv_path)

        assert df["type"].iloc[0] == "buy"

    def test_load_transactions_invalid_type(self, temp_csv):
        """Raise ValueError for invalid transaction type."""
        content = """date,ticker,amount,type
2023-01-03,AAPL,2000,transfer"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="Invalid transaction types"):
            load_transactions(csv_path)

    def test_load_transactions_sorts_by_date(self, temp_csv):
        """Transactions should be sorted by date."""
        content = """date,ticker,amount
2023-06-01,MSFT,3000
2023-01-03,AAPL,2000"""
        csv_path = temp_csv(content)
        df = load_transactions(csv_path)

        assert df["date"].iloc[0] == date(2023, 1, 3)
        assert df["date"].iloc[1] == date(2023, 6, 1)

    def test_load_transactions_empty_file(self, temp_csv):
        """Raise ValueError for empty file (just headers)."""
        content = """date,ticker,amount"""
        csv_path = temp_csv(content)

        with pytest.raises(ValueError, match="No transactions found"):
            load_transactions(csv_path)


class TestFetchPrices:
    """Tests for fetch_prices function."""

    def test_fetch_prices_success(self, mocker, mock_yfinance_data):
        """Successfully fetch prices from mocked yfinance."""
        mocker.patch("portfolio.data.yf.download", return_value=mock_yfinance_data)

        prices = fetch_prices(
            ["AAPL", "MSFT", "SPY"], date(2023, 1, 3), date(2023, 12, 29)
        )

        assert "AAPL" in prices.columns
        assert "MSFT" in prices.columns
        assert "SPY" in prices.columns
        assert len(prices) > 0
        # Index should be date objects, not datetime
        assert isinstance(prices.index[0], date)

    def test_fetch_prices_single_ticker(self, mocker, mock_yfinance_single_ticker):
        """Fetch prices for single ticker returns DataFrame not Series."""
        mocker.patch(
            "portfolio.data.yf.download", return_value=mock_yfinance_single_ticker
        )

        prices = fetch_prices(["AAPL"], date(2023, 1, 3), date(2023, 12, 29))

        assert isinstance(prices, pd.DataFrame)
        assert "AAPL" in prices.columns
        assert len(prices) > 0

    def test_fetch_prices_network_error(self, mocker):
        """Handle network errors from yfinance."""
        mocker.patch(
            "portfolio.data.yf.download", side_effect=Exception("Network error")
        )

        with pytest.raises(ConnectionError, match="Failed to fetch price data"):
            fetch_prices(["AAPL"], date(2023, 1, 3), date(2023, 12, 29))

    def test_fetch_prices_empty_response(self, mocker):
        """Handle empty response from yfinance."""
        mocker.patch("portfolio.data.yf.download", return_value=pd.DataFrame())

        with pytest.raises(ValueError, match="No price data returned"):
            fetch_prices(["AAPL"], date(2023, 1, 3), date(2023, 12, 29))

    def test_fetch_prices_none_response(self, mocker):
        """Handle None response from yfinance."""
        mocker.patch("portfolio.data.yf.download", return_value=None)

        with pytest.raises(ValueError, match="No price data returned"):
            fetch_prices(["AAPL"], date(2023, 1, 3), date(2023, 12, 29))

    def test_fetch_prices_missing_ticker(self, mocker):
        """Raise error when requested ticker is missing from response."""
        # Mock returns data only for AAPL, not MSFT
        dates = pd.date_range(start="2023-01-03", end="2023-12-29", freq="B")
        data = pd.DataFrame(
            {("Close", "AAPL"): [130.0] * len(dates)},
            index=dates,
        )
        data.columns = pd.MultiIndex.from_tuples(data.columns)
        mocker.patch("portfolio.data.yf.download", return_value=data)

        with pytest.raises(ValueError, match="Failed to fetch prices for tickers"):
            fetch_prices(["AAPL", "MSFT"], date(2023, 1, 3), date(2023, 12, 29))

    def test_fetch_prices_default_end_date(self, mocker, mock_yfinance_single_ticker):
        """Use today as default end date when not specified."""
        mock_download = mocker.patch(
            "portfolio.data.yf.download", return_value=mock_yfinance_single_ticker
        )

        fetch_prices(["AAPL"], date(2023, 1, 3))

        # Verify download was called (end_date defaults to today)
        mock_download.assert_called_once()
