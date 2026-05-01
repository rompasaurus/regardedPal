# 10440 Li-Ion AAA Wiring Guide

Complete wiring for dual 10440 cells + TP4056 charger + solar panel + Pico W power and battery monitoring.

---

## Components

| Part | Spec | Notes |
|------|------|-------|
| 2x 10440 Li-Ion cells | 3.7V nominal, 350mAh each | Raw cells, no built-in regulator |
| TP4056 module | USB-C variant with DW01A protection | Blue PCB, ~25x15mm |
| Solar panel | AK 62x36mm, 5-6V open circuit | ~100mA peak in direct sun |
| Schottky diode (optional) | 1N5817 or SS34 | Blocks solar reverse current at night |
| Pico W | Pin 39 (VSYS), Pin 38 (GND) | Built-in buck-boost handles 1.8-5.5V |
| Wire | 26-28 AWG silicone | Red (+), Black (-) |

---

## Battery Configuration: PARALLEL ONLY

```
     Cell 1 (3.7V 350mAh)          Cell 2 (3.7V 350mAh)
     ┌──────────────────┐          ┌──────────────────┐
   (+)                (-)        (+)                (-)
     │                  │          │                  │
     └────────┬─────────┘          └────────┬─────────┘
              │                             │
              ├─────────────────────────────┤
              │         PARALLEL            │
           POS bus (+)                   NEG bus (-)
              │                             │
              ▼                             ▼
         TP4056 BAT+                   TP4056 BAT-
```

**Combined output: 3.7V nominal, ~700mAh capacity.**

!!! danger "NEVER wire 10440 cells in series"
    Series = 7.4V. This exceeds the Pico VSYS max (5.5V) and will destroy the TP4056 (single-cell charger only, max input 8V on VCC but charges to 4.2V on BAT pin). Parallel only.

---

## How to Wire the Cells in Parallel

Parallel means positive-to-positive, negative-to-negative. Both cells see the same voltage (3.7V) and their capacities add up (350 + 350 = 700mAh).

### Physical Layout in the Cradle

The two 10440 cells sit side-by-side in the cradle's battery bays. Each bay has two Swpeet 7x7mm clip plates — one at each end — held in vertical slots. The cells drop in on top of the clips.

```
  CRADLE (top view, looking down into the bays)

  -X wall                                              +X wall
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │  ┌─[NEG clip]── Cell 1 (AAA 10440) ──[POS clip]─┐      │
  │  │   (-)          ◄────────────►         (+)      │      │
  │  │                                                │      │
  │  │              TP4056 sits here                   │      │
  │  │              on the ConnBlock                   │      │
  │  │                                                │      │
  │  ├─[NEG clip]── Cell 2 (AAA 10440) ──[POS clip]─┤      │
  │  │   (-)          ◄────────────►         (+)      │      │
  │  └────────────────────────────────────────────────┘      │
  │                                                          │
  └──────────────────────────────────────────────────────────┘
```

Both cells face the **same direction** — positive nub on the same end, flat negative on the other end.

### Wiring the Parallel Bus

You need two short bus wires: one red (positive), one black (negative).

**Step 1 — Positive bus:**

```
  Cell 1 POS clip ──── red wire ──── Cell 2 POS clip
         │
         └──── red wire continues to TP4056 BAT+
```

Solder a red wire between the two positive-end clip plates. Both POS clips are on the same X-end of the cradle. Run a third red wire from this junction to the TP4056 BAT+ pad.

**Step 2 — Negative bus:**

```
  Cell 1 NEG clip ──── black wire ──── Cell 2 NEG clip
         │
         └──── black wire continues to TP4056 BAT-
```

Same thing on the other end. Solder between the two negative-end clip plates, then run to TP4056 BAT-.

**Step 3 — Verify before inserting cells:**

1. Insert both cells (nub = positive end, flat = negative end)
2. Multimeter across the POS bus and NEG bus wires
3. Should read **3.6-4.2V** (depends on cell charge state)
4. If you read ~0V, one cell is backwards
5. If you read ~7.4V, you wired series by mistake — **STOP and fix**

### Wiring Directly to the Clip Plates

The Swpeet clip plates are 7x7mm stamped sheet metal, 0.5mm thick. To solder to them:

1. **Scratch the surface** with sandpaper or a blade — the nickel plating needs roughing up for solder to stick
2. **Tin the pad** — blob of solder on the clip plate first, let it cool
3. **Tin the wire** — strip 3-4mm of insulation, apply solder to the exposed wire
4. **Join** — hold the tinned wire against the tinned pad, touch with iron for 2-3 seconds
5. **Route the wire** — run it along the cradle wall, out through the FPC gap or over the ConnBlock edge to reach the TP4056

Use 28 AWG silicone wire — thin enough to route inside the cradle without interfering with cell fit, flexible enough to not stress the solder joints.

### Why Not Solder Directly to the Cells?

You can, but:

- 10440 cells are small and heat up fast — prolonged iron contact can damage the chemistry
- The cradle clip system lets you swap cells without desoldering
- If you must solder to cells, use tabbed/tagged 10440s (pre-spot-welded nickel strips) and solder to the tabs, not the cell body

---

## Full Wiring Diagram

```
                    ┌─────────────────────────────┐
                    │        SOLAR PANEL           │
                    │       AK 62x36mm             │
                    │      5-6V, ~100mA            │
                    │                              │
                    │   RED (+)        BLACK (-)   │
                    └─────┬──────────────┬─────────┘
                          │              │
                   ┌──────┴──────┐       │
                   │ 1N5817      │       │   (optional blocking diode
                   │ Schottky    │       │    prevents reverse current
                   │ Vf ≈ 0.3V  │       │    from battery → panel at night)
                   └──────┬──────┘       │
                          │              │
  ┌───────────────────────┼──────────────┼────────────────────────┐
  │                  TP4056 MODULE (with DW01A)                   │
  │                                                               │
  │   IN+  ◄─────────┘              IN-  ◄──────────┘            │
  │   (USB-C port also connects here — either source charges)     │
  │                                                               │
  │   ┌─────────────────────────────────────────────────┐         │
  │   │  TP4056 IC          RPROG (1.2kΩ = 1A charge)  │         │
  │   │                     (swap to 10kΩ for solar-    │         │
  │   │                      matched 120mA charge rate) │         │
  │   │  CC/CV charging     Red LED = charging          │         │
  │   │  4.2V termination   Green LED = done            │         │
  │   └─────────────────────────────────────────────────┘         │
  │                                                               │
  │   BAT+ ◄──── 10440 cells parallel (+)                        │
  │   BAT- ◄──── 10440 cells parallel (-)                        │
  │                                                               │
  │   ┌─────────────────────────────────────────────────┐         │
  │   │  DW01A Protection IC                            │         │
  │   │  Over-discharge cutoff: 2.9V (saves cells)      │         │
  │   │  Over-charge cutoff: 4.3V (backup safety)       │         │
  │   │  Short-circuit protection                       │         │
  │   └─────────────────────────────────────────────────┘         │
  │                                                               │
  │   OUT+ ─────────────────────────────► Pico VSYS (pin 39)     │
  │   OUT- ─────────────────────────────► Pico GND  (pin 38)     │
  │                                                               │
  └───────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Wiring

### 1. Wire cells in parallel

Solder a red wire between both cells' positive clip plates (or solder directly to the Swpeet contact plates in the cradle). Solder a black wire between both negative clip plates. This creates a single 3.7V ~700mAh battery pack.

### 2. Connect battery to TP4056

| Wire | From | To |
|------|------|----|
| Red | Parallel positive bus | TP4056 **BAT+** pad |
| Black | Parallel negative bus | TP4056 **BAT-** pad |

### 3. Connect solar panel to TP4056

| Wire | From | To |
|------|------|----|
| Red | Solar panel (+) | 1N5817 anode → cathode to TP4056 **IN+** |
| Black | Solar panel (-) | TP4056 **IN-** |

The 1N5817 Schottky diode prevents the battery from discharging back through the solar panel at night. Many TP4056 modules already have this built in — check yours. If the module has a USB-C port, the solar wires go to the IN+/IN- pads (separate from the USB port, same electrical node).

**Both USB-C and solar can be connected simultaneously.** Whichever source has higher voltage wins. USB provides ~5V, solar provides ~4.5-5V under load — USB will take priority when plugged in.

### 4. Connect TP4056 output to Pico

| Wire | From | To |
|------|------|----|
| Red | TP4056 **OUT+** | Pico W **VSYS** (pin 39) |
| Black | TP4056 **OUT-** | Pico W **GND** (pin 38) |

Use OUT+/OUT- (not BAT+/BAT-) so the DW01A protection is in the circuit. This cuts power if the battery drops below 2.9V, preventing deep discharge damage.

### 5. Solder points on the ePaper board (optional)

As discussed — you can solder these power wires to the corresponding VSYS and GND pass-through pads on the Waveshare ePaper HAT instead of directly to the Pico. Same electrical connection, keeps the Pico clean.

---

## Solar Panel RPROG Tuning

The default 1.2kΩ RPROG resistor sets a 1A charge current. The solar panel can only deliver ~100mA, so the TP4056 will constantly try to pull more than the panel can give, causing voltage sag and unstable behavior.

**Fix:** Replace RPROG with a 10kΩ resistor to set charge current to ~120mA, matching the solar panel's capacity.

```
RPROG formula:  Icharge (mA) = 1200 / RPROG (kΩ)

