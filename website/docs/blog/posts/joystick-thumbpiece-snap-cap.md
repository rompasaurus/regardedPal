---
date: 2026-04-30
authors:
  - rompasaurus
categories:
  - Hardware
tags:
  - freecad
  - joystick
  - 3d-printing
  - parametric
---

# A snap-on thumbpiece for the joystick — designing a tiny part by talking to the CAD

The K1-1506SN-01 5-way switch on the joystick PCB has a bare 3.2 × 3.2 mm rectangular peg sticking up through the cover. Pressing it directly works, but it's small, sharp at the corners, and the peg sticks up into the cover's 12 mm circle cutout where it looks half-finished. I wanted a printable snap cap — concave for the thumb, sized to vanish into the cutout, and tight enough on the peg to stay put without glue.

<!-- more -->

This post walks through how the design landed, what the wrong turns were, and the one geometric constraint that almost ruined it.

## The brief, in one sentence

> Make a thumbpiece that snaps onto the joystick peg, sits flush in the 12 mm cover hole, has a concave thumb dish on top, and is 1 mm smaller in diameter than the cutout.

That's pretty specific — but each phrase ends up implying something the others don't. "Snaps onto the peg" wants the snap socket to land on the actuator. "Flush in the hole" wants the disc centered on the cover hole. Those two centers turn out to be **different points**.

## The peg isn't where you think it is

Selecting the peg's faces in FreeCAD's tree view (the `JoystickPCB` STEP imported from KiCad) and reading off the click coordinates:

| Face | X | Y | Z |
|------|---|---|---|
| Face276 | 77.86 | 22.76 | 19.12 |
| Face274 | 80.88 | 22.79 | 18.54 |
| Face281 | 80.84 | 22.77 | 21.07 |
| Face273 | 80.95 | 24.08 | 17.91 |
| Face271 | 79.01 | 25.94 | 19.58 |
| Face270 | 77.79 | 25.86 | 19.82 |
| Face269 | 77.75 | 25.32 | 19.80 |
| Face278 | 80.83 | 25.85 | 21.17 |

Span: X 77.75 → 80.95 (3.2 mm), Y 22.76 → 25.94 (3.18 mm), Z 17.91 → 21.17 (3.26 mm). So the peg cross-section is 3.2 × 3.2 mm, with its **center** at (79.35, 24.35), and the top of the peg is at Z = 21.17.

The cover hole, on the other hand, is at (79.35, **23.67**) — that's `joy_cx, enc_y/2 + joy_pcb_y_offset` from the spreadsheet. Same X, but +0.68 mm Y offset. The K1-1506SN-01 sits at a Y offset on the PCB layout, and the cover hole was already shifted to match the **PCB bbox center**, not the peg axis.

The implication: a thumbpiece that "looks centered in the hole" is not centered on the peg. If the disc and the snap socket share an axis, you have to pick one — the disc looks crooked, or the socket misses the peg by 0.68 mm. The fix is to give them **separate centers**: disc on the hole, socket on the peg.

## The wrong turn: a T-shape

First attempt (after "I do not want the square of the joystick exposed") was a mushroom shape — a wider cap riding on top of the cover that hides the peg, with a narrower stem dropping through the hole onto the actuator. The cap's overhanging rim would bottom on the cover top and act as a downward-travel stop. Two cylinders, fused at the shoulder, dish on the cap top, socket inside the stem.

This was wrong because "1 mm shorter than the cutout" already meant the **whole thing** lives inside the hole, not above it. The T-shape sticks out — even with a 0.3 mm air gap for press travel, the cap is permanently visible above the cover. Reverted.

## The single disc, with one hidden constraint

