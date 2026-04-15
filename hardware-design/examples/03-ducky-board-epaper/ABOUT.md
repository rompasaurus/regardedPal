# Ducky Board — ESP32-S3 with 1.52" E-Paper Display

## Overview

A compact breakout board pairing the ESP32-S3 with a 1.52" e-paper display. Designed in KiCad 9 with native USB-C programming support and an integrated Li-Ion battery charger. Minimal, focused design — just the essentials for a battery-powered e-ink project.

## Origin & Backstory

Created by **MakersFunDuck**. The Ducky Board is a straightforward "get it working" design that combines the three core pieces most e-ink projects need: ESP32-S3 module, e-paper display connector, and battery charging. Unlike more ambitious projects, this one stays lean — no extra sensors, no audio, no SD card. That simplicity makes it an excellent reference for understanding the bare minimum wiring needed for an ESP32-S3 + e-paper + battery design.

## Relevance to Dilder

**High relevance** — the most architecturally similar design to Dilder's core:

| Feature | Ducky Board | Dilder |
|---------|------------|--------|
| MCU | ESP32-S3 | ESP32-S3-WROOM-1-N16R8 |
| Display | 1.52" e-paper (SPI) | 2.13" e-paper (SPI) |
| Power | Li-Ion + charger + USB-C | LiPo + TP4056 + USB-C |
| Extras | None | Joystick, IMU |
| Design tool | KiCad 9 | KiCad 10 |

## Key Takeaways for Dilder

- **Simplest ESP32-S3 + e-paper reference** — minimal design to compare against
- **Battery charger integration** — different charger IC but same topology
- **KiCad 9 project** — modern KiCad format, easy to open
- **E-paper SPI wiring** — direct reference for display connections
- Demonstrates that a functional e-ink device can be very compact

## KiCad Files

```
hardware.kicad_pro
hardware.kicad_sch
hardware.kicad_pcb
```

## Links

- **Repository:** https://github.com/MakersFunDuck/Ducky-board-ESP32-S3-with-1.52-inch-e-paper-display
- **License:** GPL-3.0
- **Stars:** ~12
