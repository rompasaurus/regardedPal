# Dilder Testing Infrastructure

Comprehensive test suite for the Dilder project tools: **DevTool** (Tkinter GUI), **Setup CLI** (terminal wizard), and the **MkDocs website**.

---

## Quick Start

```bash
# 1. Install dependencies
cd testing
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Run all tests
pytest -v

# 4. Run only screenshot tests
pytest -m screenshot -v

# 5. Generate user guides from screenshots
python3 -m testing.utils.guide_generator
```

---

## Architecture

```
testing/
├── devtool/          # Tkinter GUI tests (pytest + Pillow screenshots)
├── setup_cli/        # CLI wizard tests (pytest + subprocess)
├── website/          # MkDocs site tests (Playwright browser automation)
├── utils/            # Shared utilities
│   ├── screenshot_helper.py   # Unified screenshot capture
│   ├── ansi_renderer.py       # ANSI terminal → styled HTML
│   └── guide_generator.py     # Assemble screenshots into guides
├── guides/           # Generated user guides (markdown + screenshots)
├── reports/          # pytest-html test reports
└── .vscode/          # VSCode debug & test configs
```

### Testing Strategy

| Tool | Framework | Screenshot Method | Hardware |
|------|-----------|-------------------|----------|
| DevTool | pytest + Tkinter | `Pillow.ImageGrab` | Mocked (serial, USB) |
| Setup CLI | pytest + subprocess | ANSI→HTML + Playwright | Mocked (system cmds) |
| Website | pytest-playwright | `page.screenshot()` | MkDocs dev server |

**Why not pure Playwright for everything?** Playwright automates web browsers. DevTool is a Tkinter desktop app and Setup CLI is a terminal program — neither runs in a browser. We use Playwright where it fits (website) and the right tool for each domain.

---

## Prerequisites

- **Python 3.9+**
- **Tkinter** (system package: `tk` on Arch, `python3-tk` on Debian)
- **A display** (X11, Wayland, or Xvfb for headless/CI)
- **MkDocs** (for website tests only — `cd website && python3 dev.py install`)

### Install on Arch / CachyOS

```bash
sudo pacman -S tk python-pip
pip install -r testing/requirements.txt
playwright install chromium
```

### Install on Ubuntu / Debian

```bash
sudo apt install python3-tk python3-pip
pip install -r testing/requirements.txt
playwright install chromium --with-deps
```

### Headless (CI / SSH)

For environments without a display:

```bash
pip install pyvirtualdisplay
sudo apt install xvfb  # or: sudo pacman -S xorg-server-xvfb
```

The DevTool test fixtures auto-detect and start Xvfb when no `$DISPLAY` is set.

---

## Running Tests

### By Domain

```bash
# DevTool GUI tests
pytest devtool/ -v

# Setup CLI tests
pytest setup_cli/ -v

# Website tests (requires MkDocs server)
cd ../website && python3 dev.py serve &
cd ../testing && pytest website/ -v
```

### By Marker

```bash
# Only screenshot-capturing tests
pytest -m screenshot -v

# Skip slow tests
pytest -m "not slow" -v

# Skip hardware-dependent tests
pytest -m "not hardware" -v
```

### Single Test File

```bash
pytest devtool/test_display_emulator.py -v
pytest setup_cli/test_cli_navigation.py -v
pytest website/test_navigation.py -v
```

### With HTML Report

```bash
pytest -v --html=reports/report.html --self-contained-html
# Open reports/report.html in a browser to view results
```

---

## VSCode Integration

### Setup

1. Open the project root in VSCode
2. Install the **Python** extension (ms-python.python)
3. Install the **Python Test Explorer** extension (optional, for sidebar test tree)
4. The `.vscode/` configs in `testing/` are auto-detected

### Running Tests from VSCode

- **Test Explorer sidebar**: Click the flask icon in the activity bar to see all discovered tests. Click play to run individual tests or entire suites.
- **Debug configurations**: Open the Run and Debug panel (Ctrl+Shift+D) and select from:
  - `Run All Tests`
  - `Run DevTool Tests`
  - `Run Setup CLI Tests`
  - `Run Website Tests`
  - `Run Screenshot Tests Only`
  - `Run Current Test File`
  - `Generate User Guides`
