# 14 — Dilder Encounters, Geocaching Challenges & Collectible System

> Proximity-triggered encounters between Dilders, riddle-based geocaching treasure hunts with physical electronic prizes, and a collectible ecosystem that doubles as a community growth engine.

---

## Overview

This document extends the existing peer discovery protocol (see `peer-discovery-research.md`) and treasure hunt system (see `user-engagement-plan.md` §13) into a three-layer gameplay and marketing system:

1. **Proximity Encounters** — When two Dilders detect each other via BLE, both devices react with unique audio, animations, and a collectible exchange.
2. **Geocaching Challenges** — The device presents riddles with approximate real-world coordinates. Solving the riddle and reaching the location reveals a physical electronic prize hidden at the spot.
3. **Collectible Ecosystem** — Digital and physical collectibles that drive community engagement, word-of-mouth marketing, and device sales.

---

## 1. Proximity Encounters — "Dilder Meet"

### How It Works

Building on the existing 13-byte BLE advertising packet (`DLDR` group ID, device ID, emotion state), encounters trigger automatically when two Dilders come within BLE range (~10-30 meters).

```
┌─────────────────────────────────────────────────────────┐
│  1. BLE SCAN detects another DLDR packet                │
│     └─ Validate: group_id match, version match,        │
│        device_id ≠ self, not seen in last 24 hours      │
├─────────────────────────────────────────────────────────┤
│  2. ENCOUNTER ALERT                                      │
│     └─ Piezo plays a unique 3-note encounter chime      │
│     └─ E-ink shows encounter animation (octopus waves)  │
│     └─ Vibration motor pulse (if installed)             │
├─────────────────────────────────────────────────────────┤
│  3. DATA EXCHANGE (BLE GATT connection)                  │
│     └─ Swap: pet name, emotion, life stage, evolution   │
│     └─ Swap: encounter count (how many others met)      │
│     └─ Swap: collectible offer (1 random from inventory)│
├─────────────────────────────────────────────────────────┤
│  4. ENCOUNTER REWARD                                     │
│     └─ Both receive a "Meeting Token" (digital)         │
│     └─ Both get +25 XP, +15 happiness, mood → Excited  │
│     └─ Encounter logged to flash (device_id, timestamp) │
│     └─ If 1st encounter ever: "First Contact" achievement│
├─────────────────────────────────────────────────────────┤
│  5. COLLECTIBLE TRADE (optional, joystick-confirmed)     │
│     └─ Each player sees what the other offers            │
│     └─ Press joystick to accept trade, or ignore        │
│     └─ Traded items are removed from giver, added to    │
│        receiver — true scarcity                          │
└─────────────────────────────────────────────────────────┘
```

### Encounter Audio — The "Dilder Chime"

Each Dilder generates a **unique 3-note signature chime** derived from its `device_id` hash. The chime serves two purposes:

- **Recognition** — Regular players learn to recognize their own Dilder's chime and can tell when a *different* Dilder is nearby by the unfamiliar tones.
- **Social signal** — In public, the chime creates a moment of surprise and curiosity for both the owner and bystanders. "What was that sound?" is the opening for a conversation about the device.

```
Chime generation:
  note_1 = MIDI_NOTE[(device_id >> 0) & 0x0F]   // 16 possible root notes
  note_2 = MIDI_NOTE[(device_id >> 4) & 0x0F]   // 16 possible second notes
  note_3 = MIDI_NOTE[(device_id >> 8) & 0x0F]   // 16 possible third notes
  duration = 150ms per note, 50ms gap between
  Total chime: ~550ms
```

The encountering Dilder plays **the other device's chime**, not its own — so both owners hear something new.

### Encounter Display Animation

The e-ink partial-refreshes a special encounter screen:

