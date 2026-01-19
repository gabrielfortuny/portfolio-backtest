"""Shared fixtures for portfolio backtesting tests."""

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

# Add project root to path so 'portfolio' module can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_transactions_df():
    """DataFrame mimicking loaded transactions with shares calculated."""
    return pd.DataFrame(
        {
            "date": [date(2023, 1, 3), date(2023, 3, 1), date(2023, 6, 1)],
            "ticker": ["AAPL", "MSFT", "AAPL"],
            "amount": [2000.0, 3000.0, 1500.0],
            "type": ["buy", "buy", "buy"],
            "shares": [15.0, 12.0, 8.0],
        }
    )


@pytest.fixture
def sample_transactions_with_sell_df():
    """DataFrame with buy and sell transactions."""
    return pd.DataFrame(
        {
            "date": [
                date(2023, 1, 3),
                date(2023, 3, 1),
                date(2023, 6, 1),
                date(2023, 9, 1),
            ],
            "ticker": ["AAPL", "MSFT", "AAPL", "AAPL"],
            "amount": [2000.0, 3000.0, 1500.0, 1000.0],
            "type": ["buy", "buy", "buy", "sell"],
            "shares": [15.0, 12.0, 8.0, -5.0],
        }
    )


@pytest.fixture
def sample_transactions_unprocessed_df():
    """DataFrame mimicking loaded transactions before shares are calculated."""
    return pd.DataFrame(
        {
            "date": [date(2023, 1, 3), date(2023, 3, 1)],
            "ticker": ["AAPL", "MSFT"],
            "amount": [2000.0, 3000.0],
            "type": ["buy", "buy"],
            "shares": [float("nan"), float("nan")],
        }
    )


@pytest.fixture
def sample_prices_df():
    """DataFrame with price data for testing."""
    dates = pd.date_range(start="2023-01-03", end="2023-12-29", freq="B")
    dates = [d.date() for d in dates]

    # Create somewhat realistic price data
    import numpy as np

    np.random.seed(42)
    n = len(dates)

    aapl_base = 130.0
    msft_base = 250.0
    spy_base = 400.0

    # Add some trend and noise
    aapl_prices = aapl_base * (1 + np.cumsum(np.random.randn(n) * 0.01 + 0.0003))
    msft_prices = msft_base * (1 + np.cumsum(np.random.randn(n) * 0.012 + 0.0004))
    spy_prices = spy_base * (1 + np.cumsum(np.random.randn(n) * 0.008 + 0.0002))

    df = pd.DataFrame(
        {"AAPL": aapl_prices, "MSFT": msft_prices, "SPY": spy_prices}, index=dates
    )
    return df


@pytest.fixture
def sample_holdings_df(sample_prices_df):
    """DataFrame with holdings history."""
    dates = sample_prices_df.index
    n = len(dates)

    # AAPL: 15 shares from start, +8 from June
    aapl_shares = [15.0] * n
    june_idx = next(i for i, d in enumerate(dates) if d >= date(2023, 6, 1))
    for i in range(june_idx, n):
        aapl_shares[i] = 23.0

    # MSFT: 12 shares from March
    msft_shares = [0.0] * n
    march_idx = next(i for i, d in enumerate(dates) if d >= date(2023, 3, 1))
    for i in range(march_idx, n):
        msft_shares[i] = 12.0

    return pd.DataFrame({"AAPL": aapl_shares, "MSFT": msft_shares}, index=dates)


@pytest.fixture
def sample_portfolio_value_series(sample_holdings_df, sample_prices_df):
    """Series with portfolio values."""
    holdings = sample_holdings_df
    prices = sample_prices_df[["AAPL", "MSFT"]]
    portfolio_value = (holdings * prices).sum(axis=1)
    portfolio_value.name = "portfolio_value"
    return portfolio_value


@pytest.fixture
def sample_current_holdings_df():
    """DataFrame with current holdings snapshot."""
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT"],
            "shares": [23.0, 12.0],
            "current_price": [185.50, 375.25],
            "position_value": [4266.50, 4503.00],
            "portfolio_pct": [48.65, 51.35],
        }
    )


@pytest.fixture
def sample_metrics():
    """Sample metrics dictionary."""
    return {
        "total_contributions": 6500.0,
        "total_withdrawals": 0.0,
        "net_contributions": 6500.0,
        "current_value": 8769.50,
        "gain_loss": 2269.50,
        "gain_loss_pct": 34.92,
        "years_elapsed": 0.99,
        "first_transaction_date": date(2023, 1, 3),
        "end_date": date(2023, 12, 29),
        "simple_annualized_return": 35.27,
        "cagr": 35.27,
    }


@pytest.fixture
def sample_metrics_with_benchmark(sample_metrics):
    """Sample metrics with benchmark data."""
    metrics = sample_metrics.copy()
    metrics.update(
        {
            "benchmark_return": 24.5,
            "benchmark_cagr": 24.5,
            "alpha": 10.77,
            "benchmark_name": "SPY",
        }
    )
    return metrics


@pytest.fixture
def temp_csv(tmp_path):
    """Create a function to generate temporary CSV files."""

    def _create_csv(content: str, filename: str = "test.csv"):
        csv_path = tmp_path / filename
        csv_path.write_text(content)
        return csv_path

    return _create_csv


@pytest.fixture
def valid_csv_content():
    """Valid CSV content for testing."""
    return """date,ticker,amount,type
2023-01-03,AAPL,2000,buy
2023-03-01,MSFT,3000,buy
2023-06-01,AAPL,1500,buy"""


@pytest.fixture
def mock_yfinance_data():
    """Mock yfinance download response."""
    dates = pd.date_range(start="2023-01-03", end="2023-12-29", freq="B")

    import numpy as np

    np.random.seed(42)
    n = len(dates)

    data = pd.DataFrame(
        {
            ("Close", "AAPL"): 130.0 * (1 + np.cumsum(np.random.randn(n) * 0.01)),
            ("Close", "MSFT"): 250.0 * (1 + np.cumsum(np.random.randn(n) * 0.012)),
            ("Close", "SPY"): 400.0 * (1 + np.cumsum(np.random.randn(n) * 0.008)),
            ("Open", "AAPL"): 129.5 * (1 + np.cumsum(np.random.randn(n) * 0.01)),
            ("Open", "MSFT"): 249.5 * (1 + np.cumsum(np.random.randn(n) * 0.012)),
            ("Open", "SPY"): 399.5 * (1 + np.cumsum(np.random.randn(n) * 0.008)),
        },
        index=dates,
    )
    data.columns = pd.MultiIndex.from_tuples(data.columns)
    return data


@pytest.fixture
def mock_yfinance_single_ticker():
    """Mock yfinance download response for single ticker."""
    dates = pd.date_range(start="2023-01-03", end="2023-12-29", freq="B")

    import numpy as np

    np.random.seed(42)
    n = len(dates)

    data = pd.DataFrame(
        {
            "Close": 130.0 * (1 + np.cumsum(np.random.randn(n) * 0.01)),
            "Open": 129.5 * (1 + np.cumsum(np.random.randn(n) * 0.01)),
        },
        index=dates,
    )
    return data
