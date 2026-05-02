---
date: 2026-05-02
authors:
  - rompasaurus
categories:
  - Hardware
tags:
  - freecad
  - 3d-printing
  - battery
  - soldering
  - nosolar
  - pico-w
---

# The NoSolar Variant Is Alive — Soldered, Battery-Powered, and Charging Over USB

The Dilder has a second enclosure option now: the **NoSolar variant** — a slimmer build that drops the solar panel cutout from the base plate and shaves 2 mm off the total height. Today it powered on for the first time running entirely off a 10440 Li-ion battery, with USB charging confirmed working through the TP4056 board.

<!-- more -->

## Why a NoSolar Variant?

The solar panel integration was always optional. The AK 62x36mm panel fits nicely in the base plate's cutout, but it adds height, complexity (adhesive bonding, wire routing), and only trickle-charges in ideal conditions. For indoor use — desk companion, shelf pet, bedside buddy — you just want USB-C charging and the thinnest possible case.

The NoSolar macro (`dilder_rev2_mk2_no_solar.FCMacro`) is a fork of the main Mk2 design with three changes:

1. **Solar panel pit, wire holes, and solar panel model removed** from the base plate
2. **Base plate height reduced** from 6 mm to 4 mm (`bp_h=4.0`, `floor=0.6`)
3. **USB reinforcement block added** under the USB-C cutout for structural support

Everything else — the AAA cradle, top cover with screen inlay and joystick hole, thumbpiece — is identical.

## First Power-On: Battery and Display

The unit is fully soldered now. The Pico W sits in the AAA cradle's center nest, wired directly to the TP4056 charge board and a single 10440 Li-ion cell (3.7V, 350mAh). No breadboard, no jumper wires — just solder joints and heat shrink.

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder powered on for the first time on battery — e-ink display showing the Sassy Octopus emotion with date header and quote, 10440 battery visible in the 3D-printed AAA cradle, TP4056 charge board LED glowing red indicating active charging, solder wick spool visible on the workbench](../../assets/images/hardware/first-battery-power-display-on.jpg){ width="420" loading=lazy }
  <figcaption>First battery power-on — the Sassy Octopus appears on the e-ink display, powered by a single 10440 cell with the TP4056 red LED confirming charge</figcaption>
</figure>

<figure markdown="span">
  ![Dilder unit side view showing the Waveshare 2.13-inch e-ink display edge profile, the soldered Pico W board edge visible behind the screen, 10440 battery seated in the 3D-printed AAA cradle with battery clips holding it in place, TP4056 USB-C charge board with red charging LED illuminated, wires connecting battery to charger to Pico VSYS, workbench with solder wick and flux pen in background](../../assets/images/hardware/first-battery-power-side-view.jpg){ width="420" loading=lazy }
  <figcaption>Side view — display, battery in cradle, and TP4056 charger with red LED (charging active)</figcaption>
</figure>

</div>

<figure markdown="span">
  ![Close-up of the soldered Dilder unit showing the Waveshare e-ink display face down at an angle, behind it the Pico W circuit board with visible solder joints and colored wires (red power, black ground) connecting to the TP4056 charge module, a single 10440 Li-ion cell (teal cylinder, 350mAh label visible) seated in the 3D-printed black AAA cradle insert with stamped metal battery clips, red LED on TP4056 indicating active USB charging, soldering supplies (flux, wick, solder) scattered on the workspace](../../assets/images/hardware/soldered-unit-battery-cradle.jpg){ width="420" loading=lazy }
  <figcaption>The soldered unit — Pico W wired to TP4056 and 10440 battery in the cradle. No breadboard, no jumpers — just solder</figcaption>
</figure>

## The NoSolar Case — Open and Closed

The NoSolar base plate is noticeably slimmer. Without the solar panel pit, the floor can be thinner and the whole case sits lower on the desk.

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder NoSolar variant open showing internals — the 3D-printed black base plate (without solar panel cutout) separated from the main case body, inside the case the Pico W circuit board is visible with its green PCB and gold castellated pads, a teal 10440 Li-ion battery sits below the board, red and black wires connect to the TP4056 USB-C charge module which has its red charging LED lit, a white USB-C cable is plugged into the TP4056 port for charging, the base plate shows the smooth underside with a circular thumbpiece depression and two rectangular slots for the cradle pegs](../../assets/images/enclosure/rev2-nosolar/nosolar-open-internals-top-view.jpg){ width="420" loading=lazy }
  <figcaption>NoSolar case opened — base plate (left) and assembled unit (right) with Pico W, 10440 battery, and TP4056 charging via USB</figcaption>
</figure>

<figure markdown="span">
  ![Dilder NoSolar variant assembled on a wooden surface — the 3D-printed black base plate with its flat underside (no solar cutout) sits next to the fully assembled unit, the case is a slim rectangular box with the Pico W visible through the open top, TP4056 charge module at one end with a white USB-C cable connected and red LED lit indicating active charging, wires routed from battery to charger to Pico, a Logitech THX speaker visible in the background on the workbench](../../assets/images/enclosure/rev2-nosolar/nosolar-base-and-unit-usb-charging.jpg){ width="420" loading=lazy }
  <figcaption>NoSolar variant — slimmer base plate with no solar cutout, USB-C charging active</figcaption>
</figure>

</div>

