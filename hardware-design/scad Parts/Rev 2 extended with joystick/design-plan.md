# Rev 2 Extended — Joystick Base Design Plan

Source sketches: `IMG20260422215826.jpg` (side+top), `IMG20260422215927.jpg` (same view, with labels `Battery` / `Esp32`).

## Intent

- Battery lies flat on the **left** half of the enclosure.
- ESP32 board stack sits to the **right** of the battery and **overhangs ~2 mm onto the battery top**, so the board's left edge is supported by the battery shelf rather than hitting the floor.
- This part is **the BASE** of the case only: curved bottom, four corner pillars with screw holes (same style as `enclosure-prints/base.3mf`), footprint sized for the extended-with-joystick Rev 2 stack.
- Later iterations will add: middle plate, top cover with joystick window, wire routing channels.

## Measurements read from the sketch

All values in millimetres. Where the handwriting was ambiguous I picked the value that makes the side + top views close numerically.

### Side view (long axis, looking from +Y)

```
   <----------- 56.7 ----------->|<----- 26.8 ----->
   +-----------------------------+                    ---
   |                             |                     |
   |       [ Battery ]           +-- 2 ----+           | 22
   |                             | [ ESP32 stack ]     |   (total height)
   |                             |  19 mm cavity       |
   +-----------------------------+---------+-----------+
   ^                                                   ^
   22 mm tall on the left (battery chamber full-height)
                                           .2 mm right-edge lip note
```

| Label on sketch | Meaning | Value |
|---|---|---|
| `56.7 mm` | Battery compartment length (outer, includes left wall) | 56.7 |
| `26.8 mm` | ESP32 compartment length (outer, includes right wall) | 26.8 |
| Sum (56.7 + 26.8) | Total outer length, with ~1.5 mm shared at the divider | ≈ 82 |
| `19 mm` | ESP32 cavity inner length | 19 |
| `22 mm` | Total enclosure height (battery chamber full-depth) | 22 |
| `2 mm` | Step where ESP32 PCB overhangs battery top | 2 |
| `.2 mm` | Right-side wall trim note (thin rim, not critical) | — |

### Top view (looking down, −Z)

```
    <-------------------- 82 mm -------------------->
    +-----+---------------------------+-------+------+   ^
    | O   ` - - - - - - - - - - - - - - - - - `    O |   |  4 mm margin
    |     | <-- 51 mm -->|            |<-35 mm->|    |   |
    |     |              |            |         |    |   |
    |     |   Battery    |  divider   |  ESP32  |    |  44 mm
    |     |  ~51 x 34    |            | ~35 x 34|    |
    |     |              |            |         |    |   |
    |     ` - - - - - - - - - - - - - - - - - - `    |   |  4 mm margin
    | O                                            O |   |
    +------------------------------------------------+   v
```

| Label on sketch | Meaning | Value |
|---|---|---|
| `82 mm` | Outer width (X) | 82 |
| `44 mm` | Outer depth (Y) | 44 |
| `51 mm` | Battery cavity inner length (X) | 51 |
| `35 mm` | ESP32 cavity inner length (X) | 35 |
| `4 mm` | Margin from outer wall to cavity top/bottom (Y) on each long edge | 4 |
| `3…` (left inner, partially legible) | Battery cavity inner depth (Y) | ~34 |
| `O` (×4 corners) | Corner pillars with screw holes | 4 ×  M3 |

Note: `51 + 35 = 86`, outer is `82`. The 4 mm difference is the **overlap zone** where the ESP32 cavity extends 4 mm over the battery cavity in top view — consistent with the side-view "boards slightly overhang the battery" intent.

## Derived dimensions (what I build to)

The battery cell is confirmed as the **same 1000 mAh pack used in `top-cover-v3`**:
`52 × 35 mm` footprint. The battery chamber dimensions come from that spec
plus `slop`, not from the sketch's nearest-mm guesses (`51`, `34`).

The ESP32 is **slightly thinner in Y than the battery**, so the ESP32 chamber
narrows to ~29 mm in Y, centered on the enclosure Y axis.

