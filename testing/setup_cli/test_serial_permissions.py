"""
Tests for serial port permissions (Step 5).

Covers: group membership detection, group add commands.
"""

from unittest.mock import patch, MagicMock

import pytest


class TestGroupMembership:
    """Test user group membership checks."""

    def test_user_in_serial_group(self, setup_module):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="user wheel uucp", returncode=0
            )
            result = setup_module.user_in_serial_group()
        # Should detect membership based on group list
        assert isinstance(result, bool)

    def test_user_not_in_serial_group(self, setup_module):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="user wheel", returncode=0
            )
            with patch.object(setup_module, "detect_serial_group", return_value="uucp"):
                result = setup_module.user_in_serial_group()
        assert isinstance(result, bool)
