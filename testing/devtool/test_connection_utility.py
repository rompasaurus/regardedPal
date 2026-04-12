"""
Tests for the Connection Utility tab.

Covers: USB/Wi-Fi mode switching, step rendering, check buttons,
live status checks (mocked hardware).
"""

from unittest.mock import patch, MagicMock

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name


class TestModeSelection:
    """Test USB/Wi-Fi mode radio buttons."""

    def test_default_mode_is_usb(self, devtool_app, select_tab):
        tab = select_tab("conn_tab")
        assert tab.mode_var.get() == "usb"

    def test_switch_to_wifi_mode(self, devtool_app, select_tab):
        tab = select_tab("conn_tab")
        tab.mode_var.set("wifi")
        tab._show_mode()
        devtool_app.update()
        assert tab.mode_var.get() == "wifi"

    def test_switch_back_to_usb(self, devtool_app, select_tab):
        tab = select_tab("conn_tab")
        tab.mode_var.set("wifi")
        tab._show_mode()
        tab.mode_var.set("usb")
        tab._show_mode()
        devtool_app.update()
        assert tab.mode_var.get() == "usb"

    @pytest.mark.screenshot
    def test_screenshot_usb_mode(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("conn_tab")
        tab.mode_var.set("usb")
        tab._show_mode()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "connection_usb_mode")
        capture_tkinter_window(devtool_app, path)

    @pytest.mark.screenshot
    def test_screenshot_wifi_mode(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("conn_tab")
        tab.mode_var.set("wifi")
        tab._show_mode()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "connection_wifi_mode")
        capture_tkinter_window(devtool_app, path)


class TestUSBChecks:
    """Test the USB connection diagnostic checks (mocked)."""

    def test_usb_check_labels_exist(self, devtool_app, select_tab):
        tab = select_tab("conn_tab")
        tab.mode_var.set("usb")
        tab._show_mode()
        devtool_app.update()
        # Step labels should exist
        assert hasattr(tab, "usb_step1_label")
        assert hasattr(tab, "usb_step2_label")
        assert hasattr(tab, "usb_step3_label")

    @pytest.mark.screenshot
    def test_screenshot_usb_steps(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("conn_tab")
        tab.mode_var.set("usb")
        tab._show_mode()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "connection_usb_walkthrough")
        capture_tkinter_window(devtool_app, path)
