# Waveshare 2.13" e-Paper — Physical Dimensions

Reference for sizing the display inlay recess in `top-cover-windowed-*.scad`.

Photos of the user's actual display + HAT are in this folder:
- `waveshare-screen-1.jpg` — raw e-paper module (front, with FPC)
- `waveshare-screen-2.jpg` — Rev 2.1 driver HAT (top of PCB)

**All values below are approximate Waveshare spec / typical values. Verify against the actual parts with calipers before finalizing the recess — individual revisions (V1, V2, V3, V4) differ by ~0.5 mm and the PCB bezel trim has changed over time.**

## Raw e-paper module (what goes into the cover inlay)

| Feature                        | Nominal (mm) | Notes |
|--------------------------------|--------------|-------|
| Module outer length (long)     | 65.0         | runs along enclosure X in Rev 2 |
| Module outer width (short)     | 30.2         | runs along enclosure Y |
| Module thickness (glass + PCB) | 1.18         | **<< 3 mm recess depth — screen will have headroom** |
| Active display area length     | 48.55        | horizontal (X) in landscape |
| Active display area width      | 23.70        | vertical (Y) |
| Resolution                     | 250 × 122 px | |
| Pixel pitch                    | ~0.194       | both axes |
| Diagonal (marketing)           | 2.13 inch    | |

### Active area placement on the module

The active area is NOT centered on the module — the bezel is asymmetric:
- The **FPC-end short edge** has extra bezel width to accommodate the flex cable, driver traces, and alignment hole.
- The **opposite short edge** has a minimal bezel (~1–2 mm).
- Both long edges have roughly equal, thin bezels (~3 mm each).

Approximate active-area offsets (from the module's outer edges, with the FPC exiting the +X short edge — confirm against the photo):
- Offset from -X short edge to active area: ~9 mm (thin bezel side is -X)
- Offset from +X short edge to active area: ~7 mm (FPC/driver side is +X, slightly thicker)
- Offset from ±Y long edges to active area: ~3.25 mm each

## FPC ribbon cable

| Feature              | Nominal (mm) | Notes |
|----------------------|--------------|-------|
| FPC exit edge        | short edge   | see photo — exits +X side in photo orientation |
| FPC width            | ~6.5         | typical 24-pin 0.5 mm-pitch ribbon |
| FPC length (to connector) | ~14     | folds back onto module or mates with HAT connector |
| FPC pitch            | 0.5          | 24-pin, 0.5 mm pitch is standard for 2.13" V4 |

## Mounting / alignment hole

Photo shows a small circular hole near the FPC-end edge, on one long-side corner of the bezel (visible near the bottom-right of photo 1). Used for mechanical alignment in some mounting schemes.

| Feature                 | Nominal (mm) | Notes |
|-------------------------|--------------|-------|
| Hole diameter           | ~1.5         | typical alignment hole, not a screw |
| Position (from nearest corner) | ~3 / ~3 | X / Y offset; confirm with calipers |

Not currently used by the Dilder enclosure — retention is via the 3 mm recess cut into the top cover's face plate underside.

## Rev 2.1 driver HAT (reference only — NOT in the enclosure)

Photo 2 shows the separate Raspberry Pi-format HAT that accepts the raw module's FPC. Not relevant to the enclosure geometry but kept here so the part count is clear.

| Feature                 | Nominal (mm) | Notes |
|-------------------------|--------------|-------|
| HAT PCB length          | ~65          | matches the raw module footprint |
| HAT PCB width           | ~30          | |
| GPIO header             | 2×20, 2.54 mm pitch | standard Pi HAT |
| FPC connector (on HAT)  | 24-pin, 0.5 mm pitch | receives raw module's FPC |
| BS jumper (interface select) | 1 = 3-wire SPI / 0 = 4-wire SPI | |
| Driver IC               | SSD1680 (typical for 2.13" V4) | |
| Markings                | "Waveshare 2.13inch e-Paper HAT Rev 2.1" | |

## Dimensions used by the SCAD files

Matches the values in `top-cover-windowed-v1.scad` and `top-cover-windowed-screen-inlay-v1.scad`:

```
display_footprint_length_along_x_mm   = 65     // long axis, landscape
display_footprint_depth_along_y_mm    = 30     // short axis
display_footprint_thickness_z_mm      = 5      // SCAD clearance envelope (> 1.18 mm actual)
print_fit_tolerance_slop_mm           = 0.4    // XY clearance per edge for 3D print shrink
```

The 5 mm `display_footprint_thickness_z_mm` is a **clearance envelope** — it's what the cavity below the face plate was sized to accept in the old rail-retention design. The actual display glass + PCB is ~1.18 mm; the extra room is for the FPC fold and any driver board stacked underneath.

The inlay recess uses 3 mm depth, which is ~2.5× the raw module thickness — leaves room for foam / adhesive tape behind the module without the module bottoming out in the recess.
