# OLIMEX ESP32-S3-DevKit-LiPo

## Overview

A professional-grade, certified Open Source Hardware (OSHW) ESP32-S3 development board from OLIMEX — a well-established Bulgarian electronics manufacturer. Features JTAG and USB-OTG support, LiPo charging circuit, 8MB PSRAM, 8MB flash. This is a production-quality reference design with proper ESD protection, power regulation, and signal integrity considerations.

## Origin & Backstory

OLIMEX has been making open-source hardware since 2004 and is one of the most respected names in the OSHW movement. Their ESP32-S3-DevKit-LiPo was designed as a drop-in replacement for Espressif's official DevKitC but with the added LiPo charging capability that the official board lacks. The design went through multiple revisions (currently Rev B) and includes proper mechanical dimensions files for enclosure design. OLIMEX designs are known for being conservative and reliable — they prioritize proven circuits over cutting-edge features.

## Relevance to Dilder

| Feature | OLIMEX S3 | Dilder |
|---------|----------|--------|
| MCU | ESP32-S3-WROOM-1 | ESP32-S3-WROOM-1-N16R8 |
| Power | LiPo charger + LDO | LiPo + TP4056 + AMS1117-3.3 |
| USB | USB-C (JTAG + OTG) | USB-C (OTG only) |
| ESD | Proper protection | Basic CC pull-downs |
| Form factor | Dev board (breadboard-compatible) | Custom handheld |

## Key Takeaways for Dilder

- **Professional ESP32-S3 power design** — study their voltage regulation and decoupling strategy
- **LiPo charging circuit** — OLIMEX's approach to battery management (likely different IC than TP4056)
- **ESD protection on USB** — if you add USBLC6-2SC6 later, this is a reference
- **Mechanical dimensions file** — useful for 3D enclosure integration
- **Production-proven design** — the kind of conservative choices that survive manufacturing

## KiCad Files

```
HARDWARE/
├── ESP32-S3-DevKit-LiPo_Rev_B/
│   ├── ESP32-S3-DevKit-LiPo_Rev_B.kicad_pro
│   ├── ESP32-S3-DevKit-LiPo_Rev_B.sch
│   └── ESP32-S3-DevKit-LiPo_Rev_B.kicad_pcb
└── Dimensions/
    └── ESP32-S3-DevKit-LiPo_Rev_B_DIMM.kicad_pcb
```

## Links

- **Repository:** https://github.com/OLIMEX/ESP32-S3-DevKit-LiPo
- **License:** GPL-3.0
- **Stars:** ~35
- **Manufacturer:** https://www.olimex.com
