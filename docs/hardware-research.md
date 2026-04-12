# Hardware Research & Materials List

Research compiled during Phase 1 planning for the Dilder prototype test bench.

---

## Development Platform Strategy

**Phase 1 (current):** Raspberry Pi Pico W — cheap, on hand, great for prototyping the display + input system with C/C++ via the Pico SDK.

**Recommended upgrade:** Raspberry Pi Pico 2 W — drop-in replacement with WiFi, BLE, 2× SRAM, 2× flash, faster CPU, near-zero porting effort.

**Future:** Raspberry Pi Zero WH — upgrade when we need Linux, filesystem, networking features, or more compute. The display and button wiring is nearly identical; the firmware port is Phase 5.

---

## Board Comparison

Evaluated against Dilder's requirements: SPI display (6 GPIO), 5 buttons (5 GPIO), USB serial, future WiFi/BLE (Phase 7), and the existing C/Pico SDK firmware.

| Board | CPU | GPIO | Flash | SRAM | WiFi | BT | SPI | USB | SDK Compatibility | Price |
|---|---|---|---|---|---|---|---|---|---|---|
| **Pi Pico** (current) | RP2040 M0+ 133MHz | **26** | 2MB | 264KB | -- | -- | 2× | Micro | Pico SDK (current) | ~4.80 |
| **Pi Pico H** | RP2040 M0+ 133MHz | **26** | 2MB | 264KB | -- | -- | 2× | Micro | Pico SDK (current) | ~4.80 |
| **Pi Pico 2 W** | RP2350 M33 150MHz | **26** | 4MB | 520KB | **Yes** | **BLE 5.2** | 2× | Micro | Pico SDK 2.x (backwards-compatible) | ~7.50 |
| **Pi Pico 2 WH** | RP2350 M33 150MHz | **26** | 4MB | 520KB | **Yes** | **BLE 5.2** | 2× | Micro | Pico SDK 2.x (backwards-compatible) | ~8.50 |
| **XIAO RP2350** | RP2350 M33 150MHz | **11** | 2MB | 520KB | -- | -- | 1× | USB-C | Pico SDK 2.x | ~6.45 |
| **XIAO ESP32S3+** | Xtensa LX7 240MHz | **11** | 8MB | 512KB | **Yes** | **BLE 5.0** | 1× | USB-C | ESP-IDF (full rewrite) | ~9.99 |
| **XIAO nRF52840** | M4 64MHz | **11** | 1MB+2MB | 256KB | -- | **BLE 5.0** | 1× | USB-C | Zephyr/nRF SDK (full rewrite) | ~9.40 |
| **XIAO SAMD21** | M0+ 48MHz | **11** | 256KB | 32KB | -- | -- | 1× | USB-C | Arduino (full rewrite) | ~5.99 |
| **XIAO MG24 Sense** | M33 78MHz | **11** | 1.5MB | 256KB | -- | **BLE+Zigbee** | 1× | USB-C | Gecko SDK (full rewrite) | ~10.60 |

### Key findings

- **All XIAO boards** have only 11 GPIO — exactly enough for 6 display + 5 buttons with zero pins remaining for the planned piezo buzzer or future sensors.
- **Non-RP2350 XIAO boards** require a full firmware rewrite to a different SDK (ESP-IDF, Zephyr, Arduino, Gecko).
- **The Pico 2 W** is the clear upgrade path: same form factor, same pinout, backwards-compatible SDK, WiFi + BLE for Phase 7, 2× memory, and only 2.70 more than the current Pico.
- **XIAO nRF52840** has no WiFi, which blocks Phase 7 networking plans. Its BLE 5.0 alone is not sufficient for the planned WiFi-based features.

### Board recommendation

The **Raspberry Pi Pico 2 W** at 7.50 covers the entire project roadmap through Phase 7 with minimal code changes — just recompile against Pico SDK 2.x.

---

## Core Components

### 1. Raspberry Pi Pico W

