# Dilder Rev 2 "extended with joystick" — All Models Dimensions

Canonical reference for every SCAD part in this folder. Each numeric value is traceable to a named parameter (or derivation) in its source file.

**Coordinate convention** — each part has its own local frame with origin at the -X/-Y outer corner and Z=0 at the part's mating bottom. The stack global Z increases upward:

```
Global Z  Layer
0         base-v1 mating bottom (outside bottom of enclosure)
0–14      base-v1
14        base-v1 top = middle-platform-v1 bottom
14–22     middle-platform-v1 (short portion)
14–27     middle-platform-v1 -X pedestal (pokes 5 mm above shell top)
22        middle-platform-v1 shell top = top cover mating bottom
22–36.5   top-cover-windowed-v1 (OR top-cover-windowed-screen-inlay-v1)
22–32     display occupies this range (Waveshare 2.13" landscape on the pedestal)
```

All units in mm. All parts share: 91.5 × 44 outer footprint, -X wall 3.0, +X wall 1.2, corner-pillar side 5, M3 clearance 3.2, `print_fit_tolerance_slop_mm = 0.4`.

**Common corner-pillar XY origins** (-X/-Y corner of each 5×5 pillar — identical in all four parts so the M3 stack bolts line up):

| Pillar | Origin (X, Y) | Screw center (X, Y) |
|---|---|---|
| -X -Y | (3.0, 2.0) | (5.5, 4.5) |
| +X -Y | (85.3, 2.0) | (87.8, 4.5) |
| -X +Y | (3.0, 37.0) | (5.5, 39.5) |
| +X +Y | (85.3, 37.0) | (87.8, 39.5) |

Screw-center pitch: **82.3 mm in X × 35.0 mm in Y**.

---

## 1. `base-v1.scad` — bottom shell

Bottom of the enclosure. Houses the battery flat on the -X half and the ESP32 board on an overhang shelf on the +X half. Two USB-C ports pop through the +X end wall. Curved-bottom fillet on the outer shell.

### 1.1 Outer shell

| Parameter | Value |
|---|---|
| Outer length (X) | 91.5 |
| Outer depth (Y) | 44.0 |
| Outer height (Z) | 14.0 |
| Outer top-view corner radius | 4.0 |
| Outer bottom-edge fillet radius | 2.0 |
| Base floor plate thickness | 3.0 |
| ±Y long-wall thickness | 2.0 |
| -X end-wall thickness (battery) | 3.0 |
| +X end-wall thickness (USB-C) | 1.2 |

### 1.2 Battery chamber (-X half)

| Parameter | Value |
|---|---|
| Cell footprint X | 61.5 |
| Cell footprint Y | 35.0 |
| Chamber inner X | 62.3 (cell + 2×0.4 slop) |
| Chamber inner Y | 35.8 |
| Chamber Y start | 4.1 (centered) |
| Chamber Y end | 39.9 |
| Chamber X start | 3.0 |
| Chamber X end | 65.3 |
| Chamber floor Z | 3.0 (top of floor plate) |

### 1.3 ESP32 chamber (+X half, on overhang shelf)

| Parameter | Value |
|---|---|
| Board footprint Y | 28.0 |
| Chamber inner Y | 28.8 |
| Chamber Y start | 7.6 (centered) |
| Chamber Y end | 36.4 |
| Overhang onto battery (X) | 4.0 |
| Shelf Z height above battery floor | 5.0 |
| Shelf top Z | 8.0 |
| Internal divider wall thickness | 2.0 |
| Divider X start | 65.3 |
| Divider X end | 67.3 |
| Chamber X start (= divider end − overhang) | 63.3 |
| Chamber X end | 90.3 |
| Chamber inner X length | 27.0 |

### 1.4 USB-C port cutouts (+X end wall)

Stadium-shaped (pill) cutouts — two ports, symmetric about Y=22.

