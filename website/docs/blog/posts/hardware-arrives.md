---
date: 2026-04-13
authors:
  - rompasaurus
categories:
  - Hardware
slug: hardware-arrives
---

# New Hardware: Joystick Module and LiPo Battery

Two new components arrived for the Dilder build — a 5-way navigation joystick and a 1000mAh LiPo battery. Both have been fully documented with wiring guides, test code, and integration plans.

<!-- more -->

## The Joystick Module

The [DollaTek 5-Way Navigation Button Module](https://www.amazon.de/dp/B07HBPW3DF) is a compact rocker joystick with five discrete directions: up, down, left, right, and center press. Unlike an analog joystick, each direction is a simple switch — press a direction and it shorts to ground. This makes it a perfect drop-in replacement for the five individual tactile buttons originally planned.

### Wiring

The joystick uses the same GPIO assignments already defined in the codebase:

| Direction | GPIO | Pin |
|-----------|------|-----|
| Up | GP2 | 4 |
| Down | GP3 | 5 |
| Left | GP4 | 6 |
| Right | GP5 | 7 |
| Center | GP6 | 9 |
| Ground | GND | 8 |

Six wires total. No resistors needed — the Pico W's internal pull-ups handle everything. When a direction is pressed, it pulls the GPIO LOW. The firmware reads this as a button press.

The joystick sits on the **top-left** of the Pico W (pins 4-9), completely separate from the display wiring (pins 11-17). Clean separation, easy debugging.

### Testing

A simple polling test confirms each direction:

```c
while (1) {
    if (gpio_get(2) == 0) printf("UP\n");
    if (gpio_get(3) == 0) printf("DOWN\n");
    // ... etc
    sleep_ms(100);
}
```

Connect a serial terminal at 115200 baud and press each direction. If it prints, the wiring is good.

## The LiPo Battery

The [InnCraft Energy 503450](https://www.amazon.de/dp/B0F88RQX7C) is a 1000mAh 3.7V lithium polymer pouch cell — 51x34x5mm, about the size of a business card and thinner than a pencil.

### Why This Battery Works

The Pico W's VSYS pin accepts **1.8-5.5V**. A LiPo operates between 3.0V (empty) and 4.2V (full). The entire range sits comfortably inside the VSYS window — no boost converter needed. Two wires: red to VSYS (pin 39), black to GND (pin 38).

### Battery Life

In Tamagotchi mode (10 minutes active per hour, 50 minutes deep sleep):

- **~6.8 days** on a single charge
- ~12.6 days with aggressive sleep (5 min active / 55 min sleep)

### Charging Options

Three paths documented:

1. **Direct to VSYS** — simplest, no charging (remove battery to charge externally)
2. **TP4056 module** (~EUR 1.50) — USB charging with over-discharge protection
3. **Adafruit PowerBoost 500C** (~EUR 16) — premium, full load-sharing

The TP4056 is the sweet spot for most builders.

### The Connector Gotcha

This battery uses a **Molex 51021-0200** (1.25mm pitch), not the common JST PH 2.0mm. It won't plug into an Adafruit-style JST socket. For prototyping, cut the connector and solder wires directly — or get a Molex 1.25mm adapter.

## Expansion Headroom

With both new components wired up, plus the display, the Pico W still has **11+ GPIO pins free**. Enough room for:

- GPS module on UART0 (GP0, GP1)
- Accelerometer on I2C0 (GP16, GP17)
- All planned Phase 3-4 sensors

No conflicts between any peripherals. The pin budget was planned from day one to support this exact expansion path.

## Documentation

Full wiring guides with step-by-step instructions, diagrams, test code, and troubleshooting tables:

- [Joystick Wiring Guide](https://dilder.dev/docs/hardware/joystick-wiring/)
- [Battery Wiring Guide](https://dilder.dev/docs/hardware/battery-wiring/)
