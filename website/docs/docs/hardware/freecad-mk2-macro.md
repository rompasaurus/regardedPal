# FreeCAD Mk2 Macro — `dilder_rev2_mk2.FCMacro`

The Mk2 macro is the parametric source of truth for the Rev 2 enclosure. One Python file builds three `PartDesign::Body` objects (BasePlate, AAACradle, TopCover), positions them as an assembly, imports the Raspberry Pi Pico 2 W board STEP file, generates pin headers procedurally, and saves the result to `Dilder_Rev2_Mk2.FCStd`.

This page documents how the macro is structured and how to drive it.

## File layout

```
hardware-design/
├── freecad-mk2/
│   ├── dilder_rev2_mk2.FCMacro        ← the macro
│   ├── Dilder_Rev2_Mk2.FCStd          ← output document
│   ├── Dilder_Rev2_Mk2-*.3mf          ← exported meshes
│   └── BUILD-INSTRUCTIONS.txt
└── reference-boards/
    └── raspberry-pi-pico-2/
        ├── RaspberryPi-Pico-2.step    ← 1.7 MB official STEP
        └── Pico-2-step.zip
```

## Running the macro

```bash
freecadcmd hardware-design/freecad-mk2/dilder_rev2_mk2.FCMacro
```

Or open FreeCAD's GUI and run via `Macro → Macros... → Execute`. After it finishes:

- The active document is `Dilder_Rev2_Mk2`
- The file is saved alongside the macro
- Console prints feature counts per body and the Pico's final bbox

## Architecture

The macro splits cleanly into five sections:

| Section | Function | Output |
|---------|----------|--------|
| 1. Helpers | `find_edges`, `edges_at_z`, `make_rect_sketch`, `make_circle_sketch`, `SP` | Reusable utilities |
| 2. Spreadsheet | `setup_spreadsheet` | `Parameters` sheet with 100+ aliased cells |
| 3. Bodies | `build_base_plate`, `build_cradle`, `build_top_cover` | Three PartDesign Bodies |
| 4. Pico import | `add_pico_with_headers` | `Pico2W_Board` + `Pico2W_Headers` features |
| 5. Main | `main` | Spreadsheet → bodies → assembly placements → Pico import → save |

### The Parameters spreadsheet

Every dimension that anyone is likely to want to change lives in a single FreeCAD spreadsheet (`Parameters`) with named aliases. Sketches and primitives bind to these via `setExpression(...)` calls. The `SP("alias")` helper just produces the string `"Parameters.alias"`.

```python
sk.setExpression(f"Constraints[{c_w}]", SP("enc_x"))
pad.setExpression("Length", SP("bp_h"))
```

To change the enclosure width, edit `Parameters.enc_x` and recompute (`Ctrl+Shift+R`). Every dependent feature updates.

### Sketch helpers

Two helpers cover most plan-view sketches:

- `make_rect_sketch(body, name, z_offset, x0, y0, x1, y1)` — a fully constrained rectangle on the XY plane at `z_offset`, returning the sketch and the four constraint indices (`c_ox, c_oy, c_w, c_h`) so the caller can bind them to spreadsheet expressions.
- `make_circle_sketch(body, name, z_offset, cx, cy, r)` — same but for circles, returning the three constraints `(c_x, c_y, c_r)`.

For features like USB-C cutouts where a sketch on a vertical face would require fighting the face-coordinate system, the macro uses `PartDesign::SubtractiveBox` and `PartDesign::SubtractiveCylinder` with explicit XYZ placements instead. These are simpler and just as parametric (`Length`, `Width`, `Height`, `Radius` accept expressions).

### Edge finders

PartDesign Fillets need an edge list. Edge indices change as the model rebuilds, so the macro re-discovers them by orientation:

```python
find_edges(feature, axis="vertical")           # corner edges for rounding
find_edges(feature, axis="horizontal_bottom")  # bottom rim for chamfer
edges_at_z(feature, z_target=8.0)              # peg-tip rim for chamfer
```

