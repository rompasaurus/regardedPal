# BH1750FVI-TR — Digital Ambient Light Sensor

## Table of Contents

- [Quick Reference](#quick-reference)
- [What Is This Part?](#what-is-this-part)
- [How Photodiode Light Sensors Work](#how-photodiode-light-sensors-work)
  - [The Photodiode](#the-photodiode)
  - [Integration — Accumulating Light Over Time](#integration--accumulating-light-over-time)
  - [The ADC — From Charge to Lux](#the-adc--from-charge-to-lux)
  - [Spectral Response — Seeing Like a Human Eye](#spectral-response--seeing-like-a-human-eye)
  - [Why This Is Better Than a Raw LDR](#why-this-is-better-than-a-raw-ldr)
- [Why This Part](#why-this-part)
- [Key Specifications](#key-specifications)
- [Operating Modes](#operating-modes)
- [Pin Connections on Dilder Board](#pin-connections-on-dilder-board)
- [Application Circuit](#application-circuit)
- [Common Mistakes and Gotchas](#common-mistakes-and-gotchas)
- [Lux Reference Values](#lux-reference-values)
- [I2C Bus Sharing](#i2c-bus-sharing)
- [History and Background](#history-and-background)
- [Datasheet and Sources](#datasheet-and-sources)

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Manufacturer** | ROHM Semiconductor (Kyoto, Japan) |
| **Part Number** | BH1750FVI-TR |
| **Function** | Digital ambient light sensor, spectral response close to human eye |
| **Package** | WSOF-6 (3.0 x 1.6 x 0.9 mm) |
| **LCSC** | [C78960](https://www.lcsc.com/product-detail/C78960.html) |
| **Price (qty 5)** | ~$0.49 |
| **Dilder ref** | U7 |

---

## What Is This Part?

The BH1750FVI is a **digital ambient light sensor** that measures the brightness of its environment and reports the result as a **lux value over I2C**. No ADC is needed on the microcontroller side — you send a "measure" command, wait, and read back a 16-bit number that directly represents illuminance in lux.

Inside, it contains:
- A photodiode with a spectral response filter matched to the human eye
- An integration amplifier that accumulates photocurrent over time
- A 16-bit analog-to-digital converter
- Digital logic that converts the raw count into a calibrated lux value
- An I2C slave interface

The result: you ask the chip "how bright is it?" and it answers with a number like 342, meaning 342 lux (a well-lit living room). No calibration curves, no voltage dividers, no analog-to-digital conversion on the ESP32.

In the Dilder, it provides:
- **Day/night detection** — drives the pet's sleep/wake cycle based on real ambient light
- **Screen brightness adaptation** — dim the e-paper refresh strategy in darkness
- **"Hiding in pocket" detection** — near-zero lux triggers pocket/bag behavior
- **Light-based gameplay events** — sudden brightness changes startle the pet, sustained darkness makes it scared or sleepy
- **Energy mechanics** — bright light = active daytime, darkness = time to rest

---

## How Photodiode Light Sensors Work

### The Photodiode

At the heart of the BH1750 is a **photodiode** — a semiconductor junction that converts photons (light particles) into electrical current.

```
    Photon (light)
        │
        ▼ ─ ─ ─ hν (energy = Planck's constant × frequency)
    ┌───────────┐
    │  P-type   │  ← Holes (positive carriers)
    │───────────│  ← Depletion region (electric field zone)
    │  N-type   │  ← Electrons (negative carriers)
    └───────────┘
        │
        ▼
    Photocurrent (I_ph)
```

When a photon with sufficient energy strikes the depletion region of the PN junction, it knocks an electron free from the crystal lattice, creating an **electron-hole pair**. The built-in electric field across the depletion region sweeps the electron toward the N-side and the hole toward the P-side. This movement of charge is a tiny current — the **photocurrent**.

The photocurrent is proportional to the number of photons hitting the junction per second. More light = more photons = more electron-hole pairs = more current. At typical indoor lighting (~500 lux), the photocurrent is on the order of **nanoamps to microamps** — far too small for a microcontroller ADC to read directly.

### Integration — Accumulating Light Over Time

Instead of trying to measure the tiny photocurrent instantaneously, the BH1750 uses **integration** — it accumulates charge over a fixed time period using a capacitor:

```
                      Reset switch
                          │
    Photodiode      ┌─────┤
        │           │     │
        ▼           │   ┌─┴─┐
    ┌───┤───┐       │   │   │
    │  I_ph │───────┤   │ C │  Integration
    └───┤───┘       │   │   │  capacitor
        │      ┌────┘   └─┬─┘
        │      │     ─    │
        │    ──┤──  Op    ├──────► V_out
        │      │   Amp    │
        │      └────┬─────┘
        │           │
       GND         GND

    V_out rises linearly as charge accumulates:

    Voltage
    across C
        │          ╱ Bright light (steep slope)
        │        ╱
        │      ╱─── Dim light (gentle slope)
        │    ╱  ╱
        │  ╱  ╱
        │╱__╱_____________
        └─────────────────── Time
        0    Integration
             period
```

The integration capacitor starts at zero. Photocurrent flows in and the voltage across the capacitor rises steadily. The brighter the light, the faster the voltage rises. After a fixed integration time (120ms in high-resolution mode), the voltage is sampled by the ADC, and then the capacitor is reset to zero for the next measurement.

This integration approach has a key advantage: it **averages out noise**. Random fluctuations in the photocurrent (shot noise, thermal noise) cancel out over the integration period, giving a much cleaner reading than a single instantaneous sample. Longer integration time = better signal-to-noise ratio = finer resolution.

### The ADC — From Charge to Lux

After the integration period, the accumulated voltage is fed to a **16-bit ADC** (analog-to-digital converter). This converts the voltage into a digital count from 0 to 65535.

```
    Accumulated      ┌──────────────┐     16-bit
    voltage  ───────►│   16-bit     ├────► digital
    (analog)         │     ADC      │      count
                     └──────────────┘

    The internal logic then applies a calibration factor:

    Lux = Digital count / 1.2  (in high-resolution mode)
```

The BH1750's internal logic divides the raw ADC count by 1.2 to produce the final lux value. This calibration factor is set at the factory and accounts for the photodiode's spectral response, the integration gain, and the optical characteristics of the package window.

The result is a 16-bit lux value from 1 to 65535 lux, which you read directly over I2C. No math needed on the ESP32 — the number you read *is* the lux.

### Spectral Response — Seeing Like a Human Eye

Not all light sensors are equal. A raw silicon photodiode responds to a wide range of wavelengths, including infrared (which humans cannot see). This means a bare photodiode would report a TV remote's IR beam as "bright light" even though the room looks dark to you.

The BH1750 solves this with a **spectral response filter** built into the package that shapes the photodiode's response to approximate the **CIE photopic luminosity function** — the standard curve describing how the human eye perceives brightness:

```
    Relative
    Response
    1.0 │         ╭──╮
        │        ╱    ╲         ← Human eye (CIE photopic)
        │       ╱      ╲          peaks at 555nm (green)
    0.5 │      ╱        ╲
        │     ╱          ╲
        │    ╱            ╲
        │   ╱              ╲
    0.0 │──╱────────────────╲──────
        400    500    600    700    800  nm
        Violet Blue  Green  Red    IR
              Visible spectrum
```

The human eye is most sensitive to green light (555 nm) and less sensitive to blue and red. The BH1750's filter attenuates infrared and ultraviolet while preserving the visible spectrum, so the sensor's output closely matches how bright a scene *appears* to a human — which is exactly what "lux" measures.

### Why This Is Better Than a Raw LDR

A **photoresistor** (LDR — Light Dependent Resistor) is the simplest light sensor: a resistor whose resistance decreases with light. It's cheap (~$0.05) and requires only a voltage divider and an ADC pin. So why not use one?

```
    LDR approach:                    BH1750 approach:

    3.3V ──┬── ADC pin              3.3V ──── VCC
           │                                   │
          [LDR]                         ┌──────┴──────┐
           │                            │   BH1750    │
          [R]                           │  (does all  │
           │                            │  the work)  │
          GND                           └──────┬──────┘
                                          SDA  SCL
    Output: arbitrary                        │    │
    analog voltage                     Output: lux value
    (needs calibration,                (calibrated, linear,
    non-linear, drifts                 temperature-stable,
    with temperature)                  matches human eye)
```

| Factor | LDR | BH1750 |
|--------|-----|--------|
| Output | Arbitrary analog voltage | Calibrated lux value |
| Linearity | Logarithmic (non-linear) | Linear across range |
| Spectral match | Poor (responds to IR) | Matches human eye |
| Temperature drift | Significant | Internally compensated |
| ADC pin needed | Yes (consumes ESP32 ADC) | No (I2C digital) |
| Calibration | Required per-unit | Factory calibrated |
| Resolution | Limited by MCU ADC (12-bit) | 16-bit (1 lux) |
| Price | ~$0.05 | ~$0.49 |
| Board space | Resistor + LDR + routing | Single IC + decoupling cap |

The LDR is cheaper, but it gives you a number that means nothing without a calibration curve specific to that LDR, that resistor value, that ADC reference voltage, and that temperature. The BH1750 gives you lux — a universal unit you can compare against published tables and use directly in code.

---

## Why This Part

| Factor | BH1750FVI | VEML7700 | OPT3001 | TSL2561 | Simple LDR |
|--------|-----------|----------|---------|---------|------------|
| **Price** | **~$0.49** | ~$0.85 | ~$1.80 | ~$2.50 | ~$0.05 |
| **JLCPCB/LCSC** | **C78960 (in stock)** | C161445 | Limited | Limited | Generic |
| **Interface** | I2C (simple) | I2C | I2C | I2C | Analog (ADC) |
| **Range** | 1-65535 lux | 0-120k lux | 0.01-83k lux | 0.1-40k lux | Varies |
| **Resolution** | 1 lux | 0.0036 lux | 0.01 lux | Variable | MCU ADC |
| **Output** | Direct lux | Direct lux | Direct lux | Raw counts | Voltage |
| **Configuration** | Minimal | Moderate | Moderate | Complex | None |
| **Arduino/ESP32 libs** | **Many (mature)** | Several | Few | Many | N/A |
| **Package size** | 3.0x1.6mm | 4.0x3.15mm | 2.0x2.0mm | 3.9x2.6mm | 5mm+ |
| **Power (active)** | 120 uA | 45 uA | 1.8 uA | 240 uA | ~0 |
| **Power (sleep)** | <1 uA | 0.5 uA | 0.4 uA | 15 uA | ~0 |

**Why the BH1750 wins for Dilder:**

1. **Price** — At $0.49 it's the cheapest digital light sensor with real lux output. The VEML7700 is nearly double; the OPT3001 is 4x.

2. **JLCPCB availability** — LCSC part C78960 is a basic part (no extended library surcharge). VEML7700 is available but extended. OPT3001 and TSL2561 have spotty LCSC stock.

3. **Simplicity** — Power on, send one command ("measure in high-res mode"), wait 120ms, read two bytes. That's it. No register configuration, no gain/timing tables, no interrupt setup. The VEML7700 and OPT3001 require multi-register configuration with gain and integration time settings.

4. **Library ecosystem** — The BH1750 has been used in Arduino projects since ~2012. Multiple mature, well-tested libraries exist (BH1750 by Christopher Laws is the de-facto standard). ESP32 support is excellent.

5. **Resolution is sufficient** — The Dilder needs to know "is it bright, dim, or dark?" for gameplay. 1-lux resolution is more than adequate. The VEML7700's 0.0036-lux resolution is impressive but unnecessary — the Dilder is a virtual pet, not a photography light meter.

6. **1-65535 lux range covers all gameplay scenarios** — moonlight (~1 lux) through direct indoor sunlight near a window (~10,000+ lux). The sensor saturates at 65535 lux (direct sunlight), but the Dilder just treats anything above ~1000 as "very bright."

---

## Key Specifications

| Parameter | Value |
|-----------|-------|
| Operating voltage | 2.4V to 3.6V |
| I2C address | 0x23 (ADDR pin LOW) or 0x5C (ADDR pin HIGH) |
| Measurement range | 1 to 65535 lux |
| Resolution (high-res) | 1 lux |
| Resolution (low-res) | 4 lux |
| Accuracy | ±20% (typical variation between units) |
| Measurement time (high-res) | 120 ms (typical), 180 ms (max) |
| Measurement time (low-res) | 16 ms (typical), 24 ms (max) |
| Current (active, measuring) | 120 uA (typical) |
| Current (power down) | <1 uA (typically 0.01 uA) |
| Spectral response peak | 560 nm (close to human eye's 555 nm) |
| Interface | I2C, up to 400 kHz (Fast mode) |
| 50/60 Hz rejection | Built-in (integration time chosen to reject flicker) |
| Operating temperature | -40°C to +85°C |
| Package | WSOF-6 (3.0 x 1.6 x 0.9 mm) |

**Note on 50/60 Hz rejection:** Artificial lighting powered by mains AC flickers at 100 Hz (50 Hz mains) or 120 Hz (60 Hz mains). The BH1750's high-resolution integration time of 120ms is exactly one period of 100 Hz / one period of 120 Hz (or close enough), which means the flicker averages out over the integration window. This prevents readings from jumping up and down under fluorescent or LED lighting.

---

## Operating Modes

The BH1750 has several measurement modes, selected by sending a single opcode byte over I2C:

| Mode | Opcode | Resolution | Meas. Time | Description |
|------|--------|------------|------------|-------------|
| **Continuous H-Res** | 0x10 | 1 lux | 120 ms | Measures continuously. Read anytime for latest value. |
| **Continuous H-Res2** | 0x11 | 0.5 lux | 120 ms | Like H-Res but resolution is 0.5 lux (value is 2x, divide by 2). |
| **Continuous L-Res** | 0x13 | 4 lux | 16 ms | Fast but coarse. Good for rapid change detection. |
| **One-Time H-Res** | 0x20 | 1 lux | 120 ms | Measures once, then auto-powers down. **Best for battery life.** |
| **One-Time H-Res2** | 0x21 | 0.5 lux | 120 ms | One-shot with 0.5 lux resolution, then power down. |
| **One-Time L-Res** | 0x23 | 4 lux | 16 ms | Fastest one-shot, then power down. |
| **Power Down** | 0x00 | — | — | Shuts down. Current drops to <1 uA. |
| **Power On** | 0x01 | — | — | Wakes from power down. Must send before first measurement. |
| **Reset** | 0x07 | — | — | Resets the data register (sets to 0). Does not change mode. |

**Recommended mode for Dilder:** **One-Time H-Resolution (0x20)**. The Dilder only needs a light reading every few seconds (for sleep/wake cycle decisions). Using one-time mode means:

1. Send 0x20 to trigger a measurement
2. Wait 180ms (worst case)
3. Read 2 bytes — this is the lux value (big-endian, divide by 1.2)
4. The sensor automatically powers down to <1 uA
5. Repeat when the next reading is needed

This approach consumes ~120 uA for 180ms every few seconds, then <1 uA the rest of the time. Average current at one reading per 5 seconds: **~4.3 uA** — negligible in the power budget.

```
    Power consumption timeline (One-Time mode, 1 reading per 5 seconds):

    Current
    (uA)
    120 │  ┌──┐                              ┌──┐
        │  │  │                              │  │
        │  │  │                              │  │
        │  │  │                              │  │
      1 │──┘  └──────────────────────────────┘  └─────
        └──┬──┬──────────────────────────────┬──┬─────
           0  180ms                          5s  5.18s
              Measuring        Powered down        Measuring
```

---

## Pin Connections on Dilder Board

The BH1750FVI has 6 pins in a WSOF-6 package:

| BH1750 Pin | Pin # | Connect To | Net | Notes |
|------------|-------|------------|-----|-------|
| VCC | 2 | 3.3V | 3V3 | Power supply (2.4-3.6V) |
| GND | 3 | Ground | GND | Ground reference |
| SDA | 5 | ESP32 GPIO16 | I2C_SDA | I2C data (10k pull-up via R4) |
| SCL | 6 | ESP32 GPIO17 | I2C_SCL | I2C clock (10k pull-up via R5) |
| ADDR | 4 | GND | GND | Sets I2C address to 0x23 |
| DVI | 1 | Not connected | — | Data valid input; can be left floating per datasheet |

**Pin notes:**

- **ADDR to GND** — This sets the I2C address to 0x23. If tied to VCC, the address would be 0x5C. Since no other device on the Dilder's I2C bus uses 0x23, GND is the simpler choice (no additional resistor needed).

- **DVI (Data Valid Input)** — This pin is an active-low input that, when pulled low, indicates to the sensor that the I2C bus is ready. Per the datasheet, this pin can be left floating (unconnected) for normal operation. Some designs tie it to VCC via a 1k pull-up as a precaution, but this is not required and the Dilder leaves it unconnected.

- **Existing pull-ups** — The I2C bus already has 10k pull-up resistors (R4 on SDA, R5 on SCL) installed for the LIS2DH12 accelerometer. These same pull-ups serve all I2C devices on the bus, including the BH1750. No additional pull-ups are needed.

---

## Application Circuit

```
                         3.3V
                          │
              ┌───────────┼───────────┐
              │           │           │
         R4 [10k]    R5 [10k]       [100nF] C_decoupling
              │           │           │    (ceramic, close
              │           │           │     to VCC pin)
              │           │           │
ESP32 GPIO16 ─┤           │           │
   (SDA)      │  GPIO17 ──┤           │
              │  (SCL)    │           │
              │           │           │
         .────┤───────────┤───────────┤───────.
         │   SDA        SCL        VCC        │
         │                                    │
         │            BH1750FVI-TR            │
         │                                    │
         │   DVI=NC    ADDR        GND        │
         '────┤──────────┤───────────┤────────'
              │          │           │
             N/C        GND         GND
                         │           │
                         └─────┬─────┘
                               │
                              GND
```

**Layout notes:**

- Place the 100nF decoupling capacitor as close to the BH1750's VCC pin as possible (within 2-3mm). This filters high-frequency noise from the power supply that could affect measurement accuracy.
- Keep the I2C traces short and away from high-speed switching signals (SPI clock, USB data). The BH1750 uses I2C at up to 400 kHz — it's not particularly sensitive to trace length, but good practice applies.
- The sensor has a small optical window on top of the package. Ensure no tall components or solder bridges obstruct light from reaching the sensor surface.
- If mounting the sensor under a case, the case material must be translucent or have an opening above the sensor. Opaque plastic will block all light.

---

## Common Mistakes and Gotchas

1. **Must send Power On (0x01) before the first measurement.** After power-up or reset, the BH1750 starts in power-down mode. If you immediately send a measurement command without first sending 0x01, the sensor ignores it and returns stale/zero data. The sequence is: Power On → wait → Measurement command → wait → Read.

2. **ADDR pin must be definitively HIGH or LOW — never floating.** A floating ADDR pin may settle to an indeterminate voltage, causing the I2C address to be unpredictable. On the Dilder, ADDR is tied directly to GND (0x23). Some breakout boards leave ADDR floating — this is a common source of "sensor not responding" bugs.

3. **180ms startup time after power-on.** The datasheet specifies up to 180ms for the first high-resolution measurement to complete. If you read too early, you get 0x0000. Add a 200ms delay after the measurement command to be safe, or poll until the sensor ACKs a read request.

4. **Direct sunlight saturates at 65535 lux.** The sensor's 16-bit output maxes out at 65535. Direct sunlight is ~100,000 lux, so outdoor readings in full sun will be clipped. For the Dilder this is fine — "very bright" is "very bright" regardless of whether it's 65535 or 100000.

5. **50/60 Hz flicker can affect low-resolution mode.** The 16ms integration time in low-resolution mode does not span a full mains cycle. Under some artificial lighting, low-res readings may fluctuate. High-resolution mode (120ms) is specifically designed to reject this. Use high-res for stable readings.

6. **I2C address 0x23 conflict with some devices.** The HMC5883L magnetometer also uses address 0x23. If adding a magnetometer to the Dilder in the future, either use the BH1750 at address 0x5C (ADDR=HIGH) or choose a different magnetometer (the QMC5883L uses 0x0D, no conflict).

7. **Optical path matters.** The sensor measures light that reaches its photodiode through the package window. Dirt, conformal coating, or a finger over the sensor will obviously reduce readings. When testing on a breadboard, make sure the sensor faces upward with no obstructions.

8. **Temperature coefficient.** Although internally compensated, extreme temperatures can shift readings by a few percent. At the Dilder's operating range (indoors, ~15-35°C), this is negligible.

---

## Lux Reference Values

A reference table for interpreting raw lux readings in code — useful for setting thresholds in the Dilder's gameplay:

| Condition | Typical Lux | Dilder Behavior |
|-----------|-------------|-----------------|
| Moonlight (clear night) | ~1 | Deep sleep mode |
| Very dark room | ~5 | Sleep mode triggers (if energy low) |
| Dim room / nightlight | ~10-50 | Pet gets drowsy, yawns |
| Hallway / bathroom | ~50-100 | Low activity, subdued mood |
| Living room (evening) | ~100-300 | Standard indoor operation |
| Office / well-lit room | ~300-500 | Active mode, normal energy decay |
| Overcast daylight (indoor near window) | ~500-1000 | High energy, outdoor-adjacent |
| Overcast outdoor | ~1,000-10,000 | "Outside" detection threshold |
| Full daylight (shade) | ~10,000-25,000 | Definitely outside |
| Direct sunlight | ~50,000-100,000+ | Saturates at 65535 (sensor max) |
| In a pocket / bag | 0-5 | "Hiding" — pet reacts (lonely, scared, or sleeping) |
| Sudden change >300 lux in <5s | (delta) | Startled reaction, forced wake |

**Suggested threshold values for Dilder firmware:**

```c
#define LUX_PITCH_BLACK    5      // Pocket, bag, closed drawer
#define LUX_DARK          10      // Sleep trigger (if energy low)
#define LUX_DIM          100      // Drowsy range
#define LUX_NORMAL       300      // Active indoor
#define LUX_BRIGHT      1000      // Near window / outdoor
#define LUX_SUNLIGHT   10000      // Definitely outside
#define LUX_STARTLED_DELTA 300    // Sudden change threshold
```

---

## I2C Bus Sharing

The BH1750 shares the I2C bus (GPIO16/GPIO17) with all other I2C peripherals on the Dilder. Each device has a unique 7-bit address, so they coexist on the same two wires without conflict:

```
ESP32-S3 GPIO16 (SDA) ──┬──────────────────────────────────── 3V3
ESP32-S3 GPIO17 (SCL) ──┼──┬───────────────────────────────── 3V3
                         │  │        via R4 (10k) and R5 (10k)
                         │  │
                    ┌────┤──┤────┐
                    │   SDA SCL  │
                    │  LIS2DH12  │  Address: 0x18
                    └────────────┘
                         │  │
                    ┌────┤──┤────┐
                    │   SDA SCL  │
                    │  BH1750FVI │  Address: 0x23
                    └────────────┘
                         │  │
                    (future devices)
```

**Current I2C address map:**

| Address | Device | Function |
|---------|--------|----------|
| 0x18 | LIS2DH12TR | Accelerometer / pedometer |
| 0x23 | BH1750FVI | Ambient light sensor |

No address conflicts exist. The I2C standard supports up to 112 devices on a single bus (addresses 0x08-0x77), and at 400 kHz, reading from two sensors sequentially takes under 1ms total.

**Bus capacitance:** Each I2C device and its trace routing adds capacitance to the bus. The I2C spec limits total bus capacitance to 400pF. With two devices and short traces on the Dilder's compact 30x70mm board, bus capacitance is well under 50pF — no concern. Even with 4-5 future sensors, the 10k pull-ups and short traces will keep the bus healthy.

---

## History and Background

**ROHM Semiconductor** was founded in **1958 in Kyoto, Japan** by Kenichiro Sato. The company name originally stood for "Resistor Ohm" — they started by manufacturing small resistors. Over the decades they expanded into ICs, optoelectronics, power semiconductors, and sensors.

ROHM is a vertically integrated manufacturer, meaning they control the entire process from silicon wafer fabrication to final packaging — all done in-house. Their main fabrication facilities are in Kyoto and Shiga Prefecture (Japan), with assembly plants across Southeast Asia.

The BH1750FVI was introduced in the late 2000s and became one of the most widely used digital ambient light sensors in the hobbyist and maker community, largely due to:
- **Low cost** and wide availability on breakout boards (Adafruit, SparkFun, generic modules)
- **Extreme simplicity** — one of the easiest I2C sensors to interface with
- **Accurate spectral response** — unusual for a sub-$1 sensor

It is commonly found in:
- Smartphone and tablet automatic brightness adjustment
- Industrial lighting controllers
- Agricultural greenhouse monitoring
- Weather stations
- Display backlight control

ROHM remains headquartered in Kyoto and is publicly traded on the Tokyo Stock Exchange. They employ over 20,000 people and had revenue of approximately $4.5 billion USD in 2024. Other well-known ROHM products include the BD series of voltage regulators and the ML series of laser diodes used in optical disc drives.

---

## Datasheet and Sources

- **ROHM official datasheet:** [BH1750FVI Datasheet PDF](https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf)
- **LCSC product page:** [C78960](https://www.lcsc.com/product-detail/C78960.html)
- **Arduino library (Christopher Laws):** [github.com/claws/BH1750](https://github.com/claws/BH1750) — the de-facto standard library, supports all modes, ESP32 compatible
- **ESP-IDF component:** [esp-idf-lib BH1750](https://github.com/UncleRus/esp-idf-lib/tree/master/components/bh1750) — native ESP-IDF driver if not using Arduino framework
- **Wikipedia — Lux:** [en.wikipedia.org/wiki/Lux](https://en.wikipedia.org/wiki/Lux)
- **Wikipedia — Photodiode:** [en.wikipedia.org/wiki/Photodiode](https://en.wikipedia.org/wiki/Photodiode)
- **CIE Photopic Luminosity Function:** [en.wikipedia.org/wiki/Luminosity_function](https://en.wikipedia.org/wiki/Luminosity_function)
- **ROHM Semiconductor corporate:** [rohm.com](https://www.rohm.com/)
