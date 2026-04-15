# Sensor Interfaces

> Hardware abstraction layer, driver interfaces, polling strategy, and event classification for all sensors.

---

## Table of Contents

1. [Unified Sensor Context](#1-unified-sensor-context)
2. [Sensor Manager](#2-sensor-manager)
3. [Individual Drivers](#3-individual-drivers)
4. [Event Classification](#4-event-classification)
5. [Duty Cycle Modes](#5-duty-cycle-modes)

---

## 1. Unified Sensor Context

All sensor data funneled into one struct, consumed by every gameplay system:

```c
// ─── Light (BH1750) ──────────────────────────────────────────
typedef struct {
    float    lux;              // Current ambient light (0-65535)
    float    delta_lux;        // Change since last read (for startle detection)
    uint8_t  zone;             // LIGHT_BRIGHT, LIGHT_INDOOR, LIGHT_DIM, LIGHT_DARK
} light_data_t;

#define LIGHT_BRIGHT   3       // > 500 lux
#define LIGHT_INDOOR   2       // 100-500 lux
#define LIGHT_DIM      1       // 10-100 lux
#define LIGHT_DARK     0       // < 10 lux

// ─── Microphone (MAX9814 via ADC) ────────────────────────────
typedef struct {
    uint16_t level;            // Current RMS level (12-bit ADC, 0-4095)
    uint16_t peak;             // Peak level in last sample window
    uint8_t  zone;             // MIC_SILENT, MIC_QUIET, MIC_MODERATE, MIC_LOUD, MIC_YELL
    uint32_t duration_ms;      // Duration of current zone
    bool     rhythmic;         // Heuristic: singing/music detected
} mic_data_t;

#define MIC_SILENT    0        // < noise floor (~50)
#define MIC_QUIET     1        // 50-200  (whisper)
#define MIC_MODERATE  2        // 200-800 (talking)
#define MIC_LOUD      3        // 800-2000 (loud talking)
#define MIC_YELL      4        // > 2000 (yelling)

// ─── Temperature / Humidity (AHT20) ──────────────────────────
typedef struct {
    float    celsius;          // Temperature in C
    float    percent;          // Relative humidity %
    uint8_t  comfort_zone;     // COMFORT_GOOD, _HOT, _COLD, _HUMID, _DRY
} environment_data_t;

#define COMFORT_GOOD    0      // 18-24C, 40-60% RH
#define COMFORT_HOT     1      // > 28C
#define COMFORT_COLD    2      // < 15C
#define COMFORT_HUMID   3      // > 70% RH (octopus likes this!)
#define COMFORT_DRY     4      // < 30% RH

// ─── Accelerometer (LIS2DH12TR) ─────────────────────────────
typedef struct {
    int16_t  x, y, z;          // Raw acceleration (mg)
    uint32_t step_count;        // Hardware pedometer total (since boot)
    uint16_t steps_since_last;  // Steps since last poll
    bool     walking;           // Step frequency 1-3 Hz
    bool     running;           // Step frequency > 3 Hz
    bool     shaking;           // High-frequency irregular motion
    bool     falling;           // Free-fall detected
    bool     picked_up;         // Orientation changed from resting
    bool     stationary;        // No motion for > 2 hours
    uint8_t  tilt_angle;        // Angle from horizontal (degrees)
} accel_data_t;

// ─── GPS (PA1010D) ───────────────────────────────────────────
typedef struct {
    bool     has_fix;           // Valid GPS fix
    float    latitude;          // Decimal degrees
    float    longitude;         // Decimal degrees
    float    hdop;              // Horizontal dilution of precision
    uint8_t  satellites;        // Number of satellites
} gps_data_t;

// ─── Magnetometer (QMC5883L) ─────────────────────────────────
typedef struct {
    int16_t  x, y, z;          // Raw magnetic field (uT)
    float    heading_deg;       // Compass heading 0-360
    bool     calibrated;        // Calibration completed
} mag_data_t;

// ─── WiFi Context ────────────────────────────────────────────
typedef struct {
    bool     at_home;           // Home SSID/BSSID detected
    bool     away_from_home;    // Home not detected
    uint32_t away_duration_ms;  // How long away from home
    bool     new_location;      // WiFi fingerprint not seen before
    uint8_t  location_id;       // Index into location database
} wifi_context_t;

// ─── Combined Sensor Context ─────────────────────────────────
typedef struct {
    light_data_t       light;
    mic_data_t         mic;
    environment_data_t temperature;
    environment_data_t humidity;     // Same AHT20, split for clarity
    accel_data_t       accel;
    gps_data_t         gps;
    mag_data_t         mag;
    wifi_context_t     wifi;
    uint32_t           timestamp;   // When this context was assembled
} sensor_context_t;
```

---

## 2. Sensor Manager

Orchestrates polling at different rates and assembles the unified context:

```c
typedef struct {
    sensor_context_t current;           // Latest assembled context
    uint32_t         last_poll_ms[SENSOR_COUNT];  // Per-sensor last poll time
    uint8_t          duty_mode;         // DUTY_ACTIVE, DUTY_IDLE, DUTY_SLEEP
    bool             sensor_present[SENSOR_COUNT]; // Detected during init
} sensor_manager_t;

typedef enum {
    SENSOR_LIGHT,
    SENSOR_MIC,
    SENSOR_ENV,       // AHT20 (temp + humidity)
    SENSOR_ACCEL,
    SENSOR_GPS,
    SENSOR_MAG,
    SENSOR_COUNT
} sensor_id_t;

// ─── Polling Intervals (in milliseconds) ────────────────────
typedef struct {
    uint32_t intervals[SENSOR_COUNT];
} poll_schedule_t;

static const poll_schedule_t SCHEDULE_ACTIVE = {
    .intervals = {
        [SENSOR_LIGHT] = 10000,    // Every 10s
        [SENSOR_MIC]   = 100,      // Every 100ms (volume tracking)
        [SENSOR_ENV]   = 60000,    // Every 60s
        [SENSOR_ACCEL] = 10000,    // Every 10s (read pedometer register)
        [SENSOR_GPS]   = 10000,    // Every 10s (when hunt active)
        [SENSOR_MAG]   = 10000,    // Every 10s (when hunt active)
    }
};

static const poll_schedule_t SCHEDULE_SLEEP = {
    .intervals = {
        [SENSOR_LIGHT] = 60000,    // Every 60s (wake trigger check)
        [SENSOR_MIC]   = 0,        // Off
        [SENSOR_ENV]   = 0,        // Off
        [SENSOR_ACCEL] = 0,        // Off (interrupt on motion)
        [SENSOR_GPS]   = 0,        // Off
        [SENSOR_MAG]   = 0,        // Off
    }
};

// ─── Initialization ──────────────────────────────────────────
void sensor_init(sensor_manager_t *mgr) {
    // Probe I2C bus for each sensor
    mgr->sensor_present[SENSOR_LIGHT] = drv_light_probe();   // 0x23
    mgr->sensor_present[SENSOR_ENV]   = drv_env_probe();     // 0x38
    mgr->sensor_present[SENSOR_ACCEL] = drv_accel_probe();   // 0x18
    mgr->sensor_present[SENSOR_GPS]   = drv_gps_probe();     // 0x10
    mgr->sensor_present[SENSOR_MAG]   = drv_mag_probe();     // 0x0D

    // Mic is on ADC — always present
    mgr->sensor_present[SENSOR_MIC] = true;
    drv_mic_init();

    // Configure sensors that were found
    if (mgr->sensor_present[SENSOR_LIGHT]) drv_light_configure();
    if (mgr->sensor_present[SENSOR_ENV])   drv_env_configure();
    if (mgr->sensor_present[SENSOR_ACCEL]) drv_accel_configure_pedometer();
    if (mgr->sensor_present[SENSOR_GPS])   drv_gps_configure();
    if (mgr->sensor_present[SENSOR_MAG])   drv_mag_configure();

    mgr->duty_mode = DUTY_ACTIVE;
}

// ─── Poll Orchestrator ───────────────────────────────────────
sensor_context_t sensor_poll(sensor_manager_t *mgr, uint32_t now) {
    const poll_schedule_t *sched =
        (mgr->duty_mode == DUTY_SLEEP) ? &SCHEDULE_SLEEP : &SCHEDULE_ACTIVE;

    for (int i = 0; i < SENSOR_COUNT; i++) {
        if (!mgr->sensor_present[i]) continue;
        if (sched->intervals[i] == 0) continue;  // Disabled in this mode
        if (now - mgr->last_poll_ms[i] < sched->intervals[i]) continue;

        mgr->last_poll_ms[i] = now;

        switch (i) {
            case SENSOR_LIGHT:
                drv_light_read(&mgr->current.light);
                break;
            case SENSOR_MIC:
                drv_mic_read(&mgr->current.mic);
                break;
            case SENSOR_ENV:
                drv_env_read(&mgr->current.temperature);
                break;
            case SENSOR_ACCEL:
                drv_accel_read(&mgr->current.accel);
                break;
            case SENSOR_GPS:
                drv_gps_read(&mgr->current.gps);
                break;
            case SENSOR_MAG:
                drv_mag_read(&mgr->current.mag);
                break;
        }
    }

    mgr->current.timestamp = now;
    return mgr->current;
}
```

---

## 3. Individual Drivers

### Light Sensor (BH1750)

```c
// drv_light.h
bool  drv_light_probe(void);      // I2C scan for 0x23
void  drv_light_configure(void);  // Set continuous high-res mode
void  drv_light_read(light_data_t *out);

// drv_light.c
void drv_light_read(light_data_t *out) {
    uint8_t buf[2];
    i2c_read(I2C_PORT, BH1750_ADDR, buf, 2);

    float new_lux = ((buf[0] << 8) | buf[1]) / 1.2f;
    out->delta_lux = new_lux - out->lux;
    out->lux = new_lux;

    // Classify zone
    if (new_lux > 500)      out->zone = LIGHT_BRIGHT;
    else if (new_lux > 100) out->zone = LIGHT_INDOOR;
    else if (new_lux > 10)  out->zone = LIGHT_DIM;
    else                     out->zone = LIGHT_DARK;
}
```

### Microphone (MAX9814 via ADC)

```c
// drv_mic.h
void drv_mic_init(void);
void drv_mic_read(mic_data_t *out);

// drv_mic.c
#define MIC_ADC_PIN 26        // GP26 = ADC0
#define MIC_SAMPLE_COUNT 64   // Samples per read (~1.3ms at 48kHz ADC)
#define MIC_DC_OFFSET 2048    // Center point of MAX9814 output

void drv_mic_read(mic_data_t *out) {
    // Sample burst: read N ADC values and compute RMS
    uint32_t sum_sq = 0;
    uint16_t peak = 0;

    for (int i = 0; i < MIC_SAMPLE_COUNT; i++) {
        uint16_t raw = adc_read();  // 12-bit (0-4095)
        int16_t centered = (int16_t)raw - MIC_DC_OFFSET;
        sum_sq += centered * centered;
        uint16_t abs_val = (centered >= 0) ? centered : -centered;
        if (abs_val > peak) peak = abs_val;
    }

    out->level = (uint16_t)sqrtf((float)sum_sq / MIC_SAMPLE_COUNT);
    out->peak = peak;

    // Classify zone
    if (out->level < 50)       out->zone = MIC_SILENT;
    else if (out->level < 200) out->zone = MIC_QUIET;
    else if (out->level < 800) out->zone = MIC_MODERATE;
    else if (out->level < 2000) out->zone = MIC_LOUD;
    else                        out->zone = MIC_YELL;

    // Track duration in current zone
    static uint8_t prev_zone = MIC_SILENT;
    static uint32_t zone_start = 0;
    if (out->zone != prev_zone) {
        prev_zone = out->zone;
        zone_start = time_mgr_now_ms();
    }
    out->duration_ms = time_mgr_now_ms() - zone_start;

    // Rhythmic detection (singing/music heuristic)
    // Track zero-crossing rate over last ~2 seconds
    // Music/singing: regular crossings. Speech: irregular. Noise: very high rate.
    static uint16_t crossing_history[8] = {0};
    static uint8_t hist_idx = 0;
    // (Simplified — actual implementation would analyze crossing intervals)
    out->rhythmic = false;  // TODO: implement rhythm detection
}
```

### Accelerometer (LIS2DH12TR)

```c
// drv_accel.h
bool  drv_accel_probe(void);
void  drv_accel_configure_pedometer(void);  // Enable hardware step counter
void  drv_accel_read(accel_data_t *out);

// drv_accel.c
void drv_accel_configure_pedometer(void) {
    // LIS2DH12TR has built-in pedometer in its embedded functions
    // Configure: ODR = 25Hz, FS = +/-2g, enable pedometer
    i2c_write_reg(ACCEL_ADDR, CTRL_REG1, 0x37);   // 25Hz, XYZ enabled
    i2c_write_reg(ACCEL_ADDR, CTRL_REG4, 0x00);   // +/-2g
    // Enable pedometer via embedded function registers
    // (Register map specific to LIS2DH12TR — consult datasheet)
}

void drv_accel_read(accel_data_t *out) {
    // Read raw acceleration
    uint8_t buf[6];
    i2c_read(ACCEL_ADDR, OUT_X_L | 0x80, buf, 6);  // Multi-byte read
    out->x = (int16_t)(buf[1] << 8 | buf[0]) >> 4;  // 12-bit left-justified
    out->y = (int16_t)(buf[3] << 8 | buf[2]) >> 4;
    out->z = (int16_t)(buf[5] << 8 | buf[4]) >> 4;

    // Read hardware step counter
    uint16_t new_steps = lis2dh12_read_step_count();
    out->steps_since_last = new_steps - out->step_count;
    out->step_count = new_steps;

    // Classify motion state
    float mag = sqrtf(out->x * out->x + out->y * out->y + out->z * out->z);

    // Free-fall: total acceleration near zero
    out->falling = (mag < 200);  // < 0.2g

    // Shaking: high variance in recent readings
    static float mag_history[8] = {0};
    static uint8_t mag_idx = 0;
    mag_history[mag_idx++ % 8] = mag;
    float variance = compute_variance(mag_history, 8);
    out->shaking = (variance > 500000);  // Empirical threshold

    // Walking / running based on step frequency
    static uint32_t last_step_check_ms = 0;
    uint32_t now = time_mgr_now_ms();
    if (now - last_step_check_ms >= 10000 && out->steps_since_last > 0) {
        float step_freq = (float)out->steps_since_last / ((now - last_step_check_ms) / 1000.0f);
        out->walking = (step_freq >= 0.5f && step_freq <= 3.0f);
        out->running = (step_freq > 3.0f);
        last_step_check_ms = now;
    }

    // Stationary: no steps for > 2 hours (tracked externally via activity module)

    // Tilt angle
    out->tilt_angle = (uint8_t)(acosf(out->z / fmaxf(mag, 1.0f)) * 180.0f / M_PI);

    // Picked up: tilt changed significantly from resting position
    static uint8_t resting_tilt = 0;
    if (out->stationary) resting_tilt = out->tilt_angle;
    out->picked_up = (abs(out->tilt_angle - resting_tilt) > 30);
}
```

### GPS (PA1010D)

```c
// drv_gps.h
bool  drv_gps_probe(void);
void  drv_gps_configure(void);   // Set update rate, enable GGA+RMC sentences
void  drv_gps_read(gps_data_t *out);

// drv_gps.c
// PA1010D outputs NMEA sentences over I2C at 0x10
// Read buffer, parse $GPGGA for fix/position, $GPRMC for speed/heading

void drv_gps_read(gps_data_t *out) {
    char nmea_buf[256];
    int len = i2c_read_until_newline(GPS_ADDR, nmea_buf, sizeof(nmea_buf));

    if (nmea_parse_gga(nmea_buf, len, out)) {
        // Valid GGA sentence parsed
        // out->latitude, longitude, hdop, satellites filled
        out->has_fix = (out->satellites >= 3 && out->hdop < 5.0f);
    }
}

// Haversine distance calculation (used by treasure hunt)
float gps_distance_m(float lat1, float lon1, float lat2, float lon2) {
    float dlat = (lat2 - lat1) * M_PI / 180.0f;
    float dlon = (lon2 - lon1) * M_PI / 180.0f;
    float a = sinf(dlat / 2) * sinf(dlat / 2) +
              cosf(lat1 * M_PI / 180.0f) * cosf(lat2 * M_PI / 180.0f) *
              sinf(dlon / 2) * sinf(dlon / 2);
    float c = 2 * atan2f(sqrtf(a), sqrtf(1 - a));
    return 6371000.0f * c;  // Earth radius in meters
}
```

---

## 4. Event Classification

The sensor manager classifies raw readings into game events:

```c
void sensor_classify_events(const sensor_context_t *prev,
                            const sensor_context_t *curr) {
    // ─── Light events ────────────────────────────────────────
    if (curr->light.delta_lux > 300) {
        event_fire(EVENT_LOUD_NOISE, NULL);  // Actually "sudden bright"
        // (should be a separate event — EVENT_LIGHT_STARTLE)
    }

    // ─── Mic events ──────────────────────────────────────────
    if (curr->mic.zone == MIC_YELL && prev->mic.zone < MIC_YELL) {
        event_fire(EVENT_LOUD_NOISE, NULL);
    }
    if (curr->mic.zone == MIC_MODERATE && curr->mic.duration_ms > 3000) {
        event_fire(EVENT_TALKING, NULL);
    }
    if (curr->mic.zone == MIC_SILENT && curr->mic.duration_ms > 30 * 60 * 1000) {
        event_fire(EVENT_SILENCE_LONG, NULL);
    }

    // ─── Motion events ───────────────────────────────────────
    if (curr->accel.shaking && !prev->accel.shaking) {
        event_fire(EVENT_SHAKEN, NULL);
    }
    if (curr->accel.falling) {
        event_fire(EVENT_DROPPED, NULL);
    }
    if (curr->accel.picked_up && !prev->accel.picked_up) {
        event_fire(EVENT_PICKED_UP, NULL);
    }

    // ─── Temperature events ──────────────────────────────────
    if ((curr->temperature.celsius > 28.0f || curr->temperature.celsius < 15.0f) &&
        prev->temperature.comfort_zone == COMFORT_GOOD) {
        event_fire(EVENT_TEMPERATURE_EXTREME, NULL);
    }
}
```

---

## 5. Duty Cycle Modes

Reduce power by polling less frequently when not needed:

```c
typedef enum {
    DUTY_ACTIVE,     // Normal gameplay — full polling
    DUTY_IDLE,       // User hasn't interacted for 30+ min — reduce mic
    DUTY_SLEEP,      // Dilder sleeping — light sensor only for wake trigger
    DUTY_HUNT,       // Treasure hunt — GPS + mag at full rate, reduce others
} duty_mode_t;

void sensor_set_duty_cycle(sensor_manager_t *mgr, duty_mode_t mode) {
    mgr->duty_mode = mode;

    // Power gating: disable sensors that aren't needed
    switch (mode) {
        case DUTY_SLEEP:
            drv_mic_power(false);    // Cut MAX9814 power via GPIO
            drv_gps_power(false);    // GPS draws 25mA — must disable
            break;
        case DUTY_HUNT:
            drv_gps_power(true);     // Enable GPS for treasure hunting
            break;
        case DUTY_ACTIVE:
        case DUTY_IDLE:
            drv_mic_power(true);
            drv_gps_power(false);    // GPS only in hunt mode
            break;
    }
}
```

---

### Sensor API Summary

```c
// ─── Public Interface (sensor.h) ─────────────────────────────

// Lifecycle
void sensor_init(sensor_manager_t *mgr);

// Polling (called from game loop)
sensor_context_t sensor_poll(sensor_manager_t *mgr, uint32_t now);
sensor_context_t sensor_poll_all(sensor_manager_t *mgr);  // Force-read everything

// Event classification
void sensor_classify_events(const sensor_context_t *prev,
                            const sensor_context_t *curr);

// Power management
void sensor_set_duty_cycle(sensor_manager_t *mgr, duty_mode_t mode);

// Queries
bool sensor_is_present(const sensor_manager_t *mgr, sensor_id_t id);
bool sensor_wake_trigger(const sensor_context_t *ctx);
```

---

*Next: [05-input-menu-ui.md](05-input-menu-ui.md) — Button handling, menu state machine, and screen rendering.*
