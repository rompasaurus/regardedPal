---
date: 2026-04-11
authors:
  - rompasaurus
categories:
  - Firmware
  - Architecture
slug: runtime-rendering-revolution
---

# Runtime Rendering — From 4MB Pre-Baked Frames to 30KB Firmware

The biggest architectural decision so far: throw away every pre-rendered frame and draw the octopus mathematically at runtime. The firmware went from 4MB to 30KB. This is how and why.

<!-- more -->

## The Problem with Pre-Baked Frames

The first version of the octopus firmware worked like a GIF player. The DevTool would generate every frame as a packed bitmap — octopus body, eyes, mouth expression, chat bubble, quote text — and embed them all into a `frames.h` header as C arrays. The firmware just cycled through them.

It worked. But the numbers were brutal:

- Each frame: 3,904 bytes (250 x 122 pixels, 1-bit packed)
- 4 mouth expressions x 50 quotes = 200 frames minimum
- Total: **~780KB** of frame data per program
- With two programs (Sassy + Supportive): **1.56MB** — 76% of the Pico's flash

We were running out of flash with just two personalities. Adding a third would overflow. And every quote change meant regenerating hundreds of frames and recompiling.

## The Fix: Draw Everything at Runtime

Instead of storing bitmaps, store the math. The octopus body is a set of coordinate spans. The eyes are circles. The mouth is a parametric curve. The quotes are just strings.

The new firmware draws each frame from scratch in under 1 millisecond:

```c
// Frame composition (simplified)
memset(frame, 0, sizeof(frame));      // Clear to white
draw_body();                           // RLE black silhouette
draw_eyes();                           // White circles (r²=16)
draw_pupils_normal();                  // Black circles (r²=4)
draw_mouth_smirk();                    // Parametric curve
draw_bubble();                         // Rounded rect + tail
draw_text(81, 11, quote, 158);        // 5x7 font, word-wrap
```

## What's Actually Stored

**Body (197 bytes):** Run-length encoded spans. Each row is `y, num_spans, x0, x1, ...`. The head dome is 45 rows of single spans. The tentacles are 26 rows of 5 spans each. Terminated by `0xFF`.

**Font (343 bytes):** A 5x7 bitmap font with 49 characters (A-Z, 0-9, punctuation). Each character is 7 bytes of column data.

**Drawing code (~4KB):** Circle fill, parametric curves (smirk, smile, frown, zigzag, sine wave), bubble outline with rounded corners and speech tail, word-wrapping text renderer.

**Quotes (~2-6KB):** Plain C strings in a `quotes.h` header. Each is typically 20-50 characters. A program with 30 quotes uses about 1.5KB.

**Total firmware: ~95-105KB** including the Pico SDK, SPI driver, display driver, and everything above.

## The Math Behind the Mouth

Each mouth expression is a mathematical function. The smirk, for example:

```c
for (int x = 28; x < 44; x++) {
    float t = (x - 28) / 15.0f;
    float tilt = -2.0f + t * 4.0f;
    float v = 2.0f * t - 1.0f;
    float arc = 5.0f * sqrtf(1 - v * v);
    int yc = (int)(39.0f + tilt + arc);
    px_clr_off(x, yc);       // white center
    px_set_off(x, yc - 1);   // black outline top
    px_set_off(x, yc + 1);   // black outline bottom
}
```

A tilted half-ellipse. 16 pixels wide. The angry frown is an inverted parabola. The chaotic mouth is a zigzag. The hungry mouth is an ellipse with drool drops. Each is about 10-15 lines of C.

## The Impact

| Metric | Pre-Baked | Runtime |
|--------|-----------|---------|
| Frame data per program | ~780 KB | 0 KB |
| Total firmware size | ~800 KB | ~100 KB |
| Adding a new quote | Regenerate all frames | Add one string |
| Adding a new expression | Generate new frame set | Add one function |
| Flash used (2 programs) | 76% | 10% |
| Flash used (16 programs) | Impossible | ~5% each |

The runtime approach made 16 different octopus personalities possible on the same 2MB chip, each with unique eyes, mouths, body animations, and 30+ quotes. That would have been physically impossible with pre-baked frames.

## Lessons

The obvious approach (generate all the frames) was easy to build but impossible to scale. The "harder" approach (draw everything with math) was actually less code, less data, more flexible, and faster. Sometimes the clever solution and the simple solution are the same thing — you just have to find it.
