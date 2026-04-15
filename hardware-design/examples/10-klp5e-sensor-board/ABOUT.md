# KLP-5e ESP32 Sensor Board

## Overview

A custom PCB for IoT applications built around the ESP32-C3 with an integrated **TP4056 Li-ion battery charger** IC. Well-documented educational project from the "KLP" (KiCad Learn PCB) series. Features hierarchical schematics with separate sheets for MCU, sensors, and user interface. Designed as a teaching tool for KiCad PCB design.

## Origin & Backstory

Created by **futureshocked** (Peter Dalmaris), an educator and author who runs tech education courses. The KLP-5e is part of a series designed to teach PCB design using KiCad. This makes it particularly well-organized and well-commented — the schematics are meant to be read and understood by learners. The hierarchical sheet structure is clean and deliberate, not just a convenience. With ~89 stars, it has solid community adoption for an educational project.

## Relevance to Dilder

| Feature | KLP-5e | Dilder |
|---------|--------|--------|
| MCU | ESP32-C3 | ESP32-S3-WROOM-1-N16R8 |
| Charger | **TP4056** | **TP4056** |
| USB | USB-C | USB-C |
| Sensors | Multiple (sub-sheet) | MPU-6050 IMU |
| Organization | Hierarchical sheets | Single sheet (generated) |

## Key Takeaways for Dilder

- **Educational quality schematics** — designed to be read and learned from, so component values and connections are well-annotated
- **TP4056 charging circuit** — another reference implementation of the same charger IC
- **Hierarchical schematic best practices** — if Dilder's schematic needs to be split into sheets later, this is the model to follow
- **Sensor integration patterns** — how to organize multiple sensors on a separate schematic sheet
- **User interface sub-sheet** — buttons, LEDs, and status indicators organized cleanly

## KiCad Files

```
KiCad project/
├── ESP32 sensor board.kicad_pro    (project file)
├── ESP32 sensor board.kicad_sch    (top-level schematic)
├── ESP32 sensor board.kicad_pcb    (PCB layout)
├── ESP32-C3-02.kicad_sch           (ESP32-C3 sub-sheet)
├── sensors.kicad_sch                (sensor sub-sheet)
└── user_interface.kicad_sch         (UI sub-sheet)
```

## Links

- **Repository:** https://github.com/futureshocked/KLP-5e-ESP32-sensor-board
- **License:** Not specified
- **Stars:** ~89
- **Author:** Peter Dalmaris (futureshocked)
