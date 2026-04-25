# FreeCAD Modification Guide — Top Cover (Windowed + Screen Inlay)

How to open, measure, and modify the cover models in FreeCAD. Three import paths are provided; pick based on what kind of edit you need.

---

## TL;DR: which file do I open?

| Goal | Open this file | Why |
|---|---|---|
| Just look / measure / mark up | `*.FCStd` (native FreeCAD) | Fastest, includes both the mesh and the solid Part |
| Boolean edit the solid (cut a hole, round an edge, chamfer a corner) | `*.step` | Clean analytic solid, Part workbench ops work directly |
| Re-parameterize and re-export SCAD-style | `*.csg` (via OpenSCAD workbench) | Keeps the CSG tree; edit like SCAD |

Everything below assumes **FreeCAD 0.20+** (tested on 0.21). Earlier versions have janky STEP import of shapes with this many facets.

---

## 1. Opening the native `.FCStd`

1. Launch FreeCAD
2. `File → Open → <name>.FCStd`
3. You'll see a tree with two objects: `<name>_mesh` (triangle mesh, low-level) and `<name>_solid` (Part feature built from the mesh, what you want to edit)
4. Click the solid and switch to the **Part** workbench (top-left combo box)

### Measure anything

- Toolbar: `Measure distance` button (or `Measure → Distance` menu)
- Pick two vertices, edges, or faces — the distance drops into a panel
- For precise reads use `View → Draw style → As is` so the mesh faceting doesn't fool you on rounded surfaces

### Set the navigation you want

- `Edit → Preferences → Display → Navigation → Navigation cube` on
- `Navigation style = CAD`
- Middle-mouse drags rotate, Shift+middle pans, scroll zooms

---

## 2. Boolean edits on the `.step` solid (the workhorse workflow)

Use this when you want to **change** the cover — move a hole, resize the window, add a new cutout, etc. The STEP import gives you an analytic solid; Part workbench Booleans are clean.

### 2.1 Import

1. `File → Open → <name>.step`
2. Accept defaults in the import dialog (BRep, SI units)
3. Switch to the **Part** workbench

### 2.2 Example: change the joystick hole diameter from 12 mm to 14 mm

1. Create a new cylinder: `Part → Primitives → Cylinder`
   - Radius = 7 (14 / 2)
   - Height = 20 (anything taller than the cover)
   - Placement:
     - Position X = 79.35, Y = 22.0, Z = 0
     - Rotation = 0° around X/Y/Z (axis is already along Z)
2. Select the imported solid, then Ctrl-click the new cylinder
3. `Part → Boolean → Cut`
4. `Cut → Apply` → new cut solid replaces both inputs
5. The old 12 mm hole is still there from the STEP, and the new cut opens around it — the union-of-holes behaves like a wider 14 mm hole. **Clean up**: if you care, delete the cylinder BEFORE the cut, re-import, do a single subtract at the right size.

> **Tip**: for symmetric edits (four corner pillars, two FPC divets, etc.) use `Part → Compound → Make compound` on the cut tool before the boolean so one op does all four.

### 2.3 Example: add a 5 mm tab on the -X wall for a status LED

1. `Part → Primitives → Box`
   - Length = 5, Width = 8, Height = 3
   - Position X = 0, Y = 18, Z = 8 (adjust per your stack)
2. `Part → Boolean → Union` (after selecting the imported solid + the new box)
3. Done — the tab is now part of the solid

### 2.4 Example: fillet all 4 bottom outer corners

1. Select the imported solid
2. `Part → Fillet`
3. Pick the 4 bottom vertical edges (Ctrl-click each in the 3D view)
4. Radius = 2
5. OK

---

## 3. Parametric editing via OpenSCAD workbench (`.csg`)

Use this when you want to keep a **parameter-driven** model — closest to the SCAD workflow.

### 3.1 Enable OpenSCAD workbench

1. `Edit → Preferences → Workbenches → Available workbenches → enable OpenSCAD`
2. Restart FreeCAD
3. Switch to the **OpenSCAD** workbench from the combo box

### 3.2 Import

1. `File → Open → <name>.csg`
2. Import dialog should appear — just OK
3. You'll see a tree of **booleans** mirroring the SCAD tree (union, difference, intersection, hull, translate, rotate, cube, cylinder, sphere)

### 3.3 Edit the tree

- Expand a boolean node to see its children
- Select a node → edit its placement / dimensions in the Properties panel at bottom-left
- Changes recompute live (may be slow on CSG trees of this size)

### 3.4 Re-export back to STL/STEP

- `File → Export → <pick format>`
- Format options include STL, STEP, IGES, PLY, OBJ, 3MF, AMF

### 3.5 Limitations

