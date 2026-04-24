# Battery Redesign Shopping List — Dilder Rev 2 (04-24)

Cheap sourcing for the 10440 / dual-cell / 3000mAh battery redesign. All items compatible with the existing TP4056 USB-C charger module.

**Date:** 2026-04-24
**Related:** [solar-charging-research.md](solar-charging-research.md), `hardware-design/scad Parts/Rev 2 extended with joystick/04-24-designs-alterations/`

---

## ⚠️ Critical wiring rule

- **10440 cells are 3.7V Li-ion, NOT 1.5V AAA alkaline.** Do not use alkaline AAAs in this design.
- **Dual 10440 must be wired in PARALLEL, never series.** Series = 7.4V → destroys the TP4056 (single-cell charger only). Parallel doubles capacity (~700mAh) at 3.7V.
- Always match paralleled cells from the same batch; prefer protected cells.

---

## Option A — Dual 10440 (parallel) — for `base-v2-thin-dual-10440.scad`

### Batteries

| Item | Source | Approx price | Link |
|---|---|---|---|
| Soshine 10440 350mAh protected (2-pack) | Amazon | €10–12 | https://www.amazon.com/s?k=soshine+10440+350mah+protected |
| PKCELL 10440 350mAh (AliExpress 4-pack) | AliExpress | €4–6 | https://www.aliexpress.com/w/wholesale-10440-350mah.html |
| LiitoKala 10440 600mAh | AliExpress | €2–3/cell | https://www.aliexpress.com/w/wholesale-liitokala-10440.html |
| Windy Fire 10440 350mAh | 18650batterystore.com | ~$4/cell | https://www.18650batterystore.com/collections/10440-batteries |

### Holders & clips

| Item | Source | Approx price | Link |
|---|---|---|---|
| Dual AAA holder with wire leads (wire in parallel!) | AliExpress | €1 | https://www.aliexpress.com/w/wholesale-2-aaa-battery-holder-wire-leads.html |
| Single AAA holder with leads (×2, parallel externally) | Amazon | €3 for 10 | https://www.amazon.com/s?k=single+aaa+battery+holder+leads |
| Keystone 82 / 92 spring contacts (for SCAD-printed pockets) | LCSC | €0.20 each | https://www.lcsc.com/search?q=keystone+battery+contact |
| Nickel strip 0.1×5mm (solder tabs for flat-top cells) | AliExpress | €3/roll | https://www.aliexpress.com/w/wholesale-nickel-strip-0.1x5mm.html |

---

## Option B — Single 3000mAh LiPo — for `battery-fit-3000mah-single-on-pico`

| Item | Source | Approx price | Link |
|---|---|---|---|
| EEMB 3000mAh 103450 LiPo with JST-PH 2.0 | Amazon | €10–14 | https://www.amazon.com/s?k=eemb+3000mah+103450+jst+ph |
| Generic 103450 3000mAh 3.7V JST | AliExpress | €5–8 | https://www.aliexpress.com/w/wholesale-103450-3000mah-jst.html |
| Adafruit #328 (2500mAh, QC'd, JST-PH) | Adafruit | $15 | https://www.adafruit.com/product/328 |

---

## Wire, connectors, consumables

| Item | Source | Approx price | Link |
|---|---|---|---|
| JST-PH 2.0 pigtails (pre-crimped, 10-pack) | AliExpress | €2 | https://www.aliexpress.com/w/wholesale-jst-ph-2.0-pigtail.html |
| JST-PH 2.0 crimp kit (connectors + crimper, one-time) | Amazon | €20–25 | https://www.amazon.com/s?k=jst+ph+2.0+crimp+kit |
| Silicone hookup wire 26 AWG, 6-color spool kit | Amazon | €10 | https://www.amazon.com/s?k=bntechgo+26awg+silicone+wire+kit |
| Heat-shrink tubing assortment | AliExpress | €3 | https://www.aliexpress.com/w/wholesale-heat-shrink-tubing-assortment.html |
| 1N5817 Schottky diode (solar blocking, optional — from solar research) | LCSC | €0.05 | https://www.lcsc.com/search?q=1N5817 |

---

## Cheapest "just works" starter bundle

Sufficient to wire a parallel-10440 pack into the existing TP4056 charger:

| Qty | Item | Approx cost |
|---|---|---|
| 2 | Soshine protected 10440 350mAh | €10 |
| 1 | Dual AAA holder with leads (wire parallel) | €1 |
| 1 | JST-PH pigtail pack | €2 |
| — | Wire + heat shrink (if not on hand) | €13 |
| | **Minimum total** | **~€13** |
| | **With wire/heat-shrink kits** | **~€26** |

---

## Sanity checks before ordering

1. Confirm 10440 enclosure slot internal length is ≥43mm (10440 is 10×44mm including button top).
2. Confirm the holder you pick matches the SCAD pocket dimensions in `base-v2-thin-dual-10440.scad`.
3. If using flat-top cells, you'll need solder tabs or nickel strip — spring clips need button-top.
4. Verify protected cells fit — protection circuit adds ~2–3mm to cell length.
5. Re-read the parallel-wiring rule above before soldering.
