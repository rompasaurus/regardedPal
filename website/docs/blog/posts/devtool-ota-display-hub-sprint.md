---
date: 2026-05-05
authors:
  - rompasaurus
categories:
  - Software
  - Hardware
tags:
  - devtool
  - ota
  - picotool
  - display
  - e-ink
  - wifi
  - firmware
  - pico-2-w
---

# The Sprint That Fixed Everything: OTA Updates, Flicker-Free Display, and a Hub Firmware

Three days. 31 commits. The Dilder DevTool grew from 8 tabs to 11, the V4 e-ink display stopped flashing, and the Pico 2 W can now be flashed over WiFi — or over USB without ever touching the BOOTSEL button.

This is the story of a sprint that started with "I'm tired of plugging in USB" and ended with a complete development workflow overhaul.

<!-- more -->

## The Problem: USB Cable Fatigue

Every firmware update on the Pico 2 W required the same ritual: hold BOOTSEL, plug in USB, copy the .uf2, unplug, wait. For a device under active development with 24 firmware variants, this was happening dozens of times a day. Something had to give.

## Attempt 1: WiFi OTA via picowota

The first approach was ambitious — flash firmware wirelessly over WiFi using the [picowota](https://github.com/usedbytes/picowota) bootloader. This required:

1. **Porting picowota to RP2350** — the upstream repo only supported RP2040. Two patches were needed: a conditional CMSIS header include (`RP2350.h` vs `RP2040.h`) and a renamed `disable_interrupts` function that conflicted with the RP2350 SDK.

2. **A Python TCP client** — picowota's flash tool was written in Go. We reimplemented the entire [serial-flash protocol](https://github.com/usedbytes/serial-flash) in pure Python (`picowota_client.py`, 580 lines): SYNC, INFO, ERASE, WRITE, SEAL, GOTO commands, ELF/UF2/BIN loaders, subnet scanner, and progress callbacks.

3. **A new DevTool tab** ("Pico 2 W OTA") with WiFi configuration (AP/STA modes), device discovery (subnet scanner), bootloader build+flash workflow, and OTA firmware push with progress bar.

**The result:** It worked — the Pico 2 W connected to WiFi (`Moopster 2.4`) and appeared on the network at 192.168.2.184. But the RP2040-compatibility-mode build couldn't perform flash erase operations on the RP2350's flash hardware. The TCP server started, the SYNC handshake succeeded, but ERASE returned ERR.

**Lesson learned:** picowota's flash operations use RP2040-specific hardware registers that behave differently on the RP2350, even in compatibility mode. A full RP2350 port of picowota's flash abstraction layer is needed — beyond the scope of a weekend sprint.

## Attempt 2: picotool — The Right Tool

`picotool` is Raspberry Pi's official CLI for the Pico. It can reboot a running Pico into BOOTSEL mode via USB — no button press, no cable unplug. The entire flash cycle becomes:

```
picotool reboot -f -u    # reboot to BOOTSEL (no button)
# wait 2 seconds for drive to mount
cp firmware.uf2 /run/media/$USER/RP2350/
# eject drive → Pico reboots into new firmware
```

The new **Picotool tab** (Tab 9) wraps this into a one-click workflow:

- **Install picotool** — builds from SDK source or installs via AUR (`yay -S picotool`)
- **Device Info** — queries the connected Pico over USB
- **Reboot to BOOTSEL** — one click, no button
- **Flash (existing build)** — auto reboot → wait for mount → copy .uf2 → eject
- **Clean Build & Flash** — Docker build from scratch → automatic flash
- **Dependency checker** — shows missing tools (cmake, ninja, ARM toolchain, Docker, etc.) with one-click installer

The firmware list auto-discovers all 24 projects in `dev-setup/` that contain a `CMakeLists.txt` — no code changes needed when adding new firmware.

## The V4 Display: A Flicker Saga

The Waveshare 2.13" V4 e-ink display uses the SSD1680 controller — the same chip as the V3. But the V4 was marketed as using the "internal LUT" (look-up table), which means the waveform data for driving the e-ink particles is stored in the chip's OTP (one-time programmable) memory instead of being uploaded by the host.

**The problem:** the internal LUT has no proper partial-refresh waveform. Every "partial" update actually drove a full black-white-black cycle across the entire screen, causing a visible flash every 2-3 seconds.

### What We Tried (and Why It Failed)

1. **Two-pass partial refresh** — clear changed pixels to white first, then draw new content. Eliminated ghosting but doubled the flash (two full-screen waveform cycles per frame).

2. **Single-pass with `0xC7` command** — direct old→new diff. Still flashed because the internal LUT's partial waveform included a black pulse.

3. **Waveform reload avoidance** — loaded the waveform once and reused it. Didn't help because the waveform itself was the problem.

4. **`0xF7`, `0xFF`, `0xC7`, `0xCF`, `0x0F`** — tried every documented update command byte. All used the same internal LUT waveform.

5. **Syncing both RAM buffers** in `EPD_Clear()` — fixed a secondary issue (controller was diffing against garbage in register 0x26) but the primary flash from the waveform persisted.

### The Fix: Steal the V3's Waveform

The breakthrough came from reading the V3 driver's source code. The V3 uploads a **custom 159-byte partial waveform** (`WF_PARTIAL`) that drives only changed pixels with short, weak voltage pulses — no black flash. And since V3 and V4 use the identical SSD1680 chip, this waveform works on V4 hardware too.

The rewritten V4 `Display_Partial()` now mirrors the V3 approach exactly:

1. **Hardware reset** — clears controller state
2. **Load custom partial LUT** — 153 bytes to register 0x32, plus gate/source voltage config
3. **Enable RAM ping-pong** — register 0x37 bit 6. The controller auto-copies 0x24→0x26 after each update, eliminating the need to manually write the old frame
4. **Write only new data to 0x24** — half the SPI traffic per frame
5. **Trigger with `0x0F`** — the V3's partial trigger command, using our custom LUT

**Result:** Zero flicker. Only changed pixels update. The display refreshes smoothly with no visible full-screen redraw. The improvement is night and day.

## Dilder Hub: The All-In-One Firmware

With the display fixed, we built a combined firmware that brings together everything the Dilder can do:

### Main Screen
The animated octopus with 823 quotes across all 16 moods, RTC clock header, WiFi status icon (top-left), and battery/power icon (top-right). The tagline shows the current mood name (e.g. "- CONSPIRATORIAL -") instead of a static label. Press DOWN to open the menu.

### Menu System
Joystick-navigated overlay on the bottom half of the screen:

- **Mood Select** — scroll through all 16 moods + "ALL (RANDOM)". Pick one and the octopus immediately switches to quotes from that mood, returning to the main screen with the new personality.
- **Network** — WiFi on/off toggle (CENTER), live display of SSID, connection status, IP address, signal strength (RSSI), and NTP sync status.
- **Sound Test** — each joystick direction plays a different tone (C5, G4, A4, B4, E5) through the push-pull piezo driver.
- **Device Info** — firmware version, build date, display variant, quote count, live clock, current mood, WiFi status, battery voltage/percentage, board ID.
- **Back** — return to octopus.

### Push-Pull Piezo Audio
The speaker uses GP14 and GP15 (PWM slice 7) driven in opposite phase. Both pins at 50% duty, but channel A is inverted — the piezo sees 6.6Vpp instead of 3.3V from a single pin. Double the voltage, noticeably louder, no external components.

### WiFi and NTP
The CYW43 WiFi chip connects in STA mode to the configured network. On connection, an NTP client syncs the RTC to pool.ntp.org with timezone offset (UTC+2 for CEST). The clock header on the main screen shows real network time.

### Battery Monitoring
ADC3 (GP29) reads VSYS through the Pico's built-in 3:1 voltage divider. The battery icon shows 0-4 fill bars for 3.0-4.2V (10440 Li-ion range), or a lightning bolt when USB powered (>4.5V). The Device Info screen shows the actual voltage.

## Development Workflow

The complete development workflow is now:

1. **One-time setup:** `./install-deps.sh` — installs everything (ARM toolchain, cmake, ninja, Docker, picotool, Pico SDK, udev rules)
2. **Open DevTool:** `python3 tools/devtool/devtool.py` — auto-relaunches with Docker group if needed
3. **Select firmware** in the Picotool tab — all 24 projects auto-discovered
4. **Click "Clean Build & Flash"** — Docker builds the firmware, picotool reboots the Pico to BOOTSEL, copies the .uf2, ejects the drive
5. **Pico reboots** into new firmware automatically

No BOOTSEL button. No USB cable unplugging. No manual file copying.

## What's Next

- **Active buzzer integration** — ordered a 95dB active buzzer pack for louder audio (arrives tomorrow)
- **Joystick PCB wiring** — the JLCPCB boards arrived, thumbpiece fits, need to wire into the Mk2 case
- **Game loop** — the 8-module firmware architecture (stat system, emotion engine, life stages, dialogue) is implemented and waiting for integration with the hub
- **Encounter system** — BLE proximity detection with unique per-device chimes, designed in the gameplay planning docs
