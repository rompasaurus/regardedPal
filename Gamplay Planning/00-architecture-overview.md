# Dilder Gameplay Architecture Overview

> System architecture, module dependencies, and data flow for the Dilder gameplay firmware.

---

## Table of Contents

1. [System Block Diagram](#1-system-block-diagram)
2. [Module Dependency Graph](#2-module-dependency-graph)
3. [Data Flow](#3-data-flow)
4. [Module Summary](#4-module-summary)
5. [Memory Map](#5-memory-map)
6. [File Organization](#6-file-organization)

---

## 1. System Block Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MAIN GAME LOOP                               │
│                     (game_loop.c / game_loop.h)                     │
│                                                                     │
│   tick_update() called every 1s (configurable)                      │
│   Orchestrates all subsystems per frame                             │
└────┬──────────┬──────────┬──────────┬──────────┬──────────┬────────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│ SENSOR  ││  STAT   ││ EMOTION ││  INPUT  ││ACTIVITY ││PERSIST- │
│ MANAGER ││ SYSTEM  ││ ENGINE  ││ & MENU  ││ TRACKER ││  ENCE   │
│         ││         ││         ││  & UI   ││         ││         │
│sensor.h ││ stat.h  ││emotion.h││  ui.h   ││activity.││persist. │
│         ││         ││         ││         ││    h    ││    h    │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │          │          │          │          │
     ▼          ▼          ▼          ▼          ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│DIALOGUE ││  LIFE   ││PROGRESS-││ DECOR & ││TREASURE ││  TIME   │
│ SYSTEM  ││ STAGES  ││  ION    ││COSMETIC ││  HUNT   ││ MANAGER │
│         ││         ││         ││         ││         ││         │
│dialog.h ││ life.h  ││progress.││ decor.h ││treasure.││ time.h  │
│         ││         ││    h    ││         ││    h    ││         │
└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
     │          │          │          │          │          │
     └──────────┴──────────┴──────────┴──────────┴──────────┘
                               │
                    ┌──────────┴──────────┐
                    │   HARDWARE LAYER    │
                    │                     │
                    │  Display (EPD/SPI)  │
                    │  Buttons (GPIO)     │
                    │  Sensors (I2C/ADC)  │
                    │  Flash (LittleFS)   │
                    │  RTC (hardware)     │
                    │  WiFi (CYW43)       │
                    └─────────────────────┘
```

---

## 2. Module Dependency Graph

Arrows indicate "depends on" / "calls into":

```
game_loop ──► sensor_manager ──► [I2C drivers, ADC]
    │
    ├──► stat_system
    │        │
    │        └──► time_manager (for decay rate by time-of-day)
    │
    ├──► emotion_engine
    │        │
    │        ├──► stat_system    (reads current stats)
    │        ├──► sensor_manager (reads sensor context)
    │        └──► life_stages    (emotion set varies by stage)
    │
    ├──► input_menu_ui
    │        │
    │        ├──► stat_system    (care actions modify stats)
    │        ├──► emotion_engine (display current emotion)
    │        ├──► dialogue       (show contextual text)
    │        ├──► decor          (render equipped cosmetics)
    │        ├──► progression    (display XP, achievements)
    │        └──► [EPD display driver]
    │
    ├──► activity_tracker
    │        │
    │        ├──► sensor_manager (accelerometer, GPS)
    │        ├──► stat_system    (step bonuses affect stats)
    │        └──► progression    (step milestones grant XP)
    │
    ├──► life_stages
    │        │
    │        ├──► stat_system    (accumulated stats drive evolution)
    │        ├──► time_manager   (age triggers stage transitions)
    │        └──► progression    (evolution grants unlocks)
    │
    ├──► dialogue
    │        │
    │        ├──► emotion_engine (mood-matched quotes)
    │        ├──► life_stages    (stage-appropriate vocabulary)
    │        ├──► stat_system    (intelligence gates complexity)
    │        └──► activity_tracker (context: steps, location)
    │
    ├──► progression
    │        │
    │        ├──► stat_system    (XP sources from care)
    │        └──► decor          (unlocks cosmetics)
    │
    ├──► treasure_hunt
    │        │
    │        ├──► sensor_manager (GPS, magnetometer)
    │        ├──► activity_tracker (step milestones trigger spawns)
    │        ├──► progression    (rewards grant XP/items)
    │        └──► input_menu_ui  (compass display, collection)
    │
    └──► persistence
             │
             ├──► stat_system    (save/load stats)
             ├──► progression    (save/load XP, achievements)
             ├──► life_stages    (save/load stage, evolution data)
             ├──► activity_tracker (save/load step history)
             ├──► decor          (save/load equipped items)
             └──► [LittleFS / flash driver]
```

---

## 3. Data Flow

### Per-Tick Data Flow (1-second cycle)

```
  ┌─── SENSORS ──────────────────────────────────────────────────┐
  │                                                               │
  │  light ─────────────┐                                         │
  │  mic_level ─────────┤                                         │
  │  temperature ───────┼──► sensor_context_t ──┐                 │
  │  humidity ──────────┤                       │                 │
  │  accel_xyz ─────────┤                       │                 │
  │  gps_fix ───────────┘                       │                 │
  │                                             ▼                 │
  │  ┌────────────────────────────────────────────────────┐       │
  │  │              STAT DECAY                             │       │
  │  │                                                     │       │
  │  │  for each primary stat:                             │       │
  │  │    stat -= base_decay * stage_modifier              │       │
  │  │                     * bond_modifier                 │       │
  │  │                     * environment_modifier           │       │
  │  │                     * time_of_day_modifier           │       │
  │  │                                                     │       │
  │  │  output: stats_t (hunger, happiness, energy, ...)   │       │
  │  └───────────────────────┬─────────────────────────────┘       │
  │                          │                                     │
  │                          ▼                                     │
  │  ┌────────────────────────────────────────────────────┐       │
  │  │           EMOTION RESOLUTION                        │       │
  │  │                                                     │       │
  │  │  inputs: stats_t + sensor_context_t                 │       │
  │  │        + recent_events[] + personality_traits        │       │
  │  │                                                     │       │
  │  │  for each emotion:                                  │       │
  │  │    weight = evaluate_trigger(emotion, inputs)        │       │
  │  │                                                     │       │
  │  │  blend + hysteresis + minimum dwell                 │       │
  │  │  output: emotion_state_t (current, weight, prev)    │       │
  │  └───────────────────────┬─────────────────────────────┘       │
  │                          │                                     │
  │                          ▼                                     │
  │  ┌────────────────────────────────────────────────────┐       │
  │  │             DISPLAY UPDATE                          │       │
  │  │                                                     │       │
  │  │  if emotion changed OR dialogue triggered:          │       │
  │  │    render_octopus(emotion_state, decor, life_stage) │       │
  │  │    render_header(time, stat_icons)                   │       │
  │  │    render_dialogue(quote)                            │       │
  │  │    epd_partial_refresh()                             │       │
  │  └─────────────────────────────────────────────────────┘       │
  └────────────────────────────────────────────────────────────────┘
```

### User Interaction Data Flow

```
  BUTTON PRESS ──► input_handler ──► action_resolver
                                          │
                       ┌──────────────────┼──────────────────┐
                       ▼                  ▼                  ▼
                  CARE ACTION        MENU NAVIGATE      CONTEXT ACTION
                  (feed, clean,      (scroll, select,   (collect treasure,
                   medicine)          back)              scold)
                       │                  │                  │
                       ▼                  ▼                  ▼
                  stat_modify()     ui_transition()    game_event_fire()
                       │                  │                  │
                       ▼                  ▼                  ▼
                  +hunger/hygiene   render new screen   progression_xp_add()
                  +bond_xp                              emotion_trigger()
                  event_log()                           dialogue_show()
```

---

## 4. Module Summary

| Module | Header | Responsibility | State Owned |
|--------|--------|---------------|-------------|
| **Game Loop** | `game_loop.h` | Tick orchestration, sleep/wake, frame timing | `game_state_t` (running, paused, sleeping) |
| **Stat System** | `stat.h` | All stat values, decay, modification, thresholds | `stats_t`, `stat_modifiers_t` |
| **Emotion Engine** | `emotion.h` | Resolve current emotion from inputs, blend transitions | `emotion_state_t`, `emotion_weights[16]` |
| **Sensor Manager** | `sensor.h` | Poll hardware, debounce, classify events | `sensor_context_t`, `sensor_event_t` |
| **Input & Menu & UI** | `ui.h` | Button handling, menu FSM, screen composition | `menu_state_t`, `ui_screen_t` |
| **Life Stages** | `life.h` | Stage transitions, evolution branching, age tracking | `life_stage_t`, `evolution_data_t` |
| **Progression** | `progress.h` | XP, bond level, achievements, unlock gates | `progression_t`, `achievement_t[]` |
| **Dialogue** | `dialog.h` | Quote selection, context triggers, recency filter | `dialogue_state_t`, `quote_history[]` |
| **Decor & Cosmetics** | `decor.h` | Equipped items, inventory, slot management | `decor_loadout_t`, `inventory_t` |
| **Activity Tracker** | `activity.h` | Steps, distance, location, daily/weekly/monthly | `activity_t`, `location_db_t` |
| **Treasure Hunt** | `treasure.h` | Spawn, compass, proximity, collection | `treasure_t`, `hunt_state_t` |
| **Persistence** | `persist.h` | Flash read/write, save scheduling, data integrity | `save_data_t` (aggregate of all) |
| **Time Manager** | `time.h` | RTC wrapper, day/night detection, age calculation | `game_time_t` |

---

## 5. Memory Map

### RAM Budget (RP2040: 264KB total, ~200KB usable after stack/heap)

```
CATEGORY                    ESTIMATED SIZE    NOTES
─────────────────────────────────────────────────────
Display buffer              3,904 bytes       250x122 @ 1bpp
Stats + modifiers             128 bytes       Primary + secondary + hidden
Emotion state                  64 bytes       Weights array + blend state
Sensor context                 96 bytes       All sensor readings + events
Menu / UI state               256 bytes       Menu stack, screen state
Life stage data                64 bytes       Stage, evolution accumulators
Progression data              512 bytes       XP, bond, 64 achievement flags
Dialogue state                128 bytes       History ring buffer (10 entries)
Decor loadout                  32 bytes       4 slots + 8 inventory items
Activity data                 256 bytes       Step counters, location cache
Treasure hunt                  64 bytes       1 active hunt + compass state
Event ring buffer             256 bytes       Last 16 events for context
Quote string buffer           128 bytes       Current displayed quote
Location DB (WiFi FPs)      2,048 bytes       32 known locations x 64B
─────────────────────────────────────────────────────
TOTAL GAMEPLAY STATE       ~7,936 bytes       ~3% of usable RAM

Remaining for:
  Stack                    ~8,000 bytes
  Heap                    ~16,000 bytes
  Pico SDK + drivers     ~168,000 bytes
```

### Flash Budget (Pico W: 2MB, ESP32-S3: 16MB)

```
CATEGORY                    ESTIMATED SIZE    NOTES
─────────────────────────────────────────────────────
Firmware binary             ~200 KB           Code + embedded data
Quote strings                ~40 KB           800+ quotes, compressed
Font data                    ~20 KB           5 bitmap fonts
Save data (LittleFS)         ~16 KB           All persistent game state
Location database             ~8 KB           128 known WiFi fingerprints
Achievement definitions       ~4 KB           Unlock conditions table
Decor definitions             ~2 KB           Item catalog
─────────────────────────────────────────────────────
TOTAL                       ~290 KB           14% of 2MB Pico W flash
```

---

## 6. File Organization

```
dev-setup/dilder-game/
├── CMakeLists.txt
├── main.c                          # Entry point, init, main loop dispatch
│
├── game/
│   ├── game_loop.h                 # Game loop interface
│   ├── game_loop.c                 # Tick orchestration, sleep/wake
│   ├── game_state.h                # Top-level game state enum + struct
│   │
│   ├── stat.h                      # Stat types, decay API
│   ├── stat.c                      # Stat decay, modification, thresholds
│   │
│   ├── emotion.h                   # Emotion types, resolution API
│   ├── emotion.c                   # Trigger evaluation, blending
│   │
│   ├── life.h                      # Life stage types, evolution API
│   ├── life.c                      # Stage transitions, evolution calc
│   │
│   ├── dialog.h                    # Dialogue selection API
│   ├── dialog.c                    # Context matching, recency filter
│   ├── quotes.h                    # Auto-generated quote arrays (per mood/stage)
│   │
│   ├── progress.h                  # XP, bond, achievement API
│   ├── progress.c                  # Leveling, unlock checks
│   ├── achievements.h              # Achievement definition table
│   │
│   ├── decor.h                     # Decor slot + inventory API
│   ├── decor.c                     # Equip/unequip, unlock gating
│   ├── decor_catalog.h             # Item definitions
│   │
│   ├── activity.h                  # Step tracking, location API
│   ├── activity.c                  # Step milestones, WiFi geolocation
│   │
│   ├── treasure.h                  # Treasure hunt API
│   ├── treasure.c                  # Spawn, compass, proximity, collection
│   │
│   ├── persist.h                   # Save/load API
│   ├── persist.c                   # LittleFS operations, data packing
│   │
│   └── time_mgr.h / time_mgr.c    # RTC wrapper, day/night, age
│
├── sensor/
│   ├── sensor.h                    # Unified sensor context API
│   ├── sensor.c                    # Poll orchestration, event classification
│   ├── drv_light.h / drv_light.c   # BH1750 driver
│   ├── drv_mic.h / drv_mic.c       # MAX9814 ADC processing
│   ├── drv_env.h / drv_env.c       # AHT20 driver
│   ├── drv_accel.h / drv_accel.c   # LIS2DH12TR driver + pedometer
│   ├── drv_gps.h / drv_gps.c       # PA1010D NMEA parser
│   └── drv_mag.h / drv_mag.c       # QMC5883L magnetometer
│
├── ui/
│   ├── ui.h                        # UI state machine API
│   ├── ui.c                        # Screen composition, transitions
│   ├── ui_menu.h / ui_menu.c       # Menu tree navigation
│   ├── ui_render.h / ui_render.c   # Octopus renderer (existing engine)
│   ├── ui_hud.h / ui_hud.c         # Header bar, stat icons
│   ├── ui_screens.h / ui_screens.c # Special screens (stats, compass, gift box)
│   └── input.h / input.c           # Button debounce, press classification
│
├── lib/                            # Existing Pico SDK display/GPIO drivers
│   ├── Config/
│   ├── e-Paper/
│   ├── GUI/
│   └── Fonts/
│
└── data/
    ├── quote_data.c                # Compiled quote strings
    ├── achievement_data.c          # Achievement definitions
    └── decor_data.c                # Item catalog data
```

---

## Cross-Cutting Concerns

### Event System

All modules communicate side-effects through a lightweight event bus:

```c
// Any module can fire an event
event_fire(EVENT_STAT_CRITICAL, &(event_data_t){ .stat_id = STAT_HUNGER });

// Any module can register a listener
event_listen(EVENT_STAT_CRITICAL, on_stat_critical_handler);
```

This decouples modules — the stat system doesn't need to know about dialogue or emotion directly. It just fires events. See [01-core-game-loop.md](01-core-game-loop.md) for event types and dispatch.

### Error Handling

Hardware failures (sensor I2C timeout, flash write failure) are handled at the driver level with graceful degradation — the game loop continues with stale/default data. No gameplay system should crash the device.

### Build Configuration

Feature flags control which modules compile in, enabling phased rollout:

```cmake
option(DILDER_SENSORS    "Enable sensor integration (Phase 3B)"  OFF)
option(DILDER_ACTIVITY   "Enable step/location tracking (Phase 3C)" OFF)
option(DILDER_TREASURE   "Enable treasure hunts (Phase 4B)"     OFF)
option(DILDER_GPS        "Enable GPS module (Phase 4B)"         OFF)
```

---

*Next: [01-core-game-loop.md](01-core-game-loop.md) — The tick system, timing, and main loop pseudocode.*