# Build & Render Tool

Interactive CLI pipeline for rendering Dilder FreeCAD models into publication-quality PNGs.

## Quick Start

```bash
cd hardware-design
./build_and_render.sh
```

## What It Does

1. **Pick a model** — interactive menu lists all `.FCStd` files sorted by date (newest first)
2. **Choose what to render** — 19 options from full sets to individual components
3. **Set render style** — resolution, background, cover transparency
4. **Renders** — launches FreeCAD GUI, generates PNGs from the live 3D viewport
5. **Copies to website** — drops renders into `website/docs/assets/images/enclosure/`

## Menu Options

### Full Sets
| Option | Description | Images |
|--------|-------------|--------|
| 1 | Everything | 40+ |
| 2 | Assembly only | 10 |
| 3 | Exploded views | 3 |
| 4 | Component portraits | 14 |

### Individual Bodies
| Option | Description |
|--------|-------------|
| 5 | Base plate (iso + top + bottom + sensors) |
| 6 | AAA cradle (iso + top + bottom) |
| 7 | Top cover (transparent + opaque + bottom) |
| 8 | Thumbpiece |

### Peripherals
| Option | Description |
|--------|-------------|
| 9 | Joystick PCB (K1-1506SN-01 breakout) |
| 10 | Pico 2 W + headers |
| 11 | Piezo speaker (20 mm FT-20T) |
| 12 | IMU accelerometer (GY-6500) |
| 13 | TP4056 charger |
| 14 | Batteries + clips |
| 15 | E-ink display |
| 16 | Solar panel |

### Special
| Option | Description |
|--------|-------------|
| 17 | Detail close-ups (joystick, thumbpiece, sensors) |
| 18 | Animation frames (13-step assembly drop) |
| 19 | Custom combo (pick exactly which components) |

## Render Styles

- **Resolution:** 1920x1440 (default), 2560x1920, 1280x960, 960x720
- **Background:** Transparent (default), White, Black, Light gray
- **Cover transparency:** 40% (default), 0% (opaque), 70%, 85% (ghost)

## Animation

Option 18 generates frame-by-frame PNGs of components dropping into place with cosine ease-in-out. If `ffmpeg` is installed, assembles them into a GIF automatically.

```bash
# Manual GIF assembly if needed
ffmpeg -framerate 12 -i renders/anim/frame-%04d.png \
       -vf "scale=960:720" -loop 0 renders/assembly-animation.gif
```

## Flags

```bash
./build_and_render.sh --rebuild    # rebuild FCStd from macro before rendering
./build_and_render.sh --all        # (with animation) not needed — pick option 18 in menu
```

## Output

- `renders/var-*.png` — assembly views (hero, angles, exploded, etc.)
- `renders/comp-*.png` — isolated component portraits
- `renders/anim/frame-*.png` — animation frames
- Automatically copied to `website/docs/assets/images/enclosure/`

## Requirements

- FreeCAD (GUI version, not `freecadcmd` — needs the 3D viewport for `saveImage`)
- `ffmpeg` (optional, for GIF assembly)
- `identify` from ImageMagick (optional, for blank image detection)
