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

## Rev 2 "Extended with Joystick" — Base v1.4

A purpose-built base for the extended layout: battery on the left half, ESP32 stack on the right overhanging the battery top by 5mm, dual USB-C ports popping out the +X end wall, four M3 corner pillars, and two Ø1mm **vertical poke-through holes in the base floor** so a paperclip can reach BOOT/RESET on the upside-down-mounted ESP32 board. **Outer footprint 89.5 × 44 × 12mm** — v1.2 trimmed the battery end by 6.5mm, v1.3 raised the USB-C cutouts 2mm above the ESP32 shelf, v1.4 added the button access holes. 2mm bottom fillet, 4mm top-view corner radius.

Source: [`hardware-design/scad Parts/Rev 2 extended with joystick/base-v1.scad`](https://github.com/rompasaurus/dilder/blob/main/hardware-design/scad%20Parts/Rev%202%20extended%20with%20joystick/base-v1.scad).

### Hand-drawn design sketches

Initial concept sketches drawn on a tablet showing the Rev 2 extended layout dimensions and component placement.

**Dimensions sketch** — Side profile (22mm tall, 35mm deep) and top view (82mm x 44mm outer) with internal section measurements (56.7mm battery chamber, 26.8mm ESP32 section, 19mm display area), 4mm corner radii, and screw post locations.

![Rev 2 dimensions sketch](../../assets/images/enclosure/rev2-sketch-dimensions.jpg)

**Component layout sketch** — Same views annotated with component placement: battery in the left chamber, ESP32 in the right chamber with a 2mm divider between them. Shows how the board sits alongside the battery in the split-chamber layout.

![Rev 2 component layout sketch](../../assets/images/enclosure/rev2-sketch-component-layout.jpg)

### Isometric render

Four-corner M3 pillars with rounded inner edges, internal Y-axis divider between the battery and ESP32 chambers, and the step-down ESP32 shelf (narrower in Y than the battery to match the real PCB footprint). The longer/flatter profile and the deeper step under the overhang are visible here. Pillars' outer bottom corners inherit the shell's 2mm fillet — no plane-popping off the front face.

![Rev 2 joystick base — isometric](../../assets/images/enclosure/rev2-base-v1-iso.png)

### Top view

Layout at a glance: battery chamber (60.3 × 35.8mm interior) on the left, ESP32 chamber (narrower Y, 28.8mm, 23mm X) on the right, 2mm divider rib between them, 4mm outer corner radius, four M3 through-holes visible in the corners.

![Rev 2 joystick base — top](../../assets/images/enclosure/rev2-base-v1-top.png)

### +X end view — dual USB-C cutouts

The +X face with both USB-C cutouts (7.8 × 2.8mm each), centered on Y=16mm and Y=28mm. Wall is intentionally thin at 1.2mm on this end so the ports poke through cleanly. Cutout z-center now 8mm (raised +2mm in v1.3 so the cutouts clear the ESP32 shelf at z=7).

![Rev 2 joystick base — +X end](../../assets/images/enclosure/rev2-base-v1-end-plusx.png)

### Side view

Outer long-side profile — the long-axis walls are solid (all cutouts live on the ±X end walls or the bottom). The shorter, elongated profile is from the v1.1/v1.2 resize.

![Rev 2 joystick base — side](../../assets/images/enclosure/rev2-base-v1-side.png)

### Bottom view — BOOT/RESET paperclip poke-through holes

View of the underside. Four large circles are the corner pillar screw holes. The two small dots in the +X half are the Ø1mm vertical poke-through holes added in v1.4 — placed so a paperclip inserted from below the enclosure travels straight up through 2mm of base plate plus 5mm of shelf material and reaches the BOOT and RESET buttons on the ESP32 board (which is mounted **component-side down**, so the buttons face the floor).

Positions (bottom-face coordinates): hole 1 at (x=71.3, y=32.5), hole 2 at (x=58.8, y=32.5), both Ø1mm.

![Rev 2 joystick base — bottom with button holes](../../assets/images/enclosure/rev2-base-v1-bottom.png)

### USB-C closeup (looking from inside)

The two cutouts punched through the thin 1.2mm +X wall at z-center 8mm — fully above the ESP32 shelf (z=7) after the v1.3 bump, so the port recess lives entirely in clear chamber space rather than carving through the shelf.

![Rev 2 joystick base — USB-C closeup](../../assets/images/enclosure/rev2-base-v1-usb-closeup.png)

### Shelf step closeup

Inside view showing the 5mm step from the battery floor (lower) up to the ESP32 overhang shelf (higher), the internal divider rib between chambers, and a corner pillar with its M3 through-hole. The 0.2mm shelf divets under each USB port sit at the +X end, out of frame in this angle.

![Rev 2 joystick base — shelf step closeup](../../assets/images/enclosure/rev2-base-v1-divet.png)

---

## Rev 2 "Extended with Joystick" — Top Cover (Windowed) v1

The top piece for the Rev 2 stack. Outer footprint `91.5 × 44mm` matches `base-v1` and `middle-platform-v1` so the M3 through-bolts line up through the entire sandwich. Combines two Rev 1 ideas — the curved bullnose top from `top-cover-v3-rounded-top` and the display slide-in housing with ±Y snap rails from `top-plate-windowed-v1` — plus a new tapered joystick through-hole on the +X half of the face plate.

Source: [`hardware-design/scad Parts/Rev 2 extended with joystick/top-cover-windowed-v1.scad`](https://github.com/rompasaurus/dilder/blob/main/hardware-design/scad%20Parts/Rev%202%20extended%20with%20joystick/top-cover-windowed-v1.scad).

### Isometric — cavity view

![Rev 2 top cover — isometric](../../assets/images/enclosure/rev2-top-cover-windowed-v1-iso.png)

The bullnose radius is 4mm — big enough that the curve reads across the whole front face as a rolled edge rather than a small corner fillet. The face plate itself is only **0.5mm** thick (minimum printable for FDM); most of the visible "top-face taper" happens inside the bullnose above the face plate, via the tapered window and joystick cuts.

### Top view — tapered window + joystick hole

![Rev 2 top cover — top view](../../assets/images/enclosure/rev2-top-cover-windowed-v1-top.png)

Both openings are cut as a `hull()` frustum — true size at the face-plate bottom and `(opening + 2·taper)` at the top of the cover — so the bullnose rolls into each opening as a shallow funnel instead of meeting it at a hard square edge. Window taper: 2mm per side. Joystick hole taper: 1.5mm on radius (12mm Ø at the face plate, 15mm Ø at the top).

### Side profile — bullnose

![Rev 2 top cover — side](../../assets/images/enclosure/rev2-top-cover-windowed-v1-side.png)

Side view showing the 4mm bullnose rolling the outer wall into the top face across the full long axis.

### Underside — rails, wire gap, -X pillar shortening

![Rev 2 top cover — underside](../../assets/images/enclosure/rev2-top-cover-windowed-v1-under.png)

Two ±Y snap rails run along the display's long edges. Each rail is **2.5mm** wide in Y (matching Rev 1's `top-plate-windowed-v1`), with a 1mm-thick lip at the bottom that protrudes 1mm inward past the display's ±Y edge to catch the display from below. The open space between rail inner edge and display edge doubles as a wire-routing channel.

A **30 × 6mm wire pass-through gap** notches the middle of the -Y rail so wires can cross the rail boundary without fighting the snap — same pattern as Rev 1, rotated for the landscape display orientation.

The **-X corner pillars** show only the screw-clearance hole at this level — the full square pillar only exists at the base (z=0 → 5.5), where it mates with `middle-platform-v1`. Above the rail-bottom level, the -X pillars are omitted so the square-pillar edges don't clutter the cavity between the rail top and the face plate. The M3 bolt still has a continuous material path — pillar → rail → face plate → bullnose — but the visible pillar footprint only appears where it's structurally needed at the base. The +X pillars stay full-height (no rails reach them).

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
| 2026-04-23 | Rev 2 joystick base | v1.1 | Resize pass: outer width 82→96mm (+14), total height 22→12mm (-10), battery cell length 52→66mm (+14), overhang shelf 2→5mm (battery pit 3mm deeper), USB-C z-center 7→6mm (1mm lower) |
| 2026-04-23 | Rev 2 joystick base | v1.2 | Battery section trimmed -6.5mm: outer width 96→89.5mm, battery cell length 66→59.5mm, ESP32 chamber unchanged |
| 2026-04-23 | Rev 2 joystick base | v1.3 | USB-C cutouts raised +2mm (z-center 6→8mm) so they clear the ESP32 shelf (z=7) and sit fully above it |
| 2026-04-23 | Rev 2 joystick base | v1.4 | Added two Ø1mm vertical BOOT/RESET paperclip poke-through holes in the base floor at (71.3, 32.5) and (58.8, 32.5); board is mounted component-side down so paperclip reaches buttons from below |
| 2026-04-23 | Rev 2 top cover (windowed) | v1 | Top piece for the Rev 2 stack: 4mm bullnose across the whole front face, 0.5mm face plate, tapered display window (50×25 → +2mm per side at the cover top) and tapered joystick hole (Ø12 → Ø15), 2.5mm ±Y snap rails with 1mm lips, 30×6mm wire pass-through gap in the -Y rail, -X pillars shortened to `rail_bottom_z` so the square pillar only exists where it meets the base |
