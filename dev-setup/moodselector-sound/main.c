/**
 * Joystick + Speaker Test — GPIO joystick input with piezo speaker feedback
 *
 * Tests all 5 joystick directions and the piezo speaker simultaneously.
 * Each direction plays a different tone. Center plays a short melody.
 * Display shows the last pressed direction and tone frequency.
 *
 * Wiring:
 *   Display (SPI1):
 *     CLK  -> GP10  pin 14    DIN  -> GP11  pin 15
 *     CS   -> GP9   pin 12    DC   -> GP8   pin 11
 *     RST  -> GP12  pin 16    BUSY -> GP13  pin 17
 *
 *   Joystick (K1-1506SN-01 breakout):
 *     COM  -> GND   pin 3
 *     L    -> GP2   pin 4     D    -> GP3   pin 5
 *     UP   -> GP4   pin 6     R    -> GP5   pin 7
 *     C    -> GP6   pin 9
 *
 *   Speaker:
 *     +    -> GP15  pin 20 (PWM)
 *     -    -> GND   pin 23 (or any GND)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include "DEV_Config.h"
#include "version.h"

/* Display variant selection */
#if defined(DISPLAY_V4)
  #include "EPD_2in13_V4.h"
  #define DISP_W EPD_2in13_V4_WIDTH
  #define DISP_H EPD_2in13_V4_HEIGHT
  #define EPD_Init()     EPD_2in13_V4_Init()
  #define EPD_Clear()    EPD_2in13_V4_Clear()
  #define EPD_Base(b)    EPD_2in13_V4_Display_Base(b)
  #define EPD_Partial(b) EPD_2in13_V4_Display_Partial(b)
  #define EPD_Sleep()    EPD_2in13_V4_Sleep()
  #define DISPLAY_NAME   "V4"
#else
  #include "EPD_2in13_V3.h"
  #define DISP_W EPD_2in13_V3_WIDTH
  #define DISP_H EPD_2in13_V3_HEIGHT
  #define EPD_Init()     EPD_2in13_V3_Init()
  #define EPD_Clear()    EPD_2in13_V3_Clear()
  #define EPD_Base(b)    EPD_2in13_V3_Display_Base(b)
  #define EPD_Partial(b) EPD_2in13_V3_Display_Partial(b)
  #define EPD_Sleep()    EPD_2in13_V3_Sleep()
  #define DISPLAY_NAME   "V3"
#endif

/* ─── Pin definitions ─── */
#define JOY_LEFT   2
#define JOY_DOWN   3
#define JOY_UP     4
#define JOY_RIGHT  5
#define JOY_CENTER 6
#define SPEAKER    15  /* GP15 = pin 20 (PWM) */

#define DEBOUNCE_MS 200

/* ─── Tone frequencies (Hz) ─── */
#define TONE_UP     1047   /* C5 */
#define TONE_DOWN    784   /* G4 */
#define TONE_LEFT    880   /* A4 */
#define TONE_RIGHT   988   /* B4 */
#define TONE_CENTER 1319   /* E5 */

/* Melody notes for center press (frequencies + durations) */
static const uint16_t melody_freq[] = { 1047, 1319, 1568, 1319, 1047, 0 };
static const uint16_t melody_dur[]  = {  100,  100,  200,  100,  200, 0 };

/* ─── Canvas constants ─── */
#define IMG_W         250
#define IMG_H         122
#define IMG_ROW_BYTES ((IMG_W + 7) / 8)

static uint8_t frame[IMG_ROW_BYTES * IMG_H];
static uint8_t display_buf[((DISP_W + 7) / 8) * DISP_H];

/* ─── Speaker PWM ─── */
static uint speaker_slice;

static void speaker_init(void) {
    gpio_set_function(SPEAKER, GPIO_FUNC_PWM);
    speaker_slice = pwm_gpio_to_slice_num(SPEAKER);
    pwm_set_enabled(speaker_slice, false);
    printf("Speaker PWM initialized on GP%d (slice %d)\n", SPEAKER, speaker_slice);
}

static void speaker_tone(uint16_t freq_hz, uint16_t duration_ms) {
    if (freq_hz == 0) {
        pwm_set_enabled(speaker_slice, false);
        sleep_ms(duration_ms);
        return;
    }

    /* PWM clock is 125 MHz. We want a specific frequency.
     * wrap = 125000000 / freq_hz
     * duty = 50% (wrap / 2) for loudest piezo output */
    uint32_t wrap = 125000000 / freq_hz;
    if (wrap > 65535) wrap = 65535;  /* 16-bit counter max */

    pwm_set_wrap(speaker_slice, (uint16_t)wrap);
    pwm_set_chan_level(speaker_slice, pwm_gpio_to_channel(SPEAKER), (uint16_t)(wrap / 2));
    pwm_set_enabled(speaker_slice, true);

    sleep_ms(duration_ms);

    pwm_set_enabled(speaker_slice, false);
}

