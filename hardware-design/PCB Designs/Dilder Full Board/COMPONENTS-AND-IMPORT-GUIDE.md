# Dilder Full Board — Component References & KiCad Import Guide

This document is the working reference for the all-in-one Dilder PCB. It does two things:

1. **Lists every component that the FreeCAD assembly macro physically places** in the enclosure — i.e. the actual modules/boards/parts that need a footprint and net on the new PCB.
2. **Walks through how to import** existing schematics, symbols, footprints, and sub-circuits into the new KiCad project that will live alongside this file (`Dilder Full Board/dilder-full-board.kicad_pro`).

> **Source of truth for the component list:**
> `hardware-design/freecad-mk2/dilder_rev2_mk2.FCMacro` — every body the macro creates is a real part that has to land on the PCB or wire to it.
>
> All paths below are relative to the repo root (`/home/rompasaurus/CodingProjects/Dilder/`).
> All reference projects are already cloned locally — no internet needed to open them in KiCad.

---

## 1. Components Modeled in the FreeCAD Macro

These are the parts whose physical bodies the macro instantiates. The macro is the authoritative dimensional model — anything in here is mechanically committed to the enclosure and must therefore be represented on the PCB (either as a footprint, a wire-out connector, or both).

### 1.1 Compute / module boards

| # | Body name in macro | Real part | Macro line | Approx. dims | How it joins the board |
|---|---------------------|-----------|------------|--------------|------------------------|
| 1 | `add_pico_with_headers` | **Raspberry Pi Pico 2 W** (RP2350 + CYW43439) | L1219 | 51 × 21 × 1.0 mm, 2×20 pin headers | Through-hole castellated module — drops onto a 2×20 header on the PCB |
| 2 | `JoystickPCB` (imported STEP) | **Hand-routed joystick breakout** with K1-1506SN-01 5-way switch | L1373 | 19.6 × 19.6 × 1.5 mm | Sub-board on flying leads / pin header into the main board |

### 1.2 Power-path modules

| # | Body name | Real part | Macro line | Approx. dims | How it joins the board |
|---|-----------|-----------|------------|--------------|------------------------|
| 3 | `TP4056_Module` | **TP4056 USB-C LiPo charger module** (off-the-shelf, USB-C input variant) | L1597 | 28 × 17 × 1.6 mm PCB + USB-C bump (~9 × 7 × 3.4) | Stand-alone module on flying leads (BAT+ / BAT- / OUT+ / OUT-) |
| 4 | `AAA_Battery_1`, `AAA_Battery_2` (+ `_PosTerm`) | **2× 1.5 V Li-Ion AAA / 10440 cells** | L1556 | 10.5 mm dia × 41.5 mm length | Wired in **parallel** through battery clips → TP4056 BAT+/BAT- |
| 5 | `BatteryClip_*` (4 plates + 2 springs + 2 bumps) | **Swpeet 7 × 7 mm sheet-metal AAA contact kit** | inside `add_peripherals` | 7 × 7 × 0.5 mm plate, 5 mm coil spring, 4 mm bump | Two POS plates → bus → TP4056 BAT+; two NEG plates → bus → TP4056 BAT- |
| 6 | `Solar_Frame`, `Solar_Cells` (+ `Solar_Wire_Plus`, `Solar_Wire_Minus`) | **AK 62 × 36 mm monocrystalline solar panel** | L1897 | 62 × 36 × 2.0 mm + 2× 1 mm OD lead wires | 2-wire input — typically through a Schottky diode to TP4056 IN+ |

### 1.3 Sensor modules

| # | Body name | Real part | Macro line | Approx. dims | How it joins the board |
|---|-----------|-----------|------------|--------------|------------------------|
| 7 | `IMU_Module` | **GY-6500 / MPU-6500 6-axis IMU breakout** | L1841 | 25 × 15 × 1.0 mm PCB, 8-pin 2.54 mm header | I²C: VCC, GND, SDA, SCL (+ INT optional) |

