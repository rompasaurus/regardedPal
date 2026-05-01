# Project Structure

Directory layout and module overview for the Dilder project.

---

## Repository Layout

```
dilder/
├── README.md                        # Project overview and phase tracker
├── PromptProgression.md             # Every AI prompt logged with token counts
├── setup.py                         # Interactive CLI for first-time dev environment setup
│
├── tools/                           # Design and build automation
│   ├── designtool/                  # Tkinter GUI for SCAD design management
│   │   ├── designtool.py            # 5-tab app: browser, presets, export, 3D preview, history
│   │   ├── exports/                 # Timestamped export snapshots (SCAD + 3MF + description.md)
│   │   └── history.json             # Export tracking log
│   │
│   ├── design-tracker/              # Tkinter GUI for CAD version history and print logs
│   │   ├── design-tracker.py        # 6-tab app: dashboard, models, prints, renders, packages, guide
│   │   ├── screenshots/             # GUI screenshots for documentation
│   │   └── .design-tracker/         # Persistent data
│   │       ├── history.json         # Snapshots, prints, packages
│   │       ├── snapshots/           # Numbered FCStd backups (snap-0001/, snap-0002/, ...)
│   │       └── packages/            # Bundled release folders (FCStd + 3MF + renders + photos + CHANGES.md)
│   │
│   └── build-render/                # Interactive render pipeline for FreeCAD models
│       ├── build_and_render.sh      # 19 render presets, 4 resolutions, custom combos, animation
│       └── README.md
│
├── DevTool/                         # Tkinter GUI for Pico W development
│   ├── devtool.py                   # Main application (9 classes, 7 tabs)
│   ├── requirements.txt             # Python dependencies (pyserial, Pillow)
│   └── README.md
│
├── firmware/                        # C game engine (compiles to .so + CLI)
│   ├── CMakeLists.txt               # Build system (shared lib + standalone CLI)
│   ├── FIRMWARE.md                  # Architecture guide, reading order, debugging
│   ├── include/                     # Headers
│   │   ├── dilder.h                 # Public API (called from Python via ctypes)
│   │   ├── game/                    # game_state.h, event.h, stat.h, emotion.h, life.h,
│   │   │                            #   dialog.h, progress.h, time_mgr.h, game_loop.h
│   │   ├── sensor/                  # sensor.h (emulation layer)
│   │   └── ui/                      # input.h, render.h, ui.h
│   └── src/                         # Implementation
│       ├── game/                    # stat.c, emotion.c, life.c, dialog.c, event.c,
│       │                            #   game_loop.c, progress.c, time_mgr.c
│       ├── sensor/                  # sensor.c (emulated sensor values)
│       ├── ui/                      # render.c (bitmap font, octopus), ui.c (menus), input.c
│       └── platform/
│           ├── desktop/             # dilder_api.c (Python bridge), main_desktop.c (CLI)
│           └── esp32s3/             # esp32s3_hal.cpp (ESP32-S3 hardware abstraction)
│
├── hardware-design/                 # Enclosure, CAD, PCB, and component planning
│   ├── freecad-mk2/                 # Current production FreeCAD model
│   │   ├── dilder_rev2_mk2.FCMacro  # Parametric macro (3 Bodies, 180+ spreadsheet params)
│   │   ├── Dilder_Rev2_Mk2.FCStd   # Master assembly (BasePlate, AAACradle, TopCover)
│   │   ├── render_views.FCMacro     # Batch render macro (27+ camera presets)
│   │   ├── animate_assembly.FCMacro # 13-step assembly animation
│   │   ├── BUILD-INSTRUCTIONS.txt   # FreeCAD rebuild instructions
│   │   └── *.3mf                    # Slicer-ready exports (47+ files)
│   │
│   ├── freecad/                     # Earlier FreeCAD iterations (Rev 2 PartDesign)
│   ├── scad Parts/                  # OpenSCAD parametric source files
│   │   ├── Rev 2 extended with joystick/  # Current Rev 2 design iterations
│   │   │   ├── 04-24-designs-alterations/
│   │   │   ├── 04-25-design-alterations/
│   │   │   └── 04-26-design-alterations/  # Latest: cradle, base plate, top cover SCAD
│   │   └── historical-archive/      # Earlier Rev 1 and experimental designs
│   │
│   ├── renders/                     # Publication-quality PNG renders (76+ images)
│   │   └── anim/                    # Assembly animation frames
│   ├── joystick-pcb-by-hand/        # Hand-routed K1-1506SN-01 breakout board (KiCad + STEP)
│   ├── reference-boards/            # STEP models and design guides for reference hardware
│   │   ├── raspberry-pi-pico-2/     # Official Pico 2 STEP file
│   │   ├── esp32s3-basic-devboard/
│   │   ├── rp2040-minimal-jlcpcb/
│   │   └── ...                      # 9 reference board packages
│   ├── parts-sheets/                # Component datasheets (17 parts: TP4056, AHT20, etc.)
│   ├── enclosure-prints/            # Photos of physical 3D prints
│   ├── Working Designs/             # Completed reference STL/3MF designs
│   ├── hardware-planning.md         # Dimensions, CAD plan, print costs
│   ├── BOM.md                       # Bill of materials
│   ├── pcb-design-plan.md           # Custom PCB design strategy
│   ├── HARDWARE-DESIGN-PROCESS.md   # Retrospective on print-waste optimization
│   ├── 3d-printing-pipeline.md      # SCAD → FreeCAD → 3MF workflow
│   └── speaker-module-selection.md  # Piezo speaker research
│
├── dev-setup/                       # Hardware setup + 16 personality firmware programs
│   ├── pico-and-display-first-time-setup.md
│   ├── hello-world/                 # C project — e-ink display Hello World
│   ├── hello-world-serial/          # C project — serial-only Hello World
│   ├── img-receiver/                # C project — receive images over serial
│   ├── joystick-mood-selector/      # Interactive joystick-driven mood picker
│   ├── mood-selector/               # Interactive: all 16 moods, serial input
│   ├── sassy-octopus/               # Sassy personality (196 quotes)
│   ├── supportive-octopus/          # Supportive personality (160 quotes)
│   ├── angry-octopus/               # Angry personality (45 quotes)
│   ├── conspiratorial-octopus/      # Conspiratorial/weird personality (47 quotes)
│   ├── sad-octopus/                 # Sad personality (35 quotes)
│   ├── chaotic-octopus/             # Chaotic personality (40 quotes)
│   ├── hungry-octopus/              # Hungry personality (30 quotes)
│   ├── tired-octopus/               # Tired personality (30 quotes)
│   ├── slaphappy-octopus/           # Slap happy personality (30 quotes)
│   ├── lazy-octopus/                # Lazy personality (30 quotes, custom body)
│   ├── fat-octopus/                 # Fat personality (30 quotes, custom body)
│   ├── chill-octopus/               # Chill personality (30 quotes)
│   ├── creepy-octopus/              # Creepy personality (30 quotes)
│   ├── excited-octopus/             # Excited personality (30 quotes)
│   ├── nostalgic-octopus/           # Nostalgic personality (30 quotes)
│   ├── homesick-octopus/            # Homesick personality (30 quotes)
│   ├── Dockerfile                   # Reproducible ARM cross-compile container
│   └── docker-compose.yml           # Build services for all programs
│
├── ESP Protyping/                   # ESP32-S3 prototyping workspace
│   ├── dilder-esp32/                # PlatformIO project (ESP32-S3 DevKit-Lipo)
│   │   ├── platformio.ini
│   │   ├── src/                     # ESP32 firmware source
│   │   └── include/
│   ├── dev setup guide.md
│   └── setup wiring guide.md
│
├── Gamplay Planning/                # 14 game design documents (11,000+ lines)
│   ├── 00-architecture-overview.md
│   ├── 01-core-game-loop.md
│   ├── 02-stat-system.md
│   ├── 03-emotion-engine.md
│   ├── 04-sensor-interfaces.md
│   ├── 05-input-menu-ui.md
│   ├── 06-life-stages-evolution.md
│   ├── 07-progression-unlocks.md
│   ├── 08-dialogue-system.md
│   ├── 09-persistence-storage.md
│   ├── 10-activity-tracker.md
│   ├── 11-mcu-migration-impact.md
│   ├── 12-user-guide.md
│   └── 13-feature-menus-achievements.md
│
├── docs/                            # Raw research and reference docs
│   ├── breadboard-wiring-guide.md
│   ├── custom-pcb-design-research.md
│   ├── esp32-s3-pcb-research.md
│   ├── keyboard-to-pico-input.md
│   ├── motion-location-detection.md
│   ├── peer-discovery-research.md
│   ├── programs-guide.md
│   ├── setup-guide.md
│   ├── solar-charging-research.md
│   ├── user-engagement-plan.md
│   ├── battery-redesign-shopping-list.md
│   └── concepts/
│       ├── prototype-v1.svg
│       └── prototype-v2.svg
│
├── assets/                          # Display images and emotion previews
│   ├── c-render/                    # C-rendered emotion frame PNGs
│   ├── emotion-previews/            # Emotion state preview strips
│   ├── py-render/                   # Python-rendered comparison images
│   ├── octopus/                     # Octopus sprite assets
│   └── render_c_previews.py         # Preview generation script
│
├── testing/                         # Pytest test suites
│   ├── pytest.ini
│   ├── conftest.py
│   ├── requirements.txt
│   ├── devtool/                     # DevTool GUI tests (screenshots)
│   ├── setup_cli/                   # Setup CLI tests
│   ├── website/                     # Website build/content tests
│   ├── guides/                      # Documentation validation tests
│   └── reports/                     # Test output and coverage reports
│
└── website/                         # Documentation site (MkDocs Material)
    ├── mkdocs.yml                   # Site configuration (Material theme, blog, plugins)
    ├── dev.py                       # Website dev CLI (serve, build, deploy)
    ├── requirements.txt
    ├── PLAN.md                      # Site architecture plan
    ├── IMPLEMENTATION.md            # Build process documentation
    ├── CONTENT-GUIDE.md             # Content management guide
    ├── DEPLOY.md                    # GitHub Pages deployment guide
    └── docs/                        # Site content
        ├── index.md                 # Home page
        ├── blog/posts/              # 50+ blog posts (build journal)
        ├── docs/                    # Main documentation (6 sections, 30+ pages)
        ├── prompts/                 # Prompt Progression log mirror
        ├── community/               # Discord, support pages
        ├── about/                   # About, contact
        └── assets/                  # Images, CSS, JS
```

