# Picotool & OTA — Wireless and USB Firmware Updates

Two methods for flashing firmware to the Pico 2 W without pressing the BOOTSEL button.

---

## Picotool (Recommended)

`picotool` is Raspberry Pi's official CLI for the Pico. It reboots the board into BOOTSEL mode over USB, then the DevTool copies the firmware and ejects the drive — all in one click.

### Requirements

- Pico 2 W connected via USB
- `picotool` installed (the DevTool can install it for you)
- Firmware must have USB stdio enabled (`pico_enable_stdio_usb` in CMakeLists.txt)

### DevTool Tab: Picotool

**Tab 9** in the DevTool provides the complete workflow:

#### Section 1: Setup

| Button | What It Does |
|--------|-------------|
| **Install picotool** | Builds picotool from the Pico SDK source, or installs from AUR on Arch Linux |
| **Install All Dependencies** | Opens `install-deps.sh` in a terminal — installs cmake, ninja, ARM toolchain, Docker, picotool, udev rules |
| **Refresh** | Re-checks all dependencies |

The dependency checker shows the status of every required tool on startup:
```
All dependencies OK: cmake, ninja, arm-none-eabi-gcc, docker, git, picotool, pico-sdk
```

#### Section 2: Device

| Button | What It Does |
|--------|-------------|
| **Device Info** | Queries the connected Pico over USB — shows firmware info, board type |
| **Reboot to BOOTSEL** | Sends a reboot command via USB — no button press needed |

#### Section 3: Flash Firmware

The firmware list auto-discovers all projects under `dev-setup/` that contain a `CMakeLists.txt`. Projects are organized by category:

| Category | Firmware |
|----------|----------|
| **Tools** | Hello World, Hello World Serial, Image Receiver |
| **Classic** | Sassy Octopus, Supportive Octopus |
| **Intense** | Angry, Chaotic, Conspiratorial |
| **Melancholy** | Sad, Tired, Nostalgic, Homesick |
| **Playful** | Slap Happy, Excited, Creepy |
| **Relaxed** | Chill, Lazy, Fat, Hungry |
| **Interactive** | Mood Selector, Joystick Mood Selector, Moodselector Sound, Moodselector Sound WiFi, Dilder Hub |

Each entry shows build status ("Built" with size, or "Not built").

| Button | What It Does |
|--------|-------------|
| **Flash (existing build)** | Reboots Pico → waits for BOOTSEL drive → copies .uf2 → ejects drive |
| **Clean Build & Flash** | Nukes build dir → Docker build → copies .uf2 → ejects drive |
| **Refresh List** | Re-scans dev-setup/ for new projects |

The **Display** dropdown in the top toolbar selects the e-ink variant (V2/V3/V3a/V4) used for builds.

### Flash Workflow

```
1. picotool reboot -f -u        → Pico enters BOOTSEL (no button)
2. Wait for /run/media/$USER/RP2350 to mount
3. cp firmware.uf2 → drive
4. sync && udisksctl unmount     → Pico reboots into new firmware
```

### Troubleshooting

| Issue | Fix |
|-------|-----|
| "picotool not found" | Click "Install picotool" or run `yay -S picotool` (Arch) |
| "No device" | Plug in the Pico via USB |
| Reboot fails | The Pico must be running firmware (not hung). Use BOOTSEL manually once, flash working firmware, then picotool works |
| Permission denied on build | Run `newgrp docker` or reboot — the DevTool auto-detects and relaunches with `sg docker` |
| Root-owned build dir | Docker creates files as root. The DevTool cleans them via `docker run alpine rm -rf` |

---

## WiFi OTA via picowota

