---
date: 2026-04-15
authors:
  - rompasaurus
categories:
  - Software
  - Planning
slug: gameplay-architecture
---

# Designing the Gameplay Loop — From Design Doc to Program Structure

The User Engagement Plan was 1,380 lines of game design. Today it became 11 structured documents of pseudocode, data structures, and module interfaces that define exactly how the Dilder gameplay firmware will be built.

<!-- more -->

## Why Plan This Now?

The breadboard prototype displays 16 emotional states, cycles through 823 quotes, and reads joystick input. But it doesn't *play* — there's no stat decay, no care actions, no progression. Phase 3A (core game loop) is next, and implementing it without a program architecture would mean rewriting everything once the pieces don't fit together.

The User Engagement Plan describes *what* the game does. The Gameplay Planning documents describe *how the code does it* — structs, function signatures, module boundaries, and data flow.

## The Architecture

The firmware is organized as 13 modules that communicate through a lightweight event bus:

```
Game Loop (orchestrator)
  ├── Stat System         — hunger, happiness, energy, hygiene, health
  ├── Emotion Engine      — 16 emotions resolved from stats + sensors
  ├── Sensor Manager      — HAL for 7 sensors (light, touch, mic, temp, accel, GPS, mag)
  ├── Input & Menu & UI   — buttons, menu FSM, e-ink screen composition
  ├── Life Stages          — egg → hatchling → juvenile → adolescent → adult → elder
  ├── Progression          — XP, bond levels, 20+ achievements, decor unlocks
  ├── Dialogue             — context-aware quote selection with intelligence gating
  ├── Activity Tracker     — steps, daily/weekly/monthly targets, streaks
  ├── Treasure Hunts       — GPS-based spawning, compass navigation, collection
  ├── Decor & Cosmetics    — 4 equip slots, unlock inventory
  ├── Persistence          — LittleFS save/load with CRC integrity + backup
  └── Time Manager         — RTC wrapper, day/night, age tracking
```

Every module owns its own state and exposes a clean public API. No module reaches into another's internals. Side effects flow through events — when the stat system detects a critical hunger level, it fires `EVENT_STAT_CRITICAL`, and the emotion engine, dialogue system, and UI each handle it independently.

## The Core Loop

The game runs on a 1-second base tick. Not all systems need to run every tick — sensors poll at different rates to spread CPU load:

| System | Rate | Why |
|--------|------|-----|
| Button input | Every tick (1s) | Responsiveness |
| Mic level | Every tick | Volume tracking for sound events |
| Stat decay | Every tick | Fractional accumulators need consistent timing |
| Emotion resolution | Every 5s | E-ink can't refresh faster anyway |
| Touch sensor | Every 10s | Petting detection doesn't need sub-second resolution |
| Light sensor | Every 10s | Ambient light changes slowly |
| Accelerometer | Every 10s | Read hardware pedometer register |
| Temperature | Every 60s | Room temperature changes on minute timescales |
| Dialogue check | Every 30s | Idle dialogue trigger |
| Flash save | Every 5 min | Wear leveling — don't write flash every second |

Buttons are the exception: they use GPIO interrupts for instant response, with a ring buffer that the main loop drains each tick.

## Stat Decay — The Math

Stats decay fractionally. Hunger drops 1 point every 10 minutes, but the game ticks every second. A fixed-point accumulator handles this without floating-point drift:

```c
// Base decay: 1 point per 600 ticks (10 minutes)
// Accumulator threshold: 600,000 (600 * 1000 for fixed-point precision)
accum.hunger += base_rate * stage_modifier * bond_modifier * env_modifier;
if (accum.hunger >= 600000) {
    stats.hunger -= 1;
    accum.hunger -= 600000;
}
```

Modifiers stack multiplicatively — a hatchling (2x decay) in hot weather (1.3x) during active hours (1.2x) decays at 3.12x base rate. An elder (0.6x) with a strong bond (0.85x) at night (0.8x) decays at only 0.41x.

## Emotion Resolution — Weighted Priority

