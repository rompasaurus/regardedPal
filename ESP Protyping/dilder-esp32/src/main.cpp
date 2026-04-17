/*
 * ======================================================================
 *  Dilder ESP32-S3 — Mood Selector
 * ======================================================================
 *
 *  PURPOSE
 *  -------
 *  This file is the entire application for an ESP32-S3 "mood pet" device.
 *  It renders an animated octopus on a small e-Paper (e-Ink) display,
 *  cycling through 16 emotional states with 823 sassy quotes.  The user
 *  navigates moods via a 5-way joystick or serial keyboard commands.
 *
 *  ARCHITECTURE
 *  ------------
 *  The rendering engine is *platform-independent* — it was originally
 *  written for the Raspberry Pi Pico W and then ported here.  All
 *  drawing happens into a plain byte-array framebuffer (`frame[]`).
 *  Only the very bottom of the file touches ESP32-specific APIs (SPI
 *  init, GxEPD2 display push, esp_random() for hardware RNG).
 *
 *  Rendering pipeline (each frame):
 *    1. Clear framebuffer to all-white
 *    2. Draw clock header (top center)
 *    3. Draw octopus body (RLE-decoded outline)
 *    4. Draw eyes (white circles carved into body)
 *    5. Draw pupils (mood-specific: dots, rings, stars, etc.)
 *    6. Draw eyebrows / eyelids / tears if the mood calls for them
 *    7. Draw mouth (mood-specific expression)
 *    8. Draw speech bubble (rounded rectangle with a triangular tail)
 *    9. Draw quote text inside the bubble
 *   10. Draw status bar ("< MOOD NAME >") at the bottom
 *   11. Push finished framebuffer to the e-Paper display
 *
 *  WHY C++ (.cpp) WRAPPING C-STYLE CODE
 *  -------------------------------------
 *  This file is compiled as C++ because the Arduino framework and the
 *  GxEPD2 / Adafruit_GFX libraries are C++ (they use classes, templates,
 *  and overloading).  However, most of *our* rendering code is plain C:
 *  no classes, no exceptions, no STL.  The HAL (Hardware Abstraction
 *  Layer) headers are pure C, so we include them inside an `extern "C"`
 *  block to prevent the C++ compiler from "name-mangling" those symbols.
 *  (C++ normally decorates function names with type info for overloading;
 *  `extern "C"` tells it to use the simpler C naming convention so the
 *  linker can find the HAL functions compiled by the C compiler.)
 *
 *  ARDUINO EXECUTION MODEL
 *  -----------------------
 *  Traditional C/C++ programs start at `main()`.  The Arduino framework
 *  hides `main()` inside its own startup code.  Instead, you provide two
 *  functions:
 *
 *    setup() — called ONCE after the chip boots.  Initialize hardware,
 *              configure pins, set up serial, etc.
 *
 *    loop()  — called REPEATEDLY forever after setup() returns.  This is
 *              your main application loop.  Each call = one iteration.
 *              (Think of it as the body of `while (true) { ... }`.)
 *
 *  Input:
 *    Joystick LEFT/RIGHT = cycle moods
 *    Joystick CENTER     = random mood
 *    Joystick UP         = new quote (same mood)
 *    Joystick DOWN       = show chip info
 *    Serial keyboard     = same keys as Pico version ([/] navigate, etc.)
 *
 *  Display: Waveshare 2.13" V3 (SSD1680) via GxEPD2, landscape 250x122.
 * ======================================================================
 */

/* ── Standard includes ─────────────────────────────────────────────────
 *
 *  <Arduino.h>     — Core Arduino API: Serial, delay(), millis(),
 *                     pinMode(), digitalRead(), etc.  Always include
 *                     this first in a PlatformIO / Arduino project.
 *
 *  <SPI.h>         — Arduino SPI library.  Provides the global `SPI`
 *                     object used to talk to the e-Paper display.
 *
 *  <GxEPD2_BW.h>   — GxEPD2 e-Paper library for black-and-white
 *                     displays.  Wraps the low-level SSD1680 controller
 *                     protocol behind a convenient Adafruit_GFX-
 *                     compatible API (drawBitmap, fillScreen, etc.).
 *
 *  <Adafruit_GFX.h> — Graphics primitives base class that GxEPD2
 *                     inherits from.  We don't call it directly, but
 *                     it's required by GxEPD2's template.
 *
 *  <math.h>        — C math: sinf(), sqrtf(), fabsf().
 *                     Used for body wobble animations and curved mouths.
 *
 *  <string.h>      — C strings: memset(), strlen().
 *                     memset() zeroes the framebuffer; strlen() measures
 *                     strings for centering text on screen.
 *
 *  <stdio.h>       — C formatted I/O: snprintf().
 *                     Used to format the clock string and status bar.
 * ──────────────────────────────────────────────────────────────────── */
#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

/*
 * extern "C" { ... }
 *
 * These two header files are written in pure C.  When the C++ compiler
 * sees a function declaration, it normally "mangles" the name — e.g.,
 * `hal_btn_up` might become `_Z10hal_btn_upv` internally — so it can
 * support function overloading (same name, different parameter types).
 *
 * The HAL implementation files are compiled separately as C, which does
 * NOT mangle names.  If we included these headers without `extern "C"`,
 * the C++ compiler would look for the mangled name at link time and
 * fail with "undefined reference."
 *
 * `extern "C"` says: "These functions use C linkage — don't mangle
 * the names."  This is the standard pattern for mixing C and C++ code.
 *
 * board_config.h — Provides hardware pin macros (PIN_EPD_CS, PIN_BTN_UP,
 *                  BOARD_NAME, etc.) selected at compile time based on
 *                  which board you're building for.
 *
 * hal.h          — Hardware Abstraction Layer.  Declares functions like
 *                  dilder_hal_init(), hal_btn_left(), hal_btn_right()
 *                  that are implemented differently for each target board.
 */
extern "C" {
#include "platform/board_config.h"
#include "platform/hal.h"
}

/* ── Display setup ─────────────────────────────────────────────────────
 *
 *  GxEPD2 uses C++ templates to create a display object tailored to the
 *  specific e-Paper panel you have.  Let's break down this declaration:
 *
 *    GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT>
 *
 *  - GxEPD2_BW         — Template class for Black & White e-Paper.
 *  - GxEPD2_213_BN     — Driver class for the 2.13" BN panel (SSD1680).
 *  - ::HEIGHT           — The display's native height in pixels.  The
 *                         template uses this to size an internal page
 *                         buffer (the display is too large for a single
 *                         full-screen buffer on some MCUs, so GxEPD2
 *                         renders in horizontal "pages" or stripes).
 *
 *  Constructor arguments — the GPIO pin numbers for the SPI control
 *  signals.  These come from board_config.h:
 *    PIN_EPD_CS   — Chip Select: pulled LOW to select this SPI device.
 *    PIN_EPD_DC   — Data/Command: tells the display whether we're
 *                   sending a command byte or pixel data.
 *    PIN_EPD_RST  — Reset: pulse LOW to hardware-reset the controller.
 *    PIN_EPD_BUSY — Busy: the display pulls this HIGH while it's
 *                   updating its e-Ink particles (can take ~2 seconds).
 * ──────────────────────────────────────────────────────────────────── */
GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT>
    display(GxEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RST, PIN_EPD_BUSY));

/* ── Canvas constants (same as Pico) ───────────────────────────────────
 *
 *  IMG_W / IMG_H define our logical canvas size in pixels (landscape).
 *
 *  IMG_ROW_BYTES is how many bytes one horizontal row takes in the
 *  framebuffer.  Each pixel is 1 bit (black or white), so we need
 *  ceil(250 / 8) = 32 bytes per row.  The expression (IMG_W + 7) / 8
 *  is a common trick for ceiling integer division:
 *    (250 + 7) / 8 = 257 / 8 = 32  (integer division rounds down)
 * ──────────────────────────────────────────────────────────────────── */
#define IMG_W         250
#define IMG_H         122
#define IMG_ROW_BYTES ((IMG_W + 7) / 8)

/* ── Mood definitions ──────────────────────────────────────────────────
 *
 *  Each mood is assigned an integer ID (0-15).  These are used as
 *  indices into mood_names[], as values in the Quote struct, and as
 *  cases in switch statements throughout the rendering engine.
 *
 *  MOOD_COUNT is used for bounds checking and wrapping (e.g.,
 *  `(current_mood + 1) % MOOD_COUNT` wraps from 15 back to 0).
 * ──────────────────────────────────────────────────────────────────── */
#define MOOD_NORMAL    0
#define MOOD_WEIRD     1
#define MOOD_UNHINGED  2
#define MOOD_ANGRY     3
#define MOOD_SAD       4
#define MOOD_CHAOTIC   5
#define MOOD_HUNGRY    6
#define MOOD_TIRED     7
#define MOOD_SLAPHAPPY 8
#define MOOD_LAZY      9
#define MOOD_FAT       10
#define MOOD_CHILL     11
#define MOOD_CREEPY    12
#define MOOD_EXCITED   13
#define MOOD_NOSTALGIC 14
#define MOOD_HOMESICK  15
#define MOOD_COUNT     16

/* Mouth expressions
 *
 * Each mood has its own characteristic mouth shape.  Some moods share
 * expressions (e.g., many moods use EXPR_OPEN for the "talking" frame).
 * The expression IDs map to draw_mouth_*() functions in a switch below.
 */
#define EXPR_SMIRK     0
#define EXPR_OPEN      1
#define EXPR_SMILE     2
#define EXPR_WEIRD     3
#define EXPR_UNHINGED  4
#define EXPR_ANGRY     5
#define EXPR_SAD       6
#define EXPR_CHAOTIC   7
#define EXPR_HUNGRY    8
#define EXPR_TIRED     9
#define EXPR_SLAPHAPPY 10
#define EXPR_LAZY      11
#define EXPR_FAT       12
#define EXPR_CHILL     13
#define EXPR_CREEPY    14
#define EXPR_EXCITED   15
#define EXPR_NOSTALGIC 16
#define EXPR_HOMESICK  17

/*
 * mood_names[] — Human-readable labels for each mood, displayed in the
 * status bar at the bottom of the screen ("< ANGRY >").  The array
 * index matches the MOOD_* constants above.
 *
 * `static` means this array is only visible within this file (internal
 * linkage).  `const char *` means each element is a pointer to a
 * read-only string literal stored in flash/ROM.
 */
static const char *mood_names[MOOD_COUNT] = {
    "SASSY",    "WEIRD",    "UNHINGED",   "ANGRY",
    "SAD",      "CHAOTIC",  "HUNGRY",     "TIRED",
    "SLAPHAPPY","LAZY",     "FAT",        "CHILL",
    "CREEPY",   "EXCITED",  "NOSTALGIC",  "HOMESICK",
};

/* ── Framebuffer (landscape, same as Pico) ─────────────────────────────
 *
 *  The framebuffer is a flat byte array that holds the entire 250x122
 *  black-and-white image.  Each pixel is 1 bit:
 *    1 = black pixel,  0 = white pixel.
 *
 *  Memory layout:
 *    frame[0]                  = pixels (0,0) through (7,0)   — first 8 pixels of row 0
 *    frame[1]                  = pixels (8,0) through (15,0)  — next 8 pixels of row 0
 *    ...
 *    frame[IMG_ROW_BYTES - 1]  = last byte of row 0
 *    frame[IMG_ROW_BYTES]      = first byte of row 1
 *    ...and so on.
 *
 *  Within each byte, the MOST significant bit (bit 7, value 0x80)
 *  corresponds to the leftmost pixel.  This is called "MSB-first"
 *  or "big-endian" bit ordering.  See px_set() below for how we
 *  use this.
 *
 *  Total size: 32 * 122 = 3,904 bytes.  Tiny!
 * ──────────────────────────────────────────────────────────────────── */
static uint8_t frame[IMG_ROW_BYTES * IMG_H];

/*
 * Y_OFF — Vertical offset (in pixels) that pushes the octopus body
 * down from the top of the screen, leaving room for the clock header.
 */