<figure markdown="span">
  ![Wide view of the Dilder NoSolar variant on a wooden chopping board on the workbench — the black 3D-printed base plate (no solar panel pit, smooth flat bottom) sits on the left next to the assembled unit on the right, the unit shows the Pico W green PCB, teal 10440 battery, and TP4056 with USB-C cable connected and red charging LED glowing, a Logitech speaker in the background, soldering supplies on the desk mat](../../assets/images/enclosure/rev2-nosolar/nosolar-base-and-unit-wide-view.jpg){ width="420" loading=lazy }
  <figcaption>The NoSolar build on the bench — thinner case, same internals</figcaption>
</figure>

## Fully Assembled and Running

The next morning, everything went back together. The display shows the Conspiratorial Octopus personality running with the RTC clock header — "DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS."

<figure markdown="span">
  ![Fully assembled Dilder unit in the black NoSolar 3D-printed case, the Waveshare 2.13-inch e-ink display is fully visible through the front window showing the date and time header reading MAY 2 2025 6:09 AM, below that is a text box containing the quote DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS with the pixel-art octopus character to the left of the text and CONSPIRATORIAL OCTOPUS personality label at the bottom, the case sits on a world map desk mat with North Africa visible below, a white USB-C cable connects from the right side for charging, a webcam and keyboard are visible in the background](../../assets/images/hardware/fully-assembled-display-running.jpg){ width="500" loading=lazy }
  <figcaption>"DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS." — Conspiratorial Octopus, running on battery with USB-C charging. The unit is fully soldered and assembled in the NoSolar case</figcaption>
</figure>

## The Solar Variant Still Exists

For comparison, here's the original solar panel variant from the back — the AK 62x36mm photovoltaic cells are visible through the base plate's cutout window.

<figure markdown="span">
  ![Dilder solar panel variant viewed from the back and top angle — the 3D-printed black case is seen from above and behind, the rectangular cutout in the base plate reveals the AK 62x36mm solar panel with its blue-grey photovoltaic cells arranged in rows behind a clear protective layer, the solar panel sits in a 2mm-deep recessed pit in the base plate with breakaway support ribs visible at the edges, a white USB-C cable is connected to the right side of the case, the unit sits on a world map desk mat with Europe and Turkey visible](../../assets/images/enclosure/rev2-nosolar/solar-variant-back-view.jpg){ width="420" loading=lazy }
  <figcaption>The solar variant — AK 62x36mm panel visible through the base plate cutout. Same internals, just with solar charging capability</figcaption>
</figure>

## What's Different Between the Two Variants

| Feature | Solar Variant | NoSolar Variant |
|---------|--------------|-----------------|
| Base plate height | 6 mm | 4 mm |
| Solar panel pit | 62x36mm, 2mm deep | None |
| Wire pass-through holes | 2x 3mm | None |
| USB reinforcement | Standard | Added block |
| Weight | Slightly heavier | Lighter |
| Charging | USB-C + solar trickle | USB-C only |

Both variants use the same AAA cradle, top cover, and thumbpiece. Swap the base plate and you switch between solar and non-solar.

## 3D Printing the Parts

The build session also produced a full set of parts for both variants. All the white and black pieces organized in the printer's storage drawer — base plates, top covers, cradles, and thumbpieces ready for the next build.

<div class="grid" markdown>

<figure markdown="span">
  ![3D printer storage drawer unit viewed from above and to the side — the top drawer is open showing a collection of freshly printed Dilder enclosure parts in white and black PLA, including multiple base plates (both solar and nosolar variants), top covers with display window cutouts, AAA cradle inserts with battery bay channels, and smaller thumbpiece caps, the parts are arranged loosely in the drawer alongside black foam inserts from the printer packaging, the drawer unit has a textured diagonal pattern on the white drawer fronts, two lower drawers are closed, a Gerolsteiner water bottle and energy drink can sit on the desk next to the drawer](../../assets/images/hardware/build-session/printed-parts-storage-close.jpg){ width="420" loading=lazy }
  <figcaption>The parts bin — both variants' pieces fresh off the printer, sorted in the storage drawer</figcaption>
</figure>

<figure markdown="span">
  ![Wider angle of the 3D printer storage drawer showing three stacked drawers with textured white fronts and black frames, the top drawer is open revealing the pile of printed Dilder case parts (white top covers, black base plates, white cradle inserts, thumbpieces) mixed with black foam packaging material, an Xbox controller is visible on the desk to the right, the drawer sits on a dark wooden desk surface with parquet flooring visible in the background](../../assets/images/hardware/build-session/printed-parts-storage-wide.jpg){ width="420" loading=lazy }
  <figcaption>The full drawer unit — three levels of printed parts and prototyping supplies</figcaption>
</figure>

</div>

## What's Next

The hardware is done for now. The unit is soldered, battery-powered, USB-charging, and running firmware. Next steps:

- **Order the joystick breakout PCB** from JLCPCB (gerbers already exported)
- **Wire the joystick** to the Pico W's GPIO pins
- **Start the game loop** — state machine, input handling, mood transitions
- **Evaluate battery life** — how long does 350mAh last with the e-ink display and WiFi off?

The NoSolar variant is available as a FreeCAD macro at `hardware-design/freecad-mk2/dilder_rev2_mk2_no_solar.FCMacro` and as pre-exported 3MF files for each part.
