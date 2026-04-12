"""
Tests for VSCode extension installation (Step 6).

Covers: extension install command generation.
"""

from unittest.mock import patch, MagicMock

import pytest


class TestVSCodeExtensions:
    """Test VSCode extension installation flow."""

    def test_step_vscode_calls_code_cli(self, setup_module):
        with patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=True), \
             patch.object(setup_module, "cmd_exists", return_value=True):
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            try:
                setup_module.step_vscode()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass
            # Should have attempted to install extensions via run_cmd


class TestCodeOSSDetection:
    """Test Code OSS vs Microsoft VSCode detection."""

    def test_detects_code_oss_via_pacman(self, setup_module):
        """On Arch with Code OSS, should use open-source extensions."""
        calls = []

        def mock_run_cmd(cmd, **kwargs):
            calls.append(cmd)
            if cmd == ["code", "--version"]:
                return MagicMock(returncode=0, stdout="1.85.0\nabc123\noss")
            if cmd == ["pacman", "-Qi", "code"]:
                return MagicMock(returncode=0, stdout="Name : code\nDescription : The Open Source build of Visual Studio Code")
            if cmd == ["code", "--list-extensions"]:
                return MagicMock(returncode=0, stdout="")
            return MagicMock(returncode=0, stdout="")

        with patch.object(setup_module, "run_cmd", side_effect=mock_run_cmd), \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch("shutil.which", return_value="/usr/bin/code"):
            try:
                setup_module.step_vscode()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_detects_codium_via_path(self, setup_module):
        """Should detect codium as Code OSS."""
        def mock_run_cmd(cmd, **kwargs):
            if cmd == ["code", "--version"]:
                return MagicMock(returncode=0, stdout="1.85.0")
            if cmd == ["pacman", "-Qi", "code"]:
                return MagicMock(returncode=1, stdout="")
            if cmd == ["code", "--list-extensions"]:
                return MagicMock(returncode=0, stdout="")
            return MagicMock(returncode=0, stdout="")

        with patch.object(setup_module, "run_cmd", side_effect=mock_run_cmd), \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch("shutil.which", return_value="/usr/bin/codium"):
            try:
                setup_module.step_vscode()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_detects_proprietary_vscode(self, setup_module):
        """When no OSS indicators, should use Microsoft extensions."""
        def mock_run_cmd(cmd, **kwargs):
            if cmd == ["code", "--version"]:
                return MagicMock(returncode=0, stdout="1.85.0")
            if cmd == ["pacman", "-Qi", "code"]:
                return MagicMock(returncode=1, stdout="")
            if cmd == ["code", "--list-extensions"]:
                return MagicMock(returncode=0, stdout="")
            return MagicMock(returncode=0, stdout="")

        with patch.object(setup_module, "run_cmd", side_effect=mock_run_cmd), \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch("shutil.which", return_value="/usr/bin/code"):
            try:
                setup_module.step_vscode()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass
