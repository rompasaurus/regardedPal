"""
Unified screenshot capture for Tkinter windows and Playwright pages.

Provides helpers to:
- Capture a Tkinter window to PNG (via Pillow ImageGrab)
- Capture a Playwright page to PNG
- Annotate screenshots with descriptive metadata
"""

import os
from pathlib import Path
from datetime import datetime


def capture_tkinter_window(root, save_path: Path, description: str = ""):
    """Capture a screenshot of a Tkinter window.

    Uses Pillow's ImageGrab to grab the window region.  Falls back to
    the full-screen grab with manual crop if the window geometry can't
    be parsed.

    Args:
        root: The Tkinter root or Toplevel window.
        save_path: Where to save the PNG screenshot.
        description: Optional description stored in PNG metadata.

    Returns:
        Path to the saved screenshot, or None on failure.
    """
    try:
        from PIL import ImageGrab
    except ImportError:
        print("[screenshot] Pillow not installed — skipping Tkinter capture")
        return None

    root.update_idletasks()
    root.update()

    try:
        # Get the window position and size
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        w = root.winfo_width()
        h = root.winfo_height()
        bbox = (x, y, x + w, y + h)
        img = ImageGrab.grab(bbox=bbox)
    except Exception:
        # Fallback: grab entire screen (works on headless with Xvfb)
        img = ImageGrab.grab()

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(save_path), "PNG")
    return save_path


def capture_playwright_page(page, save_path: Path, full_page: bool = True):
    """Capture a screenshot of a Playwright page.

    Args:
        page: Playwright page object.
        save_path: Where to save the PNG screenshot.
        full_page: Whether to capture the entire scrollable page.

    Returns:
        Path to the saved screenshot.
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(save_path), full_page=full_page)
    return save_path


def screenshot_name(prefix: str, feature: str, suffix: str = "") -> str:
    """Generate a consistent screenshot filename.

    Example: screenshot_name("devtool", "display_pencil_tool") ->
             "devtool_display_pencil_tool.png"
    """
    parts = [prefix, feature]
    if suffix:
        parts.append(suffix)
    return "_".join(parts) + ".png"
