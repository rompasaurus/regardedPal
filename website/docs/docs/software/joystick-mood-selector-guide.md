# How the Joystick Mood Selector Works — A Beginner's Guide

This guide explains how the joystick mood selector firmware works, from the moment you click "Deploy" to the octopus appearing on screen. Written so a 12-year-old can follow along.

---

## What This Program Does

The joystick mood selector is a program that runs on a tiny computer (the Pico 2 W) connected to a small black-and-white screen. It draws a pixel-art octopus with a speech bubble, shows a funny quote, and lets you change the octopus's mood using a 5-way joystick.

Every 4 seconds, the octopus opens its mouth (like it's talking), picks a new quote, and the screen updates. Push the joystick left or right to cycle through 16 moods. Each mood changes the eyes, mouth, body animation, and which quotes appear.

---

## The File Structure

Here's what's inside the project folder:

```
joystick-mood-selector/
├── main.c                    The actual program (1,441 lines of C code)
├── quotes.h                  823 funny quotes, auto-generated
├── CMakeLists.txt            Build instructions (like a recipe card)
├── pico_sdk_import.cmake     Tells the build system where the Pico SDK lives
└── lib/                      Shared helper code
    ├── Config/
    │   ├── DEV_Config.c      Talks to the hardware (SPI bus, GPIO pins)
    │   ├── DEV_Config.h      Pin number definitions
    │   └── rtc_compat.h      Clock compatibility for different Pico boards
    ├── e-Paper/
    │   ├── EPD_2in13_V4.c    The e-ink display driver (sends pixels to screen)
    │   ├── EPD_2in13_V4.h    Driver function declarations
    │   └── (V2, V3, V3a)     Older display drivers (for different screen versions)
    └── version.h             Firmware version number
```

**Think of it like this:**

- `main.c` is the **brain** — it decides what to draw and when
- `lib/e-Paper/` is the **mouth** — it knows how to talk to the screen
- `lib/Config/` is the **nervous system** — it connects the brain to the actual hardware pins
- `quotes.h` is the **memory** — all the jokes the octopus knows

---

## How It Gets Built (Compiled)

The Pico 2 W speaks ARM machine code, but we write in C (which humans can read). A **compiler** translates our C code into machine code. Here's the chain:

```
Your C code (main.c)
       │
       ▼
   CMake reads CMakeLists.txt
   (figures out which files to compile and how)
       │
       ▼
   ARM cross-compiler (gcc-arm-none-eabi)
   (translates C → ARM machine code)
       │
       ▼
   Linker combines everything into one binary
       │
       ▼
   joystick_mood_selector.uf2
   (a file the Pico understands)
```

### What CMakeLists.txt Does

The `CMakeLists.txt` file is like a recipe card. It tells the build system:

1. **Which files to compile:** `main.c`, `DEV_Config.c`, and whichever display driver matches your screen version
2. **Which libraries to link:** `pico_stdlib` (basic functions), `hardware_spi` (SPI communication), `hardware_gpio` (pin control), `hardware_adc` (random number seeding), `m` (math for animations)
3. **Which display driver to use:** The `DISPLAY_VARIANT` flag selects V2, V3, V3a, or V4. Default is V4 for current hardware

```cmake
# If nobody specified a variant, use V4
if(NOT DEFINED DISPLAY_VARIANT)
    set(DISPLAY_VARIANT "V4")
endif()

# Pick the right driver file based on the variant
if(DISPLAY_VARIANT STREQUAL "V4")
    set(EPD_SOURCE lib/e-Paper/EPD_2in13_V4.c)
    set(EPD_DEFINE DISPLAY_V4)
endif()
```

### The Docker Build Environment

You can't compile ARM code on a regular PC without special tools. The project uses Docker — a system that creates a mini virtual computer with all the right tools pre-installed:

```
┌─────────────────────────────────────────────┐
│  Docker Container                           │
│                                             │
│  Ubuntu 24.04                               │
│  + gcc-arm-none-eabi  (ARM compiler)        │
│  + cmake + ninja      (build tools)         │
│  + Pico SDK           (hardware library)    │
│                                             │
│  Your code gets mounted into /project/      │
│  Build runs automatically:                  │
│    cmake → ninja → joystick_mood_selector.uf2│
└─────────────────────────────────────────────┘
```

### Flashing to the Pico

1. Hold the **BOOTSEL** button on the Pico 2 W
2. Plug in the USB cable (keep holding)
3. Release BOOTSEL — a USB drive named `RP2350` appears
4. Copy the `.uf2` file onto that drive
5. The Pico reboots and starts running your code immediately

---

## How the Display Works

### The Screen

The Waveshare 2.13" e-ink display is 250 pixels wide and 122 pixels tall. It's **black and white only** — each pixel is either on (black) or off (white). No grays, no colors.

E-ink displays are special: they only use power when changing the image. Once the pixels are set, they stay visible even if you unplug everything. That's why they look like paper.

### Talking to the Screen (SPI)

The Pico talks to the display using **SPI** (Serial Peripheral Interface) — a way for chips to send data over wires. Six wires connect them:

| Wire | Pin | Purpose |
|------|-----|---------|
| CLK | GP10 | Clock — ticks to sync the data |
| DIN | GP11 | Data In — the actual pixel data |
| CS | GP9 | Chip Select — "hey screen, I'm talking to you" |
| DC | GP8 | Data/Command — tells screen if it's receiving a command or pixel data |
| RST | GP12 | Reset — restarts the screen controller |
| BUSY | GP13 | Busy — screen says "wait, I'm still updating" |

To send a command (like "start updating"):
```c
DC pin LOW       // "This is a command"
CS pin LOW       // "Listen up"
Send byte 0x20   // The command code
CS pin HIGH      // "Done talking"
```

To send pixel data:
```c
DC pin HIGH      // "This is data"
CS pin LOW       // "Listen up"
Send 3,904 bytes // Every pixel on the screen
CS pin HIGH      // "Done talking"
```

### The Frame Buffer — Drawing Before Displaying

The program doesn't draw directly to the screen. Instead, it draws into a chunk of memory called the **frame buffer** — like sketching on paper before photocopying it.

```c
#define IMG_W         250              // 250 pixels wide
#define IMG_H         122              // 122 pixels tall
#define IMG_ROW_BYTES ((IMG_W + 7) / 8)  // 32 bytes per row

static uint8_t frame[IMG_ROW_BYTES * IMG_H];  // 3,904 bytes total
```

**Why 32 bytes per row?** Each pixel is just one bit (on or off). We pack 8 pixels into each byte. 250 pixels / 8 = 31.25, rounded up to 32 bytes.

**How pixels are stored:**

```
Byte:        [10110100]
Pixel index:  0 1 2 3 4 5 6 7
Value:        1 0 1 1 0 1 0 0
              ■ □ ■ ■ □ ■ □ □

■ = black (bit is 1)
□ = white (bit is 0)
```

To turn a single pixel black:
```c
static inline void px_set(int x, int y) {
    frame[y * IMG_ROW_BYTES + x / 8] |= (0x80 >> (x & 7));
}
```

Breaking this down:
- `y * IMG_ROW_BYTES + x / 8` — finds which byte the pixel lives in
- `x & 7` — finds which bit within that byte (0-7)
- `0x80 >> (x & 7)` — creates a mask with just that one bit set
- `|=` — turns that bit on without touching the others

### The Landscape-to-Portrait Rotation

Here's a trick: the program draws everything in **landscape** (250 wide x 122 tall, like a TV), but the e-ink controller expects data in **portrait** (122 wide x 250 tall, like a phone). So after drawing, the entire image gets rotated 90 degrees:

```c
static void transpose_to_display(void) {
    for (int y = 0; y < IMG_H; y++) {
        for (int x = 0; x < IMG_W; x++) {
            if (pixel_is_black_at(x, y)) {
                int new_x = y;          // Old Y becomes new X
                int new_y = 249 - x;    // Old X becomes new Y (flipped)
                set_pixel_in_display_buf(new_x, new_y);
            }
        }
    }
}
```

**Why not just draw in portrait?** Because it's much easier to think about layout in landscape. The octopus is on the left, the speech bubble on the right, text flows left-to-right. Drawing in portrait would mean everything is sideways in your head.

### Full Refresh vs. Partial Refresh

E-ink screens have two ways to update:

**Full refresh (~2 seconds):** The screen flashes black, then white, then shows the new image. It looks like a camera flash. Every pixel gets fully driven to its new state. No ghosting, but slow and flashy.

**Partial refresh (~0.3 seconds per pass):** Only the pixels that changed get updated. Fast and smooth, but the old pixels can leave faint "ghost" traces because they don't get fully erased.

The V4 driver uses a **two-pass partial refresh** to get the best of both:

```
Pass 1 (Clear): Find pixels that changed → drive them to white
Pass 2 (Draw):  Draw the new content on a clean white background
```

This takes about 0.8 seconds total but produces clean, ghost-free updates.

---

## How the Octopus Gets Drawn

Every frame, the `render_frame()` function draws 7 layers in order:

```
Layer 1: Clock header    "MAY 4, 2026  2:30 PM"
Layer 2: Body            The octopus shape (dome + tentacles)
Layer 3: Eye sockets     Two white circles
Layer 4: Pupils          Mood-specific (dots, rings, crosses, etc.)
Layer 5: Eyebrows/lids   Mood-specific (angry brows, tired lids, etc.)
Layer 6: Mouth           18 different expressions
Layer 7: Speech bubble   Rectangle with quote text inside
Layer 8: Status bar      "< SASSY >" centered, "LEFT" on the right
```

### The Body — Run-Length Encoding

The octopus body is stored as a list of horizontal line segments (spans):

```c
static const uint8_t body_rle[] = {
    10, 1, 22, 48,        // Row 10: one span from x=22 to x=48
    11, 1, 18, 52,        // Row 11: one span from x=18 to x=52
    ...
    55, 5, 10,17, 21,28, 32,39, 43,50, 54,61,  // Row 55: five spans (tentacles!)
    ...
    0xFF                   // End marker
};
```

**Why RLE?** Drawing a circle with `px_set()` one pixel at a time would need hundreds of individual pixel coordinates. RLE stores the same shape as "fill from x=22 to x=48 on row 10" — much more compact.

The body can also be **animated** per mood:

| Mood | Animation |
|------|-----------|
| Angry | Trembles + expands horizontally |
| Chaotic | Random offset each frame |
| Lazy | Tilts right, lounging |
| Excited | Bounces up and down |
| Normal | Gentle breathing bob |

### The 16 Moods

Each mood changes four things:

1. **Pupils** — shape and position (dots, rings, crosses, lines)
2. **Eyebrows/eyelids** — angry brows, sad brows, tired lids
3. **Mouth** — 18 different expressions (smirk, frown, zigzag, fangs)
4. **Body animation** — trembling, bouncing, wobbling, tilting

The moods cycle through a 4-frame **expression loop**:

```c
// ANGRY mood cycle: frown → open → frown → frown
static const uint8_t cycle_angry[] = {
    EXPR_ANGRY, EXPR_OPEN, EXPR_ANGRY, EXPR_ANGRY
};
```

Frame 0 shows the angry frown. Frame 1 opens the mouth (like talking). Frames 2-3 return to angry. Then it loops.

### The Font — A 5x7 Bitmap

Each character is stored as a 5-wide, 7-tall grid of bits:

```
Letter "A":
  .XXX.    → 0x0e (00001110)
  X...X    → 0x11 (00010001)
  X...X    → 0x11
  XXXXX    → 0x1f (00011111)
  X...X    → 0x11
  X...X    → 0x11
  X...X    → 0x11
```

Text rendering walks through each character, looks up its glyph, and stamps the pixels. Words wrap to the next line when they'd overflow the speech bubble.

---

## The Main Loop — Putting It All Together

Here's the program's heartbeat, simplified:

```
1. Boot up
   ├── Initialize USB serial (for debug output)
   ├── Initialize SPI (for display communication)
   ├── Initialize GPIO (for joystick buttons)
   ├── Initialize display (full screen clear)
   └── Print version info to serial

2. Main loop (runs forever)
   │
   ├── Pick expression from 4-frame mood cycle
   ├── Pick a random quote matching the current mood
   │
   ├── RENDER (draw everything into the frame buffer)
   │   ├── Clear frame to white
   │   ├── Draw clock header
   │   ├── Draw octopus body (with animation transform)
   │   ├── Draw eyes → pupils → eyebrows
   │   ├── Draw mouth expression
   │   ├── Draw speech bubble + quote text
   │   └── Draw status bar (mood name + last input)
   │
   ├── ROTATE (landscape → portrait)
   │
   ├── DISPLAY (send to screen)
   │   ├── Frame 0: EPD_Base() — full refresh, seeds both RAM buffers
   │   └── Frame 1+: EPD_Partial() — two-pass partial refresh
   │
   └── WAIT 4 SECONDS (while polling for input)
       ├── Every 200ms: check joystick GPIO pins
       │   ├── LEFT pressed?  → previous mood
       │   ├── RIGHT pressed? → next mood
       │   ├── UP pressed?    → random mood
       │   ├── DOWN pressed?  → new random quote
       │   └── CENTER pressed?→ reset to SASSY
       │
       ├── Every 50ms: check USB serial for keyboard input
       │
       └── Every 2s: print GPIO pin states (debug)
```

### How Joystick Input Works

The joystick is a 5-way switch with one common (ground) pin and 5 signal pins. Each direction connects its signal pin to ground when pressed. The Pico's internal **pull-up resistors** keep the pins at HIGH (1) when nothing is pressed.

```
Not pressed:   3.3V ──[pull-up]──● GPIO pin reads HIGH (1)

Pressed:       3.3V ──[pull-up]──●──[switch]──GND
                                 GPIO pin reads LOW (0)
```

The code checks:
```c
if (gpio_get(JOY_LEFT) == 0) {
    // LEFT is pressed! Do something.
}
```

**Debouncing:** Mechanical switches bounce (rapidly toggle on/off) for a few milliseconds when pressed. Without debouncing, one press could register as 5-10 presses. The 200ms debounce timer prevents this — after detecting a press, it ignores that pin for 200ms.

---

## The Display Driver Deep Dive

### Why Two RAM Buffers?

The SSD1680 display controller has two separate memory banks:

- **RAM 0x24** — the "new" image (what you want to show)
- **RAM 0x26** — the "old" image (what was shown before)

For a partial refresh, the controller **compares** these two buffers and only drives the pixels that are different. This is much faster than redrawing everything.

### The Two-Pass Partial Refresh

The problem: the partial waveform is weak. It can make white pixels go black easily, but making black pixels go white is harder. Old black content leaves ghost traces.

The solution: clear changed pixels first, then draw new content.

```c
// Pass 1: Build a "clear" frame
// Pixels black in BOTH old and new → stay black
// Everything else → white (erases stale content)
for (int i = 0; i < BUFFER_SIZE; i++) {
    clear_buf[i] = prev_frame[i] & new_frame[i];
}
// Partial refresh: old=prev_frame, new=clear_buf → erases stale pixels

// Pass 2: Draw the actual new content
// Partial refresh: old=clear_buf, new=actual_frame → draws new pixels
```

The `AND` operation is the clever part:

| Old pixel | New pixel | AND result | What happens |
|-----------|-----------|------------|--------------|
| Black (1) | Black (1) | Black (1) | Stays black (no change needed) |
| Black (1) | White (0) | White (0) | Old content gets erased |
| White (0) | Black (1) | White (0) | Will be drawn in pass 2 |
| White (0) | White (0) | White (0) | Stays white (no change needed) |

---

## Key Design Decisions

### Why C Instead of Python?

The Pico 2 W can run MicroPython, but C gives:
- **Direct hardware control** — we talk to the SPI bus and GPIO pins directly
- **Speed** — frame rendering takes ~1ms in C vs ~50ms in Python
- **Small binary** — the entire firmware is ~100KB, leaving plenty of room in the 4MB flash
- **No garbage collector** — no random pauses while drawing

### Why Draw in Landscape and Rotate?

The display hardware is physically portrait (122 wide). But humans think in landscape — the octopus on the left, bubble on the right, text flowing left-to-right. Drawing in landscape and rotating at the end means the coordinate system makes intuitive sense throughout the drawing code.

### Why Run-Length Encoding for the Body?

The octopus body has smooth curves and wide horizontal spans. RLE compresses this efficiently — instead of storing 3,000+ individual pixel coordinates, the body is defined by ~200 span endpoints. It's also easy to apply transformations (shift, expand, wobble) to the spans during rendering.

### Why 4-Second Frame Delay?

E-ink displays take about 0.8 seconds to do a two-pass partial refresh. With a 4-second cycle, you get 3.2 seconds of polling time for input. The octopus "talks" at a natural pace — fast enough to feel alive, slow enough to read each quote.

---

## Glossary

| Term | Meaning |
|------|---------|
| **Frame buffer** | A chunk of memory representing the screen contents, drawn before sending to display |
| **SPI** | Serial Peripheral Interface — a 4-wire communication protocol between chips |
| **GPIO** | General Purpose Input/Output — pins on the Pico that can be set HIGH/LOW or read |
| **Pull-up resistor** | Internal resistor that keeps a pin at HIGH when nothing is connected |
| **Debounce** | Ignoring rapid on/off toggles from a mechanical switch |
| **RLE** | Run-Length Encoding — storing shapes as horizontal spans instead of individual pixels |
| **LUT** | Lookup Table — waveform timing data that tells the e-ink controller how to drive pixels |
| **UF2** | USB Flashing Format — the binary file format the Pico accepts via drag-and-drop |
| **Cross-compiler** | A compiler that runs on one CPU type (x86) but produces code for another (ARM) |
| **Partial refresh** | Updating only changed pixels instead of the whole screen |
