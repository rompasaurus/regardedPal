---
date: 2026-05-01
authors:
  - rompasaurus
categories:
  - Hardware
  - Software
tags:
  - freecad
  - tooling
  - renders
  - documentation
  - 3d-printing
---

# Build & Render Tool + Comprehensive Design Documentation

Built an interactive CLI render pipeline for FreeCAD models and wrote a complete component-by-component design document for the Rev 2 Mk2 enclosure.

<!-- more -->

## The Render Tool

Rendering FreeCAD models for documentation was a manual process: open the file, set visibility, position the camera, screenshot, repeat 30 times. The new `build_and_render.sh` tool automates all of it with an interactive menu.

### How it works

Run `./build_and_render.sh` from the `hardware-design/` directory and walk through 5 screens:

1. **Pick your FCStd file** from a date-sorted list (newest first, with file sizes)
2. **Choose what to render** from 19 options: full sets, individual bodies, peripherals, close-ups, animation, or custom combos
3. **Set the style**: resolution (up to 2560x1920), background (transparent/white/black), cover transparency (0-85%)
4. **Confirm** and the tool generates a Python render script on the fly
5. **FreeCAD GUI opens**, runs through each view, saves PNGs, and copies them to the website

### Technical challenges

- **Blank renders**: FreeCAD's `saveImage()` captures the viewport mid-draw if you don't wait. Fixed by pumping the Qt event loop 5 times with 300ms delays between each flush
- **Internal features**: toggling visibility on PartDesign features inside a Body (Pad, Pocket, Sketch) makes the parent Body render empty. Fixed by only toggling top-level objects
- **Custom camera angles**: FreeCAD doesn't have `ViewRotateRight` messages. Used pivy's Coin3D `SbRotation` to set exact yaw/pitch angles for product-shot views
- **Long filenames with spaces**: FCStd files with descriptive names broke shell argument parsing. The interactive picker eliminates typing entirely

## Design Document

The new [FreeCAD Mk2 Design](../../docs/hardware/freecad-mk2-design.md) page is a complete breakdown of every body, peripheral, and design decision in the enclosure:

- **12 component sections** each with isolated renders, specs tables, and design nuance
- **Assembly order** walkthrough (13 steps from solar panel to M3 screws)
- **Pain points** section documenting the Y-offset double-application bug, the cradle flip mental model, the dish-through-socket failure, fillet edge selection issues, and display inlay binding

## Render Gallery

The render tool produces 40+ images in a single run. Here's the current set:

| Render | Description |
|--------|-------------|
| `var-01-hero-iso` | Full assembly, transparent cover, isometric |
| `var-06a/b/c/d` | Four angled hero shots (front-right, front-left, low, rear) |
| `var-07/08` | Cover removed (iso + top) |
| `var-23/24/25` | Exploded views (iso, front, top) |
| `var-26/27` | Assembled opaque (iso + front) |
| `comp-*` | 14 isolated component portraits |

Source: [`tools/build-render/build_and_render.sh`](https://github.com/rompasaurus/dilder/blob/main/tools/build-render/build_and_render.sh)
