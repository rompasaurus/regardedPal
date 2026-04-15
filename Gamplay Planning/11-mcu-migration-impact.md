# MCU Migration Impact on Gameplay Implementation

> How the RP2040 (Pico W) → ESP32-S3-WROOM-1-N16R8 migration affects every gameplay module, what changes, what stays, and how to write portable code now.

---

## Table of Contents

1. [Migration Summary](#1-migration-summary)
2. [SDK Translation Layer](#2-sdk-translation-layer)
3. [Impact Per Module](#3-impact-per-module)
4. [GPIO Remapping](#4-gpio-remapping)
5. [FreeRTOS Implications](#5-freertos-implications)
6. [Memory & Flash Gains](#6-memory--flash-gains)
7. [WiFi & BLE Differences](#7-wifi--ble-differences)
8. [Power Management Changes](#8-power-management-changes)
9. [Build System Migration](#9-build-system-migration)
10. [Portability Strategy](#10-portability-strategy)

---

## 1. Migration Summary

| | RP2040 (Pico W) | ESP32-S3-WROOM-1-N16R8 |
|---|---|---|
| **Core** | Dual Cortex-M0+ @ 133 MHz | Dual Xtensa LX7 @ 240 MHz |
| **SRAM** | 264 KB | 512 KB + 8 MB PSRAM |
| **Flash** | 2 MB external | 16 MB integrated |
| **WiFi** | CYW43439 companion chip | Integrated 802.11 b/g/n |
| **BLE** | None | BLE 5.0 + Mesh |
| **GPIO** | 26 pins | 36 pins |
| **USB** | 1.1 (needs resistors) | OTG native |
| **RTC** | Software RTC (drifts) | Hardware RTC + ULP coprocessor |
| **SDK** | pico-sdk (lightweight) | ESP-IDF (FreeRTOS mandatory) |
| **Build** | CMake + arm-none-eabi-gcc | CMake + xtensa-esp32s3-elf-gcc |
| **Sleep** | `__wfi()`, dormant mode | Light/deep sleep, ULP wakeup |
| **Flash FS** | LittleFS (manual setup) | SPIFFS or LittleFS (built-in) |
| **OTA** | Not practical | Dual-partition, built-in |

**Bottom line**: The gameplay logic (stat decay, emotion resolution, dialogue selection, progression math) is pure C with no hardware dependencies — it ports unchanged. The hardware-touching code (GPIO, SPI, I2C, ADC, WiFi, sleep) gets rewritten against ESP-IDF APIs. The biggest structural change is that FreeRTOS becomes mandatory, which reshapes the game loop from a bare-metal `while(true)` into task-based scheduling.

---

## 2. SDK Translation Layer

Every Pico SDK call has an ESP-IDF equivalent. The gameplay code should never call these directly — they go through a hardware abstraction layer (HAL) defined in `sensor/` and `lib/`.

### GPIO

```c
// ─── Pico SDK ────────────────────────────────────────────────
gpio_init(PIN);
gpio_set_dir(PIN, GPIO_IN);
gpio_pull_up(PIN);
gpio_set_irq_enabled_with_callback(PIN, GPIO_IRQ_EDGE_FALL, true, &irq_cb);

// ─── ESP-IDF ─────────────────────────────────────────────────
gpio_config_t cfg = {
    .pin_bit_mask = (1ULL << PIN),
    .mode = GPIO_MODE_INPUT,
    .pull_up_en = GPIO_PULLUP_ENABLE,
    .intr_type = GPIO_INTR_NEGEDGE,
};
gpio_config(&cfg);
gpio_install_isr_service(0);
gpio_isr_handler_add(PIN, irq_cb, NULL);
```

### SPI (Display Driver)

```c
// ─── Pico SDK ────────────────────────────────────────────────
spi_init(spi1, 4000000);
gpio_set_function(CLK_PIN, GPIO_FUNC_SPI);
gpio_set_function(MOSI_PIN, GPIO_FUNC_SPI);
spi_write_blocking(spi1, data, len);

// ─── ESP-IDF ─────────────────────────────────────────────────
spi_bus_config_t bus = {
    .mosi_io_num = MOSI_PIN,
    .sclk_io_num = CLK_PIN,
    .miso_io_num = -1,
    .max_transfer_sz = 4096,
};
spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);

spi_device_interface_config_t dev = {
    .clock_speed_hz = 4000000,
    .mode = 0,
    .spics_io_num = CS_PIN,
    .queue_size = 1,
};
spi_device_handle_t spi;
spi_bus_add_device(SPI2_HOST, &dev, &spi);

spi_transaction_t t = { .length = len * 8, .tx_buffer = data };
spi_device_transmit(spi, &t);
```

### I2C (Sensors)

```c
// ─── Pico SDK ────────────────────────────────────────────────
i2c_init(i2c0, 400000);
gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
i2c_write_blocking(i2c0, addr, data, len, false);
i2c_read_blocking(i2c0, addr, buf, len, false);

// ─── ESP-IDF ─────────────────────────────────────────────────
i2c_config_t conf = {
    .mode = I2C_MODE_MASTER,
    .sda_io_num = SDA_PIN,
    .scl_io_num = SCL_PIN,
    .sda_pullup_en = GPIO_PULLUP_ENABLE,
    .scl_pullup_en = GPIO_PULLUP_ENABLE,
    .master.clk_speed = 400000,
};
i2c_param_config(I2C_NUM_0, &conf);
i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0);

// Transactions use command link builder:
i2c_cmd_handle_t cmd = i2c_cmd_link_create();
i2c_master_start(cmd);
i2c_master_write_byte(cmd, (addr << 1) | I2C_MASTER_WRITE, true);
i2c_master_write(cmd, data, len, true);
i2c_master_stop(cmd);
i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(100));
i2c_cmd_link_delete(cmd);
```

### ADC (Microphone, Battery)

```c
// ─── Pico SDK ────────────────────────────────────────────────
adc_init();
adc_gpio_init(26);       // GP26 = ADC0
adc_select_input(0);
uint16_t raw = adc_read();  // 12-bit

// ─── ESP-IDF ─────────────────────────────────────────────────
adc_oneshot_unit_handle_t adc_handle;
adc_oneshot_unit_init_cfg_t unit_cfg = { .unit_id = ADC_UNIT_1 };
adc_oneshot_new_unit(&unit_cfg, &adc_handle);

adc_oneshot_chan_cfg_t chan_cfg = {
    .atten = ADC_ATTEN_DB_12,   // Full range 0-3.3V
    .bitwidth = ADC_BITWIDTH_12,
};
adc_oneshot_config_channel(adc_handle, ADC_CHANNEL_0, &chan_cfg);

int raw;
adc_oneshot_read(adc_handle, ADC_CHANNEL_0, &raw);
```

### Timing

```c
// ─── Pico SDK ────────────────────────────────────────────────
uint32_t now = to_ms_since_boot(get_absolute_time());
sleep_ms(100);

// ─── ESP-IDF ─────────────────────────────────────────────────
uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);  // usec → ms
vTaskDelay(pdMS_TO_TICKS(100));  // FreeRTOS delay (yields to scheduler)
```

### Serial / printf

```c
// ─── Pico SDK ────────────────────────────────────────────────
stdio_init_all();   // USB CDC
printf("debug\n");

// ─── ESP-IDF ─────────────────────────────────────────────────
// stdio is routed automatically via ESP-IDF console
ESP_LOGI(TAG, "debug");   // Preferred: tagged logging with levels
printf("debug\n");         // Also works (goes to USB/UART monitor)
```

---

## 3. Impact Per Module

### Modules with ZERO code changes

These modules are pure game logic — no hardware calls:

| Module | File | Why it's portable |
|--------|------|-------------------|
| **Stat System** | `stat.c` | Pure math: decay accumulators, clamp, threshold checks |
| **Emotion Engine** | `emotion.c` | Weight evaluation, blending, hysteresis — all float math |
| **Life Stages** | `life.c` | FSM transitions, evolution scoring — pure logic |
| **Progression** | `progress.c` | XP math, achievement bitfield checks |
| **Dialogue** | `dialog.c` | Quote selection, context matching, recency filter |
| **Decor** | `decor.c` | Inventory bitfields, equip/unequip logic |
| **Event Bus** | `event.c` | Function pointer dispatch, ring buffer |

**These 7 modules compile identically on both platforms.** They only depend on `<stdint.h>`, `<stdbool.h>`, `<string.h>`, `<math.h>`, and the game's own headers.

### Modules with HAL-layer changes only

These modules call hardware through a thin abstraction that gets swapped per platform:

| Module | What changes | Scope |
|--------|-------------|-------|
| **Sensor Drivers** (`drv_*.c`) | I2C read/write calls, ADC calls | Rewrite each driver's init + read functions against ESP-IDF I2C/ADC API. Protocol bytes (register addresses, data formats) stay identical. |
| **Input** (`input.c`) | GPIO pin numbers, interrupt setup | Change pin defines and IRQ registration. Debounce logic unchanged. |
| **Display** (`EPD_*.c`, `ui_render.c`) | SPI init, SPI write, GPIO for DC/RST/BUSY | Rewrite SPI transaction calls. The SSD1680 command sequences and framebuffer format are hardware-independent. |
| **Time Manager** (`time_mgr.c`) | Millisecond timer source, RTC access | Replace `to_ms_since_boot()` with `esp_timer_get_time()`. ESP32-S3 has a real hardware RTC that survives deep sleep — better than Pico's software RTC. |

### Modules with structural changes

| Module | What changes | Why |
|--------|-------------|-----|
| **Game Loop** (`game_loop.c`) | `while(true)` loop becomes a FreeRTOS task. Timer-based tick becomes `vTaskDelay()` or `esp_timer` periodic callback. | ESP-IDF requires FreeRTOS. The game loop must yield to the scheduler. See [Section 5](#5-freertos-implications). |
| **Persistence** (`persist.c`) | LittleFS mount/read/write calls change to ESP-IDF's partition + SPIFFS/LittleFS API. | ESP-IDF has its own partition table and filesystem abstractions. Save data struct and CRC logic stay the same. |
| **WiFi Context** | CYW43 driver calls → ESP-IDF `esp_wifi` API. WiFi scanning completely different. | Different driver stack. The `wifi_context_t` struct and location DB logic stay the same — only the scan function changes. |
| **Treasure Hunt** (GPS/compass) | GPS NMEA parser stays. I2C driver for magnetometer rewrites. | Same I2C sensor protocol, different I2C API calls. |

---

## 4. GPIO Remapping

The pin numbers change completely. Isolate them into one header:

```c
// ─── hal_pins.h (RP2040 version) ─────────────────────────────
#ifdef PLATFORM_RP2040

#define PIN_EPD_CLK     10
#define PIN_EPD_MOSI    11
#define PIN_EPD_CS       9
#define PIN_EPD_DC       8
#define PIN_EPD_RST     12
#define PIN_EPD_BUSY    13

#define PIN_BTN_SELECT   2
#define PIN_BTN_BACK     3
#define PIN_BTN_UP       4
#define PIN_BTN_DOWN     5
#define PIN_BTN_ACTION   6

#define PIN_I2C_SDA      4   // I2C0
#define PIN_I2C_SCL      5

#define PIN_MIC_ADC     26   // ADC0

#define SPI_INSTANCE    spi1
#define I2C_INSTANCE    i2c0

#endif

// ─── hal_pins.h (ESP32-S3 version) ───────────────────────────
#ifdef PLATFORM_ESP32S3

#define PIN_EPD_CLK      9
#define PIN_EPD_MOSI    10
#define PIN_EPD_CS      11
#define PIN_EPD_DC       3
#define PIN_EPD_RST     12
#define PIN_EPD_BUSY    13   // TBD — verify with PCB v0.4 routing

#define PIN_BTN_UP       4
#define PIN_BTN_DOWN     5
#define PIN_BTN_LEFT     6   // ESP32 board uses 5-way joystick
#define PIN_BTN_RIGHT    7
#define PIN_BTN_CENTER   8

#define PIN_I2C_SDA     16   // I2C0 for sensors
#define PIN_I2C_SCL     17
#define PIN_ACCEL_INT   18   // LIS2DH12TR interrupt (optional)

#define PIN_MIC_ADC      1   // TBD — assign ADC1 channel

#define PIN_USB_DN      19   // Native USB
#define PIN_USB_DP      20

#define SPI_HOST_ID     SPI2_HOST
#define I2C_PORT_ID     I2C_NUM_0

#endif
```

**The gameplay code never references GPIO numbers directly.** It uses `PIN_BTN_SELECT`, `PIN_EPD_DC`, etc. Only `hal_pins.h` changes per platform.

### Button Mapping Note

The Pico W prototype uses 5 discrete buttons. The ESP32-S3 PCB v0.4 uses a 5-way joystick (up/down/left/right/center). The input abstraction (`input.h`) already works in terms of `BTN_SELECT`, `BTN_BACK`, `BTN_UP`, `BTN_DOWN`, `BTN_ACTION` — the mapping from physical GPIO to logical button lives in `input.c` and just needs the pin defines swapped.

If the 5-way joystick has different physical behavior (center = select, no separate back button), the input layer handles that remapping without touching any gameplay code.

---

## 5. FreeRTOS Implications

This is the most significant structural change. The Pico SDK firmware runs as bare-metal with an optional FreeRTOS layer. ESP-IDF **requires** FreeRTOS — the WiFi stack, timers, and power management all depend on it.

### Before (Pico W — bare-metal)

```c
int main(void) {
    hardware_init();
    game_loop_init();

    while (true) {
        game_loop_tick();    // Runs everything in one thread
    }
}
```

### After (ESP32-S3 — FreeRTOS tasks)

```c
void app_main(void) {     // ESP-IDF entry point (not "main")
    hardware_init();
    game_loop_init();

    // Create game loop task on core 0
    xTaskCreatePinnedToCore(
        game_task,           // Task function
        "game_loop",         // Name
        8192,                // Stack size (bytes) — generous for float math
        NULL,                // Parameters
        5,                   // Priority (mid)
        &game_task_handle,   // Handle
        0                    // Core 0 (core 1 reserved for WiFi)
    );

    // WiFi runs on core 1 automatically via ESP-IDF
}

void game_task(void *param) {
    while (true) {
        game_loop_tick();
        vTaskDelay(pdMS_TO_TICKS(100));  // Yield to FreeRTOS scheduler
    }
}
```

### What changes in practice

| Aspect | Bare-metal (Pico) | FreeRTOS (ESP32) | Action needed |
|--------|-------------------|------------------|---------------|
| **Main loop** | `while(true)` | `xTaskCreate` + `vTaskDelay` | Wrap game_loop_tick in a task |
| **Delays** | `sleep_ms()` (blocks CPU) | `vTaskDelay()` (yields to scheduler) | Replace all sleep calls |
| **Interrupts** | Direct GPIO IRQ | ISR must defer to task via queue | Button IRQ pushes to `xQueueSend`, task reads via `xQueueReceive` |
| **Shared state** | No concurrency concerns | WiFi task may access shared data | Protect `wifi_context_t` with a mutex if WiFi scan runs on core 1 |
| **Timers** | Manual tick counting | `esp_timer` periodic callbacks | Can replace tick counter with `esp_timer_create` for cleaner 1s game tick |
| **Stack size** | Unlimited (one thread) | Must size per task | 8 KB for game task is safe; sensor-heavy tasks may need more |

### Concurrency Safety

Most gameplay state is only accessed by the game task (core 0). The only cross-core access is WiFi scan results:

```c
// WiFi scan runs on core 1 via ESP-IDF internals.
// Results are copied to a shared struct protected by a mutex.

static SemaphoreHandle_t wifi_mutex;

void wifi_scan_complete_cb(wifi_scan_result_t *results, uint8_t count) {
    if (xSemaphoreTake(wifi_mutex, pdMS_TO_TICKS(10))) {
        // Copy results into sensor context
        memcpy(&shared_wifi_data, results, ...);
        xSemaphoreGive(wifi_mutex);
    }
}

// In game task (core 0):
void activity_update_location(...) {
    wifi_context_t local;
    if (xSemaphoreTake(wifi_mutex, pdMS_TO_TICKS(10))) {
        local = shared_wifi_data;  // Copy under lock
        xSemaphoreGive(wifi_mutex);
    }
    // Use local copy — no lock needed for the rest of the function
}
```

No other module needs concurrency protection. The game loop is single-threaded by design.

---

## 6. Memory & Flash Gains

### RAM: 264 KB → 512 KB + 8 MB PSRAM

The gameplay state uses ~8 KB (see [00-architecture-overview.md](00-architecture-overview.md)). The jump from 264 KB to 512 KB doesn't change the gameplay code, but it removes constraints:

| Opportunity | Impact |
|---|---|
| **Larger quote database** | Can embed 2000+ quotes instead of 800. No need to compress. |
| **Double-buffered display** | Two 3.9 KB framebuffers for flicker-free rendering. |
| **Deeper event history** | 64-entry event ring instead of 16 — richer context for emotion engine. |
| **Location DB in RAM** | Keep all 128 WiFi fingerprints in RAM (4 KB) instead of reading from flash each scan. |
| **PSRAM for assets** | Pre-rendered sprite overlays (hats, backgrounds) cached in PSRAM instead of drawn procedurally. |

**No gameplay code changes needed** — just increase buffer sizes in `#define` constants.

### Flash: 2 MB → 16 MB

| Opportunity | Impact |
|---|---|
| **OTA firmware updates** | ESP-IDF dual-partition boot: 7 MB per firmware slot. Download updates over WiFi. |
| **Larger filesystem** | 4+ MB for LittleFS/SPIFFS. Store location history, detailed achievement logs, memorial entries. |
| **Asset storage** | Pre-rendered bitmap overlays for decor items stored in flash, loaded to PSRAM at runtime. |
| **Save versioning** | Keep last N saves for rollback (paranoia against corruption). |

**Persistence module** (`persist.c`) benefits most: more room for location DB growth, memorial history, and eventual player profile data.

---

## 7. WiFi & BLE Differences

### WiFi Stack Rewrite

The WiFi code is the only module that gets completely rewritten (not ported):

```c
// ─── Pico W (CYW43 driver) ──────────────────────────────────
// Minimal: scan APs, check BSSID list, no real connection needed for gameplay
cyw43_arch_init();
cyw43_wifi_scan(...);

// ─── ESP-IDF (esp_wifi) ──────────────────────────────────────
// Full WiFi stack with event-driven API
wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
esp_wifi_init(&cfg);
esp_wifi_set_mode(WIFI_MODE_STA);
esp_wifi_start();
esp_wifi_scan_start(&scan_config, false);
// Results arrive via event handler on core 1
```

**What stays the same:**
- `wifi_context_t` struct (at_home, away_from_home, new_location, etc.)
- `location_db_t` and all location tracking logic
- WiFi fingerprint matching algorithm
- Home detection logic

**What changes:**
- Scan API calls (completely different driver)
- Event model (Pico: polling / ESP: event loop callback)
- Connection management (ESP-IDF has full TCP/IP stack — can do NTP, OTA, weather API)

### BLE (New Capability)

The ESP32-S3 adds BLE 5.0 which the Pico W doesn't have. This enables future features without any gameplay architecture changes:

| Feature | BLE Use | Gameplay Impact |
|---|---|---|
| **Peer discovery** | Two Dilders detect each other via BLE advertising | Social achievements, breeding (Phase 5+) |
| **Location beacons** | Read iBeacon / Eddystone for indoor positioning | More precise location tracking than WiFi alone |
| **Phone companion** | BLE GATT service for a future phone app | Push notifications, remote stat viewing |

None of these require changes to the core gameplay modules. They'd add new event types (`EVENT_PEER_DISCOVERED`, `EVENT_BEACON_DETECTED`) that plug into the existing event bus.

---

## 8. Power Management Changes

### Sleep Modes

```c
// ─── Pico W ──────────────────────────────────────────────────
// Light sleep: WFI (wait for interrupt)
__wfi();
// Deep sleep: dormant mode (loses RAM, wakes on GPIO/RTC)
// Pico W dormant is unreliable with CYW43 chip

// ─── ESP-IDF ─────────────────────────────────────────────────
// Light sleep: CPU halted, RAM retained, GPIO/timer wake
esp_sleep_enable_gpio_wakeup();
esp_sleep_enable_timer_wakeup(60 * 1000000);  // 60 seconds
esp_light_sleep_start();

// Deep sleep: CPU off, RTC RAM only (~8 KB), GPIO/timer wake
// ULP coprocessor can monitor sensors during deep sleep
esp_sleep_enable_ext0_wakeup(PIN_BTN_CENTER, 0);  // Wake on button
esp_deep_sleep_start();
```

### ULP Coprocessor (ESP32-S3 exclusive)

The ESP32-S3 has an Ultra-Low-Power coprocessor that runs while the main CPUs are in deep sleep. This enables:

```c
// ULP can:
// - Monitor GPIO pins (button press → wake main CPU)
// - Read ADC (battery level check while sleeping)
// - Read I2C sensors (light sensor for dawn detection)
// - Increment counters (step counting via accelerometer interrupt)

// Impact on gameplay:
// - GAME_STATE_SLEEPING can use deep sleep (~10 uA) instead of light sleep (~800 uA)
// - Pedometer keeps counting steps during sleep via accelerometer INT → ULP counter
// - Light sensor wakes device at dawn without polling from main CPU
```

**Game loop change**: The `enter_low_power()` function in [01-core-game-loop.md](01-core-game-loop.md) becomes significantly more capable. Instead of a simple `__wfi()`, it can enter true deep sleep with ULP monitoring sensors, giving orders of magnitude better battery life.

### RTC Improvement

The Pico W uses a software RTC that resets on power loss and drifts ~2 min/day. The ESP32-S3 has a hardware RTC with battery backup capability:

```c
// ESP32-S3 RTC survives deep sleep and light sleep
// Can optionally add a 32.768 kHz crystal for ±20ppm accuracy
// If no crystal: internal 150kHz oscillator (~5% drift, still better than Pico)

// Impact on time_mgr:
// - rtc_get_epoch() works after deep sleep (no re-sync needed)
// - NTP sync over WiFi corrects drift automatically
// - Age tracking (life->age_seconds) is more accurate
```

---

## 9. Build System Migration

### Current (Pico SDK)

```cmake
cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)
project(dilder-game C CXX)
pico_sdk_init()

add_executable(dilder-game main.c game/*.c sensor/*.c ui/*.c lib/*.c)
target_link_libraries(dilder-game
    pico_stdlib hardware_spi hardware_i2c hardware_adc hardware_rtc)
pico_enable_stdio_usb(dilder-game 1)
pico_add_extra_outputs(dilder-game)
```

### After (ESP-IDF)

```cmake
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(dilder-game)

# Component structure replaces flat source list
# main/CMakeLists.txt:
idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES "driver" "esp_timer" "esp_wifi" "nvs_flash" "fatfs"
)

# game/CMakeLists.txt:
idf_component_register(
    SRCS "stat.c" "emotion.c" "life.c" "dialog.c" "progress.c"
         "decor.c" "event.c" "game_loop.c" "persist.c" "activity.c"
         "treasure.c" "time_mgr.c"
    INCLUDE_DIRS "."
    REQUIRES "driver"    # Only for time_mgr (esp_timer)
)

# sensor/CMakeLists.txt:
idf_component_register(
    SRCS "sensor.c" "drv_light.c" "drv_mic.c"
         "drv_env.c" "drv_accel.c" "drv_gps.c" "drv_mag.c"
    INCLUDE_DIRS "."
    REQUIRES "driver"    # I2C, ADC, GPIO drivers
)
```

### Key Differences

| Aspect | Pico SDK | ESP-IDF |
|---|---|---|
| **Project structure** | Flat: all .c files in one CMakeLists | Component-based: each module is a component with its own CMakeLists |
| **Entry point** | `int main(void)` | `void app_main(void)` |
| **Output** | `.uf2` file (drag-and-drop flash) | `.bin` file (flash via `esptool.py` or USB-OTG) |
| **Configuration** | `#define` in code or CMake options | `menuconfig` (Kconfig-based, persistent `.config`) |
| **Feature flags** | CMake `option()` | Kconfig `menuconfig` entries |

### Feature Flags Migration

```
# Pico SDK (CMakeLists.txt):
option(DILDER_SENSORS  "Enable sensor integration" OFF)

# ESP-IDF (Kconfig.projbuild):
menu "Dilder Configuration"
    config DILDER_SENSORS
        bool "Enable sensor integration (Phase 3B)"
        default n
    config DILDER_ACTIVITY
        bool "Enable step/location tracking (Phase 3C)"
        default n
    config DILDER_TREASURE
        bool "Enable treasure hunts (Phase 4B)"
        default n
endmenu
```

Same concept, different syntax. The gameplay code uses `#ifdef CONFIG_DILDER_SENSORS` instead of `#ifdef DILDER_SENSORS`.

---

## 10. Portability Strategy

### How to write code now that ports cleanly later

**Rule 1: Gameplay logic never includes platform headers.**

```c
// GOOD — stat.c includes only its own header and standard lib
#include "stat.h"
#include <stdint.h>
#include <math.h>

// BAD — stat.c reaches into hardware
#include "hardware/gpio.h"    // Pico SDK header — don't do this
```

**Rule 2: Time comes from a wrapper, not the SDK.**

```c
// time_mgr.h — platform-agnostic interface
uint32_t time_mgr_now_ms(void);
uint32_t time_mgr_epoch(void);

// time_mgr_rp2040.c
uint32_t time_mgr_now_ms(void) {
    return to_ms_since_boot(get_absolute_time());
}

// time_mgr_esp32.c
uint32_t time_mgr_now_ms(void) {
    return (uint32_t)(esp_timer_get_time() / 1000);
}
```

**Rule 3: Sensor drivers implement a common interface.**

```c
// drv_light.h — same on both platforms
bool  drv_light_probe(void);
void  drv_light_configure(void);
void  drv_light_read(light_data_t *out);

// drv_light_rp2040.c — uses pico-sdk I2C
// drv_light_esp32.c  — uses esp-idf I2C
// Both fill the same light_data_t struct
```

**Rule 4: The event bus isolates modules.**

Because modules communicate through `event_fire()` and `event_listen()` rather than direct function calls, swapping or stubbing a module doesn't cascade. If the WiFi driver isn't ready on ESP32-S3, the location tracking module still compiles — it just never receives `EVENT_NEW_LOCATION`.

**Rule 5: Pin definitions live in one file.**

`hal_pins.h` with `#ifdef PLATFORM_*` guards (shown in [Section 4](#4-gpio-remapping)) is the single source of truth for all GPIO assignments. No magic numbers in driver code.

### Suggested File Structure for Dual-Platform

```
game/                     # Pure logic — compiles on both
    stat.c, emotion.c, life.c, dialog.c, ...
    (no platform #ifdefs needed)

hal/                      # Hardware abstraction headers
    hal_pins.h            # Pin defines per platform
    hal_time.h            # time_mgr_now_ms(), time_mgr_epoch()
    hal_spi.h             # hal_spi_write(data, len)
    hal_i2c.h             # hal_i2c_read(addr, reg, buf, len)
    hal_gpio.h            # hal_gpio_read(pin), hal_gpio_set_irq(...)
    hal_flash.h           # hal_flash_read/write (LittleFS wrapper)
    hal_wifi.h            # hal_wifi_scan(), hal_wifi_is_home()

hal/rp2040/               # Pico SDK implementations
    hal_time.c, hal_spi.c, hal_i2c.c, hal_gpio.c, hal_flash.c, hal_wifi.c

hal/esp32s3/              # ESP-IDF implementations
    hal_time.c, hal_spi.c, hal_i2c.c, hal_gpio.c, hal_flash.c, hal_wifi.c

sensor/                   # Sensor protocols (platform-agnostic via hal_i2c)
    drv_light.c           # Uses hal_i2c_read/write — same code on both
    drv_accel.c
    ...

ui/                       # Display rendering (platform-agnostic via hal_spi)
    ui_render.c           # Uses hal_spi_write for display — same code on both
    ...
```

With this structure, migrating to ESP32-S3 means:
1. Write new files in `hal/esp32s3/` (the actual porting work)
2. Update CMakeLists to link the new HAL source files
3. Change nothing in `game/`, `sensor/`, or `ui/`

---

## Migration Effort Estimate by Module

| Module | Files | Effort | Notes |
|--------|-------|--------|-------|
| `game/` (all gameplay) | 12 files | **None** | Pure logic, zero platform calls |
| `hal/` (new abstraction) | ~12 files | **Medium** | Write thin wrappers — mostly boilerplate |
| `sensor/drv_*.c` | 6 drivers | **Low** | If using HAL: no changes. If drivers call SDK directly: rewrite I2C calls. |
| `ui/` (rendering) | 5 files | **Low** | SPI display writes go through HAL. Drawing math unchanged. |
| `main.c` (entry point) | 1 file | **Low** | `main()` → `app_main()`, add FreeRTOS task creation |
| `persist.c` (flash) | 1 file | **Medium** | LittleFS mount API differs. Save/load struct unchanged. |
| WiFi code | 1-2 files | **High** | Complete rewrite against `esp_wifi`. Scanning API is fundamentally different. |
| Power management | 1 file | **Medium** | Sleep/wake rewritten for ESP-IDF sleep API + ULP. |

**Total: ~70% of code compiles unchanged. ~20% needs HAL wrapper swaps. ~10% (WiFi, power, entry point) gets rewritten.**

---

*This document should be revisited when the ESP32-S3 PCB v0.4 is assembled and ready for firmware bring-up. Pin assignments may shift during PCB routing — update `hal_pins.h` accordingly.*
