# BitwiseAjeet — ESP32 PCB with TP4056

## Overview

A compact, low-power IoT system using the ESP32-C3 with an integrated **TP4056 Li-Ion battery charger** — the exact same charger IC used in the Dilder. USB-C for charging and programming. Includes battery protection circuitry, sensor integration, and a user interface sub-sheet. Uses hierarchical schematics in KiCad.

## Origin & Backstory

Created by **BitwiseAjeet**. This is a practical IoT board designed for sensor data collection with battery power. The standout value is the **TP4056 charging circuit implementation in KiCad** — since Dilder uses the same TP4056 charger IC, this is a direct reference for how to wire it up, including the PROG resistor, charge/standby LEDs, and battery protection (DW01A + FS8205A or equivalent). The hierarchical schematic approach (separate sheets for MCU, sensors, UI) is also a good organizational model.

## Relevance to Dilder

**High relevance** — exact TP4056 charger IC match:

| Feature | BitwiseAjeet | Dilder |
|---------|-------------|--------|
| MCU | ESP32-C3 | ESP32-S3-WROOM-1-N16R8 |
| Charger | **TP4056** | **TP4056** |
| USB | USB-C | USB-C |
| Sensors | Various (hierarchical sheet) | MPU-6050 IMU |
| Battery protection | Yes | DW01A + FS8205A |

## Key Takeaways for Dilder

- **TP4056 wiring reference** — compare their PROG resistor value, LED wiring, and protection circuit against Dilder's implementation
- **Hierarchical schematics** — separate sheets for ESP32, sensors, and UI make the design easier to navigate
- **Battery protection topology** — verify Dilder's DW01A/FS8205A wiring against this reference
- **USB-C + charging integration** — how VBUS feeds into the TP4056
- **Sensor sub-sheet** — model for organizing peripheral connections

## KiCad Files

```
ESP32 PCB.kicad_pro          (project file)
ESP32 PCB.kicad_sch          (top-level schematic)
ESP32 PCB.kicad_pcb          (PCB layout)
ESP32-C3-02.kicad_sch        (ESP32-C3 sub-sheet)
sensors.kicad_sch             (sensor sub-sheet)
USER INTERFACE.kicad_sch      (UI sub-sheet)
```

## Links

- **Repository:** https://github.com/BitwiseAjeet/ESP32_BASED_PCB-KiCAD
- **License:** MIT
- **Stars:** ~3
