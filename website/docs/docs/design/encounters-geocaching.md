# Encounters, Geocaching & Collectibles

> Proximity-triggered encounters between Dilders, riddle-based geocaching treasure hunts with physical electronic prizes, and a collectible ecosystem that doubles as a community growth engine.

---

## Three-Layer Gameplay System

The encounter system builds on the existing [peer discovery protocol](../../blog/posts/peer-discovery.md) and [treasure hunt system](user-engagement-plan.md) with three new layers:

1. **Proximity Encounters** — When two Dilders detect each other via BLE, both devices react with unique audio, animations, and a collectible exchange
2. **Riddle Hunts** — Curated geocaching challenges with text riddles, approximate locations, and physical electronic prizes in weatherproof capsules
3. **Collectible Ecosystem** — Digital and physical collectibles that drive community engagement and word-of-mouth marketing

---

## 1. Proximity Encounters — "Dilder Meet"

Every Dilder broadcasts a 13-byte BLE advertising packet with the `DLDR` group ID, a unique device ID, and the pet's current emotion state. When two Dilders come within BLE range (~10-30m), the encounter triggers automatically:

| Step | What Happens |
|------|-------------|
| **Detection** | BLE scan matches `DLDR` group ID, validates version, checks 24-hour cooldown |
| **Alert** | Piezo plays a unique 3-note encounter chime (derived from other device's ID hash) |
| **Display** | E-ink shows encounter screen: other pet's name, emotion, evolution form, encounter count |
| **Reward** | +25 XP, +15 happiness, mood → Excited, encounter logged to flash |
| **Trade** | Optional: each player can offer one collectible for exchange via joystick |

### The Dilder Chime

Each Dilder generates a unique 3-note audio signature from its `device_id` hash:

```
note_1 = MIDI_NOTE[(device_id >> 0) & 0x0F]   // 16 possible root notes
note_2 = MIDI_NOTE[(device_id >> 4) & 0x0F]   // 16 possible second notes
note_3 = MIDI_NOTE[(device_id >> 8) & 0x0F]   // 16 possible third notes
duration = 150ms per note, 50ms gap
Total: ~550ms
```

The encountering Dilder plays **the other device's chime** — so both owners hear something new. This creates recognition (you learn your own Dilder's voice) and curiosity (bystanders hear the chime and ask what it is).

### Encounter Display

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

### Anti-Farming

- **24-hour cooldown** per unique device_id
- **5 rewarded encounters per day** (extras log but give no XP)
- **Encounter history**: last 256 entries in flash (2KB)

### Extended GATT Payload

On BLE connection after detection, a richer 26-byte payload is exchanged:

| Field | Size | Purpose |
|-------|------|---------|
| `pet_name` | 16B | Display name (UTF-8) |
| `evolution_form` | 1B | Which of 6 evolution forms |
| `life_stage` | 1B | Current life stage |
| `encounter_count` | 2B | Lifetime encounters |
| `trade_offer_id` | 2B | Collectible offered for trade |
| `trade_offer_rarity` | 1B | Rarity tier |
| `genome` | 3B | 17-bit genetic traits |

---

## 2. Riddle Hunts — Geocaching with Physical Prizes

### How They Differ from Treasure Hunts

| Feature | Treasure Hunt (existing) | Riddle Hunt (new) |
|---------|-------------------------|-------------------|
| Trigger | Automatic (daily, milestones) | Community-placed or event-seeded |
| Location | Random GPS within radius | Curated real-world spot |
| Navigation | Compass + exact distance | Approximate area + riddle clue |
| Prize | Virtual (XP, cosmetics) | Physical electronic collectible |
| Difficulty | Walk there | Solve riddle + find capsule |
| Duration | 1 hour max | Days/weeks (persistent) |

### Riddle Display

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

### Physical Capsule Contents

Each capsule contains an NFC tag (NTAG215, ~$0.30) and a physical electronic prize:

