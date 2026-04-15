# Core Game Loop

> The tick system, timing architecture, sleep/wake management, and event dispatch.

---

## Table of Contents

1. [Main Loop Pseudocode](#1-main-loop-pseudocode)
2. [Tick Timing](#2-tick-timing)
3. [Game States](#3-game-states)
4. [Sleep / Wake Cycle](#4-sleep--wake-cycle)
5. [Event System](#5-event-system)
6. [Initialization Sequence](#6-initialization-sequence)

---

## 1. Main Loop Pseudocode

```c
// ─── Entry Point ─────────────────────────────────────────────
int main(void) {
    hardware_init();          // GPIO, SPI, I2C, ADC, RTC
    display_init();           // EPD controller, clear screen
    sensor_init();            // Probe I2C bus, configure sensors
    persistence_load();       // Load saved game state from flash
    ui_init();                // Set initial screen, render first frame
    game_loop_init();         // Set tick timer, enter ACTIVE state

    while (true) {
        game_loop_tick();
    }
}

// ─── Core Tick ───────────────────────────────────────────────
void game_loop_tick(void) {
    uint32_t now = time_mgr_now_ms();

    // Phase 1: Poll inputs (non-blocking)
    button_event_t btn = input_poll();
    sensor_context_t ctx = sensor_poll(now);

    // Phase 2: Handle button input (immediate response)
    if (btn.type != BTN_NONE) {
        ui_handle_input(btn);
    }

    // Phase 3: Game tick (runs on timer interval)
    if (now - last_tick_ms >= tick_interval_ms) {
        last_tick_ms = now;
        game_tick(now, &ctx);
    }

    // Phase 4: Render if dirty
    if (ui_needs_redraw()) {
        ui_render();
        display_partial_refresh();
    }

    // Phase 5: Periodic save (every 5 minutes)
    if (now - last_save_ms >= SAVE_INTERVAL_MS) {
        last_save_ms = now;
        persistence_save();
    }

    // Phase 6: Sleep check
    if (game_state == GAME_STATE_SLEEPING) {
        enter_low_power();    // RP2040 dormant mode
    }
}

// ─── Game Tick (1-second interval) ───────────────────────────
void game_tick(uint32_t now, sensor_context_t *ctx) {
    // 1. Update time context
    game_time_t gt = time_mgr_update(now);

    // 2. Decay stats
    stat_decay_tick(&game.stats, &game.modifiers, &gt);

    // 3. Check stat thresholds → fire events
    stat_check_thresholds(&game.stats);

    // 4. Update activity tracker (step count, location)
    activity_update(&game.activity, ctx, &gt);

    // 5. Check activity milestones
    activity_check_milestones(&game.activity, &game.progression);

    // 6. Resolve emotion from stats + sensors + events
    emotion_resolve(&game.emotion, &game.stats, ctx,
                    &game.events, &game.life);

    // 7. Check life stage transitions
    life_stage_check(&game.life, &game.stats, &gt);

    // 8. Update treasure hunt (if active)
    if (game.treasure.state == HUNT_ACTIVE) {
        treasure_update(&game.treasure, ctx);
    }

    // 9. Check for random events (daily hooks)
    random_event_check(&game, &gt);

    // 10. Dialogue trigger check
    dialogue_check_triggers(&game.dialogue, &game.emotion,
                            &game.stats, ctx, &gt);

    // 11. Mark UI dirty if state changed
    if (game.emotion.changed || game.dialogue.pending) {
        ui_mark_dirty();
    }
}
```

---

## 2. Tick Timing

### Multi-Rate Tick Schedule

Not all systems need to run every second. Stagger polling to spread CPU load:

```c
typedef struct {
    uint32_t tick_count;          // Monotonic tick counter (wraps at ~49 days)
    uint32_t tick_interval_ms;    // Base tick: 1000ms
} tick_state_t;

// Poll rates defined as tick divisors
#define TICK_RATE_INPUT       1     // Every tick   (1s)   — button responsiveness
#define TICK_RATE_TOUCH      10     // Every 10s           — touch zone check
#define TICK_RATE_SOUND       1     // Every tick   (1s)   — mic level sampling
#define TICK_RATE_LIGHT      10     // Every 10s           — ambient light
#define TICK_RATE_TEMP       60     // Every 60s           — temperature/humidity
#define TICK_RATE_ACCEL      10     // Every 10s           — read pedometer count
#define TICK_RATE_GPS        10     // Every 10s           — GPS fix (when active)
#define TICK_RATE_STAT_DECAY  1     // Every tick   (1s)   — fractional stat decay
#define TICK_RATE_EMOTION     5     // Every 5s            — emotion re-evaluation
#define TICK_RATE_DIALOGUE   30     // Every 30s           — idle dialogue check
#define TICK_RATE_SAVE      300     // Every 300s  (5min)  — persist to flash

// In sensor_poll():
bool should_poll(uint32_t tick_count, uint32_t rate) {
    return (tick_count % rate) == 0;
}
```

### Why 1-Second Base Tick

- E-ink partial refresh takes ~300ms — cannot update faster than ~3Hz anyway
- Stat decay fractions accumulate over ticks (see [02-stat-system.md](02-stat-system.md))
- Sensor polling at 1s is sufficient for all gameplay purposes
- Button input uses hardware interrupt for immediate response (not tick-dependent)

### Button Input: Interrupt-Driven

Buttons are the exception to tick-based polling. They use GPIO interrupts for instant response:

```c
// GPIO IRQ fires on button press/release
void gpio_irq_handler(uint gpio, uint32_t events) {
    uint32_t now = time_mgr_now_ms();
    button_raw_event_t raw = { .gpio = gpio, .edge = events, .timestamp = now };
    ring_buffer_push(&button_queue, &raw);
}

// input_poll() processes the queue each tick
button_event_t input_poll(void) {
    button_raw_event_t raw;
    if (!ring_buffer_pop(&button_queue, &raw)) {
        return (button_event_t){ .type = BTN_NONE };
    }
    return input_classify(raw);  // debounce, short/long/double detection
}
```

---

## 3. Game States

```c
typedef enum {
    GAME_STATE_BOOT,        // Hardware init, loading save
    GAME_STATE_ACTIVE,      // Normal gameplay, full tick processing
    GAME_STATE_MENU,        // User in menu — stats still decay but no dialogue
    GAME_STATE_SLEEPING,    // Dilder asleep — low power, minimal processing
    GAME_STATE_HUNT,        // Treasure hunt active — compass display mode
    GAME_STATE_EVENT,       // Special event playing (gift box, evolution, etc.)
    GAME_STATE_DEAD,        // Dilder has died — memorial screen, rebirth option
} game_state_t;
```

### State Transition Diagram

```
                    ┌──────────┐
                    │   BOOT   │
                    └────┬─────┘
                         │ init complete
                         ▼
              ┌──────────────────────┐
              │       ACTIVE         │◄──────────────────┐
              │  (normal gameplay)   │                    │
              └──┬───┬───┬───┬──────┘                    │
                 │   │   │   │                           │
    menu open    │   │   │   │  light < 10 lux           │
    ┌────────────┘   │   │   │  + energy low             │
    ▼                │   │   └──────────┐                │
┌────────┐           │   │             ▼                │
│  MENU  │           │   │      ┌────────────┐          │
│        │───────────┘   │      │  SLEEPING  │──────────┘
│ back   │  menu close   │      │            │  wake trigger:
└────────┘               │      └────────────┘  light/touch/alarm
                         │
         treasure spawn  │   stat event / evolution
         ┌───────────────┘   ┌──────────────────────────┐
         ▼                   ▼                           │
    ┌─────────┐        ┌─────────┐                      │
    │  HUNT   │        │  EVENT  │──────────────────────┘
    │         │────────►│         │  event complete
    └─────────┘ found/ └─────────┘
                cancel
```

### Per-State Processing

```c
void game_tick(uint32_t now, sensor_context_t *ctx) {
    switch (game.state) {

    case GAME_STATE_ACTIVE:
        // Full processing: decay, emotion, dialogue, activity
        stat_decay_tick(...);
        emotion_resolve(...);
        activity_update(...);
        dialogue_check_triggers(...);
        break;

    case GAME_STATE_MENU:
        // Stats still decay (Tamagotchi never pauses)
        // But no dialogue, no random events
        stat_decay_tick(...);
        break;

    case GAME_STATE_SLEEPING:
        // Reduced decay (0.25x normal rate)
        // Only wake triggers processed
        // Energy regenerates
        stat_sleep_tick(...);
        if (sensor_wake_trigger(ctx)) {
            game_state_transition(GAME_STATE_ACTIVE);
            event_fire(EVENT_WAKE_UP, NULL);
        }
        break;

    case GAME_STATE_HUNT:
        // Full stat processing + compass updates
        stat_decay_tick(...);
        treasure_update(...);
        break;

    case GAME_STATE_EVENT:
        // Event animation plays out, then return to ACTIVE
        if (event_animation_done()) {
            game_state_transition(GAME_STATE_ACTIVE);
        }
        break;

    case GAME_STATE_DEAD:
        // No stat processing. Wait for rebirth input.
        break;
    }
}
```

---

## 4. Sleep / Wake Cycle

### Sleep Entry

```c
void sleep_check(sensor_context_t *ctx, game_time_t *gt) {
    bool dark = ctx->light.lux < SLEEP_LUX_THRESHOLD;      // < 10 lux
    bool tired = game.stats.energy < SLEEP_ENERGY_THRESHOLD; // < 20
    bool late = gt->hour >= 22 || gt->hour < 6;             // 10pm - 6am

    // Auto-sleep: dark AND (tired OR late)
    if (dark && (tired || late) && game.state == GAME_STATE_ACTIVE) {
        // Show drowsy animation first
        emotion_force(EMOTION_TIRED, 30);  // 30-second dwell
        // After dwell, transition to sleep
        schedule_transition(GAME_STATE_SLEEPING, 30000);
    }
}
```

### Sleep Mode Processing

```c
void stat_sleep_tick(stats_t *stats, stat_modifiers_t *mods) {
    // Energy regenerates during sleep
    stats->energy += ENERGY_REGEN_PER_TICK;  // +1 per 30s → full in ~50 min
    clamp(&stats->energy, 0, 100);

    // Other stats decay at 0.25x normal rate
    stat_apply_decay(stats, mods, 0.25f);

    // Track sleep quality
    game.life.sleep_quality += (stats->energy > 50) ? 1 : 0;
}
```

### Wake Triggers

```c
bool sensor_wake_trigger(sensor_context_t *ctx) {
    // Bright light (curtains opened, lamp on)
    if (ctx->light.delta_lux > 300) return true;

    // Touch (user picks up device)
    if (ctx->touch.any_zone_active) return true;

    // Loud noise
    if (ctx->mic.level > MIC_YELL_THRESHOLD) return true;

    // Significant motion (picked up)
    if (ctx->accel.picked_up) return true;

    // Alarm time (if energy is full)
    if (game.stats.energy >= 95) return true;

    return false;
}
```

### Low Power Implementation

```c
void enter_low_power(void) {
    // Disable non-essential peripherals
    sensor_set_duty_cycle(DUTY_SLEEP);   // Light sensor only, every 60s
    // Display shows sleeping animation (static, no refresh needed)
    // RP2040 enters light sleep (WFI) between tick intervals
    // Wake on: GPIO interrupt (button/touch) OR RTC alarm
    __wfi();  // Wait for interrupt
}
```

---

## 5. Event System

### Event Types

```c
typedef enum {
    // Stat events
    EVENT_STAT_CRITICAL,        // A primary stat dropped below critical threshold
    EVENT_STAT_ZERO,            // A stat hit 0
    EVENT_STAT_RECOVERED,       // A stat recovered from critical
    EVENT_ALL_STATS_BALANCED,   // All primary stats 40-80

    // Care events
    EVENT_FED,                  // User fed Dilder
    EVENT_PETTED,               // User petted (touch sensor)
    EVENT_CLEANED,              // User cleaned
    EVENT_PLAYED,               // Mini-game completed
    EVENT_SCOLDED,              // User scolded (button or yell)
    EVENT_MEDICINE,             // Medicine administered

    // Sensor events
    EVENT_LOUD_NOISE,           // Mic spike above threshold
    EVENT_TALKING,              // Sustained moderate mic input
    EVENT_SINGING,              // Rhythmic mic pattern detected
    EVENT_SILENCE_LONG,         // No mic input for 30+ min
    EVENT_TOUCH_SUSTAINED,      // 5+ second hold on touch zone
    EVENT_SHAKEN,               // High-frequency accelerometer
    EVENT_DROPPED,              // Free-fall detected
    EVENT_PICKED_UP,            // Orientation change from resting
    EVENT_TEMPERATURE_EXTREME,  // Too hot or too cold

    // Activity events
    EVENT_STEP_MILESTONE,       // Daily step tier reached
    EVENT_NEW_LOCATION,         // New WiFi fingerprint
    EVENT_HOME_ARRIVED,         // Home WiFi detected
    EVENT_HOME_LEFT,            // Home WiFi lost

    // Progression events
    EVENT_XP_GAINED,            // Bond XP added
    EVENT_BOND_LEVEL_UP,        // New bond level reached
    EVENT_ACHIEVEMENT_UNLOCK,   // Achievement earned
    EVENT_DECOR_UNLOCK,         // New cosmetic available

    // Life events
    EVENT_STAGE_TRANSITION,     // Life stage changed
    EVENT_EVOLUTION,            // Adult form determined
    EVENT_MISBEHAVIOR,          // Discipline window opened
    EVENT_WAKE_UP,              // Dilder woke up
    EVENT_SLEEP,                // Dilder fell asleep

    // Treasure events
    EVENT_TREASURE_SPAWNED,     // New treasure appeared
    EVENT_TREASURE_FOUND,       // User collected treasure
    EVENT_TREASURE_EXPIRED,     // Uncollected treasure timed out

    // System
    EVENT_DAY_CHANGE,           // Midnight rollover
    EVENT_STREAK_UPDATE,        // Daily streak changed
    EVENT_RANDOM_EVENT,         // Random daily event triggered

    EVENT_COUNT                 // Total event types (for array sizing)
} event_type_t;
```

### Event Bus Implementation

```c
#define MAX_LISTENERS_PER_EVENT 4
#define EVENT_RING_SIZE 16

typedef struct {
    uint8_t stat_id;          // Which stat (for stat events)
    int16_t value;            // Relevant value
    uint32_t timestamp;       // When it happened
} event_data_t;

typedef void (*event_handler_t)(event_type_t type, const event_data_t *data);

// Registration (called during init)
void event_listen(event_type_t type, event_handler_t handler);

// Firing (called by any module)
void event_fire(event_type_t type, const event_data_t *data);

// Recent event ring buffer (for emotion engine context)
typedef struct {
    event_type_t type;
    uint32_t     timestamp;
} event_record_t;

event_record_t recent_events[EVENT_RING_SIZE];
uint8_t        recent_events_head;
```

### Event Dispatch (synchronous, immediate)

```c
static event_handler_t listeners[EVENT_COUNT][MAX_LISTENERS_PER_EVENT];

void event_fire(event_type_t type, const event_data_t *data) {
    // Log to recent events ring
    recent_events[recent_events_head] = (event_record_t){
        .type = type,
        .timestamp = time_mgr_now_ms()
    };
    recent_events_head = (recent_events_head + 1) % EVENT_RING_SIZE;

    // Dispatch to listeners
    for (int i = 0; i < MAX_LISTENERS_PER_EVENT; i++) {
        if (listeners[type][i]) {
            listeners[type][i](type, data);
        }
    }
}
```

### Who Listens to What

```
EVENT_STAT_CRITICAL     → emotion_engine, dialogue, ui
EVENT_FED               → progression (XP), emotion_engine, dialogue
EVENT_PETTED            → progression (XP), emotion_engine, stat_system (+happiness)
EVENT_STEP_MILESTONE    → progression (XP), dialogue, decor (unlock check)
EVENT_NEW_LOCATION      → progression (XP), dialogue, treasure (spawn chance)
EVENT_STAGE_TRANSITION  → dialogue (vocabulary change), decor (slot unlock),
                          progression (guaranteed treasure), ui (evolution anim)
EVENT_MISBEHAVIOR       → ui (show scold prompt), life_stages (discipline window)
EVENT_DAY_CHANGE        → activity (reset daily counters), progression (streak check)
EVENT_WAKE_UP           → dialogue (morning greeting), stat_system (overnight summary)
```

---

## 6. Initialization Sequence

```c
void hardware_init(void) {
    stdio_usb_init();         // USB serial for debug
    rtc_init();               // Hardware RTC
    i2c_init(I2C_PORT, 400000);  // I2C @ 400kHz
    adc_init();               // ADC for microphone
    gpio_init_buttons();      // Button GPIOs with pull-ups + IRQ
}

void game_loop_init(void) {
    // 1. Load saved data (or create new game)
    save_data_t save;
    if (persistence_load(&save)) {
        game_restore_from_save(&save);
        // Calculate elapsed time since last save
        uint32_t elapsed_s = time_mgr_elapsed_since(save.timestamp);
        // Apply offline stat decay (capped at 8 hours)
        stat_apply_offline_decay(&game.stats, elapsed_s);
    } else {
        game_new();  // Fresh egg state
    }

    // 2. Register event listeners
    event_listen(EVENT_STAT_CRITICAL,   emotion_on_stat_critical);
    event_listen(EVENT_FED,             progression_on_care_action);
    event_listen(EVENT_PETTED,          progression_on_care_action);
    event_listen(EVENT_STEP_MILESTONE,  progression_on_step_milestone);
    event_listen(EVENT_STAGE_TRANSITION, dialogue_on_stage_change);
    event_listen(EVENT_DAY_CHANGE,      activity_on_day_change);
    event_listen(EVENT_WAKE_UP,         dialogue_on_wake);
    // ... (all listener registrations)

    // 3. Initial sensor read
    sensor_context_t ctx = sensor_poll_all();

    // 4. Determine initial state
    if (ctx.light.lux < SLEEP_LUX_THRESHOLD && game.stats.energy < 30) {
        game.state = GAME_STATE_SLEEPING;
    } else {
        game.state = GAME_STATE_ACTIVE;
        event_fire(EVENT_WAKE_UP, NULL);
    }

    // 5. Initial render
    ui_mark_dirty();
    last_tick_ms = time_mgr_now_ms();
    last_save_ms = last_tick_ms;
}
```

### New Game State

```c
void game_new(void) {
    game.state = GAME_STATE_EVENT;  // Egg hatching event

    game.stats = (stats_t){
        .hunger    = 50,
        .happiness = 50,
        .energy    = 100,
        .hygiene   = 100,
        .health    = 100,
    };

    game.life = (life_state_t){
        .stage          = LIFE_STAGE_EGG,
        .age_seconds    = 0,
        .hatch_progress = 0,
    };

    game.progression = (progression_t){
        .bond_xp    = 0,
        .bond_level = BOND_STRANGER,
    };

    game.emotion = (emotion_state_t){
        .current = EMOTION_NORMAL,
        .weight  = 1.0f,
    };

    // All other fields zero-initialized
    memset(&game.activity, 0, sizeof(activity_t));
    memset(&game.treasure, 0, sizeof(treasure_state_t));
    memset(&game.decor, 0, sizeof(decor_state_t));
}
```

---

*Next: [02-stat-system.md](02-stat-system.md) — Stat data structures, decay functions, and modifier interfaces.*