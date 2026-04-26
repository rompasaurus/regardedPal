---
date: 2026-04-26
authors:
  - rompasaurus
categories:
  - Hardware
  - Software
  - Firmware
slug: pico2w-board-support-current-design
---

# Pico 2 W Board Support + Current Design Photos

Added the Raspberry Pi Pico 2 W (RP2350) as a third target board alongside the original Pico W and ESP32-S3. The Pico 2 W is now the default development board for Dilder. Also captured photos of the current Rev 2 build running Sassy Octopus.

<!-- more -->

## Pico 2 W — What Changed

The Pico 2 W has an identical 40-pin header to the Pico W, so it's a physical drop-in replacement. Same wiring, same display, same joystick. The differences are under the hood:

- **RP2350** dual Cortex-M33 cores @ 150MHz (vs RP2040 Cortex-M0+ @ 133MHz)
- **4MB flash** (vs 2MB)
- **520KB SRAM** (vs 264KB)
- ARM TrustZone, secure boot, OTP

### Gotchas We Hit

Three issues that weren't obvious from the datasheet:

**BOOTSEL drive is `RP2350`, not `RPI-RP2`.** Every script that looked for the `RPI-RP2` USB mass storage label failed silently. Updated `find_rpi_rp2_mount()` in both the DevTool and setup CLI to search for both labels.

**No hardware RTC.** The RP2350 removed the Real-Time Clock peripheral entirely. `hardware/rtc.h`, `datetime_t`, and the `rtc_*()` functions don't exist. Created `rtc_compat.h` that provides a software fallback using `time_us_64()` on RP2350 while passing through to real hardware on RP2040.

**CMake cache poisoning.** If you built for `pico_w` and then switch to `pico2_w`, the cached `PICO_PLATFORM=rp2040` causes a fatal error. Added auto-detection that wipes the build directory when the platform mismatches.

## Current Design Photos

The Rev 2 enclosure running Sassy Octopus on a Pico 2 W:

![Dilder assembled — front view](../../assets/images/enclosure/rev2-current/rev2-assembled-front-view.jpg)

![Dilder assembled — three-quarter angle](../../assets/images/enclosure/rev2-current/rev2-assembled-three-quarter-view.jpg)

### Display Close-Up

The 250x122 e-ink display showing the RTC clock header, animated octopus sprite, speech bubble with quote, and tagline. All rendered in firmware — no PC connection needed.

![Display close-up — Sassy Octopus](../../assets/images/enclosure/rev2-current/rev2-display-closeup-sassy-octopus.jpg)

### Case Parts

Top cover with display window inlay and joystick port, base plate with solar panel cutout, and battery cradle insert.

![Case parts disassembled](../../assets/images/enclosure/rev2-current/rev2-case-parts-disassembled.jpg)

## DevTool Integration

Select "Pico 2 W (RP2350)" from the board dropdown and everything adapts — flash utility shows `RP2350` drive detection, builds use the correct CMake flag, Docker passes `PICO_BOARD=pico2_w`, documentation and connection wizard text all update dynamically.

## What's Next

- Test all 16 octopus personalities on Pico 2 W
- Joystick PCB integration with the K1-1506SN-01 switch
- Solar charging evaluation with the AK 62x36 panel