> The macro currently models the **MPU-6500** (GY-6500 module). The v0.5 sensor expansion to add **AHT20** (temp/humidity) and **BH1750** (ambient light) on the same I²C bus is **not yet modeled in the macro**. When those modules get FreeCAD bodies, add them here. For the PCB, they share the same I²C net as the IMU — single shared SDA/SCL pull-up pair on the bus, no per-module pull-ups.

### 1.4 Output / actuator modules

| # | Body name | Real part | Macro line | Approx. dims | How it joins the board |
|---|-----------|-----------|------------|--------------|------------------------|
| 8 | `Piezo_Brass`, `Piezo_Ceramic` | **20 mm piezo disc** (FT-20T / YOUMILE JK-YM-297A) | L1805 | Ø20 × 0.20 mm brass + Ø15 × 0.22 mm ceramic | 2-wire passive — solder pads to a Pico GPIO + GND (PWM tone) |
| 9 | `Thumbpiece` | **3D-printed snap cap** over joystick actuator | L1465 | inside cover's 12 mm hole | **Mechanical only** — no PCB net |

### 1.5 Display

| # | Body name | Real part | Macro line | Approx. dims | How it joins the board |
|---|-----------|-----------|------------|--------------|------------------------|
| 10 | `EInkDisplay_Module`, `EInkDisplay_Panel` | **Waveshare Pico-ePaper-2.13** (V3/V4 HAT) | L1635 | 65.2 × 30 × 3.0 mm; 48 × 22 mm active area | 8-pin 2.54 mm header on the HAT — connects to Pico SPI (DIN, CLK, CS, DC, RST, BUSY, + VCC, GND) |

### 1.6 Mechanical / enclosure (no PCB representation)

| Body name | Macro line | Notes |
|-----------|------------|-------|
| `BasePlate`, `AAACradle`, `TopCover` | L283 / L615 / L933 | The 3D-printed enclosure shells — pillar/screw locations from these constrain the PCB outline. |

---

## 2. Net-Level Summary (what the PCB has to carry)

Reading the macro plus `BOM.md` GPIO table, the consolidated "Dilder Full Board" needs to provide:

| Bus / rail | Members | Notes |
|-----------|---------|-------|
| **VBAT (≈3.0–4.2 V)** | TP4056 BAT+ ← 2× AAA in parallel; solar IN+ via Schottky | Floats with cell state |
| **VBUS (5 V)** | USB-C on TP4056 module; routed to Pico VBUS | Charging path |
| **3V3** | Pico 3V3 OUT → IMU VCC, e-paper VCC, sensors | From Pico's onboard regulator (no AMS1117 needed when using the Pico module) |
| **GND** | Common ground, star-tied at Pico GND | |
| **I²C** | SDA, SCL → MPU-6500, AHT20 (planned), BH1750 (planned) | One shared 10 kΩ pull-up pair |
| **SPI** | SCK, MOSI + CS, DC, RST, BUSY → e-paper HAT | Per Pico-ePaper-2.13 wiring |
| **Joystick** | 5× GPIO with internal pull-ups → SW1 (UP/DOWN/LEFT/RIGHT/CENTER) → GND | From the joystick sub-board |
| **Piezo** | 1× GPIO (PWM-capable) + GND | Direct drive of the disc |

> **Important asymmetry vs. `BOM.md` v0.3:** the FreeCAD macro models the system around a **Raspberry Pi Pico 2 W module** (a pre-made board you solder onto headers), not around a bare **ESP32-S3-WROOM-1** soldered to the PCB. That changes the PCB role from "carry the MCU + flash + crystal + USB-C" to "carry headers + power glue + connectors". Decide which the Full Board targets before importing schematics — §2 of `pcb-design-plan.md` and §3 of this guide assume **the macro's view (Pico 2 W on headers)**. If you switch to the bare ESP32-S3, the import sources for §3 change accordingly (use the Ducky/OLIMEX/AeonLabs references instead of the Pico ones).

