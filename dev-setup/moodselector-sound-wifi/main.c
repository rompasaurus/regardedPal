/**
 * Joystick + Speaker + WiFi Test
 *
 * Connects to WiFi, syncs time via NTP, shows WiFi status icon on display.
 * Joystick plays tones. Display shows real network time, SSID, signal, and
 * a WiFi emblem (solid = connected, crossed = disconnected).
 *
 * Wiring (same as joystick-sound-test):
 *   Display SPI1: CLK=GP10, DIN=GP11, CS=GP9, DC=GP8, RST=GP12, BUSY=GP13
 *   Joystick:     COM=GND(pin3), L=GP2, D=GP3, UP=GP4, R=GP5, C=GP6
 *   Speaker:      +=GP7(pin10), -=GND(pin8)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"
#include "hardware/pwm.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
// hardware/rtc.h only exists on RP2040 — RP2350 uses pico_aon_timer
#if !defined(PICO_RP2350)
#include "hardware/rtc.h"
#endif
#include "lwip/dns.h"
#include "lwip/pbuf.h"
#include "lwip/udp.h"
#include "DEV_Config.h"
#include "version.h"
#include "wifi_config.h"

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
#define SPEAKER    7

#define DEBOUNCE_MS 200

/* Tone frequencies */
#define TONE_UP     1047
#define TONE_DOWN    784
#define TONE_LEFT    880
#define TONE_RIGHT   988
#define TONE_CENTER 1319

static const uint16_t melody_freq[] = { 1047, 1319, 1568, 1319, 1047, 0 };
static const uint16_t melody_dur[]  = {  100,  100,  200,  100,  200, 0 };

/* ─── Canvas ─── */
#define IMG_W         250
#define IMG_H         122
#define IMG_ROW_BYTES ((IMG_W + 7) / 8)

static uint8_t frame[IMG_ROW_BYTES * IMG_H];
static uint8_t display_buf[((DISP_W + 7) / 8) * DISP_H];

/* ─── WiFi state ─── */
static bool wifi_connected = false;
static bool ntp_synced = false;
static int32_t wifi_rssi = 0;
static char wifi_ssid_display[33] = "---";
static char wifi_ip_str[20] = "---";

/* ─── NTP state ─── */
#define NTP_PORT 123
#define NTP_MSG_LEN 48
#define NTP_DELTA 2208988800ULL  /* seconds between 1900 and 1970 */

static struct udp_pcb *ntp_pcb = NULL;
static ip_addr_t ntp_server_addr;
static bool ntp_request_sent = false;
static volatile bool ntp_time_received = false;
static time_t ntp_epoch = 0;

/* ─── Speaker PWM ─── */
static uint speaker_slice;

static void speaker_init(void) {
    gpio_set_function(SPEAKER, GPIO_FUNC_PWM);
    speaker_slice = pwm_gpio_to_slice_num(SPEAKER);
    pwm_set_enabled(speaker_slice, false);
}

static void speaker_tone(uint16_t freq_hz, uint16_t duration_ms) {
    if (freq_hz == 0) { sleep_ms(duration_ms); return; }
    uint32_t wrap = 125000000 / freq_hz;
    if (wrap > 65535) wrap = 65535;
    pwm_set_wrap(speaker_slice, (uint16_t)wrap);
    pwm_set_chan_level(speaker_slice, pwm_gpio_to_channel(SPEAKER), (uint16_t)(wrap / 2));
    pwm_set_enabled(speaker_slice, true);
    sleep_ms(duration_ms);
    pwm_set_enabled(speaker_slice, false);
}

static void speaker_melody(const uint16_t *freqs, const uint16_t *durs) {
    for (int i = 0; freqs[i] != 0 || durs[i] != 0; i++) {
        speaker_tone(freqs[i], durs[i]);
        sleep_ms(30);
    }
}

/* ─── Pixel drawing ─── */
static inline void px_set(int x, int y) {
    if (x >= 0 && x < IMG_W && y >= 0 && y < IMG_H)
        frame[y * IMG_ROW_BYTES + x / 8] |= (0x80 >> (x & 7));
}

static inline void px_clr(int x, int y) {
    if (x >= 0 && x < IMG_W && y >= 0 && y < IMG_H)
        frame[y * IMG_ROW_BYTES + x / 8] &= ~(0x80 >> (x & 7));
}

