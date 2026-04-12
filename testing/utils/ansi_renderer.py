"""
Render ANSI-colored terminal output as styled HTML.

Used to capture Setup CLI output as high-quality screenshots:
1. Run the CLI command and capture ANSI output
2. Convert to styled HTML via ansi2html
3. Screenshot the HTML page with Playwright

This gives us consistent, crisp screenshots of terminal output
that look great in user guides.
"""

import subprocess
import sys
from pathlib import Path

# HTML template wrapping the converted ANSI output in a terminal-like frame
TERMINAL_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{
    margin: 0;
    padding: 20px;
    background: #1e1e2e;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 14px;
  }}
  .terminal {{
    background: #0d0d1a;
    border: 1px solid #3a3a5c;
    border-radius: 8px;
    overflow: hidden;
    max-width: 900px;
    margin: 0 auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
  }}
  .titlebar {{
    background: #282840;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .dot {{
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }}
  .dot.red {{ background: #f38ba8; }}
  .dot.yellow {{ background: #f9e2af; }}
  .dot.green {{ background: #a6e3a1; }}
  .titlebar-text {{
    color: #6c7086;
    font-size: 12px;
    margin-left: auto;
  }}
  .content {{
    padding: 16px;
    color: #cdd6f4;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
  }}
  /* ansi2html default classes */
  .ansi1 {{ font-weight: bold; }}
  .ansi2 {{ opacity: 0.6; }}
  .ansi30 {{ color: #1a1a1a; }}
  .ansi31 {{ color: #f38ba8; }}
  .ansi32 {{ color: #a6e3a1; }}
  .ansi33 {{ color: #f9e2af; }}
  .ansi34 {{ color: #89b4fa; }}
  .ansi35 {{ color: #cba6f7; }}
  .ansi36 {{ color: #94e2d5; }}
  .ansi37 {{ color: #cdd6f4; }}
  .ansi90 {{ color: #6c7086; }}
  .ansi97 {{ color: #ffffff; }}
</style>
</head>
<body>
<div class="terminal">
  <div class="titlebar">
    <div class="dot red"></div>
    <div class="dot yellow"></div>
    <div class="dot green"></div>
    <span class="titlebar-text">{title}</span>
  </div>
  <div class="content">{content}</div>
</div>
</body>
</html>
"""


def ansi_to_html(ansi_text: str) -> str:
    """Convert ANSI escape sequences to HTML spans.

    Uses ansi2html if available, otherwise falls back to a basic
    regex-based converter that handles the most common codes.
    """
    try:
        from ansi2html import Ansi2HTMLConverter
        conv = Ansi2HTMLConverter(inline=False, scheme="osx")
        return conv.convert(ansi_text, full=False)
    except ImportError:
        # Basic fallback: strip ANSI codes
        import re
        return re.sub(r"\033\[[0-9;]*m", "", ansi_text)


def render_terminal_html(ansi_text: str, title: str = "Terminal") -> str:
    """Wrap ANSI-converted text in a terminal-styled HTML page."""
    html_content = ansi_to_html(ansi_text)
    return TERMINAL_TEMPLATE.format(title=title, content=html_content)


def capture_cli_output(cmd: list, timeout: int = 30, env: dict = None) -> str:
    """Run a CLI command and return its combined stdout+stderr with ANSI codes.

    Args:
        cmd: Command and arguments as a list.
        timeout: Maximum seconds to wait.
        env: Optional environment overrides.

    Returns:
        Combined output string (may contain ANSI escape sequences).
    """
    run_env = dict(**__import__("os").environ)
    if env:
        run_env.update(env)
    # Force colour output even though we're not a TTY
    run_env["FORCE_COLOR"] = "1"
    run_env.pop("NO_COLOR", None)

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=run_env,
        text=True,
    )
    return result.stdout


def save_terminal_screenshot(page, ansi_text: str, save_path: Path,
                             title: str = "Terminal"):
    """Render ANSI output as HTML and screenshot it with Playwright.

    Args:
        page: Playwright page object.
        ansi_text: Raw ANSI terminal output.
        save_path: Where to save the PNG.
        title: Title shown in the terminal titlebar.

    Returns:
        Path to the saved screenshot.
    """
    html = render_terminal_html(ansi_text, title=title)
    page.set_content(html)
    page.wait_for_timeout(500)  # Let CSS render
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(save_path), full_page=True)
    return save_path
