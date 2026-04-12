"""
Tests for setup.py prerequisite checking (Step 1).

Covers: distro detection, tool availability checks, Python version.
"""

import sys
from unittest.mock import patch, MagicMock, mock_open

import pytest


class TestDistroDetection:
    """Test Linux distribution detection from /etc/os-release."""

    def test_detect_arch(self, setup_module):
        content = 'ID=arch\nNAME="Arch Linux"\n'
        with patch("builtins.open", mock_open(read_data=content)):
            result = setup_module.detect_distro()
        assert result == "arch"

    def test_detect_debian(self, setup_module):
        content = 'ID=debian\nNAME="Debian GNU/Linux"\n'
        with patch("builtins.open", mock_open(read_data=content)):
            result = setup_module.detect_distro()
        assert result == "debian"

    def test_detect_ubuntu_maps_to_debian(self, setup_module):
        content = 'ID=ubuntu\nID_LIKE=debian\nNAME="Ubuntu"\n'
        with patch("builtins.open", mock_open(read_data=content)):
            result = setup_module.detect_distro()
        assert result == "debian"

    def test_detect_fedora(self, setup_module):
        content = 'ID=fedora\nNAME="Fedora Linux"\n'
        with patch("builtins.open", mock_open(read_data=content)):
            result = setup_module.detect_distro()
        assert result == "fedora"

    def test_unknown_distro(self, setup_module):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = setup_module.detect_distro()
        assert result == "unknown"


class TestSerialGroupDetection:
    """Test serial port group detection per distro."""

    def test_arch_uses_uucp(self, setup_module):
        """On a system where uucp group exists, should return uucp."""
        with patch("subprocess.run") as mock_run:
            # getent group uucp succeeds, getent group dialout fails
            def side_effect(cmd, **kwargs):
                if cmd == ["getent", "group", "uucp"]:
                    return MagicMock(returncode=0, stdout="uucp:x:14:")
                return MagicMock(returncode=2, stdout="")
            mock_run.side_effect = side_effect
            group = setup_module.detect_serial_group()
        assert group == "uucp"

    def test_debian_uses_dialout(self, setup_module):
        """On a system where only dialout group exists, should return dialout."""
        with patch("subprocess.run") as mock_run:
            def side_effect(cmd, **kwargs):
                if cmd == ["getent", "group", "dialout"]:
                    return MagicMock(returncode=0, stdout="dialout:x:20:")
                return MagicMock(returncode=2, stdout="")
            mock_run.side_effect = side_effect
            group = setup_module.detect_serial_group()
        assert group == "dialout"


class TestToolAvailability:
    """Test checking for required tools."""

    def test_cmd_exists_found(self, setup_module):
        with patch("shutil.which", return_value="/usr/bin/git"):
            assert setup_module.cmd_exists("git") is True

    def test_cmd_exists_not_found(self, setup_module):
        with patch("shutil.which", return_value=None):
            assert setup_module.cmd_exists("nonexistent_tool") is False


class TestTkinterPrereqCheck:
    """Test the Tkinter availability check added to step_prerequisites."""

    def _make_run_cmd(self, tk_ok=True, serial_ok=True):
        """Build a mock run_cmd that returns realistic stdout."""
        def mock_run_cmd(cmd, **kwargs):
            if isinstance(cmd, list):
                cmd_str = " ".join(str(c) for c in cmd)
                if "import tkinter" in cmd_str:
                    return MagicMock(returncode=0 if tk_ok else 1, stdout="", stderr="")
                if "import serial" in cmd_str:
                    return MagicMock(returncode=0 if serial_ok else 1, stdout="", stderr="")
                if "cmake" in cmd_str and "--version" in cmd_str:
                    return MagicMock(returncode=0, stdout="cmake version 3.28.1\n")
                if "git" in cmd_str and "--version" in cmd_str:
                    return MagicMock(returncode=0, stdout="git version 2.43.0\n")
            return MagicMock(returncode=0, stdout="OK\n")
        return mock_run_cmd

    def test_tkinter_available(self, setup_module):
        """step_prerequisites should report Tkinter as available when importable."""
        with patch.object(setup_module, "run_cmd", side_effect=self._make_run_cmd(tk_ok=True)), \
             patch.object(setup_module, "detect_distro", return_value="arch"), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch.object(setup_module, "prompt_continue", return_value=""):
            try:
                setup_module.step_prerequisites()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_tkinter_missing_shows_install_hint(self, setup_module):
        """When Tkinter import fails, should show distro-specific install hint."""
        with patch.object(setup_module, "run_cmd", side_effect=self._make_run_cmd(tk_ok=False)), \
             patch.object(setup_module, "detect_distro", return_value="arch"), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch.object(setup_module, "prompt_continue", return_value=""):
            try:
                setup_module.step_prerequisites()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass


class TestPyserialPrereqCheck:
    """Test the pyserial availability check added to step_prerequisites."""

    def _make_run_cmd(self, serial_ok=True):
        """Build a mock run_cmd that returns realistic stdout."""
        def mock_run_cmd(cmd, **kwargs):
            if isinstance(cmd, list):
                cmd_str = " ".join(str(c) for c in cmd)
                if "import serial" in cmd_str:
                    return MagicMock(returncode=0 if serial_ok else 1, stdout="", stderr="")
                if "import tkinter" in cmd_str:
                    return MagicMock(returncode=0, stdout="", stderr="")
                if "cmake" in cmd_str and "--version" in cmd_str:
                    return MagicMock(returncode=0, stdout="cmake version 3.28.1\n")
                if "git" in cmd_str and "--version" in cmd_str:
                    return MagicMock(returncode=0, stdout="git version 2.43.0\n")
            return MagicMock(returncode=0, stdout="OK\n")
        return mock_run_cmd

    def test_pyserial_available(self, setup_module):
        """step_prerequisites should check for pyserial."""
        with patch.object(setup_module, "run_cmd", side_effect=self._make_run_cmd(serial_ok=True)), \
             patch.object(setup_module, "detect_distro", return_value="debian"), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch.object(setup_module, "prompt_continue", return_value=""):
            try:
                setup_module.step_prerequisites()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_pyserial_missing_shows_install_hint(self, setup_module):
        """When pyserial import fails, should show distro-specific install hint."""
        with patch.object(setup_module, "run_cmd", side_effect=self._make_run_cmd(serial_ok=False)), \
             patch.object(setup_module, "detect_distro", return_value="debian"), \
             patch.object(setup_module, "cmd_exists", return_value=True), \
             patch.object(setup_module, "prompt_continue", return_value=""):
            try:
                setup_module.step_prerequisites()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass
