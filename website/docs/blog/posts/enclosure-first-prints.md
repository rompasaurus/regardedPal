---
date: 2026-04-22
authors:
  - rompasaurus
categories:
  - Hardware
  - 3D Printing
slug: enclosure-first-prints
---

# First 3D-Printed Enclosure Prototype

The parametric OpenSCAD enclosure design has made the jump from screen to plastic. First FDM prints are off the bed and components are fitting together.

<!-- more -->

## From CAD to Real Parts

The ESP32-S3 enclosure started as a single monolithic `.scad` file and has been broken out into standalone parametric parts, each iterated through multiple versions:

- **Middle plate** (board tray) — v2 with 56.5mm header slots, centered on the plate
- **Top plate windowed** (display cover) — v1 with solid face, snap-fit retaining rails, and printable full-width lips
- **Top cover frame** — v3 with rounded inner corners, single-corner-rounded pillars, and countersunk pockets for flush plate seating
- **Case separators** — inner and outer divider sheets with header pass-through slots

## Assembly Test

The stacked shell design works as intended. The LiPo battery drops into the base chamber, the middle plate rests on the lower shelf with the ESP32-S3 board's headers passing through the clearance slots, and the display cover snaps in over the Waveshare e-ink display.

![Assembled enclosure with e-ink display](../../assets/images/enclosure/enclosure-assembled-front.jpg)

![Base shell with LiPo battery and display top cover side by side](../../assets/images/enclosure/enclosure-halves-with-battery.jpg)

## Component Fit Check

All printed parts laid out alongside the electronics — the Olimex ESP32-S3-DevKit-Lipo, Waveshare 2.13" e-ink display, joystick breakout board, and 1000mAh LiPo battery.

![Components layout](../../assets/images/enclosure/components-layout-overview.jpg)

![ESP32-S3 board sitting on printed middle plate](../../assets/images/enclosure/esp32-board-on-printed-parts.jpg)

## What's Next

The current prints identified a few fit issues that drove the v2 and v3 iterations of the top cover — rounded inner corners and single-corner-rounded pillars so the windowed plate slides in without catching. The parametric design makes these changes fast: tweak a variable, re-export, reprint.

Next up: finalizing wire routing, testing snap-fit retention under repeated assembly cycles, and exploring the rounded-top cover variant for a more polished exterior feel.

All source files are in `hardware-design/scad Parts/` and the full design history is on the [Design Evolution](../../docs/hardware/design-evolution.md) page.
