# Speaker Module Selection Guide — Dilder Rev 2

## Case Constraints

| Parameter | Value |
|-----------|-------|
| Internal Z-height available | ~5 mm above board/display stack |
| Largest cavity (battery bay) | 39.0 x 41.4 x ~6 mm |
| Side gap clearance | 2-3 mm per side |
| Total case outer dims | 94.5 x 46.0 x 29.8 mm |
| MCU interface | PWM (Pico W) or I2S via PIO |

> **Key constraint:** Z-height is the tightest dimension. Speaker + amp combined
> stack must stay under ~6 mm in the battery bay, or ~5 mm elsewhere.

---

## Ultra-Budget Options (Under $1) — No Amplifier Needed

These options drive directly from a Pico W GPIO pin using PWM. No amplifier
board required. Perfect for beeps, tones, alerts, and simple melodies.

The RP2040 has hardware PWM on every GPIO pin. In MicroPython use
`machine.PWM(pin)` with `.freq()` to set pitch. In C SDK use the PWM
slice API. One GPIO pin + one ground wire.

> **Pico W GPIO limit:** Each pin sources max **12 mA** (vs 40 mA on ESP32).
> This matters for driving speakers directly — piezo buzzers are fine,
> but 8-ohm speakers need a transistor buffer.

### 1. Bare Passive Piezo Disc 12-14 mm (Recommended Budget Pick)