#define Y_OFF 12

/* ── Body animation transform ──────────────────────────────────────────
 *
 *  These global variables control how the octopus body is positioned
 *  and distorted each frame.  They are set by setup_body_transform()
 *  and read by px_set_off() / px_clr_off() and draw_body_transformed().
 *
 *  body_dx, body_dy   — Horizontal/vertical translation (shift).
 *  body_x_expand      — How many extra pixels to grow (positive) or
 *                        shrink (negative) the body horizontally.
 *  wobble_amp/freq/phase — Parameters for a sine-wave horizontal
 *                          distortion applied per-row, giving the
 *                          body a wiggly, jelly-like wobble.
 * ──────────────────────────────────────────────────────────────────── */
static int body_dx = 0, body_dy = 0, body_x_expand = 0;
static float wobble_amp = 0, wobble_freq = 0, wobble_phase = 0;

/*
 * row_wobble() — Returns the horizontal pixel offset for a given row y.
 *
 * Uses the sine function to create a wave pattern: each row is shifted
 * left/right by a different amount, making the body look like it's
 * wiggling.  If wobble_amp is 0 (most moods), this returns 0 and the
 * body draws straight.
 *
 * Parameters:
 *   y — The row number being drawn.
 *
 * Returns:
 *   The number of pixels to shift this row horizontally.
 *
 * sinf() is the single-precision (float) version of sin().  The "f"
 * suffix matters on embedded — double-precision sin() is much slower
 * on chips without a hardware FPU for doubles.
 */
static int row_wobble(int y) {
    if (wobble_amp == 0) return 0;
    return (int)(wobble_amp * sinf(y * wobble_freq + wobble_phase));
}

/* ── Pixel helpers (identical to Pico) ─────────────────────────────────
 *
 *  These are the lowest-level drawing primitives.  Every shape in the
 *  octopus is built by calling px_set() or px_clr() for individual
 *  pixels.
 *
 *  `static inline` — The compiler will try to paste the function body
 *  directly at each call site instead of generating a real function
 *  call.  This avoids the overhead of pushing/popping the stack for
 *  something called millions of times per frame.
 * ──────────────────────────────────────────────────────────────────── */

/*
 * px_set() — Turn on (set to black) the pixel at (x, y).
 *
 * How the bit math works, step by step:
 *
 *   1. Bounds check: skip if (x,y) is outside the 250x122 canvas.
 *
 *   2. Find the byte:  frame[y * IMG_ROW_BYTES + x / 8]
 *      - y * IMG_ROW_BYTES jumps to the start of row y.
 *      - x / 8 picks which byte within that row (each byte = 8 pixels).
 *
 *   3. Find the bit within that byte:  0x80 >> (x & 7)
 *      - (x & 7) is equivalent to (x % 8) but faster.  It gives the
 *        bit position within the byte (0 = leftmost, 7 = rightmost).
 *      - 0x80 is binary 10000000.  Shifting it right by (x & 7)
 *        positions creates a mask with exactly one bit set:
 *          x & 7 == 0  =>  0x80  =>  10000000  (leftmost pixel)
 *          x & 7 == 1  =>  0x40  =>  01000000
 *          x & 7 == 3  =>  0x10  =>  00010000
 *          x & 7 == 7  =>  0x01  =>  00000001  (rightmost pixel)
 *
 *   4. |= (bitwise OR-assign) sets that one bit to 1 without
 *      disturbing the other 7 pixels in the same byte.
 */
static inline void px_set(int x, int y) {
    if (x >= 0 && x < IMG_W && y >= 0 && y < IMG_H)
        frame[y * IMG_ROW_BYTES + x / 8] |= (0x80 >> (x & 7));
}

/*
 * px_clr() — Turn off (set to white) the pixel at (x, y).
 *
 * Same byte/bit math as px_set(), but uses &= ~ (AND-NOT) instead of
 * |= (OR).  The ~ operator flips all bits of the mask:
 *   ~(0x80 >> 3) = ~(00010000) = 11101111
 * AND-ing with this clears just that one bit, leaving the rest intact.
 */
static inline void px_clr(int x, int y) {
    if (x >= 0 && x < IMG_W && y >= 0 && y < IMG_H)
        frame[y * IMG_ROW_BYTES + x / 8] &= ~(0x80 >> (x & 7));
}

/*
 * px_set_off() / px_clr_off() — "Offset" versions of px_set/px_clr.
 *
 * These apply the body animation transforms before drawing:
 *   - body_dx + row_wobble(y) shifts horizontally (translation + wobble)
 *   - Y_OFF + body_dy shifts vertically (constant header offset + animation)
 *
 * All octopus body parts (body, eyes, pupils, mouth, etc.) use these
 * offset versions so they move together as a unit when the body
 * animates.  The bubble and text use raw px_set() because they're
 * anchored to the screen, not the body.
 */
static inline void px_set_off(int x, int y) {
    px_set(x + body_dx + row_wobble(y), y + Y_OFF + body_dy);
}
static inline void px_clr_off(int x, int y) {
    px_clr(x + body_dx + row_wobble(y), y + Y_OFF + body_dy);
}

/* ── Quotes (auto-generated, 823 entries) ──────────────────────────────
 *
 *  quotes.h is auto-generated by a DevTool script.  It defines:
 *    - typedef struct { const char *text; uint8_t mood; } Quote;
 *    - static const Quote quotes[QUOTE_COUNT] = { ... };
 *    - #define QUOTE_COUNT 823
 *
 *  Each Quote has a text string and a mood ID (0-15) that determines
 *  which mood it belongs to.  The pick_quote_for_mood() function
 *  filters this array at runtime.
 * ──────────────────────────────────────────────────────────────────── */
#include "quotes.h"

/* ======================================================================
 *  OCTOPUS RENDERING ENGINE
 *  (Copied verbatim from Pico mood-selector — platform-independent)
 *
 *  Everything from here down to the "ESP32-SPECIFIC" section draws
 *  into the `frame[]` byte array using only px_set/px_clr.  No
 *  Arduino or ESP32 APIs are used, making this code portable to any
 *  platform that can provide a 250x122 monochrome framebuffer.
 * ====================================================================== */

/* ── Body RLE data ─────────────────────────────────────────────────────
 *
 *  RLE = Run-Length Encoding — a simple compression format.
 *
 *  The octopus body is a filled silhouette made of horizontal spans.
 *  Instead of storing every single pixel, we store just the start and
 *  end X coordinates of each filled run on each row.
 *
 *  Format of body_rle[]:
 *    For each row:
 *      byte 0: Y coordinate of this row
 *      byte 1: N = number of horizontal spans on this row
 *      Then N pairs of bytes:
 *        byte 2i+2: X-start of span i  (inclusive)
 *        byte 2i+3: X-end of span i    (inclusive)
 *
 *    The sentinel value 0xFF marks the end of the data.
 *
 *  Example: "10,1, 22,48" means:
 *    Row y=10 has 1 span, from x=22 to x=48 (a single horizontal line).
 *
 *  Example: "55,5, 10,17, 21,28, 32,39, 43,50, 54,61" means:
 *    Row y=55 has 5 spans (the tentacles splitting apart).
 *
 *  This RLE format is very compact: the entire body shape is ~340 bytes,
 *  vs ~2,500 bytes for a raw bitmap.  The decoder in
 *  draw_body_transformed() reads through this array sequentially.
 */
static const uint8_t body_rle[] = {
    10,1, 22,48,  11,1, 18,52,  12,1, 16,54,  13,1, 14,56,
    14,1, 13,57,  15,1, 12,58,  16,1, 11,59,  17,1, 10,60,
    18,1, 10,60,  19,1,  9,61,  20,1,  9,61,  21,1,  9,61,
    22,1,  9,61,  23,1,  9,61,  24,1,  9,61,  25,1,  9,61,
    26,1,  9,61,  27,1,  9,61,  28,1, 10,60,  29,1, 10,60,
    30,1, 10,60,  31,1, 10,60,  32,1, 10,60,  33,1, 10,60,
    34,1, 10,60,  35,1, 10,60,  36,1, 10,60,  37,1, 10,60,
    38,1, 10,60,  39,1, 10,60,  40,1, 10,60,  41,1, 11,59,
    42,1, 11,59,  43,1, 12,58,  44,1, 13,57,  45,1, 14,56,
    46,1, 12,58,  47,1, 11,59,  48,1, 10,60,  49,1, 10,60,
    50,1, 11,59,  51,1, 12,58,  52,1, 13,57,  53,1, 14,56,
    54,1, 15,55,
    55,5, 10,17, 21,28, 32,39, 43,50, 54,61,
    56,5,  8,15, 19,26, 30,37, 45,52, 56,63,
    57,5,  7,14, 18,24, 29,35, 47,53, 58,64,
    58,5,  6,12, 19,25, 31,37, 46,52, 57,63,
    59,5,  7,13, 21,27, 33,39, 44,50, 55,61,
    60,5,  8,14, 20,26, 31,37, 43,49, 54,60,
    61,5,  9,14, 18,24, 30,36, 44,50, 56,62,
    62,5,  8,13, 17,22, 31,37, 46,52, 57,63,
    63,5,  7,12, 18,23, 33,38, 45,51, 55,61,
    64,5,  8,13, 20,25, 32,37, 43,48, 54,59,
    65,5,  9,14, 19,24, 30,35, 44,49, 55,60,
    66,5, 10,14, 17,22, 31,36, 46,51, 57,62,
    67,5,  9,13, 18,22, 33,37, 45,50, 56,61,
    68,5,  8,12, 19,23, 32,36, 43,48, 54,59,
    69,5,  9,13, 21,25, 30,34, 44,48, 55,59,
    70,5, 10,14, 20,24, 31,35, 46,50, 57,61,
    71,5, 11,14, 18,22, 33,37, 45,49, 56,60,
    72,5, 10,13, 19,22, 32,35, 43,47, 54,58,
    73,5,  9,12, 20,23, 30,33, 44,47, 55,58,
    74,5, 10,13, 21,24, 31,34, 46,49, 57,60,
    75,5, 11,14, 20,23, 33,36, 45,48, 56,59,
    76,5, 12,14, 19,22, 32,35, 43,46, 54,57,
    77,5, 11,13, 20,22, 30,33, 44,46, 55,57,
    78,5, 10,12, 21,23, 31,33, 45,47, 56,58,
    79,5, 11,13, 22,24, 32,34, 44,46, 55,57,
    80,5, 12,14, 21,23, 33,35, 43,45, 54,56,
    0xFF
};

/* ── 5x7 bitmap font ───────────────────────────────────────────────────
 *
 *  A tiny hand-encoded monochrome bitmap font.  Each character is
 *  5 pixels wide and 7 pixels tall.
 *
 *  ENCODING:
 *  Each character is an array of 7 bytes (one byte per row, top to
 *  bottom).  Within each byte, bits 4..0 (the low 5 bits) represent
 *  the 5 pixel columns, with bit 4 = leftmost column and bit 0 =
 *  rightmost column.
 *
 *  Example: The letter 'A' = {0x0e, 0x11, 0x11, 0x1f, 0x11, 0x11, 0x11}
 *
 *    Row 0: 0x0e = 01110  =>  .XXX.     (top of the A)
 *    Row 1: 0x11 = 10001  =>  X...X     (sides)
 *    Row 2: 0x11 = 10001  =>  X...X
 *    Row 3: 0x1f = 11111  =>  XXXXX     (crossbar)
 *    Row 4: 0x11 = 10001  =>  X...X
 *    Row 5: 0x11 = 10001  =>  X...X
 *    Row 6: 0x11 = 10001  =>  X...X     (bottom)
 *
 *  The draw_char() function reads these bytes and tests each bit with
 *  a mask (0x10 >> col) to decide whether to draw a pixel.
 *
 *  The font_chars[] string maps array indices to characters:
 *    Index 0 = 'A', 1 = 'B', ..., 25 = 'Z',
 *    26 = '0', ..., 35 = '9',
 *    36 = ' ' (space, also the fallback for unknown characters),
 *    37+ = punctuation
 * ──────────────────────────────────────────────────────────────────── */
