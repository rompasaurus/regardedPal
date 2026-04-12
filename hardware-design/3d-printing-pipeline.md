# 3D Printing Prototyping Pipeline — Analysis Document

A comprehensive evaluation of every viable 3D printing technology, service, and CAD workflow for designing and manufacturing the Dilder enclosure. This document exists to make informed, cost-effective decisions about how to go from CAD model to physical prototype (and eventually small-batch production).

**Target part:** Two-piece snap-fit enclosure, ~88 x 34 x 19 mm, ~15–25 g material, housing a Pico W + Waveshare 2.13" e-Paper display + 5 tactile buttons.

---

## Table of Contents

1. [Technology Overview](#1-technology-overview)
2. [FDM / FFF — Fused Deposition Modeling](#2-fdm--fff--fused-deposition-modeling)
3. [SLA / MSLA — Resin Printing](#3-sla--msla--resin-printing)
4. [SLS — Selective Laser Sintering](#4-sls--selective-laser-sintering)
5. [MJF — Multi Jet Fusion](#5-mjf--multi-jet-fusion)
6. [Other Industrial Technologies](#6-other-industrial-technologies)
7. [Technology Comparison Matrix](#7-technology-comparison-matrix)
8. [Third-Party Print Services — Deep Dive](#8-third-party-print-services--deep-dive)
9. [Third-Party Service Comparison Matrix](#9-third-party-service-comparison-matrix)
10. [Material Guide](#10-material-guide)
11. [CAD Software and Design Workflow](#11-cad-software-and-design-workflow)
12. [Pricing Estimates for the Dilder Enclosure](#12-pricing-estimates-for-the-dilder-enclosure)
13. [Viable Options — Ranked Recommendations](#13-viable-options--ranked-recommendations)
14. [Decision Framework](#14-decision-framework)
15. [Scaling Path — Prototype to Production](#15-scaling-path--prototype-to-production)

---

## 1. Technology Overview

There are four 3D printing technologies relevant to small electronics enclosures. Each makes fundamental trade-offs between cost, speed, surface finish, and mechanical properties.

| Technology | Process | Home Printer? | Service Available? | Best For |
|------------|---------|---------------|-------------------|----------|
| **FDM/FFF** | Melted plastic filament deposited layer by layer | Yes ($150–$1500) | Yes | Cheapest functional prototypes, fastest iteration |
| **SLA/MSLA** | UV light cures liquid resin layer by layer | Yes ($150–$3000) | Yes | Best surface finish and detail at desktop scale |
| **SLS** | Laser sinters nylon powder | No (machines start ~$10K) | Yes | Strongest functional parts, no supports needed |
| **MJF** | Inkjet + infrared fuses nylon powder | No (machines start ~$100K) | Yes | Production-quality nylon parts, best price/quality via services |

---

## 2. FDM / FFF — Fused Deposition Modeling

### How It Works

A thermoplastic filament (1.75 mm diameter spool) is fed through a heated nozzle (180–300 C) and deposited in layers (typically 0.2 mm) onto a heated build plate. The part builds up layer by layer from the bottom.

### Printer Tiers

| Tier | Price Range | Examples | Notes |
|------|------------|----------|-------|
| **Budget** | $150–$300 | Creality Ender 3 V3, Elegoo Neptune 4, Anycubic Kobra 3 | Adequate for enclosures. Most now have auto-leveling and direct drive. |
| **Mid-range** | $300–$700 | **Bambu Lab A1 Mini (~$250)**, Bambu Lab A1 (~$400), Prusa MK4S (~$600) | Significantly better quality, speed (200–500 mm/s), and reliability out of the box. The A1 Mini is the sweet spot for this project. |
| **Enthusiast** | $700–$1500 | Bambu Lab P1S/X1C, Prusa XL, Voron kits | Enclosed chambers (needed for ABS/ASA), multi-material, excellent reliability. |

### Material Costs Per Spool (1 kg)

| Material | Cost/kg | For our enclosure (~25 g) |
|----------|---------|--------------------------|
| PLA | $15–25 | ~$0.50 |
| PETG | $18–28 | ~$0.60 |
| ABS | $18–25 | ~$0.55 |
| ASA | $22–30 | ~$0.70 |
| TPU | $25–35 | ~$0.80 |
| Nylon PA12 | $35–60 | ~$1.25 |
| CF-PETG | $35–55 | ~$1.10 |

### Pros

- **Lowest cost of entry** — a capable printer costs $200–400
- **Cheapest per-part cost** — under $1 in material for our enclosure
- **Fastest iteration** — print a new revision in 1–3 hours, same day
- **Enormous material variety** — rigid, flexible, high-temp, filled composites
- **Functionally strong** — PETG and ASA parts handle real-world use
- **Supports snap-fits, screw bosses, living hinges** in the right materials
- **Post-processing options** — sanding, painting, acetone smoothing (ABS), filler primer
- **Massive community** — thousands of tutorials, pre-made parametric enclosure generators
- **No hazardous chemicals** — PLA and PETG are safe in a normal room

### Cons

- **Visible layer lines** — 0.2 mm layers are noticeable; 0.12 mm is better but slower
- **Dimensional accuracy** — typically +/- 0.2–0.3 mm (well-tuned machines hit +/- 0.1 mm)
- **Anisotropic strength** — parts are weakest between layers (Z-axis)
- **Overhangs > 45 deg require supports** — which leave marks on the surface
- **Fine features are limited** — thin walls under 1 mm and small text are challenging
- **Surface finish is not consumer-product quality** without post-processing
- **Stringing and artifacts** need cleanup, especially with PETG

### Print Time for Dilder Enclosure (Both Halves)

| Printer Speed | Layer Height | Estimated Time |
|---------------|-------------|----------------|
| Budget (60 mm/s) | 0.2 mm | 3–5 hours |
| Mid-range (200 mm/s) | 0.2 mm | 1–2 hours |
| Mid-range (200 mm/s) | 0.12 mm | 2–3 hours |

### Verdict for This Project

**Best choice for rapid iteration during early prototyping.** If you plan to iterate the enclosure design more than 2–3 times, owning a $200–400 FDM printer pays for itself vs. ordering from services each time. The Bambu Lab A1 Mini ($250) is the strongest recommendation for this use case.

---

## 3. SLA / MSLA — Resin Printing

### How It Works

A vat of liquid photopolymer resin sits above an LCD screen (MSLA) or under a UV laser (SLA). The screen/laser selectively cures one layer of resin at a time. The build plate lifts, fresh resin flows in, and the next layer is cured. Parts require post-processing: washing in IPA or water, then UV curing.

### Printer Tiers

| Tier | Price Range | Examples | Notes |
|------|------------|----------|-------|
| **Budget MSLA** | $150–$300 | Elegoo Mars/Saturn series, Anycubic Photon Mono series | Excellent detail. The Elegoo Saturn 4 Ultra offers 10K+ resolution. |
| **Mid-range MSLA** | $300–$700 | Elegoo Saturn 4 Ultra, Anycubic Photon Mono M7, Phrozen Sonic series | Larger build volumes, higher resolution. |
| **Professional** | $700–$3500 | Formlabs Form 4 (~$2000–3500), Prusa SL1S | Gold standard. Exceptional material options and engineering resins. |

### Material Costs

| Resin Type | Cost/Liter | For our enclosure (~20 ml) |
|------------|-----------|---------------------------|
| Standard | $25–40 | ~$0.70 |
| ABS-like / tough | $35–55 | ~$1.00 |
| Flexible | $45–65 | ~$1.20 |
| High-temp | $50–80 | ~$1.50 |
| Water-washable | $30–45 | ~$0.80 |
| Engineering (Formlabs) | $100–200 | ~$3.50 |

### Pros

- **Exceptional surface finish** — layer heights 0.025–0.05 mm, near-smooth surfaces
- **Best dimensional accuracy** at desktop scale — +/- 0.05–0.1 mm
- **Fine features and small text/logos** render cleanly
- **Near-injection-mold surface quality** on appearance prototypes
- **Isotropic strength** within the XY plane
- **Speed is independent of part count per layer** — print multiple enclosures at same speed as one

### Cons

- **Resin is messy, toxic (uncured), and requires PPE** — nitrile gloves, ventilation
- **Post-processing is mandatory** — IPA wash + UV cure adds 30–60 minutes
- **Parts are generally more brittle** than FDM (standard resin snaps under flex)
- **Snap-fits are fragile** unless using tough/engineering resin at higher cost
- **Resin fumes** — printer needs a well-ventilated area, not a bedroom or living space
- **IPA waste disposal** is an environmental/safety consideration
- **Smaller build volumes** than FDM at equivalent price
- **Resin has a shelf life** — opened bottles degrade over months
- **Support removal leaves witness marks** that need sanding

### Print Time for Dilder Enclosure

| Resin Printer | Layer Height | Estimated Time |
|---------------|-------------|----------------|
| MSLA (any) | 0.05 mm | 2–4 hours + 30–60 min post-processing |

> MSLA cures the entire layer at once, so print time depends on height, not footprint area. Printing 4 enclosures takes the same time as 1 (if they fit on the plate).

### Verdict for This Project

**Best for appearance prototypes and demos.** If you need a case that looks polished for a presentation or photo, SLA delivers the best surface quality. Not ideal for functional snap-fit prototypes (brittleness), and the messy/toxic workflow adds friction to rapid iteration. Consider SLA for the "final look" prototype, FDM for iterating the fit.

---

## 4. SLS — Selective Laser Sintering

### How It Works

A thin layer of powdered nylon is spread across the build area. A CO2 laser traces the cross-section, sintering (fusing) the powder into solid plastic. A new layer of powder is spread and the process repeats. The surrounding unsintered powder acts as support, so **no support structures are needed** — any geometry is printable.

### Availability

| Option | Price | Notes |
|--------|-------|-------|
| Formlabs Fuse 1+ 30W | ~$18,000–25,000 | "Prosumer" SLS. Not hobbyist-viable. |
| Sinterit Lisa PRO | ~$10,000–15,000 | Small-format SLS. Still too expensive. |
| **Print services** | **$4–25 per enclosure** | **Widely available, most practical option.** |

### Pros

- **No supports needed** — complete geometric freedom for complex snap-fits, internal features, living hinges
- **Excellent mechanical properties** — nylon PA12 is strong, slightly flexible, and impact-resistant
- **Functional end-use quality** — parts feel and perform like injection-molded plastic
- **Good dimensional accuracy** — +/- 0.1–0.2 mm
- **Self-supporting** means parts stack efficiently in the build volume — reduces per-part cost at volume
- **Can be dyed, polished, or vapor smoothed** for improved appearance
- **High temperature resistance** — PA12 melts at ~175 C

### Cons

- **Not available as a home printer** at hobbyist budgets
- **Surface is slightly rough/grainy** — matte texture, not glossy smooth
- **Minimum wall thickness ~0.8 mm** — thinner features may not resolve
- **Per-part cost is higher** than home FDM — $4–25 through services
- **Lead time** — 5–15 days including shipping from services
- **Limited colour options** — natural white/grey PA12, or dyed black. Custom colours via painting.
- **Fine detail is softer** than SLA — small text below ~1 mm may blur

### Verdict for This Project

**Best for functional prototypes and final enclosures.** When the design is locked down after FDM iteration, ordering SLS PA12 through JLCPCB or PCBWay gives you a durable, professional-feeling case for under $15 shipped. No layer lines, strong snap-fits, and it feels like a real product.

---

## 5. MJF — Multi Jet Fusion

### How It Works

HP's proprietary process. An inkjet array deposits fusing agent and detailing agent onto a bed of nylon powder. An infrared energy source passes over, fusing the powder where the agent was deposited. Similar to SLS in concept but faster and with slightly better surface finish.

### Availability

Only available through print services. HP machines start at ~$100,000+.

### Pros

- **Slightly better surface finish than SLS** — smoother, more uniform
- **Excellent mechanical properties** — comparable to or slightly better than SLS PA12
- **Very good dimensional accuracy** — +/- 0.1–0.2 mm
- **Faster throughput than SLS** — better economics at volume
- **Parts are dark grey/black by default** — no painting needed for a dark enclosure
- **Functional end-use quality** — production-viable parts
- **Often same price or cheaper than SLS** through services

### Cons

- **Not available for home use** — service-only
- **Limited material options** — primarily PA12 nylon
- **Per-part cost still higher than home FDM** — $3–20 through services
- **Lead time** — 5–15 days through services
- **Dark grey/black default colour** — if you want white or coloured, you need to paint/dye
- **Slightly grainy surface** — better than SLS but not SLA-smooth

### Verdict for This Project

**The strongest service-based option for this enclosure.** MJF PA12 through JLCPCB is often $3–8 for our part, it comes out dark grey (which looks good), it's mechanically excellent, and the finish is better than SLS. If ordering from a service, MJF PA12 should be the default choice.

---

## 6. Other Industrial Technologies

These are less relevant for this project but included for completeness.

### PolyJet / Material Jetting (Stratasys)

Inkjet-like deposition of photopolymer droplets, UV cured. Exceptional detail and multi-material/multi-colour capability. Parts tend to be brittle and UV-sensitive. Available through services at $30–80+ for small parts. **Overkill for this project** unless you need multi-material prototyping.

### Binder Jetting

Used for metal parts and full-colour sandstone. Not relevant for functional plastic enclosures.

### DMLS / SLM (Metal 3D Printing)

Laser-sintered metal (aluminium, stainless steel, titanium). $100+ per small part. Only relevant if you need RF shielding or extreme thermal conductivity. **Not applicable to this project.**

### Sheet Metal (Laser Cut + CNC Bend)

Not technically 3D printing, but a viable alternative enclosure strategy. Services like SendCutSend can laser-cut aluminium panels and CNC-bend them into enclosures for $5–15 per piece with 1–3 day turnaround. Worth considering for a production enclosure with a premium metal feel.

---

## 7. Technology Comparison Matrix

Side-by-side comparison for the Dilder enclosure specifically.

| Factor | FDM | SLA/MSLA | SLS | MJF |
|--------|-----|----------|-----|-----|
| **Home printer cost** | $200–$700 | $150–$3500 | Not viable | Not viable |
| **Material cost per enclosure** | $0.35–$1.30 | $0.55–$3.50 | Service only | Service only |
| **Service cost per enclosure** | $1–$5 | $1–$8 | $4–$25 | $3–$20 |
| **Dimensional accuracy** | +/- 0.2 mm | +/- 0.05 mm | +/- 0.15 mm | +/- 0.15 mm |
| **Surface finish** | Visible layers | Near-smooth | Slightly grainy | Slightly grainy |
| **Snap-fit durability** | Good (PETG) | Poor (brittle) | Excellent | Excellent |
| **Layer visibility** | Yes | Barely | No | No |
| **Supports needed** | Yes (overhangs) | Yes (always) | No | No |
| **Post-processing** | Minimal | Wash + cure | Optional dyeing | Optional dyeing |
| **Safety/mess** | Clean, safe | Toxic resin, PPE | N/A (service) | N/A (service) |
| **Iteration speed** | 1–3 hours | 3–5 hours | 5–15 days | 5–15 days |
| **Min wall thickness** | 1.0 mm | 0.5 mm | 0.8 mm | 0.8 mm |
| **Heat resistance** | 55–100 C | 50–230 C | ~175 C | ~175 C |
| **Best for** | Rapid iteration | Appearance models | Functional finals | Functional finals |

---

## 8. Third-Party Print Services — Deep Dive

### JLCPCB (JLC3DP)

| Detail | Value |
|--------|-------|
| **URL** | jlcpcb.com/3d-printing |
| **Materials** | SLA (standard, ABS-like, tough, high-temp resins), SLS (PA12, PA12-HP), MJF (PA12), FDM (ABS, PLA) |
| **Pricing for Dilder enclosure** | SLA standard: $1–4. MJF PA12: $3–8. SLS PA12: $4–10. |
| **Lead time** | 3–5 business days production + 5–15 days shipping (standard) |
| **Shipping** | $3–15 depending on method. Can combine with PCB orders. |
| **Minimum order** | None, but shipping cost makes batching smart |
| **Finish options** | Dyeing (MJF/SLS), sanding, painting |

**Pros:** Cheapest option by far. Instant online quoting. Consistent quality. Combines with PCB orders to share shipping. Huge material selection. Upload STL/STEP and get a quote in seconds.

**Cons:** Shipping from China takes 7–15 days. Quality control is good but not premium-tier. Limited colour options for MJF/SLS. Communication can be slow if issues arise.

**Verdict:** Default choice for cost-effective prototyping. Order MJF PA12 for functional parts, SLA for appearance parts.

---

### PCBWay 3D Printing

| Detail | Value |
|--------|-------|
| **URL** | pcbway.com/3d-printing |
| **Materials** | SLA (standard, ABS-like, tough, castable), SLS (PA12, glass-filled nylon), MJF (PA12), FDM (PLA, ABS, PETG, Nylon), also metal DMLS and CNC machining |
| **Pricing for Dilder enclosure** | SLA standard: $3–8. MJF PA12: $5–12. SLS PA12: $6–15. |
| **Lead time** | 3–7 business days production + 5–15 days shipping |
| **Shipping** | $5–20 depending on method |
| **Minimum order** | None |
| **Finish options** | Dyeing, painting, polishing, vapor smoothing |

**Pros:** Wider material selection than JLCPCB. More finishing options (painting, polishing, vapour smoothing). Good quality. Also offers CNC machining and injection moulding for scaling up. Convenient to bundle with PCB orders.

**Cons:** Slightly more expensive than JLCPCB. Same China shipping times. $25 minimum on some order types may apply.

**Verdict:** Good alternative to JLCPCB, especially if you need finishing services or want to explore CNC/injection moulding for later production runs.

---

### Craftcloud (All3DP)

| Detail | Value |
|--------|-------|
| **URL** | craftcloud3d.com |
| **What it is** | Price-comparison marketplace aggregating quotes from 150+ print services worldwide |
| **Materials** | Whatever the underlying services offer — essentially everything |
| **Pricing** | Upload your STL, select material, compare quotes from many providers |
| **Lead time** | Varies by provider (typically 3–14 days + shipping) |

**Pros:** One upload, many quotes. Finds local printers that can deliver faster. Great for discovering the cheapest option for a specific material/quantity. Some providers offer domestic shipping (faster than China).

**Cons:** Not a printer — you're ordering from an unknown shop. Quality varies by provider. Less predictable than ordering from JLCPCB/PCBWay directly. No relationship or combined ordering.

**Verdict:** Use as a comparison tool. Upload the STL to Craftcloud alongside JLCPCB to sanity-check pricing. Especially useful when you need a US/EU-based printer for faster delivery.

---

### Shapeways

| Detail | Value |
|--------|-------|
| **URL** | shapeways.com |
| **Materials** | SLS (PA12, PA11, glass-filled), MJF (PA12), Metals (stainless, brass, silver, gold), full-colour sandstone |
| **Pricing for Dilder enclosure** | Nylon SLS: $10–25. MJF: $10–20. Metal: $30–100+. |
| **Lead time** | 5–10 business days + shipping |
| **Shipping** | Standard from $5–10 (US) |
| **Minimum order** | None |

**Pros:** Unique material options (metals, full colour). Good quality SLS/MJF. US-based shipping. Established brand.

**Cons:** Went through bankruptcy in 2024 (acquired by Brainstone) — verify current service status. Significantly more expensive than JLCPCB/PCBWay. Limited FDM options.

**Verdict:** Only consider for unique materials (metal enclosure, full-colour model) or if you need US-based fast shipping and Craftcloud doesn't surface cheaper options.

---

### Xometry

| Detail | Value |
|--------|-------|
| **URL** | xometry.com |
| **Materials** | FDM, SLA, SLS, MJF, PolyJet, DMLS metal, CNC machining, injection moulding, sheet metal |
| **Pricing for Dilder enclosure** | SLS PA12: $15–35. MJF: $12–30. SLA: $10–25. |
| **Lead time** | 3 business days (expedited) to 10 days (standard) |
| **Shipping** | Included in US quotes |
| **Minimum order** | None |

**Pros:** Fastest US-based option (3-day expedite). Professional-grade quality. Inspection reports and tolerancing available. Instant online quoting. Also offers CNC, injection moulding, sheet metal — one-stop shop for scaling.

**Cons:** 3–5x more expensive than JLCPCB. Overkill for hobby prototyping. Pricing targets professional/industrial customers.

**Verdict:** Use when you need parts fast in the US (3-day turnaround) and cost is secondary, or when you need certifications/inspection reports.

---

### Hubs (Protolabs Network)

| Detail | Value |
|--------|-------|
| **URL** | hubs.com |
| **Materials** | FDM, SLA, SLS, MJF, PolyJet, Metal — full range |
| **Pricing for Dilder enclosure** | SLS: $15–30. MJF: $12–25. SLA: $10–20. |
| **Lead time** | 5–10 business days standard, 3 days expedited |
| **Minimum order** | None |

**Pros:** Reliable, professional quality. Part of Protolabs (large manufacturing network). Good for guaranteed consistency.

**Cons:** Similar pricing to Xometry — professional tier. Not cost-effective for hobby prototyping.

**Verdict:** Interchangeable with Xometry. Use whichever quotes lower for your specific part.

---

### Sculpteo (BASF Forward AM)

| Detail | Value |
|--------|-------|
| **URL** | sculpteo.com |
| **Materials** | SLS (PA12, PA11, glass-filled, alumide, TPU), SLA, metals |
| **Pricing for Dilder enclosure** | SLS PA12: $10–25. SLA: $8–15. |
| **Lead time** | 5–10 business days + shipping from France/US |
| **Minimum order** | None |

**Pros:** Good European option. Part of BASF's additive manufacturing division. Online batch analysis and design optimisation tools. Reliable quality.

**Cons:** Mid-range pricing. Shipping from France to US adds time and cost.

**Verdict:** Best option for EU-based ordering. Otherwise, JLCPCB is cheaper.

---

### SendCutSend (Sheet Metal Alternative)

| Detail | Value |
|--------|-------|
| **URL** | sendcutsend.com |
| **What it is** | Laser cutting, waterjet, and CNC bending — NOT 3D printing |
| **Materials** | Aluminium, steel, stainless, copper, brass, acrylic, delrin |
| **Pricing** | Laser-cut aluminium panels: $5–15 per piece |
| **Lead time** | 1–3 business days (US domestic) |
| **Minimum order** | $29 per order |

**Pros:** Extremely fast turnaround (1–3 days). Premium metal feel. Precise laser cutting. Can CNC-bend flat patterns into enclosure shapes.

**Cons:** Not 3D printing — requires designing the enclosure as flat panels + bend lines. $29 minimum order. Limited to flat/bent geometries (no complex 3D shapes). Requires different CAD approach.

**Verdict:** Consider for a premium metal enclosure in later production phases. Not practical for initial prototyping where you need complex internal features (standoffs, screw bosses, battery bay).

---

### Other Notable Services

| Service | Specialty | Notes |
|---------|-----------|-------|
| **Protolabs** (protolabs.com) | Industrial-grade, 1–3 day rush | Premium pricing ($30–100+). For urgent professional needs only. |
| **Wenext** (wenext.cn) | Chinese MJF/SLS | Very competitive for bulk orders. Worth checking for 10+ units. |
| **Treatstock** (treatstock.com) | Marketplace for local print shops | Variable quality. Can find local printers for same-day pickup. |
| **Jawstec** (jawstec.com) | US-based SLS specialist | PA12 nylon. Good quality, $10–20 for small parts. |

---

## 9. Third-Party Service Comparison Matrix

All prices are for the Dilder enclosure (both halves, ~88 x 34 x 19 mm, ~15–25 cm cubed).

| Service | FDM Price | SLA Price | SLS PA12 | MJF PA12 | Shipping | Lead Time | Best For |
|---------|-----------|-----------|----------|----------|----------|-----------|----------|
| **JLCPCB** | $1–4 | $1–5 | $4–10 | **$3–8** | $3–15 | 7–15 days | **Cheapest overall** |
| **PCBWay** | $2–5 | $3–8 | $5–12 | $5–12 | $5–20 | 8–14 days | Good finishing options |
| **Craftcloud** | Varies | Varies | Varies | Varies | Varies | 3–14 days | Price comparison |
| **Shapeways** | — | $8–15 | $10–25 | $10–20 | $5–10 | 7–12 days | Metal/unique materials |
| **Xometry** | $10–25 | $10–25 | $15–35 | $12–30 | Included | 3–10 days | **Fastest US delivery** |
| **Hubs** | $10–25 | $10–20 | $15–30 | $12–25 | Varies | 3–10 days | Professional quality |
| **Sculpteo** | $5–15 | $8–15 | $10–25 | $8–20 | Varies | 5–10 days | Best EU option |
| **SendCutSend** | — | — | — | — | Included | 1–3 days | Sheet metal alternative |

---

## 10. Material Guide

### FDM Materials — For Enclosures

| Material | Cost/kg | Bed Temp | Enclosure Req'd | Heat Resist | Snap-Fit Suitability | Best Use Case |
|----------|---------|----------|-----------------|-------------|---------------------|---------------|
| **PLA** | $15–25 | 60 C | No | ~55 C | Poor (brittle) | Cheap fit-check prototypes |
| **PETG** | $18–28 | 80 C | No | ~80 C | **Good** (flexible) | **Best general-purpose enclosure material** |
| **ABS** | $18–25 | 100 C | **Yes** | ~100 C | Good | Acetone-smoothable for polished finish |
| **ASA** | $22–30 | 100 C | **Yes** | ~100 C | Good | **UV-stable for outdoor/sun exposure** |
| **TPU** | $25–35 | 50 C | No | ~80 C | Excellent (rubber) | Gaskets, bumpers, flexible grips |
| **Nylon PA** | $35–60 | 80 C | **Yes** | ~180 C | **Excellent** | Best snap-fits, living hinges |
| **CF-PETG** | $35–55 | 80 C | No | ~85 C | Good | Stiff, premium look, dimensionally stable |

**Recommendation for Dilder:** Start with **PLA** for quick fit checks, switch to **PETG** for functional prototypes. If you own an enclosed printer, **ASA** is the upgrade path for a durable final case.

### SLA Resins — For Enclosures

| Resin Type | Cost/L | Toughness | Best Use |
|------------|--------|-----------|----------|
| Standard | $25–40 | Brittle | Appearance prototypes, display models |
| ABS-like | $35–55 | Moderate | Functional prototypes with care |
| **Tough** | $45–70 | **Good** | **Best resin for functional snap-fits** |
| Water-washable | $30–45 | Moderate | Convenience (no IPA cleanup) |
| High-temp | $50–80 | Moderate | Enclosures near heat sources |
| Engineering (Formlabs) | $100–200 | Excellent | When you need injection-mold-like performance |

### SLS/MJF Materials — For Enclosures

| Material | Service Cost/cm cubed | Key Properties | Best Use |
|----------|----------------------|----------------|----------|
| **PA12 Nylon** | $0.15–0.40 | Strong, slightly flexible, ~175 C melting | **Default for functional parts** |
| PA11 Nylon | $0.20–0.50 | More flexible, better impact than PA12 | Snap-fits, living hinges |
| PA12 Glass-Filled | $0.20–0.50 | Stiffer, more dimensionally stable, more brittle | Precision parts needing rigidity |
| Alumide | $0.25–0.50 | Aluminium-filled PA12, metallic appearance | Premium cosmetic finish |

---

## 11. CAD Software and Design Workflow

### Software Comparison

| Software | Cost | Platform | Parametric | Learning Curve | Best For |
|----------|------|----------|------------|----------------|----------|
| **Fusion 360 (Personal)** | Free | Win/Mac | Yes | Moderate | **Best overall for this project** |
| FreeCAD | Free | Win/Mac/Linux | Yes | Steep | Open-source, Linux-native |
| OpenSCAD | Free | All | Yes (code) | Moderate (if you code) | Programmers, parametric generators |
| Tinkercad | Free | Browser | No | Easy | Quick first sketch, beginners |
| Onshape (Free) | Free | Browser | Yes | Moderate | Linux users, browser-based CAD |
| Fusion 360 (Commercial) | $595/yr | Win/Mac | Yes | Moderate | STEP export, unlimited docs |
| SolidWorks Maker | ~$99/yr | Win | Yes | Moderate | If you can get a Maker licence |
| SolidWorks (Full) | $3,995/yr | Win | Yes | Moderate | Industry standard, overkill for hobby |

### Recommended Workflow for This Project

1. **Quick shape exploration** — Tinkercad (1–2 hours to confirm proportions)
2. **Parametric model** — Fusion 360 with user parameters for all key dimensions (4–8 hours)
3. **Import PCB reference** — Export KiCad board as STEP, import into Fusion 360 as reference body
4. **Design around components** — use actual component bodies for clearance checks
5. **Export STL** — separate files for top shell and bottom shell
6. **Upload to print service** — or slice for home printer

### KiCad to CAD Integration

If a custom PCB is designed later:

1. **KiCad:** Assign 3D models to all footprints. Export via File > Export > STEP.
2. **Fusion 360:** File > Insert > Insert Mesh (STEP). Create enclosure as new component around the PCB body.
3. **FreeCAD + StepUp:** The KiCadStepUp workbench reads `.kicad_pcb` files directly — tightest integration.
4. **OpenSCAD:** Import dimensions as parameters. Less direct but fully scriptable.

### Key CAD Libraries / Resources

| Resource | What It Provides |
|----------|-----------------|
| **GrabCAD** | Pre-made 3D models of Pico W, common connectors, batteries |
| **BOSL2 (OpenSCAD)** | Snap-fit joints, threads, rounded boxes, hardware inserts |
| **NopSCADlib (OpenSCAD)** | Screws, nuts, heat-set inserts, PCB models |
| **Adafruit Fritzing/STEP libs** | Component 3D models |
| **McMaster-Carr CAD** | Every fastener and hardware component as STEP |

---

## 12. Pricing Estimates for the Dilder Enclosure

All estimates are for the two-piece enclosure (top + bottom shell), ~88 x 34 x 19 mm, ~15–25 g of material.

### Home Printing — Marginal Cost Per Enclosure

| Method | Material | Electricity | Total | Notes |
|--------|----------|-------------|-------|-------|
| Home FDM (PLA) | $0.40 | $0.05 | **$0.45** | Cheapest possible |
| Home FDM (PETG) | $0.60 | $0.05 | **$0.65** | Best functional material |
| Home FDM (ASA) | $0.70 | $0.08 | **$0.78** | UV-stable |
| Home SLA (standard) | $0.70 | $0.05 | **$0.75** | + IPA/consumables ~$0.50 |
| Home SLA (tough) | $1.20 | $0.05 | **$1.25** | Best resin for function |

> These do not include printer amortisation. A $250 printer over 100 prints adds $2.50/print.

### Service Printing — Total Cost Including Shipping

| Option | Part Cost | Shipping | Total | Material | Lead Time |
|--------|-----------|----------|-------|----------|-----------|
| JLCPCB MJF PA12 | $3–8 | $5–10 | **$8–18** | Nylon | 7–15 days |
| JLCPCB SLA | $1–5 | $5–10 | **$6–15** | Resin | 7–15 days |
| JLCPCB SLS PA12 | $4–10 | $5–10 | **$9–20** | Nylon | 7–15 days |
| PCBWay MJF PA12 | $5–12 | $8–15 | **$13–27** | Nylon | 8–14 days |
| Craftcloud (best quote) | $5–15 | Varies | **$10–25** | Varies | 3–14 days |
| Xometry MJF PA12 | $12–30 | Included | **$12–30** | Nylon | 3–10 days |
| Shapeways SLS PA12 | $10–25 | $5–10 | **$15–35** | Nylon | 7–12 days |

### Hardware Costs (One-Time, Reusable Across Prints)

| Item | Cost | Source | Notes |
|------|------|--------|-------|
| M2 heat-set inserts (50-pack) | ~$6 | Amazon | Brass knurled inserts, press-fit with soldering iron |
| M2 x 6 mm screws (50-pack) | ~$5 | Amazon | Socket head cap screws |
| Soldering iron (for heat-set inserts) | ~$25 | Amazon (if not already owned) | Any iron with a conical tip works |

### Total First Prototype Cost

| Scenario | Print | Hardware | Tools | Total |
|----------|-------|----------|-------|-------|
| **Cheapest (JLCPCB MJF)** | $8–18 | $11 | $0 (if own iron) | **$19–29** |
| **Cheapest (home FDM, own printer)** | $0.65 | $11 | $0 | **$12** |
| **Buy printer + print** | $250 (printer) + $0.65 | $11 | $0 | **$262** (amortised to ~$14 after 100 prints) |
| **Fastest (Xometry MJF)** | $12–30 | $11 | $0 | **$23–41** (3-day delivery) |
| **Premium (SLS PA12, polished)** | $15–35 | $11 | $0 | **$26–46** |

---

## 13. Viable Options — Ranked Recommendations

### Option A: JLCPCB MJF PA12 (Best Value Without a Printer)

**Total cost:** ~$12–20 per iteration (part + shipping)
**Lead time:** 7–15 days
**Quality:** Production-grade nylon, no layer lines, dark grey finish

| Pros | Cons |
|------|------|
| Cheapest service option | 1–2 week wait per iteration |
| MJF nylon is mechanically excellent | Limited to JLCPCB's material/colour options |
| No printer investment needed | Can't iterate same-day |
| Bundle with PCB orders to save shipping | Requires uploading STL each time |
| Parts look and feel professional | |

**Best for:** If you don't want to buy a printer and can tolerate 1–2 week iteration cycles. Especially good if you're already ordering PCBs from JLCPCB.

---

### Option B: Bambu Lab A1 Mini + PETG (Best for Rapid Iteration)

**Upfront cost:** ~$250 (printer) + ~$25 (PETG spool)
**Per-iteration cost:** ~$0.65
**Lead time:** 1–3 hours per print
**Quality:** Visible layer lines, but mechanically sound

| Pros | Cons |
|------|------|
| Same-day iteration — print, test, revise, reprint | $275 upfront investment |
| Under $1 per enclosure in material | Visible layer lines (not presentation quality) |
| Enormous material variety | Requires desk space and some learning |
| Printer is useful for future projects | Print quality depends on tuning and settings |
| PETG snap-fits work well | Not as clean as MJF/SLS for final product |
| Community and troubleshooting resources are vast | |

**Best for:** If you plan to iterate the design more than 3–4 times (likely) and want the fastest feedback loop. The printer pays for itself quickly and is useful for all future hardware projects.

---

### Option C: Hybrid — Home FDM for Iteration + JLCPCB MJF for Finals

**Cost:** ~$275 upfront + ~$0.65/iteration + ~$15 for final MJF print
**Lead time:** Hours for iteration, 1–2 weeks for final

| Pros | Cons |
|------|------|
| Best of both worlds | Highest total spend |
| Fast iteration during design phase | Need to manage two workflows |
| Professional final parts via MJF | |
| Each technology covers the other's weakness | |

**Best for:** The recommended approach if budget allows. Use FDM to nail the fit, then order MJF PA12 for the final version.

---

### Option D: Craftcloud — Best Quote Shopping

**Total cost:** ~$10–25 per iteration
**Lead time:** 3–14 days depending on provider

| Pros | Cons |
|------|------|
| Finds the cheapest provider for your specific part | Ordering from unknown shops |
| May find local printers with 2–3 day delivery | Variable quality between providers |
| Wide material selection | No relationship building with a single service |
| No printer investment | Not as cheap as JLCPCB direct |

**Best for:** When you want domestic (US/EU) shipping speed without buying a printer, or when you need a specific material that JLCPCB doesn't offer.

---

### Option E: Xometry/Hubs — Fastest Professional Parts

**Total cost:** ~$15–40 per iteration
**Lead time:** 3–5 business days (US domestic)

| Pros | Cons |
|------|------|
| Fastest service-based option | Most expensive per-part |
| Guaranteed professional quality | Overkill for hobby prototyping |
| Instant quoting, inspection reports available | |
| One-stop shop for scaling (CNC, injection) | |

**Best for:** When you need parts urgently for a deadline or demo and cost is secondary.

---

## 14. Decision Framework

Use this flowchart to pick your approach:

```
Will you iterate the enclosure design more than 3 times?
├── YES → Do you have $250–400 for a printer?
│   ├── YES → Option B (Bambu A1 Mini + PETG) or Option C (Hybrid)
│   └── NO  → Option A (JLCPCB MJF), accept slower iteration
└── NO  → Do you need parts in under 5 days?
    ├── YES → Option E (Xometry/Hubs)
    └── NO  → Option A (JLCPCB MJF) — cheapest for 1–3 prints
```

**For the Dilder specifically:** The enclosure will almost certainly need 3+ iterations (display fit, button alignment, USB port clearance, battery bay sizing). **Option C (Hybrid)** is the strongest long-term recommendation. **Option A (JLCPCB MJF)** is the best if minimising upfront spend.

---

## 15. Scaling Path — Prototype to Production

If the Dilder moves beyond one-off prototyping:

| Volume | Best Technology | Per-Unit Cost | Setup Cost | Notes |
|--------|----------------|---------------|------------|-------|
| 1–5 units | MJF PA12 via JLCPCB | $5–15 | $0 | Order as needed |
| 5–20 units | MJF PA12 bulk via JLCPCB | $3–10 | $0 | Volume discounts kick in |
| 20–50 units | MJF PA12 or SLS bulk | $2–8 | $0 | Services offer batch pricing |
| 50–100 units | **Injection moulding consideration** | $1–3 | $500–3,000 (mould) | Break-even vs. MJF at ~50–100 units |
| 100–500 units | Injection moulding (JLCPCB/PCBWay) | $0.50–2 | $1,000–3,000 (mould) | Per-unit cost drops dramatically |
| 500+ units | Injection moulding (dedicated manufacturer) | $0.20–1 | $2,000–5,000 (mould) | Standard mass production |

> **Key insight:** JLCPCB and PCBWay both offer injection moulding services. A simple two-part mould for the Dilder enclosure would cost $500–2,000 and produce parts at $0.50–2 each. At ~100 units, injection moulding becomes cheaper per-unit than MJF 3D printing. This is the natural scaling path from the same vendors already used for prototyping.

---

## References

| Resource | URL | Purpose |
|----------|-----|---------|
| JLCPCB 3D Printing | jlcpcb.com/3d-printing | Primary print service recommendation |
| PCBWay 3D Printing | pcbway.com/3d-printing | Secondary print service |
| Craftcloud | craftcloud3d.com | Price comparison marketplace |
| Bambu Lab | bambulab.com | Recommended home FDM printer |
| Fusion 360 Personal | autodesk.com/products/fusion-360/personal | Recommended CAD software |
| All3DP Material Guide | all3dp.com | Material comparison articles |
| CNC Kitchen (YouTube) | youtube.com/@CNCKitchen | Material testing and print optimisation |
| Maker's Muse (YouTube) | youtube.com/@MakersMuse | Enclosure design tutorials |
