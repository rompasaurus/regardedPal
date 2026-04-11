# Setup CLI — First-Time Environment Setup

An interactive Python CLI that walks through the entire Pico W development environment setup — from installing the C/C++ ARM toolchain to flashing your first Hello World onto the e-ink display.

---

## Usage

```bash
python3 setup.py              # interactive step-by-step walkthrough
python3 setup.py --status     # show current setup state
python3 setup.py --step N     # jump to step N
python3 setup.py --list       # list all steps
```

No external dependencies required — runs on Python 3.9+ with only the standard library.

---

## What It Does

The script walks through 14 steps, split into two checkpoints:

### Checkpoint 1 — Serial Hello World (Steps 1–9)

Verifies your toolchain works end-to-end without any display wiring.

| Step | Description | Type |
|------|-------------|------|
| 1 | Check prerequisites (Python, pip, git, gcc) | Automated |
| 2 | Install ARM cross-compiler toolchain | Automated |
| 3 | Clone the Pico SDK | Automated |
| 4 | Set `PICO_SDK_PATH` environment variable | Automated |
| 5 | Configure serial port permissions (`uucp`/`dialout`) | Automated |
| 6 | Install VSCode + MicroPico extension | Manual guidance |
| 7 | Build `hello-world-serial` with CMake + Ninja | Automated |
| 8 | Flash the serial `.uf2` to Pico W via BOOTSEL | Automated |
| 9 | Verify serial output (LED blink + heartbeat) | Manual verification |

### Checkpoint 2 — Display Hello World (Steps 10–14)

Connects the Waveshare display and gets pixels on screen.

| Step | Description | Type |
|------|-------------|------|
| 10 | Connect display to Pico W (header-on-header) | Manual wiring |
| 11 | Download Waveshare e-Paper driver library | Automated |
| 12 | Build `hello-world` display program | Automated |
| 13 | Flash the display `.uf2` to Pico W | Automated |
| 14 | Verify display output | Manual verification |

---

## Features

- **Distro detection** — automatically detects Arch/CachyOS vs Ubuntu/Debian for package manager commands and serial group names
- **Resume support** — tracks which steps are complete; use `--step N` to jump to any step
- **BOOTSEL detection** — scans for the `RPI-RP2` mount point using `findmnt`/`lsblk` with retry for automount delays
- **Build error reporting** — captures both stdout and stderr from CMake/Ninja for clear error output
- **ANSI terminal UI** — colored output with spinners, boxed explanations, and step-by-step progress indicators

---

## Status Dashboard

Run `python3 setup.py --status` to see a snapshot of your environment:

```
┌─────────────────────────────────────────┐
│  Dilder — Setup Status                  │
├─────────────────────────────────────────┤
│  ✓ Python 3.12.3                        │
│  ✓ arm-none-eabi-gcc                    │
│  ✓ Pico SDK at ~/pico/pico-sdk         │
│  ✓ PICO_SDK_PATH set                   │
│  ✓ Serial group: uucp                  │
│  ✗ hello-world-serial not built        │
│  …                                      │
└─────────────────────────────────────────┘
```

---

!!! info "Source"
    The script lives at [`setup.py`](https://github.com/rompasaurus/dilder/blob/main/setup.py) in the project root. The companion guide with full wiring instructions is in [`dev-setup/pico-and-display-first-time-setup.md`](https://github.com/rompasaurus/dilder/blob/main/dev-setup/pico-and-display-first-time-setup.md).
