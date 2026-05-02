<div id="octopus-banner"></div>

# Dilder

**A real-time build journal for an open-source AI-assisted virtual pet.**

Dilder is a Tamagotchi-style device built on a Raspberry Pi Pico W, a Waveshare 2.13" e-ink display, and a 3D-printed case — developed entirely in the open, one phase at a time.

---

## The Origin Story — How Jamal Was Found

<figure markdown="span">
  ![Jamal the plush octopus, lounging in a chair like he owns the place](assets/images/jamal-the-original.jpg){ width="420" loading=lazy }
  <figcaption>Jamal. Chair thief. Hat enthusiast. The one who started it all.</figcaption>
</figure>

It started with a trip to TEDi — a German dollar store where the shelves are chaos and the deals are questionable. My wife Emma and I were browsing the bins, not looking for anything in particular, when we spotted him: a massive plush octopus, soft as a cloud, grinning up at us from a pile of discount stuffed animals like he'd been waiting.

We bought him. Obviously.

On the walk home, something happened. We started talking *to* him. Then *about* him — as if he had opinions, preferences, a whole inner life. By the time we got back to the apartment, he had a name: **Jamal**. He had a personality: laid-back but opinionated, a little sassy, suspiciously wise for a creature with no skeleton. He claimed the armchair immediately. He looked... comfortable. *Too* comfortable. Like he'd always lived there and we were the guests.

And then the question asked itself:

> *What if we could actually bring him to life?*

Not literally — we're not mad scientists (yet). But what if we could build a tiny digital version of Jamal? A pocket-sized octopus with moods, opinions, and an attitude problem? Something that lives on a screen, reacts to the world, and roasts you when you forget to feed it?

That's how Dilder was born. Not from a grand engineering vision or a product roadmap — from a plush octopus in a discount bin and two people who couldn't stop giving him a backstory on the walk home.

Jamal still sits in the armchair. He still wears the hat. He watches us build his digital self from across the room, and honestly? He looks unimpressed. Which tracks.

---

## The Current Build

<div class="grid" markdown>

<figure markdown="span">
  ![Fully assembled Dilder unit running the Conspiratorial Octopus personality — e-ink display shows MAY 2 2025 6:09 AM header and the quote DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS with pixel-art octopus, housed in the black NoSolar 3D-printed case, USB-C cable connected for charging](assets/images/hardware/fully-assembled-display-running.jpg){ width="420" loading=lazy }
  <figcaption>"DREAMS ARE LEAKED FOOTAGE FROM ALTERNATE DIMENSIONS." — Conspiratorial Octopus, fully soldered and battery-powered</figcaption>
</figure>

<figure markdown="span">
  ![Dilder Rev 2 — assembled front view showing Sassy Octopus on e-ink display](assets/images/enclosure/rev2-current/rev2-assembled-front-view.jpg){ width="420" loading=lazy }
  <figcaption>"COFFEE IS JUST BEAN BROTH FOR PEOPLE WHO HATE THEMSELVES." — Sassy Octopus, running on Pico 2 W</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder NoSolar variant opened showing internals — black base plate without solar cutout separated from the assembled unit with Pico W, 10440 battery, and TP4056 USB-C charger with red LED lit](assets/images/enclosure/rev2-nosolar/nosolar-open-internals-top-view.jpg){ width="420" loading=lazy }
  <figcaption>NoSolar variant opened — Pico W, 10440 battery, and TP4056 charger. Fully soldered, USB-C charging confirmed</figcaption>
</figure>

<figure markdown="span">
  ![Dilder Rev 2 — case parts disassembled showing top cover, base plate, and cradle](assets/images/enclosure/rev2-current/rev2-case-parts-disassembled.jpg){ width="420" loading=lazy }
  <figcaption>Disassembled — top cover with display inlay, base plate with solar cutout, battery cradle insert</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder first battery power-on — e-ink display showing the Sassy Octopus with 10440 battery in cradle and TP4056 charging LED glowing red](assets/images/hardware/first-battery-power-display-on.jpg){ width="420" loading=lazy }
  <figcaption>First battery power-on — soldered unit running off a single 10440 cell with TP4056 charge indicator</figcaption>
</figure>

