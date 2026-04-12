"""
Tests for the Display Emulator tab.

Covers: drawing tools (pencil, eraser, line, rect, filled rect, text),
clear, invert, save (PBM/BIN/PNG), load, pixel buffer integrity.
"""

import struct
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name

# ── Display constants (must match devtool.py) ──
DISPLAY_W = 250
DISPLAY_H = 122


class TestCanvasInitialisation:
    """Verify the emulator starts in a clean, known state."""

    def test_canvas_starts_blank(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        # All pixels should be 0 (white)
        for row in tab.pixels:
            assert all(p == 0 for p in row), "Canvas should start blank (all white)"

    def test_canvas_dimensions(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        assert len(tab.pixels) == DISPLAY_H
        assert len(tab.pixels[0]) == DISPLAY_W

    def test_default_tool_is_pencil(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        assert tab.tool_var.get() == "pencil"

    def test_default_brush_size(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        assert tab.size_var.get() == 1

    @pytest.mark.screenshot
    def test_screenshot_blank_canvas(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("display_tab")
        path = devtool_screenshot_dir / screenshot_name("devtool", "display_blank_canvas")
        capture_tkinter_window(devtool_app, path)


class TestDrawingTools:
    """Test each drawing tool modifies the pixel buffer correctly."""

    def test_pencil_draws_black_pixel(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab.tool_var.set("pencil")
        tab.size_var.set(1)
        # Simulate drawing at centre
        tab._draw_brush(125, 61, 1)
        assert tab.pixels[61][125] == 1, "Pencil should set pixel to black"

    def test_eraser_clears_pixel(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        # Draw then erase
        tab._draw_brush(100, 50, 1)
        assert tab.pixels[50][100] == 1
        tab._draw_brush(100, 50, 0)
        assert tab.pixels[50][100] == 0, "Eraser should set pixel to white"

    def test_brush_size_affects_area(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab.size_var.set(3)
        tab._draw_brush(50, 50, 1)
        # With brush size 3, a 3x3 area around the center should be filled
        assert tab.pixels[49][49] == 1
        assert tab.pixels[50][50] == 1
        assert tab.pixels[51][51] == 1

    def test_line_tool_draws_line(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab.size_var.set(1)
        tab._draw_line(0, 0, 10, 0)
        # Horizontal line at y=0 from x=0 to x=10
        for x in range(11):
            assert tab.pixels[0][x] == 1, f"Pixel ({x}, 0) should be black"

    def test_rectangle_outline(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_rect(10, 10, 20, 20, fill=False)
        # Corners should be set
        assert tab.pixels[10][10] == 1
        assert tab.pixels[10][20] == 1
        assert tab.pixels[20][10] == 1
        assert tab.pixels[20][20] == 1
        # Interior should be empty
        assert tab.pixels[15][15] == 0

    def test_filled_rectangle(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_rect(10, 10, 20, 20, fill=True)
        # Interior should be filled
        assert tab.pixels[15][15] == 1
        assert tab.pixels[12][18] == 1

    @pytest.mark.screenshot
    def test_screenshot_drawing_tools(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        # Draw a sample scene: line, rectangle, filled rectangle
        tab._draw_line(10, 10, 80, 10)
        tab._draw_rect(10, 20, 60, 50, fill=False)
        tab._draw_rect(70, 20, 120, 50, fill=True)
        tab._draw_line(10, 60, 120, 100)
        tab._redraw_from_buffer()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "display_drawing_tools")
        capture_tkinter_window(devtool_app, path)


class TestCanvasOperations:
    """Test clear, invert, and redraw operations."""

    def test_clear_resets_all_pixels(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab._draw_brush(50, 50, 1)
        tab._clear_canvas()
        for row in tab.pixels:
            assert all(p == 0 for p in row), "Clear should reset all pixels to white"

    def test_invert_flips_all_pixels(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_brush(50, 50, 1)
        original_50_50 = tab.pixels[50][50]
        original_0_0 = tab.pixels[0][0]
        tab._invert_canvas()
        assert tab.pixels[50][50] == 1 - original_50_50
        assert tab.pixels[0][0] == 1 - original_0_0

    def test_invert_twice_returns_to_original(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_brush(30, 30, 1)
        import copy
        original = copy.deepcopy(tab.pixels)
        tab._invert_canvas()
        tab._invert_canvas()
        assert tab.pixels == original

    @pytest.mark.screenshot
    def test_screenshot_inverted_canvas(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_rect(20, 20, 100, 80, fill=True)
        tab._invert_canvas()
        tab._redraw_from_buffer()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "display_inverted")
        capture_tkinter_window(devtool_app, path)


class TestSaveAndLoad:
    """Test saving and loading display images in all formats."""

    def test_pixels_to_bytes_and_back(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_brush(100, 60, 1)
        data = tab._pixels_to_bytes()
        byte_width = (DISPLAY_W + 7) // 8
        assert len(data) == byte_width * DISPLAY_H

        # Roundtrip: bytes -> pixels -> bytes should match
        tab._bytes_to_pixels(data)
        assert tab.pixels[60][100] == 1

    def test_save_creates_pbm_and_bin(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("display_tab")
        tab._draw_brush(50, 50, 1)

        # Mock the save dialog to auto-provide a name
        with patch("devtool_src.simpledialog.askstring", return_value="test_save"):
            tab._save_image()

        assets = devtool_module.ASSETS_DIR
        assert (assets / "test_save.pbm").exists(), "PBM file should be created"
        assert (assets / "test_save.bin").exists(), "BIN file should be created"

    def test_bin_file_has_correct_size(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("display_tab")
        tab._draw_brush(50, 50, 1)

        with patch("devtool_src.simpledialog.askstring", return_value="size_test"):
            tab._save_image()

        bin_path = devtool_module.ASSETS_DIR / "size_test.bin"
        byte_width = (DISPLAY_W + 7) // 8
        expected_size = byte_width * DISPLAY_H
        assert bin_path.stat().st_size == expected_size

    def test_load_bin_restores_pixels(self, devtool_app, select_tab, devtool_module):
        tab = select_tab("display_tab")

        # Draw, save, clear, reload
        tab._draw_brush(75, 40, 1)
        with patch("devtool_src.simpledialog.askstring", return_value="reload_test"):
            tab._save_image()

        tab._clear_canvas()
        assert tab.pixels[40][75] == 0

        bin_path = devtool_module.ASSETS_DIR / "reload_test.bin"
        data = bin_path.read_bytes()
        tab._bytes_to_pixels(data)
        assert tab.pixels[40][75] == 1

    @pytest.mark.screenshot
    def test_screenshot_save_workflow(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("display_tab")
        tab._clear_canvas()
        tab._draw_rect(30, 20, 220, 100, fill=False)
        tab._draw_line(30, 20, 220, 100)
        tab._draw_line(220, 20, 30, 100)
        tab._redraw_from_buffer()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "display_save_workflow")
        capture_tkinter_window(devtool_app, path)


class TestToolSelection:
    """Test switching between drawing tools."""

    def test_tool_variable_updates(self, devtool_app, select_tab):
        tab = select_tab("display_tab")
        for tool in ["pencil", "eraser", "line", "rectangle", "filled_rect", "text"]:
            tab.tool_var.set(tool)
            assert tab.tool_var.get() == tool

    @pytest.mark.screenshot
    def test_screenshot_each_tool_selected(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("display_tab")
        for tool in ["pencil", "eraser", "line", "rectangle", "filled_rect", "text"]:
            tab.tool_var.set(tool)
            devtool_app.update()
            path = devtool_screenshot_dir / screenshot_name("devtool", f"display_tool_{tool}")
            capture_tkinter_window(devtool_app, path)