static const uint8_t font5x7[][7] = {
    {0x0e,0x11,0x11,0x1f,0x11,0x11,0x11}, {0x1e,0x11,0x11,0x1e,0x11,0x11,0x1e},
    {0x0e,0x11,0x10,0x10,0x10,0x11,0x0e}, {0x1e,0x11,0x11,0x11,0x11,0x11,0x1e},
    {0x1f,0x10,0x10,0x1e,0x10,0x10,0x1f}, {0x1f,0x10,0x10,0x1e,0x10,0x10,0x10},
    {0x0e,0x11,0x10,0x17,0x11,0x11,0x0e}, {0x11,0x11,0x11,0x1f,0x11,0x11,0x11},
    {0x1f,0x04,0x04,0x04,0x04,0x04,0x1f}, {0x07,0x02,0x02,0x02,0x02,0x12,0x0c},
    {0x11,0x12,0x14,0x18,0x14,0x12,0x11}, {0x10,0x10,0x10,0x10,0x10,0x10,0x1f},
    {0x11,0x1b,0x15,0x15,0x11,0x11,0x11}, {0x11,0x11,0x19,0x15,0x13,0x11,0x11},
    {0x0e,0x11,0x11,0x11,0x11,0x11,0x0e}, {0x1e,0x11,0x11,0x1e,0x10,0x10,0x10},
    {0x0e,0x11,0x11,0x11,0x15,0x12,0x0d}, {0x1e,0x11,0x11,0x1e,0x14,0x12,0x11},
    {0x0e,0x11,0x10,0x0e,0x01,0x11,0x0e}, {0x1f,0x04,0x04,0x04,0x04,0x04,0x04},
    {0x11,0x11,0x11,0x11,0x11,0x11,0x0e}, {0x11,0x11,0x11,0x11,0x0a,0x0a,0x04},
    {0x11,0x11,0x11,0x15,0x15,0x15,0x0a}, {0x11,0x11,0x0a,0x04,0x0a,0x11,0x11},
    {0x11,0x11,0x0a,0x04,0x04,0x04,0x04}, {0x1f,0x01,0x02,0x04,0x08,0x10,0x1f},
    {0x0e,0x11,0x13,0x15,0x19,0x11,0x0e}, {0x04,0x0c,0x04,0x04,0x04,0x04,0x0e},
    {0x0e,0x11,0x01,0x06,0x08,0x10,0x1f}, {0x0e,0x11,0x01,0x06,0x01,0x11,0x0e},
    {0x02,0x06,0x0a,0x12,0x1f,0x02,0x02}, {0x1f,0x10,0x1e,0x01,0x01,0x11,0x0e},
    {0x0e,0x11,0x10,0x1e,0x11,0x11,0x0e}, {0x1f,0x01,0x02,0x04,0x08,0x08,0x08},
    {0x0e,0x11,0x11,0x0e,0x11,0x11,0x0e}, {0x0e,0x11,0x11,0x0f,0x01,0x11,0x0e},
    {0x00,0x00,0x00,0x00,0x00,0x00,0x00}, {0x00,0x00,0x00,0x00,0x00,0x0c,0x0c},
    {0x00,0x00,0x00,0x00,0x04,0x04,0x08}, {0x04,0x04,0x04,0x04,0x04,0x00,0x04},
    {0x0e,0x11,0x01,0x06,0x04,0x00,0x04}, {0x04,0x04,0x08,0x00,0x00,0x00,0x00},
    {0x00,0x00,0x00,0x1f,0x00,0x00,0x00}, {0x00,0x00,0x08,0x15,0x02,0x00,0x00},
    {0x01,0x02,0x02,0x04,0x08,0x08,0x10}, {0x00,0x0c,0x0c,0x00,0x0c,0x0c,0x00},
    {0x02,0x04,0x08,0x08,0x08,0x04,0x02}, {0x08,0x04,0x02,0x02,0x02,0x04,0x08},
    {0x19,0x1a,0x02,0x04,0x08,0x0b,0x13}, {0x01,0x02,0x04,0x08,0x04,0x02,0x01},
    {0x10,0x08,0x04,0x02,0x04,0x08,0x10},
};

/*
 * font_chars[] — The character set supported by our bitmap font.
 * The position of each character in this string is its index into
 * the font5x7[][] array above.  For example, 'A' is at index 0,
 * 'B' at index 1, '0' at index 26, ' ' at index 36, etc.
 */
static const char font_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-~/:()\%<>";

/*
 * font_index() — Look up a character's index in the font table.
 *
 * Scans font_chars[] linearly until it finds a match.  For a 50-char
 * alphabet this is fast enough (no need for a hash table).
 *
 * Parameters:
 *   c — The character to look up (should be uppercase or punctuation).
 *
 * Returns:
 *   The index into font5x7[][] for that character, or 36 (the space
 *   glyph) if the character isn't found.  This is a safe fallback —
 *   unknown characters render as blank space instead of crashing.
 */
static int font_index(char c) {
    for (int i = 0; font_chars[i]; i++)
        if (font_chars[i] == c) return i;
    return 36;
}

/* ── Drawing primitives ────────────────────────────────────────────────
 *
 *  These are mid-level shape routines used to build up the octopus
 *  features (eyes, pupils, etc.).
 * ──────────────────────────────────────────────────────────────────── */

/*
 * fill_circle() — Draw or erase a filled circle at a given center.
 *
 * Uses the "distance squared" test to avoid calling sqrt():
 *   A point (cx+dx, cy+dy) is inside a circle of radius r when:
 *     dx*dx + dy*dy <= r*r
 *   We pass r_sq (r-squared) directly, so we never need sqrt().
 *
 * Parameters:
 *   cx, cy — Center of the circle in body-relative coordinates.
 *   r_sq   — Radius squared.  E.g., pass 16 for a radius-4 circle.
 *   set    — 1 to draw black pixels, 0 to erase (draw white pixels).
 *
 * Note: The loop radius `r = 5` is hardcoded as a generous scan range.
 * Only points passing the r_sq distance test actually get drawn, so
 * increasing this value just means checking a few extra points.
 */
static void fill_circle(int cx, int cy, int r_sq, int set) {
    int r = 5;
    for (int dy = -r; dy <= r; dy++)
        for (int dx = -r; dx <= r; dx++)
            if (dx * dx + dy * dy <= r_sq) {
                if (set) px_set_off(cx + dx, cy + dy);
                else     px_clr_off(cx + dx, cy + dy);
            }
}

/*
 * draw_body_transformed() — Decode the body RLE data and draw the
 * filled octopus body silhouette, applying the current animation
 * transforms (body_dx, body_dy, body_x_expand, wobble).
 *
 * Walks through body_rle[] byte by byte:
 *   1. Read the Y coordinate and span count.
 *   2. For each span, read X-start and X-end.
 *   3. Expand or shrink the span by body_x_expand pixels.
 *   4. Clamp to screen bounds.
 *   5. Draw every pixel in the span using px_set_off().
 *
 * The pointer `p` advances through the array as it reads successive
 * bytes.  The `*p++` idiom means "read the byte that p points to,
 * then advance p to the next byte."
 */
static void draw_body_transformed(void) {
    const uint8_t *p = body_rle;       /* Pointer walks through the RLE data */
    while (*p != 0xFF) {               /* 0xFF = end-of-data sentinel */
        int y = *p++;                  /* Read Y coordinate, advance pointer */
        int n = *p++;                  /* Read number of spans on this row */
        for (int i = 0; i < n; i++) {
            int x0 = *p++;            /* Read span start X */
            int x1 = *p++;            /* Read span end X */
            int ax0 = x0 - body_x_expand;   /* Grow/shrink left edge */
            int ax1 = x1 + body_x_expand;   /* Grow/shrink right edge */
            if (ax0 < 0) ax0 = 0;           /* Clamp to left screen edge */
            if (ax1 >= IMG_W) ax1 = IMG_W - 1;  /* Clamp to right edge */
            for (int x = ax0; x <= ax1; x++)
                px_set_off(x, y);      /* Fill the span with black pixels */
        }
    }
}

/*
 * draw_eyes() — Carve the eye sockets into the body by erasing
 * (clearing to white) two small filled circles.  The body is drawn
 * first as a solid black shape, then the eyes are "punched out" of
 * it.  Left eye at (22,25), right eye at (48,25), radius-squared=16
 * (i.e., radius 4).  The `0` argument to fill_circle means "erase."
 */
static void draw_eyes(void) { fill_circle(22, 25, 16, 0); fill_circle(48, 25, 16, 0); }

/* ── Pupil variations (identical to Pico) ──────────────────────────────
 *
 *  Each mood has a unique pupil style drawn inside the white eye sockets.
 *  Pupils are drawn black (set=1).  Some also add a tiny white highlight
 *  dot (the "glint" or "catchlight") by clearing a pixel afterward.
 *
 *  Coordinates are relative to the eye centers (22,25) and (48,25),
 *  with small offsets for artistic effect.
 * ──────────────────────────────────────────────────────────────────── */

/* Normal pupils: solid dots with highlight glint at upper-left */
static void draw_pupils_normal(void) { fill_circle(23,26,4,1); fill_circle(49,26,4,1); fill_circle(20,23,1,0); fill_circle(46,23,1,0); }

/* Weird: pupils at different positions (left looks up-left, right looks down-right) */
static void draw_pupils_weird(void) { fill_circle(21,24,4,1); fill_circle(50,28,4,1); fill_circle(20,23,1,0); fill_circle(46,23,1,0); }

/* Unhinged: tiny 2x2 pixel pupils (unsettlingly small) */
static void draw_pupils_unhinged(void) { px_set_off(22,25); px_set_off(23,25); px_set_off(22,26); px_set_off(23,26); px_set_off(48,25); px_set_off(49,25); px_set_off(48,26); px_set_off(49,26); }

/* Angry: pupils shifted down and inward (glaring), with highlight */
static void draw_pupils_angry(void) { fill_circle(25,27,4,1); fill_circle(47,27,4,1); fill_circle(23,24,1,0); fill_circle(45,24,1,0); }

/*
 * draw_brows_angry() — Draw angry V-shaped eyebrows above the eyes.
 *
 * Uses parametric lines (t goes from 0.0 to 1.0 in 18 steps) with
 * a sine-wave arc subtracted to give them a menacing, downward-slanting
 * curve.  Left brow slopes down-right; right brow slopes down-left.
 *
 * Each brow is 3 pixels thick (the `for (int dy = 0; dy < 3; dy++)`
 * loop) plus an extra pixel offset for anti-alias-like thickening.
 *
 * The float `t` normalizes the loop variable i to the 0..1 range,
 * which is a common trick for parametric drawing (it makes the math
 * independent of the number of steps).
 *
 * 3.14159f is pi — one full half-period of sin(), creating a single
 * arch shape across the brow.
 */
static void draw_brows_angry(void) {
    for (int i = 0; i < 18; i++) { float t = i / 17.0f; int x = 14 + (int)(t * 16); float arc = 2.5f * sinf(t * 3.14159f); int y = (int)(20 + t * 5 - arc); for (int dy = 0; dy < 3; dy++) px_set_off(x, y + dy); px_set_off(x + 1, y + 1); }
    for (int i = 0; i < 18; i++) { float t = i / 17.0f; int x = 40 + (int)(t * 16); float arc = 2.5f * sinf(t * 3.14159f); int y = (int)(25 - t * 5 - arc); for (int dy = 0; dy < 3; dy++) px_set_off(x, y + dy); px_set_off(x + 1, y + 1); }
}

/* Sad: pupils shifted downward (looking down dejectedly) */
static void draw_pupils_sad(void) { fill_circle(23,28,4,1); fill_circle(49,28,4,1); fill_circle(21,25,1,0); fill_circle(47,25,1,0); }

/*
 * draw_brows_sad() — Draw sad, drooping eyebrows.
 * Same parametric approach as angry brows, but the slopes are reversed:
 * left brow slopes up-right (droops at the inner edge), right brow
 * slopes up-left.  This creates the classic "worried" or "sad" look.
 */
