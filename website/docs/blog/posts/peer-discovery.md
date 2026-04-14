---
date: 2026-04-13
authors:
  - rompasaurus
categories:
  - Planning
  - Software
slug: peer-discovery
---

# Peer Discovery and Mating — When Dilders Meet

What if your virtual pet could detect other Dilders nearby? What if they could interact, exchange data, and even produce offspring with inherited traits? That's the peer discovery system.

<!-- more -->

## The Concept

The Pico W has built-in BLE 5.2 (Bluetooth Low Energy). Every Dilder broadcasts a 13-byte advertisement packet containing its identity, species, mood, and genetic traits. When two devices come within BLE range (~10-30 meters), they detect each other automatically.

No Wi-Fi network needed. No internet. No pairing. Just proximity.

## What Happens When Two Dilders Meet

1. **Discovery notification** — both displays show an animation: "Someone's nearby!"
2. **Data exchange** — a BLE handshake swaps species, mood, generation, and genome data
3. **Reward** — both pets get a happiness boost, XP, and an encounter log entry
4. **Cooldown** — the same pair can't trigger again for 24 hours (prevents farming)

The encounter log records every meeting: timestamp, the other pet's species, mood, and adult form. Over time, this becomes a journal of social interactions.

## The Mating System

If both pets are adults with happiness above 70 and bond level above a threshold, a mating event can trigger. The offspring inherits traits from both parents using a genetic system:

### The Genome

Each Dilder carries a 17-bit genome encoding 6 traits:

| Trait | Bits | Options |
|-------|------|---------|
| Body Shape | 3 | 8 shapes (round, tall, wide, etc.) |
| Eye Style | 3 | 8 styles |
| Tentacle Pattern | 3 | 8 patterns |
| Color Tint | 2 | 4 tint values |
| Personality Bias | 3 | 8 personality leanings |
| Special Trait | 3 | 8 rare traits |

### Inheritance

- 45% chance each trait comes from Parent A
- 45% from Parent B
- 10% random mutation

This creates 131,072 unique possible combinations from just 308 bytes of lookup tables. The genetics calculation takes sub-microseconds on the RP2040 — the Pico has orders of magnitude more compute than this needs.

### Offspring Lifecycle

After mating, an egg appears. The user tends the egg (warmth via touch, patience) until it hatches. The offspring gets its own save slot and can eventually grow into a unique adult form influenced by its inherited genome.

## Can the Pico Handle This?

Short answer: yes, trivially.

- Genetics calculation: <1 microsecond
- Additional SRAM: ~45 bytes
- Additional flash: ~3.4KB for lookup tables
- BLE advertising: built into the CYW43439 chip

The RP2040 at 133MHz with 264KB SRAM is massively overpowered for this. The hardest part isn't computation — it's the UX design of making the mating event feel special on a 250x122 monochrome display.

## Privacy and Safety

- No personal data is transmitted — only pet data (species, mood, genome)
- No persistent connections — just one-shot BLE advertisements
- Device IDs are randomized per session
- No location data is shared between devices
- Mating requires explicit button confirmation from both users

## Implementation Timeline

This is a Phase 7 feature (Wi-Fi/BLE peer discovery). The research document covers the full protocol design, packet format, validation logic, and five implementation phases.

The full research is in the [docs folder](https://github.com/rompasaurus/dilder/blob/main/docs/peer-discovery-research.md).
