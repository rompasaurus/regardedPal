# Top Cover (Windowed) — Full Blueprints & Dimensions

Files in this folder:

| File | Purpose |
|---|---|
| `top-cover-windowed-v1.step` | Parametric STEP solid (industry-standard, full FreeCAD/Fusion/Inventor edit support) |
| `top-cover-windowed-v1.FCStd` | Native FreeCAD document (opens directly, same solid) |
| `top-cover-windowed-v1.csg` | OpenSCAD CSG dump (loadable via FreeCAD's OpenSCAD workbench) |
| `top-cover-windowed-screen-inlay-v1.step` / `.FCStd` / `.csg` | Same three formats for the screen-inlay variant |
| `top-cover-windowed-screen-inlay-v1-2mm.step` / `.FCStd` / `.csg` | 2 mm divet variant |
| `blueprints/*-top.png` / `*-bottom.png` / `*-front.png` / `*-side.png` / `*-iso.png` | Orthographic + iso renders |

All dimensions in millimetres. Origin is at the cover's -X -Y outer corner with Z=0 at the cover's mating bottom (the plane that lands on the middle-platform or base top rim). Units are export-honest: the STEP files use the same origin and scale.

---

## 1. Shared outer shell (both variants)

The outer shape is identical between `top-cover-windowed-v1` and `top-cover-windowed-screen-inlay-v1`. Only the inside differs.

### 1.1 Footprint

| Parameter | Value |
|---|---|
| Outer length along X | **91.5** |
| Outer depth along Y | **44** |
| Outer top-view corner radius | 4.0 |
| Outer top-edge bullnose radius (dome) | 4.0 |
| Cover total height along Z | **14.5** (windowed-v1) / 14.5 (screen-inlay v1, same) |

### 1.2 Walls (asymmetric ±X)

| Wall | Thickness | Inner face at |
|---|---|---|
| -X (battery end) | 3.0 | X = 3.0 |
| +X (USB-C end) | 1.2 | X = 90.3 |
| ±Y base-shell wall | 2.0 | Y = 2.0 and Y = 42.0 |

### 1.3 Z-stack layout

| Layer | Z range | Height |
|---|---|---|
| Cavity (hollow interior) | 0 → ~10 | 10 |
| Face plate (solid lid) | 10 → 10.5 | 0.5 (windowed-v1) or 12 → 12.5 inlay v1 after +2 mm display |
| Bullnose dome | 10.5 → 14.5 | 4 (curved) |

On the **screen-inlay variant**, the display-envelope was grown +2 mm, which shifts the face plate and all above layers +2 mm: `face_plate_bottom_z_mm = 12`, `cover_total_height_z_mm = 14.5` (no change to total — the bullnose radius also dropped to keep the overall height the same in most revisions, check the SCAD head-of-file for live values).

### 1.4 Corner pillars (stack bolts)

4 pillars at the enclosure corners. Fully load-bearing from cover floor to face-plate top, with a blind M3 clearance bore open from below.

| Pillar | Origin (-X -Y corner of pillar) | Screw center |
|---|---|---|
| -X -Y | (3.0, 2.0) | (5.5, 4.5) |
| +X -Y | (85.3, 2.0) | (87.8, 4.5) |
| -X +Y | (3.0, 37.0) | (5.5, 39.5) |
| +X +Y | (85.3, 37.0) | (87.8, 39.5) |

| Parameter | Value |
|---|---|
| Pillar cross-section | 5.0 × 5.0 square, 1.0 mm inner-corner fillet |
| Pillar Z range | 0 → `face_plate_top_z_mm` (varies by variant) |
| M3 clearance hole ⌀ | **3.2** |
| M3 bore Z range | −0.1 → `face_plate_bottom_z_mm` (BLIND — stops at face plate so no hole shows on front) |
| Screw-pattern pitch (X × Y) | **82.3 × 35.0** |

---

## 2. Features common to both cover variants

### 2.1 Display viewing window (tapered)

Tapered through-cut for the display's active area.

| Parameter | Value |
|---|---|
| Window length along X (at face-plate bottom) | 48 — updated in last revisions (was 50) |
| Window depth along Y (at face-plate bottom) | 24 — updated (was 25) |
| +X shift toward joystick | 2.8 |
| Top taper per edge | 2.0 |

Current (post-shift, post-resize) bezel margins from the display footprint edges:
- -X bezel: ~12.4 mm
- +X bezel: ~3.0 mm
- ±Y bezels: ~3.0 mm each

### 2.2 Joystick through-hole (tapered)

| Parameter | Value |
|---|---|
| Hole ⌀ at face-plate bottom | **12.0** |
| Top taper width per radius | 1.5 |
| Hole ⌀ at cover top | 15.0 |
| Hole center X | (display_plus_x + inner_plus_x) / 2 ≈ **79.35** |
| Hole center Y | 22.0 (display Y centerline) |

---

## 3. Screen-inlay-only features (`top-cover-windowed-screen-inlay-v1*.scad`)

### 3.1 Screen inlay recess

Cavity extended UP into the face plate/bullnose so a Waveshare 2.13" raw module slots in from below and lands flush against the bezel material.

| Parameter | Value |
|---|---|
| Recess depth into face plate (Z) | **3.0** |
| XY slop per edge | 0.3 (±X), 0.35 (±Y) |
| X range | 3.10 → 68.70 |
| Y range | 6.65 → 37.35 |
| Z range | `face_plate_bottom_z_mm` → `face_plate_bottom_z_mm + 3` |
| Remaining bullnose above recess ceiling | 1.5 |

### 3.2 FPC ribbon divet (cuts -X wall)

Thins the battery-end wall in a 13 mm Y band so the display FPC can exit.

| Parameter | Value (v1) | Value (v1-2mm) |
|---|---|---|
| Divet Y width | 13.0 | 13.0 |
| Remaining -X wall thickness | **1.0** | **1.0** |
| Divet X range | 1.00 → 3.10 | 1.00 → 3.10 |
| Divet Z extension below face-plate bottom | **3.0** | **2.0** |
| Divet Z range | `face_plate_bottom - 3` → `inlay_top` | `face_plate_bottom - 2` → `inlay_top` |
| Y range | 15.50 → 28.50 (display Y-centerline ±6.5) | same |

### 3.3 Joystick PCB pocket

Square pocket pulled flush with the inlay's +X edge (no thin uncut sliver between them).

| Parameter | Value |
|---|---|
| Pocket X range | 68.70 → 88.70 |
| Pocket Y range | 12.00 → 32.00 |
| Pocket Z depth | matches inlay (3 mm → pocket ceiling = inlay ceiling) |
| Pocket center (X, Y) | (78.70, 22.00) |
| Joystick-hole offset in X (from pocket center) | +0.65 (PCB's joystick component must sit this far +X of its geometric PCB center) |

### 3.4 Joystick-PCB mount bores (4 blind)

| Corner | Bore center (X, Y) |
|---|---|
| -X -Y | (71.20, 14.50) |
| +X -Y | (86.20, 14.50) |
| -X +Y | (71.20, 29.50) |
| +X +Y | (86.20, 29.50) |

| Parameter | Value |
|---|---|
| Bore ⌀ (M3 clearance) | 3.2 |
| Bore Z depth above pocket ceiling | 1.2 (blind; ~0.3 mm cap of bullnose above bore top) |
| Screw pattern pitch | 15.0 × 15.0 |
| Target PCB footprint | 20 × 20 mm, holes at 15 × 15 center-to-center |

---

## 4. Orthographic views

Renders in the `blueprints/` subfolder:

| View | File pattern |
|---|---|
| Top (looking -Z) | `{name}-top.png` |
| Bottom (looking +Z into cavity) | `{name}-bottom.png` |
| Front (looking +Y) | `{name}-front.png` |
| Side (looking +X) | `{name}-side.png` |
| Isometric | `{name}-iso.png` |

All orthographic renders use **parallel projection** (no perspective distortion). Pixels-to-mm ratio depends on view framing — use for proportion/feature inspection, not as a ruler. For exact measurements use the STEP file.

---

## 5. Caveats

- The parametric structure from SCAD is NOT preserved in the STEP or FCStd. The meshes are converted to a single-solid Part, so moving a corner pillar or resizing the window in FreeCAD is a fresh Boolean op on the solid, not a parameter tweak. See `FREECAD-GUIDE.md` for how to work with that.
- The 2 mm variant differs from the base inlay only in `fpc_ribbon_divet_z_extend_below_inlay_mm` (3 → 2). All other dimensions are identical.
- Export tolerances: STL mesh export at OpenSCAD default `$fn = 48` → mesh faceting visible at <0.05 mm on rounded corners. STEP is reconstructed from that mesh, so rounded corners (outer corner radius, bullnose, pillar inner-corner fillet, joystick hole) appear as many flat facets rather than true analytic curves.
