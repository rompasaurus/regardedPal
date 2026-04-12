#!/usr/bin/env python3
"""
Dilder testing CLI.

Run with no arguments for the interactive menu.
Pass a command directly to skip the menu (useful for CI/scripts).

Usage:
  python3 test.py                        # interactive menu
  python3 test.py <command> [options]    # direct invocation

Commands:
  install     Install test dependencies + Playwright browsers
  run         Run the full test suite
  devtool     Run DevTool tests only
  setup-cli   Run Setup CLI tests only
  website     Run Website tests only
  screenshots Run only screenshot-capturing tests
  guides      Generate user guides from screenshots
  status      Show test environment and discovered tests
  report      Open the latest HTML test report
  watch       Watch for new/changed test files and re-run
  clean       Remove reports, screenshots, and caches
"""

import argparse
import glob as _glob
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# Terminal / colour helpers (matching project style from dev.py / setup.py)
# ─────────────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

FG_GREEN  = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE   = "\033[34m"
FG_CYAN   = "\033[36m"
FG_RED    = "\033[31m"
FG_WHITE  = "\033[97m"
FG_GREY   = "\033[90m"
FG_MAGENTA = "\033[35m"

NO_COLOUR = bool(os.environ.get("NO_COLOR")) or not sys.stdout.isatty()


def c(text: str, *codes: str) -> str:
    if NO_COLOUR:
        return text
    return "".join(codes) + text + RESET


def icon(sym: str) -> str:
    if platform.system() == "Windows":
        return {"✓": "[OK]", "✗": "[FAIL]", "→": "->",
                "⚙": "[*]",  "⚠": "[!]",   "●": "[.]"}.get(sym, sym)
    return sym


# ─────────────────────────────────────────────────────────────────────────────
# Logging helpers
# ─────────────────────────────────────────────────────────────────────────────

def log_header(title: str) -> None:
    width = 60
    bar = "─" * width
    print()
    print(c(f"┌{bar}┐", FG_BLUE, BOLD))
    print(c(f"│{title.center(width)}│", FG_BLUE, BOLD))
    print(c(f"└{bar}┘", FG_BLUE, BOLD))
    print()


def log_step(msg: str) -> None:
    print(c(f"  {icon('→')} {msg}", FG_CYAN))


def log_ok(msg: str) -> None:
    print(c(f"  {icon('✓')} {msg}", FG_GREEN))


def log_warn(msg: str) -> None:
    print(c(f"  {icon('⚠')} {msg}", FG_YELLOW))


def log_error(msg: str) -> None:
    print(c(f"  {icon('✗')} {msg}", FG_RED, BOLD), file=sys.stderr)


def log_info(msg: str) -> None:
    print(c(f"  {icon('●')} {msg}", FG_GREY))


def log_section(title: str) -> None:
    print()
    print(c(f"  {BOLD}{title}", FG_WHITE))
    print(c(f"  {'─' * len(title)}", FG_GREY))


# ─────────────────────────────────────────────────────────────────────────────
# Spinner
# ─────────────────────────────────────────────────────────────────────────────

class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, label: str) -> None:
        self.label = label
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)

    def _spin(self) -> None:
        i = 0
        while not self._stop.is_set():
            frame = self.FRAMES[i % len(self.FRAMES)]
            if not NO_COLOUR:
                print(f"\r{c(frame, FG_CYAN)}  {self.label} ", end="", flush=True)
            i += 1
            time.sleep(0.08)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *_):
        self._stop.set()
        self._thread.join()
        if not NO_COLOUR:
            print("\r" + " " * (len(self.label) + 6) + "\r", end="")


# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR    = Path(__file__).parent.resolve()
PROJECT_ROOT  = SCRIPT_DIR.parent
WEBSITE_DIR   = PROJECT_ROOT / "website"
REQUIREMENTS  = SCRIPT_DIR / "requirements.txt"
REPORTS_DIR   = SCRIPT_DIR / "reports"
VENV_DIR      = SCRIPT_DIR / ".venv"

IS_WINDOWS = platform.system() == "Windows"
VENV_BIN   = VENV_DIR / ("Scripts" if IS_WINDOWS else "bin")
PYTHON_EXE = VENV_BIN / ("python.exe" if IS_WINDOWS else "python")
PIP_EXE    = VENV_BIN / ("pip.exe"    if IS_WINDOWS else "pip")
PYTEST_EXE = VENV_BIN / ("pytest.exe" if IS_WINDOWS else "pytest")

