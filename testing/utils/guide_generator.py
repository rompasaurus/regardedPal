"""
User Guide Generator

Scans screenshot directories and assembles markdown user guides
with embedded screenshots and descriptions. Generated guides can
be copied into the website docs for publication.

Usage:
    python3 -m testing.utils.guide_generator
"""

import re
from pathlib import Path

TESTING_DIR = Path(__file__).parent.parent.resolve()
GUIDES_DIR = TESTING_DIR / "guides"

# Screenshot directory mapping
SCREENSHOT_DIRS = {
    "devtool": TESTING_DIR / "devtool" / "screenshots",
    "setup_cli": TESTING_DIR / "setup_cli" / "screenshots",
    "website": TESTING_DIR / "website" / "screenshots",
}

# Human-readable descriptions for screenshot name patterns
DESCRIPTIONS = {
    # DevTool
    "devtool_display_blank_canvas": "The Display Emulator tab with a fresh blank canvas (250x122 pixels, matching the Waveshare 2.13\" e-ink display).",
    "devtool_display_drawing_tools": "Drawing tools in action: line, rectangle, and filled rectangle demonstrated on the emulator canvas.",
    "devtool_display_inverted": "The display after using the Invert function, which flips all black pixels to white and vice versa.",
    "devtool_display_save_workflow": "A sample image ready to be saved in PBM, BIN, and PNG formats for use on the Pico W.",
    "devtool_display_tool_pencil": "The Pencil tool selected — draw freehand with configurable brush size (1-10px).",
    "devtool_display_tool_eraser": "The Eraser tool selected — erase pixels back to white with configurable brush size.",
    "devtool_display_tool_line": "The Line tool selected — click and drag to draw straight lines using Bresenham's algorithm.",
    "devtool_display_tool_rectangle": "The Rectangle tool selected — click and drag to draw rectangle outlines.",
    "devtool_display_tool_filled_rect": "The Filled Rectangle tool selected — click and drag to draw filled rectangles.",
    "devtool_display_tool_text": "The Text tool selected — click to place rasterised text at any position.",
    "devtool_serial_disconnected": "The Serial Monitor tab in its disconnected state, showing port selection and baud rate configuration.",
    "devtool_serial_connected": "The Serial Monitor connected to the Pico W, ready to receive output.",
    "devtool_serial_with_output": "Live serial output from the Pico W showing sensor readings and button events.",
    "devtool_flash_firmware_tab": "The Flash Firmware tab with UF2 file selection, BOOTSEL detection, and quick-flash presets.",
    "devtool_flash_mount_detected": "BOOTSEL mode detected — RPI-RP2 drive found and ready for firmware flashing.",
    "devtool_flash_instructions": "Step-by-step flashing instructions displayed in the Flash Firmware tab.",
    "devtool_asset_manager_list": "The Asset Manager showing saved display images (PBM, BIN, PNG files).",
    "devtool_asset_manager_preview": "A checkerboard test pattern previewed at 2x zoom in the Asset Manager.",
    "devtool_programs_list": "The Programs tab with Sassy Octopus selected, showing program description and deploy options.",
    "devtool_programs_preview_area": "The preview canvas area where programs are animated before deployment.",
    "devtool_programs_deploy_buttons": "Deploy buttons: Preview, Deploy to Pico (streaming), Flash IMG Receiver, and Deploy Standalone.",
    "devtool_gpio_pin_diagram": "The GPIO Pin Viewer showing the complete Pico W pinout with Dilder-specific pin assignments highlighted.",
    "devtool_connection_usb_mode": "USB Serial Connection walkthrough with step-by-step diagnostic checks.",
    "devtool_connection_wifi_mode": "Wi-Fi Connection setup guide with code samples and CMakeLists configuration.",
    "devtool_connection_usb_walkthrough": "The full USB connection walkthrough showing all 4 diagnostic steps.",
    "devtool_documentation_tab": "The built-in Documentation tab with searchable table of contents.",
    "devtool_documentation_search": "Documentation search in action, filtering content by keyword.",
    "devtool_tab_display_emulator": "Overview of the Display Emulator tab.",
    "devtool_tab_serial_monitor": "Overview of the Serial Monitor tab.",
    "devtool_tab_flash_firmware": "Overview of the Flash Firmware tab.",
    "devtool_tab_asset_manager": "Overview of the Asset Manager tab.",
    "devtool_tab_programs": "Overview of the Programs tab.",
    "devtool_tab_gpio_pins": "Overview of the GPIO Pins tab.",
    "devtool_tab_connection_utility": "Overview of the Connection Utility tab.",
    "devtool_tab_documentation": "Overview of the Documentation tab.",
    # Setup CLI — global flags
    "setup_cli_help_rendered": "The setup.py help output showing all available flags and usage examples.",
    "setup_cli_list_rendered": "The step list output showing all 15 setup steps with their status.",
    "setup_cli_status_rendered": "The environment status output showing installed tools, SDK paths, Docker, and testing framework.",
    "setup_cli_test_setup_rendered": "The --test-setup output showing testing framework installation progress.",
    "setup_cli_help_output": "Raw ANSI capture of setup.py --help output.",
    "setup_cli_list_output": "Raw ANSI capture of setup.py --list output.",
    "setup_cli_status_output": "Raw ANSI capture of setup.py --status output.",
    "setup_cli_test_setup_output": "Raw ANSI capture of setup.py --test-setup output.",
    # Setup CLI — individual step screenshots
    "setup_cli_step_01": "Step 1 — Check Prerequisites: verifies git, cmake, Python, Tkinter, and pyserial are installed.",
    "setup_cli_step_02": "Step 2 — Install ARM Toolchain: installs arm-none-eabi-gcc, cmake, and ninja via the distro package manager.",
    "setup_cli_step_03": "Step 3 — Clone Pico SDK: downloads the official pico-sdk with all submodules.",
    "setup_cli_step_04": "Step 4 — Set PICO_SDK_PATH: appends the SDK path export to your shell rc file.",
    "setup_cli_step_05": "Step 5 — Serial Port Permissions: adds user to the uucp/dialout serial group.",
    "setup_cli_step_06": "Step 6 — Install VSCode Extensions: installs C/C++, CMake Tools, and Cortex-Debug extensions.",
    "setup_cli_step_07": "Step 7 — Build Hello World (Serial): CMake configure and Ninja build for the serial test firmware.",
    "setup_cli_step_08": "Step 8 — Flash Hello World (Serial): BOOTSEL detection and UF2 firmware flash.",
    "setup_cli_step_09": "Step 9 — Verify Serial Output: confirms the Pico W is alive via serial monitor.",
    "setup_cli_step_10": "Step 10 — Connect the Display: step-by-step HAT attachment instructions with ASCII diagrams.",
    "setup_cli_step_11": "Step 11 — Get Waveshare Library: downloads the C display driver and font files.",
    "setup_cli_step_12": "Step 12 — Build Hello World (Display): CMake + Ninja build for the display firmware.",
    "setup_cli_step_13": "Step 13 — Flash Hello World (Display): BOOTSEL detection and display firmware flash.",
    "setup_cli_step_14": "Step 14 — Verify Display Output: confirms text appears on the e-ink display.",
    "setup_cli_step_15": "Step 15 — Docker Build Toolchain: installs Docker and pre-builds the ARM cross-compilation container.",
    # Website
    "website_home_page": "The Dilder project home page.",
    "website_docs_overview": "The documentation overview page.",
    "website_docs_devtool": "The DevTool documentation page on the website.",
    "website_docs_setup_cli": "The Setup CLI documentation page on the website.",
    "website_blog_index": "The blog index showing build series posts.",
    "website_search_results": "Search results for 'Pico W' demonstrating the built-in search.",
    "website_reference_pico_w": "The Pico W hardware reference page.",
    "website_home_desktop": "Home page at desktop resolution (1280x800).",
    "website_home_tablet": "Home page at tablet resolution (768x1024).",
    "website_home_mobile": "Home page at mobile resolution (375x812).",
    "website_docs_desktop": "Documentation at desktop resolution.",
    "website_docs_tablet": "Documentation at tablet resolution.",
    "website_docs_mobile": "Documentation at mobile resolution.",
}