/* ─── 5x7 font ─── */
static const uint8_t font5x7[][7] = {
    {0x0e,0x11,0x11,0x1f,0x11,0x11,0x11},{0x1e,0x11,0x11,0x1e,0x11,0x11,0x1e},
    {0x0e,0x11,0x10,0x10,0x10,0x11,0x0e},{0x1e,0x11,0x11,0x11,0x11,0x11,0x1e},
    {0x1f,0x10,0x10,0x1e,0x10,0x10,0x1f},{0x1f,0x10,0x10,0x1e,0x10,0x10,0x10},
    {0x0e,0x11,0x10,0x17,0x11,0x11,0x0f},{0x11,0x11,0x11,0x1f,0x11,0x11,0x11},
    {0x0e,0x04,0x04,0x04,0x04,0x04,0x0e},{0x07,0x02,0x02,0x02,0x02,0x12,0x0c},
    {0x11,0x12,0x14,0x18,0x14,0x12,0x11},{0x10,0x10,0x10,0x10,0x10,0x10,0x1f},
    {0x11,0x1b,0x15,0x15,0x11,0x11,0x11},{0x11,0x19,0x15,0x13,0x11,0x11,0x11},
    {0x0e,0x11,0x11,0x11,0x11,0x11,0x0e},{0x1e,0x11,0x11,0x1e,0x10,0x10,0x10},
    {0x0e,0x11,0x11,0x11,0x15,0x12,0x0d},{0x1e,0x11,0x11,0x1e,0x14,0x12,0x11},
    {0x0e,0x11,0x10,0x0e,0x01,0x11,0x0e},{0x1f,0x04,0x04,0x04,0x04,0x04,0x04},
    {0x11,0x11,0x11,0x11,0x11,0x11,0x0e},{0x11,0x11,0x11,0x0a,0x0a,0x04,0x04},
    {0x11,0x11,0x11,0x15,0x15,0x1b,0x11},{0x11,0x0a,0x04,0x04,0x04,0x0a,0x11},
    {0x11,0x0a,0x04,0x04,0x04,0x04,0x04},{0x1f,0x01,0x02,0x04,0x08,0x10,0x1f},
    {0x0e,0x11,0x13,0x15,0x19,0x11,0x0e},{0x04,0x0c,0x04,0x04,0x04,0x04,0x0e},
    {0x0e,0x11,0x01,0x06,0x08,0x10,0x1f},{0x0e,0x11,0x01,0x06,0x01,0x11,0x0e},
    {0x02,0x06,0x0a,0x12,0x1f,0x02,0x02},{0x1f,0x10,0x1e,0x01,0x01,0x11,0x0e},
    {0x06,0x08,0x10,0x1e,0x11,0x11,0x0e},{0x1f,0x01,0x02,0x04,0x08,0x08,0x08},
    {0x0e,0x11,0x11,0x0e,0x11,0x11,0x0e},{0x0e,0x11,0x11,0x0f,0x01,0x02,0x0c},
    {0x00,0x00,0x00,0x00,0x00,0x00,0x00},{0x00,0x00,0x00,0x00,0x00,0x04,0x04},
    {0x00,0x00,0x00,0x00,0x00,0x04,0x08},{0x04,0x04,0x04,0x04,0x04,0x00,0x04},
    {0x0e,0x11,0x01,0x02,0x04,0x00,0x04},{0x00,0x00,0x00,0x1f,0x00,0x00,0x00},
    {0x00,0x00,0x00,0x00,0x00,0x00,0x00},{0x01,0x02,0x04,0x08,0x10,0x00,0x00},
    {0x04,0x04,0x04,0x00,0x00,0x04,0x04},
};
static const char font_chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?-~/:%";

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
        if (up >= 'a' && up <= 'z') up -= 32;
        const char *pos = strchr(font_chars, up);
        if (pos) draw_char(cx, y0, (int)(pos - font_chars));
        cx += 6;
    }
}

/* ─── WiFi icon (16x12 pixels) ─── */
static void draw_wifi_icon(int x0, int y0, bool connected) {
    /* Three arcs (signal strength bars) */
    /* Outer arc */
    for (int i = -6; i <= 6; i++) {
        int ay = y0 + 1;
        if (i >= -5 && i <= 5) ay = y0;
        if (i >= -3 && i <= 3) ay = y0 - 1;
        px_set(x0 + 8 + i, ay);
    }
    /* Middle arc */
    for (int i = -4; i <= 4; i++) {
        int ay = y0 + 4;
        if (i >= -3 && i <= 3) ay = y0 + 3;
        if (i >= -1 && i <= 1) ay = y0 + 2;
        px_set(x0 + 8 + i, ay);
    }
    /* Inner arc */
    for (int i = -2; i <= 2; i++) {
        int ay = y0 + 6;
        if (i >= -1 && i <= 1) ay = y0 + 5;
        px_set(x0 + 8 + i, ay);
    }
    /* Center dot */
    px_set(x0 + 8, y0 + 8);
    px_set(x0 + 7, y0 + 8);
    px_set(x0 + 9, y0 + 8);
    px_set(x0 + 8, y0 + 9);

    /* Cross-out if disconnected */
    if (!connected) {
        for (int i = 0; i < 12; i++) {
            px_set(x0 + 2 + i, y0 + i);
            px_set(x0 + 3 + i, y0 + i);
            px_set(x0 + 14 - i, y0 + i);
            px_set(x0 + 13 - i, y0 + i);
        }
    }
}

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