```
┌──────────────────────────────────┐
│          DILDER MEET!            │
│                                  │
│    🐙 ~~~~ 🐙                   │
│   "Sparky"  "Bubbles"           │
│                                  │
│  Sparky is feeling: EXCITED      │
│  Evolution: Reef Guardian        │
│  Encounters: 14                  │
│                                  │
│  [🎁 Trade offer: Coral Hat]     │
│  [A: Accept]  [B: Pass]         │
└──────────────────────────────────┘
```

### Encounter Cooldown & Anti-Farming

- **24-hour cooldown** per unique `device_id` — you can only benefit from meeting the same Dilder once per day.
- **5 encounters per day cap** — prevents farming at events (bonus encounters beyond 5 still log but give no XP/rewards).
- **Encounter history** stored in flash: last 256 encounters (device_id + timestamp = 8 bytes each = 2KB).

### Extended BLE Packet for Encounters

The existing 13-byte advertising packet is sufficient for detection. On GATT connection, a richer payload is exchanged:

| Field | Size | Purpose |
|-------|------|---------|
| `pet_name` | 16 bytes | Display name (UTF-8, null-padded) |
| `evolution_form` | 1 byte | Which of the 6 evolution forms (0 = unevolved) |
| `life_stage` | 1 byte | Egg/Hatchling/Juvenile/Adolescent/Adult/Elder |
| `encounter_count` | 2 bytes | Total lifetime encounters with other Dilders |
| `trade_offer_id` | 2 bytes | ID of collectible being offered for trade |
| `trade_offer_rarity` | 1 byte | Rarity tier of the offer |
| `genome` | 3 bytes | 17-bit genetic traits (for breeding compatibility) |
| **Total** | **26 bytes** | Fits in a single GATT characteristic |

---

## 2. Geocaching Challenges — "Riddle Hunts"

### Concept

Riddle Hunts extend the existing GPS treasure hunt system with **human-curated puzzles** and **physical prizes**. Instead of a random GPS coordinate with a virtual reward, the player receives:

1. A **riddle** displayed on the e-ink screen hinting at a real-world location
2. An **approximate area** (not exact coordinates) — the riddle narrows it further
3. A **physical electronic collectible** hidden at the location (waterproof capsule)

### How Riddle Hunts Differ from Treasure Hunts

| Feature | Treasure Hunt (existing) | Riddle Hunt (new) |
|---------|-------------------------|-------------------|
| Trigger | Automatic (daily, step milestones) | Community-placed or event-seeded |
| Location | Random GPS within radius | Curated real-world spot |
| Navigation | Compass + exact distance | Approximate area + riddle clue |
| Prize | Virtual (XP, cosmetics) | Physical electronic collectible |
| Difficulty | Walk there | Solve riddle + find the capsule |
| Social | Solo | Community-driven placement |
| Duration | 1 hour max | Days/weeks (persistent) |

### Riddle Format

Riddles are stored as compact text blocks in flash and displayed on the e-ink screen:

```
┌──────────────────────────────────┐
│       RIDDLE HUNT #0042          │
│                                  │
│  "Where iron horses once drank   │
│   and the clock tower still      │
│   watches, look beneath the      │
│   bench that faces west."        │
│                                  │
│  Area: Hauptbahnhof district     │
│  Radius: ~200m                   │
│  Placed: 3 days ago              │
│  Found by: 2 others              │
│                                  │
│  [A: Navigate]  [B: Skip]       │
└──────────────────────────────────┘
```

### Physical Capsule System

Each Riddle Hunt location contains a **weatherproof capsule** (3D-printed or off-the-shelf geocaching container) holding:

1. **An NFC tag** (NTAG215, ~$0.30 each) programmed with:
   - A unique collectible ID
   - A one-time-use redemption code
   - The capsule's GPS coordinates (for verification)

2. **A collectible electronic component** — a small, useful, or decorative electronic part:

