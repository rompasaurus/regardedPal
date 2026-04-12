"""
Shared pytest fixtures for the Dilder test suite.

Provides common configuration, paths, and utilities used across
all three test domains (DevTool, Setup CLI, Website).
"""

import os
import sys
from pathlib import Path

import pytest

# ── Ensure project root is importable ──
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "DevTool"))

# ── Paths ──
TESTING_DIR = Path(__file__).parent.resolve()
DEVTOOL_SCREENSHOTS = TESTING_DIR / "devtool" / "screenshots"
SETUP_CLI_SCREENSHOTS = TESTING_DIR / "setup_cli" / "screenshots"
WEBSITE_SCREENSHOTS = TESTING_DIR / "website" / "screenshots"


@pytest.fixture(scope="session")
def project_root():
    """Absolute path to the Dilder project root."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def testing_dir():
    """Absolute path to the testing directory."""
    return TESTING_DIR


@pytest.fixture
def devtool_screenshot_dir():
    """Path to DevTool screenshot output directory."""
    DEVTOOL_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    return DEVTOOL_SCREENSHOTS


@pytest.fixture
def setup_cli_screenshot_dir():
    """Path to Setup CLI screenshot output directory."""
    SETUP_CLI_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    return SETUP_CLI_SCREENSHOTS


@pytest.fixture
def website_screenshot_dir():
    """Path to Website screenshot output directory."""
    WEBSITE_SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    return WEBSITE_SCREENSHOTS


@pytest.fixture
def tmp_assets(tmp_path):
    """Provide a temporary assets directory for tests that save files."""
    assets = tmp_path / "assets"
    assets.mkdir()
    return assets