| Parameter | Value |
|---|---|
| Cutout Y width (port length 7.8 + 1 slop) | 8.8 |
| Port body Z height (above PCB) | 2.6 |
| Extra Z seat allowance | 0.2 |
| Top-only Z extra | 0.5 |
| Cutout total Z height | 3.3 |
| Port Y centers | 16.0 (lower), 28.0 (upper) |
| Port body recess depth into enclosure | 8.0 |
| Port vertical center Z | 9.0 |
| Cutout effective center Z | 8.25 |
| Cutout top Z | 9.9 |
| Cutout bottom Z | 6.6 |

### 1.5 USB-C shield-tab shelf divets

Two pockets carved INTO the top of the ESP32 shelf, one under each USB-C port, so the port shield tab (~0.2 mm below PCB) has somewhere to sit.

| Parameter | Value |
|---|---|
| Divet depth into shelf (Z) | **0.7** |
| Divet X length | 8.0 |
| Divet Y width | 7.8 |
| Divet X range | 82.3 → 90.3 |
| Divet Y centers | 16.0 and 28.0 |
| Divet Z top | 8.0 (shelf top) |
| Divet Z bottom | 7.3 |

### 1.6 Battery stop pillars

Two solid blocks added AFTER the chamber carve, against the divider's -X face and flush to each ±Y inner wall. Prevent the cell from sliding into the ESP32 PCB's under-board connector.

| Parameter | Value |
|---|---|
| Width along X (-X from divider) | 9.0 |
| Width along Y (per pillar, along wall) | 6.0 |
| Height along Z (from pit floor) | 5.0 |
| X range | 56.3 → 65.3 |
| -Y pillar Y range | 4.1 → 10.1 |
| +Y pillar Y range | 33.9 → 39.9 |
| Z bottom | 1.0 (= pit floor) |
| Z top | 6.0 |

### 1.7 Battery-floor pit

Rectangular pit dug DOWN into the battery floor plate, flush with the battery +X edge (against the divider wall), Y-centered.

| Parameter | Value |
|---|---|
| Pit X width | 10.0 |
| Pit Y width | 35.5 |
| Pit depth below battery floor (Z) | 2.0 |
| X range | 55.3 → 65.3 |
| Y range | 4.25 → 39.75 (Y-centered) |
| Z range | 1.0 → 3.0 |
| Material remaining below pit | 1.0 (3 floor − 2 pit) |

### 1.8 BOOT/RST paperclip holes (base floor)

Two small vertical holes through the base floor + shelf material for accessing the ESP32 buttons (board is component-side DOWN on the shelf).

| Parameter | Value |
|---|---|
| Hole diameter | 2.0 |
| Hole 1 X (from +X inner wall, inward) | 17.0 → center X = 73.3 |
| Hole 2 offset -X from hole 1 | 12.5 → center X = 60.8 |
| Y inset from +Y outer edge | 11.5 → center Y = 32.5 |
| Z range | −0.5 → 14.5 (through-bore) |

### 1.9 base-v1 stack bolts (4 × M3)

Clearance holes through all 4 corner pillars, full height (Z = −0.1 → 14.1).

---

## 2. `middle-platform-v1.scad` — mid-stack platform

8 mm-tall shell with thick ±Y long walls (8 mm), same ±X end walls as base-v1. The -X interior has a solid fill pedestal that pokes 5 mm above the shell top — the display rests on this pedestal's top.

### 2.1 Outer shell

| Parameter | Value |
|---|---|
| Outer length (X) | 91.5 |
| Outer depth (Y) | 44.0 |
| Short-portion height (Z) | 8.0 |
| Outer top-view corner radius | 4.0 |
| ±Y long-wall thickness | 8.0 |
| -X end-wall thickness | 3.0 |
| +X end-wall thickness | 1.2 |

### 2.2 -X pedestal (solid fill block)

| Parameter | Value |
|---|---|
| Interior fill depth along X (from -X inner wall) | 22.0 |
| Fill X range | 3.0 → 25.0 |
| Fill Y range (flush to ±Y inner walls) | 8.0 → 36.0 |
| Fill height above 8 mm shell top | 5.0 |
| Fill top Z | **13.0** |
| Fill total Z height | 0 → 13.0 |

### 2.3 Hollow right-side interior

