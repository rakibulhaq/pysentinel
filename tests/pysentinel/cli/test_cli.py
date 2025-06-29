import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import argparse
import sys
from io import StringIO

from pysentinel.cli.cli import (
    main,
    start_scanner_sync,
    start_scanner_async,
    validate_config_file,
)


class TestValidateConfigFile:
    """Test config file validation"""

    def test_valid_config_file(self, tmp_path):
        """Test validation with valid config file"""
        config_file = tmp_path / "config.yml"
        config_file.write_text("test: config")

        result = validate_config_file(str(config_file))
        assert result == str(config_file)

    def test_nonexistent_config_file(self):
        """Test validation with non-existent config file"""
        with pytest.raises(argparse.ArgumentTypeError, match="does not exist"):
            validate_config_file("nonexistent.yml")

    def test_directory_instead_of_file(self, tmp_path):
        """Test validation when path is directory not file"""
        with pytest.raises(argparse.ArgumentTypeError, match="is not a file"):
            validate_config_file(str(tmp_path))


class TestStartScannerSync:
    """Test synchronous scanner startup"""

    @patch("pysentinel.cli.cli.load_config")
    @patch("pysentinel.cli.cli.Scanner")
    def test_start_scanner_sync_success(self, mock_scanner_class, mock_load_config):
        """Test successful synchronous scanner start"""
        mock_config = {"test": "config"}
        mock_load_config.return_value = mock_config
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner

        start_scanner_sync("config.yml")

        mock_load_config.assert_called_once_with("config.yml")
        mock_scanner_class.assert_called_once_with(mock_config)
        mock_scanner.start.assert_called_once()

    @patch("pysentinel.cli.cli.load_config")
    @patch("builtins.print")
    def test_start_scanner_sync_load_config_error(self, mock_print, mock_load_config):
        """Test error during config loading"""
        mock_load_config.side_effect = Exception("Config error")

        with pytest.raises(SystemExit) as exc_info:
            start_scanner_sync("config.yml")

        assert exc_info.value.code == 1
        mock_print.assert_called_with("Error starting scanner: Config error")

    @patch("pysentinel.cli.cli.load_config")
    @patch("pysentinel.cli.cli.Scanner")
    @patch("builtins.print")
    def test_start_scanner_sync_keyboard_interrupt(
        self, mock_print, mock_scanner_class, mock_load_config
    ):
        """Test keyboard interrupt handling"""
        mock_load_config.return_value = {"test": "config"}
        mock_scanner = Mock()
        mock_scanner.start.side_effect = KeyboardInterrupt()
        mock_scanner_class.return_value = mock_scanner

        with pytest.raises(SystemExit) as exc_info:
            start_scanner_sync("config.yml")

        assert exc_info.value.code == 0
        mock_print.assert_called_with("\nScanner stopped by user")


class TestStartScannerAsync:
    """Test asynchronous scanner startup"""

    @patch("pysentinel.cli.cli.load_config")
    @patch("pysentinel.cli.cli.Scanner")
    @pytest.mark.asyncio
    async def test_start_scanner_async_success(
        self, mock_scanner_class, mock_load_config
    ):
        """Test successful asynchronous scanner start"""
        mock_config = {"test": "config"}
        mock_load_config.return_value = mock_config
        mock_scanner = Mock()
        mock_scanner.start_async = AsyncMock()
        mock_scanner_class.return_value = mock_scanner

        await start_scanner_async("config.yml")

        mock_load_config.assert_called_once_with("config.yml")
        mock_scanner_class.assert_called_once_with(mock_config)
        mock_scanner.start_async.assert_called_once()

    @patch("pysentinel.cli.cli.load_config")
    @patch("builtins.print")
    @pytest.mark.asyncio
    async def test_start_scanner_async_load_config_error(
        self, mock_print, mock_load_config
    ):
        """Test error during async config loading"""
        mock_load_config.side_effect = Exception("Config error")

        with pytest.raises(SystemExit) as exc_info:
            await start_scanner_async("config.yml")

        assert exc_info.value.code == 1
        mock_print.assert_called_with("Error starting scanner: Config error")

    @patch("pysentinel.cli.cli.load_config")
    @patch("pysentinel.cli.cli.Scanner")
    @patch("builtins.print")
    @pytest.mark.asyncio
    async def test_start_scanner_async_keyboard_interrupt(
        self, mock_print, mock_scanner_class, mock_load_config
    ):
        """Test keyboard interrupt handling in async mode"""
        mock_load_config.return_value = {"test": "config"}
        mock_scanner = Mock()
        mock_scanner.start_async = AsyncMock(side_effect=KeyboardInterrupt())
        mock_scanner_class.return_value = mock_scanner

        with pytest.raises(SystemExit) as exc_info:
            await start_scanner_async("config.yml")

        assert exc_info.value.code == 0
        mock_print.assert_called_with("\nScanner stopped by user")


