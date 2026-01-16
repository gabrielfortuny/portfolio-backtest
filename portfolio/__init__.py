"""Portfolio backtesting package."""

from .cli import main
from .data import fetch_prices, load_transactions
from .engine import (
    build_holdings_history,
    calculate_portfolio_value,
    get_current_holdings,
    process_transactions,
)
from .metrics import calculate_metrics
from .models import (
    HoldingsDF,
    PortfolioValueSeries,
    PricesDF,
    Transaction,
    TransactionsDF,
    TransactionType,
)
from .report import generate_pdf_report
from .visualization import create_holdings_pie_chart, create_portfolio_value_chart

__all__ = [
    # Main entry point
    "main",
    # Data loading
    "load_transactions",
    "fetch_prices",
    # Engine
    "process_transactions",
    "build_holdings_history",
    "calculate_portfolio_value",
    "get_current_holdings",
    # Metrics
    "calculate_metrics",
    # Visualization
    "create_portfolio_value_chart",
    "create_holdings_pie_chart",
    # Report
    "generate_pdf_report",
    # Models
    "Transaction",
    "TransactionType",
    "TransactionsDF",
    "HoldingsDF",
    "PricesDF",
    "PortfolioValueSeries",
]