static void speaker_melody(const uint16_t *freqs, const uint16_t *durs) {
    for (int i = 0; freqs[i] != 0 || durs[i] != 0; i++) {
        speaker_tone(freqs[i], durs[i]);
        sleep_ms(30);  /* gap between notes */
    }
}

/* ─── Pixel drawing ─── */
static inline void px_set(int x, int y) {
    if (x >= 0 && x < IMG_W && y >= 0 && y < IMG_H)
        frame[y * IMG_ROW_BYTES + x / 8] |= (0x80 >> (x & 7));
}

/* ─── 5x7 bitmap font (subset: A-Z, 0-9, space, common punctuation) ─── */
static const uint8_t font5x7[][7] = {
    {0x0e,0x11,0x11,0x1f,0x11,0x11,0x11}, /* A */
    {0x1e,0x11,0x11,0x1e,0x11,0x11,0x1e}, /* B */
    {0x0e,0x11,0x10,0x10,0x10,0x11,0x0e}, /* C */
    {0x1e,0x11,0x11,0x11,0x11,0x11,0x1e}, /* D */
    {0x1f,0x10,0x10,0x1e,0x10,0x10,0x1f}, /* E */
    {0x1f,0x10,0x10,0x1e,0x10,0x10,0x10}, /* F */
    {0x0e,0x11,0x10,0x17,0x11,0x11,0x0f}, /* G */
    {0x11,0x11,0x11,0x1f,0x11,0x11,0x11}, /* H */
    {0x0e,0x04,0x04,0x04,0x04,0x04,0x0e}, /* I */
    {0x07,0x02,0x02,0x02,0x02,0x12,0x0c}, /* J */
    {0x11,0x12,0x14,0x18,0x14,0x12,0x11}, /* K */
    {0x10,0x10,0x10,0x10,0x10,0x10,0x1f}, /* L */
    {0x11,0x1b,0x15,0x15,0x11,0x11,0x11}, /* M */
    {0x11,0x19,0x15,0x13,0x11,0x11,0x11}, /* N */
    {0x0e,0x11,0x11,0x11,0x11,0x11,0x0e}, /* O */
    {0x1e,0x11,0x11,0x1e,0x10,0x10,0x10}, /* P */
    {0x0e,0x11,0x11,0x11,0x15,0x12,0x0d}, /* Q */
    {0x1e,0x11,0x11,0x1e,0x14,0x12,0x11}, /* R */
    {0x0e,0x11,0x10,0x0e,0x01,0x11,0x0e}, /* S */
    {0x1f,0x04,0x04,0x04,0x04,0x04,0x04}, /* T */
    {0x11,0x11,0x11,0x11,0x11,0x11,0x0e}, /* U */
    {0x11,0x11,0x11,0x0a,0x0a,0x04,0x04}, /* V */
    {0x11,0x11,0x11,0x15,0x15,0x1b,0x11}, /* W */
    {0x11,0x0a,0x04,0x04,0x04,0x0a,0x11}, /* X */
    {0x11,0x0a,0x04,0x04,0x04,0x04,0x04}, /* Y */
    {0x1f,0x01,0x02,0x04,0x08,0x10,0x1f}, /* Z */
    {0x0e,0x11,0x13,0x15,0x19,0x11,0x0e}, /* 0 */
    {0x04,0x0c,0x04,0x04,0x04,0x04,0x0e}, /* 1 */
    {0x0e,0x11,0x01,0x06,0x08,0x10,0x1f}, /* 2 */
    {0x0e,0x11,0x01,0x06,0x01,0x11,0x0e}, /* 3 */
    {0x02,0x06,0x0a,0x12,0x1f,0x02,0x02}, /* 4 */
    {0x1f,0x10,0x1e,0x01,0x01,0x11,0x0e}, /* 5 */
    {0x06,0x08,0x10,0x1e,0x11,0x11,0x0e}, /* 6 */
    {0x1f,0x01,0x02,0x04,0x08,0x08,0x08}, /* 7 */
    {0x0e,0x11,0x11,0x0e,0x11,0x11,0x0e}, /* 8 */
    {0x0e,0x11,0x11,0x0f,0x01,0x02,0x0c}, /* 9 */
    {0x00,0x00,0x00,0x00,0x00,0x00,0x00}, /* space */
    {0x00,0x00,0x00,0x00,0x00,0x04,0x04}, /* . */
    {0x00,0x00,0x00,0x00,0x00,0x04,0x08}, /* , */
    {0x04,0x04,0x04,0x04,0x04,0x00,0x04}, /* ! */
    {0x0e,0x11,0x01,0x02,0x04,0x00,0x04}, /* ? */
    {0x00,0x00,0x00,0x1f,0x00,0x00,0x00}, /* - */
    {0x00,0x00,0x00,0x00,0x00,0x00,0x00}, /* ~ (blank) */
    {0x0e,0x11,0x11,0x11,0x11,0x11,0x0e}, /* : (reuse O) */
};
static const char font_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-~:";