---

## 3. Reference Design Cross-Map

For every macro-modeled component, the table tells you **which already-cloned project to open** and **where to look in it**. These are the schematics you will pull circuits from when wiring `dilder-full-board.kicad_sch`.

Open any of these in KiCad with `kicad <project>.kicad_pro`.

### 3.1 Raspberry Pi Pico 2 W on headers (component #1)

| Project | KiCad project file | What to study |
|---------|--------------------|---------------|
| Reverse-engineered Pico WH | `hardware-design/reference-boards/rp2040-pico-usbc/KiCad Projects/Pico WH - No License/Pico WH.kicad_pro` | Closest schematic to the Pico 2 W's wireless module — full RP2040 + CYW43439 wiring, USB-C, power path. |
| Pico 2 C reverse-engineered | `hardware-design/reference-boards/rp2040-pico-usbc/KiCad Projects/Pico 2 C/Pico 2 C.kicad_pro` | RP2350 (Pico 2) schematic — the MCU on your module. Useful for reading 3V3/VSYS/VBUS interaction even though you're not laying out the chip. |
| Official Pico 2 STEP | `hardware-design/reference-boards/raspberry-pi-pico-2/RaspberryPi-Pico-2.step` | The exact mechanical model the macro imports — confirms the 2×20 header pitch (2.54 mm) and pin 1 location for the footprint. |
| RP2040 design guide | `hardware-design/reference-boards/rp2040-designguide/PCB/RP2040-Guide.kicad_pro` | Headed Pico-on-header carrier patterns. |

> **What you actually place on the PCB for component #1:** a **Raspberry Pi Pico 2×20 castellated/THT footprint** (2.54 mm pitch, 51 × 21 mm outline) — not the bare RP2350 chip. KiCad's `MCU_Module` library has a `Pico` symbol already; the matching footprint is `RPi_Pico:RPi_Pico_SMD_TH` from the JLCPCB libs registered by `setup-kicad-jlcpcb.py`.

### 3.2 Joystick sub-board (component #2)

| Project | KiCad project file | What to study |
|---------|--------------------|---------------|
| Existing joystick PCB | `hardware-design/PCB Designs/joystick-pcb-by-hand/JoystickBoardDilder/JoystickBoardDilder.kicad_pro` | **Authoritative — your own production sub-board.** SW1 footprint, K1-1506SN-01 net mapping, pin header pinout. The macro imports the STEP from this exact project. |
| Lilka console | `hardware-design/examples/02-lilka-console/hardware/v2/main.kicad_sch` | D-pad debounce + 5-direction button topology if you want to compare. |

> Decide whether to **keep the joystick as a separate sub-board** (current macro behavior — ribbon/header to main board) or **merge SW1 onto the Full Board PCB**. If merging: copy the SW1 footprint and net layout from the joystick project's `.pretty` library and `.kicad_sch`.

### 3.3 TP4056 USB-C charger module (component #3)

The macro models the **off-the-shelf TP4056 module**, which means the Full Board only has to expose 4 pads (BAT+, BAT-, OUT+, OUT-) and a wire harness. But if you want to fold the TP4056 onto the Full Board itself, these are the references:

| Project | KiCad project file | What to study |
|---------|--------------------|---------------|
| BitwiseAjeet TP4056 | `hardware-design/examples/09-bitwiseajeet-tp4056/ESP32 PCB.kicad_pro` | **Canonical TP4056 schematic.** Full IC + DW01A + FS8205A + status LEDs + PROG resistor. |
| KLP-5e sensor board | `hardware-design/examples/10-klp5e-sensor-board/KiCad project/ESP32 sensor board.kicad_pro` | TP4056 in a hierarchical "Power" sheet — easy to lift wholesale. |
| Ducky e-paper | `hardware-design/reference-boards/esp32s3-ducky-epaper/hardware.kicad_sch` | TP4056 next to an MCU and an e-ink connector — the same neighborhood as Dilder. |

