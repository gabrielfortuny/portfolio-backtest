"""PDF report generation for portfolio backtesting."""

import logging
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

# Use clean modern font
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Helvetica", "Arial", "DejaVu Sans"]


def generate_pdf_report(
    path: Path,
    metrics: dict[str, Any],
    transactions: pd.DataFrame,
    holdings: pd.DataFrame,
    portfolio_value_chart: Figure,
    holdings_pie_chart: Figure,
) -> None:
    """Generate PDF report with metrics and charts."""
    with PdfPages(path) as pdf:
        # Summary page with metrics
        summary_fig = _create_summary_page(metrics)
        pdf.savefig(summary_fig, bbox_inches="tight", pad_inches=0.5)
        plt.close(summary_fig)

        # Transactions table
        transactions_fig = _create_transactions_page(transactions)
        pdf.savefig(transactions_fig, bbox_inches="tight", pad_inches=0.5)
        plt.close(transactions_fig)

        # Holdings table
        holdings_fig = _create_holdings_page(holdings)
        pdf.savefig(holdings_fig, bbox_inches="tight", pad_inches=0.5)
        plt.close(holdings_fig)

        # Portfolio value chart
        pdf.savefig(portfolio_value_chart, bbox_inches="tight", pad_inches=0.5)
        plt.close(portfolio_value_chart)

        # Holdings pie chart
        pdf.savefig(holdings_pie_chart, bbox_inches="tight", pad_inches=0.5)
        plt.close(holdings_pie_chart)

    logger.info(f"PDF report written to {path}")


def _create_summary_page(metrics: dict[str, Any]) -> Figure:
    """Create summary page with portfolio metrics."""
    fig = plt.figure(figsize=(8.5, 6))
    ax = fig.add_subplot(111)
    ax.axis("off")

    # Title
    ax.text(
        0.5,
        0.95,
        "Portfolio Backtest Report",
        fontsize=22,
        fontweight="bold",
        ha="center",
        transform=ax.transAxes,
    )

    # Time period subtitle
    ax.text(
        0.5,
        0.85,
        f"{metrics['first_transaction_date']} to {metrics['end_date']} ({metrics['years_elapsed']:.2f} years)",
        fontsize=11,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )

    # Summary section
    ax.text(
        0.5,
        0.72,
        "Summary",
        fontsize=14,
        fontweight="bold",
        ha="center",
        transform=ax.transAxes,
    )

    # Two-column layout
    left_x, right_x = 0.25, 0.75
    y = 0.62

    # Row 1: Contributions / Final Value
    ax.text(
        left_x,
        y,
        "Total Contributions",
        fontsize=10,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )
    ax.text(
        right_x,
        y,
        "Final Value",
        fontsize=10,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )
    y -= 0.06
    ax.text(
        left_x,
        y,
        f"${metrics['total_contributions']:,.2f}",
        fontsize=13,
        ha="center",
        fontweight="medium",
        transform=ax.transAxes,
    )
    ax.text(
        right_x,
        y,
        f"${metrics['current_value']:,.2f}",
        fontsize=13,
        ha="center",
        fontweight="medium",
        transform=ax.transAxes,
    )
    y -= 0.10

    # Row 2: Withdrawals / Net (if applicable)
    if metrics.get("total_withdrawals", 0) > 0:
        ax.text(
            left_x,
            y,
            "Total Withdrawals",
            fontsize=10,
            ha="center",
            color="#666666",
            transform=ax.transAxes,
        )
        ax.text(
            right_x,
            y,
            "Net Contributions",
            fontsize=10,
            ha="center",
            color="#666666",
            transform=ax.transAxes,
        )
        y -= 0.06
        ax.text(
            left_x,
            y,
            f"${metrics['total_withdrawals']:,.2f}",
            fontsize=13,
            ha="center",
            fontweight="medium",
            transform=ax.transAxes,
        )
        ax.text(
            right_x,
            y,
            f"${metrics['net_contributions']:,.2f}",
            fontsize=13,
            ha="center",
            fontweight="medium",
            transform=ax.transAxes,
        )
        y -= 0.10

    # Row 3: Gain/Loss
    ax.text(
        left_x,
        y,
        "Gain/Loss",
        fontsize=10,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )
    ax.text(
        right_x,
        y,
        "Gain/Loss %",
        fontsize=10,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )
    y -= 0.06
    gain_color = "#10b981" if metrics["gain_loss"] >= 0 else "#ef4444"
    ax.text(
        left_x,
        y,
        f"${metrics['gain_loss']:,.2f}",
        fontsize=13,
        ha="center",
        fontweight="medium",
        color=gain_color,
        transform=ax.transAxes,
    )
    ax.text(
        right_x,
        y,
        f"{metrics['gain_loss_pct']:+.2f}%",
        fontsize=13,
        ha="center",
        fontweight="medium",
        color=gain_color,
        transform=ax.transAxes,
    )
    y -= 0.12

    # Returns section
    ax.text(
        0.5,
        y,
        "Returns",
        fontsize=14,
        fontweight="bold",
        ha="center",
        transform=ax.transAxes,
    )
    y -= 0.10

    ax.text(
        left_x,
        y,
        "Simple Annualized",
        fontsize=10,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )
    ax.text(
        right_x,
        y,
        "CAGR",
        fontsize=10,
        ha="center",
        color="#666666",
        transform=ax.transAxes,
    )
    y -= 0.06
    ax.text(
        left_x,
        y,
        f"{metrics['simple_annualized_return']:+.2f}%",
        fontsize=13,
        ha="center",
        fontweight="medium",
        transform=ax.transAxes,
    )
    ax.text(
        right_x,
        y,
        f"{metrics['cagr']:+.2f}%",
        fontsize=13,
        ha="center",
        fontweight="medium",
        transform=ax.transAxes,
    )

    return fig


