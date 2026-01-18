"""Visualization functions for portfolio backtesting."""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from .models import NormalizedSeries, PortfolioValueSeries

# Use clean modern font
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]


def create_portfolio_value_chart(portfolio_value: PortfolioValueSeries) -> Figure:
    """Create a line chart of portfolio value over time.

    Args:
        portfolio_value: Series with dates as index, portfolio value as values.

    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        portfolio_value.index, portfolio_value.values, linewidth=1.5, color="#2563eb"
    )
    ax.fill_between(
        portfolio_value.index,
        portfolio_value.values,
        alpha=0.1,
        color="#2563eb",
    )

    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Portfolio Value ($)", fontsize=11)
    ax.set_title("Portfolio Value Over Time", fontsize=14, fontweight="medium")

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha="right")

    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return fig


def create_holdings_pie_chart(holdings: pd.DataFrame) -> Figure:
    """Create a pie chart of holdings breakdown by position value.

    Args:
        holdings: DataFrame with columns: ticker, shares, current_price,
                  position_value, portfolio_pct

    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    if holdings.empty:
        ax.text(0.5, 0.5, "No holdings", ha="center", va="center", fontsize=14)
        ax.set_title("Holdings Breakdown", fontsize=14, fontweight="medium")
        return fig

    # Sort by position value descending
    holdings_sorted = holdings.sort_values("position_value", ascending=False).copy()

    # Group small holdings (< 3%) into "Other"
    threshold = 3.0
    large_holdings = holdings_sorted[holdings_sorted["portfolio_pct"] >= threshold]
    small_holdings = holdings_sorted[holdings_sorted["portfolio_pct"] < threshold]

    if not small_holdings.empty:
        other_value = small_holdings["position_value"].sum()
        other_pct = small_holdings["portfolio_pct"].sum()
        other_row = pd.DataFrame(
            [
                {
                    "ticker": "Other",
                    "position_value": other_value,
                    "portfolio_pct": other_pct,
                }
            ]
        )
        holdings_display = pd.concat([large_holdings, other_row], ignore_index=True)
    else:
        holdings_display = large_holdings

    # Modern, clean color palette
    colors = [
        "#3b82f6",  # blue
        "#10b981",  # emerald
        "#f59e0b",  # amber
        "#ef4444",  # red
        "#8b5cf6",  # violet
        "#06b6d4",  # cyan
        "#f97316",  # orange
        "#84cc16",  # lime
        "#ec4899",  # pink
        "#6366f1",  # indigo
        "#14b8a6",  # teal
        "#a855f7",  # purple
        "#94a3b8",  # slate (for "Other")
    ]

    labels = holdings_display["ticker"].tolist()

    ax.pie(
        holdings_display["position_value"],
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        counterclock=False,
        colors=colors[: len(holdings_display)],
        textprops={"fontsize": 10},
    )

    ax.set_title("Holdings Breakdown by Value", fontsize=14, fontweight="medium")

    fig.tight_layout()

    return fig


def create_benchmark_comparison_chart(
    portfolio_indexed: NormalizedSeries,
    benchmark_indexed: NormalizedSeries,
    benchmark_name: str,
) -> Figure:
    """Create a line chart comparing portfolio and benchmark performance.

    Both series should be indexed to 100 at the start date.

    Args:
        portfolio_indexed: Normalized portfolio series (base 100).
        benchmark_indexed: Normalized benchmark series (base 100).
        benchmark_name: Name of the benchmark for the legend.

    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Convert from base 100 to percentage returns
    portfolio_returns = portfolio_indexed - 100
    benchmark_returns = benchmark_indexed - 100

    # Portfolio line (blue solid)
    ax.plot(
        portfolio_returns.index,
        portfolio_returns.values,
        linewidth=1.5,
        color="#2563eb",
        label="Portfolio",
    )

    # Benchmark line (green dashed)
    ax.plot(
        benchmark_returns.index,
        benchmark_returns.values,
        linewidth=1.5,
        color="#10b981",
        linestyle="--",
        label=benchmark_name,
    )

    # Reference line at 0%
    ax.axhline(y=0, color="#94a3b8", linestyle=":", linewidth=1, alpha=0.7)

    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Return (%)", fontsize=11)
    ax.set_title(
        f"Portfolio vs {benchmark_name}",
        fontsize=14,
        fontweight="medium",
    )

    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:+.0f}%"))

    ax.legend(loc="upper left")

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha="right")

    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return fig
