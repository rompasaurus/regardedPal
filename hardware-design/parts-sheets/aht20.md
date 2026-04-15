# AHT20 — Digital Temperature & Humidity Sensor

## Table of Contents

- [Quick Reference](#quick-reference)
- [What Is This Part?](#what-is-this-part)
- [How Capacitive Humidity Sensors Work](#how-capacitive-humidity-sensors-work)
  - [The Sensing Element](#the-sensing-element)
  - [From Humidity to Capacitance Change](#from-humidity-to-capacitance-change)
  - [The Temperature Measurement](#the-temperature-measurement)
  - [Signal Conditioning and ADC](#signal-conditioning-and-adc)
- [Why This Part](#why-this-part)
- [Key Specifications](#key-specifications)
- [Pin Connections on Dilder Board](#pin-connections-on-dilder-board)
- [Application Circuit](#application-circuit)
- [Common Mistakes and Gotchas](#common-mistakes-and-gotchas)
- [I2C Bus Sharing](#i2c-bus-sharing)
- [Datasheet and Sources](#datasheet-and-sources)

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Manufacturer** | Aosong (Guangzhou, China) |
| **Part Number** | AHT20 |
| **Function** | Digital temperature and humidity sensor (I2C) |
| **Package** | DFN-6 (3 x 3 x 1 mm) |
| **LCSC** | [C2757850](https://www.lcsc.com/product-detail/C2757850.html) |
| **Price (qty 5)** | ~$0.43 |
| **Dilder ref** | U6 |

---

## What Is This Part?

The AHT20 is a **combined temperature and humidity sensor** in a single 3mm x 3mm chip. It measures the air temperature and relative humidity around the Dilder and converts both into digital numbers the ESP32 can read over I2C.

It's remarkably small — about the size of a grain of rice — yet inside it contains:
- A polymer capacitive humidity sensing element that physically absorbs water molecules from the air
- A bandgap temperature sensor
- A 20-bit analog-to-digital converter for each measurement
- A calibration engine with factory-trimmed coefficients stored in OTP memory
- An I2C communication interface

In the Dilder, it provides:
- **Ambient temperature for gameplay weather sync** — the pet reacts to real-world temperature. Too hot (>28C) makes the octopus grumpy; too cold (<15C) makes it sad. The "comfort zone" of 18-24C boosts the chill emotion weight.
- **Humidity for "comfort" mechanics** — relative humidity feeds into the environment modifier for stat decay. The octopus actually likes high humidity (>70% RH) because, well, it's an octopus. Dry air (<30% RH) makes it uncomfortable.
- **Sleep mode awareness of environment** — during low-power sleep, the ESP32 can wake periodically, take a quick AHT20 reading (~80ms), update the pet's environmental state, and go back to sleep. At <0.25uA standby current, the sensor adds virtually nothing to the sleep power budget.

---

## How Capacitive Humidity Sensors Work

Most cheap humidity sensors (like the blue DHT11 module popular with Arduino beginners) use a resistive sensing approach. The AHT20 uses a **capacitive** approach, which is more accurate, more stable over time, and less affected by contamination.

### The Sensing Element

At the heart of the AHT20 is a tiny parallel-plate capacitor. But instead of air or ceramic between the plates, there's a **hygroscopic polymer** — a thin film of material that readily absorbs and releases water molecules from the surrounding air.

```
Cross-section of the humidity sensing element:

    Humid air (water molecules: o)
    o   o       o   o
    ↓   ↓       ↓   ↓
┌──────────────────────────┐
│ ░░░ Porous top electrode ░░░│  ← Permeable (lets moisture through)
├──────────────────────────┤
│                              │
│  Polymer dielectric film     │  ← Absorbs/releases H2O molecules
│  (polyimide, ~1 micrometer)  │
│                              │
├──────────────────────────┤
│▓▓▓ Bottom electrode ▓▓▓▓▓▓▓│  ← Solid (sealed)
└──────────────────────────┘
        Silicon substrate
```

The top electrode is porous — it has tiny holes or is made from a permeable material — so water vapor molecules can pass through it and reach the polymer film underneath. The bottom electrode is solid, sitting on the silicon die.

### From Humidity to Capacitance Change

The capacitance of a parallel plate capacitor is:

```
C = epsilon_0 * epsilon_r * A / d

Where:
  C         = capacitance (farads)
  epsilon_0 = permittivity of free space (8.854 x 10^-12 F/m)
  epsilon_r = relative permittivity (dielectric constant) of the material
  A         = plate area
  d         = distance between plates
```

Here's the key insight: **the dielectric constant of the polymer changes when it absorbs water**. Dry polyimide has a dielectric constant of about 3.5. Water has a dielectric constant of about 80. When the polymer absorbs water molecules, its effective dielectric constant increases, which increases the capacitance.

```
Dry air (20% RH):                    Humid air (80% RH):

┌────────────────┐                   ┌────────────────┐
│░░░ Top plate ░░│                   │░░░ Top plate ░░│
├────────────────┤                   ├────────────────┤
│  Polymer       │                   │o Polymer  o  o │
│    (few H2O)   │  C = C_dry       │ o (many H2O) o │  C = C_dry + delta_C
│                │                   │  o    o  o     │
├────────────────┤                   ├────────────────┤
│▓▓ Bottom plate▓│                   │▓▓ Bottom plate▓│
└────────────────┘                   └────────────────┘

  epsilon_r ~ 3.5                      epsilon_r ~ 5-6
  Lower capacitance                    Higher capacitance
```

The change is roughly linear: a 1% increase in relative humidity produces a proportional increase in capacitance. The AHT20's internal circuitry measures this capacitance change with high precision (20-bit resolution means it can distinguish over 1 million discrete levels across the humidity range).

The response isn't instant — water molecules need time to diffuse into and out of the polymer. Typical response time is a few seconds, which is why the datasheet specifies an ~80ms measurement time (for the electronic conversion) but recommends not polling faster than every 2 seconds (to let the polymer equilibrate).

### The Temperature Measurement

Temperature is measured using a completely separate element: a **bandgap temperature sensor**. This exploits a fundamental property of semiconductor physics.

A silicon PN junction (a diode) has a forward voltage that decreases predictably with temperature — about -2 mV/C. By running two identical transistors at different current densities and measuring the difference in their base-emitter voltages (delta V_BE), you get a voltage that is Proportional To Absolute Temperature (PTAT):

```
                 ┌─────────┐
   I1 ──────────►│ Q1      │──┐
                 │ (1x)    │  │
                 └─────────┘  │
                              ├──► Delta_VBE = (kT/q) * ln(N)
                 ┌─────────┐  │
   I2 = N*I1 ──►│ Q2      │──┘     k = Boltzmann constant
                 │ (Nx)    │        T = temperature (Kelvin)
                 └─────────┘        q = electron charge
                                    N = current density ratio
```

This voltage difference is directly proportional to absolute temperature (in Kelvin), independent of process variations. The "bandgap" name comes from the fact that the technique was originally used to create a voltage reference equal to the silicon bandgap voltage (~1.2V), but the same circuit topology gives you a temperature-proportional signal for free.

The AHT20 achieves +/-0.3C accuracy, which means the factory calibration and trimming are quite good. For context, a clinical thermometer needs +/-0.1C, so the AHT20 isn't medical grade — but it's more than adequate for "is the room hot or cold."

### Signal Conditioning and ADC

Both the humidity capacitance and the temperature voltage are tiny analog signals contaminated with noise. The AHT20 processes them through:

```
Sensing       Amplification    Analog-to-Digital     Calibration
Element  ──►  & Filtering  ──►  Conversion (ADC)  ──►  & Output
                                   20-bit

┌──────┐    ┌───────────┐    ┌─────────────┐    ┌──────────┐
│ Cap  │───►│ Charge     │───►│ Sigma-Delta  │───►│ Factory  │──► I2C
│sensor│    │ amplifier  │    │ ADC (20-bit) │    │ cal      │    out
└──────┘    │ + filter   │    └─────────────┘    │ coeffs   │
            └───────────┘                         └──────────┘
┌──────┐    ┌───────────┐    ┌─────────────┐         │
│Temp  │───►│ Diff amp   │───►│ Sigma-Delta  │────────┘
│sensor│    │ + filter   │    │ ADC (20-bit) │
└──────┘    └───────────┘    └─────────────┘
```

The sigma-delta ADC (same type used in the LIS2DH12 accelerometer) achieves high resolution by oversampling at a high rate and digitally filtering the result. 20 bits gives over 1 million counts of resolution — far more than the sensor's actual accuracy, but the extra resolution means you can average readings to reduce noise.

Factory calibration coefficients are burned into the chip's one-time-programmable (OTP) memory during manufacturing. These correct for:
- Offset errors (the sensor reads 32% RH when actual is 30%)
- Gain errors (the sensor's slope doesn't match the ideal curve)
- Cross-sensitivity (temperature affecting humidity reading and vice versa)

The calibrated output is then available over I2C as raw 20-bit values, which the host MCU converts to physical units using the formulas in the datasheet:

```
Relative Humidity (%) = (raw_humidity / 2^20) * 100

Temperature (C) = (raw_temperature / 2^20) * 200 - 50
```

---

## Why This Part

The original Dilder design documents referenced a BME280 for temperature/humidity (~$4, Bosch). The AHT20 is a much better fit for this project:

| Factor | AHT20 | SHT40 | SHTC3 | DHT11 | BME280 |
|--------|-------|-------|-------|-------|--------|
| **Price (LCSC qty 5)** | **$0.43** | $1.20 | $0.90 | $0.80 | $3.50 |
| **JLCPCB basic part** | Yes | No | No | No | No |
| **Package** | DFN-6, 3x3mm | DFN-4, 1.5x1.5mm | DFN-4, 2x2mm | Through-hole 4-pin | LGA-8, 2.5x2.5mm |
| **Interface** | I2C | I2C | I2C | One-wire (bit-bang) | I2C/SPI |
| **Temp accuracy** | +/-0.3C | +/-0.2C | +/-0.2C | +/-2C | +/-1C |
| **Humidity accuracy** | +/-2% RH | +/-1.8% RH | +/-2% RH | +/-5% RH | +/-3% RH |
| **Supply voltage** | 2.0-5.5V | 1.08-3.6V | 1.62-3.6V | 3.3-5.5V | 1.71-3.6V |
| **Sleep current** | <0.25uA | 0.08uA | 0.3uA | N/A | 0.1uA |
| **Measurement current** | ~23uA | ~37uA | ~260uA | ~300uA | ~350uA |
| **Extra features** | None | Heater | Heater | None | Pressure sensor |
| **I2C address** | 0x38 | 0x44 | 0x70 | N/A | 0x76/0x77 |

**Why AHT20 wins for Dilder:**

1. **Cheapest option at $0.43** — less than half the price of the next cheapest alternative. For a hobby project with a tight BOM budget (~$4.26/board), every penny matters.

2. **Available as JLCPCB basic part** — this means JLCPCB keeps it in stock for SMT assembly with no extended part fee ($3 surcharge per unique extended part). The SHT40 and SHTC3 are extended parts at JLCPCB, which adds cost.

3. **Good enough accuracy** — +/-0.3C temperature and +/-2% RH humidity is plenty for gameplay mechanics. The pet doesn't need to know the temperature to 0.1C resolution. It just needs to know "is it hot, cold, or comfortable?"

4. **Standard I2C at 0x38** — no address conflict with the LIS2DH12 (0x18) or BH1750 (0x23) on the shared bus.

5. **Wide voltage range (2.0-5.5V)** — works directly at 3.3V with no level shifting needed, and would even work at 5V if the design ever changed.

6. **Ultra-low sleep current (<0.25uA)** — contributes negligibly to the Dilder's sleep power budget. The ESP32 in deep sleep (~10uA) dominates by 40x.

The BME280 adds a barometric pressure sensor, which would be interesting for weather prediction ("your pet can sense a storm coming"), but at 8x the cost it's not justified for v0.4 of the board. The DHT11 is ruled out immediately — it uses a non-standard one-wire protocol that requires precise timing (not I2C), it's through-hole only (can't be machine-assembled), and its +/-2C accuracy is terrible.

---

## Key Specifications

| Parameter | Value |
|-----------|-------|
| Supply voltage | 2.0V to 5.5V |
| I2C address | 0x38 (fixed, not configurable) |
| I2C speed | Standard (100 kHz) and Fast (400 kHz) |
| Temperature range | -40C to +85C |
| Temperature accuracy | +/-0.3C (typical, at 25C) |
| Temperature resolution | 0.01C (20-bit raw) |
| Humidity range | 0% to 100% RH |
| Humidity accuracy | +/-2% RH (typical, 25C, 20-80% range) |
| Humidity resolution | 0.024% RH (20-bit raw) |
| Measurement current | ~23uA (during conversion) |
| Standby current | <0.25uA |
| Measurement time | ~80ms (typical for both temp + humidity) |
| Response time (humidity) | ~8 seconds (63% step response in still air) |
| Package | DFN-6, 3.0 x 3.0 x 1.0 mm |
| Operating temperature | -40C to +85C |
| Long-term drift (humidity) | <0.25% RH/year |

---

## Pin Connections on Dilder Board

The AHT20 comes in a 6-pin DFN package. Not all pins are used — pin 3 and pin 4 are listed as NC (no connect) in the datasheet.

| AHT20 Pin | Pin # | Connect To | Net | Notes |
|-----------|-------|------------|-----|-------|
| VDD | 1 | 3.3V | 3V3 | Power supply (2.0-5.5V range) |
| SDA | 2 | ESP32 GPIO16 | I2C_SDA | I2C data (shared bus, 10k pull-up R4) |
| GND | 3 | Ground | GND | Ground |
| NC | 4 | — | — | No connect (leave unconnected) |
| NC | 5 | — | — | No connect (leave unconnected) |
| SCL | 6 | ESP32 GPIO17 | I2C_SCL | I2C clock (shared bus, 10k pull-up R5) |

The I2C pull-up resistors R4 (10k on SDA) and R5 (10k on SCL) are already on the Dilder board for the LIS2DH12 accelerometer. **No additional pull-ups are needed** — the AHT20 simply connects to the same SDA and SCL lines. One set of pull-ups serves the entire I2C bus regardless of how many devices are on it.

---

## Application Circuit

```
                       3.3V (3V3 rail)
                         │
                         │
              ┌──────────┼──────────────────────────────────┐
              │          │                                    │
              │        ┌─┴─┐                                  │
              │        │   │ C_AHT (100nF)                    │
              │        │   │ decoupling                       │
              │        └─┬─┘                                  │
              │          │                                    │
         R4 [10k]   R5 [10k]                                 │
              │          │                                    │
ESP32 GPIO16 ─┤──────────┤                                    │
   (SDA)      │          │                                    │
              │   ESP32 GPIO17                                │
              │    (SCL)  │                                    │
              │          │                                    │
         .────┤──────────┤────────────────────────────────────┤───.
         │   SDA       SCL                                  VDD   │
         │                                                        │
         │                    AHT20                               │
         │                                                        │
         │              NC (pin 4)    NC (pin 5)                  │
         │                                                        │
         '────────────────────────┬───────────────────────────────'
                                  │
                               GND (pin 3)
                                  │
                                 GND

  Shared I2C bus (same physical wires):
  ┌─────────────────────────────────┐
  │  SDA (GPIO16) ──────────────────┤──► LIS2DH12 (U5) @ 0x18
  │                                 ├──► AHT20    (U6) @ 0x38
  │                                 └──► BH1750   (U7) @ 0x23
  │  SCL (GPIO17) ──────────────────┤──► LIS2DH12 (U5)
  │                                 ├──► AHT20    (U6)
  │                                 └──► BH1750   (U7)
  └─────────────────────────────────┘
```

**Decoupling:** A 100nF ceramic capacitor placed as close to the AHT20's VDD pin as possible. This filters high-frequency noise from the power supply that could affect measurement accuracy. The AHT20 datasheet specifically recommends a 100nF cap on VDD.

**No additional components required.** The AHT20 is one of the simplest sensors to integrate — just power, ground, and two I2C wires. No external oscillator, no reference resistors, no configuration pins.

---

## Common Mistakes and Gotchas

### 1. Forgetting the 20ms Initialization Delay

After power-up, the AHT20 needs at least **20ms** before it's ready to accept commands. During this time, it loads calibration coefficients from internal OTP memory into working registers. If you send a measurement command too early, you'll get garbage data or a NACK.

```c
// Correct startup sequence:
power_on();
delay_ms(40);                    // Datasheet says 20ms; use 40ms for margin

// Check calibration status
uint8_t status = i2c_read_byte(0x38, 0x71);
if (!(status & 0x08)) {
    // Bit 3 = calibrated flag. If not set, send init command:
    uint8_t init_cmd[] = {0xBE, 0x08, 0x00};
    i2c_write(0x38, init_cmd, 3);
    delay_ms(10);
}
```

### 2. Polling Too Fast

The AHT20 should not be read faster than **once every 2 seconds**. The datasheet is clear about this, and there are two reasons:

- **Sensor equilibration:** The humidity polymer needs time to reach equilibrium with the ambient air between readings. Polling at 10 Hz gives you 10 readings per second of a polymer that hasn't finished absorbing/releasing water — the readings will lag behind reality.
- **Self-heating:** The measurement circuit dissipates ~23uA * 3.3V = ~76 microwatts during each conversion. This is tiny, but the sensor die is also tiny. At high polling rates, the accumulated heat raises the die temperature above ambient, causing the temperature reading to drift upward and the humidity reading to drift downward (warm air holds more moisture, so the relative humidity drops).

For the Dilder, polling every 30-60 seconds is ideal. Room temperature and humidity don't change on a second-by-second basis.

### 3. Liquid Water Damage

The humidity sensor is designed to measure water **vapor** (gas-phase H2O molecules in air). If liquid water (condensation, rain, a splash) reaches the sensing element, it can:

- Saturate the polymer, causing readings to peg at 100% RH for hours
- In extreme cases, permanently shift the calibration (the polymer swells and doesn't fully recover)
- Cause corrosion of the thin-film electrodes

The AHT20 has a small PTFE membrane over the sensing element that helps block liquid water and dust while allowing vapor to pass through. But this isn't waterproofing — it's splash resistance at best.

For the Dilder (a handheld device), this means: **don't use it in the rain without a case.** The sensor should be placed where it can breathe (not sealed inside the enclosure) but is protected from direct liquid contact.

### 4. Confusing the Status/Command Protocol

The AHT20 does not use a traditional register-based I2C protocol like most sensors. Instead, it uses a command-based protocol:

```
To trigger a measurement:
  1. Write: [0xAC, 0x33, 0x00]     (trigger measurement command)
  2. Wait 80ms
  3. Read: 7 bytes                   (status + 20-bit humidity + 20-bit temp + CRC)

Byte layout of the 7-byte response:
  Byte 0:     Status (bit 7 = busy, bit 3 = calibrated)
  Bytes 1-2:  Humidity [19:4]
  Byte 3:     Humidity [3:0] | Temperature [19:16]  (shared byte!)
  Bytes 4-5:  Temperature [15:0]
  Byte 6:     CRC-8
```

Note that **byte 3 is shared** between humidity and temperature data. The upper 4 bits are the low nibble of humidity; the lower 4 bits are the high nibble of temperature. This is a common source of bugs when writing a driver from scratch.

### 5. Not Checking the Busy Bit

After sending the measurement trigger command (0xAC), you must wait for the conversion to complete. The status byte's bit 7 indicates busy:

- Bit 7 = 1: Measurement in progress, data not ready
- Bit 7 = 0: Data ready, you can read

If you read data while the busy bit is set, you'll get stale data from the previous measurement (or zeros if it's the first reading after power-up).

---

## I2C Bus Sharing

The Dilder's I2C bus on GPIO16 (SDA) and GPIO17 (SCL) is shared among three sensors. Each has a unique 7-bit address, so there are no conflicts:

| Device | I2C Address | Function |
|--------|-------------|----------|
| LIS2DH12 (U5) | 0x18 | 3-axis accelerometer |
| BH1750 (U7) | 0x23 | Ambient light sensor |
| AHT20 (U6) | 0x38 | Temperature & humidity sensor |

```
I2C Address Map (7-bit addresses, 0x00-0x7F):

0x00 ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0x0F
     ▲ reserved

0x10 ░░░░░░░░████░░░░░░░░░░░░░░░░░░░░ 0x1F
              ▲ 0x18 = LIS2DH12

0x20 ░░░░░░████░░░░░░░░░░░░░░░░░░░░░░ 0x2F
           ▲ 0x23 = BH1750

0x30 ░░░░░░░░░░░░░░░░████░░░░░░░░░░░░ 0x3F
                      ▲ 0x38 = AHT20

(No conflicts — all three addresses are well separated)
```

**How bus sharing works:** I2C is a multi-drop bus. All devices share the same two wires (SDA and SCL). The master (ESP32) selects which device to talk to by sending its 7-bit address at the start of every transaction. Only the device whose address matches will respond (by pulling SDA low for the ACK bit). All other devices ignore the traffic.

**One set of pull-ups serves the entire bus.** The 10k pull-up resistors R4 and R5 pull SDA and SCL high when no device is actively driving them low. Adding more devices to the bus does not require additional pull-ups. In fact, adding more pull-ups in parallel would lower the effective pull-up resistance, which increases the current each device must sink to pull the line low. Three devices on one bus with 10k pull-ups is completely standard and well within spec.

**Bus capacitance budget:** The I2C spec limits total bus capacitance to 400pF. Each device adds roughly 3-10pF of pin capacitance, and each centimeter of PCB trace adds about 1pF. With three devices and short traces on a 30x70mm board, total bus capacitance is well under 100pF — comfortably within budget. The 10k pull-ups combined with <100pF gives rise times well under the 300ns limit for 400 kHz Fast mode.

**Polling order in firmware:** The sensor manager polls each device sequentially. A typical cycle:

```
1. Read LIS2DH12 (0x18) — acceleration + step count    (~180us)
2. Read BH1750    (0x23) — ambient light level           (~120us)
3. Read AHT20     (0x38) — temperature + humidity        (~80ms, but only every 30s)

Total I2C bus time per poll cycle: < 1ms (excluding AHT20 wait)
```

The AHT20's 80ms measurement time doesn't block the bus. The ESP32 sends the trigger command (0xAC), releases the bus, does other work for 80ms, then comes back to read the 7-byte result. The bus is free for LIS2DH12 and BH1750 transactions during the AHT20 conversion.

---

## Datasheet and Sources

- **Aosong AHT20 datasheet:** [AHT20 Datasheet PDF](http://www.aosong.com/userfiles/files/media/AHT20%20%E8%8B%B1%E6%96%87%E7%89%88%E8%AF%B4%E6%98%8E%E4%B9%A6%20A1%2020201222.pdf)
- **LCSC product page:** [C2757850](https://www.lcsc.com/product-detail/C2757850.html)
- **Adafruit AHT20 breakout board:** [adafruit.com/product/4566](https://www.adafruit.com/product/4566) (useful reference schematic and Arduino/Python library)
- **Adafruit AHT20 Arduino library:** [github.com/adafruit/Adafruit_AHTX0](https://github.com/adafruit/Adafruit_AHTX0)
- **Wikipedia — Humidity sensor:** [en.wikipedia.org/wiki/Hygrometer#Capacitive](https://en.wikipedia.org/wiki/Hygrometer#Capacitive)
- **Wikipedia — Bandgap voltage reference:** [en.wikipedia.org/wiki/Bandgap_voltage_reference](https://en.wikipedia.org/wiki/Bandgap_voltage_reference)
- **Aosong (manufacturer) homepage:** [aosong.com](http://www.aosong.com/)
