# Exporting OpenSCAD (.scad) to 3MF for Printing

## Prerequisites

- **OpenSCAD** installed (`openscad --version` to verify)
  - Arch/CachyOS: `sudo pacman -S openscad`
  - Ubuntu/Debian: `sudo apt install openscad`
- A slicer for your printer (PrusaSlicer, OrcaSlicer, Cura, etc.)

## Quick Export (Command Line)

```bash
# Basic export — renders the .scad and writes a .3mf
openscad -o middle.3mf middle-plate.scad

# Override a parameter at export time
openscad -D 'plate_thk=3' -o middle.3mf middle-plate.scad

# Export a specific part from a multi-part file
openscad -D 'part="base"' -o base.3mf esp32s3-enclosure.scad
```

## Export from the OpenSCAD GUI

1. Open the `.scad` file in OpenSCAD
2. Press **F5** to preview (fast, wireframe check)
3. Press **F6** to render (full CGAL render — required before export)
4. **File > Export > Export as 3MF** (or STL if your slicer prefers it)
5. Choose your filename and save

## Supported Export Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **3MF** | `.3mf` | Preferred — stores units, metadata, colors |
| **STL** | `.stl` | Universal but unitless — slicer assumes mm |
| **OFF** | `.off` | Rarely needed |
| **AMF** | `.amf` | XML-based, less common |

## Batch Export (All Parts)

For the Dilder enclosure, export all 5 parts at once:

```bash
cd hardware-design
for part in base middle topmid cover screws; do
    openscad -D "part=\"$part\"" -o "enclosure-prints/$part.3mf" esp32s3-enclosure.scad
    echo "Exported $part.3mf"
done
```

## Loading into Your Slicer

1. Open your slicer (PrusaSlicer, OrcaSlicer, Cura, etc.)
2. Import the `.3mf` file
3. The model loads at the correct scale (mm)
4. Orient the part for printing:
   - **base** — print upside-down (flip 180 on X)
   - **middle** — print flat, no supports needed
   - **topmid** — print top-face-down so snap rails point up
   - **cover** — print dome-side-up
   - **screws** — print standing upright
5. Slice and send to printer

## Recommended Print Settings

| Setting | Value |
|---------|-------|
| Layer height | 0.2mm (0.16mm for screws) |
| Infill | 20-30% |
| Walls/perimeters | 3 |
| Supports | None (designed support-free) |
| Material | PLA or PETG |
| Bed adhesion | Brim for base/cover, none for plates |

## Troubleshooting

**"WARNING: Object may not be a valid 2-manifold"**
- The mesh has holes or self-intersections. Fix in the .scad by ensuring all `difference()` cuts extend past the surfaces (use `-1` / `+2` offsets on cut objects).

**Export takes forever**
- Reduce `$fn` for previewing (`$fn = 24`), then set it back to 48+ for final export.
- Avoid `minkowski()` and `hull()` on complex shapes when possible.

**Model is tiny/huge in slicer**
- 3MF preserves units. STL does not — make sure your slicer is set to millimeters.

**"Current top level object is not a 3D object"**
- You have a 2D shape (e.g. `square()`) without an `extrude`. Wrap it in `linear_extrude()`.