<figure markdown="span">
  ![Dilder solar variant back view showing the AK 62x36mm solar panel through the base plate cutout](assets/images/enclosure/rev2-nosolar/solar-variant-back-view.jpg){ width="420" loading=lazy }
  <figcaption>Solar variant (alternative) — AK 62x36mm panel visible through the base plate. Same internals, plus solar trickle charging</figcaption>
</figure>

</div>

---

## Latest Prototype — Sensors, Speaker, and Joystick Anchor

The parametric FreeCAD macro gained three new systems: a **20 mm piezo speaker** in a circular retaining ring, an **MPU-6500 6-axis accelerometer** in a recessed pocket, and a precision **joystick anchor pad** that replaces the old well/sleeve design. The joystick PCB alignment was fixed (stick now dead-center in the hole), and the cradle pit tightened from 23 mm to 20 mm for a snug board fit.

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder Rev 2 — hero isometric](assets/images/enclosure/var-01-hero-iso.png){ width="420" loading=lazy }
  <figcaption>Hero shot — full assembly with all components visible through the translucent cover</figcaption>
</figure>

<figure markdown="span">
  ![Dilder Rev 2 — 3/4 angle front-right](assets/images/enclosure/var-06a-angle-front-right.png){ width="420" loading=lazy }
  <figcaption>3/4 angle — joystick thumbpiece and display window on the bullnose dome</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder Rev 2 — exploded isometric](assets/images/enclosure/var-23-exploded-iso.png){ width="420" loading=lazy }
  <figcaption>Exploded view — base plate, cradle with batteries, cover with anchor pad, and thumbpiece</figcaption>
</figure>

<figure markdown="span">
  ![Dilder Rev 2 — assembled opaque](assets/images/enclosure/var-26-assembled-opaque-iso.png){ width="420" loading=lazy }
  <figcaption>Assembled (opaque cover) — the finished device with display window and joystick</figcaption>
</figure>

</div>

<div class="grid" markdown>

<figure markdown="span">
  ![Dilder Rev 2 — cover removed](assets/images/enclosure/var-07-cover-removed-iso.png){ width="420" loading=lazy }
  <figcaption>Cover removed — cradle with batteries, Pico board, TP4056 charger, and joystick PCB</figcaption>
</figure>

<figure markdown="span">
  ![Dilder Rev 2 — base plate sensors](assets/images/enclosure/var-11-pico-sensors-on-base.png){ width="420" loading=lazy }
  <figcaption>Base plate — piezo speaker ring (center) and IMU pocket (left) between battery rails</figcaption>
</figure>

</div>

[Read the full build write-up :material-arrow-right:](blog/posts/joystick-anchor-piezo-imu-sensors.md){ .md-button }

[View the complete design breakdown :material-arrow-right:](docs/hardware/freecad-mk2-design.md){ .md-button }

---

## Meet the Octopus

A tiny octopus lives on a 250x122 pixel e-ink display. It has **16 emotional states**, each with unique eyes, mouth expressions, body animations, and themed quotes. It's sassy. It's opinionated. It runs on 100KB of firmware and a coin cell's worth of ambition.

Pick a personality, flash it to the board, and you've got a desk companion that judges your life choices in ALL CAPS.

---

## The Hardware

Three supported boards. Same firmware. Under $25 to get started.

| Component | Price | Why |
|-----------|-------|-----|
| Raspberry Pi Pico 2 W | ~$7 | 4MB flash, WiFi + BLE, RP2350 dual Cortex-M33, current default |
| Raspberry Pi Pico W | ~$6 | 2MB flash, WiFi + BLE, RP2040, original dev board |
| Waveshare 2.13" e-Paper V3 | ~$15 | 250x122px, paper-like readability, near-zero standby current |
| 3D-printed enclosure | ~$2 filament | Two-piece snap-fit case, SCAD source files included |

---

## 16 Emotions, One Octopus

Every mood changes the face, the body, and the attitude.

<div class="grid" markdown>

![Normal](docs/software/emotion-previews/normal.png){ width="220" }
![Angry](docs/software/emotion-previews/angry.png){ width="220" }
![Sad](docs/software/emotion-previews/sad.png){ width="220" }

