---
date: 2026-04-10
authors:
  - rompasaurus
categories:
  - Hardware
  - Firmware
slug: phase-1-first-pixels
---

# First Pixels — Hello World on the E-Ink Display

We got pixels. Real, physical, black-on-white pixels on the Waveshare 2.13" e-ink display, driven by C firmware on the Pico W. Phase 1's proof-of-life is alive.

<!-- more -->

## The Moment

There's a specific feeling when hardware you've been researching and wiring actually does the thing. You flash the UF2, the Pico reboots, the BUSY pin goes low, and then — text appears on the display. No Python interpreter, no OS, no abstraction layers. Just C talking SPI to a display controller pushing pixels into electrophoretic ink.

The `hello-world` firmware is 106KB compiled. It initializes SPI1 at 4MHz, configures the SSD1680 display controller, clears the screen, and renders "HELLO DILDER" using the Waveshare paint library. Takes about 3 seconds for the full refresh. Partial refresh drops that to under a second.

## What It Took to Get Here

More than you'd think. The Pico SDK's build system is CMake + Ninja, which is powerful but unforgiving if your environment isn't set up exactly right. On Arch Linux (my daily driver), the ARM cross-compiler is `arm-none-eabi-gcc` from the AUR, and the SDK needs `PICO_SDK_PATH` exported before CMake will even configure.

The wiring was straightforward — 8 jumper wires from the e-Paper HAT's side header to the Pico W's SPI1 pins. No level shifters needed since both run at 3.3V. The only gotcha: the display's BUSY pin is active-high during refresh, and you have to poll it before sending the next command or you'll corrupt the frame.

```
Pico W SPI1 → Waveshare 2.13" V3:
  GP11 (TX)  → DIN     GP10 (SCK) → CLK
  GP9  (CSn) → CS      GP8        → DC
  GP12       → RST     GP13       → BUSY
  3V3        → VCC     GND        → GND
```

## The Serial Heartbeat

Before touching the display, I flashed `hello-world-serial` — a minimal firmware that blinks the onboard LED and prints "Heartbeat" over USB serial at 115200 baud. This verified the entire toolchain end-to-end: compiler, linker, UF2 generation, BOOTSEL flashing, and USB CDC enumeration.

Watching `minicom` print heartbeat messages while the LED blinks is boring. But it's the kind of boring that means everything downstream is going to work.

## Flash Efficiency

The compiled `hello_dilder.uf2` is 106KB. The Pico W has 2MB (2048KB) of flash. That's 5.2% used for a program that initializes the full SPI display stack and renders text. This confirmed what the hardware research suggested — we have enormous headroom for the actual pet firmware, quote databases, sprite data, and whatever else Phase 2 brings.

For comparison, MicroPython's firmware alone uses ~700KB before you write a single line of code. Going C-first was the right call.

## What's Next

The display works. Serial works. The toolchain is solid. Now we need proper tooling — a setup CLI so others can replicate this environment, and a DevTool GUI for day-to-day development. That's the next post.

But right now? Right now we're staring at text on e-ink and it feels real.