| Tier | Example Physical Prize | Est. Cost | Rarity |
|------|----------------------|-----------|--------|
| **Common** | LED pack (5 assorted colors), resistor kit, jumper wire bundle | $0.50-1.00 | 60% |
| **Uncommon** | Piezo buzzer, push button switch set, header pin strips, breadboard | $1.00-2.00 | 25% |
| **Rare** | NeoPixel ring (8 LED), I2C sensor breakout (temp/humidity), small OLED display | $3.00-5.00 | 10% |
| **Legendary** | Pico W board, e-ink display module, custom Dilder sticker pack, exclusive 3MF file on USB | $5.00-15.00 | 4% |
| **Mythic** | Pre-assembled Dilder unit, signed PCB, one-of-a-kind 3D print, custom firmware personality | $15.00-40.00 | 1% |

### NFC Tap-to-Collect

When the player finds the capsule:

1. Hold the Dilder's NFC reader (PN532 or RC522, ~$3) against the NTAG215 tag
2. The Dilder reads the collectible ID and verifies it hasn't been redeemed
3. The collectible is added to the player's inventory (digital + the physical part is theirs to keep)
4. The tag is marked as "redeemed by [device_id]" — subsequent scans show "Already collected!"
5. The Dilder plays a reward animation and chime

**Alternative (no NFC hardware):** The capsule contains a printed QR code or alphanumeric code. The player enters the code via the joystick on a character-entry screen. Less elegant but works with existing hardware.

### Capsule Placement

**Who places capsules?**

- **Project team** — Seed capsules in key cities for launch events
- **Community members** — Any Dilder owner can register as a "Cache Keeper" through the website
- **Event organizers** — Hackerspaces, maker faires, meetups can request capsule kits
- **Partners** — Local electronics shops, makerspaces, or cafes can host permanent caches as foot traffic generators

**Placement rules:**

- Must be accessible without trespassing
- Must be weatherproof (IP65+ container)
- Must be retrievable without tools
- Placer registers the GPS coordinates + riddle text via the Dilder website
- Riddle is pushed to all Dilders within a configurable radius via WiFi sync (at home) or BLE relay chain

### Cache Keeper Program

Community members who place and maintain caches earn a "Cache Keeper" badge on their Dilder's profile. Benefits:

- Exclusive Cache Keeper cosmetics (treasure map background, compass hat)
- Early access to new Riddle Hunt features
- Listed on the community leaderboard as a contributor
- Receive a Cache Keeper starter kit (10 capsules, NFC tags, waterproof containers, sticker labels)

---

## 3. Collectible Ecosystem

### Digital Collectibles

Earned from encounters, riddle hunts, and regular gameplay:

| Category | Examples | Source |
|----------|---------|--------|
| **Cosmetics** | Hats, accessories, backgrounds, tentacle styles | Encounters, hunts, achievements |
| **Sound Packs** | Custom chimes, alert tones, mood music loops | Rare encounters, mythic hunts |
| **Personality Fragments** | Unlock new emotion variants or quote packs | Life stage transitions, hunts |
| **Genome Traits** | Rare breeding traits (bioluminescent, deep-sea, coral) | Mating encounters, legendary hunts |
| **Lore Fragments** | Story pieces about Jamal's ocean origins | Scattered across riddle hunts |

### Physical Collectibles (from Riddle Hunts)

See the capsule tier table above. Physical collectibles serve double duty:

1. **Immediately useful** — Electronic components the owner can use in their own projects
2. **Dilder ecosystem parts** — Some prizes are actual Dilder upgrade components (sensors, displays, batteries) that expand the device's capabilities

### Trading Between Dilders

During a proximity encounter, each player can offer one collectible for trade:

- Both players see what the other offers
- Both must accept (joystick press) for the trade to execute
- Traded items are fully transferred — the giver loses it, the receiver gains it
- Trade history is logged (prevents "I never got it" disputes)
- **No duplicate protection** — if you trade away your only Coral Hat, it's gone

### Collection Journal

The Dilder's menu system (joystick-navigated) includes a Collection Journal screen:

```
┌──────────────────────────────────┐
│       COLLECTION JOURNAL         │
│                                  │
│  Cosmetics: 12/48  ████░░░░ 25% │
│  Sounds:     3/16  ██░░░░░░ 19% │
│  Lore:       7/20  ███░░░░░ 35% │
│  Traits:     2/8   ██░░░░░░ 25% │
│  Encounters: 31                  │
│  Hunts:      8                   │
│                                  │
│  [↑↓: Browse]  [A: Details]     │
└──────────────────────────────────┘
```

---

## 4. Marketing & Community Growth Engine

### The Viral Loop

The encounter and geocaching systems create natural viral moments:

```
┌──────────────────────────────────────────────────────┐
│  1. CURIOSITY                                         │
│     Someone hears a Dilder chime in public            │
│     "What was that? What's that device?"              │
├──────────────────────────────────────────────────────┤
│  2. DEMONSTRATION                                     │
│     Owner shows the e-ink pet, explains the concept   │
│     "It's a virtual pet that reacts when it meets     │
│      other Dilders. It just detected yours would be   │
│      its first friend."                               │
├──────────────────────────────────────────────────────┤
│  3. DESIRE                                            │
│     Non-owner sees the encounter animation, the       │
│     collectibles, the personality. Wants one.         │
│     "Where do I get one? Can I build one?"            │
├──────────────────────────────────────────────────────┤
│  4. ACCESS                                            │
│     Point to GitHub (free, build your own) or         │
│     Patreon (pre-assembled kits, exclusive firmware)  │
│     or local makerspace (group build sessions)        │
├──────────────────────────────────────────────────────┤
│  5. NETWORK EFFECT                                    │
│     More Dilders = more encounters = more fun         │
│     The device is literally more valuable the more    │
│     people own one                                    │
└──────────────────────────────────────────────────────┘
```

### Marketing Channels

| Channel | Mechanism | Cost |
|---------|-----------|------|
| **Encounter chime** | Audio curiosity in public spaces — "What's that sound?" | Free (built-in) |
| **Geocaching community** | Cross-pollination with existing geocaching players who discover Dilder capsules | Capsule cost ($1-5 per cache) |
| **Maker faire demos** | Live encounter demonstrations at events | Travel + booth |
| **Hackathon challenges** | "Build a Dilder in 48 hours" — introduces the platform to makers | Prize sponsorship |
| **YouTube/TikTok content** | "Two Dilders meet for the first time" encounter videos | Free (organic) |
| **Local electronics shops** | Partner caches — "Find the Dilder cache at [shop], get 10% off components" | Revenue share |
| **University/school programs** | STEM education kits — build a Dilder as an embedded systems project | Kit cost |

### Seeded Cache Launch Strategy

For initial rollout, the project team seeds caches in phases:

| Phase | Scope | Caches | Purpose |
|-------|-------|--------|---------|
| **Alpha** | Home city (Berlin) | 10-20 | Test the system, iterate on capsule design |
| **Beta** | 5 cities with active maker communities | 50-100 | Validate cross-city engagement |
| **Launch** | Community-placed worldwide | 500+ | Cache Keeper program goes live |

### Revenue Integration

The geocaching and encounter systems create natural Patreon/shop tier differentiation:

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free (GitHub)** | $0 | Full firmware, all gameplay, BLE encounters, digital collectibles |
| **Supporter** | $5/mo | Monthly exclusive personality pack, Cache Keeper starter kit (once) |
| **Builder** | $15/mo | Pre-assembled Dilder kit, exclusive firmware personalities, early access to Riddle Hunts |
| **Legendary** | $30/mo | Custom-engraved case, unique chime, mythic-tier cache placement rights, name in firmware credits |

---

## 5. Technical Requirements

### New Hardware (beyond existing Pico W + e-ink + TP4056 + piezo)

| Component | Purpose | Cost | Phase |
|-----------|---------|------|-------|
| PN532 NFC reader | Tap-to-collect from capsules | ~$3 | Optional (QR code fallback exists) |
| PA1010D GPS | Riddle Hunt navigation | ~$12 | Phase 4B |
| QMC5883L magnetometer | Compass heading for navigation | ~$2 | Phase 4B |
| Vibration motor | Haptic encounter feedback | ~$1 | Optional |

