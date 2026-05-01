# Dilder Tools

All project tools live in their own directories here.

| Tool | Directory | Description |
|------|-----------|-------------|
| [DevTool](../DevTool/) | `DevTool/` | Tkinter GUI for firmware development — display emulator, serial monitor, flash utility |
| [Build & Render](build-render/) | `tools/build-render/` | Interactive CLI for rendering FreeCAD models into PNGs |
| [Design Tracker](design-tracker/) | `tools/design-tracker/` | CAD version history, print log, and snapshot diffing |
| [DesignTool](designtool/) | `tools/designtool/` | Tkinter GUI for OpenSCAD file management and export |

## Quick Start

```bash
# Render FreeCAD models
./tools/build-render/build_and_render.sh

# Track design changes
python3 tools/design-tracker/design-tracker.py

# Manage OpenSCAD files
python3 tools/designtool/designtool.py

# Firmware development
python3 DevTool/devtool.py
```