static void draw_char(int x0, int y0, int idx) {
    for (int row = 0; row < 7; row++) {
        uint8_t bits = font5x7[idx][row];
        for (int col = 0; col < 5; col++)
            if (bits & (0x10 >> col))
                px_set(x0 + col, y0 + row);
    }
}

static void draw_text(int x0, int y0, const char *text) {
    int cx = x0;
    for (const char *c = text; *c; c++) {
        char up = *c;
        if (up >= 'a' && up <= 'z') up -= 32;  /* uppercase */
        const char *pos = strchr(font_chars, up);
        if (pos) {
            draw_char(cx, y0, (int)(pos - font_chars));
        }
        cx += 6;
    }
}

/* ─── Filled rectangle ─── */
static void fill_rect(int x0, int y0, int w, int h) {
    for (int y = y0; y < y0 + h; y++)
        for (int x = x0; x < x0 + w; x++)
            px_set(x, y);
}

/* ─── Transpose landscape → portrait ─── */
static void transpose_to_display(void) {
    uint16_t dst_row_bytes = (DISP_W + 7) / 8;
    memset(display_buf, 0xFF, sizeof(display_buf));
    for (int y = 0; y < IMG_H; y++) {
        for (int x = 0; x < IMG_W; x++) {
            int src_byte = y * IMG_ROW_BYTES + x / 8;
            int src_bit  = 7 - (x & 7);
            if ((frame[src_byte] >> src_bit) & 1) {
                int dx = y;
                int dy = 249 - x;
                int dst_byte = dy * dst_row_bytes + dx / 8;
                int dst_bit  = 7 - (dx & 7);
                display_buf[dst_byte] &= ~(1 << dst_bit);
            }
        }
    }
}

/* ─── Draw the test screen ─── */
static void render_screen(const char *direction, uint16_t freq, int press_count) {
    memset(frame, 0, sizeof(frame));

    /* Title */
    draw_text(30, 5, "MOODSELECTOR-SOUND");

    /* Divider line */
    for (int x = 10; x < 240; x++) px_set(x, 16);

    /* Direction display (big) */
    char dir_line[32];
    snprintf(dir_line, sizeof(dir_line), "DIRECTION: %s", direction);
    draw_text(20, 25, dir_line);

    /* Frequency */
    char freq_line[32];
    if (freq > 0)
        snprintf(freq_line, sizeof(freq_line), "TONE: %d HZ", freq);
    else
        snprintf(freq_line, sizeof(freq_line), "TONE: ---");
    draw_text(20, 40, freq_line);

    /* Press counter */
    char count_line[32];
    snprintf(count_line, sizeof(count_line), "PRESSES: %d", press_count);
    draw_text(20, 55, count_line);

    /* GPIO pin status header */
    draw_text(20, 72, "GPIO STATUS:");

    /* Visual pin indicators */
    const char *labels[] = {"L", "D", "U", "R", "C"};
    const int pins[] = {JOY_LEFT, JOY_DOWN, JOY_UP, JOY_RIGHT, JOY_CENTER};
    for (int i = 0; i < 5; i++) {
        int bx = 20 + i * 44;
        int by = 85;
        int pressed = !gpio_get(pins[i]);

        /* Label */
        draw_text(bx + 8, by, labels[i]);

        /* Pin number */
        char pn[8];
        snprintf(pn, sizeof(pn), "GP%d", pins[i]);
        draw_text(bx + 2, by + 10, pn);

        /* Indicator box (filled if pressed, outline if not) */
        if (pressed) {
            fill_rect(bx, by + 20, 30, 10);
        } else {
            for (int x = bx; x < bx + 30; x++) { px_set(x, by + 20); px_set(x, by + 29); }
            for (int y = by + 20; y < by + 30; y++) { px_set(bx, y); px_set(bx + 29, y); }
        }
    }

    /* Speaker pin */
    draw_text(20, 110, "SPEAKER: GP7");

    /* Version */
    char ver[32];
    snprintf(ver, sizeof(ver), "V%s", DILDER_VERSION);
    draw_text(190, 110, ver);
}

/* ─── Joystick init ─── */
static void joystick_init(void) {
    const uint pins[] = {JOY_UP, JOY_DOWN, JOY_LEFT, JOY_RIGHT, JOY_CENTER};
    for (int i = 0; i < 5; i++) {
        gpio_init(pins[i]);
        gpio_set_dir(pins[i], GPIO_IN);
        gpio_pull_up(pins[i]);
    }
    printf("Joystick GPIO initialized: L=GP%d D=GP%d U=GP%d R=GP%d C=GP%d\n",
           JOY_LEFT, JOY_DOWN, JOY_UP, JOY_RIGHT, JOY_CENTER);
}

