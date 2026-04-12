# Setup CLI User Guide

> Auto-generated from 19 test screenshots.
> Re-run the test suite to update: `pytest setup_cli/ -m screenshot`

---

## Cli

### Setup Cli Help Rendered

The setup.py help output showing all available flags and usage examples.

![setup_cli_help_rendered](../setup_cli/screenshots/setup_cli_help_rendered.png)

### Setup Cli List Rendered

The step list output showing all 15 setup steps with their status.

![setup_cli_list_rendered](../setup_cli/screenshots/setup_cli_list_rendered.png)

### Setup Cli Status Rendered

The environment status output showing installed tools, SDK paths, Docker, and testing framework.

![setup_cli_status_rendered](../setup_cli/screenshots/setup_cli_status_rendered.png)

### Setup Cli Step 01

Step 1 — Check Prerequisites: verifies git, cmake, Python, Tkinter, and pyserial are installed.

![setup_cli_step_01](../setup_cli/screenshots/setup_cli_step_01.png)

### Setup Cli Step 02

Step 2 — Install ARM Toolchain: installs arm-none-eabi-gcc, cmake, and ninja via the distro package manager.

![setup_cli_step_02](../setup_cli/screenshots/setup_cli_step_02.png)

### Setup Cli Step 03

Step 3 — Clone Pico SDK: downloads the official pico-sdk with all submodules.

![setup_cli_step_03](../setup_cli/screenshots/setup_cli_step_03.png)

### Setup Cli Step 04

Step 4 — Set PICO_SDK_PATH: appends the SDK path export to your shell rc file.

![setup_cli_step_04](../setup_cli/screenshots/setup_cli_step_04.png)

### Setup Cli Step 05

Step 5 — Serial Port Permissions: adds user to the uucp/dialout serial group.

![setup_cli_step_05](../setup_cli/screenshots/setup_cli_step_05.png)

### Setup Cli Step 06

Step 6 — Install VSCode Extensions: installs C/C++, CMake Tools, and Cortex-Debug extensions.

![setup_cli_step_06](../setup_cli/screenshots/setup_cli_step_06.png)

### Setup Cli Step 07

Step 7 — Build Hello World (Serial): CMake configure and Ninja build for the serial test firmware.

![setup_cli_step_07](../setup_cli/screenshots/setup_cli_step_07.png)

### Setup Cli Step 08

Step 8 — Flash Hello World (Serial): BOOTSEL detection and UF2 firmware flash.

![setup_cli_step_08](../setup_cli/screenshots/setup_cli_step_08.png)

### Setup Cli Step 09

Step 9 — Verify Serial Output: confirms the Pico W is alive via serial monitor.

![setup_cli_step_09](../setup_cli/screenshots/setup_cli_step_09.png)

### Setup Cli Step 10

Step 10 — Connect the Display: step-by-step HAT attachment instructions with ASCII diagrams.

![setup_cli_step_10](../setup_cli/screenshots/setup_cli_step_10.png)

### Setup Cli Step 11

Step 11 — Get Waveshare Library: downloads the C display driver and font files.

![setup_cli_step_11](../setup_cli/screenshots/setup_cli_step_11.png)

### Setup Cli Step 12

Step 12 — Build Hello World (Display): CMake + Ninja build for the display firmware.

![setup_cli_step_12](../setup_cli/screenshots/setup_cli_step_12.png)

### Setup Cli Step 13

Step 13 — Flash Hello World (Display): BOOTSEL detection and display firmware flash.

![setup_cli_step_13](../setup_cli/screenshots/setup_cli_step_13.png)

### Setup Cli Step 14

Step 14 — Verify Display Output: confirms text appears on the e-ink display.

![setup_cli_step_14](../setup_cli/screenshots/setup_cli_step_14.png)

### Setup Cli Step 15

Step 15 — Docker Build Toolchain: installs Docker and pre-builds the ARM cross-compilation container.

![setup_cli_step_15](../setup_cli/screenshots/setup_cli_step_15.png)

### Setup Cli Test Setup Rendered

The --test-setup output showing testing framework installation progress.

![setup_cli_test_setup_rendered](../setup_cli/screenshots/setup_cli_test_setup_rendered.png)