### 3.4 AAA cells + clip kit (components #4, #5)

These are **passive** from the PCB's view — just two solder pads (BAT_POS, BAT_NEG) tied to flying leads from the cradle's spring contacts.

| Project | What to look at |
|---------|----------------|
| `reference-boards/opentama-virtual-pet/OpenTama.kicad_sch` | Same product class (handheld virtual pet); shows JST/spring battery input on the PCB side. |

For the symbol itself, use **`Connector_Generic:Conn_01x02`** (or `Conn_01x02_Pin`) from KiCad's stock library and label the pins `BAT+ / BAT-`. No need for a battery symbol — the cells are off-board.

### 3.5 Solar panel (component #6)

Two pads (`SOLAR+`, `SOLAR-`) feeding TP4056 IN+ through a Schottky diode (the `SS34` from BOM.md, refdes D1).

| Project | What to look at |
|---------|----------------|
| `examples/09-bitwiseajeet-tp4056/ESP32 PCB.kicad_sch` | Shows the canonical "USB-or-alt-source → Schottky → charger IN" gating that you'll mirror for the solar input. |

Footprint: same `Conn_01x02` for the lead pads. Add **D? — `Diode:SS34`** in the `Diode_SMD:D_SMA` footprint between SOLAR+ and the TP4056 module's IN+ pad.

### 3.6 IMU module — GY-6500 / MPU-6500 (component #7)

Treat the GY-6500 as an **off-board breakout** connected by an 8-pin 2.54 mm header. The Full Board only needs the header footprint and the I²C/power nets.

| Project | KiCad project file | What to study |
|---------|--------------------|---------------|
| BitwiseAjeet TP4056 sensors | `hardware-design/examples/09-bitwiseajeet-tp4056/sensors.kicad_sch` | I²C accelerometer wiring with shared bus pull-ups. |
| KLP-5e sensors sheet | `hardware-design/examples/10-klp5e-sensor-board/KiCad project/sensors.kicad_sch` | Hierarchical "Sensors" sheet — same architectural pattern recommended for Dilder. |

If you later **promote the IMU onto the Full Board** as a bare LIS2DH12TR (per `BOM.md` v0.5), come back here and add a row pointing to wherever LGA-12 footprints live in the JLCPCB library.

### 3.7 Piezo disc (component #8)

A 2-pad passive — fully described by `Connector_Generic:Conn_01x02` on the PCB, plus optionally a transistor driver if you don't trust the Pico GPIO to source enough current.

| Project | What to look at |
|---------|----------------|
| `examples/02-lilka-console/hardware/v2/main.kicad_sch` | "Audio" section — direct GPIO-to-piezo driver and a simple 2N7002 transistor variant. Pick one based on volume needs. |

### 3.8 Waveshare Pico-ePaper-2.13 HAT (component #10)

The HAT plugs into the Pico's 2×20 header itself, so on the **Full Board** the e-paper is *not a separate connector* — it sits on top of the Pico header you already placed for component #1. The HAT mapping is:

| Pico GPIO | HAT signal | Footprint pin (on Pico header) |
|-----------|-----------|-------------------------------|
| GP11 | EPD_RST | Pin 15 |
| GP12 | EPD_BUSY | Pin 16 |
| GP8 | EPD_DC | Pin 11 |
| GP9 | EPD_CS | Pin 12 |
| GP10 | EPD_CLK (SCK) | Pin 14 |
| GP11 already, sometimes GP12 | EPD_MOSI | Pin 19 (varies by HAT rev) |

If you'd rather **break the e-paper out via the 8-pin JST-SH header** (per `BOM.md`), drop in the same `Conn_01x08` footprint near the cover pocket.