![Excited](docs/software/emotion-previews/excited.png){ width="220" }
![Lazy](docs/software/emotion-previews/lazy.png){ width="220" }
![Fat](docs/software/emotion-previews/fat.png){ width="220" }

</div>

Normal. Angry. Sad. Excited. Lazy (tentacles draped to the right, naturally). Fat (thicc dome, no waist, proud of it). Plus Weird, Unhinged, Chaotic, Hungry, Tired, Slap Happy, Chill, Creepy, Nostalgic, and Homesick.

Each personality has 30-196 themed quotes, a 4-frame mouth animation cycle, and per-mood body movement — breathing bobs, angry trembles, chaotic distortion, lazy lounging.

[See all 16 emotion states :material-arrow-right:](docs/software/emotion-states.md){ .md-button }

---

## The DevTool

A custom Tkinter GUI for designing, previewing, and deploying octopus firmware — without touching a terminal.

<figure markdown="span">
  ![DevTool Programs tab](assets/images/devtool/devtool_tab_programs.png){ width="700" loading=lazy }
  <figcaption>Programs tab — pick a personality, preview it, flash it to the Pico</figcaption>
</figure>

**7 tabs:** Display Emulator (pixel art tools) | Serial Monitor | Flash Firmware | Asset Manager | Programs (17 octopus personalities) | GPIO Pin Reference | Connection Utility

Select a program and you get a live preview, estimated firmware size (~100KB), how much of the Pico's 2MB flash you'll use (~5%), and one-click deploy.

[DevTool docs :material-arrow-right:](docs/tools/devtool.md){ .md-button }

---

## First PCB from Scratch — Joystick Breakout Board

Before the Dilder, the closest I'd come to PCB design was staring at someone else's Gerber files and thinking "that looks complicated." This board changed that.

The joystick needed a breakout board — the K1-1506SN-01 5-way switch is a tiny surface-mount component with six pins spaced 1.27 mm apart. You can't hand-solder wires to that. So instead of buying a pre-made breakout (they don't exist for this switch), I designed one from scratch in KiCad 10.

<div class="grid" markdown>

<figure markdown="span">
  ![Schematic editor in KiCad](assets/images/hardware/pcb/joystick-hand-schematic-editor.jpg){ width="420" loading=lazy }
  <figcaption>The schematic — five direction pins (Up, Down, Left, Right, Push) plus a common ground, all routed through the switch to header pads</figcaption>
</figure>

<figure markdown="span">
  ![PCB layout editor in KiCad](assets/images/hardware/pcb/joystick-hand-pcb-layout-editor.jpg){ width="420" loading=lazy }
  <figcaption>The PCB layout — every trace hand-routed on a 19.6 x 19.6 mm board. No autorouter, no templates, just dragging copper one track at a time</figcaption>
</figure>

</div>

### What's on the board

The switch sits in the center. Six pads radiate out to header holes along one edge — 2.54 mm pitch so you can solder standard pin headers and plug it straight into a breadboard or the Dilder's cradle pit. The whole thing is smaller than a postage stamp.

The routing was the fun part. KiCad shows you the "ratsnest" — a web of thin lines showing which pads need to connect — and you trace actual copper paths between them. It's like a puzzle where the pieces are wires and the constraint is "don't let them cross." Six signals on a single-layer board means some creative curving, but the K1-1506SN-01 has a clean enough pinout that everything routes without vias.

<div class="grid" markdown>

<figure markdown="span">
  ![3D preview of the finished board](assets/images/hardware/pcb/joystick-hand-3d-viewer.jpg){ width="420" loading=lazy }
  <figcaption>KiCad's 3D viewer — the finished board with the switch model placed. You can see the gold traces, the header pads, and the silkscreen labels</figcaption>
</figure>

<figure markdown="span">
  ![Full KiCad workspace](assets/images/hardware/pcb/joystick-hand-pcb-full-workspace.jpg){ width="420" loading=lazy }
  <figcaption>The full workspace — schematic, layout, and 3D preview side by side during the design session</figcaption>
</figure>

</div>

### From screen to factory

The board went from KiCad to JLCPCB-ready in one session. Gerbers exported, BOM generated, pick-and-place file formatted. Five boards for a few dollars, shipped from Shenzhen. The switch gets placed by machine — I just solder the header pins when they arrive.

