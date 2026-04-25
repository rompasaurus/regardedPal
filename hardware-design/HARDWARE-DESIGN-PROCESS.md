# Dilder Hardware Design Process

A retrospective on how the Dilder enclosure and joystick PCB have actually
been designed (versus how engineering blogs say it should be done), and a
playbook for cutting the print-waste budget on future iterations.

This document is descriptive first — the loop we've been running for ~25
prints worth of iteration — and prescriptive second, where the experience
has surfaced clear ways to reduce wasted plastic.

---

## TL;DR

We've been running a tight **edit → preview → render → print → measure →
repeat** loop for the SCAD enclosure and a separate **schematic →
footprint → layout → autoroute → DRC** loop for the PCB. Both work, but
the SCAD loop has a print-waste tax that scales linearly with iteration
count. Most of that tax is avoidable by:

1. Doing **dimensional checks against real hardware before printing**, not
   after.
2. Replacing fit-check prints with **calibration coupons** (small parts
   that test one tolerance at a time).
3. Using **OpenSCAD presets + `export-preset.py`** to A/B variants in
   slicer rendering before printing the loser.
4. Treating **SVG layouts and 2D cross-sections** as first-class outputs
   for fit verification (cheap, instant, just as accurate as a print for
   linear dimensions).

---

## The current loop (descriptive)

### Enclosure (OpenSCAD → FDM print)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Edit .scad in   │────▶│ F5 preview in   │────▶│ Eyeball-OK?     │
│ VS Code         │     │ OpenSCAD GUI    │     │ Yes ↓  No ↑     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Print, measure, │◀────│ Slicer (Bambu/  │◀────│ scad-export.py  │
│ test fit        │     │ Orca/Prusa)     │     │ → 3MF           │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │
        ▼  measurements / fit notes
   ┌──────────────────┐
   │ Edit .scad — go  │
   │ back to top loop │
   └──────────────────┘
```

The full cycle for a single dimensional change is roughly:

| Step | Time |
|------|------|
| SCAD edit | 1–10 min |
| F5 preview | <5 s |
| `scad-export.py` → 3MF | 10–60 s (CGAL render) |
| Slice + send to printer | 1–3 min |
| **Print** | **5 min – 2 hr** depending on part |
| Cool, eject, deburr | 1–5 min |
| Fit check + measurement | 1–5 min |
| **Total per iteration** | **~10 min – 2.5 hr** |

The bottleneck is overwhelmingly the print. The SCAD edit→preview portion
is essentially free; the iteration cost is the printed plastic and the
clock time.

### PCB (KiCad → Freerouting → fab)

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│ Edit         │────▶│ Schematic     │────▶│ Update PCB   │
│ schematic    │     │ ERC clean?    │     │ from sch     │
└──────────────┘     └───────────────┘     └──────────────┘
                                                   │
                                                   ▼
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│ kicad-cli    │◀────│ ImportSpecctra│◀────│ Place parts; │
│ pcb drc      │     │ SES (python   │     │ ExportSpecc- │
│ → DRC clean? │     │ pcbnew)       │     │ traDSN       │
└──────────────┘     └───────────────┘     └──────────────┘
        │                                          │
        │ DRC clean                                ▼
        ▼                                  ┌──────────────┐
┌──────────────┐                           │ Freerouting  │
│ Render PNG   │                           │ headless     │
│ → blog,      │                           │ (Docker)     │
│ design-evol  │                           └──────────────┘
└──────────────┘                                   │
                                                   └─ writes .ses
```

PCB iteration is **completely free** until you fab — the whole loop runs
on the machine in seconds. The cost is shifted to the end: a wrong fab
is $15+shipping+a week. The mitigation is: never fab without `kicad-cli
pcb drc` clean, with parity against the schematic enforced.

---

## Where we've burned plastic (specific incidents)

A non-exhaustive list of prints from this project that turned out to be
mostly wasted, and what should have caught the problem upstream:

| Print | What was wrong | Could have been caught by |
|-------|----------------|--------------------------|
| Top cover v1 (windowed) | Window 50×25 mm — wrong; Waveshare's actual viewable area is 48×27 mm | Measuring the part with calipers before cutting the window |
| Top cover v1.x (multiple) | Inlay depth wrong by 1–2 mm across several iterations | Stacking actual module + FPC and measuring with a depth gauge |
| Cradle v1 → v2 | Connecting block too small for TP4056 board (9.5 mm vs 28 mm) | Reading the TP4056 datasheet before the first print |
| Base plate v1 → v2 → v3 | USB-C notch wrong location, wrong size, wrong wall thickness | Cross-section preview in OpenSCAD against a known cable footprint |
| Joystick PCB Rev 1 | Wire pad J1.6 overlapped M3 hole; routing physically infeasible | Computing pad/hole clearances *before* drawing them — `python3` math, no print needed |

Across these, the common pattern is **physical-feature dimensions guessed
from screenshots or memory, not measured from the real component or its
datasheet**. The print catches the mistake, but at high cost.

---

## Improvements (prescriptive)

The following are concrete, low-effort changes to the current workflow
that reduce wasted prints. Ordered roughly by ROI (highest first).

### 1. Mandatory pre-print dimensional check against real hardware

Before exporting any SCAD that mates with a physical component, *the
SCAD must reference the component's measured dimensions in a comment
block*, e.g.:

```scad
// === Waveshare 2.13" e-Paper ===
// Measured 2026-04-22 with calipers:
//   Module: 48.55 x 26.90 x 1.18 mm
//   Active area: 48.0 x 27.0 mm (datasheet)
//   FPC ribbon: 6.5 mm wide, exits +X edge
//   FPC pivot (fold point): 3.2 mm from active area edge
display_width  = 48.0;  // active area, not module
display_height = 27.0;
display_thk    = 1.18;  // module top to bottom of active area
```

This forces the dimensions into the SCAD and into git. If a print later
turns out wrong, the comment block is the source of truth that gets
audited, not your memory.

**Process gate**: no `scad-export.py` until the SCAD's parametrically-
relevant dimensions all trace back to a measurement comment block.

### 2. Calibration coupons instead of full prints

A "calibration coupon" is a 20 × 20 × 5 mm test print that exercises one
tolerance: a single peg+hole pair, a single channel, a single chamfer. It
prints in 10–15 minutes on a 0.2 mm layer height and tells you exactly
the same thing as a 2-hour full-part print.

**Concrete coupons we should have**:

- `coupon-m3-clearance.scad` — 4 holes at Ø3.0/3.1/3.2/3.3 mm, label
  silkscreened next to each. Tests M3 free fit vs press fit on this
  printer/filament/temperature. Reuse the result for *every* mounting
  hole going forward.
- `coupon-usbc-port.scad` — sample wall with 4 USB-C cutouts at varying
  width × height. Plug a real cable in. Lock in the right pair.
- `coupon-snap-rib.scad` — 6 rib variants for cover/base mating.
- `coupon-batt-bay-aaa.scad` — single-cell bay at varying ID. Drop a
  battery in.

Run the coupon set **once per filament/printer combination**, then refer
to the chosen tolerances by name in subsequent SCADs. Stop guessing
tolerances afresh on every part.

### 3. SVG cross-sections for fit verification

OpenSCAD can export 2D `.svg` profiles via `projection(cut=true)`. For
linear-dimension fit checks (does this slot fit this connector?
does this pocket fit this PCB?), an SVG opened in any viewer is identical
information to a printed fit-check coupon — and free.

Workflow:

```bash
# In the SCAD, add a 'part="section_xy"' that uses projection(cut=true)
openscad -D 'part="section_xy"' -o /tmp/section.svg my-part.scad
inkscape /tmp/section.svg   # or any SVG viewer
# Measure with the viewer's ruler tool against the cable/PCB CAD
```

Add a `section_*` part to every SCAD that mates with non-trivial
hardware. F5 + view-SVG is a sub-10-second iteration loop.

### 4. OpenSCAD customizer presets + `export-preset.py` for A/B

