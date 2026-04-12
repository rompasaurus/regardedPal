"""
Tests for the Asset Manager tab.

Covers: file listing, preview, delete, file format handling.
"""

import struct
from pathlib import Path
from unittest.mock import patch

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name

DISPLAY_W = 250
DISPLAY_H = 122


def create_test_bin(path: Path, pattern: str = "checkerboard"):
    """Create a test .bin file with a known pixel pattern."""
    byte_width = (DISPLAY_W + 7) // 8
    data = bytearray(byte_width * DISPLAY_H)
    if pattern == "checkerboard":
        for y in range(DISPLAY_H):
            for x in range(DISPLAY_W):
                if (x + y) % 2 == 0:
                    byte_idx = y * byte_width + x // 8
                    bit_idx = 7 - (x % 8)
                    data[byte_idx] |= (1 << bit_idx)
    path.write_bytes(bytes(data))


class TestAssetListing:
    """Test asset file listing and filtering."""

    def test_empty_assets_dir(self, devtool_app, select_tab):
        tab = select_tab("asset_tab")
        tab._refresh_list()
        assert tab.file_list.size() == 0

    def test_lists_bin_files(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("asset_tab")
        # Create test files in the mock assets dir
        (devtool_module.ASSETS_DIR / "test1.bin").write_bytes(b"\x00" * 100)
        (devtool_module.ASSETS_DIR / "test2.bin").write_bytes(b"\x00" * 100)
        (devtool_module.ASSETS_DIR / "ignored.txt").write_text("not an asset")
        tab._refresh_list()
        names = [tab.file_list.get(i) for i in range(tab.file_list.size())]
        assert "test1.bin" in names
        assert "test2.bin" in names
        assert "ignored.txt" not in names

    def test_lists_pbm_and_png_files(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("asset_tab")
        (devtool_module.ASSETS_DIR / "image.pbm").write_bytes(b"P4\n250 122\n" + b"\x00" * 3904)
        (devtool_module.ASSETS_DIR / "image.png").write_bytes(b"\x89PNG" + b"\x00" * 100)
        tab._refresh_list()
        names = [tab.file_list.get(i) for i in range(tab.file_list.size())]
        assert "image.pbm" in names
        assert "image.png" in names

    @pytest.mark.screenshot
    def test_screenshot_asset_list(self, devtool_app, select_tab, devtool_screenshot_dir,
                                    devtool_module):
        tab = select_tab("asset_tab")
        # Create some sample assets
        for name in ["logo.bin", "splash.bin", "test_pattern.pbm"]:
            (devtool_module.ASSETS_DIR / name).write_bytes(b"\x00" * 100)
        tab._refresh_list()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "asset_manager_list")
        capture_tkinter_window(devtool_app, path)


class TestAssetPreview:
    """Test asset preview rendering."""

    def test_preview_bin_file(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("asset_tab")
        bin_path = devtool_module.ASSETS_DIR / "preview_test.bin"
        create_test_bin(bin_path, "checkerboard")
        tab._refresh_list()
        tab._preview_file(bin_path)
        # Preview info should show the filename
        info_text = tab.preview_info.cget("text")
        assert "preview_test.bin" in info_text

    @pytest.mark.screenshot
    def test_screenshot_asset_preview(self, devtool_app, select_tab, devtool_screenshot_dir,
                                       devtool_module):
        tab = select_tab("asset_tab")
        bin_path = devtool_module.ASSETS_DIR / "checkerboard.bin"
        create_test_bin(bin_path, "checkerboard")
        tab._refresh_list()
        tab._preview_file(bin_path)
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "asset_manager_preview")
        capture_tkinter_window(devtool_app, path)


class TestAssetDeletion:
    """Test asset file deletion."""

    def test_delete_removes_file(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("asset_tab")
        test_file = devtool_module.ASSETS_DIR / "to_delete.bin"
        test_file.write_bytes(b"\x00" * 100)
        tab._refresh_list()

        # Select the file
        for i in range(tab.file_list.size()):
            if tab.file_list.get(i) == "to_delete.bin":
                tab.file_list.selection_set(i)
                break

        with patch("devtool_src.messagebox.askyesno", return_value=True):
            tab._delete_selected()

        assert not test_file.exists(), "File should be deleted"

    def test_delete_cancelled_keeps_file(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("asset_tab")
        test_file = devtool_module.ASSETS_DIR / "keep_this.bin"
        test_file.write_bytes(b"\x00" * 100)
        tab._refresh_list()

        for i in range(tab.file_list.size()):
            if tab.file_list.get(i) == "keep_this.bin":
                tab.file_list.selection_set(i)
                break

        with patch("devtool_src.messagebox.askyesno", return_value=False):
            tab._delete_selected()

        assert test_file.exists(), "File should not be deleted when cancelled"