| Project | KiCad project file | What to study |
|---------|--------------------|---------------|
| Ducky e-paper | `hardware-design/reference-boards/esp32s3-ducky-epaper/hardware.kicad_sch` | Full ESP32-S3 → e-paper SPI + control-line wiring. Pin assignments differ but the topology transfers 1:1 to a Pico. |
| WhirlingBits S3 platform | `hardware-design/examples/07-whirlingbits-s3-platform/` | Hierarchical "Display" sheet with e-paper. |
| PocketMage PDA | `hardware-design/examples/01-pocketmage-pda/Docs/Documents & Advanced/PCB/V3.3/einkPDA_screen/einkPDA_screen.kicad_pro` | Production-grade e-ink interface. |

---

## 4. Importing Existing Designs into the Dilder Full Board Project

KiCad gives you **four** ways to bring outside content into a project. Pick the right one for the task; mixing them is normal.

| Goal | Use this |
|------|----------|
| Re-use a *complete sub-circuit* (e.g. the whole TP4056 charger block) as a separate page | **Append Schematic** (§4.2) |
| Drop one as a *hierarchical sub-sheet* with named net ties | **Add Hierarchical Sheet → existing file** (§4.3) |
| Cherry-pick *individual components and wires* | **Copy/paste between schematics** (§4.4) |
| Re-use a *symbol/footprint* without its circuit | **Add libraries to project tables** (§4.5) |

> All four require KiCad 7+ (the repo standardised on KiCad 10.0; see `hardware-design/pcb-design-plan.md`). When opening a v6 reference project, KiCad will offer to upgrade — say yes; an `*-bak` of the original is written automatically.

### 4.1 First — set up the new project

The skeleton project for this folder doesn't exist yet. Create it manually in KiCad:

1. **File → New Project…** → save as
   `hardware-design/PCB Designs/Dilder Full Board/dilder-full-board.kicad_pro`.
   This produces `dilder-full-board.kicad_sch` and `dilder-full-board.kicad_pcb`.
2. Confirm the JLCPCB libraries from the existing project register here too:
   **Preferences → Manage Symbol Libraries → Project Specific Libraries**.
   If empty, copy the entries from
   `hardware-design/Board Design kicad/sym-lib-table` and `fp-lib-table` into the new project (or add them at the *Global* tab so every project sees them).
3. Open the schematic editor (Ctrl+E) and save once so KiCad creates an empty sheet you can append to.

### 4.2 Append Schematic — copy a whole sheet's contents

Best for: pulling in the *Power* page of a reference design wholesale, then editing the labels.

1. In the schematic editor, **File → Append Schematic Sheet Content…**
2. Pick the source `.kicad_sch` (e.g. `examples/09-bitwiseajeet-tp4056/ESP32 PCB.kicad_sch`).
3. KiCad places every symbol, wire, label, and net tie at your cursor. You drag once, click to drop.
4. **What is preserved:** all wiring, net labels, hierarchical labels, component values, and references to symbols *if* the source library is reachable.
5. **What can break:** if the source uses a custom symbol library not added to your project, those symbols appear as placeholders ("???"). Fix by adding the library — see §4.5 — then re-link with **Tools → Edit Symbol Library Links**.
6. Renumber: **Tools → Annotate Schematic → Reset existing annotations** so you don't collide with the rest of your sheet.

### 4.3 Hierarchical sub-sheet — link a whole project file

Best for: keeping the reference circuit in its own page (e.g., "USB.kicad_sch") and exposing only named ports (VBUS, D+, D-, GND) to the parent.

1. In the schematic editor, **Place → Add Hierarchical Sheet** (or press `S`).
2. Drag a rectangle. In the dialog, set **File name** to a path inside this folder, e.g. `usb.kicad_sch`. Click OK; KiCad creates the file.
3. To populate it from a reference, *open the new empty `usb.kicad_sch`* and use **Append Schematic** (§4.2) to dump in the USB section of the reference design.
4. Back on the parent sheet, double-click the sub-sheet and run **Place → Hierarchical Label** for each pin you want to expose. The parent then drives those nets via matching hierarchical labels.

