# Stat System

> Data structures, decay mechanics, modifiers, and threshold logic for all pet statistics.

---

## Table of Contents

1. [Data Structures](#1-data-structures)
2. [Stat Decay](#2-stat-decay)
3. [Stat Modification (Care Actions)](#3-stat-modification-care-actions)
4. [Threshold Checks & Events](#4-threshold-checks--events)
5. [Modifier Stack](#5-modifier-stack)
6. [Secondary & Hidden Stats](#6-secondary--hidden-stats)
7. [Offline Decay](#7-offline-decay)

---

## 1. Data Structures

```c
// ─── Primary Stats ───────────────────────────────────────────
typedef struct {
    int16_t hunger;       // 0-100. Food level.
    int16_t happiness;    // 0-100. Emotional wellbeing.
    int16_t energy;       // 0-100. Wakefulness.
    int16_t hygiene;      // 0-100. Cleanliness.
    int16_t health;       // 0-100. Overall health (derived from others).
} primary_stats_t;

// ─── Secondary Stats (accumulated over lifetime) ─────────────
typedef struct {
    uint32_t bond_xp;          // Total interaction XP (never decays)
    uint16_t discipline;       // 0-100. Correct scolds / total scold windows
    uint16_t intelligence;     // 0-100. Accumulated from talking/word exposure
    uint16_t fitness;          // 0-100. Accumulated from steps/activity
    uint16_t exploration;      // 0-100. Unique locations visited (scaled)
    uint32_t age_seconds;      // Real time since hatch
    int16_t  weight;           // 50-150 (100 = normal). Feeding affects this.
} secondary_stats_t;

// ─── Hidden Stats (tracking, not displayed to user) ──────────
typedef struct {
    uint16_t care_mistakes;       // Times a critical need went unmet >15 min
    uint16_t consecutive_days;    // Streak of daily interaction
    uint16_t noise_exposure;      // Cumulative loud sound events
    uint16_t night_disturbances;  // Times woken during sleep hours
    uint32_t last_interaction_ms; // Timestamp of last user action
    uint32_t neglect_timer_ms;    // Time since last care when stat is critical
} hidden_stats_t;

// ─── Combined ────────────────────────────────────────────────
typedef struct {
    primary_stats_t   primary;
    secondary_stats_t secondary;
    hidden_stats_t    hidden;
} stats_t;
```

---

## 2. Stat Decay

### Base Decay Rates

From the engagement plan — expressed as points lost per tick at 1-second intervals:

```c
// Base decay: points per 10 minutes (600 ticks)
// Stored as fixed-point: actual_decay_per_tick = base / 600
typedef struct {
    uint16_t hunger_per_600;     // 1 point / 10 min → 1
    uint16_t happiness_per_600;  // 1 point / 15 min → 0.667 (stored as 667)
    uint16_t energy_per_600;     // 1 point / 12 min → 0.833 (stored as 833)
    uint16_t hygiene_per_600;    // 1 point / 30 min → 0.333 (stored as 333)
} decay_rates_t;

// Default rates (multiplied by 1000 for fixed-point precision)
static const decay_rates_t BASE_DECAY = {
    .hunger_per_600    = 1000,  // 1.000 per 600 ticks (10 min)
    .happiness_per_600 =  667,  // 0.667 per 600 ticks (15 min)
    .energy_per_600    =  833,  // 0.833 per 600 ticks (12 min)
    .hygiene_per_600   =  333,  // 0.333 per 600 ticks (30 min)
};
```

### Fractional Accumulator

Since stats are integers but decay is fractional, use an accumulator:

```c
typedef struct {
    uint32_t hunger_accum;     // Fractional decay accumulator (fixed-point x1000)
    uint32_t happiness_accum;
    uint32_t energy_accum;
    uint32_t hygiene_accum;
} decay_accum_t;

static decay_accum_t accum = {0};

void stat_decay_tick(stats_t *stats, const modifier_stack_t *mods,
                     const game_time_t *gt) {
    // Only decay when awake (sleep uses separate function)
    if (game.state == GAME_STATE_SLEEPING) return;

    // Calculate effective decay rate with all modifiers applied
    float stage_mod   = modifier_get(mods, MOD_LIFE_STAGE);   // e.g., 2.0 for baby
    float bond_mod    = modifier_get(mods, MOD_BOND_LEVEL);   // e.g., 0.95 at high bond
    float env_mod     = modifier_get(mods, MOD_ENVIRONMENT);  // e.g., 0.9 in good temp
    float tod_mod     = modifier_get(mods, MOD_TIME_OF_DAY);  // e.g., 1.2 during active hours
    float activity_mod = modifier_get(mods, MOD_ACTIVITY);    // e.g., 1.3 while walking

    float combined = stage_mod * bond_mod * env_mod * tod_mod;

    // Accumulate fractional decay
    accum.hunger_accum    += (uint32_t)(BASE_DECAY.hunger_per_600 * combined * tod_mod);
    accum.happiness_accum += (uint32_t)(BASE_DECAY.happiness_per_600 * combined);
    accum.energy_accum    += (uint32_t)(BASE_DECAY.energy_per_600 * combined * activity_mod);
    accum.hygiene_accum   += (uint32_t)(BASE_DECAY.hygiene_per_600 * combined);

    // When accumulator reaches 600000 (600 ticks * 1000 precision), subtract 1 point
    #define DECAY_THRESHOLD 600000

    if (accum.hunger_accum >= DECAY_THRESHOLD) {
        stats->primary.hunger -= 1;
        accum.hunger_accum -= DECAY_THRESHOLD;
    }
    if (accum.happiness_accum >= DECAY_THRESHOLD) {
        stats->primary.happiness -= 1;
        accum.happiness_accum -= DECAY_THRESHOLD;
    }
    if (accum.energy_accum >= DECAY_THRESHOLD) {
        stats->primary.energy -= 1;
        accum.energy_accum -= DECAY_THRESHOLD;
    }
    if (accum.hygiene_accum >= DECAY_THRESHOLD) {
        stats->primary.hygiene -= 1;
        accum.hygiene_accum -= DECAY_THRESHOLD;
    }

    // Clamp all stats to [0, 100]
    stat_clamp_all(&stats->primary);

    // Health derived from other stats
    stat_update_health(stats);
}
```

### Health Derivation

Health doesn't decay on its own — it reflects how well other stats are maintained:

```c
void stat_update_health(stats_t *stats) {
    primary_stats_t *p = &stats->primary;

    // Health degrades when other stats are critically low
    int critical_count = 0;
    if (p->hunger    < 20) critical_count++;
    if (p->happiness < 20) critical_count++;
    if (p->energy    < 15) critical_count++;
    if (p->hygiene   < 25) critical_count++;

    if (critical_count >= 3) {
        // Multiple critical stats → health drops
        p->health -= 1;  // -1 per tick when 3+ stats critical
    } else if (critical_count >= 2) {
        // Slow health decay
        static uint8_t health_decay_counter = 0;
        if (++health_decay_counter >= 5) {  // -1 per 5 ticks
            p->health -= 1;
            health_decay_counter = 0;
        }
    } else if (critical_count == 0 && p->hunger > 50 && p->happiness > 50) {
        // All stats healthy → slow health recovery
        static uint8_t health_regen_counter = 0;
        if (++health_regen_counter >= 30) {  // +1 per 30 ticks
            p->health += 1;
            health_regen_counter = 0;
        }
    }

    stat_clamp(&p->health, 0, 100);
}
```

---

## 3. Stat Modification (Care Actions)

```c
typedef enum {
    CARE_FEED_MEAL,     // +30 hunger, +1 weight
    CARE_FEED_SNACK,    // +10 hunger, +15 happiness, +2 weight
    CARE_FEED_TREAT,    // +5 hunger, +25 happiness, +3 weight (rare/unlockable)
    CARE_CLEAN,         // +40 hygiene
    CARE_MEDICINE,      // +20 health (only when sick, health < 30)
    CARE_PET,           // +10 happiness (center button)
    CARE_PLAY,          // +20 happiness, -10 energy, -1 weight
    CARE_TICKLE,        // +5 happiness (quick)
    CARE_SCOLD,         // +25 discipline (if misbehaving), else -10 happiness
    CARE_SLEEP_TOGGLE,  // Manual sleep/wake
} care_action_t;

typedef struct {
    int8_t hunger;
    int8_t happiness;
    int8_t energy;
    int8_t hygiene;
    int8_t health;
    int8_t weight;
    uint8_t bond_xp;
    bool requires_condition;      // e.g., medicine requires sick
    uint16_t cooldown_ticks;      // Prevent spam (0 = no cooldown)
} care_effect_t;

static const care_effect_t CARE_EFFECTS[] = {
    //                     hun  hap  ene  hyg  hea  wgt  xp   cond  cooldown
    [CARE_FEED_MEAL]   = { 30,   0,   0,   0,   0,   1,  5,  false,  30 },
    [CARE_FEED_SNACK]  = { 10,  15,   0,   0,   0,   2,  3,  false,  15 },
    [CARE_FEED_TREAT]  = {  5,  25,   0,   0,   0,   3, 10,  false,  60 },
    [CARE_CLEAN]       = {  0,   0,   0,  40,   0,   0,  5,  false,  60 },
    [CARE_MEDICINE]    = {  0,   0,   0,   0,  20,   0,  5,  true,  120 },
    [CARE_PET]         = {  0,  10,   0,   0,   0,   0,  2,  false,   5 },
    [CARE_PLAY]        = {  0,  20, -10,   0,   0,  -1, 10,  false,  30 },
    [CARE_TICKLE]      = {  0,   5,   0,   0,   0,   0,  1,  false,   3 },
    [CARE_SCOLD]       = {  0,   0,   0,   0,   0,   0,  0,  false,  30 },
};

void stat_apply_care(stats_t *stats, care_action_t action, bool misbehaving) {
    const care_effect_t *fx = &CARE_EFFECTS[action];

    // Check cooldown
    if (care_cooldowns[action] > 0) return;  // Still on cooldown
    care_cooldowns[action] = fx->cooldown_ticks;

    // Check condition (medicine only when sick)
    if (fx->requires_condition && stats->primary.health >= 30) return;

    // Special: scold
    if (action == CARE_SCOLD) {
        if (misbehaving) {
            stats->secondary.discipline += 25;
            clamp(&stats->secondary.discipline, 0, 100);
            event_fire(EVENT_SCOLDED, &(event_data_t){ .value = 1 });  // correct
        } else {
            stats->primary.happiness -= 10;
            stats->secondary.bond_xp = (stats->secondary.bond_xp > 5)
                ? stats->secondary.bond_xp - 5 : 0;
            event_fire(EVENT_SCOLDED, &(event_data_t){ .value = 0 });  // incorrect
        }
        return;
    }

    // Apply effects
    stats->primary.hunger    += fx->hunger;
    stats->primary.happiness += fx->happiness;
    stats->primary.energy    += fx->energy;
    stats->primary.hygiene   += fx->hygiene;
    stats->primary.health    += fx->health;
    stats->secondary.weight  += fx->weight;
    stats->secondary.bond_xp += fx->bond_xp;

    stat_clamp_all(&stats->primary);
    clamp(&stats->secondary.weight, 50, 150);

    // Update hidden stats
    stats->hidden.last_interaction_ms = time_mgr_now_ms();

    // Fire care event
    event_fire(EVENT_FED + (action <= CARE_FEED_TREAT ? 0 : action),
               &(event_data_t){ .value = action });
}
```

---

## 4. Threshold Checks & Events

```c
typedef struct {
    uint8_t stat_id;
    int16_t threshold;
    event_type_t event;
    bool    fired;            // Prevent re-firing until recovered
} threshold_check_t;

static threshold_check_t thresholds[] = {
    { STAT_HUNGER,    20, EVENT_STAT_CRITICAL, false },
    { STAT_HAPPINESS, 20, EVENT_STAT_CRITICAL, false },
    { STAT_ENERGY,    15, EVENT_STAT_CRITICAL, false },
    { STAT_HYGIENE,   25, EVENT_STAT_CRITICAL, false },
    { STAT_HEALTH,    30, EVENT_STAT_CRITICAL, false },
    { STAT_HUNGER,     0, EVENT_STAT_ZERO,     false },
    { STAT_HAPPINESS,  0, EVENT_STAT_ZERO,     false },
    { STAT_ENERGY,     0, EVENT_STAT_ZERO,     false },
};

void stat_check_thresholds(stats_t *stats) {
    for (int i = 0; i < ARRAY_SIZE(thresholds); i++) {
        threshold_check_t *tc = &thresholds[i];
        int16_t value = stat_get_by_id(&stats->primary, tc->stat_id);

        if (value <= tc->threshold && !tc->fired) {
            // Crossed below threshold
            tc->fired = true;
            event_fire(tc->event, &(event_data_t){
                .stat_id = tc->stat_id,
                .value = value
            });

            // Track care mistake if critical for >15 min
            if (tc->event == EVENT_STAT_CRITICAL) {
                stats->hidden.neglect_timer_ms = time_mgr_now_ms();
            }
        } else if (value > tc->threshold + 10 && tc->fired) {
            // Recovered (with hysteresis band of +10 to prevent flicker)
            tc->fired = false;
            event_fire(EVENT_STAT_RECOVERED, &(event_data_t){
                .stat_id = tc->stat_id,
                .value = value
            });
            stats->hidden.neglect_timer_ms = 0;
        }
    }

    // Care mistake tracking: if any critical stat unmet for 15 minutes
    if (stats->hidden.neglect_timer_ms > 0) {
        uint32_t elapsed = time_mgr_now_ms() - stats->hidden.neglect_timer_ms;
        if (elapsed >= 15 * 60 * 1000) {  // 15 minutes
            stats->hidden.care_mistakes++;
            stats->hidden.neglect_timer_ms = time_mgr_now_ms();  // Reset for next window
        }
    }

    // Check if all stats balanced (for EVENT_ALL_STATS_BALANCED)
    primary_stats_t *p = &stats->primary;
    if (p->hunger >= 40 && p->hunger <= 80 &&
        p->happiness >= 40 && p->happiness <= 80 &&
        p->energy >= 40 && p->energy <= 80 &&
        p->hygiene >= 40 && p->hygiene <= 80 &&
        p->health >= 40) {
        static bool balanced_fired = false;
        if (!balanced_fired) {
            balanced_fired = true;
            event_fire(EVENT_ALL_STATS_BALANCED, NULL);
        }
    }
}
```

---

## 5. Modifier Stack

Modifiers are multipliers applied to decay rates. They come from multiple sources and combine multiplicatively.

```c
typedef enum {
    MOD_LIFE_STAGE,     // Baby: 2.0, Hatchling: 1.5, Adult: 0.75, Elder: 0.6
    MOD_BOND_LEVEL,     // Higher bond → slower happiness decay (0.85 at max)
    MOD_ENVIRONMENT,    // Good temp/humidity: 0.9, bad: 1.2
    MOD_TIME_OF_DAY,    // Active hours (8am-8pm): 1.2 hunger, Night: 0.8
    MOD_ACTIVITY,       // Walking: 1.3 energy decay, 0.8 happiness decay
    MOD_STREAK,         // 14+ day streak: 0.9 happiness decay
    MOD_MONTHLY_BONUS,  // Monthly Mover reward: 0.9 all decay for a month
    MOD_COUNT
} modifier_type_t;

typedef struct {
    float values[MOD_COUNT];    // Current modifier values (1.0 = no effect)
} modifier_stack_t;

// Recalculate modifiers (called when source state changes, not every tick)
void modifier_recalculate(modifier_stack_t *mods, const stats_t *stats,
                          const life_state_t *life, const sensor_context_t *ctx,
                          const game_time_t *gt) {
    // Life stage modifier
    static const float STAGE_MODS[] = {
        [LIFE_STAGE_EGG]        = 0.0f,  // No decay in egg
        [LIFE_STAGE_HATCHLING]  = 2.0f,  // Very needy
        [LIFE_STAGE_JUVENILE]   = 1.2f,  // Slightly elevated
        [LIFE_STAGE_ADOLESCENT] = 1.0f,  // Normal
        [LIFE_STAGE_ADULT]      = 0.75f, // Self-sufficient
        [LIFE_STAGE_ELDER]      = 0.6f,  // Slower decay
    };
    mods->values[MOD_LIFE_STAGE] = STAGE_MODS[life->stage];

    // Bond modifier (happiness decay only)
    // Bond level 1-8 maps to 1.0 → 0.85
    float bond_factor = 1.0f - (stats->secondary.bond_xp / 50000.0f) * 0.15f;
    mods->values[MOD_BOND_LEVEL] = fmaxf(bond_factor, 0.85f);

    // Environment modifier (hygiene affected by temp/humidity)
    if (ctx->temperature.celsius >= 18.0f && ctx->temperature.celsius <= 24.0f &&
        ctx->humidity.percent >= 40.0f && ctx->humidity.percent <= 60.0f) {
        mods->values[MOD_ENVIRONMENT] = 0.9f;  // Comfortable
    } else if (ctx->temperature.celsius > 28.0f || ctx->temperature.celsius < 15.0f) {
        mods->values[MOD_ENVIRONMENT] = 1.3f;  // Extreme
    } else {
        mods->values[MOD_ENVIRONMENT] = 1.0f;  // Neutral
    }

    // Time of day (hunger decays faster during active hours)
    if (gt->hour >= 8 && gt->hour < 20) {
        mods->values[MOD_TIME_OF_DAY] = 1.2f;  // Active hours
    } else {
        mods->values[MOD_TIME_OF_DAY] = 0.8f;  // Night
    }

    // Activity modifier
    if (ctx->accel.steps_since_last > 0) {
        mods->values[MOD_ACTIVITY] = 1.3f;  // Walking = more energy drain
    } else {
        mods->values[MOD_ACTIVITY] = 1.0f;
    }
}

// Get combined modifier for a specific stat
float modifier_get(const modifier_stack_t *mods, modifier_type_t type) {
    return mods->values[type];
}
```

---

## 6. Secondary & Hidden Stats

### Intelligence Accumulation

```c
void stat_add_intelligence(stats_t *stats, uint8_t amount) {
    // Intelligence grows from talking, word exposure
    // Gated by life stage (hatchlings learn slower)
    float stage_factor = (game.life.stage >= LIFE_STAGE_JUVENILE) ? 1.0f : 0.5f;
    stats->secondary.intelligence += (uint16_t)(amount * stage_factor);
    clamp(&stats->secondary.intelligence, 0, 100);
}
```

### Fitness Accumulation

```c
void stat_add_fitness(stats_t *stats, uint16_t steps) {
    // Fitness grows logarithmically — diminishing returns on extreme step counts
    // 2000 steps → +1 fitness, 5000 → +3, 10000 → +5
    float fitness_gain = log2f((float)steps / 1000.0f + 1.0f);
    stats->secondary.fitness += (uint16_t)fitness_gain;
    clamp(&stats->secondary.fitness, 0, 100);
}
```

### Weight Management

```c
// Weight affects visual appearance and evolution
// 50-80: underweight → slim octopus
// 80-120: normal range
// 120-150: overweight → Fat emotion trigger

void stat_weight_check(stats_t *stats) {
    if (stats->secondary.weight > 130) {
        // Overfed → Fat mood can trigger
        event_fire(EVENT_STAT_CRITICAL, &(event_data_t){
            .stat_id = STAT_WEIGHT,
            .value = stats->secondary.weight
        });
    }
}
```

### Care Mistake Window

```c
// Called every tick to check if a critical stat has been ignored too long
void stat_check_neglect(stats_t *stats) {
    if (stats->hidden.neglect_timer_ms == 0) return;

    uint32_t now = time_mgr_now_ms();
    uint32_t elapsed = now - stats->hidden.neglect_timer_ms;

    if (elapsed >= CARE_MISTAKE_WINDOW_MS) {  // 15 minutes = 900000ms
        stats->hidden.care_mistakes++;
        stats->hidden.neglect_timer_ms = now;  // Reset window

        // Care mistakes are permanent and affect evolution quality
        // See life-stages-evolution.md for how this is used
    }
}
```

---

## 7. Offline Decay

When the device is powered off and back on, calculate how much stats should have decayed:

```c
void stat_apply_offline_decay(stats_t *stats, uint32_t elapsed_seconds) {
    // Cap offline decay at 8 hours (28800 seconds)
    // Prevents returning to a dead pet after a long power-off
    if (elapsed_seconds > 28800) elapsed_seconds = 28800;

    // Apply decay at reduced rate (0.5x normal — mercy for being off)
    float offline_rate = 0.5f;

    // Hunger: 1 point / 10 min → 6 points / hour
    int hunger_loss = (int)((elapsed_seconds / 600.0f) * offline_rate);
    stats->primary.hunger -= hunger_loss;

    // Happiness: 1 point / 15 min → 4 points / hour
    int happy_loss = (int)((elapsed_seconds / 900.0f) * offline_rate);
    stats->primary.happiness -= happy_loss;

    // Energy: assume sleeping if off → regenerate
    int energy_gain = (int)(elapsed_seconds / 30.0f);  // +1 per 30s
    stats->primary.energy += energy_gain;

    // Hygiene: 1 point / 30 min → 2 points / hour
    int hygiene_loss = (int)((elapsed_seconds / 1800.0f) * offline_rate);
    stats->primary.hygiene -= hygiene_loss;

    stat_clamp_all(&stats->primary);

    // If off for > 3 hours and stats were already low → care mistake
    if (elapsed_seconds > 10800) {
        if (stats->primary.hunger < 20 || stats->primary.happiness < 20) {
            stats->hidden.care_mistakes++;
        }
    }
}
```

---

### Stat API Summary

```c
// ─── Public Interface (stat.h) ───────────────────────────────

// Initialization
void stat_init(stats_t *stats);                     // Set starting values
void stat_restore(stats_t *stats, const save_data_t *save);

// Per-tick processing
void stat_decay_tick(stats_t *stats, const modifier_stack_t *mods,
                     const game_time_t *gt);
void stat_sleep_tick(stats_t *stats);
void stat_check_thresholds(stats_t *stats);
void stat_check_neglect(stats_t *stats);

// Care actions
void stat_apply_care(stats_t *stats, care_action_t action, bool misbehaving);

// Secondary stat updates
void stat_add_intelligence(stats_t *stats, uint8_t amount);
void stat_add_fitness(stats_t *stats, uint16_t daily_steps);
void stat_add_exploration(stats_t *stats);

// Modifiers
void modifier_recalculate(modifier_stack_t *mods, const stats_t *stats,
                          const life_state_t *life, const sensor_context_t *ctx,
                          const game_time_t *gt);

// Offline
void stat_apply_offline_decay(stats_t *stats, uint32_t elapsed_seconds);

// Queries
int16_t stat_get_by_id(const primary_stats_t *stats, uint8_t stat_id);
bool    stat_is_critical(const primary_stats_t *stats, uint8_t stat_id);
bool    stat_all_balanced(const primary_stats_t *stats);
```

---

*Next: [03-emotion-engine.md](03-emotion-engine.md) — Emotion resolution, blending, and sensor-to-emotion mapping.*