1.2kΩ  = 1000mA  (USB charging — fast)
5.0kΩ  =  240mA  (compromise)
10.0kΩ =  120mA  (solar-matched — stable)
```

If you want fast USB charging AND solar, keep the 1.2kΩ. The TP4056 will just charge slower from solar (it self-limits to what the source can provide), but it may oscillate between charging/not-charging in weak light. The 10kΩ swap is only needed if solar is the primary/only charge source.

---

## Battery Level Monitoring

**Yes, the Pico W can read battery voltage.** It has a built-in voltage divider on GPIO29 (ADC3) that reads VSYS/3.

### Hardware

No external components needed. The voltage divider is on the Pico W PCB:

```
VSYS ──┤ R1 (200kΩ) ├──┬──┤ R2 (100kΩ) ├── GND
                        │
                     GPIO29 (ADC3)
                     reads VSYS / 3
```

### Firmware (MicroPython example)

```python
import machine
import time

# On Pico W, GPIO29 is the VSYS/3 ADC input
# Must disable WiFi SPI sharing first on Pico W
vsys_adc = machine.ADC(29)

def read_battery_voltage():
    """Read VSYS voltage via the onboard divider."""
    raw = vsys_adc.read_u16()           # 0-65535
    voltage = raw * 3.3 / 65535 * 3     # Convert: ADC ref × divider ratio
    return voltage

def battery_percent(voltage):
    """Rough Li-Ion percentage from voltage (single cell, 3.0-4.2V)."""
    if voltage >= 4.10:
        return 100
    elif voltage >= 3.95:
        return 80
    elif voltage >= 3.80:
        return 60
    elif voltage >= 3.70:
        return 40
    elif voltage >= 3.55:
        return 20
    elif voltage >= 3.40:
        return 10
    else:
        return 0    # below 3.4V — critically low

# Read and display
v = read_battery_voltage()
pct = battery_percent(v)
print(f"Battery: {v:.2f}V ({pct}%)")
```

### Firmware (C / Pico SDK)

```c
#include "hardware/adc.h"
#include "hardware/gpio.h"

float read_battery_voltage(void) {
    // GPIO29 = ADC3 on Pico W (VSYS/3 divider)
    adc_init();
    adc_gpio_init(29);
    adc_select_input(3);  // ADC3

    // On Pico W, GPIO25 controls the VSYS ADC mux
    // Must set GPIO25 high to connect VSYS divider to ADC
    gpio_init(25);
    gpio_set_dir(25, GPIO_OUT);
    gpio_put(25, 1);

    uint16_t raw = adc_read();  // 12-bit: 0-4095
    float voltage = raw * 3.3f / 4095.0f * 3.0f;

    gpio_put(25, 0);  // release mux
    return voltage;
}
```

### USB Detection

GPIO24 goes HIGH when USB VBUS is present. Use this to show a charging icon:

```python
import machine

vbus_pin = machine.Pin(24, machine.Pin.IN)

if vbus_pin.value():
    print("USB connected — charging")
else:
    print("On battery")
```

### Voltage-to-Percentage Curve (Li-Ion 10440)

```
Voltage   State           Percent
──────────────────────────────────
4.20V     Fully charged     100%
4.10V     Nearly full        90%
3.95V     Good               80%
3.80V     Moderate           60%
3.70V     Nominal            40%
3.55V     Getting low        20%
3.40V     Low                10%
3.20V     Critical            5%
3.00V     Empty               0%
2.90V     DW01A cutoff     (power off)
```

The curve is non-linear — Li-Ion cells spend most of their life between 3.6-3.9V, then drop sharply below 3.4V. The percentage mapping above accounts for this.

---

## Power Budget

| State | Current Draw | Notes |
|-------|-------------|-------|
| Pico W active, WiFi off | ~28mA | Normal operation |
| Pico W deep sleep | ~1.0mA | `dormant()` or `lightsleep()` |
| e-Paper refresh | ~26mW peak | Only during screen update (~2s) |
| Tamagotchi mode (10min on / 50min sleep) | ~5.5mA avg | Realistic daily use |

**Battery life estimates (700mAh parallel 10440):**

| Mode | Current | Runtime |
|------|---------|---------|
| Always on, WiFi off | 28mA | ~25 hours |
| Tamagotchi mode | 5.5mA | ~5 days |
| Deep sleep only | 1.0mA | ~29 days |

**Solar supplement (6 hours direct sun):**

- Solar input: ~100mA x 6h = 600mAh/day
- Tamagotchi draw: ~5.5mA x 24h = 132mAh/day
- **Net daily gain: +468mAh** — battery stays topped up indefinitely in sunny conditions

---

## Safety Checklist

- [ ] Cells wired in **parallel** (NOT series)
- [ ] Multimeter confirms 3.6-4.2V across the parallel pack before connecting
- [ ] TP4056 module has DW01A protection IC (check for the small 6-pin SOT-23 near BAT pads)
- [ ] Using **OUT+/OUT-** pads (not BAT+/BAT-) for Pico connection
- [ ] Solar diode installed (or confirmed built-in on module)
- [ ] No bare wire contacts that could short inside the enclosure
- [ ] Battery voltage reading works before sealing the case
