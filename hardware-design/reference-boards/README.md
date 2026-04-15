# Reference Board Designs

Open-source KiCad board designs collected as reference material for the Dilder custom PCB. Each folder contains a complete KiCad project (schematic + PCB layout) that can be opened directly in KiCad 7+.

These are **not** Dilder designs — they are third-party projects whose circuits, layouts, and component choices serve as learning resources and validation for our own board.

---

## Pico / RP2040 Reference Designs

### [rp2040-pico-usbc/](rp2040-pico-usbc/) — Reverse-Engineered Pico with USB-C

| Attribute | Value |
|-----------|-------|
| **MCU** | RP2040 (Pico), RP2040 + CYW43439 (Pico WH), RP2350 (Pico 2) |
| **Source** | [sabogalc/project-piCo](https://github.com/sabogalc/project-piCo) |
| **License** | WTFPL (unrestricted) |
| **KiCad files** | 3 sub-projects: Pico C, Pico WH, Pico 2 C — each with `.kicad_sch` + `.kicad_pcb` |
| **Relevance** | Full reverse-engineered Pico schematic — shows the official RP2040 circuit (crystal, flash, power, USB) faithfully reproduced in KiCad with USB-C upgrade. Essential reference for understanding the Pico's power path and how VSYS/VBUS interact. |

### [rp2040-minimal-jlcpcb/](rp2040-minimal-jlcpcb/) — RP2040 Minimal Design (JLCPCB-Ready)

| Attribute | Value |
|-----------|-------|
| **MCU** | RP2040 (bare chip) |
| **Source** | [tommy-gilligan/RP2040-minimal-design](https://github.com/tommy-gilligan/RP2040-minimal-design) |
| **License** | BSD-3-Clause |
| **KiCad files** | `RP2040_minimal.kicad_sch` + `.kicad_pcb` |
| **Relevance** | Raspberry Pi's official RP2040 Minimal Viable Board ported to KiCad 7 with JLCPCB assembly files. Demonstrates the absolute minimum circuit for a working RP2040 board: crystal, flash, decoupling, USB. Good for understanding which components are mandatory vs optional. |

### [rp2040-designguide/](rp2040-designguide/) — RP2040 Hardware Design Guide

| Attribute | Value |
|-----------|-------|
| **MCU** | RP2040 (bare chip) |
| **Source** | [Sleepdealr/RP2040-designguide](https://github.com/Sleepdealr/RP2040-designguide) |
| **License** | MIT |
| **KiCad files** | `PCB/RP2040-Guide.kicad_sch` + `.kicad_pcb` + custom libraries |
| **Relevance** | Comprehensive design guide with recommended components (XC6206 LDO, specific crystal, flash). Includes custom KiCad symbol/footprint libraries. Originally for mechanical keyboard use (QMK/Vial) but the RP2040 circuit design is universally applicable. Good for learning component selection rationale. |

---

## ESP32-S3 Reference Designs

### [esp32s3-basic-devboard/](esp32s3-basic-devboard/) — Minimal ESP32-S3 Dev Board

| Attribute | Value |
|-----------|-------|
| **MCU** | ESP32-S3-WROOM-1 module |
| **Source** | [atomic14/basic-esp32s3-dev-board](https://github.com/atomic14/basic-esp32s3-dev-board) |
| **License** | MIT |
| **KiCad files** | `dev-board.kicad_sch` + `.kicad_pcb` + `.kicad_pro` |
| **Features** | USB-C with proper CC resistors, LDO regulator, reset/boot buttons, 3 status LEDs, all GPIO broken out |
| **Relevance** | The closest minimal reference for the Dilder's ESP32-S3 circuit. Shows proper USB-C implementation (5.1k CC pull-downs, differential pair routing for D+/D-), LDO power design, and GPIO breakout. Intentionally simple — no battery charging, no sensors. Use this to validate the core ESP32-S3 power and USB design. |

### [esp32s3-ducky-epaper/](esp32s3-ducky-epaper/) — ESP32-S3 + e-Paper + Battery Charger

| Attribute | Value |
|-----------|-------|
| **MCU** | ESP32-S3 module |
| **Display** | GDEM0154Z91 (1.52" e-ink, 3-color, Good Display) |
| **Source** | [MakersFunDuck/Ducky-board-ESP32-S3](https://github.com/MakersFunDuck/Ducky-board-ESP32-S3-with-1.52-inch-e-paper-display) |
| **License** | GPL-3.0 |
| **KiCad files** | `hardware.kicad_sch` + `.kicad_pcb` + `.kicad_pro` |
| **Features** | USB-C, Li-Ion battery charger with status LEDs, e-ink display connector, compact breakout |
| **Relevance** | **The closest overall match to the Dilder board.** Same MCU family, same display technology, same battery charging architecture. The schematic for ESP32-S3 power sequencing, USB-C implementation, and LiPo charging circuit can be directly referenced. Component footprints and LCSC part numbers are manufacturing-optimized. |

### [espressif-kicad-libs/](espressif-kicad-libs/) — Official Espressif KiCad Libraries

| Attribute | Value |
|-----------|-------|
| **Contents** | KiCad symbols, footprints, and 3D models for all Espressif chips and modules |
| **Source** | [espressif/kicad-libraries](https://github.com/espressif/kicad-libraries) |
| **License** | Apache-2.0 |
| **Includes** | ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6, ESP32-H2 — chips, modules, and DevKits |
| **Relevance** | Official symbols and footprints for the ESP32-S3-WROOM-1-N16R8 module. These are the authoritative reference for pin assignments, pad dimensions, and antenna keep-out zones. Install via KiCad PCM for automatic updates, or reference this local copy for offline work. |

---

## Virtual Pet Reference Designs

### [opentama-virtual-pet/](opentama-virtual-pet/) — OpenTama (Tamagotchi Reference Board)

| Attribute | Value |
|-----------|-------|
| **MCU** | STM32L072 (ARM Cortex-M0+) |
| **Display** | SPI SSD1306 OLED or SPI UC1701x LCD |
| **Battery** | 1000mAh LiPo (40x30x12mm) |
| **Input** | 3 tactile buttons |
| **Source** | [Sparkr-tech/opentama](https://github.com/Sparkr-tech/opentama) |
| **License** | CERN-OHL-S v2 (open hardware) |
| **KiCad files** | `OpenTama.kicad_sch` + `.kicad_pcb` |
| **Relevance** | **Same product category** (virtual pet), same target fab (JLCPCB), same battery spec (1000mAh LiPo). All components on one side for JLCPCB assembly. LCSC part numbers pre-assigned. Different MCU (STM32 vs ESP32-S3) but the power management, button input, battery protection (DW01A + FS8205A), and display interface circuits are directly applicable. The CERN-OHL-S v2 license explicitly permits derivative works. |

---

## How to Use These References

1. **Open in KiCad:** Navigate to any folder and open the `.kicad_pro` file. The schematic (`.kicad_sch`) and PCB layout (`.kicad_pcb`) will load with their original libraries.

2. **Compare circuits:** Use the schematic editor to compare reference designs with Dilder's schematic at `../Board Design kicad/dilder.kicad_sch`. Check power management, USB, and decoupling approaches.

3. **Validate footprints:** Compare component footprints between reference boards and Dilder's BOM to ensure pad dimensions and thermal reliefs match JLCPCB requirements.

4. **Study routing:** Examine PCB layouts for routing strategies — especially USB differential pairs, antenna keep-out zones, ground plane stitching, and power trace widths.

---

*Collected: 2026-04-15*
