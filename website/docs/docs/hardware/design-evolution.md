# Enclosure Design Evolution

A living record of the Dilder enclosure's parametric CAD design as it evolves through prototyping and print iterations. All parts are designed in OpenSCAD and exported to 3MF for slicing.

---

## Physical Prototype (First Print)

The first FDM prints of the ESP32-S3 enclosure, photographed during fit-check and assembly testing on 2026-04-22.

### Assembled enclosure — front view

The stacked shell with e-ink display visible through the viewing window. Four corner screw posts hold everything together. USB-C cable connected for power and programming.

![Assembled enclosure front view](../../assets/images/enclosure/enclosure-assembled-front.jpg)

### Enclosure halves — base shell with LiPo battery

Side-by-side of the display top cover and base shell. The 1000mAh LiPo battery sits in the base chamber with the JST connector routed up through the middle plate.

![Enclosure halves with battery installed](../../assets/images/enclosure/enclosure-halves-with-battery.jpg)

### Components layout

All printed parts and electronics laid out: middle plate (board tray) with header slots, assembled case, and joystick breakout board with labeled directional pins.

![Components layout overview](../../assets/images/enclosure/components-layout-overview.jpg)

### ESP32-S3 board on printed parts

The Olimex ESP32-S3-DevKit-Lipo (red PCB) sitting on the middle plate and separator sheets. WROOM module, dual USB-C ports, and header pins visible.

![ESP32 board on printed parts](../../assets/images/enclosure/esp32-board-on-printed-parts.jpg)

### Middle plate header slots — closeup

The two long rectangular clearance slots (56.5mm x 4mm) that allow the board's header pins to pass through the plate.

![Middle plate header slots closeup](../../assets/images/enclosure/middle-plate-header-slots-closeup.jpg)

### Board fit-check closeup

The Olimex ESP32-S3-DevKit-Lipo sitting on a printed separator sheet. The WROOM-1 module and antenna are on the left, dual USB-C ports (OTG + programming) on the right, JST battery connector in the center. This photo drove the design of the board cradle separator.

![ESP32 board fit-check closeup](../../assets/images/enclosure/esp32-board-fitcheck-closeup.jpg)

### Dev workstation

The full development setup with dual monitors, ESP32 prototype wired up with jumper cables, and joystick input board.

![Dev workstation overview](../../assets/images/enclosure/dev-workstation-overview.jpg)

---

## Rev 2 "Extended with Joystick" — Base v1

A purpose-built base for the extended layout: battery on the left half, ESP32 stack on the right overhanging the battery top by 2mm, dual USB-C ports popping out the +X end wall, four M3 corner pillars. Outer footprint 82 × 44 × 22mm with a 2mm bottom fillet and 4mm top-view corner radius.

