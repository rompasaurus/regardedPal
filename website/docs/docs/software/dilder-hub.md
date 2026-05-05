# Dilder Hub — All-In-One Firmware

The combined firmware that brings together all Dilder features: animated octopus with 16 moods, joystick menu navigation, WiFi with NTP time sync, piezo speaker, battery monitoring, and a network status screen.

---

## Features

| Feature | Details |
|---------|---------|
| **Octopus Display** | 16 animated moods with 823 quotes, RTC clock header, mood-based body transforms |
| **Mood Selector** | Joystick-navigable picker for all 16 moods + "ALL (RANDOM)" |
| **WiFi** | CYW43 STA mode, auto-connect to configured network |
| **NTP Time Sync** | Syncs RTC to pool.ntp.org on WiFi connect (UTC+2 CEST) |
| **Network Screen** | Live WiFi status, SSID, IP, RSSI, NTP sync, on/off toggle |
| **Sound Test** | Each joystick direction plays a different tone |
| **Device Info** | Firmware version, build date, display variant, battery voltage, WiFi status |
| **Battery Monitor** | ADC reads VSYS — shows percentage or USB-powered status |
| **Status Icons** | WiFi icon (top-left), battery icon with lightning bolt (top-right) |

---

## Screens

### Main Screen (STATE_OCTOPUS)

The default view: animated octopus with mouth cycling, random quotes filtered by current mood, RTC clock header at the top, WiFi status icon top-left, battery icon top-right, and "DOWN:MENU" hint.

The tagline below the speech bubble shows the current mood name (e.g. "- CONSPIRATORIAL -", "- ANGRY -"). When mood is set to ALL, it shows the mood of the current quote.

### Menu (STATE_MENU)

Press joystick DOWN on the main screen. Overlay on the bottom half showing:

1. **MOOD SELECT** — pick a personality
2. **NETWORK** — WiFi settings
3. **SOUND TEST** — test the piezo speaker
4. **DEVICE INFO** — system information
5. **BACK** — return to octopus

Navigate: UP/DOWN to move, CENTER to select, LEFT to go back.

### Mood Selector (STATE_MOOD_SELECT)

Scrollable list of all 16 moods + "ALL MOODS (RANDOM)" at the top. The current selection is highlighted with an inverted bar. Press CENTER to apply — the octopus immediately switches to quotes from that mood and returns to the main screen.

| Mood | Quote Count | Body Animation |
|------|-------------|----------------|
| Normal | 30+ | Gentle breathing bob |
| Weird | 30+ | Lateral sway + body wobble |
| Unhinged | 30+ | Random x/y jitter |
| Angry | 30+ | Trembling + expanded body |
| Sad | 30+ | Drooped posture |
| Chaotic | 30+ | Full-body distortion |
| Hungry | 30+ | Upward reaching |
| Tired | 30+ | Sagging + slow bob |
| Slap Happy | 30+ | Bouncing sway |
| Lazy | 30+ | Lazy tentacle drape |
| Fat | 30+ | Thicc body, no waist |
| Chill | 30+ | Subtle rocking |
| Creepy | 30+ | Slow wobble |
| Excited | 30+ | Fast bouncing |
| Nostalgic | 30+ | Gentle swaying |
| Homesick | 30+ | Drooped + lateral drift |

### Network (STATE_NETWORK)

Shows:
- **WIFI:** ON / OFF (CENTER to toggle)
- **SSID:** configured network name
- **STATUS:** DISABLED / CONNECTING... / CONNECTED
- **IP:** assigned IP address
- **SIGNAL:** RSSI in dBm
- **NTP:** SYNCED / NOT SYNCED

When WiFi is toggled ON, the firmware connects to the configured SSID and immediately requests NTP time sync. The clock on the main screen updates to real network time.

### Sound Test (STATE_SOUND)

Each joystick direction plays a tone through the push-pull piezo:

| Direction | Note | Frequency |
|-----------|------|-----------|
| UP | C5 | 1047 Hz |
| DOWN | G4 | 784 Hz |
| LEFT | A4 | 880 Hz |
| RIGHT | B4 | 988 Hz |
| CENTER | E5 | 1319 Hz |

Shows direction, frequency, press count, and live GPIO status indicators.

### Device Info (STATE_INFO)

- Firmware version and display variant
- Build date and time
- Live RTC clock (network time if WiFi connected)
- Current mood and quote count
- WiFi status and IP
- Battery: percentage and voltage (or "USB" with voltage)
- Board: PICO 2 W RP2350

---

## Hardware Wiring

| Component | Pin | GPIO | Function |
|-----------|-----|------|----------|
| Display CLK | 14 | GP10 | SPI1 SCK |
| Display DIN | 15 | GP11 | SPI1 TX |
| Display CS | 12 | GP9 | Chip select |
| Display DC | 11 | GP8 | Data/command |
| Display RST | 16 | GP12 | Reset |
| Display BUSY | 17 | GP13 | Busy flag |
| Joystick L | 4 | GP2 | Left |
| Joystick D | 5 | GP3 | Down |
| Joystick UP | 6 | GP4 | Up |
| Joystick R | 7 | GP5 | Right |
| Joystick C | 9 | GP6 | Center/push |
| Speaker + | 20 | GP15 | PWM7B |
| Speaker - | 19 | GP14 | PWM7A (inverted) |
| Battery sense | — | GP29 | ADC3 (VSYS/3) |

### Speaker: Push-Pull Drive

Both GP14 and GP15 share PWM slice 7. Channel A (GP14) is inverted so the piezo sees opposite-phase signals — 6.6Vpp instead of 3.3V from a single pin. Direct connection, no resistor needed.

---

## WiFi Configuration

Edit `dev-setup/dilder-hub/wifi_config.h`:

```c
#define WIFI_SSID  "YourNetwork"
#define WIFI_PASS  "YourPassword"
#define NTP_SERVER "pool.ntp.org"
#define TIMEZONE_OFFSET_SEC  7200   // UTC+2 (CEST)
```

Or pass via cmake: `-DWIFI_SSID="YourNetwork" -DWIFI_PASS="YourPassword"`

---

## Building

### Via DevTool

1. Open the Picotool tab
2. Select "Dilder Hub" from the firmware list
3. Click "Clean Build & Flash"

### Via Command Line

```bash
cd dev-setup
docker compose run --rm \
  -e DISPLAY_VARIANT=V4 \
  -e PICO_BOARD=pico2_w \
  build-dilder-hub
```

Output: `dev-setup/dilder-hub/build/dilder_hub.uf2`

---

## Source

- Firmware: `dev-setup/dilder-hub/main.c` (~1,935 lines)
- Quotes: `dev-setup/dilder-hub/quotes.h` (823 quotes, all 16 moods)
- Build: `dev-setup/dilder-hub/CMakeLists.txt`
- WiFi: `dev-setup/dilder-hub/wifi_config.h`
- Display driver: `dev-setup/hello-world/lib/e-Paper/EPD_2in13_V4.c` (shared)
