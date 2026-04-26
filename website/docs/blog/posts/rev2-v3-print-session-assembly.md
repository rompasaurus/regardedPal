---
date: 2026-04-26
authors:
  - rompasaurus
categories:
  - Hardware
  - Enclosure
  - Battery
slug: rev2-v3-print-session-assembly
---

# Rev 2 v3 Print Session — Assembly Photos and Next Steps

Overnight print of the latest base plate v3 (with support blocks and raised battery rails), updated cradle insert, and top cover. All three parts fit-checked with the Pico 2 W, TP4056 charge board, Ansmann AAA Li-Ion batteries, and Waveshare 2.13" e-ink display. Also pictured: a small solar panel being evaluated for future charging.

<!-- more -->

## What changed since last print

- **Base plate v3:** Battery rails raised 5 mm (now extend 2 mm above the plate top for better battery retention). Two 5x15 mm support blocks centered on the USB-C axis brace the TP4056 board from below. Pico retention block added.
- **Cradle insert:** Battery bay position and Pico nest length refined from yesterday's iterative session.
- **Top cover:** 5 mm wall extension below the mating plane for deeper engagement with the base plate.

## Full exploded layout

All three parts laid out with components: top cover (Pico 2 W + Waveshare display), cradle (TP4056 + AAA batteries), and base plate.

![Rev 2 v3 exploded layout](../../assets/images/enclosure/rev2-v3-exploded-all-three-parts.jpg)

## Cradle insert — fully loaded

Pico 2 W in the center nest, TP4056 charge board at the +X end, two Ansmann 1.5V Li-Ion AAA batteries in the flanking bays. The connecting block positions the TP4056 with its USB-C port aligned to the +X wall cutout.

![Cradle with all components top-down](../../assets/images/enclosure/rev2-cradle-v3-topdown-pico-tp4056-batteries.jpg)

![Cradle TP4056 close-up](../../assets/images/enclosure/rev2-cradle-v3-closeup-tp4056-batteries-topdown.jpg)

### Side and angled views

![Cradle side profile](../../assets/images/enclosure/rev2-cradle-v3-side-profile-battery-trough.jpg)

![Cradle angled — USB-C end](../../assets/images/enclosure/rev2-cradle-v3-angled-tp4056-usbc-end.jpg)

## Top cover interior

The Pico 2 W board seated in the cover's nest, with the Waveshare FPC ribbon cable folded over. The joystick through-hole and display inlay recess are visible.

![Top cover with Pico 2 W](../../assets/images/enclosure/rev2-topcover-v3-interior-pico2w-seated.jpg)

![Top cover — display inlay and joystick pocket](../../assets/images/enclosure/rev2-topcover-v3-interior-display-inlay-recess.jpg)

## Base plate v3

The updated base plate with two support blocks for TP4056 retention, battery troughs along the long sides, four corner peg pillars, and the USB-C stadium notch.

![Base plate v3 top-down](../../assets/images/enclosure/rev2-baseplate-v3-topdown-blocks-troughs.jpg)

![Base plate v3 side profile](../../assets/images/enclosure/rev2-baseplate-v3-side-profile-pegs-fillet.jpg)

## Assembled stack

The two-piece stack mated. The base plate's corner pegs slot into the top cover's blind M3 bores.

![Assembled stack side profile](../../assets/images/enclosure/rev2-v3-assembled-stack-side-profile.jpg)

## Solar panel — future charging

A small 62x36mm solar panel (AK 62X36) with pre-soldered red and black leads. This is being evaluated for trickle-charging the AAA batteries through the TP4056's input. The panel's 5V/100mA output is within the TP4056's input spec.

![Solar panel — back](../../assets/images/enclosure/rev2-solar-panel-pcb-back-ak62x36.jpg)

![Solar panel — front](../../assets/images/enclosure/rev2-solar-panel-pcb-front-cells.jpg)

## Next steps

1. **Wire batteries to the board** — solder battery contacts to Pico VSYS and TP4056 B+/B-
2. **Design joystick breakout PCB** — KiCad project already created (SKRHABE010 on 20x20mm board), ready for JLCPCB order
3. **Test solar charging** — measure the AK 62x36 panel output and verify TP4056 charging behavior

Source: [`04-25-design-alterations/`](https://github.com/rompasaurus/dilder/tree/main/hardware-design/scad%20Parts/Rev%202%20extended%20with%20joystick/04-25-design-alterations)