---

## Tools

The `tools/` directory contains three companion applications for managing the hardware design workflow:

| Tool | Type | Purpose |
|------|------|---------|
| [DesignTool](../tools/designtool.md) | Tkinter GUI | SCAD file browser, preset diffing, export to STL/3MF, 3D preview |
| [Design Tracker](../tools/design-tracker.md) | Tkinter GUI | Snapshot history, print log, render gallery, print packages |
| [Build & Render](../tools/build-render-tool.md) | Bash CLI | FreeCAD render pipeline with 19 presets, animation |

All three tools use the Catppuccin Mocha dark theme.

---

## Firmware Architecture

The firmware is written in C with platform abstraction for desktop (Python ctypes bridge) and ESP32-S3.

### Source Modules

| Directory | Files | Purpose |
|-----------|-------|---------|
| `src/game/` | 8 files | Core game logic: stats, emotions, life stages, dialog, events, progression |
| `src/ui/` | 3 files | Display rendering (bitmap font, octopus), menu system, input handling |
| `src/sensor/` | 1 file | Sensor abstraction (emulated on desktop, real on hardware) |
| `src/platform/desktop/` | 2 files | Python ctypes API bridge + standalone CLI |
| `src/platform/esp32s3/` | 1 file | ESP32-S3 hardware abstraction layer |

