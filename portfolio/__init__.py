"""Portfolio backtesting package."""

from .data import fetch_prices, load_transactions
from .engine import (
    build_holdings_history,
    calculate_portfolio_value,
    get_benchmark_series,
    get_current_holdings,
    normalize_series,
    process_transactions,
)
from .metrics import calculate_metrics
from .models import (
    HoldingsDF,
    NormalizedSeries,
    PortfolioValueSeries,
    PricesDF,
    Transaction,
    TransactionsDF,
    TransactionType,
)
from .report import generate_pdf_report
from .visualization import (
    create_benchmark_comparison_chart,
    create_holdings_pie_chart,
    create_portfolio_value_chart,
)

__all__ = [
    # Data loading
    "load_transactions",
    "fetch_prices",
    # Engine
    "process_transactions",
    "build_holdings_history",
    "calculate_portfolio_value",
    "get_current_holdings",
    "normalize_series",
    "get_benchmark_series",
    # Metrics
    "calculate_metrics",
    # Visualization
    "create_portfolio_value_chart",
    "create_holdings_pie_chart",
    "create_benchmark_comparison_chart",
    # Report
    "generate_pdf_report",
    # Models
    "Transaction",
    "TransactionType",
    "TransactionsDF",
    "HoldingsDF",
    "PricesDF",
    "PortfolioValueSeries",
    "NormalizedSeries",
]