static void draw_brows_sad(void) {
    for (int i = 0; i < 18; i++) { float t = i / 17.0f; int x = 14 + (int)(t * 16); float arc = 2.5f * sinf(t * 3.14159f); int y = (int)(25 - t * 5 - arc); for (int dy = 0; dy < 3; dy++) px_set_off(x, y + dy); }
    for (int i = 0; i < 18; i++) { float t = i / 17.0f; int x = 40 + (int)(t * 16); float arc = 2.5f * sinf(t * 3.14159f); int y = (int)(20 + t * 5 - arc); for (int dy = 0; dy < 3; dy++) px_set_off(x, y + dy); }
}

/*
 * draw_pupils_chaotic() — Draw ring-shaped pupils (hollow circles).
 *
 * For each eye, scans a 7x7 grid around the center.  Pixels whose
 * distance-squared falls between 5 and 9 (inclusive) form a ring
 * (annulus).  A single center dot is also set.  This creates an
 * unsettling "spiraling" or "hypnotic" look.
 *
 * The ternary operator `(ecx_i == 0) ? 22 : 48` picks the left or
 * right eye center X coordinate.  Ternary syntax:
 *   condition ? value_if_true : value_if_false
 */
static void draw_pupils_chaotic(void) {
    for (int ecx_i = 0; ecx_i < 2; ecx_i++) { int ecx = (ecx_i == 0) ? 22 : 48; for (int dy = -3; dy <= 3; dy++) for (int dx = -3; dx <= 3; dx++) { int dist = dx*dx + dy*dy; if (dist >= 5 && dist <= 9) px_set_off(ecx+dx, 25+dy); } px_set_off(ecx, 25); }
}

/* Hungry: pupils shifted upward (looking up longingly at food) */
static void draw_pupils_hungry(void) { fill_circle(23,23,4,1); fill_circle(49,23,4,1); fill_circle(21,21,1,0); fill_circle(47,21,1,0); }

/* Tired: tiny 3x2-pixel pupils (barely open, heavy-lidded look) */
static void draw_pupils_tired(void) { for (int dx = -1; dx <= 1; dx++) { px_set_off(22+dx,27); px_set_off(22+dx,28); px_set_off(48+dx,27); px_set_off(48+dx,28); } }

/*
 * draw_lids_tired() — Draw heavy eyelids covering the top of each eye.
 *
 * Fills the upper portion (dy from -4 to -1) of each eye socket with
 * black pixels, simulating drooping eyelids.  The distance-squared
 * check (dx*dx + dy*dy <= 16) constrains the fill to the circular
 * eye boundary so the lids don't spill outside the eye socket shape.
 */
static void draw_lids_tired(void) {
    for (int ecx_i = 0; ecx_i < 2; ecx_i++) { int ecx = (ecx_i == 0) ? 22 : 48; for (int dy = -4; dy < -1; dy++) for (int dx = -4; dx <= 4; dx++) if (dx*dx+dy*dy <= 16) px_set_off(ecx+dx, 25+dy); }
}

/*
 * draw_eyes_slaphappy() — Special eye override: left eye is a horizontal
 * line (winking/squinting), right eye has a large filled pupil.
 *
 * Left eye: fills the entire eye socket black, then clears a horizontal
 * line through the center (y=25), creating a "squint" or "wink" effect.
 *
 * Right eye: draws a medium filled circle (radius-squared=9, radius~3).
 */
static void draw_eyes_slaphappy(void) {
    for (int dy = -4; dy <= 4; dy++) for (int dx = -4; dx <= 4; dx++) if (dx*dx+dy*dy <= 16) px_set_off(22+dx, 25+dy);
    for (int dx = -3; dx <= 3; dx++) px_clr_off(22+dx, 25);
    fill_circle(49, 26, 9, 1);
}

/* Lazy: eyelids cover most of each eye (nearly closed), only bottom visible */
static void draw_lids_lazy(void) { for (int e = 0; e < 2; e++) { int ecx = e ? 48 : 22; for (int dy = -4; dy < 2; dy++) for (int dx = -4; dx <= 4; dx++) if (dx*dx+dy*dy <= 16) px_set_off(ecx+dx, 25+dy); } }

/* Lazy pupils: tiny 2-pixel dots barely visible under the heavy lids */
static void draw_pupils_lazy(void) { for (int e = 0; e < 2; e++) { int ecx = e ? 48 : 22; px_set_off(ecx,28); px_set_off(ecx+1,28); } }

/* Fat: medium filled circle pupils, slightly offset down-right */
static void draw_pupils_fat(void) { for (int e = 0; e < 2; e++) { int ecx = e ? 49 : 23; for (int dy = -3; dy <= 3; dy++) for (int dx = -3; dx <= 3; dx++) if (dx*dx+dy*dy <= 9) px_set_off(ecx+dx, 26+dy); } }

/* Chill: small pupils shifted to the right side of each eye (relaxed side-gaze) */
static void draw_pupils_chill(void) { int c[][2] = {{25,26},{51,26}}; for (int e = 0; e < 2; e++) for (int dy = -2; dy <= 2; dy++) for (int dx = -2; dx <= 2; dx++) if (dx*dx+dy*dy <= 4) px_set_off(c[e][0]+dx, c[e][1]+dy); }

/*
 * draw_pupils_creepy() — Draw diamond/star-shaped pupils.
 *
 * Uses a hardcoded coordinate table (top[][]) for the upper points,
 * then adds a horizontal line and tapered lower portion.  The result
 * looks like a vertically elongated diamond — unsettling and alien.
 *
 * `static const int8_t top[][2]` — A small lookup table of (dx, dy)
 * offsets.  `static` inside a function means the array is allocated
 * once (not on the stack each call) and persists for the program's
 * lifetime.  `const` means the values are read-only.  `int8_t` is
 * a signed 8-bit integer (range -128 to 127), saving RAM vs `int`.
 */
static void draw_pupils_creepy(void) {
    for (int e = 0; e < 2; e++) { int ecx = e ? 48 : 22; static const int8_t top[][2] = {{-2,-1},{-1,-2},{0,-1},{1,-2},{2,-1}}; for (int i = 0; i < 5; i++) px_set_off(ecx+top[i][0], 25+top[i][1]); for (int dx = -2; dx <= 2; dx++) px_set_off(ecx+dx, 25); for (int dx = -1; dx <= 1; dx++) px_set_off(ecx+dx, 26); px_set_off(ecx, 27); }
}

/* Excited: cross/plus-shaped pupils (like sparkle eyes) */
static void draw_pupils_excited(void) { for (int e = 0; e < 2; e++) { int ecx = e ? 48 : 22; for (int d = -2; d <= 2; d++) { px_set_off(ecx+d,25); px_set_off(ecx,25+d); } px_set_off(ecx-1,24); px_set_off(ecx+1,24); px_set_off(ecx-1,26); px_set_off(ecx+1,26); } }

/* Nostalgic: pupils gazing upward and slightly right (wistful look) */
static void draw_pupils_nostalgic(void) { int c[][2] = {{24,23},{50,23}}; for (int e = 0; e < 2; e++) for (int dy = -2; dy <= 2; dy++) for (int dx = -2; dx <= 2; dx++) if (dx*dx+dy*dy <= 4) px_set_off(c[e][0]+dx, c[e][1]+dy); }

/* Homesick: pupils shifted downward (eyes cast down sadly) */
static void draw_pupils_homesick(void) { for (int e = 0; e < 2; e++) { int ecx = e ? 49 : 23; for (int dy = -2; dy <= 2; dy++) for (int dx = -2; dx <= 2; dx++) if (dx*dx+dy*dy <= 4) px_set_off(ecx+dx, 27+dy); } }

/*
 * draw_tears_homesick() — Draw small teardrop shapes below each eye.
 * Three vertical pixels plus two horizontal neighbors form a cross-
 * shaped tear at (ecx, 31..33).
 */
static void draw_tears_homesick(void) { for (int e = 0; e < 2; e++) { int ecx = e ? 48 : 22; px_set_off(ecx,31); px_set_off(ecx,32); px_set_off(ecx,33); px_set_off(ecx-1,32); px_set_off(ecx+1,32); } }

/* ── Mouth expressions (identical to Pico) ─────────────────────────────
 *
 *  Each draw_mouth_*() function renders a different mouth shape.
 *  They all draw in the region roughly (x: 22-49, y: 37-48) which
 *  is the lower face area of the octopus body.
 *
 *  The mouths use a mix of techniques:
 *    - Parametric curves (sinf, quadratic) for wavy/curved mouths
 *    - Ellipse fill + edge detection for open/round mouths
 *    - Simple horizontal lines for flat mouths
 *
 *  Most curved mouths draw 2 pixels vertically per X position to
 *  create a thicker, more visible line on the low-res display.
 * ──────────────────────────────────────────────────────────────────── */

/*
 * draw_mouth_smirk() — Default asymmetric smile (tilted upward on right).
 *
 * For each X from 28 to 43, computes a Y position using:
 *   tilt  = linear ramp from -2 to +2 (tilts the line)
 *   arc   = sqrt(1 - v^2) parabolic arch (curves it upward)
 *   yc    = 39 + tilt + arc
 *
 * Then clears the center pixel (white gap = the "mouth opening")
 * and sets pixels above and below it (the lips).
 *
 * fabsf() = absolute value of a float.  The f suffix is important —
 * plain fabs() takes a double and would be slower on ESP32.
 */
static void draw_mouth_smirk(void) { for (int x = 28; x < 44; x++) { float t = (x-28)/15.0f; float tilt = -2.0f+t*4.0f; float v = 2.0f*t-1.0f; float arc = (fabsf(v)<1.0f) ? 5.0f*sqrtf(1.0f-v*v) : 0.0f; int yc = (int)(39.0f+tilt+arc); px_clr_off(x,yc); px_set_off(x,yc-1); px_set_off(x,yc+1); } }

/* Smile: simple upward-curving parabola */
static void draw_mouth_smile(void) { for (int x = 26; x < 45; x++) { int cy = 38+((x-35)*(x-35))/25; px_set_off(x,cy); px_set_off(x,cy+1); } }

/*
 * draw_mouth_open() — Round open mouth (surprised/talking).
 *
 * Two-step process:
 *   1. Fill the interior of an ellipse with WHITE pixels (px_clr_off)
 *      to create the mouth opening.
 *   2. Draw only the BORDER pixels in BLACK by checking if any
 *      neighbor is outside the ellipse (edge detection).
 *
 * The edge detection loop checks 4 neighbors (left, right, up, down).
 * If the current pixel is inside the ellipse AND at least one neighbor
 * is outside, then this pixel is on the border — draw it black.
 *
 * The ellipse equation:  (dx^2 * ry^2) + (dy^2 * rx^2) <= (rx^2 * ry^2)
 * This is the standard ellipse equation rearranged to avoid division.
 *
 * `nd` iterates over the 4 cardinal directions.  The ternary chains
 * pick dx/dy offsets: nd=0 -> left(-1,0), nd=1 -> right(+1,0),
 * nd=2 -> up(0,-1), nd=3 -> down(0,+1).
 */
static void draw_mouth_open(void) {
    int cx=35, cy=40, rx=7, ry=5;
    for (int dy=-4; dy<=4; dy++) for (int dx=-6; dx<=6; dx++) if (dx*dx*16+dy*dy*36<=36*16) px_clr_off(cx+dx,cy+dy);
    for (int dy=-ry; dy<=ry; dy++) for (int dx=-rx; dx<=rx; dx++) { if (dx*dx*ry*ry+dy*dy*rx*rx>rx*rx*ry*ry) continue; for (int nd=0;nd<4;nd++) { int nx=dx+((nd==0)?-1:(nd==1)?1:0); int ny=dy+((nd==2)?-1:(nd==3)?1:0); if (nx*nx*ry*ry+ny*ny*rx*rx>rx*rx*ry*ry) { px_set_off(cx+dx,cy+dy); break; } } }
}

