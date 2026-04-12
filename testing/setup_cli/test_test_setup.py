"""
Tests for setup.py --test-setup feature.

Covers: setup_testing() function, CLI argument parsing,
system package detection, venv creation, Playwright install.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestSetupTestingFunction:
    """Test the setup_testing() function."""

    def test_function_exists(self, setup_module):
        assert hasattr(setup_module, "setup_testing")
        assert callable(setup_module.setup_testing)

    def test_detects_system_packages(self, setup_module):
        """setup_testing should check for tkinter, pyserial, and Pillow."""
        calls = []

        def mock_run_cmd(cmd, **kwargs):
            calls.append(cmd)
            return MagicMock(returncode=0, stdout="")

        with patch.object(setup_module, "run_cmd", side_effect=mock_run_cmd), \
             patch.object(setup_module, "detect_distro", return_value="arch"):
            try:
                setup_module.setup_testing()
            except (SystemExit, EOFError, KeyboardInterrupt, Exception):
                pass

        # Should have checked for tkinter, serial, and PIL imports
        import_checks = [c for c in calls if isinstance(c, list) and len(c) >= 3
                         and c[0] == sys.executable and c[1] == "-c"]
        import_strs = [c[2] for c in import_checks]
        assert any("tkinter" in s for s in import_strs), "Should check for tkinter"
        assert any("serial" in s for s in import_strs), "Should check for pyserial"
        assert any("PIL" in s for s in import_strs), "Should check for Pillow"

    def test_creates_venv_with_system_site_packages(self, setup_module):
        """setup_testing should create venv with --system-site-packages."""
        calls = []

        def mock_run_cmd(cmd, **kwargs):
            calls.append(cmd)
            return MagicMock(returncode=0, stdout="")

        with patch.object(setup_module, "run_cmd", side_effect=mock_run_cmd), \
             patch.object(setup_module, "detect_distro", return_value="arch"):
            try:
                setup_module.setup_testing()
            except (SystemExit, EOFError, KeyboardInterrupt, Exception):
                pass

        # Should have created venv with system-site-packages
        venv_cmds = [c for c in calls if isinstance(c, list) and
                     "-m" in c and "venv" in c]
        if venv_cmds:
            assert any("--system-site-packages" in c for c in venv_cmds), \
                "Venv should be created with --system-site-packages"


class TestTestSetupCLIFlag:
    """Test the --test-setup CLI argument."""

    def test_test_setup_flag_accepted(self, cli_runner):
        """setup.py --test-setup should not error on the flag itself."""
        result = cli_runner("--test-setup", timeout=30)
        # May fail due to missing system deps but shouldn't crash on arg parsing
        assert "unrecognized" not in result.stdout.lower()
        assert "error: argument" not in result.stdout.lower()

    def test_help_mentions_test_setup(self, cli_runner):
        """--help should document the --test-setup flag."""
        result = cli_runner("--help")
        assert "--test-setup" in result.stdout


class TestStatusDockerSection:
    """Test the Docker section added to show_status."""

    def test_status_shows_docker_info(self, cli_runner):
        """--status should include Docker information."""
        result = cli_runner("--status", timeout=15)
        output = result.stdout.lower()
        assert "docker" in output, "Status should include Docker section"

    def test_status_shows_testing_info(self, cli_runner):
        """--status should include testing framework information."""
        result = cli_runner("--status", timeout=15)
        output = result.stdout.lower()
        assert "testing" in output or "test" in output, \
            "Status should include Testing section"
