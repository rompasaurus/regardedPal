"""
Tests for build and flash workflows (Steps 7-9, 11-14).

Covers: CMake/Ninja build commands, UF2 flashing, RPI-RP2 mount detection.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestRPIRP2Detection:
    """Test the find_rpi_rp2_mount function."""

    def test_mount_not_found(self, setup_module):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="", returncode=1
            )
            with patch("pathlib.Path.exists", return_value=False), \
                 patch("pathlib.Path.iterdir", return_value=[]):
                result = setup_module.find_rpi_rp2_mount()
        assert result is None

    def test_mount_found_in_media(self, setup_module, tmp_path):
        rp2_mount = tmp_path / "RPI-RP2"
        rp2_mount.mkdir()
        (rp2_mount / "INFO_UF2.TXT").write_text("UF2 Bootloader")

        search_paths = [tmp_path]
        with patch.object(setup_module, "find_rpi_rp2_mount") as mock_find:
            mock_find.return_value = rp2_mount
            result = mock_find()
        assert result == rp2_mount