| Parameter | Value |
|---|---|
| Right interior X start | 25.0 (= end of fill) |
| Right interior X end | 90.3 |
| Right interior Y start | 8.0 |
| Right interior Y end | 36.0 |
| Right interior Y span | 28.0 |
| Right interior Z range | 0 → 8.0 (through the 8 mm shell) |

### 2.4 Corner pillars

Same 4 XY origins as listed in the common section (use `perimeter_outer_wall_thickness_mm_base = 2`, NOT this file's 8 mm, so the screw centers don't shift vs. base-v1). Height = 8 mm (= shell top). Pillars sit in the ±Y 8 mm wall material band — the -X pedestal is offset inward and doesn't touch them.

### 2.5 middle-platform-v1 stack bolts (4 × M3)

Clearance holes through all 4 corner pillars, full height (Z = −0.1 → 8.1).

---

## 3. `top-cover-windowed-v1.scad` — top cover (no rails, blind holes)

Curved bullnose top with a tapered display viewing window and a joystick through-hole. No rails or lips — relies on a separate retention plate (not in this folder). Corner-pillar bores are BLIND from below so no holes show on the front face.

### 3.1 Outer shell

| Parameter | Value |
|---|---|
| Outer length (X) | 91.5 |
| Outer depth (Y) | 44.0 |
| Outer top-view corner radius | 4.0 |
| Outer top-edge bullnose radius | 4.0 |
| Face plate thickness (Z) | 0.5 |
| ±Y base-shell wall thickness | 2.0 |
| -X end-wall thickness | 3.0 |
| +X end-wall thickness | 1.2 |

### 3.2 Z stack (cover-local)

| Layer | Z range | Height |
|---|---|---|
| Pedestal protrusion into cover | 0.0 → 5.0 | 5.0 |
| Display envelope | 5.0 → 10.0 | 5.0 |
| Face plate | 10.0 → 10.5 | 0.5 |
| Bullnose | 10.5 → 14.5 | 4.0 |
| **Cover total height** | | **14.5** |

### 3.3 Display footprint

| Parameter | Value |
|---|---|
| Display length along X | 65.0 |
| Display depth along Y | 30.0 |
| Display thickness envelope (Z) | 5.0 |
| -X origin | 3.4 (wall 3.0 + slop 0.4) |
| +X end | 68.4 |
| -Y origin | 7.0 |
| +Y end | 37.0 |
| Y centerline | 22.0 |

### 3.4 Display viewing window (tapered cut)

Updated **2026-04-24** to match the Waveshare 2.13" module's actual viewable pixel area — the first print showed the window was 2 mm too long in X on the -X end and 2 mm too short in Y overall.

| Parameter | Value (post-2026-04-24) | First print |
|---|---|---|
| Window X length (at face-plate bottom) | **48.0** | 50.0 |
| Window Y depth (at face-plate bottom) | **27.0** | 25.0 |
| Window +X shift toward joystick | **3.0** | 2.0 |
| Top taper per edge | 2.0 | 2.0 |
| X range at face-plate bottom | **14.90 → 62.90** | 12.90 → 62.90 |
| Y range at face-plate bottom | **8.50 → 35.50** | 9.50 → 34.50 |
| X range at cover top | **12.90 → 64.90** | 10.90 → 64.90 |
| Y range at cover top | **6.50 → 37.50** | 7.50 → 36.50 |
| Z range | 10.0 → 14.5 (through) | same |

Length 50 → 48 with the shift bumped +1 keeps the +X short side of the window at exactly X=62.90 (unchanged); only the -X short side moves inward by 2 mm. The ±Y long sides each extend 1 mm further outward symmetrically.

Bezel dimensions after the update:
- -X bezel (window edge to display -X edge): **11.5** (was 9.5)
- +X bezel: 5.5 (unchanged)
- ±Y bezels: **1.5 each** (was 2.5)

### 3.5 Joystick through-hole (tapered cut)

| Parameter | Value |
|---|---|
| Hole diameter (at face-plate bottom) | 12.0 |
| Top taper width (per radius) | 1.5 |
| Hole diameter (at cover top) | 15.0 |
| Hole center X | (68.4 + 90.3) / 2 = **79.35** |
| Hole center Y | 22.0 |
| Hole Z range | 10.0 → 14.5 (through) |

