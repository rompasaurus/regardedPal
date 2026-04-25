# Rev 2 — Battery Cradle → Charger → Pico W Wiring Plan

Cradle: `aaa-cradle-insert-v1.scad` — 2 bays, AAA-sized (10.5 mm Ø × 44.5 mm),
designed for **2× 10440 Li-ion cells in parallel**. This document plans the
electrical buildout and answers the "can I use alkaline AAAs right now?"
question.

---

## TL;DR

- The cradle is wired **parallel only** (per `project_battery_redesign_10440`).
  Parallel = same voltage, doubled capacity. Series would output ~7.4 V and
  destroy the TP4056.
- **Do not put alkaline or NiMH AAAs into this cradle.** The TP4056 is a
  single-cell Li-ion/LiPo charger (CC/CV to 4.2 V). It will happily push
  4.2 V into a 1.5 V alkaline → leak, vent, or fire. NiMH float voltage is
  also wrong (~1.4 V/cell).
- For a **bench bring-up before the 10440s arrive**, the safe options are:
  1. Power the Pico W from USB only (skip the battery rail entirely). ✅ easiest
  2. Use a **separate 3×AAA series holder** (4.5 V alkaline / 3.6 V NiMH) wired
     **directly to Pico VSYS via a Schottky diode**, bypassing the TP4056.
     The cradle insert is not used in this mode.

---

## Components

### Battery / charge / protect chain (final config — Li-ion 10440)

| # | Part | Purpose | Notes |
|---|------|---------|-------|
| 1 | 2× **10440 Li-ion cell**, button-top, protected | Energy source | Match same brand + batch when paralleling. ~350 mAh each → ~700 mAh in parallel. |
| 2 | 2× AAA spring contact set (positive button + negative spring) **or** solder tabs | Cell-to-circuit contact | Spring clips for swappable cells; solder tabs for permanent. Cradle has 2 mm contact space per end. |
| 3 | **TP4056 module with DW01A protection** (USB-C variant preferred) | CC/CV charge from USB + over-discharge / over-current cutoff on the load side | Already in BOM. Use the variant that has both `IN+/IN-`, `B+/B-`, `OUT+/OUT-` pads (1A2B2O layout) — you want the protected OUT rail feeding the Pico, not B+ direct. |
| 4 | **JST-PH 2.0 mm pigtail** (pre-crimped) | Cradle ↔ TP4056 `B+/B-` | Standard connector for this project. |
| 5 | **Schottky diode**, 1A, ~0.3 V Vf (e.g. SS14 / 1N5817) | Prevents Pico VSYS rail from back-feeding into the battery and lets a USB power source on the Pico co-exist | Anode → TP4056 `OUT+`, cathode → Pico `VSYS` (pin 39). |
| 6 | 22 AWG silicone wire, red/black | Cell tabs ↔ JST, OUT ↔ Pico | Silicone is flexible and won't crack inside the enclosure. |
| 7 | Heatshrink, 2 mm + 3 mm | Insulate every solder joint | — |
| 8 | Slide switch, SPST (e.g. SS-12D00G3) **or** push-button latching | Hard cutoff between TP4056 OUT+ and Pico VSYS | Optional but recommended — TP4056+DW01A doesn't fully isolate when idle. |

### Pico W side

| # | Part | Purpose | Notes |
|---|------|---------|-------|
| 9 | Raspberry Pi **Pico W** | MCU | Already on hand. |
| 10 | (Optional) 1× 10 µF ceramic + 1× 100 µF electrolytic across VSYS/GND | Decouples the load when the radio TX'es | Helps if you see brownouts during Wi-Fi joins on a depleted cell. |

### Bench-only "use AAAs right now" path (skip cradle + TP4056)