Source: [`hardware-design/scad Parts/Rev 2 extended with joystick/base-v1.scad`](https://github.com/rompasaurus/dilder/blob/main/hardware-design/scad%20Parts/Rev%202%20extended%20with%20joystick/base-v1.scad).

### Isometric render

Four-corner M3 pillars with rounded inner edges, internal Y-axis divider between the battery and ESP32 chambers, and the step-down ESP32 shelf (narrower in Y than the battery to match the real PCB footprint). Notice how the pillars' outer bottom corners now inherit the shell's 2mm fillet — no more plane-popping off the front face.

![Rev 2 joystick base — isometric](../../assets/images/enclosure/rev2-base-v1-iso.png)

### Top view

Layout at a glance: battery chamber (52.8 × 35.8mm interior) on the left, ESP32 chamber (narrower Y, 28.8mm) on the right, 2mm divider rib between them, 4mm outer corner radius, four M3 through-holes visible in the corners.

![Rev 2 joystick base — top](../../assets/images/enclosure/rev2-base-v1-top.png)

### +X end view — dual USB-C cutouts

The +X face with both USB-C cutouts (7.8 × 2.8mm each), centered on Y=16mm and Y=28mm. Wall is intentionally thin at 1.2mm on this end so the ports poke through cleanly.

![Rev 2 joystick base — +X end](../../assets/images/enclosure/rev2-base-v1-end-plusx.png)

### Side view

Outer side profile (the long-axis wall is solid — all cutouts are on the ±X end walls or floor). Bottom fillet visible as the softly rounded underside.

![Rev 2 joystick base — side](../../assets/images/enclosure/rev2-base-v1-side.png)

### USB-C closeup (+X wall)

The two cutouts framed by the thin 1.2mm +X wall, sitting at Z-center ≈ 7mm so each cutout lines up with a USB-C port body above the ESP32 shelf.

![Rev 2 joystick base — USB-C closeup](../../assets/images/enclosure/rev2-base-v1-usb-closeup.png)

### Shelf divet closeup

Inside view of the ESP32 shelf with the two 0.2mm-deep divets carved into its top face. Each divet gives the USB-C receptacle's underside shield tab a place to sit so the PCB lies flat; the divets stop at the inner face of the +X wall rather than breaking through to the outside.

![Rev 2 joystick base — shelf divet closeup](../../assets/images/enclosure/rev2-base-v1-divet.png)

---

## Current Assembly (ESP32-S3 Enclosure)

The enclosure is a stacked shell design housing an Olimex ESP32-S3-DevKit-Lipo, Waveshare 2.13" e-ink display, and 1000mAh LiPo battery. Five parts print flat without supports and assemble with 4 corner screw posts.

![Full enclosure assembly — CAD render](../../assets/images/enclosure/full-enclosure-assembly.png)

| Dimension | Value |
|-----------|-------|
| Outer footprint | 39.8 x 79.8mm |
| Total height | 29.8mm |
| Wall thickness | 2mm |
| Corner radius | 4mm |

---

## Parts Breakdown

### Middle Plate (Board Tray) — v2

The board tray drops into the base shell at z=8mm, resting on the lower shelf. It holds the ESP32-S3 board with header pin clearance slots on both long edges.

![Middle plate v2](../../assets/images/enclosure/middle-plate-v2.png)

**Key dimensions:**

| Feature | Value |
|---------|-------|
| Plate size | 35 x 75 x 2mm |
| Header slot length | 56.5mm (board length + 0.5mm clearance) |
| Header slot width | 4mm |
| Slots centered on plate length | Yes |
| Pillar cutout overshoot | 1mm on far edges for clean booleans |

**Design changes (v1 to v2):**

- v1: Header slots derived from board dimensions, 46mm long, 3mm wide
- v2: Independent slot parameters (56.5mm x 4mm), centered on plate, clean pillar cutouts

**Source:** `hardware-design/scad Parts/middle-plate.scad`

---

### Top Plate Windowed (Display Cover) — v1

The display cover plate sits inside the top cover frame. Solid face plate with a 25x50mm viewing window and snap-fit retaining rails on the underside that grip the display edges.

![Top plate windowed v1](../../assets/images/enclosure/top-plate-windowed-v1.png)

**Key dimensions:**

| Feature | Value |
|---------|-------|
| Plate size | 35 x 75 x 2mm |
| Viewing window | 25 x 50mm (centered) |
| Rail depth | 4.5mm |
| Rail width | Extended to plate edges (~2.5mm per side) |
| Lip protrusion | 1mm inward under display |
| Lip thickness | 1mm (full printable layer) |

**Design features:**

- Face plate is solid all around (no wire gap in face surface)
- Wire pass-through gap preserved in rails only (below face)
- Lips are full-width shelves attached to rail bottoms (printable, no floating geometry)
- Screw clearance holes at all 4 corners

**Source:** `hardware-design/scad Parts/top-plate-windowed-v1.scad`

---

### Top Cover Frame — v2

An open border frame with rounded vertical edges and 4 corner pillar posts. The windowed plate drops into countersunk pockets at the pillar tops and sits flush.

![Top cover v2](../../assets/images/enclosure/top-cover-v2.png)

**Key dimensions:**

| Feature | Value |
|---------|-------|
| Outer footprint | 39.8 x 79.8mm |
| Height | 7mm |
| Wall thickness | 2mm |
| Corner radius | 4mm |
| Pillar size | 5 x 5mm |
| Countersink depth | 2mm (matches plate thickness) |

**Design changes (v1 to v2):**

- v1: Curved dome shell with wire notch, square pillars extending into dome causing artifacts
- v2: Flat-top open frame, solid border (no wire notch), countersunk pillars for flush plate seating

**Source:** `hardware-design/scad Parts/top-cover-v2.scad`

---

## SCAD Parts Library

All standalone parametric .scad files live in `hardware-design/scad Parts/`:

| File | Description |
|------|-------------|
| `middle-plate.scad` | Board tray (working copy) |
| `middle-plate-v1.scad` | Board tray v1 snapshot |
| `middle-plate-v2.scad` | Board tray v2 snapshot |
| `top-plate-windowed-v1.scad` | Display cover with viewing window |
| `top-plate-solid.scad` | Display cover without window |
| `top-cover.scad` | Original curved dome cover |
| `top-cover-v2.scad` | Open frame cover with countersunk pillars |
| `top-cover-v3.scad` | Rounded inner corners, single-corner-rounded pillars |
| `top-cover-v3-rounded-top.scad` | v3 with bullnose top edge |
| `top-cover-v3-{12,17,22}mm.scad` | v3 height variants (+5/10/15mm) |
| `top-cover-v3-rounded-top-{12,17,22}mm.scad` | Rounded-top height variants (+5/10/15mm) |
| `case-separator-inner.scad` | Thin divider, inner plate footprint |
| `case-separator-outer.scad` | Thin divider, outer base footprint |
| `case-separator-board-cradle.scad` | Outer separator with board-shaped cutout and raised cradle wall |
| `scad-export.py` | Interactive Python export tool (menu + file browser) |
| `scad-to-3mf-guide.md` | Export workflow guide |

---

## Export Workflow

### Quick export (command line)

```bash
openscad -o middle.3mf middle-plate.scad
```

### Batch export (all enclosure parts)

```bash
cd hardware-design
for part in base middle topmid cover screws; do
    openscad -D "part=\"$part\"" -o "enclosure-prints/$part.3mf" esp32s3-enclosure.scad
done
```

### Interactive export tool

```bash
python3 hardware-design/scad\ Parts/scad-export.py
```

Provides a menu to browse .scad files, pick export format (3MF/STL), set output path, and optionally override parameters.

---

## Print Settings

| Setting | Value |
|---------|-------|
| Layer height | 0.2mm (0.16mm for fine parts) |
| Infill | 20-30% |
| Walls/perimeters | 3 |
| Supports | None (all parts designed support-free) |
| Material | PLA or PETG |

---

## Version History

| Date | Part | Version | Changes |
|------|------|---------|---------|
| 2026-04-22 | Middle plate | v1 | Initial standalone extraction from main enclosure |
| 2026-04-22 | Middle plate | v2 | 56.5mm slots, centered, clean pillar cutouts |
| 2026-04-22 | Top plate windowed | v1 | Solid face, extended rails, printable lips, wire gap in rails only |
| 2026-04-22 | Top cover | v1 | Extracted dome cover from main enclosure |
| 2026-04-22 | Top cover | v2 | Open frame, solid border, countersunk pillar pockets |
| 2026-04-22 | Top cover | v3 | Rounded inner corners + single-corner-rounded pillars for flush plate insertion |
| 2026-04-22 | Top cover | v3-rounded-top | v3 with bullnose top edge (2mm radius) |
| 2026-04-22 | Case separator (inner) | v1 | Thin divider sheet matching inner plate footprint with header slots and screw holes |
| 2026-04-22 | Case separator (outer) | v1 | Thin divider sheet matching base outer footprint with header slots and screw holes |
| 2026-04-22 | Top cover v3 | height variants | 12mm, 17mm, 22mm versions (+5/10/15mm) for both flat-top and rounded-top |
| 2026-04-22 | Top plate windowed | v1 update | Outer edge expanded by 0.5mm per side for tighter fit |
| 2026-04-22 | Case separator (board cradle) | v1 | Outer footprint with board-shaped cutout and 2mm raised cradle wall |
| 2026-04-22 | Top plate windowed | v1 update | Rails trimmed 0.5mm from display side (flush with plate edges) |
| 2026-04-22 | Case separator (board cradle) | v1 update | Cutout widened 1mm per side for board clearance |
| 2026-04-22 | Rev 2 joystick base | v1 | Purpose-built base for the extended-with-joystick layout: split battery/ESP32 chambers, 2mm overhang shelf, dual USB-C cutouts, asymmetric end walls (1.2mm +X / 3mm -X), pillars clipped to bottom fillet |
