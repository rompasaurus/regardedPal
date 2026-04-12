"""
Tests for rendering Setup CLI screenshots from ANSI output to PNG.

These tests capture ANSI-colored CLI output and render it through
Playwright as styled HTML terminal screenshots — giving crisp,
consistent PNG screenshots for the user guide.

Covers:
- --help, --list, --status, --test-setup global flags
- All 15 individual step outputs (header + explanation + checks)
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from utils.screenshot_helper import screenshot_name
from utils.ansi_renderer import (
    render_terminal_html,
    save_terminal_screenshot,
    capture_cli_output,
)


# Skip entire module if Playwright is not available
pytest.importorskip("playwright")

SETUP_PY = Path(__file__).parent.parent.parent / "setup.py"

# Step metadata for parametrized screenshot tests
STEPS = [
    (1,  "Check Prerequisites",        "Verifies git, cmake, Python, Tkinter, pyserial"),
    (2,  "Install ARM Toolchain",       "Installs arm-none-eabi-gcc, cmake, ninja via pacman/apt/dnf"),
    (3,  "Clone Pico SDK",             "Clones pico-sdk with submodules to ~/pico/pico-sdk"),
    (4,  "Set PICO_SDK_PATH",          "Appends PICO_SDK_PATH export to shell rc file"),
    (5,  "Serial Port Permissions",     "Adds user to uucp/dialout group for /dev/ttyACM0"),
    (6,  "Install VSCode Extensions",   "Installs C/C++, CMake Tools, Cortex-Debug extensions"),
    (7,  "Build Hello World (Serial)",  "CMake configure + Ninja build for serial hello world"),
    (8,  "Flash Hello World (Serial)",  "BOOTSEL detection and UF2 flash for serial firmware"),
    (9,  "Verify Serial Output",        "Opens serial monitor to confirm Pico W is alive"),
    (10, "Connect the Display",         "Step-by-step HAT attachment instructions with diagrams"),
    (11, "Get Waveshare Library",       "Downloads C display driver and font files"),
    (12, "Build Hello World (Display)", "CMake configure + Ninja build for display hello world"),
    (13, "Flash Hello World (Display)", "BOOTSEL detection and UF2 flash for display firmware"),
    (14, "Verify Display Output",       "Confirms text appears on the e-ink display"),
    (15, "Docker Build Toolchain",      "Installs Docker and pre-builds ARM cross-compilation container"),
]


def _capture_step_output(step_num: int, timeout: int = 12) -> str:
    """Run setup.py --step N, pipe Enter + quit, capture the ANSI output.

    Each step prints a header, explanation, and checks before asking
    for user input. We pipe two newlines (to pass the preamble Enter
    prompt and the step's continue prompt) then 'q' to quit.
    """
    env = dict(os.environ)
    env["FORCE_COLOR"] = "1"
    env.pop("NO_COLOR", None)

    result = subprocess.run(
        [sys.executable, str(SETUP_PY), "--step", str(step_num)],
        input="\n\nq\nq\nq\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        text=True,
        env=env,
    )
    # Strip the preamble (everything before the step header line)
    output = result.stdout
    # Find the step progress bar (e.g. "Step  1/15")
    lines = output.split("\n")
    step_start = 0
    for i, line in enumerate(lines):
        if f"Step" in line and f"/{len(STEPS)}" in line.replace(" ", ""):
            # Found it — include the divider line above it
            step_start = max(0, i - 1)
            break
        # Also match the boxed header
        if f"Step {step_num}" in line and "─" not in line:
            step_start = max(0, i - 2)
            break
    return "\n".join(lines[step_start:])


@pytest.fixture(scope="module")
def browser_context():
    """Create a Playwright browser context for rendering ANSI screenshots."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not available")

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 960, "height": 800})
    yield context
    context.close()
    browser.close()
    pw.stop()


@pytest.fixture
def page(browser_context):
    """Create a fresh page for each test."""
    page = browser_context.new_page()
    yield page
    page.close()


class TestANSItoHTMLRendering:
    """Test the ANSI to HTML conversion pipeline."""

    def test_render_terminal_html_returns_valid_html(self):
        html = render_terminal_html("Hello \033[32mGreen\033[0m World", title="Test")
        assert "<!DOCTYPE html>" in html
        assert "Test" in html

    def test_render_preserves_content(self):
        html = render_terminal_html("Some output text")
        assert "Some output text" in html


class TestCLIGlobalScreenshots:
    """Capture screenshots of global CLI flags for the user guide."""

    @pytest.mark.screenshot
    def test_screenshot_help_output(self, page, setup_cli_screenshot_dir):
        output = capture_cli_output(
            [sys.executable, str(SETUP_PY), "--help"], timeout=10)
        path = setup_cli_screenshot_dir / screenshot_name("setup_cli", "help_rendered")
        save_terminal_screenshot(page, output, path, title="python3 setup.py --help")
        assert path.exists()

    @pytest.mark.screenshot
    def test_screenshot_list_output(self, page, setup_cli_screenshot_dir):
        output = capture_cli_output(
            [sys.executable, str(SETUP_PY), "--list"], timeout=10)
        path = setup_cli_screenshot_dir / screenshot_name("setup_cli", "list_rendered")
        save_terminal_screenshot(page, output, path, title="python3 setup.py --list")
        assert path.exists()

    @pytest.mark.screenshot
    def test_screenshot_status_output(self, page, setup_cli_screenshot_dir):
        output = capture_cli_output(
            [sys.executable, str(SETUP_PY), "--status"], timeout=15)
        path = setup_cli_screenshot_dir / screenshot_name("setup_cli", "status_rendered")
        save_terminal_screenshot(page, output, path, title="python3 setup.py --status")
        assert path.exists()

    @pytest.mark.screenshot
    def test_screenshot_test_setup_output(self, page, setup_cli_screenshot_dir):
        output = capture_cli_output(
            [sys.executable, str(SETUP_PY), "--test-setup"], timeout=30)
        path = setup_cli_screenshot_dir / screenshot_name("setup_cli", "test_setup_rendered")
        save_terminal_screenshot(page, output, path, title="python3 setup.py --test-setup")
        assert path.exists()


class TestStepScreenshots:
    """Capture a screenshot of every setup step for the walkthrough documentation."""

    @pytest.mark.screenshot
    @pytest.mark.parametrize("step_num,step_title,step_desc", STEPS,
                             ids=[f"step_{s[0]:02d}" for s in STEPS])
    def test_screenshot_step(self, page, setup_cli_screenshot_dir,
                              step_num, step_title, step_desc):
        """Capture step N's header, explanation, and initial output."""
        output = _capture_step_output(step_num)
        assert len(output.strip()) > 0, f"Step {step_num} produced no output"

        path = setup_cli_screenshot_dir / screenshot_name(
            "setup_cli", f"step_{step_num:02d}")
        save_terminal_screenshot(
            page, output, path,
            title=f"Step {step_num} — {step_title}")
        assert path.exists()
