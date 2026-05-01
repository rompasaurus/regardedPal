# DesignTool — SCAD Design Management

Tkinter GUI for managing OpenSCAD hardware design files: browsing, preset diffing, exporting to STL/3MF, 3D preview, and tracking export history.

## Usage

```bash
python3 tools/designtool/designtool.py
```

## Tabs

1. **Browser** — search and browse `.scad` files with parameter details
2. **Presets & Diff** — compare presets side-by-side with color-coded diffs
3. **Export** — STL/3MF export with embedded labels and auto-generated descriptions
4. **3D Preview** — live OpenSCAD rendering with orthographic quick-views
5. **History** — full audit trail of every export

## Requirements

- Python 3.9+ with Tkinter
- OpenSCAD (for preview and export)

## Data

- `exports/` — exported STL/3MF files with descriptions
- `history.json` — export audit trail
