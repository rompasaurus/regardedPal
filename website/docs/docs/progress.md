# Progress Report

A rolling log of what's been done, what's in progress, and what's next. Updated after each work session.

---

## 2026-05-04 — Joystick PCB, V4 Display Driver, Version System

### Done

- **Joystick PCB arrived from JLCPCB** — K1-1506SN-01 breakout boards with switches pre-mounted
- **Pin swap discovered** — COM and UP pins reversed in EasyEDA community library (C145910). KiCad symbol corrected for Rev 2 order
- **GPIO mapping confirmed** — L=GP2, D=GP3, UP=GP4, R=GP5, C=GP6 (Com=GND pin 3)
- **V4 display driver rewritten** — four iterations (V1.0→V1.4), final uses two-pass diff-based partial refresh for ghost-free updates
- **Firmware version system** — `version.h` shared across all 20 programs, startup banner with version + build timestamp
- **GPIO diagnostic** — raw pin state dump at startup and every 2s during runtime
- **DevTool updates** — V4 default, "Clean Build & Deploy" button, version verification
- **Mk2 translucent case** — 27 photos converted/named/placed, front page gallery, blog post, design evolution entry
- **Rolling TODO** created at project root

### In Progress

- V4 partial refresh blacks slightly washed compared to V3 — tuning the draw-pass waveform
- Joystick wiring needs COM/UP wire swap on current board (interim fix before Rev 2 PCB)

### Next Up

- [ ] Wire up and test piezo speaker
- [ ] Speaker grill cutout in case design
- [ ] Joystick retention chamfer
- [ ] Menu and settings system with joystick input
- [ ] Power on/off mechanism
- [ ] Battery life benchmarks
- [ ] Research wireless firmware deployment
- [ ] Compile full hardware schematic for dedicated board
- [ ] Order corrected Rev 2 joystick PCB

---

## 2026-05-02 — NoSolar Variant First Power

### Done

- Fully soldered unit — Pico W, TP4056, 10440 battery, heat shrink
- USB-C charging confirmed working (TP4056 red LED)
- NoSolar base plate variant (4mm height, no solar cutout)
- Conspiratorial Octopus personality running on battery

---

## 2026-04-27 — Joystick PCB Ordered

### Done

- Hand-routed K1-1506SN-01 breakout board designed from scratch in KiCad 10
- Gerbers + BOM + CPL exported for JLCPCB PCBA
- Order placed for 5 boards

---

## 2026-04-26 — Rev 2 v3 Print Session

### Done

- Base plate v3, cradle insert, top cover printed overnight
- All three parts fit-checked with Pico 2 W, TP4056, Ansmann batteries
- Solar panel (AK 62x36mm) evaluated for future charging
- FreeCAD parametric macro gaining new systems (piezo, IMU, joystick anchor)
