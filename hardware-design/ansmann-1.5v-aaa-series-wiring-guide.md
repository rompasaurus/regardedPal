# Wiring Guide: Ansmann 1.5V Li-Ion AAA Cells — Series Config for Pico 2 W

## Table of Contents

1. [Overview](#overview)
2. [Bill of Materials](#bill-of-materials)
3. [Series Wiring Diagram](#series-wiring-diagram)
4. [Battery Contact Recommendations](#battery-contact-recommendations)
5. [Wire Gauge Selection](#wire-gauge-selection)
6. [Step-by-Step Assembly](#step-by-step-assembly)
7. [Wire Routing Through the Cradle](#wire-routing-through-the-cradle)
8. [Safety Considerations](#safety-considerations)
9. [Charging the Ansmann Cells](#charging-the-ansmann-cells)
10. [Alternative: Raw 10440 Li-Ion Cells with TP4056](#alternative-raw-10440-li-ion-cells-with-tp4056)

---

## Overview

The Dilder virtual pet is powered by a Raspberry Pi Pico 2 W driving a Waveshare 2.13" e-ink display. This guide covers wiring two Ansmann 1.5V Li-Ion AAA cells in **series** to produce 3.0V, fed into the Pico W's VSYS pin (rated 1.8–5.5V).

**Critical distinction:** These Ansmann cells are *not* raw Li-Ion cells. Each cell contains an internal 3.7V lithium cell, a boost/buck converter, and USB-C charge circuitry. The output at the cell terminals is a regulated, constant 1.5V regardless of internal state of charge. This means:

- The TP4056 charge board **cannot** be used with these batteries — it expects a raw 3.7V cell on its BAT+/BAT- output.
- Two cells in series yield a steady 3.0V, well within the Pico W's VSYS range.
- Each cell charges individually via its own built-in USB-C port.

**Physical layout:** The 3D-printed cradle insert has two AAA bays running along the X axis at the ±Y edges, with the Pico 2 W seated in the center channel between them. The cradle plugs into a top cover; a base plate closes the bottom.

---

## Bill of Materials

| Item | Qty | Notes |
|------|-----|-------|
| Ansmann 1.5V Li-Ion AAA (USB-C, 500mAh) | 2 | Series pair |
| AAA battery spring contacts (see section 4) | 4 | 2 per bay (1 spring + 1 flat) |
| 26 AWG stranded silicone hook-up wire | ~15 cm | 3 runs: series link, VSYS, GND |
| 1N5817 Schottky diode (DO-41) | 1 | Optional reverse-polarity protection |
| 0.5A polyfuse (PPTC resettable) | 1 | Optional overcurrent protection |
| Heat-shrink tubing, 2mm dia | ~5 cm | Insulate solder joints |
| CA glue or 5-min epoxy | small amount | Secure contacts in cradle bays |

---

## Series Wiring Diagram

Orient the cells so Cell 1's positive nub faces Cell 2's negative end — this keeps the series link wire short across the center of the cradle.

```
                        SERIES WIRING LAYOUT
                     (view from above, base plate removed)

    -Y edge                    CENTER                    +Y edge
 +--------------+      +------------------+      +--------------+
 |              |      |                  |      |              |
 |   CELL 1    |      |    Pico 2 W      |      |   CELL 2    |
 |              |      |                  |      |              |
 |  (-)====(+) |      |  GND pin  VSYS   |      | (+)====(-) |
 |   |      |  |      |    |        |     |      |  |      |  |
 +----|------|--+      +----|--------|-----+      +--|------|--+
      |      |              |        |               |      |
      |      +--------------+--------+---------------+      |
      |           Series Link (Cell1+ to Cell2-)             |
      |                     |        |                       |
      +---------------------+        +-----------------------+
        GND wire                        VSYS wire
     (Cell1- to Pico GND)           (Cell2+ to Pico VSYS)
```

**Schematic (single-line):**

```
Cell 1 (-)  ----[GND wire]------>  Pico GND (pin 38)
Cell 1 (+)  ----[series wire]---->  Cell 2 (-)
Cell 2 (+)  ----[VSYS wire]----->  Pico VSYS (pin 39)

         Cell 1          Cell 2
     -|  1.5V  |+  -->  -|  1.5V  |+
     |         |          |         |
     |         +----------+         |
     |       series link            |
     |                              |
     +--- GND              VSYS ---+
          |                  |
          +--[ Pico 2 W ]---+
               3.0V supply
```

**With optional protection (recommended):**

```
Cell 2 (+) ---[polyfuse 0.5A]---[1N5817 diode]---> Pico VSYS (pin 39)
                                  anode   cathode
                                (band on cathode side, toward Pico)

Note: The 1N5817 drops ~0.3V → supply becomes ~2.7V.
      Still well above the Pico W's 1.8V minimum.
```

---

## Battery Contact Recommendations

### Option A: Bauhaus / Hardware Store (Easiest)

Walk into Bauhaus (or any German hardware store) and grab:

| Item | Where in store | What to do with it | Price |
|------|---------------|-------------------|-------|
| **2× single AAA battery holders** (Batteriehalter, 1x AAA, Goobay or no-name) | Electronics/hobby aisle | Pop out the spring (-) and flat (+) contacts, press-fit them into the cradle bays | €1–2 each |
| **Battery contact spring pack** (Batteriefederkontakte) | Near battery display | 4-pack of spring + flat contacts for AAA/AA cells, solder tabs included | €2–4 pack |
| **0.3mm brass strip** (Messingblech) | Metals/hobby metals section | Cut into 8×15mm tabs, bend into leaf-spring contacts | €3–5 per strip |

**The easiest option:** Buy 2 cheap single-AAA holders, pull the contacts out, and CA-glue them into the cradle's bay pockets.

### Option B: Online — Keystone Spring Contacts

| Part Number | Type | Description | Price (each) |
|-------------|------|-------------|--------------|
| Keystone 5225 | Negative (spring) | Coil spring, solder lug, AAA/AA | €0.30–0.50 |
| Keystone 5226 | Positive (flat) | Flat dimple contact, solder lug | €0.30–0.50 |
| Keystone 209 | Negative (spring) | Larger coil spring, wide solder tab | €0.40–0.60 |
| Keystone 210 | Positive (button) | Button contact, solder tab | €0.40–0.60 |

Available from Mouser, Digikey, or Reichelt.

### Option C: PCB-Mount AAA Holders (Embed Whole)

| Part Number | Description | Price |
|-------------|-------------|-------|
| Keystone 82 | Single AAA, PC pins | €0.80–1.20 |
| MPD BH411 | Single AAA, through-hole | €0.50–0.90 |

These can be embedded directly into the cradle if the bay dimensions are adjusted to fit the holder body.

### Mounting Contacts in the 3D-Printed Cradle

1. Design rectangular pockets (~6mm wide × 8mm tall × 3mm deep) at each end of each AAA bay
2. Spring (negative) contact goes at one end, flat (positive) contact at the other
3. The contact's solder lug should protrude through a slot in the cradle wall
4. Secure with a drop of CA glue or 5-minute epoxy
5. Let adhesive cure before soldering wires to the lugs

---

## Wire Gauge Selection

| Parameter | Value |
|-----------|-------|
| Peak current (WiFi TX burst) | ~250 mA |
| Typical current (e-ink refresh) | ~30–80 mA |
| Sleep/idle current | < 5 mA |
| Longest wire run | ~8 cm |

**Use 26 AWG stranded silicone-insulated wire.** At 250 mA over 8 cm, voltage drop is only 2.7 mV — negligible. Silicone insulation tolerates soldering heat and stays flexible in the tight cradle space. 28 AWG also works.

---

## Step-by-Step Assembly

### Step 1: Prepare Contacts

1. If using battery holders from Bauhaus: pry out the spring and flat contacts with a small flathead screwdriver.
2. Test-fit each contact in the cradle bay pockets.
3. Glue in place with CA glue. Let cure 5 minutes.

### Step 2: Cut and Strip Wires

| Wire | Color | Length | Connects |
|------|-------|--------|----------|
| GND | Black | ~7 cm | Cell 1 (−) spring → Pico GND (pin 38) |
| Series link | Yellow | ~5 cm | Cell 1 (+) flat → Cell 2 (−) spring |
| VSYS | Red | ~7 cm | Cell 2 (+) flat → Pico VSYS (pin 39) |

Strip 3–4 mm from each end.

### Step 3: Tin Everything

1. Flux each contact solder lug.
2. Tin each lug and each wire end at 350–370°C with a chisel tip.

### Step 4: Solder Wires to Contacts

1. **GND (black):** One end to Cell 1 negative spring lug. Other end free.
2. **Series link (yellow):** One end to Cell 1 positive flat lug, other end to Cell 2 negative spring lug.
3. **VSYS (red):** One end to Cell 2 positive flat lug. Other end free.
4. Apply heat-shrink over each joint.

### Step 5: Optional Protection Components

1. **Polyfuse** (Bourns MF-R050): solder inline on the red VSYS wire.
2. **Schottky diode** (1N5817): solder inline, band/cathode toward the Pico.

### Step 6: Solder to Pico 2 W

1. **GND (black):** Solder to pin 38 (GND) — bottom-right, adjacent to VSYS.
2. **VSYS (red):** Solder to pin 39 (VSYS) — system power input.
3. If headers are installed, solder to the underside of the pin. If no headers, solder directly to the through-hole pad.

### Step 7: Test Before Closing

1. Insert both Ansmann cells (check polarity).
2. Measure across VSYS and GND — expect **2.9–3.1V**.
3. Power on the Pico — LED should light, firmware should boot.
4. If 0V or negative, a cell is backwards.

---

## Wire Routing Through the Cradle

```
    CROSS-SECTION VIEW (looking along X axis)

    +-------------------------------------------------------+
    |                    TOP COVER                           |
    +-------------------------------------------------------+
    |  Cell 1 bay  |  wire channel  |  Cell 2 bay           |
    |  (-Y side)   |  (center)      |  (+Y side)            |
    |              |                |                        |
    |  [spring] ===|=== GND wire ===|======================  |
    |              |                |                        |
    |  [flat]  ====|= series link ==|=== [spring]            |
    |              |                |                        |
    |              |  VSYS wire ====|=== [flat]              |
    |              |  +----------+  |                        |
    |              |  | Pico 2 W |  |                        |
    |              |  +----------+  |                        |
    +-------------------------------------------------------+
    |                   BASE PLATE                           |
    +-------------------------------------------------------+
```

- Run wires through the 3 mm cable pass-through at the bottom of the connecting block.
- Keep GND and VSYS on opposite sides to avoid shorts.
- Tack wires down with a small dab of hot glue at each end.
- The series link crosses under/beside the Pico — keep it flat against the cradle floor.

---

## Safety Considerations

### Reverse Cell Insertion

| Scenario | Result | Risk |
|----------|--------|------|
| One cell reversed | 0V net (1.5V − 1.5V), Pico won't power on | **Low** — no damage |
| Both cells reversed | −3.0V on VSYS (reversed polarity) | **High** — can destroy Pico |
| One cell missing | Open circuit, no current | **None** |

**Mitigations:**
1. **Schottky diode on VSYS** (recommended) — blocks reverse current, costs ~0.3V drop.
2. **Polarity markings** on the cradle bays — mark + and − clearly.
3. **Asymmetric bay design** — the Ansmann cells have a USB-C port on one end that's slightly wider. Use this as a keying feature.

### Over-discharge

The Ansmann cells have built-in discharge cutoff. When the internal cell drops too low, the boost converter shuts off and output goes to 0V. No external low-voltage cutoff needed.

### USB + Battery Simultaneously

The Pico 2 W has an onboard Schottky diode between VBUS (USB 5V) and VSYS. When USB is connected, VBUS (~4.7V) is higher than the battery (3.0V), so the battery is effectively disconnected. Safe.

---

## Charging the Ansmann Cells

**Each cell charges via its own built-in USB-C port** under a small cap at the negative end.

### In-Place Charging (if ports are accessible)

If the cradle design has cutouts at the battery bay ends exposing the USB-C ports:
- Plug a USB-C cable into each cell
- The cell outputs 1.5V while charging (pass-through) — Pico stays powered
- Charge time: ~1.5–2 hours per cell

### Remove-to-Charge

If the cradle encloses the cells fully:
- Remove the base plate
- Slide cells out of the bays
- Charge externally with any USB-C cable + 5V source

**The TP4056 board CANNOT charge these cells.** It would try to push 4.2V into the cell's 1.5V output stage, which is not designed for external voltage input and could damage the cell's internal circuitry.

---

## Alternative: Raw 10440 Li-Ion Cells with TP4056

If you want to use the TP4056 charge board, substitute raw 10440 Li-Ion cells (AAA form factor, 3.7V nominal, ~350mAh).

| Parameter | Ansmann 1.5V AAA | Raw 10440 |
|-----------|------------------|-----------|
| Output voltage | Constant 1.5V | 3.0–4.2V (varies) |
| Charging | Built-in USB-C per cell | TP4056 or external |
| Wiring | 2 in **series** = 3.0V | 2 in **parallel** = 3.7V |
| VSYS feed | 3.0V constant | 3.0–4.2V variable |

### 10440 Parallel Wiring

Wire both positives together, both negatives together → single 3.7V pack. Connect to TP4056 BAT+/BAT−. Derate TP4056 R_prog to ~3.4 kΩ for 350 mA charge current.

```
Cell A (+) ---+--- Cell B (+) ---> TP4056 BAT+ ---> VSYS
Cell A (-) ---+--- Cell B (-) ---> TP4056 BAT- ---> GND
```

**Never wire 10440s in series** — 2S = 7.4V nominal, exceeds the Pico W's 5.5V VSYS maximum.

---

*Guide authored 2026-04-25 as part of the Dilder Rev 2 enclosure design.*
