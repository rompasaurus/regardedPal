# Enclosure Design Evolution

A living record of the Dilder enclosure's parametric CAD design as it evolves through prototyping and print iterations. All parts are designed in OpenSCAD and exported to 3MF for slicing.

---

## Current Assembly (ESP32-S3 Enclosure)

The enclosure is a stacked shell design housing an Olimex ESP32-S3-DevKit-Lipo, Waveshare 2.13" e-ink display, and 1000mAh LiPo battery. Five parts print flat without supports and assemble with 4 corner screw posts.

![Full enclosure assembly](../../assets/images/enclosure/full-enclosure-assembly.png)

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
