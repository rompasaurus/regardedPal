# Dilder Joystick Breakout PCB — Bill of Materials

## Rev 1.0 — 2026-04-25

---

### Components

| Ref | Qty | Description | Manufacturer | MPN | LCSC / JLCPCB | Package | Unit Price | Notes |
|-----|-----|-------------|-------------|-----|---------------|---------|------------|-------|
| SW1 | 1 | 5-direction SMD navigation switch | Alps Alpine | SKRHABE010 | C139794 | SMD-8P, 7.5x7.5mm | $0.50 (qty 100) | Primary joystick input |
| J1 | 1 | 1x6 through-hole wire pads | — | — | — | 2.0mm pitch, PTH | $0.00 | Bare pads for hand-soldered wires |
| H1-H4 | 4 | M3 mounting hole | — | — | — | 3.2mm drill, NPTH | $0.00 | Board-only (no BOM part) |

### PCB Fabrication

| Parameter | Value |
|-----------|-------|
| Board size | 20 x 20 mm |
| Layers | 2 (F.Cu + B.Cu) |
| Thickness | 1.0 mm |
| Copper weight | 1 oz |
| Surface finish | HASL (lead-free) |
| Solder mask | Green (default) |
| Silkscreen | White |
| Min trace width | 0.3 mm |
| Min drill | 1.0 mm (wire pads) |
| NPTH drills | 3.2 mm x4 (M3 mounting) |

### JLCPCB Order Notes

- **PCB only (no assembly):** Order 5-10 boards at ~$2 for the lot
- **With PCBA (recommended):** Use Economic PCBA, single-side SMT
  - SKRHABE010 is an **Extended Part** — $3 setup fee per unique extended part
  - Assembly requires fixture (noted on JLCPCB part page)
  - Upload BOM CSV + CPL (pick-and-place) file
  - J1 wire pads are hand-soldered after assembly — exclude from PCBA BOM

### Alternative Components (drop-in replacements)

| MPN | Manufacturer | LCSC | Price | Stock | Notes |
|-----|-------------|------|-------|-------|-------|
| SKRHABE010 | Alps Alpine | C139794 | $0.50 | ~3,325 | **Primary choice** |
| TM-4175-B-A | XKB Connection | C465995 | $0.73 | ~748 | Same 8-pin footprint, compatible |
| SKRHADE010 | Alps Alpine | C202415 | $0.85 | ~742 | Alps variant, same footprint |

### Wiring to ESP32-S3 (Olimex DevKit-Lipo)

| J1 Pin | Signal | Wire Color (suggested) | ESP32-S3 GPIO |
|--------|--------|----------------------|---------------|
| 1 | JOY_UP | White | GPIO4 |
| 2 | JOY_DOWN | Yellow | GPIO5 |
| 3 | JOY_LEFT | Orange | GPIO6 |
| 4 | JOY_RIGHT | Green | GPIO7 |
| 5 | JOY_CENTER | Blue | GPIO8 |
| 6 | GND | Black | GND |

### Total Cost Estimate (5 boards + assembly)

| Item | Cost |
|------|------|
| PCB fabrication (5 pcs) | ~$2.00 |
| SKRHABE010 x5 | ~$2.50 |
| Extended part fee | $3.00 |
| SMT assembly (5 pcs) | ~$5.00 |
| Shipping (economy) | ~$3.00 |
| **Total** | **~$15.50** |
