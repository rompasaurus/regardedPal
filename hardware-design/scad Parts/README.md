# SCAD Tooling — Python helper scripts

Three small Python utilities that wrap OpenSCAD's CLI for the Dilder hardware
workflow. All three discover `.scad` files automatically from this directory
and the parent `hardware-design/` tree, so you can run them from anywhere
with no arguments.

| Script | What it does | When to use |
|--------|--------------|-------------|
| [`scad-export.py`](scad-export.py) | Pick a SCAD → format → output path → render | Day-to-day "I changed something, give me a 3MF for the slicer" |
| [`bake-preset.py`](bake-preset.py) | Rewrite SCAD source so a customizer preset becomes the new default | When a preset has been validated and you want it to be the file's canonical state |
| [`export-preset.py`](export-preset.py) | Export a customizer preset directly to 3MF without touching the SCAD source | A/B comparing variants of the same SCAD without committing one as the "real" version |

All three are pure-Python, only require `openscad` on `PATH`, and have a
common interactive menu style (numbered list → typed choice) plus
non-interactive flag-driven invocation for scripting.

---

## scad-export.py — interactive 3MF/STL exporter

The general-purpose driver. Most days this is the only one you need.

```bash
python3 hardware-design/scad\ Parts/scad-export.py
```

What it does, in order:

1. **Browse** — recursively finds every `.scad` in the project, sorted by mod
   time (most recent first), with a `[4] View today's models` shortcut so
   you can jump straight to whatever you've been editing.
2. **Format** — 3MF (default, recommended), STL, OFF, or AMF.
3. **Output path** — defaults to `hardware-design/enclosure-prints/<stem>.3mf`,
   override with any custom path.
4. **Part selector** — if the SCAD has a `part="..."` toggle (with comment
   listing valid values), prompts which part to render or "all".
5. **Invoke OpenSCAD** with the chosen settings.

One-shot non-interactive form:

```bash
python3 scad-export.py --file middle-plate.scad --output middle.3mf
```

### When NOT to use this

- If you have a customizer preset that captures the variant you want, use
  [`export-preset.py`](export-preset.py) — it's faster and skips the file
  browser.

---

## bake-preset.py — make a preset the new SCAD default

OpenSCAD's customizer stores presets in a sidecar `<scadname>.json`. The
GUI applies them at render time but **never modifies the source**, so a
SCAD file checked into git can drift from the preset that's actually being
used to print parts. `bake-preset.py` rewrites the source so the preset's
parameter values become the file's defaults.

```bash
# List presets in the JSON sidecar
python3 bake-preset.py base-plate-v1.scad

# Bake a preset (writes a .bak alongside the SCAD before changes)
python3 bake-preset.py base-plate-v1.scad shorten_batt_rail

# Preview the diff without writing anything
python3 bake-preset.py base-plate-v1.scad shorten_batt_rail --dry-run
```

What it changes: for every parameter in the preset, finds a line of the
form `name = <old>;` (with optional trailing `// comment`) and replaces
`<old>` with the preset's value. Comments and unrelated lines are kept
verbatim. A `.bak` file is always written first, so you can undo with
`mv name.scad.bak name.scad`.

### Limitations

- One parameter per line. Compound declarations on the same line aren't
  matched.
- Vectors and strings work; multi-line values do not.
- If a parameter is in the JSON but not in the SCAD source, it's skipped
  with a warning.

### When to use this

- The preset has been validated by an actual print and you want it to be
  the file's canonical state in git.
- You're about to fork a SCAD into a new variant and want the parent's
  current preset baked in before diverging.

### When NOT to use this

- The preset is exploratory / one-off — leave it as a JSON-only preset and
  use `export-preset.py` to render it.

---

## export-preset.py — render a preset without baking

Same SCAD/preset discovery as `bake-preset.py` (only lists SCADs that have
a sidecar JSON with `parameterSets`), but instead of rewriting the source
it just invokes OpenSCAD with `-p <json> -P <preset>` and writes
`<scadname>__<preset>.3mf` next to the SCAD.

```bash
# Interactive: pick SCAD → pick preset → write 3MF
python3 export-preset.py

# One-shot
python3 export-preset.py base-plate-v1.scad shorten_batt_rail

# Custom output path
python3 export-preset.py base-plate-v1.scad shorten_batt_rail -o /tmp/test.3mf

# Just list what's available
python3 export-preset.py --list
```

### When to use this

- A/B testing two presets of the same SCAD (you'll get
  `base-plate-v1__variant_a.3mf` and `base-plate-v1__variant_b.3mf` next
  to each other).
- You want to print a tweaked variant without committing it as the new
  default — the source file is untouched.

---

## Common gotchas

- **`openscad` not on PATH** — install it. CachyOS/Arch:
  `sudo pacman -S openscad`. Ubuntu/Debian: `sudo apt install openscad`.
  All three scripts call `shutil.which("openscad")` and bail with a
  helpful message if it's missing.
- **No JSON sidecar** — `bake-preset.py` and `export-preset.py` need
  `<scadname>.json` next to the SCAD. Save a preset in OpenSCAD's
  customizer panel (the "save preset" button) to create it.
- **Long SCAD render times** — `openscad -o file.3mf` does a full CGAL
  render. If a part takes a few minutes, that's the SCAD geometry, not
  the script. F5 in the OpenSCAD GUI is the fast preview equivalent.
- **`scad-export.py` and the part selector** — the script looks for a
  comment line of the form `// part="base" | "middle" | "all"` to detect
  multi-part files. If your SCAD uses `part = "base"` directly, add a
  comment listing the valid options so the script can find them.

---

## Adding new helper scripts

Convention for new helpers in this folder:

- Single-file Python 3, no dependencies outside the stdlib.
- Discover SCADs via `Path(__file__).resolve().parent.parent.rglob("*.scad")`.
- Both interactive (no args) and CLI (positional + flags) modes.
- Add a row to the table at the top of this README.
