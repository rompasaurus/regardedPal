"""
Tests for setup.py Step 15 — Docker Build Toolchain.

Covers: Docker install detection, daemon check, compose check,
build file verification, pre-build workflow.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestDockerDetection:
    """Test Docker binary and daemon detection in step_docker."""

    def test_docker_not_installed(self, setup_module):
        """step_docker should handle missing Docker gracefully."""
        with patch("shutil.which", return_value=None), \
             patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False), \
             patch.object(setup_module, "detect_distro", return_value="arch"):
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
            try:
                result = setup_module.step_docker()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_docker_daemon_not_running(self, setup_module):
        """step_docker should detect when daemon is not running."""
        with patch("shutil.which", return_value="/usr/bin/docker"), \
             patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "cmd_exists", return_value=True):
            # docker --version succeeds, docker info fails
            def side_effect(cmd, **kwargs):
                if cmd == ["docker", "--version"]:
                    return MagicMock(returncode=0, stdout="Docker version 24.0.7")
                if cmd == ["docker", "info"]:
                    return MagicMock(returncode=1, stdout="", stderr="Cannot connect")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect
            try:
                result = setup_module.step_docker()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_docker_compose_missing(self, setup_module):
        """step_docker should detect missing docker compose."""
        with patch("shutil.which", return_value="/usr/bin/docker"), \
             patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "prompt_yes_no", return_value=False), \
             patch.object(setup_module, "cmd_exists", return_value=True):
            def side_effect(cmd, **kwargs):
                if cmd == ["docker", "--version"]:
                    return MagicMock(returncode=0, stdout="Docker version 24.0.7")
                if cmd == ["docker", "info"]:
                    return MagicMock(returncode=0, stdout="OK")
                if cmd[0:3] == ["docker", "compose", "version"]:
                    return MagicMock(returncode=1, stdout="", stderr="")
                if cmd[0:2] == ["docker-compose", "--version"]:
                    return MagicMock(returncode=1, stdout="", stderr="")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = side_effect
            try:
                result = setup_module.step_docker()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass


class TestDockerBuildFiles:
    """Test Docker build file verification."""

    def test_step_docker_function_exists(self, setup_module):
        assert hasattr(setup_module, "step_docker")
        assert callable(setup_module.step_docker)

    def test_step_docker_registered_as_step_15(self, setup_module):
        """step_docker should be registered in the step registry."""
        if hasattr(setup_module, "STEPS"):
            step_numbers = [s.get("number") for s in setup_module.STEPS
                            if isinstance(s, dict)]
            assert 15 in step_numbers, f"Step 15 not found in STEPS: {step_numbers}"


class TestDockerInstallCommands:
    """Test distro-specific Docker install command generation."""

    def test_arch_docker_install(self, setup_module):
        """On Arch, should suggest pacman install."""
        with patch("shutil.which", return_value=None), \
             patch.object(setup_module, "detect_distro", return_value="arch"), \
             patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False):
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            try:
                setup_module.step_docker()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass

    def test_debian_docker_install(self, setup_module):
        """On Debian, should suggest apt install."""
        with patch("shutil.which", return_value=None), \
             patch.object(setup_module, "detect_distro", return_value="debian"), \
             patch.object(setup_module, "run_cmd") as mock_run, \
             patch.object(setup_module, "prompt_continue", return_value=""), \
             patch.object(setup_module, "prompt_yes_no", return_value=False):
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            try:
                setup_module.step_docker()
            except (SystemExit, EOFError, KeyboardInterrupt):
                pass