An alternative approach using the [picowota](https://github.com/usedbytes/picowota) WiFi bootloader. Currently limited — flash operations don't work on RP2350 hardware. Documented here for reference.

### How It Works

1. Flash the picowota bootloader via USB (once)
2. The Pico creates a WiFi network or joins yours
3. The DevTool sends firmware over TCP port 4242
4. The Pico reboots into the new firmware

### DevTool Tab: Pico 2 W OTA

**Tab 8** provides:

- **Bootloader Setup** — install picowota submodule, build with WiFi credentials, flash via USB
- **WiFi Configuration** — AP mode (Pico creates network) or STA mode (joins your WiFi). Credentials persist in `~/.config/dilder-devtool/ota-settings.json`
- **Device Discovery** — probe single IP or scan /24 subnet
- **Flash OTA** — firmware list with clean build + OTA flash option

### Current Limitation

The picowota bootloader connects to WiFi successfully on the Pico 2 W (confirmed via router — device appears at 192.168.2.184 as "PicoW"). However, flash ERASE operations return ERR. The RP2040-compatibility-mode build can initialize WiFi (CYW43 chip is identical) but can't write to the RP2350's flash hardware through picowota's abstraction layer.

**Workaround:** Use picotool (Tab 9) instead. picotool works reliably for all flash operations.

### picowota_client.py

A standalone Python TCP client for the picowota protocol, located at `tools/devtool/picowota_client.py`:

```bash
# Scan for devices
python3 picowota_client.py --scan --subnet 192.168.2 dummy

# Flash firmware
python3 picowota_client.py 192.168.4.1 firmware.elf
```

Supports ELF, UF2, and raw binary files. Implements the full serial-flash protocol: SYNC, INFO, ERASE, WRITE, SEAL, GOTO.

---

## Display Variant Selector

The **Display** dropdown in the DevTool's top toolbar selects which e-ink driver variant is compiled:

| Variant | Chip | Driver | Notes |
|---------|------|--------|-------|
| **V2** | SSD1675B | EPD_2in13_V2.c | Legacy, custom LUT |
| **V3** | SSD1680 | EPD_2in13_V3.c | Custom LUT, proven partial refresh |
| **V3a** | SSD1680 (rev A) | EPD_2in13_V3a.c | Minor revision |
| **V4** | SSD1680 | EPD_2in13_V4.c | **Rewritten** — now uses V3's custom partial LUT |

The V4 driver was completely rewritten to use the V3's partial-refresh waveform. See the [V4 Display Driver](#v4-display-driver-fix) section below.

---

## V4 Display Driver Fix

### The Problem

The V4 e-ink display flashed black every 2-3 seconds during partial updates. Every frame caused a visible full-screen black-white-black waveform cycle, making the animated octopus display unusable.

### Root Cause

The SSD1680 chip's internal OTP LUT (used by V4) has no proper partial-refresh waveform. When the controller is asked to do a "partial" update, it uses the same full-refresh waveform that drives every pixel through a complete voltage cycle — resulting in the visible black flash.

The V3 driver avoids this by uploading a **custom 159-byte partial waveform** (`WF_PARTIAL`) that only drives changed pixels with short, weak voltage pulses. The V3 and V4 use the identical SSD1680 chip — the only difference is where the waveform data comes from.

### The Fix

The V4 `EPD_2in13_V4_Display_Partial()` function was rewritten to use the V3's approach:

1. **Hardware reset** — clears controller state for clean partial mode
2. **Load custom partial LUT** — 153 bytes to register `0x32`, plus gate voltage (`0x03`), source voltage (`0x04`), and VCOM (`0x2C`) from the waveform data
3. **Enable RAM ping-pong** — register `0x37` bit 6. The controller auto-copies `0x24`→`0x26` after each update, so the "old" frame is always available for diffing without the host having to send it
4. **Write only new data** — send the new image to register `0x24`. The controller diffs against `0x26` (previous frame) internally
5. **Trigger with `0x0F`** — the V3's proven partial update command

### What Changed

| Aspect | Before (broken) | After (fixed) |
|--------|-----------------|---------------|
| **Waveform** | Internal OTP LUT (has black pulse) | Custom `WF_PARTIAL` from V3 (no black pulse) |
| **RAM management** | Manual: write old to 0x26, new to 0x24 | Ping-pong: controller auto-tracks old/new |
| **Data per frame** | ~7.8KB (old + new buffers) | ~3.9KB (new buffer only) |
| **Extra RAM** | ~7.8KB (`prev_frame` + `clear_buf`) | 0 bytes |
| **Update trigger** | `0xC7` (used broken internal LUT) | `0x0F` (uses custom LUT) |
| **Visual result** | Black flash every frame | Only changed pixels update |

### File

`dev-setup/hello-world/lib/e-Paper/EPD_2in13_V4.c` — 320 lines, complete rewrite. Used by all firmware variants via the shared `lib/` symlink.

---

## install-deps.sh

One-command setup script for the complete development environment:

```bash
chmod +x install-deps.sh
./install-deps.sh
```

### What It Installs

| Category | Packages |
|----------|----------|
| **Build tools** | cmake, ninja, git, base-devel |
| **ARM toolchain** | arm-none-eabi-gcc, arm-none-eabi-newlib |
| **Docker** | docker, docker-compose |
| **Python** | python, pip, tkinter, pyserial, pillow |
| **Hardware** | libusb, hidapi, libheif |
| **Pico SDK** | Cloned to `~/pico/pico-sdk` with submodules |
| **picotool** | Installed via AUR (Arch) or built from source |
| **udev rules** | `/etc/udev/rules.d/99-pico.rules` — USB access without sudo |

Supports Arch Linux (pacman/yay), Debian/Ubuntu (apt), and Fedora (dnf).