## Body builds

### `build_base_plate(doc)`

Step-by-step:

1. Outer profile sketch (`Sk_BP_Outline`), pinned to origin
2. Pad → 6 mm box (`bp_h` post-shave)
3. Fillet vertical edges (`corner_r`)
4. Fillet bottom edges (`bp_fillet`)
5. Subtract the cradle pocket (top-down)
6. Subtract the solar pit (bottom-up)
7. USB-C stadium cutout → 3 subtractive primitives (rectangular middle, bottom strip, two corner cylinders)
8. Four corner pillars + extension wings + pegs + tip chamfers
9. Two battery rail troughs (additive box + cylinder cut)
10. Two USB support blocks
11. Pico retention block
12. Two solar wire holes (last so they cut through every additive feature added above)

The wire-hole ordering was a real bug in the first version — they were added at step 7 and only cut through what existed at that moment. Moving them to the end fixed it.

### `build_cradle(doc)`

The AAA battery cradle inserts into the base plate's pocket. Built features:

1. Plug body sketch + pad (`plug_thick = bay_d + 2 * aaa_bwall = 12.1 mm`)
2. Four pillar cutouts (matching the base plate's corner pillars)
3. FPC ribbon gap on the −X side
4. Two AAA bays (cylinder along X + top-open slot)
5. Pico nest (large rectangular subtraction across the bottom of the plug)
6. −X inset (clears space for the connecting block)
7. +X display connector cutout
8. Connecting block (re-fills the −X inset, with battery arcs cut through it)
9. TP4056 indent on the connecting block top
10. Four battery clip slots + four retainer windows

`Face44` of the cumulative cradle solid (the +X-facing inner wall of the PicoNest cavity, in cradle local coordinates) becomes the X-anchor for the Pico import. `Face6` (the +Z mating face of the plug top in local coordinates) becomes the Z-anchor.

### `build_top_cover(doc)`

The top cover is an inverted shell that snaps over the cradle. Features:

1. Outer shell sketch + pad
2. Fillet vertical edges (corner radius)
3. Fillet top edges (bullnose)
4. Interior cavity subtraction
5. Four corner pillars (fill the cavity corners to seat against the cradle)
6. Four M3 screw bores
7. Screen inlay pocket
8. FPC ribbon divet
9. Display viewing window (rectangular through-cut)
10. Joystick through-hole (cylinder)
11. Joystick PCB pocket (subtractive box from below)

## Assembly placement

After all three bodies exist, `main()` positions them in world coordinates:

```python
bp_top = 6.0   # base plate top Z (post-shave)

# Top cover — bottom face flush with base plate top
tc.Placement = App.Placement(V(0, 0, bp_top + 5.0), ROT0)

# Cradle — flipped 180° about Y, then translated so the plug-top face
# (formerly local Z=7.0) lands flush with bp_top
cr.Placement = App.Placement(
    V(96.3, 0, bp_top + 7.0),
    App.Rotation(V(0, 1, 0), 180))

doc.recompute()
```

The 180° Y rotation is what flips the cradle so its PicoNest cavity opens **downward** toward the base plate. Without it, the cradle would mount upside-down relative to the rest of the assembly.

## Pico 2 W import

`add_pico_with_headers(doc)` runs *after* the placements above. Five phases:

### 1. Read & orient

```python
shape = Part.Shape()
shape.read(step_path)

# Bbox-driven rotation: shortest axis → +Z
bb0 = shape.BoundBox
short = [bb0.XLength, bb0.YLength, bb0.ZLength].index(min(...))
m = App.Matrix()
if short == 0:   m.rotateY(math.radians(90))
elif short == 1: m.rotateX(math.radians(90))
shape = shape.transformGeometry(m)

# If long axis ended up on Y, swing it onto X
if shape.BoundBox.YLength > shape.BoundBox.XLength:
    m_z = App.Matrix(); m_z.rotateZ(math.radians(90))
    shape = shape.transformGeometry(m_z)
```

After this the board is flat in XY, components on +Z, long axis on X. The macro is robust to any source-CAD orientation.

### 2. Optional X-reverse

`PICO_USB_PLUS_X = False` flips the board 180° about Z so the USB-C end sits on the −X side of the board's bbox. This matches the Rev 2 design intent (USB-C faces the cradle's connecting block area, not the +X wall).

