# Breadboard Prototype Guide — ESP32-S3

How to build a Dilder prototype on breadboard using off-the-shelf parts that match the custom PCB design. Also covers compact "alpha board" options for real-world testing.

---

## Table of Contents

- [Dev Board Comparison](#dev-board-comparison)
- [Recommended Breadboard Parts List](#recommended-breadboard-parts-list)
- [GPIO Wiring Map](#gpio-wiring-map)
- [Shopping List by Retailer (Germany)](#shopping-list-by-retailer-germany)
- [Amazon Shopping List (US/DE)](#amazon-shopping-list-usde)
- [Compact Alpha Board — No Breadboard](#compact-alpha-board--no-breadboard)
  - [Option A: Feather Stack](#option-a-feather-stack-recommended)
  - [Option B: Protoboard Solder Build](#option-b-protoboard-solder-build)
  - [Option C: 3D-Printed Bracket](#option-c-3d-printed-bracket)
- [Key Notes and Gotchas](#key-notes-and-gotchas)

---

## Dev Board Comparison

Pick one. All have ESP32-S3 and enough GPIO for the full Dilder circuit.

| Board | Price | Flash/PSRAM | Battery Charging | USB | GPIO | Best For |
|-------|-------|-------------|-----------------|-----|------|----------|
| **Olimex ESP32-S3-DevKit-Lipo** | **7.95 EUR** | 8MB/8MB | **Yes** (built-in) | Dual USB-C | 45 | Best value, skip TP4056 |
| Waveshare ESP32-S3 N8R8 | 10.50 EUR | 8MB/8MB | No | USB-C | 36 | Cheap, widely stocked |
| Generic N16R8 DevKitC | 8-14 EUR | **16MB/8MB** | No | USB-C | 36 | Exact PCB silicon match |
| **UM FeatherS3** | **28.98 EUR** | **16MB/8MB** | **Yes** (JST + fuel gauge) | USB-C | 21 | Feather ecosystem, cleanest |
| Adafruit ESP32-S3 Feather | 22.96 EUR | 4MB/2MB | **Yes** | USB-C | 20 | Budget Feather option |
| SparkFun Thing Plus S3 | 25-30 EUR | 4MB/2MB | **Yes** (+ microSD) | USB-C | 21 | If you want SD card |
| Seeed XIAO ESP32S3 | 7.50 EUR | 8MB/8MB | Yes | USB-C | **11** | **NOT ENOUGH GPIO** |

### Recommendations

**Budget pick:** Olimex ESP32-S3-DevKit-Lipo (7.95 EUR) — has LiPo charging built in, eliminating the TP4056 module. Open-source hardware. Ships from Bulgaria (3-7 days to Germany).

**Best match to PCB:** Generic N16R8 DevKitC (10-14 EUR on Amazon/Botland) — exact same ESP32-S3-WROOM-1-N16R8 module as the custom PCB. Needs separate TP4056 for battery.

**Cleanest prototype:** Unexpected Maker FeatherS3 (28.98 EUR at exp-tech.de) — Feather ecosystem lets you stack the eInk FeatherWing directly. Battery charging, STEMMA QT I2C, exact 16MB/8MB match.

---

## Recommended Breadboard Parts List

| # | Component | Purpose | Est. Price | Notes |
|---|-----------|---------|------------|-------|
| 1 | **ESP32-S3 dev board** | Main MCU | 8-29 EUR | See comparison above |
| 2 | **Waveshare 2.13" e-Paper** (V4, SSD1680) | Display | 8-18 EUR | Use 8-pin breakout header with F-M jumper wires |
| 3 | **Adafruit LIS3DH breakout** | Accelerometer | 5-6 EUR | LIS3DH is I2C/SPI compatible substitute for LIS2DH12 (bare LIS2DH12 breakouts are discontinued) |
| 4 | **5-way navigation joystick** | Input | 2-8 EUR | Through-hole module; Adafruit ADA504 or DollaTek 5-way |
| 5 | **LiPo battery** (1000-1200mAh, JST PH 2.0mm) | Power | 6-10 EUR | Verify polarity matches your dev board |
| 6 | **TP4056 USB-C module** | Battery charging | 1.40-5.50 EUR | **Skip if dev board has charging** (Olimex, FeatherS3) |
| 7 | **Full-size breadboard** (830 points) | Prototyping platform | 4-8 EUR | Half-size is too small |
| 8 | **Jumper wire kit** (M-M + F-M) | Wiring | 4-8 EUR | Need ~15 M-M, ~10 F-M for display header |
| 9 | **2x 10k resistors** | I2C pull-ups | <1 EUR | Skip if accel breakout has onboard pull-ups |

**Total estimate:** 40-85 EUR depending on dev board choice and what you already have.

---

## GPIO Wiring Map

Same pin assignments as the custom PCB — firmware ports directly.

```
ESP32-S3 GPIO  →  Component            →  Breakout Wire
─────────────────────────────────────────────────────────
GPIO3          →  e-Paper DC            →  Display pin 6
GPIO4          →  Joystick UP           →  Joystick UP
GPIO5          →  Joystick DOWN         →  Joystick DOWN
GPIO6          →  Joystick LEFT         →  Joystick LEFT
GPIO7          →  Joystick RIGHT        →  Joystick RIGHT
GPIO8          →  Joystick CENTER       →  Joystick CENTER
GPIO9          →  e-Paper CLK (SCK)     →  Display pin 4
GPIO10         →  e-Paper MOSI (DIN)    →  Display pin 3
GPIO11         →  e-Paper RST           →  Display pin 7
GPIO12         →  e-Paper BUSY          →  Display pin 8
GPIO16         →  Accelerometer SDA     →  Accel SDA
GPIO17         →  Accelerometer SCL     →  Accel SCL
GPIO46         →  e-Paper CS            →  Display pin 5
3V3            →  All VCC lines         →  Display pin 1 + Accel VDD
GND            →  All GND lines         →  Display pin 2 + Accel GND + Joystick COM
```

**Joystick:** Common pin to GND. Each direction pin to its GPIO. Enable internal pull-ups in software.

**Accelerometer:** I2C address 0x18 (SA0/SDO to GND). 10k pull-ups on SDA/SCL to 3.3V (skip if breakout has them).

---

## Shopping List by Retailer (Germany)

Optimized for fast delivery (1-5 business days) and fewest separate orders.

### Option 1: Budget Build (~43 EUR, 3 orders)

**Botland.store** (ships in 24h from Poland/Germany)

| Item | Price |
|------|-------|
| Waveshare ESP32-S3-DEV-KIT-N8R8 | 10.50 EUR |

**Eckstein-shop.de** (1-3 workdays, Germany)

| Item | Price |
|------|-------|
| Adafruit LIS3DH accelerometer breakout | 5.89 EUR |
| V-TEC LiPo 1200mAh JST-PH | 6.97 EUR |
| Waveshare 2.13" e-Paper raw panel | 8.32 EUR |

**BerryBase.de** (1-3 workdays, Germany)

| Item | Price |
|------|-------|
| Adafruit 5-way navigation joystick (ADA504) | 1.90 EUR |
| TC4056A USB-C LiPo charger board | 1.40 EUR |

**Total: ~35 EUR** + shipping (~5-10 EUR across 3 orders)

You'll also need a breadboard and jumper wires if you don't already have them.

### Option 2: Olimex Build (~38 EUR, 2 orders, no TP4056 needed)

**Olimex.com** (3-7 days from Bulgaria)

| Item | Price |
|------|-------|
| ESP32-S3-DevKit-Lipo | 7.95 EUR |

**Eckstein-shop.de** (1-3 workdays)

| Item | Price |
|------|-------|
| Adafruit LIS3DH breakout | 5.89 EUR |
| V-TEC LiPo 1200mAh JST-PH | 6.97 EUR |
| Waveshare 2.13" e-Paper raw panel | 8.32 EUR |
| Breadboard + jumper wire kit | ~8 EUR |

**BerryBase.de**

| Item | Price |
|------|-------|
| 5-way navigation joystick | 1.90 EUR |

**Total: ~39 EUR** + shipping. No TP4056 needed — Olimex board charges the LiPo directly via USB-C.

### Option 3: Premium Feather Build (~80 EUR, 1-2 orders)

**EXP-Tech.de** (ships from Germany)

| Item | Price |
|------|-------|
| Unexpected Maker FeatherS3 | 28.98 EUR |
| Adafruit 2.13" eInk FeatherWing | 22.50 EUR |
| Adafruit LIS3DH breakout | 4.90 EUR |
| Stacking headers (for FeatherWing) | ~2 EUR |

**BerryBase.de**

| Item | Price |
|------|-------|
| 5-way navigation joystick | 1.90 EUR |
| LiPo 1200mAh JST-PH | 5.50 EUR (if in stock) |

**Total: ~66 EUR** + shipping. Cleanest setup — eInk display plugs directly onto the Feather. Battery charging built in. No breadboard needed for core stack.

---

## Amazon Shopping List (US/DE)

For one-stop Amazon ordering (all Prime-eligible where noted):

### Amazon.de (Germany)

| Item | Search Term | Est. Price |
|------|------------|------------|
| ESP32-S3 N16R8 DevKitC | "ESP32-S3 N16R8 development board" | 10-15 EUR |
| Waveshare 2.13" e-Paper | "Waveshare 2.13 e-paper HAT" | 15-20 EUR |
| TP4056 USB-C (5-pack) | "AZ-Delivery TP4056 USB-C" | 8.99 EUR |
| DollaTek 5-way joystick (5-pack) | "DollaTek 5-way navigation" or B07HBPW3DF | 8.17 EUR |
| LiPo 1000mAh JST PH | "3.7V 1000mAh LiPo JST PH" | 8-12 EUR |
| Breadboard + jumper kit | "Breadboard 830 Jumper Wire Set" | 8-12 EUR |
| 10k resistors (100-pack) | "10k Ohm 1/4W resistor" | 2-3 EUR |

**Amazon.de total: ~60-80 EUR** (all Prime, 1-2 day delivery)

**Note:** LIS3DH/LIS2DH12 breakout boards are hard to find on Amazon.de. Order the Adafruit LIS3DH from eckstein-shop.de or exp-tech.de instead.

### Amazon.com (US)

| Item | Link/Search | Est. Price |
|------|------------|------------|
| HiLetgo ESP32-S3 N16R8 | "HiLetgo ESP32-S3-DevKitC-1-N16R8" | $10-14 |
| Waveshare 2.13" e-Paper | B071S8HT76 | $15-20 |
| NOYITO LIS2DH12 breakout | "NOYITO LIS2DH12TR" or B07HFSMQNC | $6-10 |
| NOYITO 5-way joystick | "NOYITO 5-way tactile switch" or B07G4266RP | $7-9 |
| HiLetgo TP4056 USB-C (5-pack) | B07PKND8KG | $7-9 |
| LiPo 1000mAh JST PH | "1000mAh LiPo JST PH" B09F9VK77V | $8-12 |
| Breadboard + wire kit | "830 breadboard jumper wire kit" | $8-12 |

**Amazon.com total: ~$60-85**

---

## Compact Alpha Board — No Breadboard

For carrying around and real-world testing, here are three approaches from simplest to most polished.

### Option A: Feather Stack (Recommended)

The cleanest path to a pocketable prototype:

```
    ┌─────────────────────────┐
    │   2.13" eInk Display    │  ← Adafruit eInk FeatherWing
    │   (250 x 122 pixels)    │
    ├─────────────────────────┤
    │    Stacking Headers     │  ← $1.50, plug-in, no soldering
    ├─────────────────────────┤
    │   FeatherS3 (ESP32-S3)  │  ← USB-C, LiPo charging, 16MB/8MB
    ├─────────────────────────┤
    │   1000mAh LiPo Battery  │  ← JST PH connector, sandwiched behind
    └─────────────────────────┘
    
    + LIS3DH accelerometer wired to STEMMA QT / I2C
    + 5-way joystick wired to GPIO and mounted on side
```

**Size:** ~65 x 28 x 20mm (slightly larger than the 45x80mm PCB but much thinner than a breadboard)

**Cost:** ~70-85 EUR

**Pros:** No soldering for the core stack. Display plugs in. Battery charges via USB-C. Same SSD1680 display driver as the custom PCB — firmware ports directly.

**Cons:** Joystick needs to be wired separately and mounted externally. Accelerometer hangs off I2C wires.

### Option B: Protoboard Solder Build

For maximum compactness matching the final PCB:

1. Get a **50x80mm protoboard** (double-sided, through-hole, ~2 EUR for 10-pack)
2. Solder the ESP32-S3 dev board with pin headers
3. Wire all peripherals with 30 AWG wire-wrap wire on the back side
4. Mount e-paper display on front with double-sided tape or standoffs
5. Mount battery on back with foam tape
6. Solder joystick module directly to board in thumb-accessible position

**Size:** ~50 x 80 x 15mm — very close to the 45x80mm PCB target

**Cost:** ~40-50 EUR (cheapest option overall)

**Pros:** Most compact. Closest to final form factor. Permanent connections (no wires falling out).

**Cons:** Requires soldering. Harder to modify. Takes 2-3 hours to build.

### Option C: 3D-Printed Bracket

Works with any wiring approach. Print a frame that holds everything together:

```
    ┌────────────────────────────────┐
    │  ┌──────────────────────────┐  │
    │  │    e-Paper Display       │  │  ← Window cutout
    │  └──────────────────────────┘  │
    │                                │
    │  [▲]                           │  ← Joystick access hole
    │ [◄●►]                          │
    │  [▼]                           │
    │                                │
    │         [USB-C port]           │  ← Cutout for charging
    └────────────────────────────────┘
    
    Inside: Dev board, battery, accelerometer
    secured with M2 screws or friction fit
```

**Target dimensions:** 55 x 85 x 25mm

**Print cost:** 3-5 EUR via JLC3DP or local printer (PLA, 20% infill)

**Design time:** 2-4 hours in Fusion 360 or TinkerCAD. Start from existing ESP32 case models on Printables/MakerWorld and modify.

---

## Key Notes and Gotchas

1. **LIS3DH vs LIS2DH12:** For breadboarding, use the **Adafruit LIS3DH breakout** — the LIS2DH12 bare IC is a 2x2mm LGA-12 package that cannot be breadboarded, and SparkFun's breakout is discontinued. The LIS3DH is register-compatible and has the same I2C interface. The custom PCB will use the LIS2DH12TR bare IC.

2. **Battery polarity:** JST PH connectors have NO universal polarity standard. Always verify with a multimeter before connecting. Reversed polarity will destroy the charger IC and possibly the ESP32.

3. **Display version:** Make sure you get the Waveshare 2.13" **V4** (SSD1680 driver). Older V2/V3 versions use different drivers and need different firmware.

4. **GPIO46 quirk:** On some ESP32-S3 variants, GPIO46 is a strapping pin (affects boot mode). If you have issues with CS on GPIO46, try GPIO47 or another free pin during prototyping.

5. **Breadboard width:** The standard ESP32-S3 DevKitC is wide enough to cover both sides of a standard breadboard. Use the center channel, but you'll need to use jumper wires to access pins on the covered side. A wide breadboard (630+ points) helps.

6. **Power:** During prototyping, power via USB-C. Only connect the LiPo battery once you've verified all wiring is correct. A short circuit with a LiPo can cause fire.
