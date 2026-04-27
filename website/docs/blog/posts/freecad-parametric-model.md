---
date: 2026-04-27
authors:
  - rompasaurus
categories:
  - Hardware
  - CAD
slug: freecad-parametric-model
---

# OpenSCAD to FreeCAD — Full Parametric Enclosure in PartDesign

Translated the entire Dilder Rev 2 three-part enclosure from OpenSCAD into a proper FreeCAD PartDesign model with an editable feature tree and spreadsheet-driven parameters.

<!-- more -->

## Why FreeCAD?

OpenSCAD is great for scripted CAD — every dimension is a variable, presets let you swap configurations, and the text-based workflow plays nicely with Git. But it has limits:

- No GUI editing — you can't click a wall and drag it thicker
- No feature tree — the entire model recomputes from scratch every time
- No visual dimension feedback — you're working blind until you render
- Export to FreeCAD/STEP for manufacturing requires manual translation

FreeCAD's PartDesign workbench solves all of these: double-click a feature, change a number, see the result instantly. The model has a proper feature history you can step through, and every dimension can be linked to a spreadsheet.

## What Was Built

Three `PartDesign::Body` objects with **81 total features** across the three parts:

| Part | Features | Key Operations |
|------|----------|---------------|
| **Base Plate** | 33 | Sketch+Pad shell, 2 fillets (corners + bottom), SubtractiveBox pocket, USB-C stadium cutout (3 features), solar pit, wire holes, 4 pillars + 4 extension wings + 4 pegs, 2 battery troughs with cylinder cuts, USB support blocks, Pico retention block |
| **AAA Cradle** | 26 | Sketch+Pad plug, 4 pillar cutouts, FPC gap, 2 battery bays (cylinder + top-open slot), Pico nest, connecting block with battery arcs + TP4056 indent, 4 clip slots + 4 retainer windows |
| **Top Cover** | 22 | Sketch+Pad shell, corner + bullnose fillets, interior cavity, 4 corner pillars, screen inlay, display window, joystick hole, 4 M3 bores, joystick PCB pocket, FPC divet |

All linked to a **90-parameter spreadsheet** — change a cell value, recompute, and the model updates.

## The Translation Process

The original OpenSCAD models use CSG (Constructive Solid Geometry) — union, difference, intersection of primitives. FreeCAD's PartDesign is sequential: each feature modifies the solid in order.

The initial approach used `Part::Feature` (frozen shapes) which looked right but couldn't be edited. The final version uses real PartDesign operations:

- **Sketch + Pad** for the outer shells (constrained rectangle on XY plane)
- **SubtractiveBox / SubtractiveCylinder** for all cuts (avoids face-coordinate-system headaches when cutting on non-XY faces)
- **AdditiveBox / AdditiveCylinder** for pillars, pegs, support blocks
- **Fillet** for corner rounding and bottom edge curves
- **Expressions** linking feature dimensions to spreadsheet cells

## Editing Workflow

1. Open `Dilder_Rev2_PartDesign.FCStd` in FreeCAD
2. Expand a Body in the tree — see every feature in build order
3. Click a feature → **Data tab** at bottom-left shows all dimensions
4. Change a value directly, or edit the Parameters spreadsheet + **Ctrl+Shift+R**
5. Export to STL/3MF for printing

## Files

- `hardware-design/freecad/dilder_rev2_partdesign.FCMacro` — the macro that generates everything
- `hardware-design/freecad/Dilder_Rev2_PartDesign.FCStd` — pre-built model (open directly)
- `hardware-design/freecad/*_PD.stl` — exported meshes for each part

## Lessons Learned

- **Sketch-on-face coordinate systems** are different for each face orientation — SubtractiveBox/AdditiveCylinder with explicit Placement coordinates is far more reliable for non-XY-plane features
- **Pocket direction** defaults to face normal — bottom-face pockets cut into empty space unless reversed
- **Expression-linked fields** in the Data tab are read-only — you change them in the spreadsheet, not by clicking the feature
- The **PartDesign golden pattern** applies to every feature: Select face → New Sketch → Draw → Constrain → Close → Pad/Pocket → Set depth → OK