def get_description(filename: str) -> str:
    """Look up a human-readable description for a screenshot filename."""
    stem = Path(filename).stem
    return DESCRIPTIONS.get(stem, f"Screenshot: {stem.replace('_', ' ').title()}")


def generate_guide(tool_name: str, screenshots_dir: Path, output_path: Path):
    """Generate a markdown user guide from screenshots.

    Args:
        tool_name: Human-readable tool name (e.g., "DevTool")
        screenshots_dir: Directory containing PNG screenshots
        output_path: Where to write the markdown guide
    """
    screenshots = sorted(screenshots_dir.glob("*.png"))
    if not screenshots:
        print(f"  No screenshots found in {screenshots_dir}")
        return

    # Compute relative path from guides dir to screenshots
    rel_base = Path("..") / screenshots_dir.relative_to(TESTING_DIR)

    lines = [
        f"# {tool_name} User Guide",
        "",
        f"> Auto-generated from {len(screenshots)} test screenshots.",
        f"> Re-run the test suite to update: `pytest {screenshots_dir.parent.name}/ -m screenshot`",
        "",
        "---",
        "",
    ]

    # Group by feature (prefix before second underscore)
    groups = {}
    for shot in screenshots:
        stem = shot.stem
        parts = stem.split("_", 2)
        if len(parts) >= 3:
            group_key = parts[1]
        else:
            group_key = "general"
        groups.setdefault(group_key, []).append(shot)

    for group, shots in groups.items():
        heading = group.replace("_", " ").title()
        lines.append(f"## {heading}")
        lines.append("")

        for shot in shots:
            desc = get_description(shot.name)
            rel_path = rel_base / shot.name
            lines.append(f"### {shot.stem.replace('_', ' ').title()}")
            lines.append("")
            lines.append(desc)
            lines.append("")
            lines.append(f"![{shot.stem}]({rel_path})")
            lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))
    print(f"  Generated: {output_path} ({len(screenshots)} screenshots)")


def main():
    """Generate all user guides."""
    print("Generating user guides from test screenshots...\n")

    GUIDES_DIR.mkdir(parents=True, exist_ok=True)

    guides = [
        ("Dilder DevTool", SCREENSHOT_DIRS["devtool"], GUIDES_DIR / "devtool_guide.md"),
        ("Setup CLI", SCREENSHOT_DIRS["setup_cli"], GUIDES_DIR / "setup_cli_guide.md"),
        ("Dilder Website", SCREENSHOT_DIRS["website"], GUIDES_DIR / "website_guide.md"),
    ]

    for tool_name, screenshots_dir, output_path in guides:
        print(f"[{tool_name}]")
        if screenshots_dir.exists():
            generate_guide(tool_name, screenshots_dir, output_path)
        else:
            print(f"  Screenshots directory not found: {screenshots_dir}")
            print(f"  Run tests first: pytest {screenshots_dir.parent.name}/ -m screenshot")
        print()

    print("Done! Guides are in testing/guides/")
    print("Copy them to website/docs/ to publish on the site.")


if __name__ == "__main__":
    main()