What survived: a single disc, OD 11 mm, height 4.5 mm, sitting entirely inside the 12 mm hole. Top at Z = 22.9 (0.1 mm below the cover top so it doesn't poke proud), bottom at Z = 18.4. Three features:

```python
# 1. Disc
disc = body.newObject("PartDesign::AdditiveCylinder", "Thumb_Disc")
disc.Radius = 11.0 / 2
disc.Height = 4.5
disc.Placement = App.Placement(V(79.35, 23.67, 18.40), ROT0)  # disc center on hole

# 2. Concave thumb dish — sphere subtraction
dish = body.newObject("PartDesign::SubtractiveSphere", "Thumb_Dish")
dish.Radius = 12.0
dish.Placement = App.Placement(
    V(79.35, 23.67, 22.90 + 12.0 - 0.6), ROT0)  # south pole at top - 0.6

# 3. Snap socket — rectangular pocket centered on the PEG, not the disc
sock = body.newObject("PartDesign::SubtractiveBox", "Thumb_Socket")
sock.Length = 3.3   # 3.2 mm peg + 0.1 mm clearance
sock.Width = 3.3
sock.Height = 3.5 + 0.1
sock.Placement = App.Placement(
    V(79.35 - 3.3/2, 24.35 - 3.3/2, 18.40 - 0.05), ROT0)
```

Then the dish — and this is where it almost broke.

## "Why is the peg still showing through the top?"

The first cut had a 1.5 mm-deep dish on the disc top. When I rendered, the peg was clearly visible *through the top of the disc* — the dish had eaten a hole all the way into the snap cavity.

The math, after staring at it for a minute:

- Disc top at Z = 22.9
- Socket ceiling at Z = 18.4 + 3.5 + 0.05 = **21.95**
- Dish bottom (deepest point) at Z = 22.9 − 1.5 = **21.4**

21.4 < 21.95 — the dish reaches **below** the socket ceiling, breaching the cavity. Anything deeper than `disc_top - socket_ceiling` opens a window from the thumb side straight down to the peg. So the constraint, written into the spreadsheet alongside the parameter:

```
thumb_dish_d  <  thumb_h  −  thumb_top_clr  −  thumb_sock_d
```

With the current numbers: `4.5 − 0.1 − 3.5 = 0.9` mm hard limit. Set `thumb_dish_d = 0.6` and you get 0.35 mm of solid material as a "skin" covering the peg. Still visibly concave, still comfortable for a thumb, no peg poking through.

If you want a deeper dish later, you have three knobs: increase `thumb_h` (taller disc), decrease `thumb_sock_d` (shallower socket), or do both. The relationship is now in a comment next to the parameter so future-me doesn't have to rediscover it.

## Why this had to be a separate Body

The thumbpiece is a **printable accessory** — the user prints it, snaps it on, and that's the part. So it's its own PartDesign Body in the FCStd, not a feature of the cover. Three benefits:

1. **Separate STL/3MF export** — the part export pipeline already iterates over Bodies; this one slots in next to BasePlate, AAACradle, TopCover.
2. **Independent placement** — when the cover moves in the assembly, the thumbpiece moves with it via global coordinates.
3. **Spreadsheet wiring intact** — `disc.setExpression("Radius", "Parameters.thumb_od / 2")` keeps every dimension live; change `thumb_od` in the spreadsheet, hit Ctrl+Shift+R, and the disc rebuilds.

## What's next

Two follow-ups that didn't make this pass:

- **Snap retention** — the current 3.3 × 3.3 mm socket is a slip-fit, not a true snap. Dropping the socket to 3.15 × 3.15 makes it interference-fit (the part deforms slightly to slide on, then grips), which is what you want from FDM/SLA prints. I left the default loose because I'd rather print loose and discover I want tight than print tight and have it crack on first install.
- **Print orientation** — the dish should print top-up so the thumb-contact surface is the smooth side, not a layer-line side. Cap the print bed with a brim if the 11 mm contact patch wants to lift.

Source: `hardware-design/freecad-mk2/dilder_rev2_mk2.FCMacro`, `build_thumbpiece(doc)`. Default values in the `Parameters` spreadsheet — change any, hit recompute.