### 3.6 Cavity + pillars

Cavity below face plate — Z range −0.1 → 10.1. Carves all material in the inner footprint (X=3.0–90.3, Y=2.0–42.0) except the 4 corner pillars.

Corner pillars run full height (0 → 10.5, to face plate top). Same XY origins as common table.

### 3.7 top-cover-windowed-v1 BLIND M3 bores (4 × M3)

| Parameter | Value |
|---|---|
| Bore diameter | 3.2 |
| Bore Z range | −0.1 → 10.1 |
| Material above bore (cap) | 4.4 (face plate + bullnose) |

---

## 4. `top-cover-windowed-screen-inlay-v1.scad`

Variant of v1 that adds a 3 mm-deep recess for the Waveshare 2.13" display to rest INTO the face-plate underside, plus a 20 × 20 mm pocket + 4 mounting bores for a joystick-header PCB beneath the joystick hole. Everything else is identical to v1 (same shell, same bullnose, same window + joystick cut, same blind stack bolts).

### 4.1 Overrides vs. v1

The inlay variant has an **increased display envelope thickness (7 mm vs. v1's 5 mm)**, which shifts the entire Z stack up by 2 mm. It also has a **thicker face plate (0.7 mm vs. v1's 0.5 mm)**, bumped 2026-04-24 because the first print showed a hairline seam along the top edge of the inlay recess where 0.5 mm printed as one perimeter + one thin top layer and didn't fully close. 0.7 mm gives the slicer enough material for a proper multi-layer top skin.

All sections 3.1–3.7 apply identically in XY, but Z values shift:

| Z-stack value | v1 | inlay v1 (post-2026-04-24) |
|---|---|---|
| face_plate_thickness_z_mm | 0.5 | **0.7** |
| display_top_z_mm | 10.0 | **12.0** |
| face_plate_bottom_z_mm | 10.0 | **12.0** |
| face_plate_top_z_mm | 10.5 | **12.7** |
| cover_total_height_z_mm | 14.5 | **16.7** |

Display Z: 5.0 → 12.0 (7 mm envelope).

The window dimensions updated in §3.4 (48 × 27, shift 3) apply to the inlay variants too — all three cover variants share the same window geometry.

### 4.2 Screen inlay recess

Rectangular pocket carved UP from the face-plate underside.

| Parameter | Value |
|---|---|
| Depth into face plate (Z) | 3.0 |
| XY slop per edge | 0.3 |
| X range | 3.10 → 68.70 (width 65.6) |
| Y range | 6.70 → 37.30 (depth 30.6) |
| Z range | 12.0 → 15.0 |
| Remaining bullnose above ceiling | 1.5 |

### 4.2a FPC ribbon divet (cut into the -X battery-end wall)

Rectangular pocket that **thins the -X (battery-end) wall** from its
normal 3 mm down to 1 mm over a 13 mm Y band, on the opposite side of
the display from the joystick hole. Gives the raw display's FPC cable
room to exit the bay so the board seats flush in the inlay.

| Parameter | Value |
|---|---|
| Divet Y width | **13.0** |
| Remaining -X wall thickness at divet | **1.0** (from 3.0) |
| Divet X range | 1.00 → 3.10 (cuts wall + inlay overlap) |
| Divet Z range | 12.0 → 15.0 (= inlay Z range) |
| Y range | 15.50 → 28.50 (centered on display Y centerline) |

### 4.3 Joystick PCB pocket

Square pocket, carved UP from the face-plate underside. The pocket's -X edge is pulled flush with the inlay's +X edge (not centered on the joystick hole), to eliminate the thin sliver of material that would otherwise sit between the two cuts.

