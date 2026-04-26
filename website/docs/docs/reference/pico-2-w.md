# Raspberry Pi Pico 2 W — Reference & Migration Guide

Source: [raspberrypi.com/documentation/microcontrollers/pico-series.html](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html)

---

## Hardware Specifications

| Spec | Pico 2 W (RP2350) | Pico W (RP2040) |
|------|-------------------|-----------------|
| Chip | RP2350 | RP2040 |
| CPU | Dual-core ARM Cortex-M33 @ 150MHz | Dual-core ARM Cortex-M0+ @ 133MHz |
| Alt CPU | Dual-core Hazard3 RISC-V @ 150MHz | None |
| RAM | 520KB SRAM | 264KB SRAM |
| Flash | 4MB onboard QSPI | 2MB onboard QSPI |
| Wi-Fi | 802.11n 2.4GHz (Infineon CYW43439) | Same |
| Bluetooth | BLE 5.2 | Same |
| USB | Micro-USB 1.1 (device and host) | Same |
| GPIO | 26 multi-function pins (same header) | Same |
| ADC | 4 external + 1 internal (12-bit) | 3 external + 1 internal |
| SPI | 2x SPI controllers (SPI0, SPI1) | Same |
| Security | ARM TrustZone, secure boot, OTP | None |
| Dimensions | 51 x 21 x 3.9mm | Same |
| Operating temp | -20C to +85C | Same |
| Power input | 1.8V-5.5V via VSYS, or 5V via micro-USB | Same |

---

## Pin Compatibility

!!! success "Drop-in replacement"
    The Pico 2 W has an **identical 40-pin header** to the Pico W. All Dilder wiring (e-Paper SPI1, joystick buttons, power) works without any changes. You can swap boards and keep the same wiring.

The GPIO assignments, SPI controllers, and pin multiplexing are the same. Dilder uses the same `board_config.h` pin definitions for both boards.

---

## Critical Gotchas: RP2350 vs RP2040

These are the issues we hit while porting Dilder. Save yourself the debugging time.

### 1. BOOTSEL Drive Shows as `RP2350`, Not `RPI-RP2`

When you hold BOOTSEL and plug in the Pico 2 W, the USB mass storage drive appears as **`RP2350`** instead of `RPI-RP2`.

Any scripts or tools that look for `RPI-RP2` by name will fail silently. The DevTool and setup.py have been updated to search for both labels.

### 2. No Hardware RTC

The RP2040 has a hardware Real-Time Clock (RTC) peripheral. The RP2350 **removed it entirely**.

- `#include "hardware/rtc.h"` does not exist on RP2350
- `rtc_init()`, `rtc_set_datetime()`, `rtc_get_datetime()` are gone
- `pico/util/datetime.h` (which defines `datetime_t`) was also removed

**Solution:** We created `rtc_compat.h` in `dev-setup/hello-world/lib/Config/` that:

- On RP2040: includes the real hardware RTC headers (zero overhead)
- On RP2350: defines `datetime_t` ourselves and provides software `rtc_*()` functions using `time_us_64()`

All 18 program `main.c` files now use `#include "rtc_compat.h"` instead of `#include "hardware/rtc.h"`.

The CMakeLists.txt files conditionally link `hardware_rtc` only on RP2040:

```cmake
if(PICO_PLATFORM STREQUAL "rp2040")
    target_link_libraries(my_target hardware_rtc)
endif()
```

### 3. CMake Cache Poisoning When Switching Boards

If you previously built for `pico_w` (RP2040) and then try to build for `pico2_w` (RP2350) in the same build directory, CMake will fail:

```
PICO_PLATFORM is specified to be 'rp2040', but PICO_BOARD='pico2_w'
uses 'rp2350' which is incompatible.
```

The CMake cache stores `PICO_PLATFORM=rp2040` from the first build. Even if you pass `-DPICO_BOARD=pico2_w`, the cached platform wins.

**Solution:** Delete the `build/` directory (or use separate build directories per board). The setup.py and DevTool now auto-detect stale caches by checking both `PICO_BOARD` and `PICO_PLATFORM` in `CMakeCache.txt` and wipe the build directory when they mismatch.

### 4. Pico SDK Version Requirement

The Pico 2 W requires **Pico SDK 2.0 or later**. Earlier SDK versions do not include `pico2_w` board definitions.

Check your SDK version:

```bash
cat $PICO_SDK_PATH/pico_sdk_version.cmake | grep PICO_SDK_VERSION_STRING
```

If it says 1.x, update:

```bash
cd ~/pico/pico-sdk
git pull
git submodule update --init
```

### 5. Compiler Targets Cortex-M33, Not Cortex-M0+

The RP2350 uses ARM Cortex-M33 cores. The GCC flags change from `-mcpu=cortex-m0plus` to `-mcpu=cortex-m33 -mthumb -march=armv8-m.main+fp+dsp`. This is handled automatically by the Pico SDK when you set `PICO_BOARD=pico2_w` -- no manual flag changes needed.

### 6. Docker Builds Need PICO_BOARD Environment Variable

The Dockerfile was updated to accept a `PICO_BOARD` env var (defaults to `pico_w`). When building for Pico 2 W via Docker, pass:

```bash
docker compose run --rm -e PICO_BOARD=pico2_w build-sassy-octopus
```

The DevTool does this automatically based on the board selector dropdown.

---

## Build & Flash Workflow

The workflow is identical to Pico W -- the only differences are the CMake board flag and the BOOTSEL drive name.

### Build

```bash
mkdir build && cd build
cmake -G Ninja -DPICO_SDK_PATH=$PICO_SDK_PATH -DPICO_BOARD=pico2_w ..
ninja
```

### Flash

1. Hold BOOTSEL, plug in USB, release
2. `RP2350` drive appears (not `RPI-RP2`)
3. Copy the `.uf2` file to the drive
4. Board reboots automatically

### Serial Monitor

Same as Pico W -- shows as `/dev/ttyACM0` at 115200 baud.

---

## DevTool Support

Select **"Pico 2 W (RP2350)"** from the board dropdown in the DevTool toolbar. Everything adapts automatically:

- Flash utility detects `RP2350` BOOTSEL drive
- Build commands use `-DPICO_BOARD=pico2_w`
- Docker builds pass `PICO_BOARD=pico2_w`
- Pin viewer shows the correct header (identical pins, updated title)
- Flash size reported as 4MB (4096 KB)
- All documentation and connection wizard text updates to show Pico 2 W

---

## Setup CLI Support

```bash
python3 setup.py --board pico2          # Pico 2 W setup steps
python3 setup.py --board pico2 --step 7  # Jump to build step
```

The setup steps are identical to Pico W (same SDK, same toolchain) but use the correct `PICO_BOARD=pico2_w` flag and detect the `RP2350` BOOTSEL drive.