TEST_DOMAINS = {
    "devtool":   SCRIPT_DIR / "devtool",
    "setup_cli": SCRIPT_DIR / "setup_cli",
    "website":   SCRIPT_DIR / "website",
}

SCREENSHOT_DIRS = {
    "devtool":   SCRIPT_DIR / "devtool" / "screenshots",
    "setup_cli": SCRIPT_DIR / "setup_cli" / "screenshots",
    "website":   SCRIPT_DIR / "website" / "screenshots",
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def run(cmd: list, stream: bool = False, cwd: Optional[Path] = None,
        env: Optional[dict] = None) -> subprocess.CompletedProcess:
    kwargs: dict = dict(cwd=cwd or SCRIPT_DIR)
    if env:
        full_env = dict(os.environ)
        full_env.update(env)
        kwargs["env"] = full_env
    if stream:
        return subprocess.run(cmd, **kwargs)
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def get_python() -> str:
    """Return the venv Python if available, else system Python."""
    if PYTHON_EXE.exists():
        return str(PYTHON_EXE)
    return sys.executable


def get_pytest() -> str:
    """Return the venv pytest if available, else system pytest."""
    if PYTEST_EXE.exists():
        return str(PYTEST_EXE)
    return "pytest"


def python_version_ok() -> bool:
    return sys.version_info >= (3, 9)


def discover_tests() -> dict:
    """Scan test domains and return a map of {domain: [test_files]}."""
    tests = {}
    for domain, path in TEST_DOMAINS.items():
        if path.exists():
            files = sorted(path.glob("test_*.py"))
            tests[domain] = files
    return tests


def count_test_functions(filepath: Path) -> int:
    """Count test functions/methods in a file (fast regex scan)."""
    import re
    try:
        content = filepath.read_text()
        return len(re.findall(r"^\s*def test_", content, re.MULTILINE))
    except (OSError, UnicodeDecodeError):
        return 0


def count_screenshots() -> dict:
    """Count screenshots per domain."""
    counts = {}
    for domain, path in SCREENSHOT_DIRS.items():
        if path.exists():
            counts[domain] = len(list(path.glob("*.png")))
        else:
            counts[domain] = 0
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

def detect_distro() -> str:
    """Detect the Linux distribution family."""
    try:
        with open("/etc/os-release") as f:
            content = f.read().lower()
        if "cachyos" in content or "arch" in content or "manjaro" in content:
            return "arch"
        if "ubuntu" in content or "debian" in content or "mint" in content:
            return "debian"
        if "fedora" in content or "rhel" in content or "centos" in content:
            return "fedora"
    except FileNotFoundError:
        pass
    return "unknown"


def _tkinter_available() -> bool:
    """Check if Tkinter can be imported by the system Python."""
    check = run([sys.executable, "-c", "import tkinter"])
    return check.returncode == 0


def _install_system_package(packages: list, distro: str) -> bool:
    """Install system packages using the distro's package manager.

    Returns True if install succeeded or was skipped (already present).
    """
    if distro == "arch":
        cmd = ["sudo", "pacman", "-S", "--needed", "--noconfirm"] + packages
    elif distro == "debian":
        cmd = ["sudo", "apt", "install", "-y"] + packages
    elif distro == "fedora":
        cmd = ["sudo", "dnf", "install", "-y"] + packages
    else:
        return False

    log_step(f"Running: {' '.join(cmd)}")
    result = run(cmd, stream=True)
    return result.returncode == 0


def cmd_install(args) -> None:
    log_header("Install Test Dependencies")

    distro = detect_distro()
    log_info(f"Detected distro: {distro}")

    # ── 1. Python version ────────────────────────────────────────────────
    ver = platform.python_version()
    if python_version_ok():
        log_ok(f"Python {ver}")
    else:
        log_error(f"Python {ver} — need 3.9+")
        sys.exit(1)

    # ── 2. System packages (Tkinter) ─────────────────────────────────────
    log_section("System Dependencies")

    if _tkinter_available():
        log_ok("Tkinter already available")
    else:
        log_warn("Tkinter not available — required for DevTool tests")

        tk_packages = {
            "arch":   ["tk"],
            "debian": ["python3-tk"],
            "fedora": ["python3-tkinter"],
        }
        pkgs = tk_packages.get(distro)

        if pkgs:
            log_step(f"Installing Tkinter via system package manager ({', '.join(pkgs)})…")
            if _install_system_package(pkgs, distro):
                if _tkinter_available():
                    log_ok("Tkinter installed successfully")
                else:
                    log_warn("Package installed but Tkinter still not importable")
                    log_info("You may need to rebuild your Python or use the system Python")
            else:
                log_warn("System package install failed — try manually:")
                if distro == "arch":
                    log_info("  sudo pacman -S tk")
                elif distro == "debian":
                    log_info("  sudo apt install python3-tk")
                elif distro == "fedora":
                    log_info("  sudo dnf install python3-tkinter")
        else:
            log_warn(f"Unknown distro '{distro}' — install Tkinter manually")
            log_info("  Arch:   sudo pacman -S tk")
            log_info("  Debian: sudo apt install python3-tk")
            log_info("  Fedora: sudo dnf install python3-tkinter")

    # ── 3. Testing venv + pip deps ───────────────────────────────────────
    log_section("Test Framework")

    needs_recreate = False
    if VENV_DIR.exists():
        # Check if the existing venv has --system-site-packages enabled.
        # Without it, Tkinter (a system package) won't be importable inside
        # the venv. The marker is a no-global-site-packages.txt file.
        no_global = VENV_DIR / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "no-global-site-packages.txt"
        if no_global.exists():
            log_warn(".venv exists but lacks system-site-packages (Tkinter won't work)")
            log_step("Recreating .venv with --system-site-packages…")
            shutil.rmtree(VENV_DIR)
            needs_recreate = True
        else:
            log_ok(".venv already exists (system-site-packages enabled)")

    if not VENV_DIR.exists() or needs_recreate:
        log_step("Creating virtual environment…")
        with Spinner("Creating .venv"):
            run([sys.executable, "-m", "venv", "--system-site-packages", str(VENV_DIR)])
        log_ok(f".venv created at {VENV_DIR}")

    log_step("Installing Python test dependencies…")
    result = run([str(PIP_EXE), "install", "-r", str(REQUIREMENTS)], stream=True)
    if result.returncode != 0:
        log_error("pip install failed")
        sys.exit(1)
    log_ok("Python dependencies installed")

    # ── 4. Playwright browser ────────────────────────────────────────────
    log_section("Playwright")

    log_step("Installing Playwright Chromium browser…")
    result = run([str(PYTHON_EXE), "-m", "playwright", "install", "chromium"], stream=True)
    if result.returncode != 0:
        log_warn("Playwright browser install failed — website tests will be skipped")
    else:
        log_ok("Playwright Chromium installed")

    # ── 5. MkDocs (website tests) ────────────────────────────────────────
    log_section("MkDocs (Website Tests)")

    # website/dev.py uses "venv/" (no dot), check both conventions
    website_venv = WEBSITE_DIR / "venv"
    if not website_venv.exists():
        website_venv = WEBSITE_DIR / ".venv"
    website_dev = WEBSITE_DIR / "dev.py"

    if not WEBSITE_DIR.exists():
        log_warn("website/ directory not found — website tests will be skipped")
    elif website_venv.exists() and (website_venv / "bin" / "mkdocs").exists():
        log_ok(f"MkDocs already installed in {website_venv.name}/")
    elif website_dev.exists():
        log_step("Installing MkDocs via website/dev.py install…")
        result = run([sys.executable, str(website_dev), "install"],
                     stream=True, cwd=WEBSITE_DIR)
        if result.returncode == 0:
            log_ok("MkDocs installed")
        else:
            log_warn("MkDocs install failed — website tests will be skipped")
            log_info("  Try manually: cd website && python3 dev.py install")
    else:
        log_warn("website/dev.py not found — install MkDocs manually")
        log_info("  cd website && pip install mkdocs-material")

    # ── 6. Verification ──────────────────────────────────────────────────
    log_section("Verification")

    # Tkinter
    if _tkinter_available():
        log_ok("Tkinter  → DevTool tests enabled")
    else:
        log_warn("Tkinter  → DevTool tests will be SKIPPED")

    # Playwright
    check = run([str(PYTHON_EXE), "-c", "from playwright.sync_api import sync_playwright"])
    if check.returncode == 0:
        log_ok("Playwright → Website tests enabled")
    else:
        log_warn("Playwright → Website tests will be SKIPPED")

    # MkDocs — check both venv/ and .venv/ conventions
    mkdocs_exe = None
    for vdir in (WEBSITE_DIR / "venv", WEBSITE_DIR / ".venv"):
        candidate = vdir / "bin" / "mkdocs"
        if candidate.exists():
            mkdocs_exe = candidate
            break
    if mkdocs_exe:
        log_ok("MkDocs   → Website server available")
    else:
        log_warn("MkDocs   → Website tests will be SKIPPED")

    # Summary
    print()
    log_ok("Setup complete! Run tests with:")
    log_info("  python3 test.py run")
    log_info("  python3 test.py         (interactive menu)")
    print()


def cmd_run(args) -> None:
    log_header("Run Full Test Suite")
    _run_pytest([], args)


def cmd_devtool(args) -> None:
    log_header("Run DevTool Tests")
    _run_pytest(["devtool/"], args)


def cmd_setup_cli(args) -> None:
    log_header("Run Setup CLI Tests")
    _run_pytest(["setup_cli/"], args)


def cmd_website(args) -> None:
    log_header("Run Website Tests")
    _run_pytest(["website/"], args)


def cmd_screenshots(args) -> None:
    log_header("Run Screenshot Tests")
    _run_pytest(["-m", "screenshot"], args)


def _run_pytest(extra_args: list, args) -> None:
    """Run pytest with the given arguments, streaming output."""
    cmd = [get_pytest()]

    # Always verbose
    cmd.append("-v")

    # Add HTML report
    REPORTS_DIR.mkdir(exist_ok=True)
    cmd.extend(["--html", str(REPORTS_DIR / "report.html"), "--self-contained-html"])

    # Verbosity
    if getattr(args, "verbose", False):
        cmd.append("-vv")
        cmd.append("--tb=long")
    else:
        cmd.append("--tb=short")

    # Marker filter
    if getattr(args, "marker", None):
        cmd.extend(["-m", args.marker])

    # Keyword filter
    if getattr(args, "keyword", None):
        cmd.extend(["-k", args.keyword])

    # Specific test file
    if getattr(args, "file", None):
        cmd.append(args.file)

    cmd.extend(extra_args)

    log_step(f"Running: {' '.join(cmd)}")
    print()

    result = run(cmd, stream=True)

    print()
    if result.returncode == 0:
        log_ok("All tests passed!")
    else:
        log_error(f"Tests failed (exit code {result.returncode})")

    # Screenshot summary
    shots = count_screenshots()
    total = sum(shots.values())
    if total > 0:
        log_info(f"Screenshots captured: {total} total")
        for domain, count in shots.items():
            if count > 0:
                log_info(f"  {domain}: {count}")

    # Report
    report_path = REPORTS_DIR / "report.html"
    if report_path.exists():
        log_info(f"HTML report: {report_path}")

    print()


def cmd_guides(args) -> None:
    log_header("Generate User Guides")

    shots = count_screenshots()
    total = sum(shots.values())
    if total == 0:
        log_warn("No screenshots found. Run screenshot tests first:")
        log_info("  python3 test.py screenshots")
        print()
        return

    log_step(f"Found {total} screenshots across {sum(1 for v in shots.values() if v)} domains")
    for domain, count in shots.items():
        if count > 0:
            log_info(f"  {domain}: {count} screenshots")

    log_step("Generating guides…")
    result = run([get_python(), "-m", "testing.utils.guide_generator"], cwd=PROJECT_ROOT)
    if result.returncode == 0:
        log_ok("Guides generated in testing/guides/")
        guides_dir = SCRIPT_DIR / "guides"
        if guides_dir.exists():
            for g in sorted(guides_dir.glob("*.md")):
                log_info(f"  {g.name}")
    else:
        log_error("Guide generation failed")
        if result.stderr:
            print(result.stderr)

    print()


def cmd_status(args) -> None:
    log_header("Dilder Test Status")

    # Environment
    log_section("Environment")
    log_info(f"Testing dir : {SCRIPT_DIR}")
    log_info(f"Python      : {platform.python_version()} ({sys.executable})")
    log_info(f"Platform    : {platform.system()} {platform.release()}")

    # Venv
    log_section("Virtual Environment")
    if VENV_DIR.exists():
        log_ok(f".venv at {VENV_DIR}")
        if PYTEST_EXE.exists():
            result = run([str(PYTEST_EXE), "--version"])
            log_ok(result.stdout.strip() if result.stdout else "pytest installed")
        else:
            log_warn("pytest not installed in .venv")

        # Check playwright
        result = run([str(PYTHON_EXE), "-c",
                      "from playwright.sync_api import sync_playwright; print('OK')"])
        if result.returncode == 0:
            log_ok("Playwright available")
        else:
            log_warn("Playwright not installed")
    else:
        log_warn("No .venv — run: python3 test.py install")

    # Tkinter (check both system and venv Python)
    tkinter_ok = False
    for py in ([str(PYTHON_EXE)] if PYTHON_EXE.exists() else []) + [sys.executable]:
        check = run([py, "-c", "import tkinter"])
        if check.returncode == 0:
            tkinter_ok = True
            break
    if tkinter_ok:
        log_ok("Tkinter available")
    else:
        log_warn("Tkinter not available — run: sudo pacman -S tk")

    # Discovered tests
    log_section("Discovered Tests")
    tests = discover_tests()
    total_files = 0
    total_funcs = 0
    for domain, files in tests.items():
        n_files = len(files)
        n_funcs = sum(count_test_functions(f) for f in files)
        total_files += n_files
        total_funcs += n_funcs
        badge = c(f"{n_files} files, {n_funcs} tests", FG_GREEN if n_funcs > 0 else FG_GREY)
        print(f"  {c(f'{domain:<12}', FG_WHITE)} {badge}")
        for f in files:
            n = count_test_functions(f)
            print(f"    {c(f.name, FG_GREY)}  ({n} tests)")

    print()
    log_ok(f"Total: {total_files} files, {total_funcs} test functions")

    # Screenshots
    log_section("Screenshots")
    shots = count_screenshots()
    total_shots = sum(shots.values())
    if total_shots > 0:
        for domain, count in shots.items():
            status = c(f"{count} screenshots", FG_GREEN) if count > 0 else c("none", FG_GREY)
            print(f"  {c(f'{domain:<12}', FG_WHITE)} {status}")
        log_ok(f"Total: {total_shots} screenshots")
    else:
        log_info("No screenshots yet — run: python3 test.py screenshots")

    # Guides
    log_section("User Guides")
    guides_dir = SCRIPT_DIR / "guides"
    if guides_dir.exists():
        guides = list(guides_dir.glob("*.md"))
        if guides:
            for g in guides:
                size_kb = g.stat().st_size / 1024
                log_ok(f"{g.name} ({size_kb:.1f} KB)")
        else:
            log_info("No guides generated yet — run: python3 test.py guides")
    else:
        log_info("No guides generated yet")

    # Reports
    log_section("Reports")
    report_path = REPORTS_DIR / "report.html"
    if report_path.exists():
        import datetime
        mtime = datetime.datetime.fromtimestamp(report_path.stat().st_mtime)
        size_kb = report_path.stat().st_size / 1024
        log_ok(f"report.html ({size_kb:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M')})")
    else:
        log_info("No reports yet — run tests first")

    print()


def cmd_report(args) -> None:
    log_header("Open Test Report")

    report_path = REPORTS_DIR / "report.html"
    if not report_path.exists():
        log_warn("No report found. Run tests first:")
        log_info("  python3 test.py run")
        print()
        return

    import datetime
    mtime = datetime.datetime.fromtimestamp(report_path.stat().st_mtime)
    log_ok(f"Opening report from {mtime.strftime('%Y-%m-%d %H:%M')}")

    if platform.system() == "Linux":
        subprocess.Popen(["xdg-open", str(report_path)])
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", str(report_path)])
    elif platform.system() == "Windows":
        os.startfile(str(report_path))
    else:
        log_info(f"Open manually: {report_path}")

    print()


def cmd_watch(args) -> None:
    log_header("Watch Mode")
    log_step("Watching for test file changes…")
    log_info("Press Ctrl+C to stop")
    print()

    # Build initial snapshot of test files and their mtimes
    def _snapshot():
        snap = {}
        for domain, path in TEST_DOMAINS.items():
            if path.exists():
                for f in path.glob("test_*.py"):
                    snap[str(f)] = f.stat().st_mtime
                # Also watch conftest
                ct = path / "conftest.py"
                if ct.exists():
                    snap[str(ct)] = ct.stat().st_mtime
        return snap

    prev = _snapshot()
    log_info(f"Tracking {len(prev)} test files across {len(TEST_DOMAINS)} domains")

    try:
        while True:
            time.sleep(1.5)
            curr = _snapshot()

            # Detect new files
            new_files = set(curr.keys()) - set(prev.keys())
            for nf in new_files:
                npath = Path(nf)
                n_tests = count_test_functions(npath)
                log_ok(f"New test file detected: {npath.name} ({n_tests} tests)")

            # Detect changed files
            changed = []
            for f, mtime in curr.items():
                if f in prev and mtime != prev[f]:
                    changed.append(f)

            # Detect deleted files
            deleted = set(prev.keys()) - set(curr.keys())
            for df in deleted:
                log_warn(f"Test file removed: {Path(df).name}")

            if new_files or changed:
                targets = list(new_files) + changed
                names = [Path(t).name for t in targets]
                print()
                log_step(f"Changes detected in: {', '.join(names)}")
                log_step("Re-running affected tests…")
                print()

                # Run just the changed/new files
                cmd = [get_pytest(), "-v", "--tb=short"] + targets
                run(cmd, stream=True)
                print()
                log_info("Watching for changes… (Ctrl+C to stop)")

            prev = curr

    except KeyboardInterrupt:
        print()
        log_ok("Watch mode stopped")
        print()


def cmd_clean(args) -> None:
    log_header("Clean Test Artifacts")

    cleaned = False

    # Reports
    if REPORTS_DIR.exists() and any(REPORTS_DIR.iterdir()):
        count = len(list(REPORTS_DIR.iterdir()))
        log_step(f"Removing {count} report files…")
        shutil.rmtree(REPORTS_DIR)
        REPORTS_DIR.mkdir()
        log_ok("Reports cleaned")
        cleaned = True

    # Screenshots
    for domain, path in SCREENSHOT_DIRS.items():
        if path.exists():
            pngs = list(path.glob("*.png"))
            if pngs:
                log_step(f"Removing {len(pngs)} {domain} screenshots…")
                for p in pngs:
                    p.unlink()
                log_ok(f"{domain} screenshots cleaned")
                cleaned = True

    # Guides
    guides_dir = SCRIPT_DIR / "guides"
    if guides_dir.exists():
        mds = list(guides_dir.glob("*.md"))
        if mds:
            log_step(f"Removing {len(mds)} generated guides…")
            for m in mds:
                m.unlink()
            log_ok("Guides cleaned")
            cleaned = True

    # Pytest cache
    cache_dir = SCRIPT_DIR / ".pytest_cache"
    if cache_dir.exists():
        log_step("Removing .pytest_cache…")
        shutil.rmtree(cache_dir)
        log_ok("Cache cleaned")
        cleaned = True

    # __pycache__ dirs
    for pyc in SCRIPT_DIR.rglob("__pycache__"):
        shutil.rmtree(pyc)
        cleaned = True

    if not cleaned:
        log_info("Nothing to clean")

    print()


# ─────────────────────────────────────────────────────────────────────────────
# Interactive menu
# ─────────────────────────────────────────────────────────────────────────────

try:
    import tty as _tty
    import termios as _termios
    _HAS_TTY = True
except ImportError:
    _HAS_TTY = False

try:
    import msvcrt as _msvcrt
    _HAS_MSVCRT = True
except ImportError:
    _HAS_MSVCRT = False

# ANSI cursor codes
_CUP  = "\033[{}A"
_EOS  = "\033[J"
_HIDE = "\033[?25l"
_SHOW = "\033[?25h"

# Key constants
_UP    = b"\x1b[A"
_DOWN  = b"\x1b[B"
_ENTER = (b"\r", b"\n", b" ")
_QUIT  = (b"q", b"Q", b"\x03")


def _read_key() -> bytes:
    """Block until a keypress and return its raw bytes."""
    if _HAS_TTY and sys.stdin.isatty():
        import select as _select
        fd = sys.stdin.fileno()
        old = _termios.tcgetattr(fd)
        try:
            _tty.setraw(fd)
            ch = os.read(fd, 1)
            if ch == b"\x1b":
                r, _, _ = _select.select([fd], [], [], 0.05)
                if r:
                    ch += os.read(fd, 2)
        finally:
            _termios.tcsetattr(fd, _termios.TCSADRAIN, old)
        return ch
    elif _HAS_MSVCRT:
        ch = _msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = _msvcrt.getch()
            if ch2 == b"H": return _UP
            if ch2 == b"P": return _DOWN
            return b"\x00"
        return ch
    else:
        line = sys.stdin.readline().strip().encode()
        return line[:1] if line else b"\n"


# Menu items
_ITEMS = [
    dict(name="install",     desc="Install dependencies + Playwright browsers",
         fn=cmd_install,     args=argparse.Namespace()),
    dict(name="run",         desc="Run the full test suite",
         fn=cmd_run,         args=argparse.Namespace(verbose=False, marker=None, keyword=None, file=None)),
    dict(name="devtool",     desc="Run DevTool GUI tests",
         fn=cmd_devtool,     args=argparse.Namespace(verbose=False, marker=None, keyword=None, file=None)),
    dict(name="setup-cli",   desc="Run Setup CLI tests",
         fn=cmd_setup_cli,   args=argparse.Namespace(verbose=False, marker=None, keyword=None, file=None)),
    dict(name="website",     desc="Run Website / Playwright tests",
         fn=cmd_website,     args=argparse.Namespace(verbose=False, marker=None, keyword=None, file=None)),
    dict(name="screenshots", desc="Capture all screenshots for user guides",
         fn=cmd_screenshots, args=argparse.Namespace(verbose=False, marker=None, keyword=None, file=None)),
    dict(name="guides",      desc="Generate markdown user guides from screenshots",
         fn=cmd_guides,      args=argparse.Namespace()),
    dict(name="watch",       desc="Watch for changes and auto-run affected tests",
         fn=cmd_watch,       args=argparse.Namespace()),
    dict(name="status",      desc="Show test environment, discovered tests, screenshots",
         fn=cmd_status,      args=argparse.Namespace()),
    dict(name="report",      desc="Open the latest HTML test report in browser",
         fn=cmd_report,      args=argparse.Namespace()),
    dict(name="clean",       desc="Remove reports, screenshots, caches",
         fn=cmd_clean,       args=argparse.Namespace()),
    dict(name="quit",        desc="Exit",
         fn=None,            args=None),
]

_MENU_HEIGHT = len(_ITEMS) + 8  # items + header/footer chrome


def _draw_menu(items: list, selected: int) -> None:
    """Print the interactive menu. Always prints exactly _MENU_HEIGHT lines."""

    SEP = c("  " + "─" * 56, FG_GREY)

    # Header
    print()
    print(SEP)
    print()

    # Items
    for i, item in enumerate(items):
        is_sel  = (i == selected)
        is_quit = (item["name"] == "quit")

        if is_sel:
            cursor   = c(" ▶ ", FG_CYAN, BOLD)
            name_str = c(f"{item['name']:<14}", FG_CYAN, BOLD)
            desc_str = c(item["desc"], FG_WHITE)
        elif is_quit:
            cursor   = "   "
            name_str = c(f"{item['name']:<14}", FG_GREY, DIM)
            desc_str = c(item["desc"], FG_GREY, DIM)
        else:
            cursor   = "   "
            name_str = c(f"{item['name']:<14}", FG_WHITE)
            desc_str = c(item["desc"], FG_GREY)

        print(f"  {cursor}{name_str}  {desc_str}")

    # Footer
    print()

    # Status badges
    tests = discover_tests()
    total_tests = sum(count_test_functions(f) for files in tests.values() for f in files)
    shots = count_screenshots()
    total_shots = sum(shots.values())

    venv_badge = c("venv ✓", FG_GREEN) if VENV_DIR.exists() else c("venv ○", FG_YELLOW)
    test_badge = c(f"{total_tests} tests", FG_GREEN) if total_tests > 0 else c("0 tests", FG_GREY)
    shot_badge = c(f"{total_shots} shots", FG_GREEN) if total_shots > 0 else c("0 shots", FG_GREY)

    hints = (
        c("  ↑↓", FG_CYAN) + c(" navigate   ", FG_GREY) +
        c("enter", FG_CYAN) + c(" run   ", FG_GREY) +
        c("q", FG_CYAN) + c(" quit", FG_GREY)
    )

    print(f"  {venv_badge}  {test_badge}  {shot_badge}")
    print(hints)
    print(SEP)
    print()


def interactive_menu() -> None:
    """Arrow-key navigable interactive menu."""
    selected = 0

    log_header("Dilder Test Runner")

    if not sys.stdout.isatty() or NO_COLOUR:
        # Fallback: numbered list for non-interactive terminals
        for i, item in enumerate(_ITEMS):
            print(f"  [{i + 1}] {item['name']:<14}  {item['desc']}")
        print()
        try:
            choice = input("  Enter number (or q to quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if choice.lower() == "q":
            return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(_ITEMS):
                item = _ITEMS[idx]
                if item["fn"]:
                    item["fn"](item["args"])
        except ValueError:
            log_error(f"Invalid choice: {choice}")
        return

    # Interactive mode
    print(_HIDE, end="", flush=True)
    try:
        _draw_menu(_ITEMS, selected)

        while True:
            key = _read_key()

            if key == _UP:
                selected = (selected - 1) % len(_ITEMS)
            elif key == _DOWN:
                selected = (selected + 1) % len(_ITEMS)
            elif key in _ENTER:
                item = _ITEMS[selected]
                # Clear menu and restore cursor
                print(_CUP.format(_MENU_HEIGHT) + _EOS, end="")
                print(_SHOW, end="", flush=True)
                if item["fn"] is None:
                    return
                item["fn"](item["args"])
                # Redraw menu after command completes
                print(_HIDE, end="", flush=True)
                _draw_menu(_ITEMS, selected)
                continue
            elif key in _QUIT:
                print(_CUP.format(_MENU_HEIGHT) + _EOS, end="")
                print(_SHOW, end="", flush=True)
                return
            else:
                continue

            # Redraw
            print(_CUP.format(_MENU_HEIGHT) + _EOS, end="")
            _draw_menu(_ITEMS, selected)

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        print(_SHOW, end="", flush=True)
        print()


# ─────────────────────────────────────────────────────────────────────────────
# CLI argument parser
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="test.py",
        description="Dilder test runner — interactive CLI for running tests, "
                    "capturing screenshots, and generating user guides.",
    )
    subs = parser.add_subparsers(dest="command")

    # install
    subs.add_parser("install", help="Install dependencies + Playwright browsers")

    # run
    p_run = subs.add_parser("run", help="Run the full test suite")
    p_run.add_argument("-v", "--verbose", action="store_true", help="Extra verbose output")
    p_run.add_argument("-m", "--marker", help="Only run tests matching this marker")
    p_run.add_argument("-k", "--keyword", help="Only run tests matching this keyword expression")
    p_run.add_argument("file", nargs="?", help="Specific test file to run")

    # devtool
    p_dt = subs.add_parser("devtool", help="Run DevTool tests")
    p_dt.add_argument("-v", "--verbose", action="store_true")
    p_dt.add_argument("-k", "--keyword", help="Keyword filter")

    # setup-cli
    p_sc = subs.add_parser("setup-cli", help="Run Setup CLI tests")
    p_sc.add_argument("-v", "--verbose", action="store_true")
    p_sc.add_argument("-k", "--keyword", help="Keyword filter")

    # website
    p_ws = subs.add_parser("website", help="Run Website tests")
    p_ws.add_argument("-v", "--verbose", action="store_true")
    p_ws.add_argument("-k", "--keyword", help="Keyword filter")

    # screenshots
    p_ss = subs.add_parser("screenshots", help="Capture all screenshots")
    p_ss.add_argument("-v", "--verbose", action="store_true")

    # guides
    subs.add_parser("guides", help="Generate user guides from screenshots")

    # status
    subs.add_parser("status", help="Show test environment and discovered tests")

    # report
    subs.add_parser("report", help="Open the latest HTML test report")

    # watch
    subs.add_parser("watch", help="Watch for changes and auto-run tests")

    # clean
    subs.add_parser("clean", help="Remove reports, screenshots, and caches")

    return parser


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

COMMAND_MAP = {
    "install":     cmd_install,
    "run":         cmd_run,
    "devtool":     cmd_devtool,
    "setup-cli":   cmd_setup_cli,
    "setup_cli":   cmd_setup_cli,
    "website":     cmd_website,
    "screenshots": cmd_screenshots,
    "guides":      cmd_guides,
    "status":      cmd_status,
    "report":      cmd_report,
    "watch":       cmd_watch,
    "clean":       cmd_clean,
}


def main():
    if len(sys.argv) < 2:
        interactive_menu()
        return

    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        interactive_menu()
        return

    fn = COMMAND_MAP.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
