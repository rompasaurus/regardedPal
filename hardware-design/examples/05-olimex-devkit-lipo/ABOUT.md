# OLIMEX ESP32-DevKit-LiPo

## Overview

The original OLIMEX LiPo-enabled ESP32 development board (not S3). Pin-compatible with Espressif's ESP32-DevKitC but adding LiPo battery charging. Notable for having **four hardware revisions** (A1 through D) all available in the repo, making it an exceptional study in how a PCB design evolves through multiple iterations.

## Origin & Backstory

This was OLIMEX's first ESP32 board with integrated battery support, predating the S3 variant. The four revision history tells a story: Rev A1 was the initial design, each subsequent revision fixed issues, improved layouts, or updated components based on production feedback and component availability. Having all revisions in one repo is unusual and extremely valuable for learning — you can diff the schematics and PCBs to see what changed and why.

## Relevance to Dilder

| Feature | OLIMEX ESP32 | Dilder |
|---------|-------------|--------|
| MCU | ESP32-WROOM-32 | ESP32-S3-WROOM-1-N16R8 |
| Power | LiPo + charger | LiPo + TP4056 |
| USB | Micro-USB (older revs) → USB-C (newer) | USB-C |
| Revisions | 4 (A1, B, C, D) | v0.3 (first ESP32-S3 rev) |

## Key Takeaways for Dilder

- **Design evolution across 4 revisions** — the single most valuable learning resource here. Compare Rev A1 to Rev D to understand what production experience teaches
- **LiPo charging circuit maturation** — see how the charging circuit was refined over time
- **USB connector evolution** — some revisions switched connector types
- **Component substitution** — later revisions may swap parts for better availability or lower cost
- **PCB layout optimization** — each revision likely improved routing and component placement

## KiCad Files

```
HARDWARE/
├── ESP32-DevKit-LiPo-Rev.A1/
│   ├── ESP32-DevKit-Lipo_Rev_A1.sch
│   └── ESP32-DevKit-Lipo_Rev_A1.kicad_pcb
├── ESP32-DevKit-LiPo-Rev.B/
│   ├── ESP32-DevKit-Lipo_Rev_B.sch
│   └── ESP32-DevKit-Lipo_Rev_B.kicad_pcb
├── ESP32-DevKit-LiPo-Rev.C/
│   ├── ESP32-DevKit-Lipo_Rev_C.sch
│   └── ESP32-DevKit-Lipo_Rev_C.kicad_pcb
└── ESP32-DevKit-LiPo-Rev.D/
    ├── ESP32-DevKit-Lipo_Rev_D.sch
    └── ESP32-DevKit-Lipo_Rev_D.kicad_pcb
```

## Links

- **Repository:** https://github.com/OLIMEX/ESP32-DevKit-LiPo
- **License:** Apache-2.0
- **Stars:** ~89
- **Manufacturer:** https://www.olimex.com
