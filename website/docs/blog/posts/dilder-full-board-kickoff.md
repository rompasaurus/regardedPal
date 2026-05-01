---
date: 2026-05-01
authors:
  - rompasaurus
categories:
  - Hardware
tags:
  - pcb
  - kicad
  - planning
  - freecad
---

# Kicking Off the Dilder Full Board — One PCB to Carry Everything

For two months Dilder has been a constellation of off-the-shelf modules wired together on a breadboard: a Raspberry Pi Pico 2 W, a Waveshare e-paper HAT, a TP4056 charger module, a GY-6500 IMU breakout, two AAA cells, a 20 mm piezo, a 62×36 mm solar panel, and the hand-routed joystick PCB I sent to JLCPCB last month. The 3D-printed case has been growing pockets and rails for each new piece. The next step is the obvious one: collapse it all onto a single PCB.

This post is the kickoff for that work.

<!-- more -->

## The component list comes from FreeCAD, not the BOM

The first thing I tried was the canonical move: open `BOM.md`, list every part, find a reference design for each, build the schematic from there. Within ten minutes I'd written a markdown file that didn't match the actual project. The BOM is a snapshot from a different design direction (bare ESP32-S3-WROOM-1 module, AMS1117 LDO, etc.). The thing I'm *actually* building lives in the FreeCAD parametric macro at `hardware-design/freecad-mk2/dilder_rev2_mk2.FCMacro` — every body that macro instantiates has a position in the enclosure, a hole drilled for it, a rail to clip it, a pocket sized to its datasheet dimensions. Anything *not* in the macro is hypothetical.

So I rewrote the kickoff doc with the macro as the source of truth. The component list now reads off `add_pico_with_headers`, `add_joystick_pcb`, `add_peripherals` (TP4056 + AAA cells + battery clips + e-paper module), `add_imu_module`, `add_piezo_speaker`, `add_solar_panel`, and the 3D-printed `Thumbpiece`. Ten parts that the case is already shaped around.

That immediately surfaced an interesting wrinkle.

## Module-on-headers vs. bare-IC

The macro builds the system around a **Raspberry Pi Pico 2 W** sitting on a 2×20 castellated header — i.e. an off-the-shelf assembled board you solder onto pins. The BOM I drafted earlier was for a board that would carry the **bare ESP32-S3-WROOM-1** module. These are very different PCB jobs:

| Approach | What the new PCB has to do |
|----------|---------------------------|
| **Pico 2 W on headers** (what the macro models) | Header sockets, power glue, connectors. No flash, no crystal, no USB-C — those live on the Pico. |
| **Bare ESP32-S3 module** (BOM v0.3) | Carry the MCU + decoupling + USB-C with CC pull-downs + LDO + protection. |

The macro is a commitment. The case has been printed five times around the Pico 2 W's exact 51 × 21 mm footprint. So the Full Board is a *carrier* for the Pico, not a replacement for it. That decision propagates everywhere: which reference designs I open, which footprints I import, which sub-sheets the schematic gets divided into.

I flagged the asymmetry in §2 of the new doc, but the working assumption from this point on is module-on-headers.

## What's in the new doc

The kickoff document at `hardware-design/PCB Designs/Dilder Full Board/COMPONENTS-AND-IMPORT-GUIDE.md` does two jobs:

**1. Per-component reference map.** For every body the FreeCAD macro instantiates, the doc points to the exact KiCad project on disk where that part is wired correctly. Examples:

- Pico 2 W → `hardware-design/reference-boards/rp2040-pico-usbc/KiCad Projects/Pico WH - No License/`
- TP4056 + DW01A + FS8205A → `hardware-design/examples/09-bitwiseajeet-tp4056/`
- I²C sensor bus topology → `hardware-design/examples/10-klp5e-sensor-board/KiCad project/sensors.kicad_sch`
- E-paper SPI wiring → `hardware-design/reference-boards/esp32s3-ducky-epaper/`
- Joystick footprint and STEP → `hardware-design/PCB Designs/joystick-pcb-by-hand/JoystickBoardDilder/`

Eleven reference projects, all already cloned, all openable directly with `kicad <project>.kicad_pro`. No internet required.

**2. KiCad import playbook.** There are four ways to bring an existing schematic into a new project, and they are not interchangeable:

| Goal | Mechanism |
|------|-----------|
| Pull a whole sub-circuit onto your sheet | **File → Append Schematic Sheet Content** |
| Link an entire sheet as a hierarchical sub-page | **Place → Add Hierarchical Sheet** |
| Cherry-pick parts between two open windows | **Edit → Copy / Paste** |
| Reuse just the symbol or footprint | **Manage Symbol/Footprint Libraries** |

The doc walks through each, including what gets preserved (wires, net labels, footprint *strings*), what breaks (custom symbol libraries, refdes collisions, hierarchical labels with no parent counterpart), and how to fix each.

## The five-sheet plan

The schematic gets divided to mirror the macro's grouping:

```
dilder-full-board.kicad_sch (parent)
├── pico.kicad_sch       — 2×20 header, GPIO labels (the spine)
├── power.kicad_sch      — TP4056 pads, battery, solar + Schottky
├── sensors.kicad_sch    — IMU header, future AHT20 / BH1750 stubs on shared I²C
├── display.kicad_sch    — e-paper HAT routing or 8-pin JST-SH break-out
└── io.kicad_sch         — joystick K1-1506SN-01, piezo disc
```

Hierarchical labels (`SDA`, `SCL`, `SPI_SCK`, `EPD_*`, `JOY_*`, `PIEZO`, `3V3`, `GND`, `VBUS`, `VBAT`) tie them to the parent. This is the same architectural pattern as `examples/10-klp5e-sensor-board/` — the cleanest hierarchical reference in the collection.

## What's next

Skeleton project creation is a manual KiCad step (deliberately — I've been avoiding programmatic schematic generation in favor of doing this by hand to actually learn the tool). After that:

1. Add libraries — joystick `.pretty`, JLCPCB libs.
2. Build the five empty sub-sheets.
3. Wire the Pico header sheet first; it's the spine the others tie into.
4. Append the TP4056 charger block from `examples/09-bitwiseajeet-tp4056/`.
5. Wire sensors with stubs reserved for the v0.5 AHT20 + BH1750 additions.
6. Decide between HAT-on-header or 8-pin JST-SH for the e-paper.
7. ERC, then route against the macro's enclosure constraints (`enc_x = 96.9 mm`, `enc_y = 46.0 mm`).

The macro tells me where everything has to land in space. The reference designs tell me how everything has to wire up. The job in between is mine.

[Component & Import Guide :material-arrow-right:](https://github.com/rompasaurus/dilder/blob/main/hardware-design/PCB%20Designs/Dilder%20Full%20Board/COMPONENTS-AND-IMPORT-GUIDE.md){ .md-button }