| Spec | Value |
|------|-------|
| Dimensions | 12-14 mm dia x 0.5-1 mm thick |
| Weight | < 1 g |
| Interface | Direct GPIO PWM (1 pin) |
| Frequency range | ~1-5 kHz (loudest near resonance ~2.7 kHz) |
| Voltage | 1.5 - 5 VDC |
| Price | **$0.05-0.20 USD** |
| Sources | [eBay](https://www.ebay.com/itm/335419266914), AliExpress, [Sunrom](https://www.sunrom.com/p/piezo-passive-buzzer-14mm) |

**Pros:**
- Essentially free — as low as $0.05/ea in bulk
- Paper-thin (< 1 mm) — fits literally anywhere in the case
- Zero additional components — solder 2 wires to GPIO + GND
- No amplifier needed — piezo elements are high-impedance, GPIO can drive directly
- Negligible current draw (< 5 mA)
- Available in any quantity from eBay/AliExpress

**Cons:**
- Tinny, buzzer-like sound — no bass, no warmth
- Narrow usable frequency range (best around 2-3 kHz)
- Quiet without a resonant chamber (can print one into the case)
- Not suitable for voice or music playback
- Fragile ceramic — can crack if bent

### 2. Passive Electromagnetic Buzzer 9x5.5 mm (TMB09)

| Spec | Value |
|------|-------|
| Dimensions | 9.0 mm dia x 5.5 mm thick |
| Weight | ~1 g |
| Interface | Direct GPIO PWM (1 pin) |
| Drive frequency | 2-5 kHz square wave |
| Voltage | 3 - 5 VDC |
| Current | < 30 mA |
| Price | **$0.15-0.30 USD** (10-packs ~$2-3) |
| Sources | [Amazon](https://www.amazon.com/Magnetic-Continous-TMB09A03-TMB09A05-TMB09A12/dp/B0D7S5JPJY), AliExpress, eBay |

**Pros:**
- Tiny 9 mm footprint — fits in side gaps or corners
- Louder than bare piezo disc at same voltage
- Self-contained cylindrical package — durable, no fragile ceramic
- Dirt cheap in bulk (10 for ~$2-3)
- 5.5 mm height fits within Z-constraint

**Cons:**
- Fixed resonant frequency — sounds are all "buzzy"
- 5.5 mm thick — uses full Z-budget
- 30 mA draw is higher than piezo (still fine for battery)
- Must be PASSIVE version (not active) to control pitch via PWM

### 3. Passive Electromagnetic Buzzer 12x9.5 mm (TMB12)

| Spec | Value |
|------|-------|
| Dimensions | 12.0 mm dia x 9.5 mm thick |
| Interface | Direct GPIO PWM (1 pin) |
| Sound pressure | >= 85 dB @ 10 cm |
| Drive frequency | 2300 +/- 400 Hz |
| Voltage | 3 - 5 VDC |
| Current | < 30 mA |
| Price | **$0.20-0.40 USD** (10-packs ~$3-4) |
| Sources | [Amazon](https://www.amazon.com/TMB12A05-TMB12A12-Magnetic-Continous-Buzzers/dp/B0D9S9ZZMQ), AliExpress, eBay |

**Pros:**
- Loudest budget option at 85 dB
- Widely available — most common buzzer form factor
- Robust metal can housing

**Cons:**
- **Too tall at 9.5 mm** — does NOT fit the Z-constraint without case modification
- Larger footprint than TMB09
- Same buzzy sound character as TMB09

### 4. KY-006 Passive Buzzer Module

| Spec | Value |
|------|-------|
| Dimensions | 18.5 x 15 x ~8 mm (with PCB) |
| Interface | 3-pin header (VCC, GND, Signal) |
| Frequency range | 1500 - 2500 Hz |
| Voltage | 3.3 - 5 VDC |
| Price | **$0.50-0.99 USD** (3-packs ~$2-3) |
| Sources | [Amazon](https://www.amazon.com/HUABAN-KY-006-Compatible-Sensor-Passive/dp/B07MV55Z6Q), AliExpress, eBay |

**Pros:**
- Breadboard/header friendly — easy to prototype first
- Tons of Pico/Arduino tutorials and example code online
- Includes PCB with labeled pins — beginner-friendly
- Can desolder buzzer from PCB to save space (buzzer itself is ~12x9 mm)

**Cons:**
- Module with PCB is 8 mm tall — too tall for case as-is
- Must desolder buzzer element to fit
- At $0.50-0.99 you're paying for the PCB you'd throw away
- Better to just buy the bare buzzer component

### 5. Bare Mini Speaker 8 ohm 0.5-1W (AliExpress)

| Spec | Value |
|------|-------|
| Dimensions | 20 mm dia x 4 mm thick (typical) |
| Impedance | 8 ohm |
| Power | 0.5 - 1 W |
| Voltage | Direct GPIO (quiet) or with amp |
| Price | **$0.20-0.60 USD** |
| Sources | [AliExpress](https://www.aliexpress.com/w/wholesale-8-ohm-mini-speaker.html), eBay |

**Pros:**
- Real speaker cone — wider frequency response than piezo/buzzer
- Can play simple melodies that actually sound musical
- 4 mm thin — fits the Z-constraint with margin
- Cheapest actual speaker available

**Cons:**
- Very quiet when driven directly from GPIO (no amp)
- 8 ohm load draws ~40 mA — **exceeds Pico W 12 mA GPIO limit**
- **Must** use a transistor buffer (2N2222 + 1K resistor, ~$0.03)
- Cannot drive directly from GPIO without risking damage to RP2040
- AliExpress shipping takes 2-4 weeks

---

## Ultra-Budget Recommended Combo

### Best Sub-$1: Bare Piezo Disc + Printed Resonance Chamber

| Component | Cost |
|-----------|------|
| 14 mm passive piezo disc | $0.10-0.20 |
| 2 wires + solder | free (from stock) |
| Resonance cavity | print into case lid (free) |
| **Total** | **$0.10-0.20** |

- 1 GPIO pin, 0 extra boards, < 1 mm thick
- Print a small resonance chamber (dome or Helmholtz cavity) into the
  top cover to boost volume 6-10 dB
- Pico W: `pwm = machine.PWM(Pin(N)); pwm.freq(2700)` plays tones directly
- Can play melodies, alerts, startup jingles, game sounds
- Loudest at 2-3 kHz — perfect for notification beeps

### Runner-Up: TMB09 Passive Buzzer

| Component | Cost |
|-----------|------|
| TMB09 9x5.5mm passive buzzer | $0.15-0.30 |
| **Total** | **$0.15-0.30** |

- Self-contained, louder than bare piezo, fits the Z-constraint
- Same 1-pin PWM drive

### If You Want "Musical" Sound: AliExpress Mini Speaker + NPN Transistor

| Component | Cost |
|-----------|------|
| 20mm 8ohm mini speaker | $0.30-0.60 |
| 2N2222 NPN transistor | $0.02-0.05 |
| 1K base resistor | $0.01 |
| **Total** | **$0.33-0.66** |

- Transistor acts as a simple switch-amp driven by PWM GPIO
- Fuller sound than piezo — can actually hear different notes clearly
- Still no fancy amp board — 3 components total

---

## Amplifier Modules (Premium Tier — $4-6)

> The options below are for higher-fidelity audio (voice playback, WAV files,
> Bluetooth audio). Skip these if you just want beeps and tones.

### 1. Adafruit MAX98357A I2S Breakout

| Spec | Value |
|------|-------|
| Dimensions | 19.4 x 17.8 x 3.0 mm |
| Weight | 1.2 g |
| Interface | I2S (no MCLK needed) |
| Output | 3.2 W @ 4 ohm, 1.8 W @ 8 ohm (5V) |
| Supply voltage | 2.7 - 5.5 VDC |
| Gain options | 3/6/9/12/15 dB (pin-selectable) |
| Price | ~$5.95 USD |
| Sources | [Adafruit](https://www.adafruit.com/product/3006), Amazon, DigiKey, Mouser |

**Pros:**
- Ultra-thin at 3.0 mm — fits within Z-height constraints
- I2S works on Pico W via PIO (3 wires: BCLK, LRCLK, DIN)
- No external MCLK required — simplifies wiring
- Combined DAC + amplifier on one board
- Extremely well-documented with Adafruit tutorials and library support
- Works on 3.3V logic (Pico W compatible)
- Pre-soldered terminal block for speaker connection
- Widely available and cheap

**Cons:**
- Mono output only (fine for notifications/alerts)
- Needs a separate speaker (not included)
- I2S on Pico W requires PIO setup (more complex than simple PWM)
- No volume control without additional code/hardware (gain is pin-set)

![Adafruit MAX98357A](https://cdn-shop.adafruit.com/970x728/3006-05.jpg)

---

### 2. DFRobot MAX98357 I2S Module (DFR0954)

| Spec | Value |
|------|-------|
| Dimensions | ~18 x 19 x 5 mm |
| Interface | I2S |
| Output | 2.5 W @ 4 ohm (5V) |
| Supply voltage | 3.3 - 5.0 VDC |
| Connector | PH2.0 + stamp holes for speaker |
| Price | ~$4.90 USD |
| Sources | [DFRobot](https://www.dfrobot.com/product-2614.html), DigiKey, The Pi Hut |

**Pros:**
- Stamp holes allow direct PCB soldering — no headers needed
- PH2.0 connector for speaker is secure and compact
- Mode switching (left/right/mixed) via SD pin resistance
- Cheap and well-stocked at multiple distributors

**Cons:**
- Slightly thicker (~5 mm) than Adafruit variant — tight fit
- Less community documentation compared to Adafruit
- Still requires separate speaker

![DFRobot MAX98357](https://wiki.dfrobot.com/dfr0954/image/DFR0954.png)

---

### 3. Adafruit PAM8302A Mono Amplifier

| Spec | Value |
|------|-------|
| Dimensions | 15 x 24 x 2 mm |
| Weight | 1.4 g |
| Interface | Analog audio input (NOT I2S) |
| Output | 2.5 W @ 4-8 ohm |
| Supply voltage | 2.0 - 5.5 VDC |
| Gain | Adjustable via onboard trim pot |
| Price | ~$3.95 USD |
| Sources | [Adafruit](https://www.adafruit.com/product/2130), Amazon, DigiKey |

**Pros:**
- Thinnest amplifier option at only 2 mm
- Cheapest amplifier on this list
- Onboard volume trim pot — no software gain control needed
- Best match for Pico W — takes PWM audio output directly (analog input)
- Over 90% efficient at >0.5W into 8 ohm
- Extremely lightweight

**Cons:**
- Analog input only — pair with RC low-pass filter on Pico W PWM output
- No I2S support — but that's fine since Pico W PWM is the simpler path anyway
- Requires low-pass filter on PWM output for clean audio
- Slightly longer footprint (24 mm)

![Adafruit PAM8302A](https://cdn-shop.adafruit.com/970x728/2130-00.jpg)

---

### 4. NULLLAB NS4168 I2S Amplifier + Speaker Kit

| Spec | Value |
|------|-------|
| Amp dimensions | ~18 x 20 x 3 mm (estimated) |
| Interface | I2S |
| Output | 2.5 W mono |
| Supply voltage | 4.5 - 5.5 VDC |
| Includes | Amp board + speaker + PH2.0-to-DuPont cable |
| Price | ~$5.50 USD (2-pack ~$8.99) |
| Sources | [Amazon](https://www.amazon.com/Amplifier-Raspberry-Technology-Shielding-Compatible/dp/B0GGBRPKBT) |

**Pros:**
- Comes with speaker included — all-in-one kit
- Anti-clipping technology for cleaner audio at high volume
- RF shielding built-in
- Built-in high-pass filter
- Compatible with MAX98357A pinout (drop-in swap)
- Very cheap per unit when buying 2-pack
- Works with Pico W via PIO I2S (same as MAX98357A)

**Cons:**
- Less documentation than Adafruit/DFRobot
- Amazon-only sourcing (less reliable supply chain)
- Included speaker may be too large for case (dimensions unconfirmed)
- Newer/less proven in community projects

---

## Speaker Options

### 1. Adafruit Mini Oval Speaker (4227) — Recommended

| Spec | Value |
|------|-------|
| Dimensions | 30 x 20 x 5 mm |
| Weight | 3 g |
| Impedance | 8 ohm |
| Power | 1 W rated |
| Wire length | ~10 mm (short leads) |
| Price | ~$1.50 USD |
| Sources | [Adafruit](https://www.adafruit.com/product/4227), Amazon, Pimoroni |

**Pros:**
- 5 mm thin — fits the Z-height constraint exactly
- Oval shape maximizes cone area in a narrow space
- 1W is plenty for alerts, notifications, and voice feedback
- Dirt cheap
- Short wires reduce internal clutter

**Cons:**
- 30 x 20 mm footprint takes significant cavity space
- Only 1W max — not for music playback
- 5 mm is the absolute limit of Z-clearance — no margin

![Adafruit Mini Oval Speaker 4227](https://cdn-shop.adafruit.com/970x728/4227-01.jpg)

---

### 2. SparkFun Mini Speaker (COM-26553)

| Spec | Value |
|------|-------|
| Dimensions | 20 mm dia x 4 mm thick |
| Impedance | 8 ohm |
| Power | 1 W rated |
| Wire length | ~60 mm |
| Price | ~$1.60 USD |
| Sources | [SparkFun](https://www.sparkfun.com/products/26553), Amazon |

**Pros:**
- Only 4 mm thick — leaves 1-2 mm margin in cavity
- Round 20 mm footprint is compact
- 1 W output — same as Adafruit oval
- Slightly cheaper than oval option

**Cons:**
- Smaller cone = less bass response
- 60 mm wire may need trimming for tight enclosure
- Round shape less space-efficient than oval in rectangular cavity

![SparkFun Mini Speaker](https://cdn.sparkfun.com/r/600-600/assets/parts/2/6/3/1/9/COM-26553-Mini-Speaker-1W-8-Ohm-Feature.jpg)

---

### 3. Adafruit Mini Metal Speaker (1890)

| Spec | Value |
|------|-------|
| Dimensions | 28 mm dia x 4.5 mm thick |
| Weight | 6 g |
| Impedance | 8 ohm |
| Power | 0.5 W max (0.25 W rated) |
| Frequency range | ~600 - 10,000 Hz |
| Price | ~$1.95 USD |
| Sources | [Adafruit](https://www.adafruit.com/product/1890), Amazon, Micro Center |

**Pros:**
- Metal housing is durable and provides some shielding
- 4.5 mm thin — fits within constraints
- Decent frequency range for voice/notifications
- Pre-attached wires

**Cons:**
- Only 0.5 W — quietest option on this list
- 28 mm diameter is large relative to case width (46 mm)
- Heavier than plastic alternatives (6g)
- Lower power limits maximum volume

![Adafruit Mini Metal Speaker 1890](https://cdn-shop.adafruit.com/970x728/1890-02.jpg)

---

### 4. uxcell 20mm Round Speaker 1W 8 ohm (4-pack) — Amazon Budget Pick

| Spec | Value |
|------|-------|
| Dimensions | 20 mm dia x ~4 mm thick |
| Impedance | 8 ohm |
| Power | 1 W |
| Quantity | 4 pcs |
| Price | ~$5-7 USD (~$1.50/ea) |
| Sources | [Amazon B00O9Y3YAQ](https://www.amazon.com/uxcell-Internal-Magnet-Speaker-Loudspeaker/dp/B00O9Y3YAQ), [Amazon B01MYBC1CT (2-pack)](https://www.amazon.com/uxcell-Mediant-Internal-Magnetic-Speaker/dp/B01MYBC1CT) |

**Pros:**
- Same form factor as SparkFun COM-26553 but cheaper per unit in 4-pack
- Internal magnet — no stray flux into nearby Hall sensors / joystick
- Prime shipping (vs AliExpress 2-4 week wait)
- 4 mm thick fits Z-budget with margin

**Cons:**
- Generic Chinese OEM — frequency response not characterized
- Pre-attached lead length varies between batches

---

### 5. JESSINIE Ultra-Thin 20mm Speaker 1W 8 ohm (20-pack)

| Spec | Value |
|------|-------|
| Dimensions | 20 mm dia, ultra-thin profile |
| Impedance | 8 ohm |
| Power | 1 W |
| Sound pressure | 98 +/- 3 dB |
| Quantity | 20 pcs |
| Price | ~$10-13 USD (~$0.50-0.65/ea) |
| Sources | [Amazon B0G57VT7Y8](https://www.amazon.com/JESSINIE-Ultra-Thin-Speaker-8%CE%A9-1W/dp/B0G57VT7Y8) |

**Pros:**
- Cheapest per-unit on Amazon when buying the 20-pack
- 98 dB output rivals premium amp setups
- Plastic frame is lighter than metal-can speakers
- Plenty of spares for prototyping iterations

**Cons:**
- Only economical if you want bulk
- Plastic frame less rigid — needs case clamping for best bass
- Cable termination quality varies

---

### 6. IIVVERR / Aexit 30x20x4mm Oval Speaker 1W 8 ohm

| Spec | Value |
|------|-------|
| Dimensions | 30 x 20 x 4 mm (oval) |
| Impedance | 8 ohm |
| Power | 1 W |
| Price | ~$4-6 USD per pair |
| Sources | [IIVVERR B086S9F83P](https://www.amazon.com/IIVVERR-Stereo-Speaker-Est%C3%A9reo-Completa/dp/B086S9F83P), [Aexit B07LFHGSTS](https://www.amazon.com/Aexit-Speakers-Stereo-Speaker-Satellite/dp/B07LFHGSTS) |

**Pros:**
- **Direct Amazon equivalent of Adafruit Mini Oval (4227)** at lower cost
- Same 30 x 20 x 4 mm footprint that already fits the battery bay
- 1 mm thinner than Adafruit oval — adds Z-margin
- Tablet-PC pull style — designed for thin-profile use

**Cons:**
- No-name brand, dimensional tolerance not guaranteed
- Listings frequently relist under different seller names
- Lead length sometimes too short for cradle-to-amp routing

---

### 7. uxcell 16mm Round Speaker 1W 8 ohm (4-pack)

| Spec | Value |
|------|-------|
| Dimensions | 16 mm dia x ~3-4 mm thick |
| Impedance | 8 ohm |
| Power | 1 W |
| Quantity | 4 pcs |
| Price | ~$5-7 USD |
| Sources | [Amazon B082ZPP4P8](https://www.amazon.com/uxcell-Audio-Speaker-Electronic-Projects/dp/B082ZPP4P8) |

**Pros:**
- Smaller footprint than 20mm — fits in tighter cradle pockets or side gaps
- 1W rating in a 16mm body is unusually high
- Pre-wired with leads

**Cons:**
- Smaller cone = less low-end response
- Less common size — fewer mounting reference designs

---

### 8. DMiotech / Gump's 15mm Mini Speaker 1W 8 ohm (4-pack)

| Spec | Value |
|------|-------|
| Dimensions | 15 mm dia x ~3-4 mm thick |
| Impedance | 8 ohm |
| Power | 1 W |
| Price | ~$4-6 USD per 4-pack |
| Sources | [DMiotech B0BMB423HV](https://www.amazon.com/DMiotech-Diameter-Magnetic-Replacement-Loudspeaker/dp/B0BMB423HV), [Gump's B0DG8P86YD](https://www.amazon.com/Gumps-grocery-Internal-Loudspeaker-15MM-8%CE%A9-1/dp/B0DG8P86YD) |

**Pros:**
- Same size as SparkFun PRT-20660 but with full 1W rating (vs 0.5W)
- Phone-replacement style — designed for tight enclosures
- 4-pack at SparkFun single-unit price

**Cons:**
- 15mm cone struggles with anything below 1 kHz
- Best for beeps/voice prompts, not music

---

### 9. XIITIA 3W 8 ohm Mini Speaker w/ 2.54mm Dupont (6-pack)

| Spec | Value |
|------|-------|
| Impedance | 8 ohm |
| Power | 3 W |
| Connector | 2.54mm DuPont (plug-and-play) |
| Quantity | 6 pcs |
| Price | ~$8-10 USD |
| Sources | [Amazon B0D5HPQQ81](https://www.amazon.com/XIITIA-Loundspeaker-Interface-Compatible-Electronic/dp/B0D5HPQQ81) |

**Pros:**
- DuPont connector means no soldering — drop into a header on the PCB
- 3W rating gives headroom on the MAX98357A / NS4168 amps
- Great for breadboard prototyping before final assembly

**Cons:**
- Likely too thick (>5mm) for the Dilder battery bay — verify before ordering
- 3W is overkill — amps will clip first
- DuPont connector adds 2-3mm height penalty

---

### 10. Adafruit Thin Plastic Speaker 0.25W (Amazon)

| Spec | Value |
|------|-------|
| Impedance | 8 ohm |
| Power | 0.25 W |
| Profile | Thin plastic frame |
| Price | ~$2-3 USD |
| Sources | [Amazon B00N4YW7G4](https://www.amazon.com/Speakers-Transducers-Plastic-Speaker-Wires/dp/B00N4YW7G4) |

**Pros:**
- Adafruit-vetted quality on Amazon Prime
- Thin profile competitive with the SparkFun 15mm option

**Cons:**
- Only 0.25W — quietest of all options listed
- Voice-only / beep duty, no music

---

### 11. SparkFun Thin Speaker (PRT-20660)

| Spec | Value |
|------|-------|
| Dimensions | 15 mm dia x ~3 mm thick |
| Impedance | 8 ohm |
| Power | 0.5 W |
| Resonant frequency | ~1700 Hz |
| Price | ~$1.50 USD |
| Sources | [SparkFun](https://www.sparkfun.com/thin-speaker-0-5w.html) |

**Pros:**
- Smallest and thinnest option — only 15 mm and ~3 mm thick
- Leaves the most Z-margin of any option
- Could fit in side gaps or tight corners
- Cheapest option

**Cons:**
- Very low power (0.5 W) — limited volume
- Narrow frequency response centered around 2 kHz
- Tiny cone = tinny sound quality
- Best suited for beeps/tones rather than voice

---

## Recommended Combinations for Dilder Rev 2

### Cheapest Possible: Bare Piezo Disc ($0.10-0.20)

- 14 mm passive piezo disc soldered to 1 GPIO + GND
- Print a resonance dome into the case top cover
- `machine.PWM` for beeps, alerts, jingles
- Thinnest option — virtually no space impact

### Best Value: TMB09 Passive Buzzer ($0.15-0.30)

- 9 x 5.5 mm self-contained package
- Louder than bare piezo, fits Z-constraint
- Drop-in, no extra components

### Best Sub-$1 Audio: Mini Speaker + Transistor ($0.33-0.66)

- 20 mm AliExpress speaker + 2N2222 + 1K resistor
- Actual musical tones, wider frequency response
- Still no amp board — just 3 cheap components

### Premium: Adafruit MAX98357A + Mini Oval Speaker ($7.45)

| Component | Dimensions | Cost |
|-----------|-----------|------|
| MAX98357A amp | 19.4 x 17.8 x 3.0 mm | $5.95 |
| Mini Oval Speaker (4227) | 30 x 20 x 5 mm | $1.50 |
| **Total** | — | **$7.45** |

- I2S via Pico W PIO — voice/WAV audio playback
- Best audio quality — only needed if you want real audio playback

---

## Placement Strategy

```
 ┌──────────────────────────────────────────────────────┐
 │  USB-C                                     Display   │
 │  ┌───┐                                    connector  │
 │  │   │  ┌─────────┐  ┌────────────────┐    ┌──┐    │
 │  │   │  │ AMP     │  │   BATTERY BAY  │    │  │    │
 │  │   │  │ module  │  │   (speaker     │    │  │    │
 │  │   │  │ 19x18mm │  │    goes here)  │    │  │    │
 │  │   │  └─────────┘  │   30x20mm oval │    │  │    │
 │  └───┘                └────────────────┘    └──┘    │
 │  ← -X wall (3mm)              +X wall (1.2mm) →     │
 └──────────────────────────────────────────────────────┘
         Top-down view — cradle layer
```

**Suggested location:** Mount speaker in the battery bay area (39 x 41 mm)
with sound holes drilled/printed in the base plate. Amp module mounts
adjacent on the cradle insert. Both components are thin enough (<= 5 mm)
to fit below the PCB mounting level.

---

## Sourcing Quick Reference

| Component | Adafruit | Amazon | SparkFun | DigiKey |
|-----------|----------|--------|----------|---------|
| MAX98357A amp | [3006](https://www.adafruit.com/product/3006) | search "MAX98357A" | — | [search](https://www.digikey.com) |
| DFRobot MAX98357 | — | — | — | [DFR0954](https://www.digikey.com/en/products/detail/dfrobot/DFR0954/18069273) |
| PAM8302A amp | [2130](https://www.adafruit.com/product/2130) | search "PAM8302" | — | [search](https://www.digikey.com) |
| NS4168 kit | — | [B0GGBRPKBT](https://www.amazon.com/dp/B0GGBRPKBT) | — | — |
| Oval speaker | [4227](https://www.adafruit.com/product/4227) | search "Adafruit 4227" | — | — |
| Mini speaker 20mm | — | — | [26553](https://www.sparkfun.com/products/26553) | — |
| Metal speaker 28mm | [1890](https://www.adafruit.com/product/1890) | search "Adafruit 1890" | — | — |
| Thin speaker 15mm | — | — | [20660](https://www.sparkfun.com/thin-speaker-0-5w.html) | — |
