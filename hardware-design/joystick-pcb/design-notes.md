# Joystick Breakout PCB — Design Notes

## Overview

A minimal 20x20mm breakout PCB that mounts an Alps Alpine SKRHABE010 5-direction
SMD navigation switch and routes all 6 signals (5 directions + GND) to through-hole
wire pads for connection to the ESP32-S3 main board.

## Enclosure Constraints

These dimensions come from the top cover's PCB pocket (see `rev2-models-dimensions.md` section 4.3):

- **Pocket size:** 20 x 20 x 1.0 mm (XY footprint, Z depth)
- **Pocket location:** X 68.70–88.70, Y 12.00–32.00 mm (enclosure coords)
- **Joystick through-hole above:** 12mm dia at bottom, 15mm tapered at top
- **Joystick center offset:** PCB center is at (78.70, 22.00), but the joystick
  actuator must align with the through-hole at (79.35, 22.00) — so the switch
  is placed 0.65mm in the +X direction from board center
- **Mounting holes:** 4x M3 clearance (3.2mm), 2.5mm inset from corners,
  15mm pitch. Currently removed from enclosure (dimples only on first print)
  but the PCB has them for when reinstated.

## PCB Specs

- **Size:** 20 x 20 mm (exact pocket fit)
- **Thickness:** 1.0 mm (matches pocket depth — board sits flush)
- **Layers:** 2 (all routing on F.Cu, B.Cu available if needed)
- **Trace width:** 0.3 mm (signal only, no power)
- **Minimum clearance:** 0.2 mm

## Circuit

No active components. The board is purely a mechanical adapter:

```
SW1 (SKRHABE010)          J1 (wire pads)
─────────────────         ────────────────
Pin 1 (UP)      ────────→ Pin 1  → GPIO4
Pin 2 (DOWN)    ────────→ Pin 2  → GPIO5
Pin 3 (LEFT)    ────────→ Pin 3  → GPIO6
Pin 4 (RIGHT)   ────────→ Pin 4  → GPIO7
Pin 5 (CENTER)  ────────→ Pin 5  → GPIO8
Pin 6 (COM/GND) ────────→ Pin 6  → GND
```

No pull-up resistors needed — ESP32-S3 internal pull-ups are enabled in firmware.
No decoupling caps needed — this is a passive switch circuit.

## Pin Mapping (SKRHABE010 datasheet → physical direction)

The SKRHABE010 labels its pins A, B, C, D, CNTR, and COMM. The mapping to
physical directions depends on component orientation on the PCB:

| Datasheet Pin | Physical Dir | Schematic Net | J1 Pin |
|---------------|-------------|---------------|--------|
| A (pin 1) | UP | JOY_UP | 1 |
| C (pin 2) | DOWN | JOY_DOWN | 2 |
| B (pin 3) | LEFT | JOY_LEFT | 3 |
| D (pin 4) | RIGHT | JOY_RIGHT | 4 |
| CNTR (pin 5) | CENTER | JOY_CENTER | 5 |
| COMM (pin 6) | — | GND | 6 |

**Verify direction mapping after first board assembly** — the A/B/C/D to
UP/DOWN/LEFT/RIGHT mapping depends on the physical orientation of the switch
on the board. If directions are swapped, update the pin assignments in firmware
(simpler than re-spinning the PCB).

## Ordering

### JLCPCB (recommended)
1. Export Gerbers from KiCad (File → Plot)
2. Export drill files (Generate Drill Files in Plot dialog)
3. Zip all Gerber + drill files
4. Upload to jlcpcb.com → Instant Quote
5. For PCBA: upload BOM CSV and CPL (pick-and-place) file
6. Select SKRHABE010 → LCSC C139794

### PCBWay (alternative)
1. Same Gerber export
2. Upload to pcbway.com
3. For assembly: provide BOM, they source from distributors

## KiCad Project Files

```
joystick-pcb/
├── joystick-pcb.kicad_pro    # KiCad 8 project
├── joystick-pcb.kicad_sch    # Schematic
├── joystick-pcb.kicad_pcb    # PCB layout
├── BOM.md                    # Bill of materials
└── design-notes.md           # This file
```

## JLCPCB BOM CSV (for PCBA upload)

```csv
Comment,Designator,Footprint,LCSC Part Number
SKRHABE010,SW1,SMD-8P_7.5x7.5mm,C139794
```

## JLCPCB CPL (pick-and-place) CSV

```csv
Designator,Mid X,Mid Y,Rotation,Layer
SW1,10.65,10.0,0,top
```

(Origin at board bottom-left corner. Adjust rotation after first order if
directions are wrong.)