/* Weird mouth: triple sine wave (wobbly, off-kilter) */
static void draw_mouth_weird(void) { for (int x=24;x<48;x++) { float t=(x-24)/23.0f; int yc=39+(int)(3.5f*sinf(t*3.14159f*3.0f)); px_clr_off(x,yc); px_set_off(x,yc-1); px_set_off(x,yc+1); } }

/*
 * draw_mouth_unhinged() — Huge gaping oval mouth with jagged "teeth."
 *
 * Similar to draw_mouth_open() but larger (rx=10, ry=7), and adds
 * small black squares at regular intervals along the top edge of the
 * mouth to suggest teeth.  The teeth loop `for (int x=cx-7;x<=cx+7;x+=3)`
 * places them every 3 pixels.
 */
static void draw_mouth_unhinged(void) {
    int cx=35,cy=41,rx=10,ry=7;
    for (int dy=-6;dy<=6;dy++) for (int dx=-9;dx<=9;dx++) if (dx*dx*36+dy*dy*81<=81*36) px_clr_off(cx+dx,cy+dy);
    for (int dy=-ry;dy<=ry;dy++) for (int dx=-rx;dx<=rx;dx++) { if (dx*dx*ry*ry+dy*dy*rx*rx>rx*rx*ry*ry) continue; for (int nd=0;nd<4;nd++) { int nx=dx+((nd==0)?-1:(nd==1)?1:0); int ny=dy+((nd==2)?-1:(nd==3)?1:0); if (nx*nx*ry*ry+ny*ny*rx*rx>rx*rx*ry*ry) { px_set_off(cx+dx,cy+dy); break; } } }
    for (int x=cx-7;x<=cx+7;x+=3) { px_set_off(x,cy-5); px_set_off(x,cy-4); px_set_off(x+1,cy-4); }
}

/* Angry: frown (downward-curving parabola, opposite of smile) */
static void draw_mouth_angry(void) { for (int x=28;x<43;x++) { int cy=40-((x-35)*(x-35))/20; px_set_off(x,cy); px_set_off(x,cy+1); } }

/* Sad: wider, gentler frown (shallower curve, more pixels) */
static void draw_mouth_sad(void) { for (int x=26;x<45;x++) { int cy=42-((x-35)*(x-35))/30; px_set_off(x,cy); px_set_off(x,cy+1); } }

/* Chaotic: zigzag sawtooth pattern (frantic, unstable) */
static void draw_mouth_chaotic(void) { for (int x=24;x<48;x++) { int phase=(x-24)%6; int y=(phase<3)?38+phase*2:44-phase*2+6; px_set_off(x,y); px_set_off(x,y+1); } }

/*
 * draw_mouth_hungry() — Open oval mouth with drool lines below it.
 *
 * Same filled-ellipse-with-border technique as draw_mouth_open().
 * The two extra lines at the bottom draw drool: vertical lines of
 * pixels extending downward from the chin at x=33 and x=37.
 */
static void draw_mouth_hungry(void) {
    int cx=35,cy=40,rx=8,ry=5;
    for (int dy=-(ry-1);dy<=ry-1;dy++) for (int dx=-(rx-1);dx<=rx-1;dx++) if (dx*dx*(ry-1)*(ry-1)+dy*dy*(rx-1)*(rx-1)<=(rx-1)*(rx-1)*(ry-1)*(ry-1)) px_clr_off(cx+dx,cy+dy);
    for (int dy=-ry;dy<=ry;dy++) for (int dx=-rx;dx<=rx;dx++) { if (dx*dx*ry*ry+dy*dy*rx*rx>rx*rx*ry*ry) continue; for (int nd=0;nd<4;nd++) { int nx=dx+((nd==0)?-1:(nd==1)?1:0); int ny=dy+((nd==2)?-1:(nd==3)?1:0); if (nx*nx*ry*ry+ny*ny*rx*rx>rx*rx*ry*ry) { px_set_off(cx+dx,cy+dy); break; } } }
    for (int dy=1;dy<6;dy++) px_set_off(33,cy+ry+dy); for (int dy=1;dy<4;dy++) px_set_off(37,cy+ry+dy+1);
}

/*
 * draw_mouth_tired() — Tall, narrow open yawn (vertically oriented
 * ellipse with rx=5, ry=7 — taller than wide).
 */
static void draw_mouth_tired(void) {
    int cx=35,cy=40,rx=5,ry=7;
    for (int dy=-(ry-1);dy<=ry-1;dy++) for (int dx=-(rx-1);dx<=rx-1;dx++) if (dx*dx*(ry-1)*(ry-1)+dy*dy*(rx-1)*(rx-1)<=(rx-1)*(rx-1)*(ry-1)*(ry-1)) px_clr_off(cx+dx,cy+dy);
    for (int dy=-ry;dy<=ry;dy++) for (int dx=-rx;dx<=rx;dx++) { if (dx*dx*ry*ry+dy*dy*rx*rx>rx*rx*ry*ry) continue; for (int nd=0;nd<4;nd++) { int nx=dx+((nd==0)?-1:(nd==1)?1:0); int ny=dy+((nd==2)?-1:(nd==3)?1:0); if (nx*nx*ry*ry+ny*ny*rx*rx>rx*rx*ry*ry) { px_set_off(cx+dx,cy+dy); break; } } }
}

/* Slaphappy: wide wobbly grin with sinusoidal ripple overlaid on a parabola */
static void draw_mouth_slaphappy(void) { for (int x=22;x<49;x++) { float t=(x-22)/26.0f; int base=38+((x-35)*(x-35))/20; int w=(int)(1.5f*sinf(t*3.14159f*4.0f)); px_set_off(x,base+w); px_set_off(x,base+w+1); } }

/* Lazy: simple flat horizontal line (minimal effort, even for the mouth) */
static void draw_mouth_lazy(void) { for (int x=29;x<42;x++) { px_set_off(x,40); px_set_off(x,41); } }

/*
 * draw_mouth_fat() — Extra-wide smile with rosy cheek circles.
 *
 * The parabola spans x=24 to x=46 (wider than normal smile).
 * The ch[][] array holds the two cheek positions; each cheek is a
 * small filled circle (radius-squared=4, about 2px radius).
 */
static void draw_mouth_fat(void) { for (int x=24;x<47;x++) { int cy=38+((x-35)*(x-35))/18; px_set_off(x,cy); px_set_off(x,cy+1); } int ch[][2]={{23,39},{47,39}}; for (int c=0;c<2;c++) for (int dy=-2;dy<=2;dy++) for (int dx=-2;dx<=2;dx++) if (dx*dx+dy*dy<=4) px_set_off(ch[c][0]+dx,ch[c][1]+dy); }

/* Chill: small, relaxed half-smile (short gentle upward curve) */
static void draw_mouth_chill(void) { for (int x=29;x<44;x++) { float t=(x-29)/14.0f; int y=40+(int)(1.5f*t*t); px_set_off(x,y); px_set_off(x,y+1); } }

/*
 * draw_mouth_creepy() — Half-ellipse (lower half only) open mouth
 * with a protruding "tongue" blob below it.
 *
 * The `dy==0` check draws the flat top edge of the half-ellipse.
 * For dy > 0, the standard 4-neighbor edge detection draws the
 * curved bottom portion.  Interior pixels are cleared (white mouth
 * opening).  The "tongue" is a small filled shape extending below.
 */
static void draw_mouth_creepy(void) {
    int cx=35,cy=39,rx=8,ry=5;
    for (int dy=0;dy<=ry;dy++) for (int dx=-rx;dx<=rx;dx++) { int in=(dx*dx)*(ry*ry)+(dy*dy)*(rx*rx)<=(rx*rx)*(ry*ry); if (!in) continue; int edge=0; if (dy==0) edge=1; else { int ndxs[]={-1,1,0,0},ndys[]={0,0,-1,1}; for (int n=0;n<4;n++) { int nx=dx+ndxs[n],ny=dy+ndys[n]; if (ny<0) continue; if ((nx*nx)*(ry*ry)+(ny*ny)*(rx*rx)>(rx*rx)*(ry*ry)) {edge=1;break;} } } if (edge) px_set_off(cx+dx,cy+dy); else px_clr_off(cx+dx,cy+dy); }
    for (int dy=1;dy<5;dy++) for (int dx=-2;dx<=2;dx++) if (dx*dx+dy*dy<=8) px_set_off(cx+dx,cy+ry+dy);
    for (int dy=2;dy<4;dy++) for (int dx=-1;dx<=1;dx++) px_clr_off(cx+dx,cy+ry+dy);
}

/* Excited: very wide, deep smile (steep parabola with shallow divisor=12) */
static void draw_mouth_excited(void) { for (int x=22;x<49;x++) { int cy=37+((x-35)*(x-35))/12; px_set_off(x,cy); px_set_off(x,cy+1); } }

/* Nostalgic: small, wistful smile (narrow parabola, gentle curve) */
static void draw_mouth_nostalgic(void) { for (int x=31;x<40;x++) { float t=(x-31)/8.0f; float v=2.0f*t-1.0f; int y=40+(int)(1.5f*v*v); px_set_off(x,y); px_set_off(x,y+1); } }

/* Homesick: wobbly triple-sine mouth (like trembling lips) */
static void draw_mouth_homesick(void) { for (int x=28;x<43;x++) { float t=(x-28)/14.0f; int y=40+(int)(1.5f*sinf(t*3.14159f*3.0f)); px_set_off(x,y); px_set_off(x,y+1); } }

/* ── Chat bubble ───────────────────────────────────────────────────────
 *
 *  draw_bubble() — Draw a rounded-rectangle speech bubble with a
 *  triangular tail pointing left toward the octopus.
 *
 *  The bubble sits on the right side of the screen (bx=75) to avoid
 *  overlapping the octopus body on the left.
 *
 *  Construction:
 *    1. Top/bottom edges: two horizontal lines (2px thick each),
 *       inset 3px from the sides for rounded corners.
 *    2. Left/right edges: two vertical lines (2px thick each),
 *       inset 3px from the top/bottom.
 *    3. Corner dots: 3x3 diamond shapes at each corner.
 *    4. Tail: a small triangular pointer made from a lookup table
 *       of (dx, dy) offsets, connecting the bubble to the octopus.
 *
 *  Note: the bubble uses raw px_set() (not px_set_off()) because it
 *  is anchored to the screen, not to the octopus body.  It stays
 *  fixed even when the body wobbles.
 * ──────────────────────────────────────────────────────────────────── */
static void draw_bubble(void) {
    int bx=75, by=5+Y_OFF, bw=170, bh=70;
    for (int x=bx+3;x<bx+bw-3;x++) { px_set(x,by); px_set(x,by+1); px_set(x,by+bh-1); px_set(x,by+bh-2); }
    for (int y=by+3;y<by+bh-3;y++) { px_set(bx,y); px_set(bx+1,y); px_set(bx+bw-1,y); px_set(bx+bw-2,y); }
    int corners[][2] = {{bx+2,by+2},{bx+bw-3,by+2},{bx+2,by+bh-3},{bx+bw-3,by+bh-3}};
    for (int c=0;c<4;c++) for (int dy=-1;dy<=1;dy++) for (int dx=-1;dx<=1;dx++) if (abs(dx)+abs(dy)<=1) px_set(corners[c][0]+dx,corners[c][1]+dy);
    int tb=35+Y_OFF;
    static const int8_t tail_dx[]={0,-1,-2,-3,-4,-5,-6,-7,-6,-5,-4,-3,-2,-1,0};
    static const int8_t tail_dy[]={0,1,2,3,4,5,6,7,8,8,8,7,6,5,4};
    for (int i=0;i<15;i++) px_set(bx+tail_dx[i], tb+tail_dy[i]);
}