/* ─── NTP client (manual UDP, no SNTP lib dependency) ─── */
static void ntp_recv_cb(void *arg, struct udp_pcb *pcb, struct pbuf *p,
                         const ip_addr_t *addr, u16_t port) {
    if (p->tot_len >= NTP_MSG_LEN) {
        uint8_t *buf = (uint8_t *)p->payload;
        /* Extract transmit timestamp (bytes 40-43 = seconds since 1900) */
        uint32_t secs = (buf[40] << 24) | (buf[41] << 16) | (buf[42] << 8) | buf[43];
        ntp_epoch = (time_t)(secs - NTP_DELTA) + TIMEZONE_OFFSET_SEC;
        ntp_time_received = true;

        /* Set RTC from NTP */
        struct tm *t = gmtime(&ntp_epoch);
        datetime_t dt = {
            .year  = (int16_t)(t->tm_year + 1900),
            .month = (int8_t)(t->tm_mon + 1),
            .day   = (int8_t)t->tm_mday,
            .dotw  = (int8_t)t->tm_wday,
            .hour  = (int8_t)t->tm_hour,
            .min   = (int8_t)t->tm_min,
            .sec   = (int8_t)t->tm_sec,
        };
        rtc_set_datetime(&dt);

        printf("  [NTP] Time synced: %04d-%02d-%02d %02d:%02d:%02d (UTC%+d)\n",
               dt.year, dt.month, dt.day, dt.hour, dt.min, dt.sec,
               TIMEZONE_OFFSET_SEC / 3600);
        ntp_synced = true;
    }
    pbuf_free(p);
}

static void ntp_dns_cb(const char *name, const ip_addr_t *addr, void *arg) {
    if (addr) {
        ntp_server_addr = *addr;
        printf("  [NTP] Resolved %s -> %s\n", name, ipaddr_ntoa(addr));

        /* Send NTP request */
        struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, NTP_MSG_LEN, PBUF_RAM);
        if (p) {
            uint8_t *buf = (uint8_t *)p->payload;
            memset(buf, 0, NTP_MSG_LEN);
            buf[0] = 0x1b;  /* LI=0, VN=3, Mode=3 (client) */
            udp_sendto(ntp_pcb, p, &ntp_server_addr, NTP_PORT);
            pbuf_free(p);
            ntp_request_sent = true;
            printf("  [NTP] Request sent to %s\n", ipaddr_ntoa(&ntp_server_addr));
        }
    } else {
        printf("  [NTP] DNS resolve failed for %s\n", name);
    }
}

static void ntp_init(void) {
    ntp_pcb = udp_new();
    if (!ntp_pcb) {
        printf("  [NTP] Failed to create UDP PCB\n");
        return;
    }
    udp_recv(ntp_pcb, ntp_recv_cb, NULL);

    /* Resolve NTP server */
    printf("  [NTP] Resolving %s...\n", NTP_SERVER);
    err_t err = dns_gethostbyname(NTP_SERVER, &ntp_server_addr, ntp_dns_cb, NULL);
    if (err == ERR_OK) {
        /* Already cached — send immediately */
        ntp_dns_cb(NTP_SERVER, &ntp_server_addr, NULL);
    } else if (err != ERR_INPROGRESS) {
        printf("  [NTP] DNS error: %d\n", err);
    }
}

