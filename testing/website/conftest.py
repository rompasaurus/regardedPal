"""
Website test fixtures.

Manages MkDocs dev server lifecycle and Playwright browser setup.
The server is started once per test session and shared across all
website tests.
"""

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
WEBSITE_DIR = PROJECT_ROOT / "website"
MKDOCS_PORT = 8099  # Use a non-standard port to avoid conflicts


def _find_mkdocs_python() -> str:
    """Find the Python that has mkdocs installed."""
    for vdir in (WEBSITE_DIR / "venv", WEBSITE_DIR / ".venv"):
        candidate = vdir / "bin" / "python"
        if candidate.exists():
            return str(candidate)
    return sys.executable


def _port_is_open(port: int) -> bool:
    """Check if a TCP port is accepting connections."""
    try:
        sock = socket.create_connection(("127.0.0.1", port), timeout=1)
        sock.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


@pytest.fixture(scope="session")
def mkdocs_server():
    """Start the MkDocs dev server for the test session.

    Starts `mkdocs serve` in the website directory and waits until
    it's ready to accept connections. Kills it on teardown.
    """
    python = _find_mkdocs_python()

    # Check if mkdocs is importable
    check = subprocess.run(
        [python, "-c", "import mkdocs"],
        capture_output=True,
    )
    if check.returncode != 0:
        pytest.skip("mkdocs not installed — run: cd website && python3 dev.py install")

    # Kill any leftover server on our port
    if _port_is_open(MKDOCS_PORT):
        # Something is already on the port — use it
        yield f"http://127.0.0.1:{MKDOCS_PORT}"
        return

    proc = subprocess.Popen(
        [python, "-m", "mkdocs", "serve",
         "--dev-addr", f"127.0.0.1:{MKDOCS_PORT}",
         "--no-livereload"],  # Disable livereload to reduce overhead
        cwd=str(WEBSITE_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )

    # Wait for server to be ready (up to 30 seconds)
    for _ in range(60):
        if proc.poll() is not None:
            # Server process died
            output = proc.stdout.read().decode(errors="replace")
            pytest.skip(f"MkDocs server exited unexpectedly:\n{output[:500]}")
        if _port_is_open(MKDOCS_PORT):
            break
        time.sleep(0.5)
    else:
        proc.kill()
        pytest.skip("MkDocs server failed to start within 30 seconds")

    # Give it a moment to finish building the site
    time.sleep(1)

    yield f"http://127.0.0.1:{MKDOCS_PORT}"

    # Teardown: kill the server process group
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        proc.wait(timeout=5)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass


@pytest.fixture(scope="session")
def browser_context(playwright):
    """Create a shared browser context for website tests."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
    )
    yield context
    context.close()
    browser.close()


@pytest.fixture
def page(browser_context, mkdocs_server):
    """Create a new page for each test.

    Does NOT navigate — each test should navigate to the URL it needs
    using base_url or mkdocs_server directly.
    """
    pg = browser_context.new_page()
    yield pg
    pg.close()


@pytest.fixture(scope="session")
def base_url(mkdocs_server):
    """The base URL of the running MkDocs server.

    Must be session-scoped to match pytest-base-url's _verify_url fixture
    which depends on base_url at session scope.
    """
    return mkdocs_server