- **Inline test runner**: Click the green play icon that appears above each `def test_` or `class Test` in the editor.

### Debugging a Failing Test

1. Set a breakpoint in the test file
2. Right-click the test function → "Debug Test"
3. The debugger pauses at your breakpoint with full variable inspection

---

## Screenshot Pipeline

### How It Works

1. Tests marked with `@pytest.mark.screenshot` capture screenshots as a side effect
2. **DevTool**: Pillow's `ImageGrab.grab()` captures the Tkinter window region
3. **Website**: Playwright's `page.screenshot()` captures the browser viewport
4. **Setup CLI**: ANSI output is rendered as styled HTML, then screenshotted by Playwright
5. All screenshots are saved to `{domain}/screenshots/` with descriptive filenames

### Naming Convention

Screenshots follow the pattern: `{domain}_{feature}_{detail}.png`

Examples:
- `devtool_display_pencil_tool.png`
- `devtool_serial_connected.png`
- `website_home_desktop.png`
- `website_docs_devtool.png`

### Generating User Guides

After running screenshot tests:

```bash
python3 -m testing.utils.guide_generator
```

This creates markdown files in `testing/guides/`:
- `devtool_guide.md` — DevTool user guide with all tab screenshots
- `setup_cli_guide.md` — Setup CLI walkthrough with terminal screenshots
- `website_guide.md` — Website documentation with responsive screenshots

### Publishing to the Website

Copy generated guides into the website docs:

```bash
cp testing/guides/devtool_guide.md website/docs/docs/tools/devtool-guide.md
cp testing/guides/setup_cli_guide.md website/docs/docs/tools/setup-cli-guide.md
# Copy screenshot images too
cp testing/devtool/screenshots/*.png website/docs/assets/screenshots/devtool/
cp testing/website/screenshots/*.png website/docs/assets/screenshots/website/
```

Then add the guides to `website/mkdocs.yml` navigation.

---

## Test Report & Documentation Guidelines

### Test Naming

- Test files: `test_{feature}.py`
- Test classes: `Test{Feature}{Aspect}` (e.g., `TestDrawingTools`, `TestSerialConnection`)
- Test methods: `test_{what_it_verifies}` (e.g., `test_pencil_draws_black_pixel`)

### Writing New Tests

1. **Place** the test in the appropriate domain directory
2. **Import** fixtures from conftest (they handle app lifecycle and mocking)
3. **Add screenshots** with `@pytest.mark.screenshot` for any visual state worth documenting
4. **Use descriptive names** — the test name becomes the screenshot description if no override exists

### Screenshot Test Template

```python
@pytest.mark.screenshot
def test_screenshot_my_feature(self, devtool_app, select_tab, devtool_screenshot_dir):
    tab = select_tab("display_tab")
    # Set up the UI state you want to capture
    tab._draw_rect(10, 10, 100, 80, fill=True)
    tab._redraw_from_buffer()
    devtool_app.update()
    # Capture
    path = devtool_screenshot_dir / screenshot_name("devtool", "my_feature")
    capture_tkinter_window(devtool_app, path)
```

### Report Review

After a test run, review:
1. `reports/report.html` — HTML test report with pass/fail status
2. `devtool/screenshots/` — Visual verification of DevTool states
3. `setup_cli/screenshots/` — CLI output captures
4. `website/screenshots/` — Site appearance at multiple viewports

---

## Markers Reference

| Marker | Description |
|--------|-------------|
| `screenshot` | Test captures screenshots for user guides |
| `slow` | Test takes more than 10 seconds |
| `hardware` | Requires physical Pico W hardware (skipped by default) |
| `website` | Requires running MkDocs dev server |

---

## Troubleshooting

### "No display available"

The DevTool tests need a graphical display (X11/Wayland). On headless systems:
```bash
pip install pyvirtualdisplay
sudo pacman -S xorg-server-xvfb  # or: sudo apt install xvfb
```

### "mkdocs not installed"

Website tests need MkDocs Material:
```bash
cd website && python3 dev.py install
```

### "playwright not found"

```bash
pip install pytest-playwright playwright
playwright install chromium
```

### Tests hang on serial

The DevTool tests mock all serial communication. If a test hangs, it's likely a `root.update()` loop issue — check that you're calling `devtool_app.update()` between UI actions.
