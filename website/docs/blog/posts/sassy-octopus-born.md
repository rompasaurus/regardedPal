---
date: 2026-04-11
authors:
  - rompasaurus
categories:
  - Software
  - Firmware
slug: sassy-octopus-born
---

# The Sassy Octopus is Born

Meet the first resident of Dilder. She's got a smirk, two round eyes, five wavy tentacles, and 196 opinions about WiFi, toasters, and the meaning of ink.

<!-- more -->

## Why an Octopus?

The original Tamagotchi had a blob creature. We needed something with personality — something that could express emotion through simple pixel art on a 250x122 monochrome display. An octopus has a big expressive head (room for eyes and a mouth), a round body that reads well at low resolution, and tentacles that can wiggle, droop, or flail depending on mood.

The design is deliberately chunky. The body is a filled black silhouette defined as run-length encoded spans — 45 rows for the head dome, 9 rows for the cheek bulge, and 26 rows of five wavy tentacle columns. Total body data: 197 bytes of RLE. The eyes are white circles (radius squared = 16) punched out of the silhouette, with small black pupils and highlight dots inside them.

Everything is rendered mathematically at runtime. No bitmaps, no sprite sheets, no pre-baked frames.

## The Rendering Pipeline

Each frame follows the same composition order:

1. Clear the 250x122 frame buffer to white
2. Draw the date/time header at the top
3. Draw the octopus body from RLE data (black silhouette)
4. Punch white eye sockets (filled circles)
5. Draw mood-specific pupils (position, size, shape vary)
6. Draw any eyebrows, eyelids, or special eye effects
7. Draw the mouth expression
8. Draw the chat bubble outline with speech tail
9. Render the quote text with word-wrap
10. Transpose landscape to portrait for the e-ink driver
11. Push to display via partial refresh

The whole thing fits in about 15KB of code. The frame buffer is 3,904 bytes (250 x 122 / 8, packed 1-bit MSB-first). With the quote database, a typical octopus program compiles to ~100KB — 5% of the Pico's flash.

## The Chat Bubble

The octopus sits on the left third of the display. The right two-thirds is a rounded-rectangle chat bubble with a speech tail pointing back at the octopus. Inside: a random quote rendered in a 5x7 bitmap font with automatic word-wrapping.

The mouth cycles through 4 expressions per mood. On every "open mouth" frame, a new quote is selected. The animation runs on a 4-second cycle — one e-ink partial refresh per frame.

## 196 Quotes and Counting

The Sassy Octopus launched with 196 quotes covering food hot takes, WiFi complaints, existential octopus thoughts, and self-aware flexes. Each quote is a plain C string — no markup, no formatting. The quotes are embedded directly in a `quotes.h` header that gets compiled into the firmware.

A few favorites:

- "WIFI IS JUST SPICY AIR."
- "I HAVE 8 ARMS AND ZERO PATIENCE."
- "TOASTERS ARE JUST BREAD TANNING BEDS."

## The Programs Tab

The DevTool GUI got a Programs tab where you can select any octopus personality, preview it in the emulator, stream it to the Pico via USB serial, or deploy it as standalone firmware. Select a program and you see the octopus come to life in the canvas — cycling through its expressions, displaying random quotes, and showing estimated firmware size.

This is where the project stopped being a tech demo and started being a product. You pick a personality, you flash it, you have a pet on your desk. The whole loop works.

## What's Next

The Sassy Octopus was the proof of concept. But one personality isn't enough — we needed the octopus to feel things. Angry eyebrows, sad droopy eyes, chaotic spiral pupils. That's the emotion system, and it changed everything.