/* ─── Main ─── */
int main(void) {
    stdio_init_all();
    sleep_ms(1000);

    printf("\n========================================\n");
    printf("  DILDER — MOODSELECTOR-SOUND\n");
    printf("  Version:  %s\n", DILDER_VERSION);
    printf("  Display:  %s\n", DISPLAY_NAME);
    printf("  Built:    %s %s\n", __DATE__, __TIME__);
    printf("========================================\n\n");

    if (DEV_Module_Init() != 0) {
        printf("ERROR: Hardware init failed.\n");
        return 1;
    }

    joystick_init();
    speaker_init();

    /* GPIO diagnostic */
    printf("\n--- GPIO Diagnostic ---\n");
    printf("Joystick: L=GP%d D=GP%d U=GP%d R=GP%d C=GP%d\n",
           JOY_LEFT, JOY_DOWN, JOY_UP, JOY_RIGHT, JOY_CENTER);
    printf("Speaker:  GP%d\n", SPEAKER);
    for (int t = 0; t < 3; t++) {
        printf("  Read %d: L=%d D=%d U=%d R=%d C=%d\n",
               t + 1,
               gpio_get(JOY_LEFT), gpio_get(JOY_DOWN), gpio_get(JOY_UP),
               gpio_get(JOY_RIGHT), gpio_get(JOY_CENTER));
        sleep_ms(300);
    }
    printf("--- End GPIO Diagnostic ---\n\n");

    /* Startup beep */
    printf("Playing startup beep...\n");
    speaker_tone(1000, 100);
    sleep_ms(50);
    speaker_tone(1500, 100);
    sleep_ms(50);
    speaker_tone(2000, 150);

    printf("Display init (%s)...\n", DISPLAY_NAME);
    EPD_Init();
    EPD_Clear();
    printf("Display ready.\n");

    const char *last_dir = "NONE";
    uint16_t last_freq = 0;
    int press_count = 0;
    uint32_t last_joy_time = 0;
    uint32_t frame_idx = 0;

    while (true) {
        /* Render current state */
        render_screen(last_dir, last_freq, press_count);
        transpose_to_display();

        if (frame_idx == 0)
            EPD_Base(display_buf);
        else
            EPD_Partial(display_buf);

        printf("Frame %lu | Dir: %-6s | Freq: %4d Hz | Presses: %d\n",
               (unsigned long)frame_idx, last_dir, last_freq, press_count);
        frame_idx++;

        /* Poll for 2 seconds */
        uint32_t elapsed = 0;
        bool input_received = false;

        while (elapsed < 2000 && !input_received) {
            uint32_t now = to_ms_since_boot(get_absolute_time());

            if (now - last_joy_time >= DEBOUNCE_MS) {
                if (gpio_get(JOY_LEFT) == 0) {
                    last_dir = "LEFT";
                    last_freq = TONE_LEFT;
                    speaker_tone(TONE_LEFT, 150);
                    last_joy_time = now;
                    press_count++;
                    input_received = true;
                    printf("  [JOY] LEFT  -> %d Hz\n", TONE_LEFT);
                } else if (gpio_get(JOY_RIGHT) == 0) {
                    last_dir = "RIGHT";
                    last_freq = TONE_RIGHT;
                    speaker_tone(TONE_RIGHT, 150);
                    last_joy_time = now;
                    press_count++;
                    input_received = true;
                    printf("  [JOY] RIGHT -> %d Hz\n", TONE_RIGHT);
                } else if (gpio_get(JOY_UP) == 0) {
                    last_dir = "UP";
                    last_freq = TONE_UP;
                    speaker_tone(TONE_UP, 150);
                    last_joy_time = now;
                    press_count++;
                    input_received = true;
                    printf("  [JOY] UP    -> %d Hz\n", TONE_UP);
                } else if (gpio_get(JOY_DOWN) == 0) {
                    last_dir = "DOWN";
                    last_freq = TONE_DOWN;
                    speaker_tone(TONE_DOWN, 150);
                    last_joy_time = now;
                    press_count++;
                    input_received = true;
                    printf("  [JOY] DOWN  -> %d Hz\n", TONE_DOWN);
                } else if (gpio_get(JOY_CENTER) == 0) {
                    last_dir = "CENTER";
                    last_freq = TONE_CENTER;
                    speaker_melody(melody_freq, melody_dur);
                    last_joy_time = now;
                    press_count++;
                    input_received = true;
                    printf("  [JOY] CTR   -> melody\n");
                }
            }

            sleep_ms(20);
            elapsed += 20;
        }
    }

    return 0;
}
