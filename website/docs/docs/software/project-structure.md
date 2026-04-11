# Project Structure

Directory layout and module overview for the Dilder project.

---

## Repository Layout

```
dilder/
├── README.md                    # Project overview and phase tracker
├── PromptProgression.md         # Every AI prompt logged with token counts
├── setup.py                     # Interactive CLI for first-time dev environment setup
│
├── DevTool/                     # Tkinter GUI for Pico W development
│   ├── devtool.py               # Main application (9 classes, 7 tabs)
│   ├── requirements.txt         # Python dependencies (pyserial, Pillow)
│   └── README.md                # Comprehensive usage walkthrough
│
├── dev-setup/                   # Hardware setup resources
│   ├── pico-and-display-first-time-setup.md  # Step-by-step hardware guide
│   ├── hello-world/             # C project — e-ink display Hello World
│   │   ├── main.c
│   │   ├── CMakeLists.txt
│   │   └── lib/                 # Waveshare driver files (cloned at setup)
│   ├── hello-world-serial/      # C project — serial-only Hello World
│   │   ├── main.c
│   │   └── CMakeLists.txt
│   ├── Dockerfile               # Reproducible ARM cross-compile container
│   └── docker-compose.yml
│
├── hardware-design/             # Enclosure and component planning
│   └── hardware-planning.md     # Dimensions, button options, CAD plan, print costs
│
├── docs/                        # Raw research and reference docs
│   ├── hardware-research.md     # Component specs and GPIO budget
│   ├── setup-guide.md           # Original setup walkthrough
│   └── concepts/
│       ├── prototype-v1.svg     # Enclosure concept render v1
│       └── prototype-v2.svg     # Dimension-accurate concept render v2
│
├── assets/                      # Saved display images from DevTool
│   ├── *.pbm                    # Portable Bitmap format
│   ├── *.bin                    # Raw display buffer
│   └── *.png                    # PNG exports
│
├── website/                     # This website (MkDocs Material project)
│   ├── mkdocs.yml               # Site configuration
│   ├── dev.py                   # Website dev CLI (serve, build, deploy)
│   ├── requirements.txt         # MkDocs dependencies
│   ├── PLAN.md                  # Site architecture plan
│   ├── IMPLEMENTATION.md        # Build process documentation
│   ├── CONTENT-GUIDE.md         # Content management guide
│   ├── DEPLOY.md                # GitHub Pages deployment guide
│   └── docs/                    # Site content (Markdown)
│
└── firmware/                    # C firmware for Pico W (Phase 2+)
    ├── main.c                   # Entry point
    ├── core/                    # Display, input, game loop
    ├── pet/                     # Pet state machine, mood, animations
    └── assets/                  # Sprites and fonts
```

!!! note "Firmware not yet written"
    The `firmware/` directory structure above is the planned layout. Phase 2 will establish this scaffold.

!!! warning "Flash storage limits"
    The Pico W has 2MB of flash. C firmware is much smaller than MicroPython, but keep sprite files small — use 1-bit monochrome bitmaps, not PNGs with metadata.

---

## Planned Firmware Modules (C)

The firmware is written in C using the Pico SDK. The planned module structure:

### `core/display.c`

Thin wrapper around the Waveshare e-Paper driver:

- Initializes SPI and the display via the Pico SDK
- Exposes `display_render()` for full refresh and `display_render_partial()` for partial
- Handles cleanup and sleep mode
- Manages refresh rate limiting (prevent over-refreshing)

### `core/input.c`

Button input manager:

- Sets up GPIO pins with internal pull-ups via `gpio_set_pulls()`
- Provides polling: `input_is_pressed(button)`
- Handles software debouncing (~10ms default)
- Button constants: `BTN_UP` (GP2), `BTN_DOWN` (GP3), `BTN_LEFT` (GP4), `BTN_RIGHT` (GP5), `BTN_SELECT` (GP6)

### `core/loop.c`

Main game loop:

- 10Hz target tick rate (100ms per tick)
- Calls `pet_tick()` on each loop iteration
- Reads pending input events and dispatches to pet state machine
- Triggers display refresh when pet state changes

### `pet/pet.c`

Pet state machine:

- States: `IDLE`, `EATING`, `PLAYING`, `SLEEPING`, `SICK`
- Tracks stats: hunger, happiness, energy, age
- Stat decay over time (hunger increases, happiness decreases)
- State transitions driven by input and stat thresholds

### `pet/animations.c`

Sprite animation sequences:

- Each animation is an array of `{sprite_data, duration_ms}` structs
- Animator tracks current frame, advances on tick
- Renders to a framebuffer passed to `display_render_partial()`

---

## Asset Format

### Sprites

- Format: 1-bit monochrome (raw byte arrays or PBM)
- Coordinate space: 250×122 (full display) or any sub-region
- Naming: `{state}_{frame:02d}.pbm` — e.g., `idle_00.pbm`, `idle_01.pbm`
- The [DevTool](../tools/devtool.md) display emulator can create and preview sprites at exact display resolution

!!! tip "Why not PNG?"
    The Pico W firmware works with raw byte arrays for display rendering. Pre-convert sprites to 1-bit raw format on your dev machine using the DevTool or command-line tools before embedding in firmware.

### Fonts

- For small text, use bitmap font arrays compiled into the firmware
- For larger text, use a custom font renderer
- Recommended size: 8px–16px works well at 250×122 resolution

---

## Key Differences from Pi Zero Development

| Aspect | Pico W (C SDK) | Pi Zero (CPython + Linux) |
|--------|---------------|--------------------------|
| Language | C with Pico SDK | Python with PIL/Pillow |
| Graphics | Raw framebuffer | `PIL.Image` + `ImageDraw` |
| GPIO | `gpio_init()` / `gpio_get()` | `RPi.GPIO` |
| SPI | Pico SDK `spi_init()` | `spidev` |
| File I/O | 2MB flash, no filesystem | Full Linux filesystem |
| Build | CMake + Ninja cross-compile | `pip install` packages |
| Debugging | Serial over USB + SWD | SSH + debugpy |
| Boot | Instant (~1s) | 30–90 seconds |
