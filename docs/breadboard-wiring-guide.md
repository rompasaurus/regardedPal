# Breadboard Wiring Guide — Full Test Bench

> Complete wiring diagram and setup instructions for all current hardware components on a single breadboard with the Raspberry Pi Pico WH.

---

## Table of Contents

1. [Components](#1-components)
2. [Pin Assignment Table](#2-pin-assignment-table)
3. [Master Wiring Diagram](#3-master-wiring-diagram)
4. [Pico WH Pin Map — All Peripherals](#4-pico-wh-pin-map--all-peripherals)
5. [Component-by-Component Wiring](#5-component-by-component-wiring)
    - [5.1 Waveshare 2.13" e-Paper V3 (SPI1)](#51-waveshare-213-e-paper-v3-spi1)
    - [5.2 DollaTek 5-Way Joystick (GPIO)](#52-dollatek-5-way-joystick-gpio)
    - [5.3 GY-NEO6MV2 GPS Module (UART0)](#53-gy-neo6mv2-gps-module-uart0)
    - [5.4 HC-SR04 Ultrasonic Sensor (GPIO)](#54-hc-sr04-ultrasonic-sensor-gpio)
    - [5.5 Speaker / Piezo Buzzer (PWM)](#55-speaker--piezo-buzzer-pwm)
6. [Breadboard Layout Strategy](#6-breadboard-layout-strategy)
7. [Power Budget](#7-power-budget)
8. [Important Notes and Warnings](#8-important-notes-and-warnings)
9. [Quick Test Code](#9-quick-test-code)
    - [9.1 GPS Serial Test](#91-gps-serial-test)
    - [9.2 HC-SR04 Distance Test](#92-hc-sr04-distance-test)
    - [9.3 Speaker Tone Test](#93-speaker-tone-test)
    - [9.4 All-Peripherals Diagnostic](#94-all-peripherals-diagnostic)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Components

| # | Component | Model | Interface | Voltage | Notes |
|---|-----------|-------|-----------|---------|-------|
| 1 | **Microcontroller** | Raspberry Pi Pico WH | — | 3.3V logic / 5V USB | Pre-soldered headers |
| 2 | **e-Paper Display** | Waveshare 2.13" V3 | SPI1 | 3.3V | SSD1680 driver, 250x122px |
| 3 | **5-Way Joystick** | DollaTek 5D Navigation | GPIO (active LOW) | 3.3V | Up/Down/Left/Right/Center |
| 4 | **GPS Module** | GY-NEO6MV2 (NEO-6M) | UART (9600 baud) | 3.3-5V | NMEA output, onboard voltage regulator |
| 5 | **Ultrasonic Sensor** | HC-SR04 | GPIO (TRIG/ECHO) | **5V** | Needs voltage divider on ECHO |
| 6 | **Speaker** | Piezo buzzer or small speaker | PWM | 3.3V | Through NPN transistor for volume |

---

## 2. Pin Assignment Table

| Peripheral | Signal | Pico GPIO | Physical Pin | Direction | Interface |
|------------|--------|-----------|-------------|-----------|-----------|
| **e-Paper** | VCC | 3V3(OUT) | 36 | Power out | — |
| | GND | GND | 38 | Ground | — |
| | DIN (MOSI) | GP11 | 15 | Out → display | SPI1 TX |
| | CLK | GP10 | 14 | Out → display | SPI1 SCK |
| | CS | GP9 | 12 | Out → display | SPI1 CSn |
| | DC | GP8 | 11 | Out → display | Digital |
| | RST | GP12 | 16 | Out → display | Digital |
| | BUSY | GP13 | 17 | In ← display | Digital |
| **Joystick** | UP | GP2 | 4 | In (pull-up) | GPIO |
| | DOWN | GP3 | 5 | In (pull-up) | GPIO |
| | LEFT | GP4 | 6 | In (pull-up) | GPIO |
| | RIGHT | GP5 | 7 | In (pull-up) | GPIO |
| | CENTER | GP6 | 9 | In (pull-up) | GPIO |
| | COM/GND | GND | 8 | Ground | — |
| **GPS** | TX → RX | GP1 (UART0 RX) | 2 | In ← GPS | UART0 |
| | RX ← TX | GP0 (UART0 TX) | 1 | Out → GPS | UART0 |
| | VCC | 3V3(OUT) | 36 | Power out | — |
| | GND | GND | 3 | Ground | — |
| **HC-SR04** | VCC | VBUS (5V) | 40 | Power out | — |
| | TRIG | GP14 | 19 | Out → sensor | Digital |
| | ECHO | GP16 (via divider) | 21 | In ← sensor | Digital |
| | GND | GND | 23 | Ground | — |
| **Speaker** | Signal | GP15 | 20 | Out → speaker | PWM |
| | GND | GND | 23 | Ground | — |
| **Total** | | **16 GPIO** | | | |
| **Free** | | **GP7, GP17-22, GP26-28** | | | **10 GPIO remaining** |

---

## 3. Master Wiring Diagram

```
                              PICO WH (on breadboard)
                              ┌────USB────┐
          GPS TX ────────►  GP0  [ 1]   │         │  [40]  VBUS ───► HC-SR04 VCC (5V)
          GPS RX ◄────────  GP1  [ 2]   │         │  [39]  VSYS
                            GND  [ 3] ──┼── GPS GND│  [38]  GND  ───► e-Paper GND
  Joystick UP ──────────►  GP2  [ 4]   │         │  [37]  3V3_EN
  Joystick DOWN ────────►  GP3  [ 5]   │  PICO   │  [36]  3V3(OUT)─┬► e-Paper VCC
  Joystick LEFT ────────►  GP4  [ 6]   │   WH    │                 └► GPS VCC
  Joystick RIGHT ───────►  GP5  [ 7]   │         │  [35]  ADC_VREF
  Joystick GND ─────────►  GND  [ 8]   │         │  [34]  GP28
  Joystick CENTER ──────►  GP6  [ 9]   │         │  [33]  AGND
                            GP7  [10]   │         │  [32]  GP27
          e-Paper DC ◄────  GP8  [11]   │         │  [31]  GP26
          e-Paper CS ◄────  GP9  [12]   │         │  [30]  RUN
                            GND  [13]   │         │  [29]  GP22
          e-Paper CLK ◄──  GP10  [14]   │         │  [28]  GND
          e-Paper DIN ◄──  GP11  [15]   │         │  [27]  GP21
          e-Paper RST ◄──  GP12  [16]   │         │  [26]  GP20
          e-Paper BUSY ──► GP13  [17]   │         │  [25]  GP19
                            GND  [18]   │         │  [24]  GP18
      HC-SR04 TRIG ◄────  GP14  [19]   │         │  [23]  GND  ──┬► HC-SR04 GND
      Speaker PWM ◄──────  GP15  [20]   │         │               └► Speaker GND
                                        └─────────┘
      HC-SR04 ECHO ──────────────────────────────────► GP16 [21]
                                                        (via voltage divider)


LEGEND:
  ──► = signal flows TO the Pico (input)
  ◄── = signal flows FROM the Pico (output)
  ─┬► = power rail splits to multiple devices
```

---

## 4. Pico WH Pin Map — All Peripherals

```
                    ┌────USB────┐
  GPS TX→RX   GP0  [ 1]         [40]  VBUS ◄── HC-SR04 5V
  GPS RX←TX   GP1  [ 2]         [39]  VSYS
              GND  [ 3]         [38]  GND  ◄── e-Paper GND
▶ JOY UP     GP2  [ 4]         [37]  3V3_EN
▶ JOY DOWN   GP3  [ 5]         [36]  3V3(OUT) ◄── e-Paper VCC + GPS VCC
▶ JOY LEFT   GP4  [ 6]         [35]  ADC_VREF
▶ JOY RIGHT  GP5  [ 7]         [34]  GP28
  JOY GND    GND  [ 8]         [33]  AGND
▶ JOY CTR    GP6  [ 9]         [32]  GP27
              GP7  [10]         [31]  GP26
◆ EPD DC     GP8  [11]         [30]  RUN
◆ EPD CS     GP9  [12]         [29]  GP22
              GND  [13]         [28]  GND
◆ EPD CLK   GP10  [14]         [27]  GP21
◆ EPD DIN   GP11  [15]         [26]  GP20
◆ EPD RST   GP12  [16]         [25]  GP19
◆ EPD BUSY  GP13  [17]         [24]  GP18
              GND  [18]         [23]  GND  ◄── HC-SR04 GND + Speaker GND
★ SR04 TRIG GP14  [19]         [22]  GP17
♪ SPEAKER   GP15  [20]         [21]  GP16 ◄── ★ SR04 ECHO (via divider)
                    └──────────┘

▶ = Joystick (5 pins)       Pins 4-9
◆ = e-Paper Display (6 pins) Pins 11-17
● = GPS (2 pins)            Pins 1-2
★ = HC-SR04 (2 pins)        Pins 19, 21
♪ = Speaker (1 pin)         Pin 20
```

---

## 5. Component-by-Component Wiring

### 5.1 Waveshare 2.13" e-Paper V3 (SPI1)

Uses the 8-pin header on the HAT board. Connect with female-to-male jumper wires.

| e-Paper Pin | Wire Color (suggested) | Pico WH Pin | GPIO |
|------------|------------------------|-------------|------|
| VCC | Red | Pin 36 (3V3 OUT) | — |
| GND | Black | Pin 38 (GND) | — |
| DIN | Blue | Pin 15 | GP11 (SPI1 TX) |
| CLK | Yellow | Pin 14 | GP10 (SPI1 SCK) |
| CS | Orange | Pin 12 | GP9 (SPI1 CSn) |
| DC | Green | Pin 11 | GP8 |
| RST | White | Pin 16 | GP12 |
| BUSY | Purple | Pin 17 | GP13 |

**SPI Config:** SPI1, Mode 0, 4 MHz, MSB-first.

---

### 5.2 DollaTek 5-Way Joystick (GPIO)

Check the module's silkscreen for pin labels. Wire each direction to its GPIO and COM to ground.

| Module Pin | Wire Color (suggested) | Pico WH Pin | GPIO |
|-----------|------------------------|-------------|------|
| COM / GND | Black | Pin 8 (GND) | — |
| UP | Red | Pin 4 | GP2 |
| DOWN | Blue | Pin 5 | GP3 |
| LEFT | Yellow | Pin 6 | GP4 |
| RIGHT | Green | Pin 7 | GP5 |
| CENTER / SET | White | Pin 9 | GP6 |

**Config:** Internal pull-ups enabled in software. Active LOW (pressed = 0).

If your module has a VCC pin, leave it **unconnected**.

---

### 5.3 GY-NEO6MV2 GPS Module (UART0)

The GY-NEO6MV2 has 4 pins: VCC, GND, TX, RX. It has an onboard voltage regulator that accepts 3.3-5V input and an onboard antenna (ceramic patch).

| GPS Pin | Wire Color (suggested) | Pico WH Pin | GPIO | Notes |
|---------|------------------------|-------------|------|-------|
| VCC | Red | Pin 36 (3V3 OUT) | — | 3.3V is fine — onboard regulator handles it |
| GND | Black | Pin 3 (GND) | — | Any GND pin works |
| TX | Green | Pin 2 | GP1 (UART0 RX) | GPS transmits → Pico receives |
| RX | Yellow | Pin 1 | GP0 (UART0 TX) | Pico transmits → GPS receives |

**CRITICAL: TX/RX crossover.** The GPS module's TX pin connects to the Pico's RX pin (GP1), and vice versa. This is a serial crossover — transmit connects to receive on the other end.

```
GPS Module          Pico WH
┌────────┐          ┌────────┐
│     TX ├─────────►│ GP1 RX │  (GPS sends NMEA data → Pico reads it)
│     RX │◄─────────┤ GP0 TX │  (Pico sends commands → GPS receives)
│    VCC ├─────────►│ 3V3OUT │
│    GND ├─────────►│ GND    │
└────────┘          └────────┘
```

**UART Config:** 9600 baud, 8N1 (default NEO-6M settings).

**First fix:** The GPS module needs a clear view of the sky to acquire satellites. The first cold fix can take **1-5 minutes** outdoors. The onboard LED blinks once per second when it has a fix.

**Power draw:** ~45mA active, ~10mA with the backup battery maintaining a hot start.

---

### 5.4 HC-SR04 Ultrasonic Sensor (GPIO)

The HC-SR04 measures distance (2-400cm) using ultrasonic pulses. It operates at **5V** — this requires special handling because the Pico's GPIO is **3.3V only**.

| HC-SR04 Pin | Wire Color (suggested) | Pico WH Pin | GPIO | Notes |
|------------|------------------------|-------------|------|-------|
| VCC | Red | Pin 40 (VBUS, 5V) | — | **Must be 5V** — will not work on 3.3V |
| TRIG | Orange | Pin 19 | GP14 | 3.3V output is enough to trigger (>2.5V threshold) |
| ECHO | Yellow (through divider) | Pin 21 | GP16 | **MUST use voltage divider** — ECHO outputs 5V |
| GND | Black | Pin 23 (GND) | — | |

#### ECHO Voltage Divider (Required)

The ECHO pin outputs a 5V pulse. Feeding 5V directly into GP16 **will damage the Pico**. Use a simple resistor voltage divider to reduce it to ~3.3V:

```
HC-SR04 ECHO ──── [1KΩ] ────┬──── GP16 (Pin 21)
                             │
                          [2KΩ]
                             │
                            GND

Output voltage: 5V × 2K/(1K+2K) = 3.33V  ✓ Safe for Pico
```

**Alternative resistor values that work:**
- 1KΩ + 2KΩ → 3.33V (ideal)
- 1KΩ + 1.8KΩ → 3.21V (fine)
- 2.2KΩ + 3.3KΩ → 3.0V (safe, slightly lower)
- 330Ω + 680Ω → 3.37V (fine, smaller values = faster response)

!!! danger "Do NOT skip the voltage divider"
    Connecting the HC-SR04 ECHO pin directly to any Pico GPIO will send 5V into a 3.3V-rated pin. This can permanently damage the RP2040 chip. Always use the voltage divider.

**How the HC-SR04 works:**

```
1. Pico sends 10µs HIGH pulse on TRIG (GP14)
2. HC-SR04 emits 8 ultrasonic bursts at 40kHz
3. HC-SR04 sets ECHO HIGH
4. Sound wave travels, bounces off object, returns
5. HC-SR04 sets ECHO LOW
6. Pico measures ECHO pulse duration

Distance (cm) = pulse_duration_µs / 58
Distance (inches) = pulse_duration_µs / 148
```

**Range:** 2cm to 400cm. **Cone angle:** ~15 degrees.

**Power draw:** ~15mA active, ~2mA idle.

---

### 5.5 Speaker / Piezo Buzzer (PWM)

Two options depending on what speaker hardware you have:

#### Option A — Passive Piezo Buzzer (simplest)

Wire directly between GP15 and GND. The PWM signal creates the tone.

```
GP15 (Pin 20) ──── [Piezo +] ──── [Piezo -] ──── GND (Pin 23)
```

This works but is quiet (~65dB). Fine for testing.

#### Option B — Small Speaker with NPN Transistor (louder)

For a proper speaker (8Ω, 0.5W), use an NPN transistor as an amplifier:

```
GP15 (Pin 20) ──── [1KΩ] ──── Base (B)
                                │
                           ┌────┤ NPN (2N2222 / BC547)
                           │    │
                    Speaker(+)  │
                       │    Collector (C)
                    Speaker(-)
                       │
                      GND ◄──── Emitter (E)

Power for speaker: 3V3(OUT) → Speaker(+) → Speaker(-) → Collector
```

**Components needed:**
- 1x NPN transistor (2N2222, BC547, or BC817)
- 1x 1KΩ resistor (base current limiter)
- 1x small speaker (8Ω 0.5W) or piezo buzzer

**PWM Config:** GP15, frequency sets the pitch (200Hz-8000Hz typical), duty cycle ~50%.

---

## 6. Breadboard Layout Strategy

Use a **full-size breadboard** (830 tie points) for all components. A half-size breadboard (400 tie points) will be very cramped with this many peripherals.

```
┌──────────────────────────────────────────────────────────────────┐
│                        FULL-SIZE BREADBOARD                      │
│                                                                  │
│  + Power Rail (top) ─────── 3.3V ──────────────────────────────  │
│  - Ground Rail (top) ────── GND ───────────────────────────────  │
│                                                                  │
│  ┌─────────────┐                                                 │
│  │  GPS Module  │  ← Left end, near GP0/GP1                     │
│  │  GY-NEO6MV2 │     VCC to 3.3V rail, GND to GND rail         │
│  └─────────────┘     TX→Pin 2, RX←Pin 1                         │
│                                                                  │
│  ┌──────────────────────────────────────┐                        │
│  │           PICO WH (centered)         │                        │
│  │     Straddles the center channel     │                        │
│  │                                      │                        │
│  │  Left side: Joystick (4-9)           │                        │
│  │             Display SPI (11-17)      │                        │
│  │                                      │                        │
│  │  Right side: 3V3, GND, VBUS (36-40) │                        │
│  └──────────────────────────────────────┘                        │
│                                                                  │
│  ┌──────────────┐     ┌───────────────┐     ┌───────────────┐   │
│  │  Joystick    │     │   HC-SR04     │     │   Speaker     │   │
│  │  Module      │     │ + Voltage     │     │ + Transistor  │   │
│  │  (left of    │     │   Divider     │     │   (right end) │   │
│  │   Pico)      │     │  (right of    │     │               │   │
│  └──────────────┘     │   Pico)       │     └───────────────┘   │
│                        └───────────────┘                         │
│                                                                  │
│  + Power Rail (bottom) ─── 5V (VBUS) ──── for HC-SR04 only ──   │
│  - Ground Rail (bottom) ── GND ───────────────────────────────   │
│                                                                  │
│  e-Paper display connects via flying wires (F-M jumpers)         │
│  from the HAT's 8-pin header to the left side of the Pico       │
└──────────────────────────────────────────────────────────────────┘

ZONE MAP:
  Left end:      GPS module
  Left of Pico:  Joystick module
  Center:        Pico WH (straddling channel)
  Right of Pico: HC-SR04 + voltage divider resistors
  Right end:     Speaker + transistor circuit
  Top rail:      3.3V power (for GPS, display, sensors)
  Bottom rail:   5V power (from VBUS, for HC-SR04 only)
  Flying wires:  e-Paper display (hangs off the side)
```

**Rail setup:**
1. Bridge the **top power rail** to **Pin 36 (3V3 OUT)** for 3.3V
2. Bridge the **top ground rail** to **Pin 38 (GND)**
3. Bridge the **bottom power rail** to **Pin 40 (VBUS)** for 5V (HC-SR04 only)
4. Bridge the **bottom ground rail** to the top ground rail (shared GND)

---

## 7. Power Budget

| Component | Active Current | Voltage | Source |
|-----------|---------------|---------|--------|
| Pico WH (WiFi off) | ~28mA | 3.3V | Internal LDO |
| e-Paper display (refreshing) | ~5mA | 3.3V | 3V3(OUT) |
| e-Paper display (static) | ~0.01mA | 3.3V | 3V3(OUT) |
| GPS module (acquiring) | ~45mA | 3.3V | 3V3(OUT) |
| GPS module (tracking) | ~35mA | 3.3V | 3V3(OUT) |
| HC-SR04 | ~15mA | 5V | VBUS |
| Joystick | ~0mA | — | Passive switches |
| Speaker (piezo) | ~5mA | 3.3V | GP15 PWM |
| Speaker (with transistor) | ~30mA | 3.3V | 3V3(OUT) via transistor |
| **Total (all active)** | **~130mA** | | |

The 3V3(OUT) rail is rated for **300mA max**. With everything running simultaneously, we draw ~120mA from 3V3 — well within limits.

**USB power (from computer/adapter):** Provides 500mA on VBUS, which is more than enough.

!!! warning "GPS is the biggest power consumer"
    The NEO-6M draws ~45mA while acquiring satellites. If running on battery (future), consider powering the GPS only when needed via a GPIO-controlled MOSFET switch.

---

## 8. Important Notes and Warnings

### Voltage Levels

| Component | Logic Level | Safe on Pico? |
|-----------|------------|---------------|
| e-Paper | 3.3V | Yes — direct connection |
| Joystick | 3.3V (passive) | Yes — direct connection |
| GPS (TX/RX) | 3.3V | Yes — the GY-NEO6MV2 has a 3.3V regulator and 3.3V logic |
| HC-SR04 TRIG | 3.3V input accepted | Yes — 3.3V exceeds the 2.5V HIGH threshold |
| HC-SR04 ECHO | **5V output** | **NO — use voltage divider** |
| Speaker | 3.3V PWM | Yes — direct or through transistor |

### GPS Antenna

The GY-NEO6MV2 has a ceramic patch antenna on the top of the module. For best reception:
- Keep the antenna side facing **up** (toward the sky)
- Avoid placing metallic objects or wires directly over the antenna
- First fix requires outdoor or window-side placement
- The onboard LED blinks at 1Hz when the GPS has a satellite fix

### HC-SR04 Variants

Some HC-SR04 modules are available in a **3.3V variant** (often labeled HC-SR04P or with "3V-5.5V" on the board). If you have this variant, you can skip the voltage divider and power it from 3V3(OUT) instead of VBUS. Check the silkscreen or datasheet.

### UART0 and USB Serial

UART0 (GP0/GP1) is used for the GPS module. This means **USB serial debugging (stdio over USB) still works** — the Pico SDK sends printf output over the USB CDC interface, not UART0. You can monitor GPS data and debug output simultaneously.

If you need UART-based serial debugging (not USB), use UART1 on GP4/GP5 — but this conflicts with the joystick. Stick with USB serial for debugging.

---

## 9. Quick Test Code

### 9.1 GPS Serial Test

Read NMEA sentences from the GPS module over UART0:

```c
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"

#define GPS_UART uart0
#define GPS_BAUD 9600
#define GPS_TX_PIN 0
#define GPS_RX_PIN 1

int main() {
    stdio_init_all();
    sleep_ms(2000);

    uart_init(GPS_UART, GPS_BAUD);
    gpio_set_function(GPS_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(GPS_RX_PIN, GPIO_FUNC_UART);

    printf("=== GPS Test ===\n");
    printf("Waiting for NMEA data...\n\n");

    while (1) {
        if (uart_is_readable(GPS_UART)) {
            char c = uart_getc(GPS_UART);
            putchar(c);  // Forward GPS data to USB serial
        }
    }
}
```

**Expected output** (after GPS fix):
```
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,47.0,M,,*47
$GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
```

**No fix yet** will show sentences with empty fields:
```
$GPGGA,,,,,,0,00,99.99,,,,,,*48
```

### 9.2 HC-SR04 Distance Test

Measure distance using TRIG/ECHO:

```c
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"

#define TRIG_PIN 14
#define ECHO_PIN 16

float measure_distance_cm(void) {
    // Send 10µs trigger pulse
    gpio_put(TRIG_PIN, 1);
    sleep_us(10);
    gpio_put(TRIG_PIN, 0);

    // Wait for ECHO to go HIGH
    uint32_t start = time_us_32();
    while (gpio_get(ECHO_PIN) == 0) {
        if (time_us_32() - start > 30000) return -1;  // timeout
    }

    // Measure ECHO pulse duration
    uint32_t pulse_start = time_us_32();
    while (gpio_get(ECHO_PIN) == 1) {
        if (time_us_32() - pulse_start > 30000) return -1;  // timeout
    }
    uint32_t pulse_end = time_us_32();

    float duration_us = (float)(pulse_end - pulse_start);
    return duration_us / 58.0f;  // Convert to cm
}

int main() {
    stdio_init_all();
    sleep_ms(2000);

    gpio_init(TRIG_PIN);
    gpio_set_dir(TRIG_PIN, GPIO_OUT);
    gpio_init(ECHO_PIN);
    gpio_set_dir(ECHO_PIN, GPIO_IN);

    printf("=== HC-SR04 Distance Test ===\n\n");

    while (1) {
        float dist = measure_distance_cm();
        if (dist > 0) {
            printf("Distance: %.1f cm\n", dist);
        } else {
            printf("Out of range / timeout\n");
        }
        sleep_ms(500);
    }
}
```

### 9.3 Speaker Tone Test

Play a tone on the piezo buzzer via PWM:

```c
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"

#define SPEAKER_PIN 15

void play_tone(uint pin, uint frequency, uint duration_ms) {
    gpio_set_function(pin, GPIO_FUNC_PWM);
    uint slice = pwm_gpio_to_slice_num(pin);

    uint32_t clock = 125000000;
    uint32_t divider = clock / (frequency * 4096);
    if (divider < 1) divider = 1;
    if (divider > 255) divider = 255;

    pwm_set_clkdiv(slice, (float)divider);
    uint32_t wrap = clock / (divider * frequency) - 1;
    pwm_set_wrap(slice, wrap);
    pwm_set_chan_level(slice, pwm_gpio_to_channel(pin), wrap / 2);  // 50% duty
    pwm_set_enabled(slice, true);

    sleep_ms(duration_ms);

    pwm_set_enabled(slice, false);
    gpio_init(pin);  // Reset to GPIO mode (silence)
}

int main() {
    stdio_init_all();
    sleep_ms(2000);
    printf("=== Speaker Test ===\n");

    // Play a startup melody
    play_tone(SPEAKER_PIN, 523, 200);   // C5
    sleep_ms(50);
    play_tone(SPEAKER_PIN, 659, 200);   // E5
    sleep_ms(50);
    play_tone(SPEAKER_PIN, 784, 200);   // G5
    sleep_ms(50);
    play_tone(SPEAKER_PIN, 1047, 400);  // C6
    sleep_ms(200);

    printf("Melody complete.\n");

    while (1) {
        tight_loop_contents();
    }
}
```

### 9.4 All-Peripherals Diagnostic

Run this after wiring everything to verify each component works:

```c
#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "hardware/pwm.h"

// Pin definitions
#define GPS_UART     uart0
#define GPS_TX       0
#define GPS_RX       1
#define BTN_UP       2
#define BTN_DOWN     3
#define BTN_LEFT     4
#define BTN_RIGHT    5
#define BTN_CENTER   6
#define TRIG_PIN     14
#define SPEAKER_PIN  15
#define ECHO_PIN     16

void test_buttons(void) {
    const uint btns[] = {BTN_UP, BTN_DOWN, BTN_LEFT, BTN_RIGHT, BTN_CENTER};
    const char *names[] = {"UP", "DOWN", "LEFT", "RIGHT", "CENTER"};
    printf("[JOYSTICK] ");
    for (int i = 0; i < 5; i++) {
        if (gpio_get(btns[i]) == 0)
            printf("%s ", names[i]);
    }
    printf("\n");
}

float test_distance(void) {
    gpio_put(TRIG_PIN, 1);
    sleep_us(10);
    gpio_put(TRIG_PIN, 0);
    uint32_t start = time_us_32();
    while (gpio_get(ECHO_PIN) == 0)
        if (time_us_32() - start > 30000) return -1;
    uint32_t t0 = time_us_32();
    while (gpio_get(ECHO_PIN) == 1)
        if (time_us_32() - t0 > 30000) return -1;
    return (float)(time_us_32() - t0) / 58.0f;
}

int main() {
    stdio_init_all();
    sleep_ms(2000);

    // Init buttons
    for (uint pin = BTN_UP; pin <= BTN_CENTER; pin++) {
        gpio_init(pin);
        gpio_set_dir(pin, GPIO_IN);
        gpio_pull_up(pin);
    }

    // Init HC-SR04
    gpio_init(TRIG_PIN);
    gpio_set_dir(TRIG_PIN, GPIO_OUT);
    gpio_init(ECHO_PIN);
    gpio_set_dir(ECHO_PIN, GPIO_IN);

    // Init GPS UART
    uart_init(GPS_UART, 9600);
    gpio_set_function(GPS_TX, GPIO_FUNC_UART);
    gpio_set_function(GPS_RX, GPIO_FUNC_UART);

    printf("==========================================\n");
    printf("  DILDER ALL-PERIPHERALS DIAGNOSTIC\n");
    printf("==========================================\n\n");

    // Quick speaker beep to confirm audio
    gpio_set_function(SPEAKER_PIN, GPIO_FUNC_PWM);
    uint slice = pwm_gpio_to_slice_num(SPEAKER_PIN);
    pwm_set_clkdiv(slice, 30.0f);
    pwm_set_wrap(slice, 4166);
    pwm_set_chan_level(slice, pwm_gpio_to_channel(SPEAKER_PIN), 2083);
    pwm_set_enabled(slice, true);
    sleep_ms(100);
    pwm_set_enabled(slice, false);
    gpio_init(SPEAKER_PIN);
    printf("[SPEAKER] Beep OK\n");

    while (1) {
        printf("--- tick ---\n");

        // Buttons
        test_buttons();

        // Distance
        float d = test_distance();
        if (d > 0)
            printf("[HC-SR04] Distance: %.1f cm\n", d);
        else
            printf("[HC-SR04] No reading\n");

        // GPS (drain buffer, print one NMEA sentence)
        printf("[GPS] ");
        bool got_data = false;
        uint32_t gps_start = time_us_32();
        while (time_us_32() - gps_start < 100000) {  // 100ms window
            if (uart_is_readable(GPS_UART)) {
                char c = uart_getc(GPS_UART);
                putchar(c);
                got_data = true;
                if (c == '\n') break;
            }
        }
        if (!got_data) printf("No data (check wiring / sky view)\n");

        printf("\n");
        sleep_ms(1000);
    }
}
```

---

## 10. Troubleshooting

| Symptom | Component | Likely Cause | Fix |
|---------|-----------|-------------|-----|
| Display shows nothing | e-Paper | SPI wiring wrong or VCC not on 3V3 | Check all 8 wires, confirm 3V3 not VBUS |
| No joystick response | Joystick | COM not grounded, or pull-ups not enabled | Check GND wire, verify `gpio_pull_up()` in code |
| GPS outputs empty NMEA fields | GPS | No satellite fix | Move near a window or outdoors; wait 1-5 minutes |
| GPS outputs nothing at all | GPS | TX/RX swapped, or wrong baud rate | Swap GP0/GP1 wires; confirm 9600 baud |
| GPS outputs garbage characters | GPS | Baud rate mismatch | Default is 9600; don't change it without reason |
| HC-SR04 always reads -1 | HC-SR04 | No 5V power, or ECHO divider wrong | Confirm VCC on VBUS (5V), check resistor values |
| HC-SR04 damaged the Pico | HC-SR04 | ECHO connected directly (no divider) | **The Pico is likely damaged.** Always use the voltage divider |
| HC-SR04 reads max range | HC-SR04 | Nothing in front of sensor, or angled wrong | Point sensor at a flat surface 10-100cm away |
| Speaker is silent | Speaker | Wrong pin, or PWM not configured | Check GP15, verify PWM code; try direct 3V3 to speaker briefly |
| Speaker is very quiet | Speaker | Piezo without amplifier | Add NPN transistor circuit (see Section 5.5, Option B) |
| Multiple things fail | Power | 3V3 rail overloaded | Check total current draw; GPS + display + Pico = ~80mA, should be fine |
| Pico resets randomly | Power | USB port can't supply enough current | Use a powered USB hub or wall adapter (500mA+ rated) |
| USB serial shows nothing | Pico | Firmware not flashed, or wrong COM port | Re-flash via BOOTSEL + UF2; check device manager for port |

---

## Appendix: Wire Shopping List

For this full setup you need:

| Item | Quantity | Notes |
|------|----------|-------|
| Male-to-male jumper wires | ~15 | For breadboard connections |
| Female-to-male jumper wires | ~10 | For e-Paper HAT header to breadboard |
| 1KΩ resistor | 2 | HC-SR04 voltage divider + speaker transistor base |
| 2KΩ resistor (or 1.8KΩ) | 1 | HC-SR04 voltage divider |
| NPN transistor (2N2222/BC547) | 1 | Optional: speaker amplifier |
| Full-size breadboard | 1 | 830 tie points recommended |

---

*Document version: 1.0 — Created 2026-04-14*