> **Tip for Dilder Full Board:** organise the schematic as five sub-sheets that mirror the macro sections — `pico.kicad_sch`, `power.kicad_sch` (TP4056 + battery + solar), `sensors.kicad_sch` (IMU + future AHT20/BH1750), `display.kicad_sch` (e-paper header), `io.kicad_sch` (joystick header + piezo). Project 10 (`klp5e-sensor-board`) is the canonical example of this style.

### 4.4 Copy/paste individual circuits

Best for: stealing just the TP4056 charger plus its DW01A/FS8205A from a reference, leaving the rest behind.

1. Open the source schematic in **a second KiCad window** (you can run two `eeschema` instances on the same machine).
2. Drag-select the components and wires you want, **Edit → Copy** (Ctrl+C).
3. Switch to the Dilder Full Board schematic, paste (Ctrl+V).
4. **Verify nets:** any *local* labels are pasted as-is. Any *hierarchical* labels not present in the destination become orphaned — convert them to local labels or wire them through.
5. Re-annotate with **Tools → Annotate Schematic** to renumber refdesignators.
6. **Footprints:** copy/paste preserves the *footprint assignment string* (e.g. `Package_SO:SOIC-8`). If the destination project doesn't have that footprint library, the assignment is kept but rendering shows a cross. Add the library (§4.5) or reassign with the **Footprint Assignment Tool**.

### 4.5 Bring in symbols and footprints (libraries only)

Best for: the case where you want the *part* but will draw the wiring yourself — typical for the Pico header, the e-paper header, and the joystick sub-board connector.

1. **Symbols** — Preferences → **Manage Symbol Libraries**. On the *Project Specific* tab, click + and point at any `.kicad_sym` file in the reference. Examples:
   - `reference-boards/rp2040-pico-usbc/.../Pico WH/` for the Pico WH symbol if you want a labelled GPIO header instead of a generic 2×20 connector.
   - `examples/09-bitwiseajeet-tp4056/libraries/` for TP4056, DW01A, FS8205A symbols.
   - `reference-boards/espressif-kicad-libs/symbols/` if you ever switch to the ESP32-S3 path.
2. **Footprints** — Preferences → **Manage Footprint Libraries**. Add any `.pretty` directory (KiCad treats it as a library):
   - `hardware-design/PCB Designs/joystick-pcb-by-hand/JoystickBoardDilder/JoystickBoardDilder.pretty` for the SKRHABE010 joystick footprint **and** the K1-1506SN-01 footprint your STEP export already uses.
   - Stock KiCad libraries are usually enough for the Pico header (`RPi_Pico:RPi_Pico_SMD_TH`), 2-pin/8-pin JST connectors, 0402/0805 passives, and SS34.
3. **3D models** — they live next to the footprints. KiCad finds them automatically if the `.kicad_mod` references a relative path; absolute paths are rewritten on first save.

> **JLCPCB/LCSC matching**: when you bring in a symbol, immediately set its **LCSC** field to the part number from the BOM (`hardware-design/BOM.md`). The `kicad-jlcpcb-tools` plugin (already installed per `pcb-design-plan.md` Phase 1) reads that field when generating the BOM/CPL output.

### 4.6 Importing the PCB layout (rare, but possible)

Footprint placement and routing usually do not transfer cleanly between board outlines, so most boards are routed from scratch. If you do want to copy a layout block:

1. Open the reference `.kicad_pcb`, drag-select the area, **Edit → Copy**.
2. In the Dilder Full Board PCB editor, **Edit → Paste Special** (Ctrl+Shift+V) to paste with absolute coordinates, or plain paste at cursor.
3. Re-run **Tools → Update PCB from Schematic** afterwards so refs match.

For Dilder specifically, the *footprints* and *net assignments* should come from your imported schematic; the *placement* should be hand-drawn against the macro's enclosure constraints — pillar XY, USB-C cutout XY, joystick pit XY, e-paper pocket XY all come straight from `setup_spreadsheet()` in the macro.