The STEP model of the finished board is imported directly into the FreeCAD assembly, where it sits in the cradle's 20 x 20 mm joystick pit with the switch body poking up through the cover's anchor pad into the thumbpiece.

<figure markdown="span">
  ![Joystick PCB in the FreeCAD assembly](assets/images/enclosure/comp-joystick-pcb-iso.png){ width="400" loading=lazy }
  <figcaption>The board as it appears in the 3D model — imported from the KiCad STEP export, positioned in the cradle pit</figcaption>
</figure>

[Joystick wiring guide :material-arrow-right:](docs/hardware/joystick-wiring.md){ .md-button }

---

## Current Phase

!!! info "Phase 2 — Firmware Foundation (C on Pico W)"
    Phase 1 (hardware + tooling) is complete. The unit is **fully soldered and battery-powered** — running off a 10440 Li-ion cell with USB-C charging via TP4056 confirmed working. Two enclosure variants available: **Solar** (with AK 62x36mm panel) and **NoSolar** (slimmer, USB-only).

    **Done:** Runtime rendering engine | 16 emotions | Body animations | Custom fat/lazy bodies | 823 quotes | C-faithful preview renderer | DevTool with firmware size estimation | **GPIO joystick input** | On-screen input indicator | **Soldered unit** | **Battery power** | **USB-C charging** | **NoSolar variant**

    **In Progress:** Custom PCB design — switched from RP2040 to **ESP32-S3-WROOM-1-N16R8** (WiFi+BLE, 16MB flash, 8MB PSRAM). 4-layer board (45x80mm, 27 components) designed in KiCad, ready for interactive routing and JLCPCB fabrication. **Hand-routed joystick breakout PCB** (K1-1506SN-01, 19.6x19.6mm) designed from scratch in KiCad 10 with gerbers and BOM ready for JLCPCB. **Full Board** all-in-one PCB design kicked off with component reference and KiCad import guide.

    **Next:** Order joystick PCB from JLCPCB | Complete ESP32 PCB routing and order boards | Game loop with state machine | Evaluate battery life

---

## Quick Links

<div class="grid cards" markdown>

-   :material-book-open-variant: **Docs**

    ---

    Hardware specs, wiring diagrams, setup guides, and code reference.

    [:octicons-arrow-right-24: Browse Docs](docs/index.md)

-   :material-post: **Blog**

    ---

    Build journal posts — from planning to a soldered, battery-powered unit.

    [:octicons-arrow-right-24: Read the Blog](blog/index.md)

-   :fontawesome-brands-discord: **Discord**

    ---

    Join the community server to ask questions and share your own build.

    [:octicons-arrow-right-24: Join Discord](community/discord.md)

-   :material-tools: **Dev Tools**

    ---

    DevTool GUI, setup CLI, and website dev CLI — built to support the workflow.

    [:octicons-arrow-right-24: Browse Tools](docs/tools/devtool.md)

-   :fontawesome-brands-patreon: **Patreon**

    ---

    Support the project and get early access to content and files.

    [:octicons-arrow-right-24: Support on Patreon](community/support.md)

-   :fontawesome-brands-github: **Source**

    ---

    All firmware, tools, and docs. 270+ AI prompts logged.

    [:octicons-arrow-right-24: GitHub Repo](https://github.com/rompasaurus/dilder)

</div>

---

## How This Project Works

The entire development process is public:

- **Every prompt** submitted to the AI assistant is logged in the [Prompt Log](prompts/index.md) — 270+ and counting
- **Every hardware decision** is documented in the [Docs](docs/index.md)
- **Every build step** is written up in the [Blog](blog/index.md)
- **Every drawing function** is verified pixel-by-pixel between C firmware and Python DevTool
- **All source files** are on [GitHub](https://github.com/rompasaurus/dilder)

This is learn-in-public taken to its logical extreme. No hidden steps, no "just trust me" — if it happened, it's documented.

---

<div style="text-align: center; opacity: 0.6; font-style: italic; margin-top: 2rem;">
Built with patience, a Pico W, and an unreasonable fondness for a plush octopus named Jamal.
</div>