- The CSG is a flat boolean tree; there's no way to recover the named parameters from the SCAD source (e.g., `face_plate_thickness_z_mm`) — you're editing raw numeric operands
- For actual parameter changes, **edit the `.scad` file in a text editor and re-export the CSG** (`openscad -o <name>.csg <name>.scad` from a terminal) — that remains the cleanest parametric workflow

---

## 4. Measurement verification

If you want to sanity-check dimensions against `BLUEPRINTS.md`:

1. Open the `.FCStd` or `.step`
2. Measure outer bounding box: `Part → Measure → Lengths` → pick any 2 diagonal corners of the shell — should read **91.5 × 44 × 14.5** (windowed-v1)
3. Measure joystick hole diameter: click 2 points on the circle rim at the face plate top — should read **15.0** (the tapered-top radius)
4. Measure corner pillar screw spacing: click 2 opposite-corner screw-hole centers — should read **√(82.3² + 35.0²) ≈ 89.4**

If any measurement is off by more than **0.1 mm**, the mesh-to-solid conversion accumulated rounding on that feature — use the SCAD source as authoritative and regenerate.

---

## 5. Exporting for slicer / 3D print

From any of the three file types:

1. Make sure only the solid is selected (not the mesh, if opening `.FCStd`)
2. `File → Export → Mesh STL (*.stl)` → pick ASCII or Binary (Binary is smaller)
3. Slicer (PrusaSlicer, Cura, Bambu Studio, etc.) reads the STL directly

For `.3mf` with metadata:
1. `File → Export → 3D Manufacturing Format (*.3mf)`

---

## 6. Regenerating everything from scratch

All exports in this folder came from a single pipeline. To regenerate after editing the SCAD:

```bash
cd "/home/rompasaurus/CodingProjects/Dilder/hardware-design/scad Parts/Rev 2 extended with joystick"

# 1. Export STL + CSG from SCAD
for f in top-cover-windowed-v1 top-cover-windowed-screen-inlay-v1 top-cover-windowed-screen-inlay-v1-2mm; do
  openscad -o "${f}.stl"                  "${f}.scad"
  openscad -o "freecad-export/${f}.csg"   "${f}.scad"
done

# 2. Convert STL → STEP + FCStd via the helper
freecadcmd /tmp/scad-to-step.py
```

The helper script is in `/tmp/scad-to-step.py` (reproduced below for reference):

```python
#!/usr/bin/env freecadcmd
import os, FreeCAD, Part, Mesh
base = "/home/rompasaurus/CodingProjects/Dilder/hardware-design/scad Parts/Rev 2 extended with joystick"
export = os.path.join(base, "freecad-export")
os.makedirs(export, exist_ok=True)

for name in ["top-cover-windowed-v1", "top-cover-windowed-screen-inlay-v1",
             "top-cover-windowed-screen-inlay-v1-2mm"]:
    stl = os.path.join(base, f"{name}.stl")
    doc = FreeCAD.newDocument(name)
    mesh = Mesh.Mesh(stl)
    mesh_obj = doc.addObject("Mesh::Feature", f"{name}_mesh"); mesh_obj.Mesh = mesh
    shape = Part.Shape(); shape.makeShapeFromMesh(mesh.Topology, 0.05)
    solid = Part.Solid(Part.Shell(shape.Faces))
    part_obj = doc.addObject("Part::Feature", f"{name}_solid"); part_obj.Shape = solid
    doc.recompute()
    doc.saveAs(os.path.join(export, f"{name}.FCStd"))
    Part.export([part_obj], os.path.join(export, f"{name}.step"))
    FreeCAD.closeDocument(doc.Name)
```

---

## 7. Gotchas

- **The STEP's rounded surfaces are faceted**, not analytically smooth. At `$fn = 48` in the SCAD, a 4 mm-radius corner becomes 48 tiny flat faces instead of one curved face. If you need true analytic curves in FreeCAD (for silky fillets or measurements beyond 0.05 mm), rebuild the cover in the Part workbench from scratch using the dimensions in `BLUEPRINTS.md` — the SCAD is the parametric source-of-truth, not the STEP export.

- **Hole placement uses the cover's LOCAL frame.** Origin at -X -Y outer corner, Z=0 at mating bottom. FreeCAD respects that.

- **Units**: all files are metric (mm). If FreeCAD opens with imperial, toggle `Edit → Preferences → General → Units → Metric (small parts)`.

- **Large STEP load time**: ~4-8 seconds on a modern machine. If FreeCAD appears frozen during open, give it up to 20 seconds.

- The **screen-inlay-v1-2mm** file differs from screen-inlay-v1 only in the FPC divet Z extension (2 mm vs 3 mm). Visually almost identical; compare the -X wall profile views.
