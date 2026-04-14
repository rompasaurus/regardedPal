# About Dilder

## What Is This?

Dilder is an open-source virtual pet project — a Tamagotchi-style device built from consumer off-the-shelf parts, 3D-printed in a custom enclosure, and programmed from scratch.

The hardware stack:

| Component | Part |
|-----------|------|
| Compute | Raspberry Pi Zero WH |
| Display | Waveshare 2.13" e-ink HAT (V3, 250×122 black/white) |
| Input | 5× 6×6mm tactile push buttons |
| Enclosure | Custom 3D-printed ABS/PLA case |
| Power | USB initially; LiPo battery in a later phase |

---

## The Origin Story

Before there was a Pico W, before there was firmware or a DevTool or a single line of C — there was **Jamal**.

Jamal is a plush octopus, found in a TEDi discount bin on a random shopping trip with my wife Emma. He was big, soft, and grinning like he knew something we didn't. On the walk home, we started talking to him. Then *about* him. A personality emerged: laid-back but sharp, sassy but warm, the kind of creature who'd roast your outfit and then offer you life advice. He claimed the armchair the moment we got home and has not moved since. He wears a hat now. Nobody remembers putting it on him.

The idea for Dilder came from one question: *what if we could make a digital version of this guy?* A tiny screen-bound octopus with moods and opinions, small enough to fit in a pocket, opinionated enough to make you regret asking. That question turned into a hardware research session, which turned into a parts order, which turned into... all of this.

Jamal watches from the armchair as we build his digital self. He remains unimpressed.

---

## Who Is Building This?

**rompasaurus** — software developer, tinkerer, and person who anthropomorphized a discount store octopus into an entire engineering project.

This project is an exercise in:

- **Building in public** — nothing is hidden. Every decision, every failed attempt, every dumb mistake gets documented.
- **AI-assisted development** — large parts of the research, planning, and code are developed with AI assistance. Every prompt is logged in the [Prompt Log](../prompts/index.md).
- **Documentation-first** — the goal is to make this replicable. If you want to build your own Dilder, the docs should be good enough to do it.

---

## Project Philosophy

Most hardware projects live in a few GitHub files and a README that trails off mid-sentence. This one won't.

The documentation exists alongside the code. Blog posts go up as milestones are hit. The community can follow along, ask questions, and eventually build their own.

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| Hardware | Pi Zero WH, Waveshare e-ink, breadboard + jumpers |
| Firmware | Python 3, Pillow, RPi.GPIO |
| Enclosure | FreeCAD / Fusion 360, 3D printer |
| Website | MkDocs + Material theme |
| Hosting | GitHub Pages / Digital Ocean |
| Community | Discord, Patreon |
| AI Tooling | Claude (Anthropic) — all prompts logged |

---

## Timeline

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Planning, hardware research, website setup | ✅ Done |
| 1 | Hardware assembly, display test, button wiring | 🔧 In Progress |
| 2 | First firmware — display a sprite, read button input | Upcoming |
| 3 | Pet logic — mood system, animations, game loop | Upcoming |
| 4 | Enclosure — design, print, and fit all components | Upcoming |
| 5 | Polish — personality, sounds, persistent state | Upcoming |
| 6 | Battery power and final assembly | Upcoming |