| # | Part | Purpose | Notes |
|---|------|---------|-------|
| B1 | **3×AAA series holder with switch + leads** | 3 × 1.5 V alkaline = 4.5 V, in Pico VSYS range (1.8–5.5 V) | Do NOT use 4×AAA alkaline (6.0 V > VSYS max). 4×NiMH = 4.8 V, OK. |
| B2 | Schottky diode (same SS14/1N5817 as #5) | Series with `+` lead before VSYS | Drops to ~4.2 V at the pin, also blocks reverse if you plug USB simultaneously. |
| B3 | Alkaline AAAs (or NiMH) | The cells themselves | Don't mix chemistries / old + new. |

---

## Wiring Diagram (final 10440 config)

```
   Cradle bay -Y (cell A)        Cradle bay +Y (cell B)
   [+]──────┐                    ┌──────[+]
            ├──── parallel + ────┤
   [-]──────┘                    └──────[-]
            └──── parallel - ────┘
                  │      │
                  │      │  (JST-PH 2.0)
                  ▼      ▼
            ┌──────────────────┐
            │   TP4056 + DW01A │
   USB-C ──►│ IN+      OUT+ ───┼──► [SW] ──► [Schottky →|] ──► Pico VSYS (pin 39)
            │ IN-      OUT- ───┼─────────────────────────────► Pico GND  (pin 38)
            │ B+/B-            │
            └──────────────────┘
```

Connection notes:
- **Cradle wiring:** both cells' `+` tabs jumpered together → single red lead
  to JST. Both `-` tabs jumpered together → single black lead. Tabs go on
  opposite ends of each bay (positive button vs. negative spring), so the
  jumpers cross the cradle's `-X` and `+X` end walls respectively.
- **TP4056 pads:** use the *protected* OUT+/OUT- pads (the ones DW01A gates),
  not B+/B- directly, so over-discharge cutoff actually fires.
- **Schottky direction:** stripe (cathode) toward the Pico.
- **Switch placement:** between OUT+ and the diode anode, so "off" disconnects
  the load but leaves charging functional.

---

## Bench bring-up wiring (alkaline AAAs, *no cradle, no TP4056*)

```
   3×AAA holder
   [+]──► [SW on holder] ──► [Schottky →|] ──► Pico VSYS (pin 39)
   [-]─────────────────────────────────────► Pico GND  (pin 38)
```

Use this only to verify firmware behavior on battery before the 10440s arrive.
**Never** route AAAs through the TP4056. Once the 10440s arrive, throw the
3×AAA holder in a drawer and switch to the diagram above.

---

## Shopping list (links)

These are search/category links (not specific listings) so you can pick the
seller you trust — Anthropic policy keeps me from fabricating direct product
URLs.

- **10440 Li-ion cells, button-top protected** — search "10440 button top
  protected" on `keeppower.com`, `liionwholesale.com`, or Amazon. Avoid
  no-name "fire" branded cells.
- **TP4056 + DW01A USB-C module** — search "TP4056 DW01A USB-C" on Amazon /
  AliExpress. Confirm the listing shows IN+/IN-, B+/B-, OUT+/OUT- pads
  (the "1A2B2O" layout).
- **AAA spring + button contact set** — search "AAA battery contacts spring"
  on Digi-Key, Mouser, or Amazon. Keystone 209/228 (negative spring) +
  Keystone 5204 (positive button) are the canonical pair.
- **Schottky diode SS14 (1A, SMA) or 1N5817 (1A, through-hole)** —
  Digi-Key / Mouser / LCSC, search the exact part number.
- **JST-PH 2.0 mm pre-crimped pigtail** — Adafruit #261, or search
  "JST PH 2.0 2-pin pigtail" on Amazon.
- **Slide switch SS-12D00G3** — Digi-Key / Mouser / Amazon, search the part
  number.
- **3×AAA holder with switch + leads (bench only)** — search "3xAAA battery
  holder switch leads" on Amazon. Pick one with a built-in slide switch.
- **22 AWG silicone wire** — search "22 AWG silicone wire red black" on
  Amazon (BNTECHGO and similar).
- **Heatshrink assortment 2/3 mm** — any Amazon assortment kit.

---

## Build order

1. Solder cradle contacts; verify continuity bay-to-bay (parallel jumpers in).
2. Crimp/solder JST pigtail to the cradle leads.
3. Wire TP4056: USB-C to a charger only (no cells yet); confirm red LED w/
   nothing connected, green-ish behavior with a known-good Li-ion on B+/B-.
4. Connect cradle JST to TP4056 B+/B-. Insert one 10440, check charging.
5. Wire OUT+/OUT- → switch → Schottky → Pico VSYS/GND.
6. Power-on with USB only first, then on cells only, then with both
   (verify diode actually blocks back-feed: the cell voltage should not
   rise when USB is plugged into the Pico).
