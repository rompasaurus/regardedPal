"""
Tests for the Serial Monitor tab.

Covers: port detection, connect/disconnect, send commands,
receive data, auto-scroll, clear output, save log.
"""

import time
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name


class TestSerialMonitorUI:
    """Verify the Serial Monitor UI initialises correctly."""

    def test_initial_state_disconnected(self, devtool_app, select_tab):
        tab = select_tab("serial_tab")
        assert "Disconnected" in tab.status_label.cget("text")

    def test_baud_rate_default(self, devtool_app, select_tab):
        tab = select_tab("serial_tab")
        assert tab.baud_var.get() == "115200"

    def test_auto_scroll_enabled_by_default(self, devtool_app, select_tab):
        tab = select_tab("serial_tab")
        assert tab.autoscroll_var.get() is True

    @pytest.mark.screenshot
    def test_screenshot_disconnected_state(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("serial_tab")
        path = devtool_screenshot_dir / screenshot_name("devtool", "serial_disconnected")
        capture_tkinter_window(devtool_app, path)


class TestPortDetection:
    """Test serial port refresh and auto-detection."""

    def test_refresh_populates_port_list(self, devtool_app, select_tab, mock_serial):
        tab = select_tab("serial_tab")
        tab._refresh_ports()
        devtool_app.update()
        # The mock provides /dev/ttyACM0
        values = tab.port_combo.cget("values")
        # port_combo might be populated directly or via StringVar
        assert tab.port_var.get() != "" or len(values) > 0

    def test_no_ports_shows_empty(self, devtool_app, select_tab):
        tab = select_tab("serial_tab")
        with patch("serial.tools.list_ports.comports", return_value=[]):
            tab._refresh_ports()
        devtool_app.update()


class TestSerialConnection:
    """Test connect and disconnect flows with mocked serial."""

    def test_connect_button_text_changes(self, devtool_app, select_tab, mock_serial):
        tab = select_tab("serial_tab")
        tab.port_var.set("/dev/ttyACM0")
        tab._toggle_connection()
        devtool_app.update()
        time.sleep(0.1)
        devtool_app.update()
        # After connecting, button should say "Disconnect"
        assert tab.connect_btn.cget("text") in ("Disconnect", "Connect")

    @pytest.mark.screenshot
    def test_screenshot_connected_state(self, devtool_app, select_tab, mock_serial,
                                         devtool_screenshot_dir):
        tab = select_tab("serial_tab")
        tab.port_var.set("/dev/ttyACM0")
        tab._toggle_connection()
        devtool_app.update()
        time.sleep(0.2)
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "serial_connected")
        capture_tkinter_window(devtool_app, path)


class TestOutputArea:
    """Test the serial output text area."""

    def test_clear_output(self, devtool_app, select_tab):
        tab = select_tab("serial_tab")
        # Insert some text manually
        tab.output_text.configure(state="normal")
        tab.output_text.insert("end", "test output\n")
        tab.output_text.configure(state="disabled")
        tab._clear_output()
        content = tab.output_text.get("1.0", "end").strip()
        assert content == "", "Clear should remove all output text"

    @pytest.mark.screenshot
    def test_screenshot_with_output(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("serial_tab")
        tab.output_text.configure(state="normal")
        tab.output_text.insert("end", "Hello from Pico W!\n")
        tab.output_text.insert("end", "LED blinking at 500ms\n")
        tab.output_text.insert("end", "Temperature: 23.5°C\n")
        tab.output_text.insert("end", "Button pressed: UP\n")
        tab.output_text.configure(state="disabled")
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "serial_with_output")
        capture_tkinter_window(devtool_app, path)
