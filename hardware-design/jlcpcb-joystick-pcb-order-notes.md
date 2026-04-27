# JLCPCB Joystick PCB Order Notes

## Order Details

- **Board:** Joystick Breakout PCB (hand-routed, KiCad 10)
- **Switch:** K1-1506SN-01 (Korean Hroparts, 5-way navigation, LCSC C145910)
- **Board size:** 19.6 x 19.6 mm
- **Assembly:** JLCPCB SMT (Economic PCBA)
- **Order date:** 2026-04-27

## Placement Verification Request

JLCPCB emailed a placement verification before proceeding with assembly. This is standard procedure for components where the automated system can't confidently determine orientation.

### What they asked

> "Since we are not so sure about the polarities of the components SW1 are correct or not. Could you please kindly check if the polarities and placements of the SMD components are correct in the below 2D picture?"

### What "polarity" means for a switch

The K1-1506SN-01 is a passive switch with no electrical polarity (it's not a diode or capacitor). JLCPCB uses "polarity" as a catch-all term for **component orientation/rotation**. The real question is: "Is SW1 rotated correctly so the physical directions (up/down/left/right) match your intended wiring?"

### Their verification image

![JLCPCB placement verification](website/docs/assets/images/hardware/pcb/jlcpcb-sw1-placement-verification.png)

The image shows SW1 placed with:
- **A** (up arrow) pointing toward the top of the board (away from header pins)
- **C** (down arrow) pointing toward the bottom (toward header pins)
- **B** on the left, **D** on the right
- Red dot (pin 1 marker) on the left side

This matches the intended wiring: header labels Com/L/D/UP/R/C correspond to the correct physical directions.

### Response

"Yes, the placement and orientation of SW1 is correct. Please proceed with production."

### Why the flag was raised

Several factors likely triggered the manual review:

1. **Near-symmetric package** — the switch body is roughly square, so JLCPCB's system can't auto-detect if 0/90/180/270 degree rotation is intended
2. **CPL rotation mismatch** — KiCad and JLCPCB often disagree on what "0 degrees" means for a given footprint. Their system detects the discrepancy and flags it
3. **No clear pin 1 marker on silkscreen** — the board doesn't have a visible dot or notch near pin 1 on the fab/silkscreen layer for the engineer to cross-reference
4. **Auto-flag category** — JLCPCB flags switches, ICs, and connectors by default because a wrong rotation is costly

### Lesson learned for future orders

Add a small **pin 1 indicator** on the silkscreen layer next to the pad corresponding to pin A (or pin 1). A dot, triangle, or "A" label gives the JLCPCB engineer a visual reference and avoids the confirmation email round-trip.

## PCB Design Journey Summary

### Phase 1: Autorouted board (SKRHABE010) — abandoned

- Started with an AI-generated KiCad 8 schematic and PCB for the Alps Alpine SKRHABE010
- Footprint was hand-drawn with incorrect pad geometry (pads on wrong faces)
- Wire pad physically overlapped a mounting hole
- Three pin assignments didn't match the datasheet
- Attempted fix via `crides/kleeb` footprint clone and Freerouting autorouter
- **Result:** Working KiCad files but the part was harder to source and the design had been patched too many times

### Phase 2: Hand-routed board (K1-1506SN-01) — sent to fab

- Designed from scratch in KiCad 10
- Switched to Korean Hroparts K1-1506SN-01 (LCSC C145910) — readily available on JLCPCB
- Imported symbol and footprint via `easyeda2kicad`
- Hand-routed all traces (no autorouter)
- 19.6 x 19.6 mm board fits the 20 x 20 mm enclosure pocket
- 6-pin solder-wire header with silkscreen labels (Com/L/D/UP/R/C)
- Ground plane on back copper
- Exported gerbers + JLCPCB BOM/CPL
- **Result:** Order placed, placement verified, in production

### Current status

- PCB: **In production at JLCPCB** (placement confirmed 2026-04-27)
- Enclosure: Rev 2 with top cover (face plate curvature tuning), base plate variants (thinner, solar cutout with breakaway supports), cradle with battery clip slots
- Battery: PKCELL ICR10440 (3.7V raw Li-Ion AAA) selected for TP4056 + solar path
- Solar: AK 62x36 panel, base plate pit designed, bonding adhesive research complete
- Next: Wire batteries to Pico VSYS, test solar charging through TP4056, assemble with joystick PCB when boards arrive
