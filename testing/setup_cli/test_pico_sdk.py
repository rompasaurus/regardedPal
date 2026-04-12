"""
Tests for Pico SDK setup (Steps 3-4).

Covers: SDK path detection, environment variable setup.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestSDKPathDetection:
    """Test PICO_SDK_PATH detection logic."""

    def test_sdk_path_from_env(self, setup_module):
        with patch.dict(os.environ, {"PICO_SDK_PATH": "/custom/path/pico-sdk"}):
            path = setup_module.get_sdk_path()
        assert str(path) == "/custom/path/pico-sdk"

    def test_sdk_path_default_fallback(self, setup_module):
        with patch.dict(os.environ, {}, clear=True):
            # Remove PICO_SDK_PATH if present
            os.environ.pop("PICO_SDK_PATH", None)
            path = setup_module.get_sdk_path()
        # Should fall back to ~/pico/pico-sdk
        expected = Path.home() / "pico" / "pico-sdk"
        assert path == expected
