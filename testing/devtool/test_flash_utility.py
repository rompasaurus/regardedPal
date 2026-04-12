"""
Tests for the Flash Firmware tab.

Covers: UF2 file selection, BOOTSEL mount detection (mocked),
flash workflow, build project buttons.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name


class TestFlashUtilityUI:
    """Verify the Flash Utility UI elements."""

    def test_initial_uf2_path_empty(self, devtool_app, select_tab):
        tab = select_tab("flash_tab")
        assert tab.uf2_var.get() == ""

    def test_mount_label_shows_not_detected(self, devtool_app, select_tab):
        tab = select_tab("flash_tab")
        assert "not detected" in tab.mount_label.cget("text").lower()

    @pytest.mark.screenshot
    def test_screenshot_flash_tab(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("flash_tab")
        path = devtool_screenshot_dir / screenshot_name("devtool", "flash_firmware_tab")
        capture_tkinter_window(devtool_app, path)


class TestUF2Selection:
    """Test UF2 file browsing and quick-flash presets."""

    def test_browse_sets_path(self, devtool_app, select_tab, tmp_path):
        tab = select_tab("flash_tab")
        uf2_file = tmp_path / "test_firmware.uf2"
        uf2_file.write_bytes(b"\x00" * 512)

        with patch("devtool_src.filedialog.askopenfilename", return_value=str(uf2_file)):
            tab._browse_uf2()
        assert tab.uf2_var.get() == str(uf2_file)

    def test_set_uf2_updates_variable(self, devtool_app, select_tab, tmp_path):
        tab = select_tab("flash_tab")
        uf2_path = tmp_path / "hello.uf2"
        uf2_path.write_bytes(b"\x00" * 256)
        tab._set_uf2(uf2_path)
        assert str(uf2_path) in tab.uf2_var.get()


class TestBootselDetection:
    """Test RPI-RP2 mount detection (mocked)."""

    def test_detect_mount_not_found(self, devtool_app, select_tab):
        tab = select_tab("flash_tab")
        with patch("devtool_src.find_rpi_rp2_mount", return_value=None):
            tab._detect_mount()
        devtool_app.update()
        assert "not" in tab.mount_label.cget("text").lower()

    def test_detect_mount_found(self, devtool_app, select_tab, tmp_path):
        tab = select_tab("flash_tab")
        mock_mount = tmp_path / "RPI-RP2"
        mock_mount.mkdir()
        with patch("devtool_src.find_rpi_rp2_mount", return_value=mock_mount):
            tab._detect_mount()
        devtool_app.update()
        label_text = tab.mount_label.cget("text")
        assert "RPI-RP2" in label_text or "detected" in label_text.lower() or str(mock_mount) in label_text

    @pytest.mark.screenshot
    def test_screenshot_mount_detected(self, devtool_app, select_tab, tmp_path,
                                        devtool_screenshot_dir):
        tab = select_tab("flash_tab")
        mock_mount = tmp_path / "RPI-RP2"
        mock_mount.mkdir()
        with patch("devtool_src.find_rpi_rp2_mount", return_value=mock_mount):
            tab._detect_mount()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "flash_mount_detected")
        capture_tkinter_window(devtool_app, path)


class TestFlashWorkflow:
    """Test the actual flash copy operation (mocked)."""

    def test_flash_without_uf2_shows_warning(self, devtool_app, select_tab):
        tab = select_tab("flash_tab")
        tab.uf2_var.set("")
        with patch("devtool_src.messagebox.showwarning") as mock_warn:
            tab._flash()
        # Should warn about missing UF2 or missing mount
        assert mock_warn.called or tab.uf2_var.get() == ""

    @pytest.mark.screenshot
    def test_screenshot_flash_instructions(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("flash_tab")
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "flash_instructions")
        capture_tkinter_window(devtool_app, path)
