"""Tests for portfolio.cli module and integration tests."""

import argparse
from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest

from portfolio.cli import main, parse_args, parse_date


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_date_valid(self):
        """Parse valid YYYY-MM-DD date string."""
        result = parse_date("2024-01-15")

        assert result == date(2024, 1, 15)

    def test_parse_date_invalid_format(self):
        """Raise error for invalid date format."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid date format"):
            parse_date("01-15-2024")

    def test_parse_date_invalid_value(self):
        """Raise error for invalid date value."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid date format"):
            parse_date("2024-13-01")  # Invalid month

    def test_parse_date_not_a_date(self):
        """Raise error for non-date string."""
        with pytest.raises(argparse.ArgumentTypeError, match="Invalid date format"):
            parse_date("not-a-date")


class TestParseArgs:
    """Tests for parse_args function."""

    def test_parse_args_defaults(self):
        """Default argument values."""
        with patch("sys.argv", ["portfolio"]):
            args = parse_args()

        assert args.transactions == "transactions.csv"
        assert args.output == "report.pdf"
        assert args.end_date is None
        assert args.benchmark == "SPY"
        assert args.no_benchmark is False

    def test_parse_args_custom_transactions(self):
        """Custom transactions file."""
        with patch("sys.argv", ["portfolio", "--transactions", "my_data.csv"]):
            args = parse_args()

        assert args.transactions == "my_data.csv"

    def test_parse_args_custom_output(self):
        """Custom output file."""
        with patch("sys.argv", ["portfolio", "--output", "my_report.pdf"]):
            args = parse_args()

        assert args.output == "my_report.pdf"

    def test_parse_args_custom_benchmark(self):
        """Custom benchmark ticker."""
        with patch("sys.argv", ["portfolio", "--benchmark", "VT"]):
            args = parse_args()

        assert args.benchmark == "VT"

    def test_parse_args_no_benchmark(self):
        """Disable benchmark with flag."""
        with patch("sys.argv", ["portfolio", "--no-benchmark"]):
            args = parse_args()

        assert args.no_benchmark is True

    def test_parse_args_end_date(self):
        """Custom end date."""
        with patch("sys.argv", ["portfolio", "--end-date", "2024-06-15"]):
            args = parse_args()

        assert args.end_date == date(2024, 6, 15)


class TestMain:
    """Tests for main function."""

    def test_main_missing_transactions(self, tmp_path):
        """Exit with code 1 when transactions file is missing."""
        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(tmp_path / "nonexistent.csv"),
                "--output",
                str(tmp_path / "report.pdf"),
            ],
        ):
            exit_code = main()

        assert exit_code == 1

    def test_main_invalid_output_dir(self, tmp_path, temp_csv, valid_csv_content):
        """Exit with code 1 when output directory doesn't exist."""
        csv_path = temp_csv(valid_csv_content)

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(tmp_path / "nonexistent_dir" / "report.pdf"),
            ],
        ):
            exit_code = main()

        assert exit_code == 1


class TestIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow(self, tmp_path, mocker, mock_yfinance_data):
        """End-to-end test with mocked prices."""
        # Create transactions CSV
        csv_content = """date,ticker,amount,type
2023-01-03,AAPL,2000,buy
2023-03-01,MSFT,3000,buy
2023-06-01,AAPL,1500,buy"""
        csv_path = tmp_path / "transactions.csv"
        csv_path.write_text(csv_content)

        output_path = tmp_path / "report.pdf"

        # Mock yfinance
        mocker.patch("portfolio.data.yf.download", return_value=mock_yfinance_data)

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(output_path),
                "--end-date",
                "2023-12-29",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_workflow_with_benchmark(self, tmp_path, mocker, mock_yfinance_data):
        """End-to-end test with benchmark comparison."""
        csv_content = """date,ticker,amount,type
2023-01-03,AAPL,2000,buy
2023-03-01,MSFT,3000,buy"""
        csv_path = tmp_path / "transactions.csv"
        csv_path.write_text(csv_content)

        output_path = tmp_path / "report.pdf"

        mocker.patch("portfolio.data.yf.download", return_value=mock_yfinance_data)

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(output_path),
                "--end-date",
                "2023-12-29",
                "--benchmark",
                "SPY",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_workflow_no_benchmark(self, tmp_path, mocker, mock_yfinance_data):
        """End-to-end test with --no-benchmark flag."""
        csv_content = """date,ticker,amount,type
2023-01-03,AAPL,2000,buy
2023-03-01,MSFT,3000,buy"""
        csv_path = tmp_path / "transactions.csv"
        csv_path.write_text(csv_content)

        output_path = tmp_path / "report.pdf"

        mocker.patch("portfolio.data.yf.download", return_value=mock_yfinance_data)

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(output_path),
                "--end-date",
                "2023-12-29",
                "--no-benchmark",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_workflow_with_sell_transactions(self, tmp_path, mocker, mock_yfinance_data):
        """End-to-end test with buy and sell transactions."""
        csv_content = """date,ticker,amount,type
2023-01-03,AAPL,2000,buy
2023-03-01,MSFT,3000,buy
2023-06-01,AAPL,500,sell"""
        csv_path = tmp_path / "transactions.csv"
        csv_path.write_text(csv_content)

        output_path = tmp_path / "report.pdf"

        mocker.patch("portfolio.data.yf.download", return_value=mock_yfinance_data)

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(output_path),
                "--end-date",
                "2023-12-29",
                "--no-benchmark",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        assert output_path.exists()

    def test_workflow_network_error(self, tmp_path, mocker):
        """Handle network error gracefully."""
        csv_content = """date,ticker,amount,type
2023-01-03,AAPL,2000,buy"""
        csv_path = tmp_path / "transactions.csv"
        csv_path.write_text(csv_content)

        output_path = tmp_path / "report.pdf"

        # Mock network failure
        mocker.patch(
            "portfolio.data.yf.download", side_effect=Exception("Network error")
        )

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(output_path),
            ],
        ):
            exit_code = main()

        assert exit_code == 1
        assert not output_path.exists()

    def test_workflow_invalid_csv(self, tmp_path, mocker):
        """Handle invalid CSV gracefully."""
        csv_content = """date,ticker
2023-01-03,AAPL"""  # Missing required 'amount' column
        csv_path = tmp_path / "transactions.csv"
        csv_path.write_text(csv_content)

        output_path = tmp_path / "report.pdf"

        with patch(
            "sys.argv",
            [
                "portfolio",
                "--transactions",
                str(csv_path),
                "--output",
                str(output_path),
            ],
        ):
            exit_code = main()

        assert exit_code == 1
