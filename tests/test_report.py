"""Tests for portfolio.report module."""

from datetime import date

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from portfolio.report import generate_pdf_report


class TestGeneratePdfReport:
    """Tests for generate_pdf_report function."""

    def test_generate_pdf_report(self, tmp_path, sample_metrics):
        """Generate PDF report and verify file is created."""
        output_path = tmp_path / "test_report.pdf"

        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        holdings = pd.DataFrame(
            {
                "ticker": ["AAPL"],
                "shares": [10.0],
                "current_price": [150.0],
                "position_value": [1500.0],
                "portfolio_pct": [100.0],
            }
        )

        # Create simple chart figures
        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 2, 3])
        fig2, ax2 = plt.subplots()
        ax2.pie([50, 50])

        generate_pdf_report(
            output_path,
            sample_metrics,
            transactions,
            holdings,
            fig1,
            fig2,
        )

        assert output_path.exists()
        # PDF should have some content
        assert output_path.stat().st_size > 0

    def test_generate_pdf_report_with_benchmark(
        self, tmp_path, sample_metrics_with_benchmark
    ):
        """Generate PDF report with benchmark comparison chart."""
        output_path = tmp_path / "test_report_benchmark.pdf"

        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        holdings = pd.DataFrame(
            {
                "ticker": ["AAPL"],
                "shares": [10.0],
                "current_price": [150.0],
                "position_value": [1500.0],
                "portfolio_pct": [100.0],
            }
        )

        # Create chart figures
        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 2, 3])
        fig2, ax2 = plt.subplots()
        ax2.pie([50, 50])
        fig3, ax3 = plt.subplots()
        ax3.plot([1, 2, 3], [1, 2, 3])

        generate_pdf_report(
            output_path,
            sample_metrics_with_benchmark,
            transactions,
            holdings,
            fig1,
            fig2,
            benchmark_comparison_chart=fig3,
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_generate_pdf_report_without_benchmark(self, tmp_path, sample_metrics):
        """Generate PDF report without benchmark section."""
        output_path = tmp_path / "test_report_no_benchmark.pdf"

        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3)],
                "ticker": ["AAPL"],
                "amount": [1000.0],
                "type": ["buy"],
                "shares": [10.0],
            }
        )
        holdings = pd.DataFrame(
            {
                "ticker": ["AAPL"],
                "shares": [10.0],
                "current_price": [150.0],
                "position_value": [1500.0],
                "portfolio_pct": [100.0],
            }
        )

        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 2, 3])
        fig2, ax2 = plt.subplots()
        ax2.pie([50, 50])

        # No benchmark_comparison_chart provided
        generate_pdf_report(
            output_path,
            sample_metrics,
            transactions,
            holdings,
            fig1,
            fig2,
        )

        assert output_path.exists()

    def test_generate_pdf_report_empty_holdings(self, tmp_path, sample_metrics):
        """Generate PDF report with empty holdings."""
        output_path = tmp_path / "test_report_empty.pdf"

        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 6, 1)],
                "ticker": ["AAPL", "AAPL"],
                "amount": [1000.0, 1000.0],
                "type": ["buy", "sell"],
                "shares": [10.0, -10.0],
            }
        )
        # Empty holdings (all sold)
        holdings = pd.DataFrame(
            columns=[
                "ticker",
                "shares",
                "current_price",
                "position_value",
                "portfolio_pct",
            ]
        )

        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 2, 3])
        fig2, ax2 = plt.subplots()
        ax2.text(0.5, 0.5, "No holdings")

        generate_pdf_report(
            output_path,
            sample_metrics,
            transactions,
            holdings,
            fig1,
            fig2,
        )

        assert output_path.exists()

    def test_generate_pdf_report_with_withdrawals(self, tmp_path):
        """Generate PDF report showing withdrawals section."""
        output_path = tmp_path / "test_report_withdrawals.pdf"

        metrics = {
            "total_contributions": 2000.0,
            "total_withdrawals": 500.0,
            "net_contributions": 1500.0,
            "current_value": 1800.0,
            "gain_loss": 300.0,
            "gain_loss_pct": 20.0,
            "years_elapsed": 1.0,
            "first_transaction_date": date(2023, 1, 3),
            "end_date": date(2023, 12, 29),
            "simple_annualized_return": 20.0,
            "cagr": 20.0,
        }

        transactions = pd.DataFrame(
            {
                "date": [date(2023, 1, 3), date(2023, 6, 1)],
                "ticker": ["AAPL", "AAPL"],
                "amount": [2000.0, 500.0],
                "type": ["buy", "sell"],
                "shares": [20.0, -5.0],
            }
        )
        holdings = pd.DataFrame(
            {
                "ticker": ["AAPL"],
                "shares": [15.0],
                "current_price": [120.0],
                "position_value": [1800.0],
                "portfolio_pct": [100.0],
            }
        )

        fig1, ax1 = plt.subplots()
        ax1.plot([1, 2, 3], [1, 2, 3])
        fig2, ax2 = plt.subplots()
        ax2.pie([100])

        generate_pdf_report(
            output_path,
            metrics,
            transactions,
            holdings,
            fig1,
            fig2,
        )

        assert output_path.exists()