| Parameter | Value | Notes |
|---|---|---|
| `enclosure_outer_width_along_x_axis_mm` | 82 | X |
| `enclosure_outer_depth_along_y_axis_mm` | 44 | Y |
| `enclosure_total_height_along_z_axis_mm` | 22 | Z, pillar height |
| `perimeter_outer_wall_thickness_mm` | 2 | ±Y long walls, project convention |
| `plus_x_usb_side_end_wall_thickness_mm` | **1.2** | Thin +X wall so USB-C ports pop through cleanly |
| `minus_x_battery_side_end_wall_thickness_mm` | **3** | Thicker -X wall on the battery end |
| `base_floor_plate_thickness_mm` | 2 | Project convention |
| `outer_case_bottom_edge_fillet_radius_mm` | 2 | The "curved bottom" |
| `outer_case_top_view_corner_radius_mm` | **4** | Reduced from 6 so the +X corner pillars tuck inside the arc (the thin 1.2 mm +X wall pulled the pillar corners past a 6 mm arc, causing visible plane-popping) |
| `corner_pillar_square_side_length_mm` | 5 | Project convention |
| `corner_pillar_inner_facing_corner_radius_mm` | 1 | Matches windowed plates |
| `m3_screw_clearance_hole_diameter_mm` | 3.2 | M3 through-hole |
| `print_fit_tolerance_slop_mm` | 0.4 | Project convention |
| `battery_cell_footprint_length_x_mm` | 52 | 1000 mAh cell, per `top-cover-v3` |
| `battery_cell_footprint_depth_y_mm` | 35 | 1000 mAh cell, per `top-cover-v3` |
| `battery_chamber_inner_length_along_x_axis_mm` | **52.8** | `52 + 2·slop` |
| `battery_chamber_inner_depth_along_y_axis_mm` | **35.8** | `35 + 2·slop` |
| `esp32_board_footprint_depth_y_mm` | 28 | Matches `top-cover-v3` `board_wid` |
| `esp32_chamber_inner_depth_along_y_axis_mm` | **28.8** | `28 + 2·slop`, narrower than battery |
| `esp32_chamber_inner_length_along_x_axis_mm` | 19 | From side-view sketch |
| `esp32_overhang_shelf_height_above_battery_floor_mm` | 2 | Battery/PCB overlap step |
| `battery_to_esp32_internal_divider_wall_thickness_mm` | 2 | Inner rib between chambers |
| `esp32_cavity_overhang_onto_battery_length_x_mm` | 4 | PCB overhangs battery in X |
| `usb_c_panel_cutout_width_along_y_axis_mm` | 9.5 | Per port, standard Type-C receptacle |
| `usb_c_panel_cutout_height_along_z_axis_mm` | 4.0 | Per port |
| `usb_c_port_vertical_center_z_mm` | 13 | Guess — tune to real PCB height |
| `usb_c_port_center_y_positions_list` | `[16, 28]` | Two ports symmetric about Y=22, 12 mm apart |

## Base features (what the SCAD produces)

1. Rounded-rectangle outer shell, **82 × 44**, top-view corner radius **6 mm**.
2. **2 mm fillet** on the bottom edge all around — the "curved bottom".
3. Perimeter wall **2 mm**, rising to **22 mm** (pillar top).
4. Four **5 × 5 mm** corner pillars flush inside the wall, each with an M3 **Ø 3.2 mm** through-hole.
5. **2 mm divider** rib between the battery chamber (left) and ESP32 chamber (right), oriented along Y.
6. Battery chamber floor at `z=2`. Clear inside = **52.8 × 35.8 × 20**.
7. ESP32 shelf at `z=4` (the 2 mm overhang step). Clear inside = **23 × 28.8 × 18** (includes the 4 mm of overhang back over the battery top).
8. ESP32 chamber is **centered in Y** and ~3.5 mm narrower on each side than the battery, giving a visible step in top view — matches the "ESP is slightly thinner than the battery" note.
9. **Two USB-C cutouts** through the +X end wall at the ESP32 chamber. Defaults are `9.5 × 4.0 mm` openings at `z_center = 13 mm`, with Y centers at `y = 16 mm` and `y = 28 mm`. Expect to tweak these once the exact PCB port positions are measured.

## Files in this folder

| File | Purpose |
|---|---|
| `IMG20260422215826.jpg`, `IMG20260422215927.jpg` | Source sketches (converted from HEIC) |
| `design-plan.md` | This document |
| `base-v1.scad` | Parametric base — edit constants at the top to tweak |
| `base-v1.stl` | STL render (sanity-check the geometry) |
| `base-v1.3mf` | Slicer-ready export, project convention |
| `base-v1-top.png` | Orthographic top view |
| `base-v1-side.png` | Orthographic side view |
| `base-v1-iso.png` | Isometric view of the hollowed base |
| `base-v1-end-plusx.png` | +X end view — shows the two USB-C cutouts |

## Out of scope for this pass

- Joystick cutout in the top cover (belongs to top-cover-v2 rev).
- Wire routing channels through the divider.
- Battery strap anchors.
- Middle plate screw slots (handled by a separate middle plate as before).

## Confirmed by user

