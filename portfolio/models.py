"""Data models and type definitions for portfolio backtesting."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import TypeAlias

import pandas as pd


class TransactionType(Enum):
    """Type of portfolio transaction."""

    BUY = "buy"
    SELL = "sell"


@dataclass
class Transaction:
    """Represents a single portfolio transaction."""

    date: date
    ticker: str
    shares: float
    amount: float
    type: TransactionType


# Type aliases for DataFrames
TransactionsDF: TypeAlias = pd.DataFrame  # columns: date, ticker, shares, amount, type
HoldingsDF: TypeAlias = pd.DataFrame  # index: dates, columns: tickers, values: shares
PricesDF: TypeAlias = pd.DataFrame  # index: dates, columns: tickers, values: prices
PortfolioValueSeries: TypeAlias = (
    pd.Series
)  # index: dates, values: total portfolio value