### 3. Procedural headers

2×20 pin headers built **below** the board. Plastic shroud (2.54 × 50.8 × 2.54 mm) sits on the board's bottom face, pins (0.64 × 0.64 × 8.6 mm) extend further below.

### 4. Z-flip

```python
m_flip_z = App.Matrix(); m_flip_z.rotateX(math.radians(180))
shape = shape.transformGeometry(m_flip_z)
header_shape = header_shape.transformGeometry(m_flip_z)
```

Both shapes rotate together. After the flip, headers are above the board, components face the base plate.

### 5. Anchor to named faces

```python
PICO_ANCHOR_FACE   = ("AAACradle", 44)   # X
PICO_Z_ANCHOR_FACE = ("AAACradle", 6)    # Z
```

`resolve_face_global(spec)` looks up the face on the cradle's Tip shape, applies the cradle's `Placement` to its center of mass, and returns the global point.

X anchor → translate so `bbox.XMin` lands on Face44's global X.
Y anchor → center the bbox at `enc_y / 2`.
Z anchor → translate so `bbox.ZMax − PCB_THICKNESS` (the post-flip component-side face) lands on Face6's global Z.

The result:

| Location | Z |
|----------|----|
| Component tips (bbox ZMin) | 3.27 |
| **PCB component face (anchored)** | **6.00** |
| Back of PCB (bbox ZMax) | 7.00 |
| Header shroud top | 9.54 |
| Pin tips | 18.14 |

## Tweaking it

| Goal | Change |
|------|--------|
| Different Pico orientation | Flip `PICO_USB_PLUS_X` |
| Different anchor face | Edit `PICO_ANCHOR_FACE` / `PICO_Z_ANCHOR_FACE` tuples |
| Different board (e.g. another 51×21 mm RP2040 clone) | Swap the STEP file path; the bbox-orient code handles re-orientation |
| Different pin header count / pitch | Edit `pin_count`, `pin_pitch`, `pin_above`, `shroud_h` |
| Add a TP4056 board | Mirror `add_pico_with_headers` with a new STEP and different anchor face |

## Limitations

- **Face indices are not stable across feature reorders.** If a new feature is inserted into the cradle build before `ClipWindow_2P`, Face44 may shift. A future improvement is to look up faces by topological signature (planar face with normal `(−1, 0, 0)` and bbox center near a specific point) instead of by index.
- **The official STEP doesn't include the wireless module** — the Pico 2 W antenna lump on top isn't represented. For mechanical fitment this doesn't matter (the cradle's PicoNest has plenty of vertical clearance).
- **Assembly is positional, not constrained.** FreeCAD's PartDesign workbench doesn't ship with assembly mates. Moving a body requires editing its `Placement` directly. The Assembly4 workbench would solve this but adds a heavy dependency.

## Output

After running, you should see the four render angles documented on the front page:

- `assembly-with-pico-iso.png` — translucent cover, full stack visible
- `assembly-with-pico-no-cover.png` — top cover hidden, cradle and Pico visible
- `assembly-with-pico-on-base.png` — cradle hidden, Pico's seating exposed
- `assembly-with-pico-front.png` — front elevation through the USB-C-cutout side

For the build narrative behind this macro, see the blog post [Pico 2 W in the FreeCAD Assembly](../../blog/posts/freecad-pico-import-and-assembly.md).
