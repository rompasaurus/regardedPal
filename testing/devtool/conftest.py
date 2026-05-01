"""
DevTool-specific fixtures.

Handles Tkinter app lifecycle:
- Creates a virtual display (Xvfb) if no display is available
- Instantiates DilderDevTool with mocked hardware
- Provides per-test tab selection helpers
- Cleans up after each test
"""

import importlib.util
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()


def _load_devtool_module():
    """Load tools/devtool/devtool.py by file path to avoid collision with
    the testing/devtool/ package that Python finds first.

    Registers it as 'devtool_src' in sys.modules so that
    patch("devtool_src.X") works in tests.
    """
    if "devtool_src" in sys.modules:
        return sys.modules["devtool_src"]
    spec = importlib.util.spec_from_file_location(
        "devtool_src",
        PROJECT_ROOT / "tools" / "devtool" / "devtool.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["devtool_src"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def display_env():
    """Ensure a display and Tkinter are available.

    Skips the entire DevTool test suite if Tkinter can't be imported
    (missing system library) or if no display is available.
    """
    try:
        import tkinter
    except ImportError:
        pytest.skip("Tkinter not available — install tk system package")

    if os.environ.get("DISPLAY"):
        yield os.environ["DISPLAY"]
        return

    try:
        from pyvirtualdisplay import Display
        vdisplay = Display(visible=False, size=(1280, 800))
        vdisplay.start()
        yield os.environ.get("DISPLAY", ":99")
        vdisplay.stop()
    except ImportError:
        pytest.skip("No display available and pyvirtualdisplay not installed")


@pytest.fixture
def mock_serial():
    """Mock pyserial so tests don't need a physical Pico W."""
    mock_port = MagicMock()
    mock_port.device = "/dev/ttyACM0"
    mock_port.vid = 0x2E8A
    mock_port.description = "Raspberry Pi Pico W"

    with patch("serial.tools.list_ports.comports", return_value=[mock_port]), \
         patch("serial.Serial") as mock_serial_cls:
        mock_conn = MagicMock()
        mock_conn.is_open = True
        mock_conn.read.return_value = b""
        mock_conn.in_waiting = 0
        mock_serial_cls.return_value = mock_conn
        mock_serial_cls.return_value.__enter__ = lambda s: mock_conn
        mock_serial_cls.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_serial_cls


@pytest.fixture(scope="session")
def devtool_module(display_env):
    """Load the devtool module once per session.

    Depends on display_env so it inherits the Tkinter-availability skip.
    """
    return _load_devtool_module()


@pytest.fixture
def devtool_app(display_env, mock_serial, tmp_path, devtool_module):
    """Create a DilderDevTool instance with mocked hardware.

    Patches ASSETS_DIR to a temp directory so tests don't pollute the
    real assets folder.
    """
    dt = devtool_module

    # Redirect assets to temp dir
    original_assets = dt.ASSETS_DIR
    dt.ASSETS_DIR = tmp_path / "assets"
    dt.ASSETS_DIR.mkdir()

    app = dt.DilderDevTool()
    app.update_idletasks()
    app.update()

    yield app

    # Teardown
    dt.ASSETS_DIR = original_assets
    try:
        app.destroy()
    except Exception:
        pass


@pytest.fixture
def select_tab(devtool_app):
    """Helper to select a notebook tab by its attribute name on the app."""
    def _select(tab_attr: str):
        tab = getattr(devtool_app, tab_attr)
        devtool_app.notebook.select(tab)
        devtool_app.update_idletasks()
        devtool_app.update()
        return tab
    return _select
