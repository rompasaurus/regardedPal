# DevTool — Pico W Development Companion

A Tkinter GUI application for developing on the Raspberry Pi Pico W with the Waveshare 2.13" e-ink display. Provides a display emulator, serial monitor, firmware flash utility, asset manager, GPIO reference, USB/Wi-Fi connection walkthrough, and built-in documentation — all in one window.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| Python 3.9+ | Comes with most Linux distributions |
| Tkinter | Usually included with Python. On Arch: `sudo pacman -S tk` |
| pyserial | For USB serial communication with the Pico W |
| Pillow (optional) | For PNG export/import and better text rendering |

---

## Installation

=== "Arch / CachyOS"

    ```bash
    sudo pacman -S tk python
    ```

=== "Ubuntu / Debian"

    ```bash
    sudo apt install python3-tk
    ```

Then install Python dependencies:

```bash
cd DevTool/
pip install -r requirements.txt
```

---

## Launching

```bash
python3 DevTool/devtool.py
```

The application opens with seven tabs across the top of the window.

---

## Tabs

### Tab 1 — Display Emulator

A 250×122 pixel canvas that mirrors the e-ink display resolution. Draw images, type text, and preview exactly what will appear on the physical display.

**Drawing tools:**

| Tool | Usage |
|------|-------|
| Pencil | Click and drag to draw freehand |
| Eraser | Click and drag to erase |
| Line | Click start point, drag to end |
| Rectangle | Click corner, drag to opposite corner |
| Text | Click position, type in the text dialog |

**File operations:**

- **Save** — export to PBM (portable bitmap), BIN (raw display buffer), or PNG
- **Load** — import from any of the above formats
- **Send to Pico** — push the current canvas to the connected Pico W over serial
- **Clear** — reset the canvas to white

Saved images go to the `assets/` folder in the project root.

### Tab 2 — Serial Monitor

USB serial terminal for communicating with the Pico W in real time.

- Auto-detects serial ports (`/dev/ttyACM*`, `/dev/ttyUSB*`)
- Configurable baud rate (default 115200)
- Auto-scroll with live output
- Send commands directly to the Pico
- Save session logs to file

### Tab 3 — Flash Firmware

One-click firmware flashing for UF2 files.

- Detects when the Pico W is in BOOTSEL mode
- Browse and select `.uf2` firmware files
- **Build from Source** — runs CMake + Ninja to compile C projects, then flashes the result
- Progress feedback during flash

### Tab 4 — Asset Manager

Browse and preview all saved display images in the `assets/` directory.

- Thumbnail previews for PBM, BIN, and PNG files
- Delete unwanted assets
- Quick preview at actual display resolution (250×122)

### Tab 5 — GPIO Pin Reference

Static visual reference of the Pico W GPIO pinout. Useful when wiring components without having to look up the datasheet.

### Tab 6 — Connection Utility

Step-by-step walkthrough for connecting the Pico W to your development machine.

**USB Serial walkthrough (4 steps):**

1. Plug in the Pico W via USB
2. Verify device detection (live "Check" buttons)
3. Confirm serial port is available
4. Verify serial group permissions — includes a **"Fix: Add me to serial group"** button that auto-detects the correct group (`uucp` on Arch, `dialout` on Debian) and runs the `usermod` command via `pkexec`

**Wi-Fi walkthrough:**

- Example C code for connecting to a network
- CMake configuration snippets
- Network scanner utility
- TCP connection tester with IP/port input

### Tab 7 — Documentation

Searchable built-in documentation covering all tabs, keyboard shortcuts, file formats, and troubleshooting. Includes a TOC sidebar for quick navigation and a Find/Clear search with text highlighting.

---

## Supported File Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| PBM | `.pbm` | Portable Bitmap — standard 1-bit image format, human-readable header |
| BIN | `.bin` | Raw display buffer — 250×122 pixels packed as bytes, no header |
| PNG | `.png` | Standard PNG — requires Pillow for export/import |

---

## Architecture

The application is built from nine classes:

| Class | Responsibility |
|-------|---------------|
| `DilderDevTool` | Main window, tab management |
| `DisplayEmulator` | 250×122 canvas with drawing tools |
| `SerialMonitor` | Threaded USB serial I/O |
| `FlashUtility` | UF2 flashing and CMake build integration |
| `AssetManager` | Image browser with preview |
| `PinViewer` | Static GPIO pinout diagram |
| `ConnectionUtility` | USB and Wi-Fi setup walkthrough |
| `DocumentationTab` | Searchable built-in docs |
| `ProgramsTab` | Quick-access build and flash buttons |

Serial communication runs on a background thread to keep the UI responsive. The display emulator uses Tkinter's Canvas widget with direct pixel manipulation.

---

!!! tip "Full documentation"
    The complete DevTool walkthrough with screenshots and detailed usage instructions is in [`DevTool/README.md`](https://github.com/rompasaurus/dilder/blob/main/DevTool/README.md) in the repo.