/* ─── WiFi connection ─── */
static bool wifi_init_and_connect(void) {
    printf("WiFi: Initializing CYW43...\n");
    if (cyw43_arch_init()) {
        printf("WiFi: CYW43 init FAILED\n");
        return false;
    }

    cyw43_arch_enable_sta_mode();
    printf("WiFi: Connecting to \"%s\"...\n", WIFI_SSID);
    strncpy(wifi_ssid_display, WIFI_SSID, sizeof(wifi_ssid_display) - 1);

    int err = cyw43_arch_wifi_connect_timeout_ms(WIFI_SSID, WIFI_PASS,
                                                  CYW43_AUTH_WPA2_AES_PSK, 15000);
    if (err) {
        printf("WiFi: Connection FAILED (err=%d)\n", err);
        wifi_connected = false;
        return false;
    }

    wifi_connected = true;

    /* Get IP address */
    struct netif *netif = &cyw43_state.netif[CYW43_ITF_STA];
    snprintf(wifi_ip_str, sizeof(wifi_ip_str), "%s", ipaddr_ntoa(&netif->ip_addr));
    printf("WiFi: Connected! IP: %s\n", wifi_ip_str);

    /* Get RSSI */
    cyw43_wifi_get_rssi(&cyw43_state, &wifi_rssi);
    printf("WiFi: RSSI: %d dBm\n", (int)wifi_rssi);

    return true;
}

/* ─── Render screen ─── */
static const char *month_names[] = {
    "JAN","FEB","MAR","APR","MAY","JUN",
    "JUL","AUG","SEP","OCT","NOV","DEC"
};

static void render_screen(const char *last_dir, uint16_t last_freq, int press_count) {
    memset(frame, 0, sizeof(frame));

    /* ── WiFi icon (top-right) ── */
    draw_wifi_icon(230, 2, wifi_connected);

    /* ── Date + Time from RTC (top-left) ── */
    datetime_t t;
    rtc_get_datetime(&t);
    int hr12 = t.hour % 12;
    if (hr12 == 0) hr12 = 12;
    const char *ampm = (t.hour < 12) ? "AM" : "PM";

    char time_str[48];
    snprintf(time_str, sizeof(time_str), "%s %d, %d  %d:%02d:%02d %s",
             month_names[t.month > 0 ? t.month - 1 : 0], t.day, t.year,
             hr12, t.min, t.sec, ampm);
    draw_text(5, 3, time_str);

    /* NTP sync indicator */
    draw_text(5, 13, ntp_synced ? "NTP SYNCED" : "RTC ONLY");

    /* Divider */
    for (int x = 5; x < 245; x++) px_set(x, 22);

    /* ── WiFi info ── */
    char ssid_line[48];
    snprintf(ssid_line, sizeof(ssid_line), "SSID: %s", wifi_ssid_display);
    draw_text(5, 26, ssid_line);

    char ip_line[32];
    snprintf(ip_line, sizeof(ip_line), "IP: %s", wifi_ip_str);
    draw_text(5, 36, ip_line);

    char rssi_line[32];
    if (wifi_connected)
        snprintf(rssi_line, sizeof(rssi_line), "SIGNAL: %d DBM", (int)wifi_rssi);
    else
        snprintf(rssi_line, sizeof(rssi_line), "SIGNAL: ---");
    draw_text(5, 46, rssi_line);

    /* Divider */
    for (int x = 5; x < 245; x++) px_set(x, 56);

    /* ── Joystick + speaker info ── */
    char dir_line[32];
    snprintf(dir_line, sizeof(dir_line), "DIR: %-8s  TONE: %d HZ", last_dir, last_freq);
    draw_text(5, 60, dir_line);

    char count_line[32];
    snprintf(count_line, sizeof(count_line), "PRESSES: %d", press_count);
    draw_text(5, 70, count_line);

    /* ── GPIO indicators ── */
    const char *labels[] = {"L", "D", "U", "R", "C"};
    const int pins[] = {JOY_LEFT, JOY_DOWN, JOY_UP, JOY_RIGHT, JOY_CENTER};
    for (int i = 0; i < 5; i++) {
        int bx = 5 + i * 44;
        int by = 84;
        int pressed = !gpio_get(pins[i]);
        draw_text(bx + 8, by, labels[i]);
        char pn[8];
        snprintf(pn, sizeof(pn), "GP%d", pins[i]);
        draw_text(bx + 2, by + 10, pn);
        if (pressed)
            fill_rect(bx, by + 20, 30, 8);
        else {
            for (int x = bx; x < bx + 30; x++) { px_set(x, by + 20); px_set(x, by + 27); }
            for (int y = by + 20; y < by + 28; y++) { px_set(bx, y); px_set(bx + 29, y); }
        }
    }

    /* ── Version (bottom-right) ── */
    char ver[16];
    snprintf(ver, sizeof(ver), "V%s", DILDER_VERSION);
    draw_text(200, 113, ver);

    /* Speaker label */
    draw_text(5, 113, "SPK:GP7");
}

