---
date: 2026-04-14
authors:
  - rompasaurus
categories:
  - Hardware
  - Planning
slug: custom-pcb-research
---

# From Breadboard to Custom PCB — The Research

The breadboard prototype works. The e-ink display refreshes, the joystick clicks, the octopus emotes. But a pocket-sized virtual pet can't live on a breadboard forever. It's time to research what a purpose-built Dilder board looks like.

<!-- more -->

## Why a Custom Board?

The current setup is a Pico W on a half-size breadboard with jumper wires running to the e-ink display and a 5-way joystick module. It works on a desk, but it's fragile, bulky (170x55mm), and can't fit in the 3D-printed enclosure (88x34mm). A custom PCB solves all of that — permanent connections, smaller footprint, designed to match the case.

The real question was: how hard is this, and how much does it cost?

## The PicoTop Case Study

To answer that, I reverse-engineered the [PicoTop project](https://github.com/7west/PicoTop/) — a custom RP2350-based computer designed by a single hobbyist. The PicoTop integrates a bare RP2350A chip, 16MB flash, battery charging, an RTC, a micro SD slot, USB host, HDMI output, and a piezo buzzer — all on one PCB.

Key findings:

- **Tool:** KiCad (free, open-source) for schematic and PCB layout
- **Fabrication:** JLCPCB — $2 for 5 boards, with pick-and-place assembly from $8
- **Components:** All sourced from LCSC (integrated with JLCPCB)
- **Iteration:** 14 production revisions over 3 weeks before the final board
- **Total component count:** ~85 SMD parts, all on the top side

The entire manufacturing pipeline is open: KiCad project files, Gerber files, BOM with LCSC part numbers, and component position files — all in the repo. It's a complete blueprint for how a solo developer turns a design into physical hardware.

## What the Dilder Board Needs

Unlike the PicoTop (which outputs to a monitor and takes keyboard input), the Dilder integrates sensors for physical interaction. Here's the target:

| Subsystem | Components |
|-----------|-----------|
| MCU | RP2040 (bare chip) + 2MB flash + 12MHz crystal |
| Display | e-Paper SPI connector (GP8-13) |
| Input | 5-way joystick pads (GP2-6) |
| Audio | Piezo buzzer (GP15, PWM) |
| Sensors (I2C) | LSM6DSO (steps), MPR121 (touch), BH1750 (light), BME280 (temp) |
| Microphone | MAX9814 (analog, GP26 ADC) |
| Power | MCP73831 LiPo charger + USB-C + battery connector |
| Expansion | 10-pin header: I2C, UART, SWD, GPIO |
| Future (DNP) | GPS (PA1010D), magnetometer (QMC5883L) |

Total GPIO used: 16 of 26. Total estimated cost: **~$21 per board** in a 5-board run with full PCBA assembly.

## The RP2040 Minimal Circuit

The RP2040 needs surprisingly little external circuitry:

- The chip itself ($0.70)
- A Winbond W25Q flash chip ($0.35)
- A 12MHz crystal + two load caps
- An XC6206 3.3V LDO ($0.15)
- ~10 decoupling capacitors
- USB-C with series resistors and CC resistors

Total for the minimal MCU circuit: about **$2 in components**. That's it. Everything else is the peripherals you choose to add.

## The Learning Path

I mapped out a 15-week plan:

1. **Weeks 1-2:** Learn KiCad through tutorials and a practice LED board
2. **Weeks 3-6:** Design and order a V0 breakout (just RP2040 + flash + USB)
3. **Weeks 7-12:** Design the full Dilder V1 board with all sensors
4. **Weeks 13+:** Test, iterate, fit to enclosure

The first board will probably have issues — that's expected. The PicoTop went through 14 revisions. Budget for at least 2-3 board orders.

## Resources That Made This Click

- **RP2040 Hardware Design Guide** — the official PDF from Raspberry Pi, covers everything
- **Phil's Lab on YouTube** — the best PCB design tutorials on the internet
- **PicoTop KiCad files** — a real, working custom RP2350 board to study
- **JLCPCB Fabrication Toolkit** — KiCad plugin that exports manufacturing files with one click

The full research document is in the [docs folder](https://github.com/rompasaurus/dilder/blob/main/docs/custom-pcb-design-research.md) — 14 sections covering every aspect from the PicoTop teardown to fabrication service pricing to a risk assessment.

## What's Next

The immediate plan: order a Pico W and continue firmware development on the breadboard (Phase 3A — core game loop). In parallel, start learning KiCad with the practice projects outlined in the research. When the firmware is stable, the board design can begin in earnest.

The custom board is a Phase 5-6 milestone, but the research is done. The path from here to a purpose-built Dilder is clear.