| Spec | Detail |
|------|--------|
| Chip | RP2040 — dual-core ARM Cortex-M0+ @ 133MHz |
| RAM | 264KB SRAM |
| Flash | 2MB onboard (no SD card) |
| Wi-Fi | 802.11n 2.4GHz (CYW43439) |
| Bluetooth | BLE 5.2 |
| GPIO | 26 multi-function pins (GP0–GP28, not all exposed) |
| ADC | 3 channels (12-bit) |
| SPI | 2× SPI controllers |
| USB | Micro-USB (power + data, device/host) |
| Dimensions | 51 × 21 × 3.9mm |
| Price | ~$6 |
| Firmware | C/C++ via Pico SDK (CMake + arm-none-eabi-gcc) |

The Pico WH variant has pre-soldered headers — convenient for breadboard prototyping but either works.

**Resources:**
- [Pico W Datasheet (PDF)](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf)
- [RP2040 Datasheet (PDF)](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)
- [MicroPython for Pico W](https://micropython.org/download/RPI_PICO_W/)
- [Pico W Pinout](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf)

### 2. Waveshare 2.13" E-Paper Display HAT (V3)

**Product:** [Amazon DE - B07Q5PZMGT](https://www.amazon.de/-/en/gp/product/B07Q5PZMGT)

| Spec | Detail |
|------|--------|
| Size | 2.13 inches (48.55mm x 23.71mm active area) |
| Resolution | 250 x 122 pixels |
| Colors | Black & White |
| Driver IC | SSD1680 (V3) |
| Interface | SPI (4-wire, Mode 0) |
| Operating Voltage | 3.3V / 5V (onboard voltage translator) |
| Full Refresh | ~2 seconds |
| Partial Refresh | ~0.3 seconds |
| Standby Current | < 0.01 uA |
| Refresh Interval | >= 180 seconds recommended between full refreshes |
| Price | ~$13-18 |

**Important:** This is the **V3** revision (SSD1680 driver). The HAT is designed for Pi Zero's 40-pin header, but we connect to the Pico W via jumper wires using the 8-pin SPI interface.

**Pin Connections to Pico W (via jumper wires):**

| E-Paper Pin | Function | Pico W GPIO | Pico W Pin # |
|-------------|----------|-------------|-------------|
| VCC | Power 3.3V | 3V3(OUT) | 36 |
| GND | Ground | GND | 38 |
| DIN | SPI MOSI | GP11 (SPI1 TX) | 15 |
| CLK | SPI Clock | GP10 (SPI1 SCK) | 14 |
| CS | Chip Select | GP9 (SPI1 CSn) | 12 |
| DC | Data/Command | GP8 | 11 |
| RST | Reset | GP12 | 16 |
| BUSY | Busy status | GP13 | 17 |

**Resources:**
- [Waveshare Wiki](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT)
- [Waveshare Pico e-Paper Code](https://github.com/waveshare/Pico_ePaper_Code)
- [V3 Specification PDF](https://files.waveshare.com/upload/4/4e/2.13inch_e-Paper_V3_Specification.pdf)
- [SSD1680 Datasheet](https://www.orientdisplay.com/wp-content/uploads/2022/08/SSD1680_v0.14.pdf)

---

## Display Comparison

Comparison of the current Waveshare 2.13" V3 against alternative e-paper and LCD displays evaluated for the Dilder project.

### E-Paper Displays

| Spec | **Waveshare 2.13" V3** (current) | **DEBO EPA 2.9"** | **DEBO EPA 2.1" RD** | **DEBO EPA 1.54" RD** |
|---|---|---|---|---|
| **Size** | 2.13" (48.6 × 23.7mm active) | **2.9"** (~66.9 × 29.1mm) | 2.1" (~46.9 × 22.5mm) | 1.54" (~27.5 × 27.6mm) |
| **Resolution** | 250 × 122 (30,500 px) | **296 × 128** (37,888 px) | 212 × 104 (22,048 px) | 200 × 200 (40,000 px) |
| **Dot pitch** | 0.194mm | ~0.227mm | ~0.221mm | ~0.138mm |
| **Colors** | Black / White | Black / White | Black / White / **Red** | Black / White / **Red** |
| **Driver IC** | SSD1680 | SSD1680 (likely) | SSD1675B (likely) | SSD1681 (likely) |
| **Interface** | SPI 4-wire | SPI 4-wire | SPI 4-wire | SPI 4-wire |
| **Full refresh** | ~2s | ~2s | **~6–15s** (red layer) | **~6–15s** (red layer) |
| **Partial refresh** | ~0.3s | ~0.3s | **Unreliable / unsupported** | **Unreliable / unsupported** |
| **Standby current** | < 0.01µA | < 0.01µA | < 0.01µA | < 0.01µA |
| **Active power** | ~26.4mW | ~26–30mW | ~30–40mW | ~25–35mW |
| **Buffer size** | 3,904 bytes | **4,736 bytes** | **2× 2,756 bytes** (B/W + Red) | **2× 5,000 bytes** (B/W + Red) |
| **GPIO pins needed** | 6 | 6 | 6 | 6 |
| **Price** | ~13–18 (already owned) | ~19.70 | ~17.50 | ~15.40 |

#### DEBO EPA 2.9" B/W — The Natural Upgrade

**Improvements:**
- 24% more pixels (37,888 vs 30,500) — more room for pet animations, speech bubbles, and status bars.
- 37% larger active area — physically bigger, better for a handheld device.
- Same driver family (SSD1680) — the existing Waveshare C driver likely needs only resolution constant changes and minor init sequence tweaks.
- Same refresh characteristics — full ~2s, partial ~0.3s, same 180s interval rules.
- Same SPI protocol — identical wiring, identical pin count, drop-in on the same breadboard.

**Drawbacks:**
- Buffer grows from 3,904 to 4,736 bytes (still trivial for 264KB SRAM).
- Landscape canvas in DevTool changes from 250×122 to 296×128 — the IMG protocol, transpose logic in `img-receiver/main.c`, and DevTool canvas dimensions all need updating.
- Physically larger — may affect enclosure planning.
- Slightly coarser dot pitch (0.227 vs 0.194mm) — individual pixels are more visible.

**Firmware impact:** Moderate. Update `EPD_WIDTH`/`EPD_HEIGHT` constants, `IMG_W` (250→296), `IMG_H` (122→128), `IMG_ROW_BYTES` (32→37), `IMG_TOTAL` (3904→4736), DevTool canvas size, and Sassy Octopus frame dimensions. Core SPI driver and partial refresh logic stay the same.

#### DEBO EPA 2.1" RD — Tri-Color, Smaller

**Improvements:**
- Red as a third color — could highlight health bars, warnings, and pet emotions.
- Similar physical size to the current display.

**Drawbacks:**
- Resolution drops to 212×104 — 28% fewer pixels than the current display.
- Full refresh takes 6–15 seconds — the red pigment particles are physically larger and slower to move. This is a fundamental physics limitation.
- Partial refresh is unreliable or unsupported on tri-color panels — the current 0.3s partial refresh animation approach (Sassy Octopus) would not work.
- Double buffer required — two separate image planes (B/W layer + Red layer), each ~2,756 bytes.
- Different driver IC (SSD1675B vs SSD1680) — the existing Waveshare C driver will not work. Requires a completely different init sequence, LUT, and command set.
- Red particles ghost worse than black, requiring even longer clearing refresh cycles.

**Firmware impact:** Heavy rewrite. New driver IC, new buffer format, no partial refresh means rethinking the entire animation approach. DevTool would need a 3-color canvas mode.

#### DEBO EPA 1.54" RD — Tri-Color, Square, Tiny

**Improvements:**
- Square aspect ratio (200×200) — unique layout possibilities, centered pet sprite.
- Highest pixel density (0.138mm dot pitch) — sharpest text and detail of all four.
- Smallest physical footprint — easiest to fit in a compact enclosure.

**Drawbacks:**
- Same 6–15s tri-color refresh penalty — same red particle physics problem.
- Same "no partial refresh" limitation — animations are dead.
- Physically tiny (27.5mm square) — smaller than the current 2.13" display.
- Double buffer — 2× 5,000 bytes (larger than the 2.1" RD due to higher resolution).
- Different driver IC (SSD1681) — yet another driver to write from scratch.
- Square aspect ratio means every existing asset needs redesigning for a completely different layout.

**Firmware impact:** Complete rewrite. New driver, new aspect ratio, new buffer format, no partial refresh.

### The Core Trade-off: Red Color vs. Animation

| | B/W e-ink | Tri-color (B/W/R) e-ink |
|---|---|---|
| **Full refresh** | ~2s | ~6–15s |
| **Partial refresh** | ~0.3s (smooth-ish animation) | Not reliably supported |
| **Sassy Octopus animation** | Works (current approach) | Broken — 6–15s between frames |
| **Interactive pet** | Feasible with partial refresh | Effectively a static display |
| **Visual flair** | Black and white only | Red accents for highlights |
| **Driver complexity** | Simpler (single buffer) | Double buffer, longer LUTs |

For a Tamagotchi-style pet that needs to react, animate, and feel alive, partial refresh is non-negotiable. That rules out both red displays for the primary screen.

### LCD/TFT Alternatives (Also Evaluated)

| Display | Type | Size | Resolution | Driver | Refresh | Active Power | Price |
|---|---|---|---|---|---|---|---|
| **DEBO LCD128X128** | LCD TFT | 1.44" | 128×128 | ST7735S | ~60+ FPS | ~20–40mW | ~5.90 |
| **DEBO LCD 2.0** | LCD TFT | 2.0" | 220×176 | ILI9225 | ~60+ FPS | ~40–80mW | ~7.99 |
| **DEBO LCD240X240** | LCD IPS | 1.3" | 240×240 | ST7789 | ~60+ FPS | ~30–60mW | ~10.60 |
| **DEBO TFT 1.8** | LCD TFT | 1.8" | 128×160 | ST7735R | ~60+ FPS | ~30–60mW | ~9.80 |
| **DEBO TFT 1.8 TD** | LCD TFT+Touch | 1.8" | 128×160 | ST7735R | ~60+ FPS | ~35–65mW | ~8.95 |
| **ARD SHD 2.6TD** | LCD TFT+Touch | 2.6" | 320×240 | ILI9341 | ~30–60 FPS | ~80–150mW | ~6.65 |
| **ARD SHD 2.8TD** | LCD TFT+Touch | 2.8" | 320×240 | ILI9341 | ~30–60 FPS | ~100–200mW | ~11.60 |

LCDs offer 60+ FPS full-color animation but require an always-on backlight (20–200mW continuous), killing battery life compared to e-paper's near-zero idle draw. Touch-capable displays (ILI9341 shields) could replace physical buttons but consume more GPIO pins — problematic on XIAO boards.

### Display Recommendation

**Primary display upgrade:** The **DEBO EPA 2.9" B/W** is the best fit — bigger, more pixels, same speed, same driver family, minimal porting work. Paired with the Pico 2 W, it covers the entire project roadmap.

**Red displays** could be fun for a secondary notification screen or a different project, but their 6–15s refresh and lack of partial refresh make them unusable as Dilder's primary display.

---

## Input Options (4-5 Buttons)

### Option A -- Discrete Tactile Buttons (Recommended for Prototype)

Simple 6x6mm through-hole momentary switches, optionally with colored snap-on caps.

| Detail | Value |
|--------|-------|
| Size | 6x6mm (various heights: 4.3mm to 9.5mm) |
| Cost | ~$2-3 for a pack of 20 |
| GPIO per button | 1 (+ shared ground) |
| Pull-up resistors | Use Pico W's internal software pull-ups -- no external components needed |
| Debounce | Handle in software |

**Why this option:** Cheapest, simplest, breadboard-friendly for prototyping. The original Tamagotchi used 3 tactile buttons -- this is the authentic approach.

### Other Considered Options

| Type | Cost | Notes |
|------|------|-------|
| 5-Way Nav Switch + 2 buttons | ~$3 | Compact d-pad feel, 7 GPIO pins. More "game device" than "Tamagotchi." |
| 1x4 Membrane Keypad | ~$2-4 | Very thin, adhesive-backed. Mushy feel, only 4 buttons. |
| TTP223 Capacitive Touch | ~$1-3/10-pack | No moving parts. No tactile feedback. |

### Decision

**For prototyping: Option A (5x discrete 6x6mm tactile buttons)**
- Layout: 3 nav buttons (left/select/right) + 2 action buttons (A/B)
- Total GPIO: 5 pins + shared ground
- Total cost: ~$2-3

---

## Test Bench Materials List

### Essential -- On Hand

| Item | Est. Cost | Notes |
|------|-----------|-------|
| Raspberry Pi Pico W | ~$6 | On hand. Micro-USB for power + data. |
| Waveshare 2.13" e-Paper HAT V3 | ~$15 | On hand. SSD1680 driver, 250×122px. Connected via jumper wires (not HAT connector). |
| Micro-USB cable | ~$2 | For Pico W power + programming |
| Half-size breadboard | ~$3-5 | For prototyping button + display wiring |
| Jumper wire kit (M-F and M-M) | ~$3-6 | **Required** — the display HAT doesn't plug into the Pico W directly |
| 6x6mm tactile buttons (pack of 20) | ~$2-3 | Various heights, with snap-on caps |
| **Subtotal** | **~$31-37** | |

### Nice to Have

| Item | Est. Cost | Notes |
|------|-----------|-------|
| Pico WH (pre-soldered headers) | ~$7 | Easier breadboard use than bare Pico W |
| 10k resistor assortment | ~$2-3 | External pull-ups if needed |
| Multimeter | ~$10-20 | Debugging wiring |

### For Battery Power (Later Phase)

| Item | Est. Cost | Notes |
|------|-----------|-------|
| 3.7V LiPo battery (1200mAh) | ~$8-12 | JST connector |
| Adafruit PowerBoost 500C | ~$18 | LiPo charger + 5V boost, load-sharing |
| Budget alt: TP4056 + boost converter | ~$2-3 | Cheaper but more wiring |

---

## GPIO Pin Budget (Pico W)

| Function | Pins Used | Interface | Pico W GPIO |
|----------|-----------|-----------|-------------|
| E-ink display | 6 | SPI1 + control | GP8, GP9, GP10, GP11, GP12, GP13 |
| Buttons (5) | 5 | Digital input | GP2, GP3, GP4, GP5, GP6 |
| Piezo buzzer (future) | 1 | PWM | GP15 |
| **Total** | **12** | | **14+ GPIO remaining** |

Note: Button GPIOs are chosen to avoid SPI1 pins and leave SPI0 free for future use. The specific pins can be changed — the above are suggestions for clean wiring.

---

## Prototype Enclosure Concept

> Enclosure design is deferred until Phase 5/6 when we migrate to the Pi Zero. The Pico W prototype lives on a breadboard.

### Original Form Factor: "iPod Nano" Style -- Landscape Rectangle with Side D-Pad

Concept renders (designed for Pi Zero + HAT form factor):
- [prototype-v1.svg](concepts/prototype-v1.svg) -- Initial rough layout
- **[prototype-v2.svg](concepts/prototype-v2.svg)** -- Dimension-accurate revision

These will be revised when the final board (Pico W or Pi Zero) is chosen for the enclosure build.

---

## Next Steps

1. Flash MicroPython firmware onto Pico W
2. Set up VSCode with MicroPico extension
3. Wire the e-ink display to the Pico W via jumper wires
4. Wire 5 buttons on the breadboard
5. Get Waveshare's MicroPython example code running to confirm display works
6. Display a placeholder sprite as proof of life