def _create_transactions_page(transactions: pd.DataFrame) -> Figure:
    """Create page with transactions table."""
    # Prepare table data
    table_data = []
    for _, row in transactions.iterrows():
        if pd.isna(row["shares"]):
            continue
        tx_type = "Sell" if row["type"] == "sell" else "Buy"
        price = row["amount"] / abs(row["shares"]) if row["shares"] != 0 else 0
        table_data.append(
            [
                str(row["date"]),
                tx_type,
                row["ticker"],
                f"{abs(row['shares']):.2f}",
                f"${price:,.2f}",
                f"${row['amount']:,.2f}",
            ]
        )

    # Size figure based on content
    n_rows = len(table_data) + 1  # +1 for header
    row_height = 0.35
    fig_height = max(4, min(10, 1.5 + n_rows * row_height))

    fig = plt.figure(figsize=(8.5, fig_height))
    ax = fig.add_subplot(111)
    ax.axis("off")

    ax.text(
        0.5,
        0.98,
        "Transactions",
        fontsize=16,
        fontweight="bold",
        ha="center",
        transform=ax.transAxes,
    )

    if table_data:
        table = ax.table(
            cellText=table_data,
            colLabels=["Date", "Type", "Ticker", "Shares", "Price", "Amount"],
            loc="upper center",
            cellLoc="center",
            bbox=[0.02, 0.02, 0.96, 0.90],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.auto_set_column_width(col=list(range(6)))

        # Style header row
        for i in range(6):
            table[(0, i)].set_facecolor("#f1f5f9")
            table[(0, i)].set_text_props(fontweight="bold")

    return fig


def _create_holdings_page(holdings: pd.DataFrame) -> Figure:
    """Create page with holdings table."""
    if holdings.empty:
        fig = plt.figure(figsize=(8.5, 3))
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(
            0.5, 0.5, "No holdings", fontsize=12, ha="center", transform=ax.transAxes
        )
        return fig

    # Prepare table data
    table_data = []
    for _, row in holdings.iterrows():
        table_data.append(
            [
                row["ticker"],
                f"{row['shares']:.2f}",
                f"${row['current_price']:,.2f}",
                f"${row['position_value']:,.2f}",
                f"{row['portfolio_pct']:.1f}%",
            ]
        )

    # Add total row
    total_value = holdings["position_value"].sum()
    table_data.append(["Total", "", "", f"${total_value:,.2f}", "100.0%"])

    # Size figure based on content
    n_rows = len(table_data) + 1  # +1 for header
    row_height = 0.35
    fig_height = max(4, min(10, 1.5 + n_rows * row_height))

    fig = plt.figure(figsize=(8.5, fig_height))
    ax = fig.add_subplot(111)
    ax.axis("off")

    ax.text(
        0.5,
        0.98,
        "Final Holdings",
        fontsize=16,
        fontweight="bold",
        ha="center",
        transform=ax.transAxes,
    )

    table = ax.table(
        cellText=table_data,
        colLabels=["Ticker", "Shares", "Price", "Value", "Weight"],
        loc="upper center",
        cellLoc="center",
        bbox=[0.02, 0.02, 0.96, 0.90],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(5)))

    # Style header row
    for i in range(5):
        table[(0, i)].set_facecolor("#f1f5f9")
        table[(0, i)].set_text_props(fontweight="bold")

    # Style total row
    total_row_idx = len(table_data)
    for i in range(5):
        table[(total_row_idx, i)].set_facecolor("#f1f5f9")
        table[(total_row_idx, i)].set_text_props(fontweight="bold")

    return fig
