# esp-rs / ESP Rust Board

## Overview

An Espressif-affiliated open hardware board using the ESP32-C3, designed for the Rust embedded ecosystem. Adafruit Feather form factor compatible. Features USB-C, battery charging, well-structured KiCad project with professional schematic quality. While it uses ESP32-C3 (not S3), the power management and USB-C implementation are reference-grade.

## Origin & Backstory

Created by the **esp-rs** organization — the official Rust language support team for Espressif chips. This board was designed specifically to lower the barrier for Rust developers to work with ESP32 hardware. The Feather form factor makes it compatible with a huge ecosystem of add-on boards (called "wings"). The schematic quality is notably high — this is effectively an Espressif-endorsed reference design, just expressed through the Rust community lens. ~634 stars indicates strong community adoption.

## Relevance to Dilder

| Feature | ESP Rust Board | Dilder |
|---------|---------------|--------|
| MCU | ESP32-C3 | ESP32-S3-WROOM-1-N16R8 |
| Power | Battery charging + LDO | LiPo + TP4056 + AMS1117-3.3 |
| USB | USB-C | USB-C |
| Form factor | Feather (compact) | Custom handheld |
| Schematic quality | Professional/reference | Generated script |

## Key Takeaways for Dilder

- **Professional-quality schematic** — arguably the best-organized schematic in this collection, great for learning KiCad best practices
- **Battery charging circuit** — Espressif-endorsed approach to LiPo management
- **USB-C wiring with proper CC handling** — well-documented CC pin treatment
- **Feather pinout standard** — if Dilder ever needs expansion, the Feather ecosystem is worth knowing
- **CERN-OHL-S-2.0 license** — one of the gold-standard open hardware licenses

## KiCad Files

```
hardware/esp-rust-board/
├── esp-rust-board.kicad_pro
├── esp-rust-board.kicad_sch
└── esp-rust-board.kicad_pcb
```

## Links

- **Repository:** https://github.com/esp-rs/esp-rust-board
- **License:** CERN-OHL-S-2.0
- **Stars:** ~634
- **Rust ESP ecosystem:** https://github.com/esp-rs