### Firmware Modules

| Module | Size (est.) | Dependencies |
|--------|-------------|-------------|
| `encounter.h/c` | ~8KB | BLE stack, event bus, progress, dialog |
| `trade.h/c` | ~4KB | Encounter, inventory, flash persistence |
| `riddle_hunt.h/c` | ~6KB | GPS, compass, treasure system, NFC/code entry |
| `collectible.h/c` | ~5KB | Flash persistence, display, trade |
| `chime.h/c` | ~2KB | Piezo PWM, device_id hash |

### Flash Storage Budget

| Data | Size | Notes |
|------|------|-------|
| Encounter log (256 entries) | 2KB | device_id (4B) + timestamp (4B) |
| Collectible inventory (128 items) | 512B | item_id (2B) + rarity (1B) + source (1B) |
| Active riddle hunt | 256B | Riddle text + coordinates + status |
| Trade history (64 entries) | 512B | item_id + partner_id + timestamp |
| **Total** | ~3.3KB | Well within Pico W's 2MB flash |

### BLE Power Budget

| Activity | Current Draw | Duration | Frequency |
|----------|-------------|----------|-----------|
| BLE advertising | 0.1 mA avg | Continuous | Always-on when awake |
| BLE scan (passive) | 1.5 mA avg | 2s window | Every 10s |
| BLE GATT connection | 5 mA | ~3s | Per encounter |
| Piezo chime | 15 mA | 550ms | Per encounter |
| **Impact on battery** | ~0.3 mA average | — | ~5% reduction in battery life |

---

## 6. Implementation Phases

| Phase | Features | Prerequisites |
|-------|----------|---------------|
| **Phase 3A** (now) | Encounter detection via BLE scan, chime on encounter, XP/happiness reward, encounter log | BLE stack, piezo driver |
| **Phase 4A** | Collectible inventory, trading UI, collection journal | Menu system, flash persistence |
| **Phase 4B** | Riddle Hunt system, GPS navigation, compass display | GPS module, magnetometer |
| **Phase 5** | NFC tap-to-collect, physical capsule verification | NFC reader (or QR fallback) |
| **Community** | Cache Keeper program, riddle submission portal, leaderboards | Website backend |

---

## 7. Riddle Examples

Riddles should be location-specific, solvable without a phone, and family-friendly:

> **#0001 — Berlin, Kreuzberg**
> "Where the wall once stood and the spray cans still speak, find the bench where two rivers of concrete meet. Under the seat, behind the second bolt."
> *Area: East Side Gallery ±200m*

> **#0002 — London, South Bank**
> "The eye that never blinks watches over the river. Count the benches from the ticket booth — stop at seven. Look where pigeons gather below."
> *Area: London Eye ±300m*

> **#0003 — Portland, Hawthorne**
> "The store that keeps everything weird has a garden gnome who guards the east wall. He's seen the capsule. Ask him."
> *Area: Hawthorne Blvd ±150m*

---

## 8. Open Questions

- **Anti-theft**: How to prevent capsule theft vs. legitimate collection? NTAG215 tags are cheap enough to be disposable — the value is in the digital unlock, not the tag itself.
- **Cache maintenance**: Who replaces collected capsules? Cache Keepers are responsible for restocking their caches. The website dashboard shows when a cache has been fully collected.
- **Legal**: Geocaching is legal in most jurisdictions, but placement rules vary. The Cache Keeper guidelines must include local regulation checks.
- **Accessibility**: Not everyone can walk to a GPS coordinate. Virtual alternatives (WiFi-proximity riddles solved from home) should exist alongside physical hunts.
- **Cold start**: The system needs a critical mass of Dilders for encounters to happen organically. Seeded events and maker faire demos bootstrap the network.