| Tier | Example Prize | Cost | Rarity |
|------|--------------|------|--------|
| **Common** | LED pack, resistor kit, jumper wires | $0.50-1.00 | 60% |
| **Uncommon** | Piezo buzzer, breadboard, header pins | $1.00-2.00 | 25% |
| **Rare** | NeoPixel ring, I2C sensor breakout, OLED display | $3.00-5.00 | 10% |
| **Legendary** | Pico W board, e-ink display, exclusive 3MF on USB | $5.00-15.00 | 4% |
| **Mythic** | Pre-assembled Dilder, signed PCB, custom personality | $15.00-40.00 | 1% |

### Collection Mechanism

1. Find the capsule at the riddle location
2. Hold the Dilder's NFC reader against the NTAG215 tag (or enter printed code via joystick)
3. Collectible ID is verified and added to inventory
4. Tag marked as redeemed — subsequent scans show "Already collected!"
5. Reward animation plays, physical component is yours to keep

### Cache Keeper Program

Community members who place and maintain caches earn:

- Exclusive Cache Keeper cosmetics
- Early access to Riddle Hunt features
- Cache Keeper starter kit (10 capsules, NFC tags, containers, labels)
- Listed on the community leaderboard

---

## 3. Collectible Ecosystem

### Digital Collectibles

| Category | Examples | Source |
|----------|---------|--------|
| **Cosmetics** | Hats, accessories, backgrounds, tentacle styles | Encounters, hunts, achievements |
| **Sound Packs** | Custom chimes, alert tones, mood music | Rare encounters, mythic hunts |
| **Personality Fragments** | New emotion variants, quote packs | Life stage transitions, hunts |
| **Genome Traits** | Bioluminescent, deep-sea, coral | Mating encounters, legendary hunts |
| **Lore Fragments** | Story pieces about Jamal's origins | Scattered across riddle hunts |

### Trading

During encounters, each player can offer one collectible:

- Both must accept (joystick press) for the trade to execute
- Items are fully transferred — giver loses it, receiver gains it
- No duplicate protection — genuine scarcity
- Trade history logged to flash

### Collection Journal

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

## 4. Marketing & Community Growth

### The Viral Loop

```
Curiosity (chime in public) → Demonstration (encounter animation)
  → Desire (want one) → Access (GitHub free / Patreon kit)
    → Network Effect (more Dilders = more encounters = more fun)
```

### Revenue Tiers

| Tier | Price | What You Get |
|------|-------|-------------|
| **Free** | $0 | Full firmware, all gameplay, BLE encounters, digital collectibles |
| **Supporter** | $5/mo | Monthly personality pack, Cache Keeper starter kit |
| **Builder** | $15/mo | Pre-assembled kit, exclusive personalities, early Riddle Hunts |
| **Legendary** | $30/mo | Custom-engraved case, unique chime, mythic cache placement rights |

---

## 5. Technical Requirements

### Hardware Additions

| Component | Purpose | Cost | Phase |
|-----------|---------|------|-------|
| PN532 NFC reader | Tap-to-collect | ~$3 | Optional |
| PA1010D GPS | Riddle Hunt navigation | ~$12 | Phase 4B |
| QMC5883L magnetometer | Compass heading | ~$2 | Phase 4B |
| Vibration motor | Haptic encounter feedback | ~$1 | Optional |

### Flash Budget

| Data | Size |
|------|------|
| Encounter log (256 entries) | 2KB |
| Collectible inventory (128 items) | 512B |
| Active riddle hunt | 256B |
| Trade history (64 entries) | 512B |
| **Total** | ~3.3KB |

### Power Impact

BLE encounter scanning adds ~0.3 mA average to the power budget — approximately 5% reduction in battery life. The chime draws 15 mA for 550ms per encounter.

---

## Implementation Phases

| Phase | Features |
|-------|----------|
| **3A** | BLE encounter detection, chime, XP/happiness reward, encounter log |
| **4A** | Collectible inventory, trading UI, collection journal |
| **4B** | Riddle Hunt system, GPS navigation, compass display |
| **5** | NFC tap-to-collect, physical capsule verification |
| **Community** | Cache Keeper program, riddle portal, leaderboards |

---

Full design doc: [`Gamplay Planning/14-encounters-geocaching-collectibles.md`](https://github.com/rompasaurus/dilder/blob/main/Gamplay%20Planning/14-encounters-geocaching-collectibles.md)
