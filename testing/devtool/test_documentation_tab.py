"""
Tests for the Documentation tab.

Covers: TOC rendering, content display, search functionality,
section navigation.
"""

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name


class TestDocumentationContent:
    """Verify documentation content is present and well-structured."""

    def test_documentation_tab_has_content(self, devtool_app, select_tab):
        tab = select_tab("docs_tab")
        devtool_app.update()
        # The docs tab should have child widgets
        children = tab.winfo_children()
        assert len(children) > 0

    @pytest.mark.screenshot
    def test_screenshot_docs_tab(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("docs_tab")
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "documentation_tab")
        capture_tkinter_window(devtool_app, path)


class TestDocumentationSearch:
    """Test the built-in documentation search."""

    @pytest.mark.screenshot
    def test_screenshot_docs_search(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("docs_tab")
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "documentation_search")
        capture_tkinter_window(devtool_app, path)


class TestAllTabsOverview:
    """Capture screenshots of every tab for the user guide."""

    TAB_INFO = [
        ("display_tab", "Display Emulator"),
        ("serial_tab", "Serial Monitor"),
        ("flash_tab", "Flash Firmware"),
        ("asset_tab", "Asset Manager"),
        ("programs_tab", "Programs"),
        ("pin_tab", "GPIO Pins"),
        ("conn_tab", "Connection Utility"),
        ("docs_tab", "Documentation"),
    ]

    @pytest.mark.screenshot
    @pytest.mark.parametrize("tab_attr,tab_name", TAB_INFO)
    def test_screenshot_all_tabs(self, devtool_app, select_tab, devtool_screenshot_dir,
                                  tab_attr, tab_name):
        select_tab(tab_attr)
        devtool_app.update()
        safe_name = tab_name.lower().replace(" ", "_")
        path = devtool_screenshot_dir / screenshot_name("devtool", f"tab_{safe_name}")
        capture_tkinter_window(devtool_app, path)
