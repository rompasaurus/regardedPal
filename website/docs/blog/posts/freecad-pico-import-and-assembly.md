---
date: 2026-04-29
authors:
  - rompasaurus
categories:
  - Hardware
  - CAD
  - FreeCAD
slug: freecad-pico-import-and-assembly
---

# Pico 2 W in the FreeCAD Assembly — STEP Import, Procedural Headers, Z-Flip Mount

The Rev 2 Mk2 enclosure was already a parametric three-body FreeCAD model (base plate, AAA cradle, top cover). What it was missing was the actual electronics. This pass adds the Raspberry Pi Pico 2 W board — imported from the official STEP file — plus a procedural 2×20 pin-header rail, mounted upside-down inside the cradle's PicoNest cavity with its component-side face flush against the cradle mating plane.

<!-- more -->

## What changed

| Before | After |
|--------|-------|
| Three empty enclosure shells | Three shells **+** a Pico 2 W board with full pin headers |
| Pico position implied by `pico_bx`, `pico_by` parameters only | Pico **physically present** in the assembly, anchored to named cradle faces |
| Assembly file size ~1 MB | ~1.2 MB (board STEP geometry merged in) |

Four new render angles show the result: an isometric with translucent cover, a no-cover view, a cradle-hidden view (so the Pico's seat on the base plate is visible), and a front elevation.

## Finding a model

Raspberry Pi Foundation publishes an official STEP file for the **Pico 2** but not for the **Pico 2 W** — the wireless variant is mechanically identical apart from the antenna module on top, so the same STEP works for enclosure fitment. The download lives at:

```
https://datasheets.raspberrypi.com/pico/Pico-R3-step.zip → redirects → Pico 2 STEP
```

Probing the URL confirmed it returns a real ZIP (not a 404 HTML page) and unzipping yields:

```
RP-006426-DD-A-Raspberry Pi Pico 2 3D CAD Model R5 24 07 24.step  (1.7 MB)
```

That file got renamed to `RaspberryPi-Pico-2.step` and committed under `hardware-design/reference-boards/raspberry-pi-pico-2/`.

## Step 1 — Importing without orientation guessing

`Part.Shape().read(path)` loads a STEP file as a raw `Part.Shape`. The trouble is the SolidWorks export uses Y-up (board normal on the Y axis), and the long board edge sometimes lands on the Z axis instead of X. Hand-coding the rotation works exactly once and breaks the next time someone updates the STEP.

Instead, the macro reads the bounding box and uses the dimensions themselves to drive the rotation:

```python
bb0 = shape.BoundBox
dims = [bb0.XLength, bb0.YLength, bb0.ZLength]
short = dims.index(min(dims))   # which axis is the 1mm board thickness?
m = App.Matrix()
if short == 0:
    m.rotateY(math.radians(90))
elif short == 1:
    m.rotateX(math.radians(90))
shape = shape.transformGeometry(m)

# After thickness → +Z, ensure the long axis (51mm) lies on X, not Y
bb_chk = shape.BoundBox
if bb_chk.YLength > bb_chk.XLength:
    m_z = App.Matrix(); m_z.rotateZ(math.radians(90))
    shape = shape.transformGeometry(m_z)
```

After two checks the board is guaranteed to be flat in XY with components on +Z, long axis on X. No matter what coordinate system the source CAD used.

## Step 2 — Procedural pin headers

The official STEP doesn't include headers — they ship soldered separately. Modeling 40 individual pins with cylinders would be wasteful, so the macro builds:

- 2 plastic shroud strips (one per long edge), 2.54 mm wide × 50.8 mm long × 2.54 mm tall
- 40 brass pins (0.64 mm square × 8.6 mm tall) on a 2.54 mm pitch, 1 mm in from each long board edge

```python
for row_y in (bb.YMin + row_inset, bb.YMax - row_inset):
    pieces.append(Part.makeBox(strip_len, pin_pitch, shroud_h, ...))
    for n in range(pin_count):
        pieces.append(Part.makeBox(pin_w, pin_w, pin_above, ...))
header_shape = Part.Compound(pieces)
```

Headers are built **below** the board (shroud at `pcb_z_bot - shroud_h`, pins below the shroud). This sounds wrong until step 3.

## Step 3 — The Z-flip

The Pico's intended mount in the Rev 2 design is *underneath* the cradle PCB cradle insert: chips face down toward the base plate, headers point up to plug into the cradle. So after building everything in the obvious "right side up" frame, the macro applies a single 180° rotation about the world X axis to flip the entire stack:

```python
m_flip_z = App.Matrix(); m_flip_z.rotateX(math.radians(180))
shape = shape.transformGeometry(m_flip_z)
header_shape = header_shape.transformGeometry(m_flip_z)
```

After the flip:

- The board's component side now faces **−Z** (down toward the base plate)
- The board's back face (originally bottom, no components) faces **+Z** (up toward the cradle)
- Headers were below the board, now they're above the board, pins pointing **+Z**

Building headers below the board pre-flip is exactly equivalent to building them above the board post-flip — just simpler, because the geometry generation can use the un-rotated bounding box.

## Step 4 — Anchoring to named cradle faces

Hard-coding XYZ offsets is brittle. Change a cradle parameter and everything drifts. Instead the macro looks up two specific cradle faces by name and uses their global coordinates as anchors:

```python
PICO_ANCHOR_FACE   = ("AAACradle", 44)   # X anchor: -X edge of board
PICO_Z_ANCHOR_FACE = ("AAACradle", 6)    # Z anchor: cradle mating plane
```

`AAACradle.Face44` is the inner −X wall of the PicoNest cavity (in global coordinates after the cradle's 180° Y rotation places it). The macro resolves it like this:

```python
def resolve_face_global(spec):
    body_name, face_idx = spec
    body = doc.getObject(body_name)
    f = body.Tip.Shape.Faces[face_idx - 1]
    return body.Placement.multVec(f.CenterOfMass), f"{body_name}.Face{face_idx}"
```

The board's `bbox.XMin` (after the optional 180° Z reverse) gets translated to land on Face44's global X. The board's component-side plane (`bbox.ZMax − 1mm` after the flip) gets translated to land on Face6's global Z.

One subtlety: the cradle's `Placement` is set in `main()` *after* its body is built. The Pico import has to run **after** the assembly placements have been applied so face positions resolve in global coordinates, not in the cradle's local pre-rotation frame.

```python
bp = build_base_plate(doc)
cr = build_cradle(doc)
tc = build_top_cover(doc)
# placements applied here ↓
cr.Placement = App.Placement(V(96.3, 0, bp_top + 7.0), App.Rotation(V(0, 1, 0), 180))
doc.recompute()
# THEN the Pico import runs — face anchors now resolve globally
add_pico_with_headers(doc)
```

## Step 5 — Component-side face vs. board back

After the Z-flip, the board's bounding box ZMin is the lowest component tip and ZMax is the back of the PCB (flat, no components). The user's selection in FreeCAD pointed at the planar PCB surface visible at Z = 8.73 in the un-anchored placement — that's `bbox.ZMax − 1mm` (one board thickness below the back).

To make *that* plane sit flush with the cradle mating face, the anchor expression became:

```python
PCB_THICKNESS = 1.0
pcb_plane_z = bb_b.ZMax - PCB_THICKNESS
dz = target_z - pcb_plane_z   # not target_z - cb_zmin
```

With Face6 at global Z = 6.00:

| Location | Z |
|----------|----|
| Component tips (lowest point of bbox) | 3.27 |
| **PCB component-side face (anchored)** | **6.00** |
| Back of PCB | 7.00 |
| Header shroud top | 9.54 |
| Pin tips | 18.14 |

Components hang into the base plate's cradle pocket (Z 2.6 → 6.0) — which is exactly where the empty pocket was intentionally sized to accept them. Header pins extend up into the cradle's PicoNest cavity, ready to mate with whatever sits on top.

## Why this matters

Anchoring board geometry to **named faces of other bodies** instead of literal XY offsets means:

- Tweak a cradle parameter (say, shrink the cradle X-extent) → the Pico's `−X` anchor moves with it, no manual fix needed
- Open the macro on another machine → it deterministically reorients any Pico-shaped STEP regardless of source-CAD convention
- Add a new sensor breakout later → use the same `resolve_face_global` pattern to seat it against a different cradle face

The full macro lives at `hardware-design/freecad-mk2/dilder_rev2_mk2.FCMacro` and is documented in detail in the [FreeCAD Mk2 macro reference](../../docs/hardware/freecad-mk2-macro.md).