### Headers

| Header | Purpose |
|--------|---------|
| `dilder.h` | Public API (game_init, game_tick, game_get_state — called from Python) |
| `game/game_state.h` | Core state struct, emotion enum, stat types |
| `game/emotion.h` | 16 emotion states with transition logic |
| `game/stat.h` | Hunger, happiness, energy decay and thresholds |
| `game/life.h` | Life stages and evolution paths |
| `game/dialog.h` | Personality-driven quote system |
| `ui/render.h` | Framebuffer rendering (250x122 monochrome) |
| `ui/input.h` | Button/joystick input abstraction |

!!! success "Firmware implemented"
    Build with `cd firmware/build && cmake .. && make`. Run the Dilder tab in the DevTool or test with `./dilder_cli`. See [Firmware Game Engine](firmware-engine.md) for full documentation.

---

## Hardware Design

The `hardware-design/` directory contains all CAD, PCB, and component files for the Dilder enclosure:

| Subdirectory | Contents |
|-------------|----------|
| `freecad-mk2/` | Current production model — parametric macro, master FCStd, 3MF exports, render/animation macros |
| `freecad/` | Earlier PartDesign iterations |
| `scad Parts/` | OpenSCAD parametric source files organized by revision and date |
| `renders/` | 76+ publication-quality PNGs generated by the Build & Render tool |
| `joystick-pcb-by-hand/` | Hand-routed K1-1506SN-01 5-way switch breakout (KiCad project + STEP) |
| `reference-boards/` | 9 reference board packages (Pico 2, ESP32-S3, RP2040 variants) |
| `parts-sheets/` | 17 component datasheets (TP4056, AHT20, BH1750FVI, DW01A, etc.) |
| `enclosure-prints/` | Photos of physical 3D prints |
| `Working Designs/` | Completed reference STL/3MF files |

See [FreeCAD Mk2 Design](../hardware/freecad-mk2-design.md) for a detailed component breakdown.

---

## Asset Format

### Sprites

- Format: 1-bit monochrome (raw byte arrays or PBM)
- Coordinate space: 250x122 (full display) or any sub-region
- Naming: `{state}_{frame:02d}.pbm` — e.g., `idle_00.pbm`, `idle_01.pbm`
- The [DevTool](../tools/devtool.md) display emulator can create and preview sprites at exact display resolution

!!! tip "Why not PNG?"
    The Pico W firmware works with raw byte arrays for display rendering. Pre-convert sprites to 1-bit raw format on your dev machine using the DevTool or command-line tools before embedding in firmware.

---

## Key Differences: Desktop vs Hardware

| Aspect | Pico W (C SDK) | ESP32-S3 (Arduino) | Desktop (Python + C) |
|--------|---------------|--------------------|--------------------|
| Language | C with Pico SDK | C++ with Arduino/ESP-IDF | Python + C shared lib |
| Graphics | Raw framebuffer | Raw framebuffer | PIL/Pillow |
| GPIO | `gpio_init()` / `gpio_get()` | `digitalRead()` | Emulated |
| Build | CMake + Ninja | PlatformIO | CMake → .so + ctypes |
| Flash | 2MB (no filesystem) | 4-16MB (SPIFFS/LittleFS) | Full filesystem |
| Boot | ~1s | ~2s | Instant |
| Debugging | Serial + SWD | Serial + JTAG | Python debugger |