- Battery is the **same 1000 mAh cell** as `top-cover-v3` (52 × 35 mm footprint) — the sketch's 56.7 mm is the OUTER side-view length (52 + wall + wall ≈ 56), not a new cell.
- ESP32 is **slightly thinner in Y than the battery** — ESP32 chamber narrows to 28.8 mm (centered) while the battery chamber stays at 35.8 mm.
- **Two USB-C ports** on the board pop through the +X end wall — both cut out and each extended inward as an explicit port-body pocket so the through-hole in the wall lines up with the port behind it.
- **USB-C port dimensions**: cutout is **7.8 mm long** (Y) × **2.8 mm tall** (Z), where 2.8 = 2.6 mm port body + **0.2 mm extra** allowance so the board lies flat against the plastic.
- **Asymmetric end walls** in X: the +X (USB-C) end is thin at **1.2 mm** so the ports punch through cleanly; the -X (battery) end is thickened to **3 mm** for strength and balance. The ±Y long walls stay at the project-default 2 mm.
- **Board orientation**: board lies INSIDE the base on the ESP32 shelf, component-side UP (headers facing up). USB-C ports are therefore **close to the base floor** — cutout Z center is **7 mm** (PCB on shelf at z=4 → PCB top at z=5.6 → port body z=5.6–8.2 → center 6.9 ≈ 7).
- **Screw holes fully embedded**: the battery cavity subtract is carved AROUND each corner pillar, not through it, so every M3 screw hole is fully inside solid pillar material with no open slice exposing it to the chamber.
- **USB-C shelf divets**: a `0.2 mm × 8 mm × 7.8 mm` recess is carved into the top of the ESP32 shelf under each USB-C port so the port's underside shield tab has somewhere to sit and the PCB rests flat. Divets stop at the inner face of the +X wall — they do **not** break through to the outside (earlier render had them punching through, which looked like a thin clipping slit below each USB-C cutout; fixed).
- **Pillars clipped to shell**: the corner pillars are `intersection()`'d with the outer shell so their outer bottom corners inherit the `2 mm` bottom fillet curve. Without this, each pillar's flat outer corner at `z≈0` poked `~1.4 mm` outside the shrunken z=0 shell outline (the shell contracts inward by `fillet_r` at the bottom due to the minkowski-sphere fillet), showing as a plane popping out of the curved bottom on the front face. Pillars now follow the fillet cleanly.

## Still to confirm

1. Exact Y centers of the two USB-C ports on the real board. Defaults of **16 mm and 28 mm** (symmetric about Y=22, 12 mm apart) are placeholders — tweak `usb_c_port_center_y_positions_list` after measuring.
2. Actual USB-C port body depth (default `usb_c_port_body_recess_depth_into_enclosure_mm = 8 mm`, typical for SMT Type-C receptacles).
3. Joystick cutout in the top cover — deferred to the top-cover pass.

---

## v1.1 — Resize pass (2026-04-23)

Outer footprint extended along X, total height lowered, battery cell scaled up
to match a longer cell, and the step down into the battery pit deepened to give
the cell more vertical clearance under the ESP32 overhang.

| Parameter | Old | New | Notes |
|---|---|---|---|
| `enclosure_outer_width_along_x_axis_mm` | 82 | **96** | Outer X extended +14 mm |
| `enclosure_total_height_along_z_axis_mm` | 22 | **12** | Total height lowered -10 mm |
| `battery_cell_footprint_length_x_mm` | 52 | **66** | Cell is 14 mm longer |
| `battery_chamber_inner_length_along_x_axis_mm` | 52.8 | **66.8** | Derived = cell + 2·slop |
| `esp32_overhang_shelf_height_above_battery_floor_mm` | 2 | **5** | Shelf raised 3 mm → battery pit 3 mm deeper under the overhang |
| `usb_c_port_vertical_center_z_mm` | 7 | **6** | USB cutouts drop 1 mm |

### Derived consequences

- Battery chamber inner Z clearance: **10 mm** (floor z=2 → top z=12). The 5 mm cell still fits with 5 mm of headroom.
- ESP32 chamber inner Z clearance: **5 mm** (shelf z=7 → top z=12). PCB (1.6 mm) + USB-C port body (2.6 mm) = 4.2 mm fits.
- Battery-pit depth under the ESP32 overhang shelf: **5 mm** (up from 2 mm). With the cell seated on the battery floor and the ESP32 PCB at z=7+, the cell has 3 mm more "nose room" under the PCB before binding.
- USB-C cutout now spans z=4.6 to z=7.4 — i.e., straddles the ESP32 shelf level (z=7). The cutout's recess-into-enclosure carves through the shelf locally under each port, which OpenSCAD handles cleanly since the recess is a difference() subtraction.
- ESP32 chamber inner X length now falls out of the length equation at **~21.4 mm** (was 19 mm) because the outer grew by 14 mm while the battery chamber grew by the same 14 mm — the remainder for the ESP32 side comes from the 4 mm overhang + the extra shell-trim math.

### Open questions after this pass

- If the real board's USB-C port center lands at z ≈ 9–10 mm (PCB on shelf z=7, port body above PCB), a z_center of 6 mm puts the cutout **below** the port body. This is intentional per the user's spec but worth re-measuring once the real PCB is in hand — may need to drop the shelf, flip the board component-side down, or re-lift the cutout.