/* ── Text rendering ────────────────────────────────────────────────────
 *
 *  draw_char() — Render a single 5x7 character at position (x0, y0).
 *
 *  For each of the 7 rows, reads one byte from font5x7[idx][row].
 *  Then checks each of the 5 columns with a bit mask:
 *
 *    bits & (0x10 >> col)
 *
 *  0x10 is binary 10000 (bit 4 set).  Shifting it right by `col`
 *  positions tests column 0 (leftmost) through column 4 (rightmost):
 *    col=0: 0x10 = 10000  (tests bit 4)
 *    col=1: 0x08 = 01000  (tests bit 3)
 *    col=2: 0x04 = 00100  (tests bit 2)
 *    col=3: 0x02 = 00010  (tests bit 1)
 *    col=4: 0x01 = 00001  (tests bit 0)
 *
 *  If the bit is set, that pixel is part of the character glyph.
 *
 *  Uses raw px_set() (screen-anchored) because text appears inside
 *  the fixed speech bubble, not on the moving body.
 * ──────────────────────────────────────────────────────────────────── */
static void draw_char(int x0, int y0, int idx) { for (int row=0;row<7;row++) { uint8_t bits=font5x7[idx][row]; for (int col=0;col<5;col++) if (bits&(0x10>>col)) px_set(x0+col,y0+row); } }

/*
 * draw_text() — Render a string with word-wrapping.
 *
 * Parameters:
 *   x0, y0 — Top-left corner of the text area.
 *   text   — The string to render (should be uppercase for our font).
 *   max_w  — Maximum width in pixels before wrapping to the next line.
 *
 * Algorithm:
 *   1. Scan ahead to find the next word (sequence of non-space chars).
 *   2. Check if the word fits on the current line.
 *   3. If not, wrap: reset cx to x0 and advance cy by 9 pixels
 *      (7 for the character height + 2 for line spacing).
 *   4. Draw each character, advancing cx by char_w (6 pixels: 5 for
 *      the glyph + 1 for spacing between characters).
 *   5. Lowercase letters are converted to uppercase by subtracting 32
 *      (the ASCII distance between 'a' and 'A').
 *
 * The `const char *p` pointer walks through the input string.
 * `wlen` counts the length of the current word (chars until space or
 * end of string).  `word_px` is the word's width in pixels.
 */
static void draw_text(int x0, int y0, const char *text, int max_w) {
    int cx=x0, cy=y0, char_w=6;
    const char *p = text;
    while (*p) {
        const char *ws = p; int wlen = 0;
        while (p[wlen] && p[wlen] != ' ') wlen++;
        int word_px = wlen * char_w;
        if (cx > x0 && (cx - x0) + word_px > max_w) { cx = x0; cy += 9; }
        for (int i = 0; i < wlen; i++) { char c = p[i]; if (c >= 'a' && c <= 'z') c -= 32; draw_char(cx, cy, font_index(c)); cx += char_w; }
        p += wlen;
        if (*p == ' ') { cx += char_w; p++; }
    }
}

/* ── Clock header (ESP32 uses millis-based synthetic time) ─────────────
 *
 *  draw_clock_header() — Render a fake clock at the top center of the
 *  screen.  Since the ESP32 has no real-time clock (RTC) module, we
 *  synthesize a time starting at 12:00 PM and counting up using
 *  millis() (milliseconds since boot).
 *
 *  millis() is an Arduino function that returns the number of
 *  milliseconds since the board was powered on, as an unsigned long.
 *
 *  The modular arithmetic converts total seconds into 12-hour format:
 *    total_s = ms / 1000
 *    hour    = (12 + total_s / 3600) % 24   (starts at noon)
 *    minute  = (total_s % 3600) / 60
 *    hr12    = hour % 12, with 0 mapped to 12 (so "12:00" not "0:00")
 *
 *  snprintf() is a safe version of sprintf() that limits output to
 *  `sizeof(buf)` characters, preventing buffer overflow.
 * ──────────────────────────────────────────────────────────────────── */
static void draw_clock_header(void) {
    unsigned long ms = millis();
    unsigned long total_s = ms / 1000;
    /* Synthetic clock starting at noon */
    int hour = (12 + (int)(total_s / 3600)) % 24;
    int minute = (int)((total_s % 3600) / 60);
    int hr12 = hour % 12; if (hr12 == 0) hr12 = 12;
    const char *ampm = (hour < 12) ? "AM" : "PM";

    char buf[48];
    snprintf(buf, sizeof(buf), "%d:%02d %s", hr12, minute, ampm);
    int len = (int)strlen(buf);
    int header_x = (IMG_W - len * 6) / 2;   /* Center the text horizontally */
    if (header_x < 0) header_x = 0;
    draw_text(header_x, 1, buf, IMG_W);
}

/* ── Body animation transform ──────────────────────────────────────────
 *
 *  setup_body_transform() — Configure the body position/wobble
 *  parameters for the current mood and animation frame.
 *
 *  Parameters:
 *    mood — Current mood ID (0-15).
 *    f    — Frame counter (used as a time variable for animations).
 *
 *  Each mood case sets some combination of:
 *    body_dx/dy    — Translate the body (bobbing, swaying)
 *    body_x_expand — Make the body wider or narrower
 *    wobble_*      — Apply sine-wave horizontal distortion
 *
 *  The `f` parameter drives time-varying animations via sinf():
 *    sinf(f * speed) oscillates between -1 and +1 over time.
 *    Multiplying by an amplitude scales the motion range.
 *    Different frequencies (speed) for dx vs dy create complex paths.
 *
 *  Casting sinf() result to (int) truncates the decimal, creating
 *  discrete pixel-level motion on the low-res display.
 * ──────────────────────────────────────────────────────────────────── */
static void setup_body_transform(uint8_t mood, uint32_t f) {
    body_dx=0; body_dy=0; body_x_expand=0; wobble_amp=0; wobble_freq=0; wobble_phase=0;
    float pi=3.14159f;
    switch (mood) {
        case MOOD_ANGRY: body_dy=-1; body_x_expand=2; wobble_amp=0.5f; wobble_freq=0.3f; wobble_phase=f*pi; break;
        case MOOD_SAD: body_dy=3; body_x_expand=-1; break;
        case MOOD_UNHINGED: body_dx=(int)(1.5f*sinf(f*7.3f)); body_dy=(int)(1.5f*sinf(f*5.1f+1)); break;
        case MOOD_WEIRD: body_dx=(int)(3*sinf(f*0.8f)); wobble_amp=1.5f; wobble_freq=0.15f; wobble_phase=(float)f; break;
        case MOOD_CHAOTIC: body_dx=(int)(2*sinf(f*2.1f)); body_dy=(int)(2*sinf(f*1.7f)); wobble_amp=3; wobble_freq=0.25f; wobble_phase=f*2.0f; break;
        case MOOD_HUNGRY: body_dy=-2+(int)sinf(f*1.5f); break;
        case MOOD_TIRED: body_dy=2+(int)sinf(f*0.5f); body_x_expand=-1; break;
        case MOOD_SLAPHAPPY: body_dx=(int)(3*sinf(f*1.2f)); wobble_amp=2; wobble_freq=0.1f; wobble_phase=f*1.2f; break;
        case MOOD_LAZY: body_dy=3; body_x_expand=3; break;
        case MOOD_FAT: body_x_expand=3; body_dy=(int)sinf(f*1.8f); break;
        case MOOD_CHILL: body_dx=(int)sinf(f*0.4f); body_dy=1; break;
        case MOOD_CREEPY: body_x_expand=(int)(2*sinf(f*2.0f)); break;
        case MOOD_EXCITED: body_dy=(int)(3*sinf(f*3.0f)); break;
        case MOOD_NOSTALGIC: body_dx=(int)(2*sinf(f*0.5f)); body_dy=(int)sinf(f*0.3f); break;
        case MOOD_HOMESICK: body_dy=1; body_x_expand=-2; break;
        default: body_dy=(int)sinf(f*0.8f); break;
    }
}

/* ── Status bar ────────────────────────────────────────────────────────
 *
 *  draw_status_bar() — Draw the mood label centered at the bottom of
 *  the screen, flanked by "< >" arrows to hint that the user can
 *  navigate left/right.
 *
 *  Parameters:
 *    mood — Current mood ID, used to index mood_names[].
 *
 *  The centering math: total pixel width = strlen(status) * 6,
 *  then sx = (screen_width - total_width) / 2.
 * ──────────────────────────────────────────────────────────────────── */
static void draw_status_bar(uint8_t mood) {
    char status[32];
    snprintf(status, sizeof(status), "< %s >", mood_names[mood]);
    int sw = (int)strlen(status) * 6;
    int sx = (IMG_W - sw) / 2;
    if (sx < 0) sx = 0;
    draw_text(sx, IMG_H - 8, status, IMG_W);
}

/* ── Mouth animation cycles ────────────────────────────────────────────
 *
 *  Each mood has a 4-frame animation cycle that determines which mouth
 *  expression to show on each frame.  The cycle repeats: frame 0, 1,
 *  2, 3, 0, 1, 2, 3, ...
 *
 *  This creates a simple "talking" animation.  Most moods alternate
 *  between their signature mouth and EXPR_OPEN (mouth open = talking).
 *  For example, cycle_angry = {ANGRY, ANGRY, OPEN, ANGRY} means the
 *  octopus shows its angry frown most of the time, but opens its mouth
 *  every 3rd frame.
 *
 *  The arrays are `static const` — allocated once in flash/ROM, never
 *  modified at runtime.
 * ──────────────────────────────────────────────────────────────────── */
static const uint8_t cycle_normal[]    = {EXPR_SMIRK, EXPR_SMIRK, EXPR_OPEN, EXPR_SMILE};
static const uint8_t cycle_weird[]     = {EXPR_WEIRD, EXPR_WEIRD, EXPR_OPEN, EXPR_WEIRD};
static const uint8_t cycle_unhinged[]  = {EXPR_UNHINGED, EXPR_OPEN, EXPR_UNHINGED, EXPR_OPEN};
static const uint8_t cycle_angry[]     = {EXPR_ANGRY, EXPR_ANGRY, EXPR_OPEN, EXPR_ANGRY};
static const uint8_t cycle_sad[]       = {EXPR_SAD, EXPR_SAD, EXPR_OPEN, EXPR_SAD};
static const uint8_t cycle_chaotic[]   = {EXPR_CHAOTIC, EXPR_OPEN, EXPR_CHAOTIC, EXPR_OPEN};
static const uint8_t cycle_hungry[]    = {EXPR_HUNGRY, EXPR_OPEN, EXPR_HUNGRY, EXPR_HUNGRY};
static const uint8_t cycle_tired[]     = {EXPR_TIRED, EXPR_TIRED, EXPR_TIRED, EXPR_OPEN};
static const uint8_t cycle_slaphappy[] = {EXPR_SLAPHAPPY, EXPR_OPEN, EXPR_SLAPHAPPY, EXPR_SMILE};
static const uint8_t cycle_lazy[]      = {EXPR_LAZY, EXPR_LAZY, EXPR_LAZY, EXPR_OPEN};
static const uint8_t cycle_fat[]       = {EXPR_FAT, EXPR_FAT, EXPR_OPEN, EXPR_SMILE};
static const uint8_t cycle_chill[]     = {EXPR_CHILL, EXPR_CHILL, EXPR_SMILE, EXPR_OPEN};
static const uint8_t cycle_creepy[]    = {EXPR_CREEPY, EXPR_CREEPY, EXPR_OPEN, EXPR_CREEPY};
static const uint8_t cycle_excited[]   = {EXPR_EXCITED, EXPR_OPEN, EXPR_EXCITED, EXPR_SMILE};
static const uint8_t cycle_nostalgic[] = {EXPR_NOSTALGIC, EXPR_NOSTALGIC, EXPR_OPEN, EXPR_SMILE};
static const uint8_t cycle_homesick[]  = {EXPR_HOMESICK, EXPR_HOMESICK, EXPR_SAD, EXPR_OPEN};

/*
 * mood_cycle() — Return the 4-element animation cycle array for a mood.
 *
 * Parameters:
 *   mood — Mood ID (0-15).
 *
 * Returns:
 *   Pointer to a static const array of 4 expression IDs.  The caller
 *   indexes into it with (frame_idx % 4) to pick the current mouth.
 */