---

## 5. Suggested Workflow for the Dilder Full Board

Order the work so the easiest, highest-confidence parts go first; the IC-level decisions (whether to fold TP4056 onto the PCB) come last.

1. **Create the project skeleton** (§4.1).
2. **Set up libraries** — add the joystick `.pretty` folder and confirm `RPi_Pico:RPi_Pico_SMD_TH`, `Connector_JST:JST_PH_*`, and `Connector_JST_SH` resolve (§4.5).
3. **Build sub-sheets empty:** `pico.kicad_sch`, `power.kicad_sch`, `sensors.kicad_sch`, `display.kicad_sch`, `io.kicad_sch` (§4.3).
4. **Pico sheet** — drop in a Pico symbol (or a labelled 2×20 header) and label every GPIO per the table in `BOM.md` §"GPIO Pin Assignment". This sheet becomes the spine that the others tie into via hierarchical labels (`SDA`, `SCL`, `SPI_SCK`, `EPD_*`, `JOY_*`, `PIEZO`, `3V3`, `GND`, `VBUS`, `VBAT`).
5. **Power sheet** — start with two pads each for `BAT+/BAT-`, `OUT+/OUT-`, `SOLAR+/SOLAR-`, plus a Schottky on the solar input. If folding the TP4056 onto the board, Append from `examples/09-bitwiseajeet-tp4056/ESP32 PCB.kicad_sch` (§4.2) and strip the ESP32-C3 portion.
6. **Sensors sheet** — placeholder 8-pin header for the GY-6500 module. Wire VCC/GND/SDA/SCL/INT to hierarchical labels. Add stub headers for AHT20 and BH1750 on the same I²C net so v0.5 ports drop in without rework. Single shared 10 kΩ pull-up pair (R4/R5) on the bus.
7. **Display sheet** — either route the Pico header pins through to a 2×20 stack-through (HAT mounts on top — simplest, matches the macro), **or** add an 8-pin JST-SH for the loose e-paper header per `BOM.md`. Reference the Ducky board for SPI line ordering.
8. **I/O sheet** — joystick: place the K1-1506SN-01 footprint from the `.pretty` library directly (5 pins to GPIO + 1 to GND). Piezo: 2-pin connector for the disc leads.
9. **Tie sub-sheets to the parent** with hierarchical labels matching the names from step 4.
10. **ERC** clean → **Update PCB from Schematic** → board outline matches the macro's enclosure footprint (`enc_x = 96.9 mm`, `enc_y = 46.0 mm` per `setup_spreadsheet`).

---

## 6. Quick Reference: paths

```
hardware-design/
├── BOM.md                              ← parts list (v0.3 + v0.5 sensor expansion)
├── pcb-design-plan.md                  ← phase plan, GPIO table
├── freecad-mk2/
│   └── dilder_rev2_mk2.FCMacro         ← ★ source of truth for components
├── reference-boards/
│   ├── raspberry-pi-pico-2/            ← Pico 2 STEP (used by macro)
│   ├── rp2040-pico-usbc/               ← Pico WH/Pico 2 KiCad schematics
│   ├── esp32s3-ducky-epaper/           ← e-paper SPI reference
│   └── opentama-virtual-pet/           ← same product class (handheld)
├── examples/
│   ├── INDEX.md                        ← tier-ranked overview
│   ├── 02-lilka-console/               ← D-pad + piezo audio refs
│   ├── 09-bitwiseajeet-tp4056/         ← ★ TP4056 + DW01A/FS8205A + sensors
│   └── 10-klp5e-sensor-board/          ← hierarchical-sheet style
└── PCB Designs/
    ├── joystick-pcb-by-hand/           ← K1-1506SN-01 footprint + STEP
    └── Dilder Full Board/              ← (you are here)
        └── dilder-full-board.kicad_pro (to be created — §4.1)
```
