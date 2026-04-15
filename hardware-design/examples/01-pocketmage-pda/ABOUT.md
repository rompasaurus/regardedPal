# PocketMage PDA

## Overview

An E-Ink PDA (Personal Digital Assistant) built around the ESP32-S3. Features a dual-display design with both an E-Ink screen and a small OLED working in tandem to mitigate e-ink refresh rate limitations. Full handheld device with a custom keyboard PCB.

## Origin & Backstory

Created by GitHub user **ashtf8**. The PocketMage is a passion project to build a modern, open-source PDA using e-ink technology. The dual-display approach is clever — the OLED handles fast UI feedback (menus, cursor) while the e-ink display shows persistent content (text, documents). This solves the biggest UX problem with e-ink: the slow refresh rate. The project has accumulated ~1800 GitHub stars, making it one of the most popular open-source ESP32 e-ink hardware designs.

## Relevance to Dilder

**Highest relevance** — this is the closest match to the Dilder project:

| Feature | PocketMage | Dilder |
|---------|-----------|--------|
| MCU | ESP32-S3 | ESP32-S3-WROOM-1-N16R8 |
| Display | E-Ink + OLED | E-Ink (Waveshare 2.13") |
| Power | LiPo battery | LiPo battery + TP4056 |
| Input | Custom keyboard | 5-way joystick |
| USB | USB-C | USB-C |
| Form factor | Handheld PDA | Handheld pet device |

## Key Takeaways for Dilder

- Dual-board design (screen + keyboard) — shows how to split a handheld into modular PCBs
- E-ink SPI interface wiring is a direct reference for our Waveshare display
- Custom KiCad symbol libraries for specialized parts
- Battery management circuit design

## KiCad Files

```
Docs/Documents & Advanced/PCB/V3.3/
├── einkPDA_screen/
│   ├── einkPDA_screen.kicad_pro
│   ├── einkPDA_screen.kicad_sch
│   └── einkPDA_screen.kicad_pcb
└── einkPDA_keyboard/
    ├── einkPDA_keyboard.kicad_pro
    ├── einkPDA_keyboard.kicad_sch
    ├── einkPDA_keyboard.kicad_pcb
    └── CustomParts.kicad_sym
```

## Links

- **Repository:** https://github.com/ashtf8/PocketMage_PDA
- **License:** Apache-2.0
- **Stars:** ~1800
