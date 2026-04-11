---
date: 2026-04-11
authors:
  - rompasaurus
categories:
  - Software
  - Tools
slug: phase-1-dev-tooling
---

# Phase 1 Continued: Dev Environment & Tooling

The hardware is wired up and running C firmware. Now we need proper tooling to make development sustainable. This post covers the setup CLI, DevTool GUI, and the workflow they enable.

<!-- more -->

## The Problem

Getting a Pico W development environment working from scratch involves a dozen steps: installing the ARM cross-compiler, cloning the Pico SDK, configuring environment variables, setting serial port permissions, building with CMake, flashing via BOOTSEL, and verifying output. Miss one step and you're debugging your toolchain instead of writing firmware.

We needed two things:

1. **A repeatable setup process** — so anyone can go from zero to "Hello World on the display" without guesswork
2. **A development companion** — so day-to-day work (serial debugging, display preview, firmware flashing) doesn't require juggling terminal windows and external tools

## The Setup CLI (`setup.py`)

An interactive Python script that walks through 14 steps in two checkpoints:

- **Checkpoint 1 (Steps 1–9):** Serial Hello World — verifies the toolchain end-to-end without any display wiring
- **Checkpoint 2 (Steps 10–14):** Display Hello World — connects the Waveshare and gets pixels on screen

The script auto-detects your Linux distribution (Arch uses `uucp` for serial groups, Debian uses `dialout`), finds the `RPI-RP2` BOOTSEL mount point even when automount is slow, and captures CMake/Ninja build errors cleanly.

```bash
python3 setup.py              # interactive walkthrough
python3 setup.py --status     # see what's done
python3 setup.py --step 7     # jump to a specific step
```

[Setup CLI docs :material-arrow-right:](../../docs/tools/setup-cli.md){ .md-button }

## The DevTool GUI

A Tkinter application with seven tabs:

| Tab | What it does |
|-----|-------------|
| Display Emulator | 250×122 canvas with pencil, eraser, line, rect, and text tools. Save to PBM/BIN/PNG or send directly to the Pico |
| Serial Monitor | Threaded USB serial terminal with auto-detect, command input, and log saving |
| Flash Firmware | One-click UF2 flashing with BOOTSEL detection and CMake build integration |
| Asset Manager | Browse and preview saved display images |
| GPIO Pin Reference | Static Pico W pinout diagram |
| Connection Utility | USB and Wi-Fi setup walkthroughs with live verification checks |
| Documentation | Searchable built-in docs with TOC sidebar |

The display emulator is the killer feature — design exactly what will appear on the e-ink screen, test it visually, then push it to the device. No more guessing whether your pixel coordinates are right.

```bash
cd DevTool/
pip install -r requirements.txt
python3 devtool.py
```

[DevTool docs :material-arrow-right:](../../docs/tools/devtool.md){ .md-button }

## C-First Development

An important decision: this project runs C on the Pico W, not MicroPython. The reasons:

- **Speed** — direct hardware control without an interpreter layer
- **Flash efficiency** — MicroPython firmware uses ~700KB of the 2MB flash; C leaves nearly the full 2MB for code and assets
- **Learning value** — the whole point is to learn embedded development properly

The `dev-setup/` folder contains two Hello World projects:

- `hello-world-serial/` — LED blink + serial heartbeat (verifies toolchain)
- `hello-world/` — text on the e-ink display (verifies full hardware chain)

Both compile with CMake + Ninja and flash via UF2 copy to BOOTSEL.

## What's Next

Phase 1 goals are nearly complete — hardware is wired, firmware compiles and runs, tooling is in place. Next up:

- Verify all 5 button inputs on the breadboard
- Display a custom image as proof-of-life
- Begin Phase 2: firmware scaffold with game loop, pet state machine, and sprite system
