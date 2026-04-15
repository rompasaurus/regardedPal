# Lilka DIY Gaming Console

## Overview

An open-source DIY educational gaming console from Ukraine, built on the ESP32-S3. Features a 1.69" IPS display (ST7789, 280x240), physical navigation buttons (D-pad style), I2S audio speaker, microSD card slot, and USB-C. Runs KeiraOS (FreeRTOS-based) and can play NES games and even DOOM.

## Origin & Backstory

Created by the **lilka-dev** community in Ukraine. "Lilka" means "lily" in Ukrainian. The project was designed as an educational platform to teach electronics, embedded programming, and game development. Multiple hardware revisions (v1 and v2) show the design evolution — notably, earlier versions used shift registers for button multiplexing which were later removed in favor of direct GPIO connections. The project has ~220 stars and an active community.

## Relevance to Dilder

**Highest relevance** — a complete handheld gaming device very similar in concept to a Tamagotchi:

| Feature | Lilka | Dilder |
|---------|-------|--------|
| MCU | ESP32-S3 | ESP32-S3-WROOM-1-N16R8 |
| Display | 1.69" IPS (SPI) | 2.13" E-Ink (SPI) |
| Input | D-pad + buttons | 5-way joystick |
| Audio | I2S speaker | — |
| Storage | microSD | — |
| Power | Battery + USB-C | LiPo + TP4056 + USB-C |
| Form factor | Handheld console | Handheld pet device |

## Key Takeaways for Dilder

- **Button wiring evolution** — v1 used shift registers, v2 uses direct GPIO. The Dilder uses direct GPIO too (GPIO4-8), so v2 is the relevant reference
- **Two hardware revisions** to study — shows how a design matures
- **Rounded PCB outline** variant (main_rounded.kicad_pcb) — useful if Dilder wants ergonomic board shape
- **SPI display interface** — different display but same SPI bus patterns
- **Complete handheld device** — enclosure integration, battery placement, button ergonomics

## KiCad Files

```
hardware/
├── v1/
│   ├── main.kicad_pro
│   ├── main.kicad_sch
│   ├── main.kicad_pcb
│   └── old/main_before_removed_shift_register.kicad_sch
└── v2/
    ├── main.kicad_pro
    ├── main.kicad_sch
    ├── main.kicad_pcb
    ├── main_rounded.kicad_pro
    ├── main_rounded.kicad_pcb
    └── old/main_before_removed_shift_register.kicad_sch
```

## Links

- **Repository:** https://github.com/lilka-dev/lilka
- **License:** GPL-2.0
- **Stars:** ~220
