"""
Tests for the GPIO Pins tab.

Covers: pin diagram content, display pin assignments, SPI configuration.
"""

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name


class TestPinViewer:
    """Verify the pin diagram renders with correct content."""

    def test_pin_viewer_has_content(self, devtool_app, select_tab):
        tab = select_tab("pin_tab")
        # The pin_text widget is embedded in the tab
        children = tab.winfo_children()
        assert len(children) > 0

    def test_pin_diagram_contains_key_pins(self, devtool_app, select_tab):
        tab = select_tab("pin_tab")
        # Find the Text widget
        for child in tab.winfo_children():
            if hasattr(child, "get"):
                content = child.get("1.0", "end")
                # Check for key pin labels
                assert "GP11" in content, "Should show SPI DIN pin"
                assert "GP10" in content, "Should show SPI CLK pin"
                assert "GP9" in content, "Should show SPI CS pin"
                assert "GP8" in content, "Should show SPI DC pin"
                assert "SPI1" in content, "Should reference SPI1 controller"
                break

    def test_pin_diagram_shows_button_assignments(self, devtool_app, select_tab):
        tab = select_tab("pin_tab")
        for child in tab.winfo_children():
            if hasattr(child, "get"):
                content = child.get("1.0", "end")
                assert "UP" in content
                assert "DOWN" in content
                assert "LEFT" in content
                assert "RIGHT" in content
                assert "CENTER" in content
                break

    @pytest.mark.screenshot
    def test_screenshot_pin_diagram(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("pin_tab")
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "gpio_pin_diagram")
        capture_tkinter_window(devtool_app, path)