static const uint8_t *mood_cycle(uint8_t mood) {
    switch (mood) {
        case MOOD_WEIRD:     return cycle_weird;     case MOOD_UNHINGED:  return cycle_unhinged;
        case MOOD_ANGRY:     return cycle_angry;     case MOOD_SAD:       return cycle_sad;
        case MOOD_CHAOTIC:   return cycle_chaotic;   case MOOD_HUNGRY:    return cycle_hungry;
        case MOOD_TIRED:     return cycle_tired;     case MOOD_SLAPHAPPY: return cycle_slaphappy;
        case MOOD_LAZY:      return cycle_lazy;      case MOOD_FAT:       return cycle_fat;
        case MOOD_CHILL:     return cycle_chill;     case MOOD_CREEPY:    return cycle_creepy;
        case MOOD_EXCITED:   return cycle_excited;   case MOOD_NOSTALGIC: return cycle_nostalgic;
        case MOOD_HOMESICK:  return cycle_homesick;  default:             return cycle_normal;
    }
}

/* ── Frame composition ─────────────────────────────────────────────────
 *
 *  render_frame() — Compose one complete animation frame.
 *
 *  This is the main rendering orchestrator.  It draws every visual
 *  element in the correct order (back to front, a.k.a. "painter's
 *  algorithm"):
 *
 *    1. memset(frame, 0, ...) — Clear the entire framebuffer to white.
 *       Since 0-bits = white pixels, filling with 0x00 blanks the screen.
 *
 *    2. Clock header — drawn first (behind everything else).
 *
 *    3. Body silhouette — solid black shape from RLE data.
 *
 *    4. Eyes — white circles "punched out" of the body.
 *
 *    5. Pupils — black dots/shapes drawn inside the white eyes.
 *       The mood determines which pupil style is used.
 *
 *    6. Overlays (eyebrows, eyelids, tears) — mood-specific.
 *       Only certain moods add these (angry gets brows, tired gets
 *       lids, homesick gets tears, etc.).
 *
 *    7. Mouth — the expression animation frame (from the cycle).
 *
 *    8. Speech bubble — the rounded rectangle container for text.
 *
 *    9. Quote text — rendered inside the bubble.
 *
 *   10. Status bar — mood name at the bottom of the screen.
 *
 *  Parameters:
 *    q         — Pointer to the current Quote struct (contains text
 *                string and mood ID).
 *    expr      — The mouth expression ID for this animation frame.
 *    frame_idx — Current frame counter (used for body animation).
 *    mood      — Current mood ID.
 * ──────────────────────────────────────────────────────────────────── */

static void render_frame(const Quote *q, int expr, uint32_t frame_idx, uint8_t mood) {
    memset(frame, 0, sizeof(frame));       /* Step 1: Clear to all-white */
    draw_clock_header();                   /* Step 2: Clock at top */
    setup_body_transform(mood, frame_idx); /* Set up body position/wobble */
    draw_body_transformed();               /* Step 3: Black body silhouette */
    draw_eyes();                           /* Step 4: White eye sockets */

    /* Step 5: Draw mood-specific pupils inside the eyes */
    switch (mood) {
        case MOOD_WEIRD:     draw_pupils_weird();     break;  case MOOD_UNHINGED:  draw_pupils_unhinged();  break;
        case MOOD_ANGRY:     draw_pupils_angry();     break;  case MOOD_SAD:       draw_pupils_sad();       break;
        case MOOD_CHAOTIC:   draw_pupils_chaotic();   break;  case MOOD_HUNGRY:    draw_pupils_hungry();    break;
        case MOOD_TIRED:     draw_pupils_tired();     break;  case MOOD_LAZY:      draw_pupils_lazy();      break;
        case MOOD_FAT:       draw_pupils_fat();       break;  case MOOD_CHILL:     draw_pupils_chill();     break;
        case MOOD_CREEPY:    draw_pupils_creepy();    break;  case MOOD_EXCITED:   draw_pupils_excited();   break;
        case MOOD_NOSTALGIC: draw_pupils_nostalgic(); break;  case MOOD_HOMESICK:  draw_pupils_homesick();  break;
        default:             draw_pupils_normal();    break;
    }

    /* Step 6: Mood-specific overlays (brows, lids, tears, etc.) */
    if (mood == MOOD_ANGRY)     draw_brows_angry();
    if (mood == MOOD_SAD)       draw_brows_sad();
    if (mood == MOOD_TIRED)     draw_lids_tired();
    if (mood == MOOD_SLAPHAPPY) draw_eyes_slaphappy();
    if (mood == MOOD_LAZY)      draw_lids_lazy();
    if (mood == MOOD_HOMESICK)  draw_tears_homesick();

    /* Step 7: Draw the mouth expression for this animation frame */
    switch (expr) {
        case EXPR_OPEN:      draw_mouth_open();      break;  case EXPR_SMILE:     draw_mouth_smile();     break;
        case EXPR_WEIRD:     draw_mouth_weird();     break;  case EXPR_UNHINGED:  draw_mouth_unhinged();  break;
        case EXPR_ANGRY:     draw_mouth_angry();     break;  case EXPR_SAD:       draw_mouth_sad();       break;
        case EXPR_CHAOTIC:   draw_mouth_chaotic();   break;  case EXPR_HUNGRY:    draw_mouth_hungry();    break;
        case EXPR_TIRED:     draw_mouth_tired();     break;  case EXPR_SLAPHAPPY: draw_mouth_slaphappy(); break;
        case EXPR_LAZY:      draw_mouth_lazy();      break;  case EXPR_FAT:       draw_mouth_fat();       break;
        case EXPR_CHILL:     draw_mouth_chill();     break;  case EXPR_CREEPY:    draw_mouth_creepy();    break;
        case EXPR_EXCITED:   draw_mouth_excited();   break;  case EXPR_NOSTALGIC: draw_mouth_nostalgic(); break;
        case EXPR_HOMESICK:  draw_mouth_homesick();  break;  default:             draw_mouth_smirk();     break;
    }

    draw_bubble();                                  /* Step 8: Speech bubble */
    draw_text(81, 11 + Y_OFF, q->text, 158);       /* Step 9: Quote text */
    draw_status_bar(mood);                          /* Step 10: "< MOOD >" */
}

/* ======================================================================
 *  ESP32-SPECIFIC: Display push, PRNG, input, main loop
 *
 *  Everything below this point is platform-specific to the ESP32-S3.
 *  If porting to another platform, only this section needs to change.
 * ====================================================================== */

/* ── PRNG (ESP32 hardware RNG) ─────────────────────────────────────────
 *
 *  esp_random() vs software PRNG:
 *
 *  esp_random() is a function provided by the ESP-IDF (Espressif's
 *  development framework).  It reads from the ESP32's hardware Random
 *  Number Generator (RNG), which uses electrical noise from the
 *  Wi-Fi/Bluetooth radio and thermal sensor as entropy sources.  This
 *  produces TRUE random numbers (not pseudo-random), which is ideal
 *  for cryptography and unpredictable behavior.
 *
 *  However, calling esp_random() is relatively slow (it waits for
 *  hardware entropy).  So we use it ONCE to seed our fast software
 *  PRNG (xorshift32), then use xorshift for all subsequent random
 *  numbers.  This gives us the best of both worlds: unpredictable
 *  seed + fast generation.
 *
 *  xorshift32 algorithm (rng_next):
 *    Three XOR-shift operations that thoroughly mix the bits.
 *    It has a period of 2^32 - 1 (over 4 billion values before
 *    repeating).  The shifts (13, 17, 5) are carefully chosen
 *    constants proven to give good statistical properties.
 *
 *    ^=  is XOR-assign:  a ^= b  is shorthand for  a = a ^ b
 *    <<  is left-shift:  moves bits toward higher positions
 *    >>  is right-shift: moves bits toward lower positions
 *
 *    XOR (^) flips bits where the operands differ:
 *      0 ^ 0 = 0,  1 ^ 1 = 0,  0 ^ 1 = 1,  1 ^ 0 = 1
 * ──────────────────────────────────────────────────────────────────── */
static uint32_t rng_state;
static void rng_seed(void) { rng_state = esp_random(); }
static uint32_t rng_next(void) { rng_state ^= rng_state << 13; rng_state ^= rng_state >> 17; rng_state ^= rng_state << 5; return rng_state; }

/* ── Quote filtering ───────────────────────────────────────────────────
 *
 *  pick_quote_for_mood() — Select a random quote matching the given mood.
 *
 *  Parameters:
 *    mood — Mood ID to filter by (0-15).
 *
 *  Returns:
 *    Index into the global quotes[] array.
 *
 *  Algorithm:
 *    1. Scan all 823 quotes, collecting indices of those whose .mood
 *       field matches the requested mood.
 *    2. Pick a random one from the matching set.
 *    3. Fallback: if no quotes match (shouldn't happen), pick any
 *       random quote from the entire collection.
 *
 *  The candidates[] array is allocated on the stack (QUOTE_COUNT = 823
 *  ints = ~3.3 KB).  On ESP32-S3 with its generous 512 KB SRAM, this
 *  is fine.  On a tighter platform, you'd use a two-pass approach
 *  (count first, then pick the Nth match).
 *
 *  `rng_next() % count` gives a value in [0, count-1].  The modulo
 *  operator (%) returns the remainder after division.
 * ──────────────────────────────────────────────────────────────────── */
static int pick_quote_for_mood(uint8_t mood) {
    int candidates[QUOTE_COUNT];
    int count = 0;
    for (int i = 0; i < QUOTE_COUNT; i++)
        if (quotes[i].mood == mood)
            candidates[count++] = i;
    if (count == 0) return rng_next() % QUOTE_COUNT;
    return candidates[rng_next() % count];
}

/* ── Display push (GxEPD2) ─────────────────────────────────────────────
 *
 *  push_frame_to_display() — Send our framebuffer to the e-Paper panel.
 *
 *  GxEPD2's firstPage() / nextPage() pattern:
 *  ──────────────────────────────────────────
 *  E-Paper displays on low-memory MCUs often can't hold the entire
 *  screen in RAM.  GxEPD2 solves this with "paged" rendering: it
 *  divides the screen into horizontal stripes ("pages") and draws
 *  them one at a time.
 *
 *  The pattern is always:
 *
 *    display.firstPage();
 *    do {
 *        // Draw your content here (called once per page)
 *    } while (display.nextPage());
 *
 *  - firstPage() sets up the first page region.
 *  - The do-while body draws content (GxEPD2 clips to the current page).
 *  - nextPage() advances to the next page and returns true, or returns
 *    false when all pages have been drawn, ending the loop.
 *
 *  On ESP32-S3 with plenty of RAM, the "page" is often the full screen,
 *  so the loop body executes only once.  But the pattern is still
 *  required by the library.
 *
 *  drawBitmap() — Maps our framebuffer to the display:
 *    display.drawBitmap(x, y, bitmap, width, height, color)
 *
 *    - x, y = 0, 0 — top-left corner (full screen)
 *    - bitmap = frame — our byte array
 *    - width, height = IMG_W, IMG_H — dimensions in pixels
 *    - color = GxEPD_BLACK — pixels with bit=1 are drawn black;
 *              pixels with bit=0 remain the fillScreen color (white).
 *
 *  The bitmap format matches Adafruit_GFX conventions: MSB-first,
 *  left-to-right, top-to-bottom — exactly how our frame[] is organized.
 *
 *  Full vs Partial refresh:
 *    - setFullWindow() — Refreshes the entire display.  The e-Ink
 *      particles are fully cycled (black->white->final), eliminating
 *      ghosting.  Slow (~2 sec) but clean.  Used only for the first frame.
 *    - setPartialWindow() — Updates only the specified region.  Faster
 *      (~0.3 sec) but may accumulate ghosting artifacts over many
 *      updates.  Used for all subsequent frames.
 *
 *  `first_frame` is a static bool — it persists across function calls
 *  (like a global, but scoped to this file).  It starts as `true` and
 *  is set to `false` after the first display push.
 * ──────────────────────────────────────────────────────────────────── */

static bool first_frame = true;