The emotion engine evaluates all 16 emotions every 5 seconds. Each has a trigger function that returns a weight (0.0–1.0) based on current stats, sensor readings, and recent events. The highest weight wins, with a hysteresis margin of 0.15 to prevent flickering:

```
Example tick:
  Hungry weight:  0.8  (hunger at 15/100)
  Tired weight:   0.3  (energy at 40/100)
  Current:        Chill (0.6)

  Hungry (0.8) > Chill (0.6) + hysteresis (0.15) = 0.75
  → Transition to Hungry
```

Each emotion has a minimum dwell time (10–60 seconds) to prevent rapid switching on e-ink. Forced overrides handle immediate responses — feeding a hungry pet forces 10 seconds of Excited before returning to normal resolution.

## Evolution — Deterministic, Not Random

When the pet reaches adulthood (day 14), its accumulated stats determine which of 6 adult forms it evolves into. This is fully deterministic — the player's care pattern produces a knowable outcome:

| Adult Form | Key Drivers |
|---|---|
| Deep-Sea Scholar | Intelligence + bond + discipline |
| Reef Guardian | Fitness + exploration |
| Tidal Trickster | Low discipline + high happiness |
| Abyssal Hermit | High discipline + low social |
| Coral Dancer | Happiness + music exposure |
| Storm Kraken | Lots of scolding + survived |

Each form is scored numerically. The highest score wins. A heritage bias from rebirth gives a slight nudge toward the parent's form, creating multi-generational lineage.

## MCU Migration: Write Once, Port Later

The ESP32-S3 board is in PCB design. The firmware is being written for the Pico W now, but 7 of 13 modules (stat system, emotion engine, life stages, progression, dialogue, decor, event bus) are pure C with zero hardware calls — they'll compile identically on the ESP32-S3 without a single change.

Hardware-touching code goes through a HAL abstraction layer. Sensor drivers call `hal_i2c_read()` instead of Pico SDK's `i2c_read_blocking()`. When the ESP32-S3 board arrives, only the HAL implementations swap — not the gameplay logic, not the sensor protocols, not the UI rendering.

The biggest structural change is FreeRTOS: the ESP32-S3 requires it, turning the bare-metal `while(true)` game loop into a FreeRTOS task. The game logic inside that task stays the same.

## AHT20 Replaces BME280

One hardware update made during this planning session: the temperature/humidity sensor changed from BME280 ($4, I2C 0x76) to AHT20 ($0.43, I2C 0x38). The AHT20 is a JLCPCB basic part, has better accuracy (+/-0.3C vs +/-1C), uses less power during measurement (23uA vs 350uA), and costs less than a tenth of the price. The only tradeoff is losing the barometric pressure sensor, which wasn't being used for gameplay anyway.

All documentation — engagement plan, PCB research, sensor interfaces, and this blog — has been updated to reflect the change.

## The Documents

The full gameplay architecture lives in 11 planning documents:

| Doc | Covers |
|-----|--------|
| 00 — Architecture Overview | Module map, data flow, memory budgets, file structure |
| 01 — Core Game Loop | Tick system, game states, sleep/wake, event bus |
| 02 — Stat System | Decay math, care actions, modifiers, thresholds |
| 03 — Emotion Engine | 16 trigger functions, blending, transitions |
| 04 — Sensor Interfaces | HAL for 7 sensors, polling rates, event classification |
| 05 — Input, Menu & UI | Button debounce, menu FSM, screen rendering |
| 06 — Life Stages & Evolution | Stage FSM, evolution scoring, rebirth |
| 07 — Progression & Unlocks | XP, bond levels, achievements, decor |
| 08 — Dialogue System | Quote selection, context triggers, intelligence gating |
| 09 — Persistence & Storage | Flash layout, save/load, wear leveling |
| 10 — Activity Tracker | Steps, targets, streaks, location, treasure hunts |
| 11 — MCU Migration Impact | RP2040 → ESP32-S3 porting guide |

Next step: implement Phase 3A — the core game loop with stat decay, care actions, and emotion resolution. The architecture is designed. Time to write the firmware.
