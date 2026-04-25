# Joystick Breakout PCB — Design Notes

## Overview

A minimal 20x20mm breakout PCB that mounts an Alps Alpine SKRHABE010 5-direction
SMD navigation switch and routes all 6 signals (5 directions + GND) to through-hole
wire pads for connection to the ESP32-S3 main board.

## Rev 2.0 Redesign (2026-04-26)

Rev 1.0 was hand-routed and had two real bugs:
- The SKRHABE010 footprint pin geometry was made up — pads were on the wrong
  faces of the body and the pinout didn't match the datasheet.
- One wire pad (J1.6, GND) physically overlapped the bottom-left M3 mounting
  hole — the drills would have collided in fab.
- The single-layer routing was unfeasibly convoluted (long detour traces
  with all 90° corners).

Rev 2.0:
- **Footprint**: derived from the [crides/kleeb](https://github.com/crides/kleeb)
  `SKRHA-boss` library (used in production keyboards). The kleeb pad geometry
  is rotated -45° here so pads land axis-aligned (3 on the left edge of the
  body, 3 on the right). Includes the two NPTH alignment-post holes (1.05mm
  and 0.75mm) and the two SMD mechanical anchor pads (top/bottom).
- **Wire pads**: 1.8mm pitch, 1.4mm OD / 0.8mm drill, placed along the
  bottom edge between the two lower M3 holes. All clearances verified
  (0.7mm+ pad-to-hole, 0.4mm+ pad-to-pad, 2.3mm to board edge).
- **Routing**: deferred. The PCB ships with components placed and ratlines
  visible — run Freerouting from KiCad's GUI to generate clean 2-layer
  45° traces (see "Auto-routing" section below).

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
- **Layers:** 2 (F.Cu + B.Cu, both used by autorouter)
- **Trace width:** 0.25 mm default (Freerouting will pick widths)
- **Via:** 0.6mm OD / 0.3mm drill (default Freerouting via)
- **Minimum clearance:** 0.2 mm
- **All routes:** 45° angles only (Freerouting default; no 90° turns)

## Auto-routing with Freerouting (already done in Rev 2.0)

The Rev 2.0 PCB ships **fully routed** by Freerouting v2 (run via the
official `ghcr.io/freerouting/freerouting` Docker image). Routing stats:

- **23 trace segments** + **1 through-hole via**, total length 534 mm
- **8 bends, all 45°** — zero 90° corners
- **0 clearance violations** (per Freerouting), **0 copper DRC violations**
  (per `kicad-cli pcb drc`)
- 6 nets fully connected, 0 unconnected ratlines, 0 schematic-parity issues

To re-run the autorouter (e.g. after pinout/placement changes):

### Headless workflow (used to route Rev 2.0)

```bash
# 1. Export Specctra DSN from the .kicad_pcb (uses pcbnew Python module)
python3 -c "
import pcbnew
b = pcbnew.LoadBoard('joystick-pcb.kicad_pcb')
pcbnew.ExportSpecctraDSN(b, '/tmp/joystick.dsn')
"

# 2. Run Freerouting headless via Docker (no Java needed locally)
docker run --rm -v /tmp:/work \\
  --entrypoint java ghcr.io/freerouting/freerouting:latest \\
  -jar /app/freerouting-executable.jar \\
  -de /work/joystick.dsn -do /work/joystick.ses -mp 100

# 3. Import the .ses session back into the board
python3 -c "
import pcbnew
b = pcbnew.LoadBoard('joystick-pcb.kicad_pcb')
pcbnew.ImportSpecctraSES(b, '/tmp/joystick.ses')
b.Save('joystick-pcb.kicad_pcb')
"

# 4. Verify with KiCad's CLI DRC
kicad-cli pcb drc --output drc.json --format json joystick-pcb.kicad_pcb
```

### GUI workflow (alternative)

In KiCad:
- `File → Export → Specctra DSN…` → `joystick-pcb.dsn`
- Run Freerouting GUI on the DSN; `File → Export Specctra Session…`
- Back in pcbnew: `File → Import → Specctra Session…`

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

## Pin Mapping (per Alps datasheet circuit diagram)

The SKRHABE010 datasheet circuit diagram defines the pin functions:

| SW1 Pin | Datasheet Label | Function          | Schematic Net | J1 Pin (silkscreen) |
|---------|-----------------|-------------------|---------------|---------------------|
| 1 | A      | direction (paired w/ C) | JOY_UP     | 1 (UP)  |
| 2 | Center | center-press contact    | JOY_CENTER | 5 (CT)  |
| 3 | C      | direction (paired w/ A) | JOY_DOWN   | 2 (DN)  |
| 4 | B      | direction (paired w/ D) | JOY_LEFT   | 3 (LT)  |
| 5 | Common | shared return for all 5 | GND        | 6 (GND) |
| 6 | D      | direction (paired w/ B) | JOY_RIGHT  | 4 (RT)  |

A & C form one antipodal direction pair, B & D the perpendicular pair.
Center is the press-down contact. Common is the return path that all 5
active contacts (A/B/C/D/Center) short to when actuated.

**Verify direction mapping after first board assembly** — the *physical*
direction (UP/DOWN/LEFT/RIGHT) of each pad depends on the actuator
orientation, which depends on how the part is placed on the reel. If
directions feel rotated/swapped, fix it in firmware (simpler than respinning
the PCB).

## Mechanical / Geometric Verification (Rev 2.0)

All clearances computed and verified before publishing:

| Pair | Clearance |
|------|-----------|
| Wire pad ↔ nearest M3 hole (drill-to-drill) | 0.74 mm |
| Wire pad ↔ adjacent wire pad (drill-to-drill) | 1.00 mm |
| Wire pad ↔ board edge | 2.30 mm |
| SW1 courtyard ↔ M3 hole (edge-to-edge) | 2.07 mm min |
| NPTH alignment hole ↔ nearest signal pad | 3.61 mm |
| Switch body extent ↔ M3 holes | 2.5 mm+ |

No drills overlap. JLCPCB minimum drill-to-drill is typically 0.5 mm — all
pairs comfortably exceed this.

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

## Footprint provenance

The SW1 footprint is a manually-flattened (axis-aligned) variant of the
`SKRHA-boss` footprint from the
[crides/kleeb keyboard library](https://github.com/crides/kleeb/blob/master/switch.pretty/SKRHA-boss.kicad_mod).
That library's footprints are described as "created by me, following
datasheet from Alps" and have been used in production keyboard builds.

Original kleeb pad coordinates were rotated -45° so pads land on the
left/right faces of the body in our PCB coordinate system; pad sizes
(1.35 × 1.0 mm signal, 2.0 × 1.8 mm anchor) and NPTH alignment hole
diameters (1.05 mm + 0.75 mm) are kept identical to the source.
