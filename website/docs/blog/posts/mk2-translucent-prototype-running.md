---
date: 2026-05-04
authors:
  - rompasaurus
categories:
  - Hardware
  - Enclosure
  - Battery
tags:
  - freecad
  - 3d-printing
  - translucent
  - mk2
  - battery
  - prototype
slug: mk2-translucent-prototype-running
---

# Mk2 Translucent Prototype — Fully Assembled and Running on Battery

The Dilder has a new look. The **Mk2 translucent case** is printed, assembled, and running the Conspiratorial Octopus personality on battery power. This is the first revision where the internals are deliberately visible through the case walls — the Pico W, 10440 battery, TP4056 charger, piezo speaker ring, and wiring are all part of the aesthetic.

<!-- more -->

## What's New in This Print

The Mk2 translucent variant uses the same FreeCAD parametric macro as the NoSolar revision, but printed in **natural/clear PETG** instead of black PLA. The result is a case where every internal component is visible — you can see the battery, the charging LED, the speaker pocket, and the full PCB layout without opening the device.

Key changes from the previous black NoSolar case:

- **Material:** Natural/clear PETG — semi-translucent, showing internals
- **Thicker base plate** with extended peg pillars for better snap retention
- **Joystick dome** — the circular joystick mount is clearly visible from the front, ready for the K1-1506SN-01 breakout board
- **Display window** — e-ink screen sits flush in the inlay recess with good contrast through the translucent surround

## Bare Board Battery Testing (May 1)

Before the translucent case was printed, the electronics were tested bare on the workbench. The Pico W, Waveshare 2.13" e-ink display, 10440 Li-ion battery, and TP4056 USB-C charger were wired and confirmed working — display rendering the Sassy Octopus personality while charging (red LED on TP4056).

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder bare board on workbench — e-ink display showing Sassy Octopus quote with 10440 battery and TP4056 charging LED red](../../assets/images/hardware/bare-board-battery-test/display-sassy-octopus-battery-charging.jpg){ width="420" loading=lazy }
  <figcaption>Bare board test — Sassy Octopus on display, 10440 battery with TP4056 charging (red LED)</figcaption>
</figure>

<figure markdown="span">
  ![Dilder bare board side angle — display running with battery and TP4056 charger visible](../../assets/images/hardware/bare-board-battery-test/display-running-battery-side-angle.jpg){ width="420" loading=lazy }
  <figcaption>Side angle — display, battery, and TP4056 wiring visible on the workbench</figcaption>
</figure>

</div>

## NoSolar Black Case — Internals Open (May 1)

The black NoSolar variant was opened up to show the internal wiring before the new translucent case was ready. The base plate sits alongside the assembled unit with Pico W, battery, and TP4056 all soldered in.

<div class="grid" markdown>

<figure markdown="span">
  ![NoSolar case opened — base plate separated, showing Pico W and battery inside the black case with TP4056 charging LED red](../../assets/images/enclosure/rev2-nosolar/nosolar-baseplate-and-unit-side-view.jpg){ width="420" loading=lazy }
  <figcaption>NoSolar base plate and assembled unit — side view with charging LED</figcaption>
</figure>

<figure markdown="span">
  ![NoSolar open top-down — Pico W green board, 10440 battery in teal wrapper, TP4056 with red LED, wiring visible](../../assets/images/enclosure/rev2-nosolar/nosolar-open-topdown-pico-battery-tp4056.jpg){ width="420" loading=lazy }
  <figcaption>Top-down — Pico W, 10440 battery, and TP4056 charger with red LED (charging active)</figcaption>
</figure>

</div>

## Assembled NoSolar — Display Running (May 2)

The black NoSolar variant running the Conspiratorial Octopus personality, fully assembled and battery-powered.

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder NoSolar assembled — front view showing Conspiratorial Octopus quote DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS on e-ink display in black 3D-printed case](../../assets/images/enclosure/rev2-nosolar/nosolar-assembled-front-conspiratorial-octopus.jpg){ width="420" loading=lazy }
  <figcaption>"DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS." — Conspiratorial Octopus in the black NoSolar case</figcaption>
</figure>

<figure markdown="span">
  ![Dilder solar variant — back view showing AK 62x36mm solar panel through the base plate cutout with USB cable](../../assets/images/enclosure/rev2-nosolar/solar-variant-back-panel-closeup.jpg){ width="420" loading=lazy }
  <figcaption>Solar variant back — AK 62x36mm panel visible through the base plate cutout</figcaption>
</figure>

</div>

## Mk2 Translucent Case — Indoor Desk Shots (May 3)

The new translucent case with everything assembled inside. The cross-hatch print pattern gives the case a frosted-glass look while still letting you see every component through the walls.

<div class="grid" markdown>

<figure markdown="span">
  ![Mk2 translucent Dilder — isometric view showing Conspiratorial Octopus on e-ink display, joystick dome, and internals visible through clear PETG case](../../assets/images/enclosure/mk2-translucent/mk2-translucent-isometric-display-running.jpg){ width="420" loading=lazy }
  <figcaption>Isometric — display running, joystick dome on the right, translucent walls showing battery and board</figcaption>
</figure>

<figure markdown="span">
  ![Mk2 translucent Dilder — front view showing THE MOON LANDING WAS REAL BUT THE MOON IS FAKE quote on e-ink display](../../assets/images/enclosure/mk2-translucent/mk2-translucent-front-moon-landing-quote.jpg){ width="420" loading=lazy }
  <figcaption>"THE MOON LANDING WAS REAL BUT THE MOON IS FAKE." — front view, display sharp and readable</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Mk2 translucent Dilder — three-quarter left angle showing case profile and USB-C port side](../../assets/images/enclosure/mk2-translucent/mk2-translucent-three-quarter-left.jpg){ width="420" loading=lazy }
  <figcaption>Three-quarter left — USB-C port side and case profile</figcaption>
</figure>

<figure markdown="span">
  ![Mk2 translucent Dilder — back view showing TP4056, battery, and piezo ring visible through translucent walls](../../assets/images/enclosure/mk2-translucent/mk2-translucent-back-internals-visible.jpg){ width="420" loading=lazy }
  <figcaption>Back view — TP4056, battery, and piezo speaker ring all visible through the case</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Mk2 translucent Dilder — bottom baseplate showing internal component layout through clear PETG](../../assets/images/enclosure/mk2-translucent/mk2-translucent-bottom-baseplate-layout.jpg){ width="420" loading=lazy }
  <figcaption>Base plate bottom — display pocket, piezo ring, and battery trough layout visible</figcaption>
</figure>

<figure markdown="span">
  ![Mk2 translucent Dilder — isometric view with DEJA VU IS THE SIMULATION BUFFERING quote](../../assets/images/enclosure/mk2-translucent/mk2-translucent-isometric-deja-vu-quote.jpg){ width="420" loading=lazy }
  <figcaption>"DEJA VU IS THE SIMULATION BUFFERING." — isometric with joystick dome prominent</figcaption>
</figure>

</div>

## Outdoor Shots — Balcony in Natural Light (May 3)

The translucent case taken outside to the balcony. The e-ink display is completely readable in direct sunlight — one of the key advantages of e-paper over LCD/OLED. The Conspiratorial Octopus has opinions about ancient architecture.

<div class="grid" markdown>

<figure markdown="span">
  ![Mk2 translucent Dilder outdoors — front view with THE PYRAMIDS WERE BUILT BY CATS quote on e-ink display, blue sky and rooftops in background](../../assets/images/enclosure/mk2-translucent/mk2-translucent-outdoor-front-pyramids-quote.jpg){ width="420" loading=lazy }
  <figcaption>"THE PYRAMIDS WERE BUILT BY CATS. EGYPTIANS JUST TOOK CREDIT." — e-ink perfectly readable in sunlight</figcaption>
</figure>

<figure markdown="span">
  ![Mk2 translucent Dilder outdoors — hero front shot with Claude Code terminal visible on laptop in background](../../assets/images/enclosure/mk2-translucent/mk2-translucent-outdoor-hero-front-claude-code.jpg){ width="420" loading=lazy }
  <figcaption>Hero shot — Conspiratorial Octopus on the balcony with Claude Code running on the laptop behind</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Mk2 translucent Dilder outdoors — three-quarter right angle showing case depth and joystick dome](../../assets/images/enclosure/mk2-translucent/mk2-translucent-outdoor-three-quarter-right.jpg){ width="420" loading=lazy }
  <figcaption>Three-quarter right — case depth and joystick dome profile in natural light</figcaption>
</figure>

<figure markdown="span">
  ![Mk2 translucent Dilder outdoors — back view showing internals through clear PETG with TP4056 red wiring and piezo ring](../../assets/images/enclosure/mk2-translucent/mk2-translucent-outdoor-back-internals.jpg){ width="420" loading=lazy }
  <figcaption>Back view outdoors — TP4056 wiring (red), piezo speaker ring, and display pocket all visible</figcaption>
</figure>

</div>

## What's Next

This print session confirms the Mk2 case design works. The translucent variant is now the **primary demo unit** — it shows off the internals and makes a better visual for documentation and social media. Next up from the [TODO list](../../TODO.md):

1. **Wire up the piezo speaker** and test audio through the case
2. **Add speaker grill cutout** to the case design
3. **Mount the joystick** with the K1-1506SN-01 breakout board
4. **Implement menu system** using joystick input
5. **Run battery life benchmarks** on the assembled unit

The Conspiratorial Octopus has earned its keep as the test personality — every quote it displays is a built-in sanity check that the full rendering pipeline (date header, quote text, pixel-art octopus, body animation, personality name) is working end to end.
