"""Command-line interface for portfolio backtesting."""

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

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
from .report import generate_pdf_report
from .visualization import (
    create_benchmark_comparison_chart,
    create_holdings_pie_chart,
    create_portfolio_value_chart,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_date(date_string: str) -> date:
    """Parse a date string in YYYY-MM-DD format with helpful error message."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid date format: '{date_string}'. Use YYYY-MM-DD (e.g., 2024-01-15)."
        )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Backtest portfolio performance based on historical transactions."
    )
    parser.add_argument(
        "--transactions",
        default="transactions.csv",
        help="Path to transactions CSV file (default: transactions.csv)",
    )
    parser.add_argument(
        "--output",
        default="report.pdf",
        help="Path to output PDF report (default: report.pdf)",
    )
    parser.add_argument(
        "--end-date",
        type=parse_date,
        default=None,
        help="End date for backtest in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--benchmark",
        default="SPY",
        help="Benchmark ticker for comparison (default: SPY)",
    )
    parser.add_argument(
        "--no-benchmark",
        action="store_true",
        help="Disable benchmark comparison",
    )
    return parser.parse_args()


def main() -> int:
    """Main entry point for portfolio backtesting."""
    args = parse_args()

    transactions_path = Path(args.transactions)
    output_path = Path(args.output)
    end_date = args.end_date or date.today()
    benchmark_ticker = None if args.no_benchmark else args.benchmark

    # Validate output directory exists
    output_dir = output_path.parent
    if output_dir and str(output_dir) != "." and not output_dir.exists():
        logger.error(f"Output directory does not exist: {output_dir}")
        return 1

    try:
        # Load transactions
        logger.info(f"Loading transactions from {transactions_path}")
        transactions = load_transactions(transactions_path)

        # Get unique tickers and date range
        tickers = transactions["ticker"].unique().tolist()
        start_date = transactions["date"].iloc[0]
        last_transaction_date = transactions["date"].iloc[-1]

        # Validate end date
        if end_date < last_transaction_date:
            raise ValueError(
                f"End date {end_date} must be on or after last transaction date {last_transaction_date}"
            )

        # Include benchmark ticker in price fetch if enabled
        fetch_tickers = tickers.copy()
        if benchmark_ticker and benchmark_ticker not in fetch_tickers:
            fetch_tickers.append(benchmark_ticker)

        # Fetch price data
        logger.info("Fetching price data...")
        prices = fetch_prices(fetch_tickers, start_date, end_date)

        # Process transactions to calculate shares
        logger.info("Processing transactions...")
        transactions = process_transactions(transactions, prices)

        # Build holdings history
        logger.info("Building holdings history...")
        holdings = build_holdings_history(transactions, prices)

        # Calculate portfolio value over time
        logger.info("Calculating portfolio value...")
        portfolio_value = calculate_portfolio_value(holdings, prices)

        # Get current holdings snapshot
        current_holdings = get_current_holdings(holdings, prices)

        # Handle benchmark if enabled
        benchmark_series = None
        benchmark_chart = None
        if benchmark_ticker:
            logger.info(f"Processing benchmark: {benchmark_ticker}")
            benchmark_prices = get_benchmark_series(prices, benchmark_ticker)

            # Normalize both series to 100 starting from first transaction date
            portfolio_indexed = normalize_series(portfolio_value, start_date)
            benchmark_indexed = normalize_series(benchmark_prices, start_date)

            benchmark_series = benchmark_indexed
            benchmark_chart = create_benchmark_comparison_chart(
                portfolio_indexed, benchmark_indexed, benchmark_ticker
            )

        # Calculate performance metrics
        logger.info("Calculating metrics...")
        metrics = calculate_metrics(
            transactions,
            portfolio_value,
            end_date,
            benchmark_series=benchmark_series,
            benchmark_name=benchmark_ticker,
        )

        # Create visualizations
        logger.info("Creating charts...")
        portfolio_chart = create_portfolio_value_chart(portfolio_value)
        holdings_chart = create_holdings_pie_chart(current_holdings)

        # Generate PDF report
        logger.info(f"Generating PDF report: {output_path}")
        generate_pdf_report(
            output_path,
            metrics,
            transactions,
            current_holdings,
            portfolio_chart,
            holdings_chart,
            benchmark_comparison_chart=benchmark_chart,
        )

        logger.info("Backtest completed successfully")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Invalid data: {e}")
        return 1
    except ConnectionError as e:
        logger.error(f"Network error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