class TestMainCLI:
    """Test main CLI function"""

    @patch("pysentinel.cli.cli.start_scanner_sync")
    @patch("sys.argv", ["pysentinel", "config.yml"])
    def test_main_sync_mode(self, mock_start_sync, tmp_path):
        """Test main function in sync mode"""
        config_file = tmp_path / "config.yml"
        config_file.write_text("test: config")

        with patch("sys.argv", ["pysentinel", str(config_file)]):
            main()

        mock_start_sync.assert_called_once_with(str(config_file))

    @patch("pysentinel.cli.cli.asyncio.run")
    @patch("pysentinel.cli.cli.start_scanner_async")
    def test_main_async_mode(self, mock_start_async, mock_asyncio_run, tmp_path):
        """Test main function in async mode"""
        config_file = tmp_path / "config.yml"
        config_file.write_text("test: config")

        with patch("sys.argv", ["pysentinel", str(config_file), "--async"]):
            main()

        mock_asyncio_run.assert_called_once()

    def test_main_help_output(self, capsys):
        """Test help output"""
        with patch("sys.argv", ["pysentinel", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "PySentinel - Threshold-based alerting scanner" in captured.out
        assert "Run synchronously" in captured.out
        assert "Run asynchronously" in captured.out

    def test_main_version_output(self, capsys):
        """Test version output"""
        with patch("sys.argv", ["pysentinel", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "PySentinel CLI 0.1.0" in captured.out

    def test_main_invalid_config_file(self, capsys):
        """Test main with invalid config file"""
        with patch("sys.argv", ["pysentinel", "nonexistent.yml"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 2  # argparse error code
        captured = capsys.readouterr()
        assert "does not exist" in captured.err

    def test_main_no_arguments(self, capsys):
        """Test main with no arguments"""
        with patch("sys.argv", ["pysentinel"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 2  # argparse error code
        captured = capsys.readouterr()
        assert "required" in captured.err.lower()


class TestCLIIntegration:
    """Integration tests for CLI"""

    @patch("pysentinel.cli.cli.load_config")
    @patch("pysentinel.cli.cli.Scanner")
    def test_full_sync_workflow(self, mock_scanner_class, mock_load_config, tmp_path):
        """Test complete synchronous workflow"""
        config_file = tmp_path / "config.yml"
        config_file.write_text("scanner:\n  interval: 10")

        mock_config = {"scanner": {"interval": 10}}
        mock_load_config.return_value = mock_config
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner

        with patch("sys.argv", ["pysentinel", str(config_file)]):
            main()

        mock_load_config.assert_called_once_with(str(config_file))
        mock_scanner_class.assert_called_once_with(mock_config)
        mock_scanner.start.assert_called_once()

    @patch("pysentinel.cli.cli.load_config")
    @patch("pysentinel.cli.cli.Scanner")
    @patch("pysentinel.cli.cli.asyncio.run")
    def test_full_async_workflow(
        self, mock_asyncio_run, mock_scanner_class, mock_load_config, tmp_path
    ):
        """Test complete asynchronous workflow"""
        config_file = tmp_path / "config.yml"
        config_file.write_text("scanner:\n  interval: 10")

        with patch("sys.argv", ["pysentinel", str(config_file), "--async"]):
            main()

        mock_asyncio_run.assert_called_once()
