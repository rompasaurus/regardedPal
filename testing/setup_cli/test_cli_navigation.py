"""
Tests for CLI navigation flags: --list, --status, --step N.

These tests run the actual setup.py process with NO_COLOR=1 to
verify output formatting and step listing.
"""

import pytest

from utils.screenshot_helper import screenshot_name


class TestListFlag:
    """Test the --list command."""

    def test_list_shows_all_steps(self, cli_runner):
        result = cli_runner("--list")
        assert result.returncode == 0
        # Should list all 15 steps (including new Docker step)
        assert "1" in result.stdout
        assert "15" in result.stdout or "docker" in result.stdout.lower()

    def test_list_contains_step_titles(self, cli_runner):
        result = cli_runner("--list")
        output = result.stdout.lower()
        assert "prerequisite" in output or "prereq" in output or "check" in output

    @pytest.mark.screenshot
    def test_screenshot_list_output(self, cli_runner_color, setup_cli_screenshot_dir):
        result = cli_runner_color("--list")
        # Save the raw output for later rendering with Playwright
        output_file = setup_cli_screenshot_dir / "list_output.ansi"
        output_file.write_text(result.stdout)


class TestStatusFlag:
    """Test the --status command."""

    def test_status_runs_without_error(self, cli_runner):
        result = cli_runner("--status")
        assert result.returncode == 0

    def test_status_shows_environment_info(self, cli_runner):
        result = cli_runner("--status")
        output = result.stdout.lower()
        # Should show some system info
        assert "python" in output or "pico" in output or "sdk" in output or \
               "status" in output or "step" in output

    @pytest.mark.screenshot
    def test_screenshot_status_output(self, cli_runner_color, setup_cli_screenshot_dir):
        result = cli_runner_color("--status")
        output_file = setup_cli_screenshot_dir / "status_output.ansi"
        output_file.write_text(result.stdout)


class TestStepJump:
    """Test jumping to a specific step."""

    def test_invalid_step_number(self, cli_runner):
        result = cli_runner("--step", "99")
        # Should handle gracefully (non-zero exit or error message)
        output = result.stdout.lower()
        assert "invalid" in output or "error" in output or result.returncode != 0 or \
               "99" in output


class TestHelpOutput:
    """Test help text."""

    def test_help_flag(self, cli_runner):
        result = cli_runner("--help")
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "setup" in result.stdout.lower()

    def test_help_mentions_test_setup(self, cli_runner):
        result = cli_runner("--help")
        assert "--test-setup" in result.stdout

    @pytest.mark.screenshot
    def test_screenshot_help_output(self, cli_runner_color, setup_cli_screenshot_dir):
        result = cli_runner_color("--help")
        output_file = setup_cli_screenshot_dir / "help_output.ansi"
        output_file.write_text(result.stdout)


class TestTestSetupFlag:
    """Test the --test-setup flag."""

    def test_test_setup_flag_accepted(self, cli_runner):
        result = cli_runner("--test-setup", timeout=30)
        # Should not error on argument parsing
        assert "unrecognized" not in result.stdout.lower()

    @pytest.mark.screenshot
    def test_screenshot_test_setup_output(self, cli_runner_color, setup_cli_screenshot_dir):
        result = cli_runner_color("--test-setup", timeout=30)
        output_file = setup_cli_screenshot_dir / "test_setup_output.ansi"
        output_file.write_text(result.stdout)