| Parameter | Value |
|---|---|
| Pocket X width | 20.0 |
| Pocket Y depth | 20.0 |
| Pocket Z depth | 1.0 |
| X range | **68.70 → 88.70** (shifted -X 0.65 mm from joystick-centered position) |
| Y range | 12.00 → 32.00 |
| Z range | 12.0 → 13.0 |
| Pocket center (X, Y) | (78.70, 22.00) |
| Joystick hole center (X, Y) | (79.35, 22.00) |
| Pocket-to-joystick offset (X) | 0.65 (PCB's joystick component sits this far +X of its geometric center) |

### 4.4 Joystick PCB mount bores — REMOVED 2026-04-24

On the first print these showed as a circle of dimples around the joystick cutout on the underside, and the joystick-PCB retention strategy hasn't been decided yet (glue / press-fit / heat-set inserts are all still on the table). The 4 blind bores that used to sit at the pocket corners have been removed from both inlay variants.

The parameter definitions (`joystick_pcb_mount_bore_*`, `joystick_pcb_mount_bore_xy_positions_list`) are intentionally kept in the SCAD so the geometry is one block away from coming back. Reference values if it returns:

| Corner | Bore center (X, Y) |
|---|---|
| -X -Y | (71.20, 14.50) |
| +X -Y | (86.20, 14.50) |
| -X +Y | (71.20, 29.50) |
| +X +Y | (86.20, 29.50) |

- Bore diameter: 3.2 mm (M3 clearance)
- Bore-pattern pitch (X × Y): 15.0 × 15.0 mm
- Matching PCB footprint: 20 × 20 mm with 4 × 3.2 mm holes at 15 × 15 mm center pitch.

---

## 5. Inter-part alignment check

### 5.1 Outer sides flush

All four parts share outer footprint 91.5 × 44, ±X walls 3.0 / 1.2. Side surfaces align exactly (base's bottom fillet and top cover's bullnose are the only outer-profile variations, both at the Z extremes).

### 5.2 Stack bolts line up

All four parts use identical `corner_pillar_xy_origin_positions_list` → screw centers at (5.5, 4.5), (87.8, 4.5), (5.5, 39.5), (87.8, 39.5).

Bolt path through the stack (global Z):

| Z range | Part | Bore diameter |
|---|---|---|
| 0 → 14 | base-v1 | 3.2 (through) |
| 14 → 22 | middle-platform-v1 | 3.2 (through) |
| 22 → 32.0 | top cover pillar material (bore open) | 3.2 |
| 32.0 → 36.5 | top cover pillar material (bore capped) | — |

Bolt-retention note: with the cover's bore blind at Z=10 (local) / Z=32 (global), need heat-set inserts or captive nuts somewhere in the cover's pillar column for the bolts to actually anchor. Otherwise the bolt threads have nothing to engage.

### 5.3 Display position consistency

Middle-platform pedestal top at global Z=27 supports the display's -X half from below. The top cover computes display Z as `middle_platform_pedestal_protrusion_into_cover_z_mm = 5` above the cover's mating bottom — which places the display at global Z=27 → 32 (5 mm thick envelope). ✓ consistent.

### 5.4 USB-C cutout consistency

USB-C port Y centers (16.0, 28.0) defined in base-v1 only. No matching cutout in middle-platform or top cover — ports exit through base's +X wall below the middle-platform shell, which covers the chamber from above at global Z ≥ 14.

---

## 6. Caveats

- `waveshare-2.13-dimensions.md` values are approximate Waveshare spec — verify against the actual module with calipers before the inlay recess is final.
- Stale comments in `top-cover-windowed-v1.scad` still say `face_plate_top = 12` and `cover_total_height = 14`; the actual computed values with `face_plate_thickness = 0.5` and bullnose radius `4` are 10.5 and 14.5 respectively (values in this doc are the computed ones).
- All "slop" values (`print_fit_tolerance_slop_mm = 0.4`, `screen_inlay_xy_slop_per_edge_mm = 0.3`) are tuned for typical FDM XY shrink — adjust per filament/printer.
- Heat-set inserts for M3 typically want a 4.0–4.5 mm bore; the current 3.2 mm blind bores are clearance-sized. Either re-spec the bore diameter or plan for self-tapping screws (tighter, ~2.7 mm) depending on your hardware.
- **Face plate thickness diverges across variants after 2026-04-24**: `top-cover-windowed-v1.scad` still uses 0.5 mm (it's not currently being printed); both inlay variants were bumped to 0.7 mm based on first-print seam feedback. If base v1 is ever printed as-is, expect the same seam issue until its face plate is also bumped.