/* ─── Joystick init ─── */
static void joystick_init(void) {
    const uint pins[] = {JOY_UP, JOY_DOWN, JOY_LEFT, JOY_RIGHT, JOY_CENTER};
    for (int i = 0; i < 5; i++) {
        gpio_init(pins[i]);
        gpio_set_dir(pins[i], GPIO_IN);
        gpio_pull_up(pins[i]);
    }
}

/* ─── Main ─── */
int main(void) {
    stdio_init_all();
    sleep_ms(1000);

    printf("\n========================================\n");
    printf("  DILDER — MOODSELECTOR-SOUND-WIFI\n");
    printf("  Version:  %s\n", DILDER_VERSION);
    printf("  Display:  %s\n", DISPLAY_NAME);
    printf("  Built:    %s %s\n", __DATE__, __TIME__);
    printf("========================================\n\n");

    /* Init RTC with compile time as fallback */
    rtc_init();
    datetime_t dt_fallback = {
        .year = 2026, .month = 5, .day = 5,
        .dotw = 1, .hour = 12, .min = 0, .sec = 0
    };
    rtc_set_datetime(&dt_fallback);

    joystick_init();
    speaker_init();

    /* Startup beep */
    speaker_tone(1000, 80);
    sleep_ms(30);
    speaker_tone(1500, 80);

    /* WiFi connect */
    bool wifi_ok = wifi_init_and_connect();

    if (wifi_ok) {
        /* Success chime */
        speaker_tone(1047, 80);
        sleep_ms(30);
        speaker_tone(1319, 80);
        sleep_ms(30);
        speaker_tone(1568, 150);

        /* Start NTP sync */
        ntp_init();

        /* Poll for NTP response (up to 5 seconds) */
        printf("Waiting for NTP response...\n");
        for (int i = 0; i < 100 && !ntp_time_received; i++) {
            cyw43_arch_poll();
            sleep_ms(50);
        }

        if (!ntp_time_received) {
            printf("  [NTP] No response — using compile-time fallback\n");
        }
    } else {
        /* Fail tone */
        speaker_tone(400, 200);
        sleep_ms(50);
        speaker_tone(300, 300);
    }

    /* Init display */
    if (DEV_Module_Init() != 0) {
        printf("ERROR: Hardware init failed.\n");
        return 1;
    }

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
        /* Poll WiFi stack */
        if (wifi_connected) {
            cyw43_arch_poll();
            cyw43_wifi_get_rssi(&cyw43_state, &wifi_rssi);
        }

        /* Render and display */
        render_screen(last_dir, last_freq, press_count);
        transpose_to_display();

        if (frame_idx == 0)
            EPD_Base(display_buf);
        else
            EPD_Partial(display_buf);

        printf("Frame %lu | WiFi:%s | Dir:%-6s | %d Hz\n",
               (unsigned long)frame_idx,
               wifi_connected ? "OK" : "OFF",
               last_dir, last_freq);
        frame_idx++;

        /* Poll for input (3 seconds) */
        uint32_t elapsed = 0;
        bool input_received = false;

        while (elapsed < 3000 && !input_received) {
            uint32_t now = to_ms_since_boot(get_absolute_time());

            if (wifi_connected) cyw43_arch_poll();

            if (now - last_joy_time >= DEBOUNCE_MS) {
                if (gpio_get(JOY_LEFT) == 0) {
                    last_dir = "LEFT"; last_freq = TONE_LEFT;
                    speaker_tone(TONE_LEFT, 150);
                    last_joy_time = now; press_count++; input_received = true;
                } else if (gpio_get(JOY_RIGHT) == 0) {
                    last_dir = "RIGHT"; last_freq = TONE_RIGHT;
                    speaker_tone(TONE_RIGHT, 150);
                    last_joy_time = now; press_count++; input_received = true;
                } else if (gpio_get(JOY_UP) == 0) {
                    last_dir = "UP"; last_freq = TONE_UP;
                    speaker_tone(TONE_UP, 150);
                    last_joy_time = now; press_count++; input_received = true;
                } else if (gpio_get(JOY_DOWN) == 0) {
                    last_dir = "DOWN"; last_freq = TONE_DOWN;
                    speaker_tone(TONE_DOWN, 150);
                    last_joy_time = now; press_count++; input_received = true;
                } else if (gpio_get(JOY_CENTER) == 0) {
                    last_dir = "CENTER"; last_freq = TONE_CENTER;
                    speaker_melody(melody_freq, melody_dur);
                    last_joy_time = now; press_count++; input_received = true;
                }
            }

            sleep_ms(20);
            elapsed += 20;
        }
    }

    return 0;
}
