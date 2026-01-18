"""Portfolio metrics calculations."""

from datetime import date
from typing import Any

import pandas as pd

from .models import NormalizedSeries, PortfolioValueSeries, TransactionType, TransactionsDF


def calculate_metrics(
    transactions: TransactionsDF,
    portfolio_value: PortfolioValueSeries,
    end_date: date | None = None,
    benchmark_series: NormalizedSeries | None = None,
    benchmark_name: str | None = None,
) -> dict[str, Any]:
    """Calculate portfolio performance metrics.

    Args:
        transactions: DataFrame with transaction history
        portfolio_value: Series with daily portfolio values
        end_date: End date for calculations (defaults to today)
        benchmark_series: Optional normalized benchmark series (indexed to 100)
        benchmark_name: Optional benchmark ticker name

    Returns:
        Dictionary with metrics:
        - total_contributions: sum of buy amounts
        - total_withdrawals: sum of sell amounts (Phase 2)
        - net_contributions: contributions - withdrawals
        - current_value: latest portfolio value
        - gain_loss: absolute gain/loss
        - gain_loss_pct: percentage gain/loss
        - years_elapsed: time since first transaction
        - first_transaction_date: date of first transaction
        - simple_annualized_return: gain_loss_pct / years
        - cagr: compound annual growth rate
        - benchmark_return: total benchmark return % (if benchmark provided)
        - benchmark_cagr: benchmark CAGR (if benchmark provided)
        - alpha: portfolio CAGR minus benchmark CAGR (if benchmark provided)
        - benchmark_name: benchmark ticker name (if benchmark provided)
    """
    if end_date is None:
        end_date = date.today()
    # Calculate contributions and withdrawals
    buys = transactions[transactions["type"] == TransactionType.BUY.value]
    sells = transactions[transactions["type"] == TransactionType.SELL.value]

    total_contributions = buys["amount"].sum()
    total_withdrawals = sells["amount"].sum() if not sells.empty else 0.0
    net_contributions = total_contributions - total_withdrawals

    # Current value
    current_value = portfolio_value.iloc[-1] if not portfolio_value.empty else 0.0

    # Gain/loss
    gain_loss = current_value - net_contributions
    gain_loss_pct = (
        (gain_loss / net_contributions * 100) if net_contributions > 0 else 0.0
    )

    # Time period
    first_transaction_date = transactions["date"].iloc[0]

    if isinstance(first_transaction_date, str):
        from datetime import datetime

        first_transaction_date = datetime.strptime(
            first_transaction_date, "%Y-%m-%d"
        ).date()

    days_elapsed = (end_date - first_transaction_date).days
    years_elapsed = days_elapsed / 365.25

    # Annualized returns
    if years_elapsed > 0 and net_contributions > 0:
        simple_annualized_return = gain_loss_pct / years_elapsed
        # CAGR = (final / initial)^(1/years) - 1
        if current_value > 0:
            cagr = (
                (current_value / net_contributions) ** (1 / years_elapsed) - 1
            ) * 100
        else:
            cagr = 0.0
    else:
        simple_annualized_return = 0.0
        cagr = 0.0

    result = {
        "total_contributions": total_contributions,
        "total_withdrawals": total_withdrawals,
        "net_contributions": net_contributions,
        "current_value": current_value,
        "gain_loss": gain_loss,
        "gain_loss_pct": gain_loss_pct,
        "years_elapsed": years_elapsed,
        "first_transaction_date": first_transaction_date,
        "end_date": end_date,
        "simple_annualized_return": simple_annualized_return,
        "cagr": cagr,
    }

    # Calculate benchmark metrics if provided
    if benchmark_series is not None and not benchmark_series.empty:
        benchmark_start = benchmark_series.iloc[0]
        benchmark_end = benchmark_series.iloc[-1]

        if benchmark_start > 0:
            benchmark_return = ((benchmark_end / benchmark_start) - 1) * 100
            if years_elapsed > 0:
                benchmark_cagr = (
                    (benchmark_end / benchmark_start) ** (1 / years_elapsed) - 1
                ) * 100
            else:
                benchmark_cagr = 0.0
            alpha = cagr - benchmark_cagr
        else:
            benchmark_return = 0.0
            benchmark_cagr = 0.0
            alpha = 0.0

        result["benchmark_return"] = benchmark_return
        result["benchmark_cagr"] = benchmark_cagr
        result["alpha"] = alpha
        result["benchmark_name"] = benchmark_name

    return result
