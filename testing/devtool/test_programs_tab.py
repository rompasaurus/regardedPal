"""
Tests for the Programs tab.

Covers: program list, selection, preview canvas, deploy buttons,
Sassy Octopus program presence.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from utils.screenshot_helper import capture_tkinter_window, screenshot_name


class TestProgramsList:
    """Test the program list and selection."""

    def test_programs_list_populated(self, devtool_app, select_tab):
        tab = select_tab("programs_tab")
        assert tab.prog_list.size() > 0, "Programs list should have at least one entry"

    def test_sassy_octopus_in_list(self, devtool_app, select_tab):
        tab = select_tab("programs_tab")
        names = [tab.prog_list.get(i) for i in range(tab.prog_list.size())]
        assert "Sassy Octopus" in names

    def test_program_selection_updates_description(self, devtool_app, select_tab):
        tab = select_tab("programs_tab")
        tab.prog_list.selection_set(0)
        tab._on_select()
        devtool_app.update()
        desc_text = tab.desc_label.cget("text")
        assert len(desc_text) > 0 and desc_text != "Select a program to preview or deploy."

    @pytest.mark.screenshot
    def test_screenshot_programs_list(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("programs_tab")
        tab.prog_list.selection_set(0)
        tab._on_select()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "programs_list")
        capture_tkinter_window(devtool_app, path)


class TestProgramPreview:
    """Test program preview in the canvas."""

    def test_preview_canvas_exists(self, devtool_app, select_tab):
        tab = select_tab("programs_tab")
        assert tab.preview_canvas is not None
        assert tab.preview_canvas.winfo_exists()

    @pytest.mark.screenshot
    def test_screenshot_programs_preview(self, devtool_app, select_tab, devtool_screenshot_dir):
        select_tab("programs_tab")
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "programs_preview_area")
        capture_tkinter_window(devtool_app, path)


class TestDeployButtons:
    """Test deploy button states and actions."""

    def test_deploy_buttons_exist(self, devtool_app, select_tab):
        tab = select_tab("programs_tab")
        assert tab.deploy_btn.winfo_exists()
        assert tab.flash_btn.winfo_exists()
        assert tab.standalone_btn.winfo_exists()

    def test_stop_button_initially_disabled(self, devtool_app, select_tab):
        tab = select_tab("programs_tab")
        assert str(tab.stop_btn.cget("state")) in ("disabled", "['disabled']")

    @pytest.mark.screenshot
    def test_screenshot_deploy_buttons(self, devtool_app, select_tab, devtool_screenshot_dir):
        tab = select_tab("programs_tab")
        tab.prog_list.selection_set(0)
        tab._on_select()
        devtool_app.update()
        path = devtool_screenshot_dir / screenshot_name("devtool", "programs_deploy_buttons")
        capture_tkinter_window(devtool_app, path)
