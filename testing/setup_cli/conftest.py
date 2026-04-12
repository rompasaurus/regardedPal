"""
Setup CLI test fixtures.

Provides mocked system environment for testing the setup wizard
without modifying the actual system (no package installs, no
group membership changes, no SDK cloning).
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def setup_module():
    """Import setup.py as a module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("setup_cli", PROJECT_ROOT / "setup.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mock_system_env():
    """Mock system commands to prevent actual system changes."""
    mocks = {}
    with patch("subprocess.run") as mock_run, \
         patch("subprocess.Popen") as mock_popen, \
         patch("shutil.which") as mock_which:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="mocked output",
            stderr=""
        )
        mock_popen.return_value = MagicMock()
        mock_which.return_value = "/usr/bin/mocked"
        mocks["run"] = mock_run
        mocks["popen"] = mock_popen
        mocks["which"] = mock_which
        yield mocks


@pytest.fixture
def mock_arch_env(mock_system_env):
    """Mock environment to simulate Arch Linux."""
    with patch("builtins.open", create=True) as mock_open:
        mock_open.side_effect = lambda f, *a, **k: (
            MagicMock(read=lambda: "ID=arch\nNAME=\"Arch Linux\"\n",
                      __enter__=lambda s: s,
                      __exit__=MagicMock(return_value=False))
            if str(f) == "/etc/os-release" else open(f, *a, **k)
        )
        yield mock_system_env


@pytest.fixture
def cli_runner():
    """Run setup.py as a subprocess and capture output."""
    import subprocess

    def _run(*args, timeout=10, input_text=None):
        cmd = [sys.executable, str(PROJECT_ROOT / "setup.py")] + list(args)
        env = dict(os.environ)
        env["NO_COLOR"] = "1"  # Disable colour for easier assertion
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
            env=env,
            input=input_text,
        )
        return result

    return _run


@pytest.fixture
def cli_runner_color():
    """Run setup.py as a subprocess preserving ANSI colour codes."""
    import subprocess

    def _run(*args, timeout=10, input_text=None):
        cmd = [sys.executable, str(PROJECT_ROOT / "setup.py")] + list(args)
        env = dict(os.environ)
        env.pop("NO_COLOR", None)
        env["FORCE_COLOR"] = "1"
        # Force the script to think it has a TTY
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            text=True,
            env=env,
            input=input_text,
        )
        return result

    return _run