When uncertain between two dimensional choices, **don't print both**.
Save them as customizer presets in the SCAD's JSON sidecar, render both
to 3MF with `export-preset.py`, slice both, **inspect the slicer
preview** for the actual mating geometry, and only print the one that
looks right. The slicer preview IS the dimensional truth at the
0.05 mm level for any external feature.

This caught nothing on Rev 2 because we didn't use it. It's available
now via `hardware-design/scad Parts/export-preset.py` and documented in
that folder's `README.md`.

### 5. Parametric "test slider" prints

For complex tolerance stacks (cradle insert + base plate + cover snap
fit), a single print that contains the tolerance range as a strip — say,
8 cradle bays at ±0.05 mm steps from the design value — gives 8
empirical data points per print instead of 1. This is the same idea as
calibration coupons but for compound features that can't be reduced to a
single dimension.

Build it as a SCAD with a `for(dx = [-0.2 : 0.05 : 0.2])` loop instead
of as a series of separate prints.

### 6. Treat the PCB design loop as the model

The PCB went straight from "totally broken Rev 1" to "DRC-clean, fab-
ready Rev 2" in one session because every step had a free machine-
checkable verification:

- ERC catches schematic errors before they propagate to the PCB.
- Footprint pad/hole clearances were computed in Python *before* drawing
  them, with hard distance-vs-radius assertions.
- Freerouting + `kicad-cli pcb drc` runs in 5 seconds and gives a
  binary clean/dirty answer for the entire layout.

The enclosure design loop has none of those gates. Adding them — even
just simple Python scripts that load the SCAD's known dimensions and
assert clearances against component datasheet values — would prevent the
"oh it doesn't fit" class of failures entirely.

A first version of this could be a `tools/check-clearances.py` that:

1. Reads a YAML manifest of components with measured/datasheet dimensions.
2. Reads a YAML manifest of SCAD parameters and which component they're
   constrained by.
3. Asserts the SCAD parameter is at least `component_dim + tolerance`.

Run it as a pre-commit hook. The print is now a confirmation, not an
exploration.

---

## What stays the same

The current loop's strengths are real and shouldn't be lost in
optimization:

- **F5 preview is fast enough** that geometry exploration in OpenSCAD
  (e.g. "what shape should the connecting block be?") is the right
  process. Don't try to formalize the early shape-exploration phase.
- **Real prints are the truth for non-linear properties** — surface
  finish, layer adhesion, snap-fit retention force, support visibility.
  These can't be predicted from CAD; the print is the only way.
- **Photographing prints with annotation overlays** has been valuable for
  retrospective communication (the blog posts and design-evolution doc
  are the project's collective memory). Keep doing it.

The point is not to stop printing, but to stop printing the same kind of
mistake twice.

---

## Process gates (proposed checklist)

Before committing a SCAD edit that triggers a new print, the SCAD should
satisfy:

- [ ] All parametric dimensions trace back to a measurement comment block
- [ ] At least one `section_*` part is defined for any new mating feature
- [ ] If a tolerance is being changed, the calibration coupon for that
      tolerance has been printed on the current printer/filament
- [ ] If two dimensional choices are uncertain, both are saved as
      customizer presets and rendered with `export-preset.py`

Before fabbing a PCB:

- [ ] `kicad-cli pcb drc` returns 0 copper violations, 0 unconnected,
      0 schematic-parity issues
- [ ] All footprint pad-to-hole and pad-to-pad clearances verified by
      explicit Python script (committed alongside the board)
- [ ] All pin names and net assignments traced to the manufacturer
      datasheet, with the datasheet diagram archived in the project

---

## Related documents

- [`hardware-design/scad Parts/README.md`](scad%20Parts/README.md) —
  the three Python helpers for SCAD export and presets
- [`website/docs/docs/hardware/3d-printing-pipeline.md`](../website/docs/docs/hardware/3d-printing-pipeline.md) —
  technology + service comparison for going from CAD to physical part
- [`website/docs/docs/hardware/design-evolution.md`](../website/docs/docs/hardware/design-evolution.md) —
  per-version history of every part that's been printed
- [`hardware-design/joystick-pcb/design-notes.md`](joystick-pcb/design-notes.md) —
  example of the PCB design discipline applied: dimensions, clearances,
  routing workflow all documented
