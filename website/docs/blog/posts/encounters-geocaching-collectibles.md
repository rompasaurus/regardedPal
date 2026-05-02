---
date: 2026-05-03
authors:
  - rompasaurus
categories:
  - Software
  - Hardware
tags:
  - gameplay
  - ble
  - proximity
  - geocaching
  - collectibles
  - marketing
---

# Dilders That Find Each Other, Hide Treasures, and Grow a Community

Today's design session went deep on a question that's been simmering since the peer discovery research: **what actually happens when two Dilders meet?** The answer turned into a three-layer system — proximity encounters with unique audio signatures, riddle-based geocaching challenges with physical electronic prizes, and a collectible ecosystem that naturally markets the device to new people.

<!-- more -->

## The Encounter Problem

The existing BLE peer discovery spec (13-byte advertising packet, `DLDR` group ID, 24-hour cooldown) handles *detection* — but detection alone is boring. "Your Dilder saw another Dilder" is a notification, not an experience. The encounter needs to be a *moment* — something both owners feel and remember.

## The Dilder Chime

Every Dilder gets a **unique 3-note audio signature** generated from its device ID hash. When two Dilders detect each other via BLE, each one plays *the other's* chime through its piezo speaker. You hear an unfamiliar melody — that's the other Dilder introducing itself.

This does three things:

1. **Recognition** — Regular players learn their own Dilder's voice and can tell when a stranger is nearby
2. **Curiosity** — Bystanders hear the chime and ask "what was that?" — a natural conversation starter about the device
3. **Memory** — Each encounter has a distinct sound. You remember the chime from the Dilder you met at the park last Tuesday

The chime is ~550ms (three 150ms notes with 50ms gaps). Short enough to not be annoying, long enough to notice.

## What Happens During an Encounter

After the chime, the e-ink display shows a meeting screen with the other pet's name, emotion, evolution form, and encounter count. If either player has a collectible to trade, it appears as an offer — press the joystick to accept, or ignore it.

Both players get an automatic reward: +25 XP, +15 happiness, mood jumps to Excited, and the encounter is logged to flash memory. A 24-hour cooldown per unique device prevents farming, and a daily cap of 5 rewarded encounters keeps it special.

The encounter log (256 entries, 2KB) becomes a personal history — "I've met 31 different Dilders, 14 of them more than once."

## Riddle Hunts — Geocaching with a Twist

The existing treasure hunt system places virtual rewards at random GPS coordinates. Riddle Hunts build on this with something more human: **a riddle hints at a real-world location where a physical prize is hidden**.

Instead of exact coordinates, the player gets an approximate area (~200m radius) and a text riddle:

> *"Where iron horses once drank and the clock tower still watches, look beneath the bench that faces west."*
> *Area: Hauptbahnhof district, ~200m*

The riddle narrows it down. The player has to think, explore, and physically search — not just walk to a GPS pin.

### The Capsule

At the location sits a waterproof capsule containing:

- An **NFC tag** (NTAG215, ~$0.30) with a unique collectible ID and one-time redemption code
- A **physical electronic component** — something actually useful

The prizes are tiered: common capsules have LED packs or resistor kits ($0.50-1.00). Rare ones have sensor breakouts or NeoPixel rings ($3-5). Legendary capsules might contain an actual Pico W board or exclusive 3MF files on a USB stick. Mythic capsules — placed once or twice per city — could hold a pre-assembled Dilder unit.

The player taps the capsule's NFC tag against their Dilder (or enters a printed code via joystick if they don't have an NFC reader). The digital collectible unlocks, and the physical part is theirs to keep.

### Who Places the Capsules?

This is where it becomes a community system:

- **Project team** seeds initial caches in Berlin for alpha testing
- **Cache Keepers** — community members who register on the website — place and maintain caches worldwide
- **Event organizers** (maker faires, hackerspaces) can request capsule kits
- **Partner shops** (local electronics stores, cafes) host permanent caches as foot traffic generators

Cache Keepers write their own riddles, register GPS coordinates on the website, and the riddle is pushed to nearby Dilders via WiFi sync.

## The Marketing Engine

Here's the part that excites me most: **the encounter system is inherently viral**.

The chime creates curiosity in public spaces. The bystander asks what the device is. The owner demonstrates an encounter, shows the collectibles, explains the geocaching challenges. The bystander wants one.

Then the pitch is frictionless:
- **Free**: Full firmware and hardware designs on GitHub. Build your own for ~$25.
- **Easy**: Pre-assembled kits on Patreon for people who don't want to solder.
- **Valuable**: The more Dilders exist, the more encounters happen, the more fun everyone has. It's a genuine network effect — the device is literally worth more when more people own one.

The geocaching system cross-pollinates with the existing geocaching community. Someone finds a Dilder capsule at a location they were already caching at. They've never heard of Dilder, but now they've got a sensor breakout board and a curiosity.

## Collectible Ecosystem

Digital collectibles earned from encounters and hunts fill a Collection Journal:

- **Cosmetics** — Hats, accessories, backgrounds, tentacle styles
- **Sound Packs** — Custom chimes and mood music
- **Personality Fragments** — New emotion variants and quote packs
- **Genome Traits** — Rare breeding characteristics (bioluminescent, deep-sea, coral)
- **Lore Fragments** — Story pieces about Jamal's ocean origins, scattered across riddle hunts worldwide

Trading is real: during an encounter, each player can offer one collectible. If both accept, the items swap. No duplicates, no take-backs — genuine scarcity.

## What's Needed

The encounter system works with **existing hardware** — Pico W's BLE + piezo speaker + e-ink display. No new components needed for Phase 3A.

Riddle Hunts need a GPS module (PA1010D, ~$12) and magnetometer (QMC5883L, ~$2) for compass navigation — already planned for Phase 4B.

NFC tap-to-collect needs a PN532 reader (~$3) but has a QR/code-entry fallback for builds without it.

The full design doc lives at `Gamplay Planning/14-encounters-geocaching-collectibles.md` with packet specs, flash budgets, power analysis, riddle examples, and the Cache Keeper program details.

## Why This Matters

Most hardware projects die because they solve a problem nobody has. Dilder doesn't solve a problem — it creates a *community*. The encounter system gives people a reason to carry their Dilder outside. The geocaching system gives them a reason to explore. The collectibles give them a reason to keep playing. And every chime in a coffee shop is a free advertisement that sounds like a tiny octopus saying hello.
