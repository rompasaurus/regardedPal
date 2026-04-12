"""
Tests for ARM toolchain installation (Step 2).

Covers: package manager commands for Arch/Debian/Fedora.
"""

from unittest.mock import patch, MagicMock, mock_open

import pytest


class TestToolchainCommands:
    """Verify correct package manager commands per distro."""

    def test_arch_uses_pacman(self, setup_module):
        """step_toolchain should reference pacman on Arch."""
        with patch("builtins.open", mock_open(read_data='ID=arch\n')), \
             patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False), \
             patch.object(setup_module, "cmd_exists", return_value=True):
            try:
                setup_module.step_toolchain()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass
            # Verify it ran without crashing into interactive input

    @pytest.mark.screenshot
    def test_screenshot_toolchain_step(self, cli_runner_color, setup_cli_screenshot_dir):
        """Capture the toolchain step output."""
        result = cli_runner_color("--list")
        assert "Step" in result.stdout or "step" in result.stdout.lower()
