# Activity Tracker

> Step counting, daily/weekly/monthly targets, location tracking, streak system, and treasure hunts.

---

## Table of Contents

1. [Data Structures](#1-data-structures)
2. [Step Tracking](#2-step-tracking)
3. [Step Targets & Rewards](#3-step-targets--rewards)
4. [Streak System](#4-streak-system)
5. [Location Tracking](#5-location-tracking)
6. [Treasure Hunt System](#6-treasure-hunt-system)

---

## 1. Data Structures

```c
// ─── Step Tiers ──────────────────────────────────────────────
typedef enum {
    STEP_TIER_NONE,
    STEP_TIER_BRONZE,       // 2,000 steps
    STEP_TIER_SILVER,       // 5,000 steps
    STEP_TIER_GOLD,         // 8,000 steps
    STEP_TIER_PLATINUM,     // 12,000 steps
    STEP_TIER_DIAMOND,      // 20,000 steps
    STEP_TIER_COUNT
} step_tier_t;

static const uint32_t DAILY_TARGETS[] = {
    [STEP_TIER_NONE]     = 0,
    [STEP_TIER_BRONZE]   = 2000,
    [STEP_TIER_SILVER]   = 5000,
    [STEP_TIER_GOLD]     = 8000,
    [STEP_TIER_PLATINUM] = 12000,
    [STEP_TIER_DIAMOND]  = 20000,
};

typedef enum {
    WEEK_TIER_NONE,
    WEEK_WALKER,            // 10,000 steps
    WEEK_RUNNER,            // 25,000
    WEEK_WARRIOR,           // 50,000
    WEEK_LEGEND,            // 75,000
    WEEK_TITAN,             // 100,000
    WEEK_TIER_COUNT
} week_tier_t;

static const uint32_t WEEKLY_TARGETS[] = {
    [WEEK_TIER_NONE] = 0,
    [WEEK_WALKER]    = 10000,
    [WEEK_RUNNER]    = 25000,
    [WEEK_WARRIOR]   = 50000,
    [WEEK_LEGEND]    = 75000,
    [WEEK_TITAN]     = 100000,
};

// ─── Activity State ──────────────────────────────────────────
typedef struct {
    // Step counters
    uint32_t     today_steps;           // Resets at midnight
    uint32_t     week_steps;            // Resets Monday
    uint32_t     month_steps;           // Resets 1st of month
    uint32_t     lifetime_steps;        // Never resets
    uint32_t     pedometer_offset;      // Hardware counter at day start

    // Tier tracking
    step_tier_t  today_tier_reached;    // Highest daily tier reached today
    week_tier_t  week_tier_reached;     // Highest weekly tier reached this week

    // Best records
    uint32_t     best_day_steps;        // Personal record single day
    uint8_t      best_day_weekday;      // Which day of week

    // Streak
    uint16_t     daily_streak;          // Consecutive days meeting Bronze
    uint16_t     streak_grace_remaining;// Free misses left (1/week)
    uint8_t      streak_freeze_items;   // Bonus freeze items from treasure
    bool         today_counted;         // Already counted today for streak
    uint8_t      half_days;             // 1000-1999 steps = half day (2 halves = 1)

    // Location
    uint16_t     unique_locations;      // Total unique WiFi fingerprints seen
    uint8_t      today_new_locations;   // New locations discovered today
    bool         at_home;               // Currently at home WiFi
    uint32_t     away_start_ms;         // When we left home

    // Timing
    uint8_t      current_weekday;       // 0=Mon, 6=Sun
    uint8_t      current_month_day;     // 1-31
} activity_t;
```

---

## 2. Step Tracking

### Reading the Hardware Pedometer

```c
void activity_update(activity_t *act, const sensor_context_t *ctx,
                     const game_time_t *gt) {
    // Read steps from accelerometer (hardware pedometer)
    uint32_t hw_steps = ctx->accel.step_count;

    // Calculate new steps since last read
    uint16_t new_steps = ctx->accel.steps_since_last;

    if (new_steps > 0) {
        act->today_steps += new_steps;
        act->week_steps  += new_steps;
        act->month_steps += new_steps;
        act->lifetime_steps += new_steps;

        // Apply step-based happiness modifier to stats
        // (Every 500 steps → small happiness boost)
        static uint32_t steps_since_bonus = 0;
        steps_since_bonus += new_steps;
        if (steps_since_bonus >= 500) {
            steps_since_bonus -= 500;
            game.stats.primary.happiness += 2;
            clamp(&game.stats.primary.happiness, 0, 100);
        }
    }
}
```

### Anti-Cheat: Step Validation

```c
// Reject shake-based fake steps
// Natural walking: 1.5-2.5 Hz step frequency
// Shaking: typically >4 Hz or irregular

bool step_validate(const accel_data_t *accel) {
    // Hardware pedometer in LIS2DH12TR already has built-in validation:
    // - Minimum step threshold
    // - Debounce timer (rejects <200ms between steps)
    // - Activity detection window

    // Additional firmware-side checks:
    if (accel->shaking) return false;  // Reject during detected shaking

    // Speed cap: reject >10 steps/second (running is ~3-4 Hz)
    if (accel->steps_since_last > 0) {
        float step_rate = (float)accel->steps_since_last / 10.0f;  // Per 10s poll
        if (step_rate > 10.0f) return false;  // >10 Hz = not real walking
    }

    return true;
}
```

---

## 3. Step Targets & Rewards

### Daily Target Check

```c
typedef struct {
    uint16_t xp;
    int8_t   happiness;
    bool     cosmetic_chance;    // Random cosmetic unlock
    uint8_t  cosmetic_percent;   // Chance percentage
    bool     guaranteed_cosmetic;
    bool     full_stat_restore;
} step_reward_t;

static const step_reward_t DAILY_REWARDS[] = {
    [STEP_TIER_BRONZE]   = { 10,   5, false,  0, false, false },
    [STEP_TIER_SILVER]   = { 25,  10, false,  0, false, false },
    [STEP_TIER_GOLD]     = { 50,  15, true,  20, false, false },
    [STEP_TIER_PLATINUM] = { 100, 20, false,  0, true,  false },
    [STEP_TIER_DIAMOND]  = { 200, 30, false,  0, true,  true  },
};

void activity_check_milestones(activity_t *act, progression_t *prog) {
    // Check each daily tier (award incrementally — only new tiers)
    for (int tier = STEP_TIER_BRONZE; tier < STEP_TIER_COUNT; tier++) {
        if (act->today_steps >= DAILY_TARGETS[tier] &&
            act->today_tier_reached < tier) {

            act->today_tier_reached = tier;
            const step_reward_t *reward = &DAILY_REWARDS[tier];

            // Award XP
            progression_add_xp(prog, reward->xp);

            // Happiness boost
            game.stats.primary.happiness += reward->happiness;
            clamp(&game.stats.primary.happiness, 0, 100);

            // Cosmetic rewards
            if (reward->guaranteed_cosmetic) {
                decor_unlock_random();
            } else if (reward->cosmetic_chance) {
                if ((pseudo_random() % 100) < reward->cosmetic_percent) {
                    decor_unlock_random();
                }
            }

            // Full stat restore (Diamond tier)
            if (reward->full_stat_restore) {
                game.stats.primary.hunger    = 100;
                game.stats.primary.happiness = 100;
                game.stats.primary.energy    = 100;
                game.stats.primary.hygiene   = 100;
            }

            // Fire milestone event (triggers dialogue, emotion)
            event_fire(EVENT_STEP_MILESTONE, &(event_data_t){
                .value = tier
            });

            // Bonus treasure spawn at 5k and 10k
            if (act->today_steps >= 5000 && act->today_tier_reached == STEP_TIER_SILVER) {
                treasure_spawn_chance(30);  // 30% chance
            }
            if (act->today_steps >= 10000 && act->today_tier_reached == STEP_TIER_PLATINUM) {
                treasure_spawn_chance(50);  // 50% chance
            }
        }
    }

    // Check weekly tiers
    for (int tier = WEEK_WALKER; tier < WEEK_TIER_COUNT; tier++) {
        if (act->week_steps >= WEEKLY_TARGETS[tier] &&
            act->week_tier_reached < tier) {
            act->week_tier_reached = tier;

            // Weekly rewards (larger XP, rare cosmetics)
            static const uint16_t WEEKLY_XP[] = { 0, 50, 150, 400, 800, 1500 };
            progression_add_xp(prog, WEEKLY_XP[tier]);

            if (tier >= WEEK_WARRIOR) {
                decor_unlock_random();
            }
        }
    }

    // Update fitness stat daily
    stat_add_fitness(&game.stats, act->today_steps);
}
```

### Day / Week / Month Reset

```c
void activity_on_day_change(event_type_t type, const event_data_t *data) {
    activity_t *act = &game.activity;

    // Update streak before resetting
    streak_update(act);

    // Record best day
    if (act->today_steps > act->best_day_steps) {
        act->best_day_steps = act->today_steps;
        act->best_day_weekday = act->current_weekday;
    }

    // Reset daily counters
    act->today_steps = 0;
    act->today_tier_reached = STEP_TIER_NONE;
    act->today_counted = false;
    act->today_new_locations = 0;
    act->half_days = 0;

    // Weekly reset (Monday)
    game_time_t gt = time_mgr_get();
    if (gt.weekday == 0) {  // Monday
        act->week_steps = 0;
        act->week_tier_reached = WEEK_TIER_NONE;
        act->streak_grace_remaining = 1;  // Refresh weekly grace day
    }

    // Monthly reset (1st of month)
    if (gt.month_day == 1) {
        act->month_steps = 0;
        // Monthly summary event could be fired here
    }

    // Pedometer offset for today
    act->pedometer_offset = game.sensor.accel.step_count;
}
```

---

## 4. Streak System

```c
void streak_update(activity_t *act) {
    if (act->today_counted) return;  // Already processed today

    bool met_target = (act->today_steps >= DAILY_TARGETS[STEP_TIER_BRONZE]);
    bool half_credit = (act->today_steps >= 1000 && act->today_steps < 2000);

    if (met_target) {
        // Full day — streak continues
        act->daily_streak++;
        act->today_counted = true;
        streak_check_rewards(act);
    } else if (half_credit) {
        // Half day — accumulate
        act->half_days++;
        if (act->half_days >= 2) {
            // Two half days = one streak day
            act->daily_streak++;
            act->half_days = 0;
            act->today_counted = true;
            streak_check_rewards(act);
        }
    } else {
        // Missed day
        if (act->streak_freeze_items > 0) {
            // Use freeze item
            act->streak_freeze_items--;
            act->today_counted = true;
            // Streak preserved
        } else if (act->streak_grace_remaining > 0) {
            // Use weekly grace day
            act->streak_grace_remaining--;
            act->today_counted = true;
            // Streak preserved
        } else {
            // Streak broken
            act->daily_streak = 0;
        }
    }

    event_fire(EVENT_STREAK_UPDATE, &(event_data_t){
        .value = act->daily_streak
    });
}

void streak_check_rewards(activity_t *act) {
    // Streak milestone rewards
    typedef struct {
        uint16_t days;
        uint16_t xp;
        const char *badge;
    } streak_reward_t;

    static const streak_reward_t STREAK_REWARDS[] = {
        {   3,    25, "Getting Started" },
        {   7,   100, "Week Warrior" },
        {  14,   250, NULL },    // + happiness decay -10%
        {  30,   750, "Monthly Master" },
        {  60,  2000, NULL },    // + evolution guarantee
        {  90,  5000, "Legendary Companion" },
        { 365, 25000, "Eternal Bond" },
    };

    for (int i = 0; i < ARRAY_SIZE(STREAK_REWARDS); i++) {
        if (act->daily_streak == STREAK_REWARDS[i].days) {
            progression_add_xp(&game.progression, STREAK_REWARDS[i].xp);

            // Special rewards at certain thresholds
            if (act->daily_streak == 14) {
                // Happiness decay reduced by 10% (applied via modifier stack)
                // Set a flag that modifier_recalculate reads
            }
            if (act->daily_streak == 60) {
                // Evolution guarantee: best path if stats allow
                // Flag stored in life_state_t
            }
        }
    }
}
```

---

## 5. Location Tracking

### WiFi-Based Geolocation

```c
void activity_update_location(activity_t *act, const sensor_context_t *ctx) {
    // WiFi scan results come from CYW43 driver
    // Compare current visible BSSIDs against location database

    // Check home status
    bool was_home = act->at_home;
    act->at_home = location_db_is_home(ctx->wifi.current_bssid);

    if (was_home && !act->at_home) {
        // Left home
        act->away_start_ms = time_mgr_now_ms();
        event_fire(EVENT_HOME_LEFT, NULL);
    } else if (!was_home && act->at_home) {
        // Arrived home
        act->away_start_ms = 0;
        event_fire(EVENT_HOME_ARRIVED, NULL);
    }

    // Check for new locations
    if (ctx->wifi.new_bssid_detected) {
        // Add to location DB (fires EVENT_NEW_LOCATION internally)
        location_db_add(ctx->wifi.current_bssid, ctx->wifi.current_ssid);
        act->unique_locations = location_db_unique_count();
        act->today_new_locations++;

        // Exploration stat
        stat_add_exploration(&game.stats);

        // Treasure spawn chance at new location
        treasure_spawn_chance(30);  // 30% chance
    }
}
```

### WiFi Scanning

```c
// WiFi scan runs periodically (every 5 minutes) using CYW43 driver
// Scans for visible access points and returns BSSID + SSID + signal strength

typedef struct {
    uint8_t  bssid[6];
    char     ssid[33];
    int8_t   rssi;
} wifi_scan_result_t;

void wifi_scan_callback(wifi_scan_result_t *results, uint8_t count) {
    // Find strongest signal (most likely the AP we're connected to / nearest)
    int8_t best_rssi = -127;
    int best_idx = -1;
    for (int i = 0; i < count; i++) {
        if (results[i].rssi > best_rssi) {
            best_rssi = results[i].rssi;
            best_idx = i;
        }
    }

    if (best_idx >= 0) {
        // Update sensor context with strongest AP
        memcpy(game.sensor.wifi.current_bssid, results[best_idx].bssid, 6);
        strncpy(game.sensor.wifi.current_ssid, results[best_idx].ssid, 32);

        // Check if this BSSID is already known
        game.sensor.wifi.new_bssid_detected =
            !location_db_contains(results[best_idx].bssid);
    }
}
```

---

## 6. Treasure Hunt System

### Treasure State

```c
typedef enum {
    HUNT_INACTIVE,       // No active hunt
    HUNT_ACTIVE,         // Hunt in progress — compass mode
    HUNT_FOUND,          // Within collection range
    HUNT_COLLECTING,     // Animation playing
} hunt_state_t;

typedef enum {
    TREASURE_SNACK_CRATE,     // Common (60%) — food item
    TREASURE_COSMETIC_SHELL,  // Uncommon (25%) — random decor
    TREASURE_MEMORY_FRAGMENT, // Rare (10%) — lore + dialogue
    TREASURE_GOLDEN_PEARL,    // Legendary (5%) — major XP
    TREASURE_ELDER_RELIC,     // Mythic (<1%) — unique cosmetic
    TREASURE_TYPE_COUNT
} treasure_type_t;

typedef struct {
    hunt_state_t  state;
    treasure_type_t rarity;
    float         target_lat;
    float         target_lon;
    float         distance_m;        // Current distance to target
    float         bearing_deg;       // Compass bearing to target
    uint32_t      spawn_time_ms;
    uint32_t      expiry_ms;         // 24 hours from spawn
} treasure_state_t;
```

### Spawning

```c
void treasure_spawn_chance(uint8_t percent_chance) {
    // Only one active hunt at a time
    if (game.treasure.state != HUNT_INACTIVE) return;

    // Must have GPS fix
    if (!game.sensor.gps.has_fix) return;

    // Roll
    if ((pseudo_random() % 100) >= percent_chance) return;

    treasure_spawn(&game.treasure, &game.sensor.gps);
}

void treasure_spawn(treasure_state_t *t, const gps_data_t *gps) {
    // Determine rarity
    uint8_t roll = pseudo_random() % 100;
    if      (roll < 60) t->rarity = TREASURE_SNACK_CRATE;
    else if (roll < 85) t->rarity = TREASURE_COSMETIC_SHELL;
    else if (roll < 95) t->rarity = TREASURE_MEMORY_FRAGMENT;
    else if (roll < 99) t->rarity = TREASURE_GOLDEN_PEARL;
    else                 t->rarity = TREASURE_ELDER_RELIC;

    // Bond level gates rarer treasures
    if (t->rarity == TREASURE_COSMETIC_SHELL &&
        game.progression.bond_level < BOND_COMPANION) {
        t->rarity = TREASURE_SNACK_CRATE;
    }
    if (t->rarity == TREASURE_MEMORY_FRAGMENT &&
        game.progression.bond_level < BOND_BEST_FRIEND) {
        t->rarity = TREASURE_COSMETIC_SHELL;
    }

    // Generate target location
    // Random bearing (0-360) and distance (100m-1000m)
    float bearing_rad = (float)(pseudo_random() % 3600) / 10.0f * M_PI / 180.0f;
    float distance_m  = 100.0f + (float)(pseudo_random() % 900);  // 100-1000m

    // Higher fitness = farther, rarer treasures
    if (game.stats.secondary.fitness > 50) {
        distance_m *= 1.5f;  // Up to 1500m
    }

    // Offset from current position
    float dlat = distance_m * cosf(bearing_rad) / 111320.0f;  // m to degrees
    float dlon = distance_m * sinf(bearing_rad) /
                 (111320.0f * cosf(gps->latitude * M_PI / 180.0f));

    t->target_lat = gps->latitude + dlat;
    t->target_lon = gps->longitude + dlon;
    t->state = HUNT_ACTIVE;
    t->spawn_time_ms = time_mgr_now_ms();
    t->expiry_ms = t->spawn_time_ms + (24 * 3600 * 1000);  // 24h expiry

    // Enter hunt mode
    game_state_transition(GAME_STATE_HUNT);
    sensor_set_duty_cycle(&game.sensor_mgr, DUTY_HUNT);  // Enable GPS + mag

    event_fire(EVENT_TREASURE_SPAWNED, &(event_data_t){ .value = t->rarity });
}
```

### Hunt Update (compass + proximity)

```c
void treasure_update(treasure_state_t *t, const sensor_context_t *ctx) {
    if (t->state != HUNT_ACTIVE) return;

    // Check expiry
    if (time_mgr_now_ms() > t->expiry_ms) {
        treasure_expire(t);
        return;
    }

    // Update distance
    if (ctx->gps.has_fix) {
        t->distance_m = gps_distance_m(
            ctx->gps.latitude, ctx->gps.longitude,
            t->target_lat, t->target_lon
        );

        // Update bearing
        t->bearing_deg = gps_bearing(
            ctx->gps.latitude, ctx->gps.longitude,
            t->target_lat, t->target_lon
        );
    }

    // Proximity check
    if (t->distance_m < 15.0f && ctx->gps.hdop < 5.0f) {
        t->state = HUNT_FOUND;
        // UI shows "FOUND! Press [SELECT] to collect"
    }

    ui_mark_dirty();  // Compass display needs refresh
}

// Bearing calculation (for compass arrow)
float gps_bearing(float lat1, float lon1, float lat2, float lon2) {
    float dlon = (lon2 - lon1) * M_PI / 180.0f;
    float lat1r = lat1 * M_PI / 180.0f;
    float lat2r = lat2 * M_PI / 180.0f;

    float x = sinf(dlon) * cosf(lat2r);
    float y = cosf(lat1r) * sinf(lat2r) -
              sinf(lat1r) * cosf(lat2r) * cosf(dlon);

    float bearing = atan2f(x, y) * 180.0f / M_PI;
    return fmodf(bearing + 360.0f, 360.0f);  // Normalize to 0-360
}

// Compass display: bearing relative to device heading
float treasure_compass_arrow(const treasure_state_t *t,
                              const mag_data_t *mag) {
    // Arrow points from device heading toward target
    float relative = t->bearing_deg - mag->heading_deg;
    return fmodf(relative + 360.0f, 360.0f);
}
```

### Collection

```c
void treasure_collect(treasure_state_t *t) {
    if (t->state != HUNT_FOUND) return;

    t->state = HUNT_COLLECTING;

    // Award rewards based on rarity
    switch (t->rarity) {
        case TREASURE_SNACK_CRATE:
            game.stats.primary.hunger += 30;
            game.stats.primary.happiness += 15;
            progression_add_xp(&game.progression, 30);
            break;

        case TREASURE_COSMETIC_SHELL:
            decor_unlock_random();
            progression_add_xp(&game.progression, 50);
            break;

        case TREASURE_MEMORY_FRAGMENT:
            // Unlock lore dialogue set
            progression_add_xp(&game.progression, 100);
            // Special dialogue queued
            break;

        case TREASURE_GOLDEN_PEARL:
            progression_add_xp(&game.progression, 500);
            break;

        case TREASURE_ELDER_RELIC:
            decor_unlock_unique();  // One-of-a-kind item
            progression_add_xp(&game.progression, 1000);
            break;
    }

    event_fire(EVENT_TREASURE_FOUND, &(event_data_t){ .value = t->rarity });

    // Play gift box animation
    ui_set_screen(SCREEN_GIFT);
    game_state_transition(GAME_STATE_EVENT);

    // Disable GPS (power saving)
    sensor_set_duty_cycle(&game.sensor_mgr, DUTY_ACTIVE);
}

void treasure_expire(treasure_state_t *t) {
    t->state = HUNT_INACTIVE;
    event_fire(EVENT_TREASURE_EXPIRED, NULL);
    sensor_set_duty_cycle(&game.sensor_mgr, DUTY_ACTIVE);
    game_state_transition(GAME_STATE_ACTIVE);
}

void treasure_cancel(treasure_state_t *t) {
    t->state = HUNT_INACTIVE;
    sensor_set_duty_cycle(&game.sensor_mgr, DUTY_ACTIVE);
    game_state_transition(GAME_STATE_ACTIVE);
}
```

---

### Activity API Summary

```c
// ─── Public Interface (activity.h) ───────────────────────────

// Per-tick update
void activity_update(activity_t *act, const sensor_context_t *ctx,
                     const game_time_t *gt);
void activity_check_milestones(activity_t *act, progression_t *prog);
void activity_update_location(activity_t *act, const sensor_context_t *ctx);

// Day/week/month transitions
void activity_on_day_change(event_type_t type, const event_data_t *data);

// Streak
void streak_update(activity_t *act);
void streak_check_rewards(activity_t *act);

// Queries
step_tier_t activity_current_tier(const activity_t *act);
uint32_t    activity_steps_to_next_tier(const activity_t *act);
float       activity_tier_progress(const activity_t *act);

// ─── Public Interface (treasure.h) ───────────────────────────

// Spawning
void treasure_spawn_chance(uint8_t percent);
void treasure_spawn(treasure_state_t *t, const gps_data_t *gps);

// Hunt management
void treasure_update(treasure_state_t *t, const sensor_context_t *ctx);
void treasure_collect(treasure_state_t *t);
void treasure_cancel(treasure_state_t *t);
void treasure_expire(treasure_state_t *t);

// Compass
float treasure_compass_arrow(const treasure_state_t *t, const mag_data_t *mag);
```

---

*This concludes the Dilder Gameplay Planning series. See [00-architecture-overview.md](00-architecture-overview.md) for the full module map and how these systems connect.*
