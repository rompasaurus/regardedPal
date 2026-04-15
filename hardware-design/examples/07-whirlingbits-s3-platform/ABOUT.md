# WhirlingBits ESP32-S3 Platform

## Overview

An ESP32-S3 development platform with SD card, versatile power management (5V and up to 12V input), USB-C, CP2102N USB-UART bridge, and an e-paper schematic reference. The project uses hierarchical schematics extensively — separate sheets for power, USB, SD card, interfaces, and modules — making it an excellent reference for organizing complex KiCad projects.

## Origin & Backstory

Created by **WhirlingBits**. This is a more industrial/IoT-oriented platform designed for flexibility. The standout feature is the hierarchical schematic organization — rather than cramming everything onto one sheet, each functional block gets its own schematic page. The `_schematics/` directory also contains a separate "Smarthome_Epaper" schematic that shows e-paper integration, which is directly relevant to Dilder. The project includes custom footprint libraries for USB4110 connectors and the ESP32-S3-WROOM module.

## Relevance to Dilder

| Feature | WhirlingBits | Dilder |
|---------|-------------|--------|
| MCU | ESP32-S3-WROOM | ESP32-S3-WROOM-1-N16R8 |
| Display | E-paper reference schematic | E-ink (Waveshare 2.13") |
| Power | Multi-voltage (5V/12V) | 3.7V LiPo → 3.3V |
| USB | USB-C + CP2102N UART bridge | USB-C (native USB) |
| Storage | SD card | — |

## Key Takeaways for Dilder

- **Hierarchical schematic organization** — if Dilder's schematic grows, this shows how to split it into logical sub-sheets (power, MCU, peripherals)
- **E-paper schematic** in `_schematics/Smarthome_Epaper.sch` — direct reference for e-ink wiring
- **Custom ESP32-S3-WROOM footprint** — useful for PCB layout comparison
- **USB-C connector footprint** (USB4110) — alternative USB-C connector to study
- **Power management with wider input range** — useful if Dilder ever needs to support external power

## KiCad Files

```
ESP_S3-CP-24_Platform.sch              (top-level schematic)
ESP_S3-CP-24_Platform_Power.sch        (power sub-sheet)
ESP_S3-CP-24_Platform_USBConverter.sch  (USB-UART bridge)
ESP_S3-CP-24_Platform_Modules.sch      (ESP32-S3 module)
ESP_S3-CP-24_Platform_Ifce.sch         (interfaces)
ESP_S3-CP-24_Platform_uSDCard.sch      (SD card)
ESP_S3-CP-24_Platform.kicad_pcb        (PCB layout)

_schematics/
├── Smarthome_Epaper.sch               (e-paper reference!)
└── file5FC6*.sch                      (additional sheets)
```

## Links

- **Repository:** https://github.com/WhirlingBits/ESP32-S3-Platform
- **License:** MIT
- **Stars:** ~9