static void push_frame_to_display(void) {
    /*
     * Our framebuffer: landscape 250x122, MSB-first, 1 = black pixel.
     * GxEPD2 drawBitmap(): same bit ordering (Adafruit_GFX standard).
     * We set rotation(1) = landscape, so coordinates map directly.
     */
    if (first_frame) {
        display.setFullWindow();           /* First frame: full refresh (clean) */
        first_frame = false;
    } else {
        display.setPartialWindow(0, 0, display.width(), display.height());  /* Subsequent: fast partial */
    }

    display.firstPage();                   /* Begin the paged drawing loop */
    do {
        display.fillScreen(GxEPD_WHITE);   /* Fill background with white */
        display.drawBitmap(0, 0, frame, IMG_W, IMG_H, GxEPD_BLACK);  /* Overlay our framebuffer */
    } while (display.nextPage());          /* Advance to next page (or finish) */
}

/* ── Setup ─────────────────────────────────────────────────────────────
 *
 *  setup() — Arduino entry point, called once at boot.
 *
 *  This function initializes all hardware:
 *    1. Serial port at 115200 baud for debug output and keyboard input.
 *    2. HAL (joystick GPIO pins, LED, ADC, etc.)
 *    3. SPI bus for the e-Paper display.
 *    4. GxEPD2 display driver.
 *    5. Random number generator seed.
 *
 *  SPI.begin(CLK, MISO, MOSI, CS):
 *    Initializes the SPI bus.  MISO is -1 because the e-Paper display
 *    is write-only (we never read data back from it).
 *
 *  display.init(115200, true, 2, false):
 *    - 115200: diagnostic serial baud rate for GxEPD2's own debug prints
 *    - true:   enable initial display reset
 *    - 2:      reset pulse duration (ms)
 *    - false:  don't pull CS high during reset
 *
 *  display.setRotation(1):
 *    Rotates the display coordinate system 90 degrees clockwise.
 *    The physical panel is portrait (122x250); rotation(1) makes it
 *    landscape (250x122), matching our framebuffer layout.
 * ──────────────────────────────────────────────────────────────────── */

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("\n=== Dilder ESP32-S3 — Mood Selector ===");
    Serial.printf("Board: %s  |  %d quotes\n", BOARD_NAME, QUOTE_COUNT);

    dilder_hal_init();

    SPI.begin(PIN_EPD_CLK, -1, PIN_EPD_DIN, PIN_EPD_CS);
    display.init(115200, true, 2, false);
    display.setRotation(1);

    rng_seed();

    /* Diagnostic: read all joystick GPIOs and print their raw state.
     * Expected: all 1 (HIGH) when no buttons are pressed (pull-ups active).
     * If any read 0 here with no buttons pressed, the wiring is wrong. */
    Serial.printf("GPIO check: UP(4)=%d DOWN(7)=%d LEFT(1)=%d RIGHT(2)=%d CENTER(15)=%d\n",
                  digitalRead(PIN_BTN_UP), digitalRead(PIN_BTN_DOWN),
                  digitalRead(PIN_BTN_LEFT), digitalRead(PIN_BTN_RIGHT),
                  digitalRead(PIN_BTN_CENTER));

    Serial.println("Controls:");
    Serial.println("  Joystick LEFT/RIGHT = cycle moods");
    Serial.println("  Joystick CENTER     = random mood");
    Serial.println("  Joystick UP         = new quote");
    Serial.println("  Serial: [/] = navigate, r = random, ? = help");
    Serial.println("Ready.\n");
}

/* ── Main loop ─────────────────────────────────────────────────────────
 *
 *  loop() — Arduino main loop, called repeatedly forever.
 *
 *  Each call to loop() = one animation frame.  The flow is:
 *
 *    1. Pick a quote if needed (first frame or mood changed).
 *    2. Select the mouth expression from the mood's 4-frame cycle.
 *    3. If mood changed or mouth is "open," pick a new quote
 *       (simulates the octopus "saying" something new).
 *    4. Render the complete frame into the framebuffer.
 *    5. Push the framebuffer to the e-Paper display.
 *    6. Print debug info to Serial.
 *    7. Poll for user input for 4 seconds (the inter-frame delay).
 *       - Check joystick buttons for mood navigation.
 *       - Check Serial for keyboard commands.
 *       - If any input is detected, break out early to update the
 *         display immediately.
 * ──────────────────────────────────────────────────────────────────── */

/*
 * State variables — declared `static` so they persist across loop()
 * calls (same lifetime as globals, but scoped to this file).
 *
 *  current_mood  — Which of the 16 moods is currently active.
 *  frame_idx     — Counts up every frame; drives animations and
 *                  selects which position in the 4-frame mouth cycle
 *                  to use (frame_idx % 4).
 *  qi            — Index into quotes[] for the currently displayed
 *                  quote.  -1 means "not yet picked."
 *  mood_changed  — Flag set when the user switches moods, cleared
 *                  after a new quote is picked.
 */
static uint8_t current_mood = MOOD_NORMAL;
static uint32_t frame_idx = 0;
static int qi = -1;
static bool mood_changed = true;

/*
 * Joystick edge detection — "last_*" variables.
 *
 * Problem: The joystick buttons are polled (checked) every 50 ms.
 * If you hold a button for 200 ms, it reads as "pressed" 4 times.
 * Without edge detection, the mood would advance 4 times!
 *
 * Solution: Remember the PREVIOUS state of each button.  Only act
 * on a button press when the current reading is TRUE but the
 * previous reading was FALSE — i.e., the *rising edge* of the
 * button signal (the moment it transitions from released to pressed).
 *
 *   if (left && !last_left)  =>  "left is pressed NOW, but was NOT
 *                                 pressed last time we checked"
 *                             =>  this is a fresh press, act on it.
 *
 * After checking, we save the current state: `last_left = left;`
 * so next iteration we can detect the next edge.
 *
 * `static` variables inside a function are initialized once (at
 * program start) and retain their values between function calls —
 * just like globals, but only visible inside this function.
 */
static bool last_left = false, last_right = false, last_center = false,
            last_up = false, last_down = false;

void loop() {
    if (qi < 0) qi = pick_quote_for_mood(current_mood);  /* First-time quote pick */

    const uint8_t *cycle = mood_cycle(current_mood);  /* Get the 4-frame mouth cycle */
    uint8_t expr = cycle[frame_idx % 4];              /* Pick this frame's mouth expression */

    /* Pick a new quote when mood changes or on "open mouth" frames
     * (simulates the octopus saying something new each time it opens
     * its mouth to "talk").  frame_idx > 0 avoids double-picking on
     * the very first frame. */
    if (mood_changed || (expr == EXPR_OPEN && frame_idx > 0)) {
        qi = pick_quote_for_mood(current_mood);
        mood_changed = false;
    }

    /* Render + push */
    render_frame(&quotes[qi], expr, frame_idx, current_mood);
    push_frame_to_display();

    /* Debug output to serial monitor (Serial.printf is Arduino-ESP32
     * extension; standard Arduino only has Serial.print/println) */
    Serial.printf("Frame %lu | < %s > (%d/%d) | \"%s\"\n",
                  (unsigned long)frame_idx, mood_names[current_mood],
                  current_mood + 1, MOOD_COUNT, quotes[qi].text);
    frame_idx++;

    /* Poll joystick + serial for 4 seconds between frames.
     * millis() returns current time in ms; we poll every 50ms
     * until the deadline, or until the user presses something. */
    unsigned long deadline = millis() + 4000;
    while (millis() < deadline) {
        /* Read current button states from the HAL */
        bool left   = hal_btn_left();
        bool right  = hal_btn_right();
        bool center = hal_btn_center();
        bool up     = hal_btn_up();
        bool down   = hal_btn_down();

        /* Debug: log raw GPIO state when any button is pressed */
        if (left || right || center || up || down) {
            Serial.printf("[BTN] L=%d R=%d U=%d D=%d C=%d\n",
                          left, right, up, down, center);
        }

        uint8_t prev = current_mood;
        bool input_received = false;

        /* Joystick: LEFT = previous mood (with wraparound).
         * The ternary `(current_mood == 0) ? MOOD_COUNT - 1 : current_mood - 1`
         * wraps from mood 0 back to mood 15, avoiding underflow
         * (unsigned subtraction past 0 would give a huge number). */
        if (left && !last_left) {
            Serial.println("[BTN] LEFT edge -> prev mood");
            current_mood = (current_mood == 0) ? MOOD_COUNT - 1 : current_mood - 1;
            input_received = true;
        }
        /* Joystick: RIGHT = next mood (with modulo wraparound).
         * `% MOOD_COUNT` wraps 16 back to 0. */
        if (right && !last_right) {
            Serial.println("[BTN] RIGHT edge -> next mood");
            current_mood = (current_mood + 1) % MOOD_COUNT;
            input_received = true;
        }
        /* Joystick: CENTER = random mood */
        if (center && !last_center) {
            Serial.println("[BTN] CENTER edge -> random mood");
            current_mood = rng_next() % MOOD_COUNT;
            input_received = true;
        }
        /* Joystick: UP = new quote (same mood) */
        if (up && !last_up) {
            Serial.println("[BTN] UP edge -> new quote");
            qi = pick_quote_for_mood(current_mood);
            mood_changed = true;
            input_received = true;
        }
        /* Joystick: DOWN (placeholder — no action yet) */
        if (down && !last_down) {
            Serial.println("[BTN] DOWN edge (no action assigned)");
        }

        /* Save current button states for edge detection on next poll */
        last_left = left; last_right = right; last_center = center;
        last_up = up; last_down = down;

        /* Serial input (same keys as Pico version).
         * Serial.available() returns the number of bytes waiting in
         * the serial receive buffer.  Serial.read() pops one byte.
         * The while loop drains all buffered input. */
        while (Serial.available()) {
            int ch = Serial.read();
            switch (ch) {
                case '[': case ',': current_mood = (current_mood == 0) ? MOOD_COUNT - 1 : current_mood - 1; input_received = true; break;
                case ']': case '.': current_mood = (current_mood + 1) % MOOD_COUNT; input_received = true; break;
                case 'r': case 'R': current_mood = rng_next() % MOOD_COUNT; input_received = true; break;
                case 'n': case 'N': current_mood = MOOD_NORMAL;    input_received = true; break;
                case 'w': case 'W': current_mood = MOOD_WEIRD;     input_received = true; break;
                case 'u': case 'U': current_mood = MOOD_UNHINGED;  input_received = true; break;
                case 'a': case 'A': current_mood = MOOD_ANGRY;     input_received = true; break;
                case 's': case 'S': current_mood = MOOD_SAD;       input_received = true; break;
                case 'c': case 'C': current_mood = MOOD_CHAOTIC;   input_received = true; break;
                case 'h': case 'H': current_mood = MOOD_HUNGRY;    input_received = true; break;
                case 't': case 'T': current_mood = MOOD_TIRED;     input_received = true; break;
                case 'p': case 'P': current_mood = MOOD_SLAPHAPPY; input_received = true; break;
                case 'l': case 'L': current_mood = MOOD_LAZY;      input_received = true; break;
                case 'f': case 'F': current_mood = MOOD_FAT;       input_received = true; break;
                case 'k': case 'K': current_mood = MOOD_CHILL;     input_received = true; break;
                case 'y': case 'Y': current_mood = MOOD_CREEPY;    input_received = true; break;
                case 'e': case 'E': current_mood = MOOD_EXCITED;   input_received = true; break;
                case 'o': case 'O': current_mood = MOOD_NOSTALGIC; input_received = true; break;
                case 'm': case 'M': current_mood = MOOD_HOMESICK;  input_received = true; break;
                case 'q': case 'Q': qi = pick_quote_for_mood(current_mood); mood_changed = true; input_received = true; break;
            }
        }

        if (current_mood != prev) {
            mood_changed = true;
            Serial.printf(">> Mood changed: %s --> %s\n", mood_names[prev], mood_names[current_mood]);
        }

        if (input_received) break;  /* Exit polling loop early to refresh display */
        delay(50);                  /* 50ms polling interval (20 Hz check rate) */
    }
}
