---
date: 2026-04-13
authors:
  - rompasaurus
categories:
  - Planning
  - Software
slug: engagement-plan
---

# The User Engagement Plan — Making Dilder Feel Alive

What makes a virtual pet worth carrying around? Not the hardware. Not the display. It's the feeling that something in your pocket needs you — and that it notices when you're there. The user engagement plan is the design document for that feeling.

<!-- more -->

## Beyond the Tamagotchi

The original Tamagotchi had a simple loop: stats decay, you feed/clean/play, the pet grows. It worked because the obligation was real — neglect it and it dies. But it was also frustrating. Miss an afternoon and your pet is gone.

Dilder takes a different approach: **no permanent death, but real consequences.** Neglect makes the octopus visibly suffer (sad, hungry, homesick), but recovery is always possible. The goal is the sweet spot between Tamagotchi's harshness and modern apps' toothlessness.

## The Stat System

Five primary stats decay in real time:

| Stat | Decay Rate | Refill |
|------|-----------|--------|
| Hunger | -1 / 10 min | Feed action |
| Happiness | -1 / 15 min | Pet, play, walk |
| Energy | -1 / 12 min | Sleep |
| Hygiene | -1 / 30 min | Clean action |
| Health | Static unless neglected | Maintain other stats |

Plus secondary stats that accumulate over time: Bond Level, Discipline, Intelligence, Fitness, Exploration. These drive evolution paths and unlock features.

## Sensor-Driven Emotions

This is where Dilder diverges from every other virtual pet. The 16 emotional states aren't just driven by stats — they respond to the **physical world** through sensors:

- **Bright light** wakes the octopus up, **darkness** triggers sleep
- **Loud noise** startles it, **sustained silence** makes it lonely
- **Gentle touch** (capacitive pads) boosts happiness
- **Walking** (accelerometer) builds fitness and triggers adventure mode
- **Temperature drops** make it shiver, **humidity** makes it happy (it's an octopus)

The emotion engine blends all these inputs: `EMOTION = f(stats, sensors, recent_events, personality)`. Transitions aren't instant — emotions fade between states over 2-3 animation frames.

## Life Stages and Evolution

Dilder grows through six life stages over 30+ real days:

```
EGG (day 0-1) → HATCHLING (1-3) → JUVENILE (3-7)
→ ADOLESCENT (7-14) → ADULT (14-30) → ELDER (30+)
```

The adult form depends on how the pet was raised. High intelligence + high bond = **Deep-Sea Scholar** (glasses, philosophical quotes). High fitness + exploration = **Reef Guardian** (muscular, encouraging). Low discipline + chaos = **Tidal Trickster** (jester hat, unpredictable).

Six distinct adult forms, each with unique visuals and dialogue. The evolution is fully deterministic — your care choices create the outcome, not random chance.

## Treasure Hunts

With a GPS module (Phase 4B), Dilder generates real-world treasure hunts. Virtual "gifts" are placed at GPS coordinates within walking distance. The e-ink display shows a compass bearing and distance — turn the device into a pirate treasure map.

Treasures range from common (60% — snack items) to mythic (<1% — one-of-a-kind cosmetics). They spawn based on step milestones, new locations, and life stage transitions. Hunts expire after 24 hours, creating urgency without punishment.

## Step Targets and Streaks

Daily step milestones drive both rewards and mood:

| Target | Steps | Effect |
|--------|-------|--------|
| Bronze | 2,000 | +10 XP, happy octopus |
| Silver | 5,000 | +25 XP, bonus snack |
| Gold | 8,000 | +50 XP, cosmetic chance |
| Platinum | 12,000 | +100 XP, guaranteed cosmetic |
| Diamond | 20,000 | Full stat restore, rare cosmetic |

Weekly and monthly targets stack on top. A 30-day streak earns a +750 XP bond boost and an exclusive cosmetic. One free miss per week prevents frustration from sick days or travel.

## The Research Behind It

The engagement plan is backed by research into 10+ virtual pet and activity games:

- **Tamagotchi** — deterministic evolution, care mistakes, stat decay rates (reverse-engineered from community documentation)
- **Digimon** — battle-based evolution (adapted as activity-based)
- **Pokemon GO** — step tracking, adventure sync, weekly rewards
- **Pikmin Bloom** — location-type cosmetics, ambient engagement
- **Finch** — real-world activity as pet nurturing (the closest modern analogue)
- **Creatures** — neural networks and artificial biochemistry (inspiration for emergent behavior)
- **Nintendogs** — touch and voice interaction patterns

## What's Next

The engagement plan is the design document — implementation starts with Phase 3A (core game loop: stats, decay, care actions, emotion resolution). Sensor integration follows in Phase 3B-3C.

The full document is published on the [Design docs page](https://dilder.dev/docs/design/user-engagement-plan/) — 21 sections, from gameplay loops to hardware sensor specs to a phased rollout plan.
