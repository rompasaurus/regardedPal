# Progression & Unlocks

> XP system, bond levels, achievement definitions, decor inventory, and unlock gating.

---

## Table of Contents

1. [Data Structures](#1-data-structures)
2. [XP Sources & Bond Leveling](#2-xp-sources--bond-leveling)
3. [Achievement System](#3-achievement-system)
4. [Decor & Cosmetics](#4-decor--cosmetics)
5. [Unlock Gating](#5-unlock-gating)

---

## 1. Data Structures

```c
typedef enum {
    BOND_STRANGER,       // 0     XP  — Basic feeding, minimal dialogue
    BOND_ACQUAINTANCE,   // 100   XP  — Comfort response, more expressions
    BOND_COMPANION,      // 500   XP  — Dialogue options, 1 decor slot
    BOND_FRIEND,         // 1500  XP  — Mini-games, nickname
    BOND_BEST_FRIEND,    // 4000  XP  — Full dialogue, 3 decor slots
    BOND_SOULMATE,       // 10000 XP  — Secret dialogue, all decor, special anims
    BOND_BONDED,         // 25000 XP  — Dilder initiates conversation
    BOND_LEGENDARY,      // 50000 XP  — Everything unlocked, elder wisdom
    BOND_LEVEL_COUNT
} bond_level_t;

static const uint32_t BOND_THRESHOLDS[] = {
    [BOND_STRANGER]     = 0,
    [BOND_ACQUAINTANCE] = 100,
    [BOND_COMPANION]    = 500,
    [BOND_FRIEND]       = 1500,
    [BOND_BEST_FRIEND]  = 4000,
    [BOND_SOULMATE]     = 10000,
    [BOND_BONDED]       = 25000,
    [BOND_LEGENDARY]    = 50000,
};

typedef struct {
    uint32_t     bond_xp;          // Total accumulated XP
    bond_level_t bond_level;       // Current level (derived from XP)
    uint64_t     achievements;     // Bitfield: up to 64 achievements
    uint16_t     decor_unlocked;   // Bitfield: up to 16 decor items
} progression_t;
```

---

## 2. XP Sources & Bond Leveling

### XP Award Table

```c
typedef struct {
    event_type_t trigger;
    uint16_t     xp;
    const char  *description;
} xp_source_t;

static const xp_source_t XP_SOURCES[] = {
    { EVENT_FED,                5,   "Feed when hungry" },
    { EVENT_PETTED,             2,   "Comfort (center button)" },
    { EVENT_PLAYED,            10,   "Play mini-game" },
    { EVENT_CLEANED,            5,   "Clean" },
    { EVENT_MEDICINE,           5,   "Give medicine" },
    { EVENT_TALKING,            3,   "Talk to Dilder (mic)" },
    { EVENT_STEP_MILESTONE,    15,   "Walk 1,000 steps" },
    { EVENT_NEW_LOCATION,      25,   "Visit new location" },
    { EVENT_ALL_STATS_BALANCED,10,   "Maintain all stats >50 for 1hr" },
    { EVENT_TREASURE_FOUND,    30,   "Collect treasure" },
    { EVENT_DAY_CHANGE,        20,   "Survive a full day (no care mistakes)" },
};

void progression_on_event(event_type_t type, const event_data_t *data) {
    for (int i = 0; i < ARRAY_SIZE(XP_SOURCES); i++) {
        if (XP_SOURCES[i].trigger == type) {
            progression_add_xp(&game.progression, XP_SOURCES[i].xp);
            return;
        }
    }
}
```

### Bond Level Calculation

```c
void progression_add_xp(progression_t *prog, uint16_t amount) {
    prog->bond_xp += amount;

    event_fire(EVENT_XP_GAINED, &(event_data_t){ .value = amount });

    // Check for level up
    bond_level_t new_level = prog->bond_level;
    while (new_level < BOND_LEGENDARY &&
           prog->bond_xp >= BOND_THRESHOLDS[new_level + 1]) {
        new_level++;
    }

    if (new_level != prog->bond_level) {
        prog->bond_level = new_level;
        event_fire(EVENT_BOND_LEVEL_UP, &(event_data_t){
            .value = new_level
        });
    }
}

// Progress within current level (for UI progress bar)
float progression_level_progress(const progression_t *prog) {
    if (prog->bond_level >= BOND_LEGENDARY) return 1.0f;

    uint32_t current = prog->bond_xp - BOND_THRESHOLDS[prog->bond_level];
    uint32_t needed = BOND_THRESHOLDS[prog->bond_level + 1]
                    - BOND_THRESHOLDS[prog->bond_level];
    return (float)current / (float)needed;
}
```

---

## 3. Achievement System

### Achievement Definition

```c
typedef enum {
    // Care (0-15)
    ACH_FIRST_MEAL,         // Feed Dilder for the first time
    ACH_PERFECT_DAY,        // No care mistakes for 24 hours
    ACH_WEEK_OF_LOVE,       // 7-day care streak
    ACH_MONTH_OF_DEVOTION,  // 30-day care streak

    // Exploration (16-31)
    ACH_FIRST_STEPS,        // Walk 100 steps
    ACH_NEIGHBORHOOD,       // Visit 5 unique locations
    ACH_CITY_MAPPER,        // Visit 25 unique locations
    ACH_MARATHON,           // 42,195 steps in one day

    // Social (32-39)
    ACH_FIRST_WORDS,        // Talk to Dilder via mic for 10s
    ACH_STORYTELLER,        // 100 cumulative minutes mic activity
    ACH_LOUD_AND_PROUD,     // Yell at Dilder intentionally
    ACH_WHISPER_SECRET,     // Low-volume mic for 30s

    // Environmental (40-47)
    ACH_NIGHT_OWL,          // Keep Dilder awake past midnight
    ACH_EARLY_BIRD,         // Interact before 6 AM
    ACH_WEATHER_FRIEND,     // Rain while carrying Dilder
    ACH_COZY_KEEPER,        // Optimal temp/humidity for 8 hours

    // Mastery (48-55)
    ACH_ALL_EMOTIONS,       // Witness all 16 emotional states
    ACH_DISCIPLINARIAN,     // Reach 100% discipline
    ACH_ZEN_MASTER,         // All stats >60 for 72 hours
    ACH_CHAOS_AGENT,        // Chaotic + Unhinged + Weird in one day

    // Step milestones (56-63)
    ACH_BRONZE_WALKER,      // First Bronze daily target
    ACH_GOLD_WALKER,        // First Gold daily target
    ACH_DIAMOND_WALKER,     // First Diamond daily target (20k steps)
    ACH_WEEK_TITAN,         // 100k steps in one week

    ACH_COUNT               // Must be <= 64 (bitfield limit)
} achievement_id_t;

typedef struct {
    achievement_id_t id;
    const char      *name;
    const char      *description;
    uint16_t         xp_reward;
    uint8_t          decor_reward;   // DECOR_NONE or specific item ID
    bool (*check)(const stats_t *stats, const activity_t *activity,
                  const life_state_t *life, const progression_t *prog);
} achievement_def_t;

static const achievement_def_t ACHIEVEMENTS[] = {
    {
        ACH_FIRST_MEAL, "First Meal",
        "Feed Dilder for the first time",
        10, DECOR_NONE,
        check_first_meal
    },
    {
        ACH_PERFECT_DAY, "Perfect Day",
        "No care mistakes for 24 hours",
        100, DECOR_NONE,
        check_perfect_day
    },
    {
        ACH_WEEK_OF_LOVE, "Week of Love",
        "7-day care streak",
        200, DECOR_HEART_ANIM,
        check_week_streak
    },
    {
        ACH_FIRST_STEPS, "First Steps",
        "Walk 100 steps with Dilder",
        10, DECOR_NONE,
        check_first_steps
    },
    {
        ACH_NEIGHBORHOOD, "Neighborhood Explorer",
        "Visit 5 unique locations",
        50, DECOR_EXPLORER_HAT,
        check_5_locations
    },
    {
        ACH_MARATHON, "Marathon",
        "Walk 42,195 steps in one day",
        500, DECOR_RUNNING_ANIM,
        check_marathon
    },
    {
        ACH_ALL_EMOTIONS, "All Emotions",
        "Witness all 16 emotional states",
        300, DECOR_EMOTION_GALLERY,
        check_all_emotions
    },
    {
        ACH_ZEN_MASTER, "Zen Master",
        "Keep all stats >60 for 72 hours",
        500, DECOR_CHILL_MODE,
        check_zen_master
    },
    // ... remaining achievements follow same pattern
};
```

### Achievement Check (per event)

```c
// Tracking state for complex achievements
typedef struct {
    uint16_t emotions_seen;       // Bitfield: which of 16 emotions witnessed
    uint32_t all_balanced_start;  // Timestamp when all stats became >60
    uint32_t mic_total_seconds;   // Cumulative mic activity
    uint32_t optimal_env_start;   // Timestamp when temp/humidity became optimal
} achievement_tracker_t;

static achievement_tracker_t tracker = {0};

void progression_check_achievements(progression_t *prog,
                                    const stats_t *stats,
                                    const activity_t *activity,
                                    const life_state_t *life) {
    for (int i = 0; i < ACH_COUNT; i++) {
        // Skip already unlocked
        if (prog->achievements & (1ULL << i)) continue;

        // Check condition
        if (ACHIEVEMENTS[i].check(stats, activity, life, prog)) {
            // Unlock!
            prog->achievements |= (1ULL << i);
            progression_add_xp(prog, ACHIEVEMENTS[i].xp_reward);

            if (ACHIEVEMENTS[i].decor_reward != DECOR_NONE) {
                decor_unlock(ACHIEVEMENTS[i].decor_reward);
                event_fire(EVENT_DECOR_UNLOCK, &(event_data_t){
                    .value = ACHIEVEMENTS[i].decor_reward
                });
            }

            event_fire(EVENT_ACHIEVEMENT_UNLOCK, &(event_data_t){
                .value = i
            });
        }
    }
}

// Example check functions
bool check_first_meal(const stats_t *s, const activity_t *a,
                      const life_state_t *l, const progression_t *p) {
    return event_ever_fired(EVENT_FED);
}

bool check_perfect_day(const stats_t *s, const activity_t *a,
                       const life_state_t *l, const progression_t *p) {
    return s->hidden.consecutive_days >= 1 && s->hidden.care_mistakes == 0;
}

bool check_week_streak(const stats_t *s, const activity_t *a,
                       const life_state_t *l, const progression_t *p) {
    return s->hidden.consecutive_days >= 7;
}

bool check_first_steps(const stats_t *s, const activity_t *a,
                       const life_state_t *l, const progression_t *p) {
    return a->lifetime_steps >= 100;
}

bool check_5_locations(const stats_t *s, const activity_t *a,
                       const life_state_t *l, const progression_t *p) {
    return a->unique_locations >= 5;
}

bool check_marathon(const stats_t *s, const activity_t *a,
                    const life_state_t *l, const progression_t *p) {
    return a->today_steps >= 42195;
}

bool check_all_emotions(const stats_t *s, const activity_t *a,
                        const life_state_t *l, const progression_t *p) {
    return tracker.emotions_seen == 0xFFFF;  // All 16 bits set
}

bool check_zen_master(const stats_t *s, const activity_t *a,
                      const life_state_t *l, const progression_t *p) {
    if (!stat_all_balanced(&s->primary)) {
        tracker.all_balanced_start = 0;
        return false;
    }
    if (tracker.all_balanced_start == 0) {
        tracker.all_balanced_start = time_mgr_now_ms();
    }
    return (time_mgr_now_ms() - tracker.all_balanced_start) >= (72 * 3600 * 1000);
}

// Track emotion witnessing
void progression_on_emotion_change(emotion_id_t emotion) {
    tracker.emotions_seen |= (1 << emotion);
}
```

---

## 4. Decor & Cosmetics

```c
typedef enum {
    DECOR_SLOT_HAT,
    DECOR_SLOT_BACKGROUND,
    DECOR_SLOT_ACCESSORY,
    DECOR_SLOT_ANIM_STYLE,
    DECOR_SLOT_COUNT
} decor_slot_t;

typedef enum {
    DECOR_NONE = 0,

    // Hats (1-15)
    DECOR_BOW,
    DECOR_CROWN,
    DECOR_GLASSES,
    DECOR_EXPLORER_HAT,
    DECOR_JESTER_HAT,
    DECOR_CORAL_CROWN,
    DECOR_BIRTHDAY_HAT,
    DECOR_MOON_HAT,

    // Backgrounds (16-31)
    DECOR_BG_OCEAN_FLOOR,
    DECOR_BG_REEF,
    DECOR_BG_DEEP_SEA,
    DECOR_BG_CITY,
    DECOR_BG_COZY_ROOM,
    DECOR_BG_STARRY,

    // Accessories (32-47)
    DECOR_SCARF,
    DECOR_SUNGLASSES,
    DECOR_BOOK,

    // Animation styles (48-63)
    DECOR_ANIM_CALM_SWAY,
    DECOR_ANIM_BOUNCE,
    DECOR_ANIM_LAZY_SLOUCH,
    DECOR_ANIM_REGAL_FLOAT,

    // Special unlocks
    DECOR_HEART_ANIM,
    DECOR_RUNNING_ANIM,
    DECOR_EMOTION_GALLERY,
    DECOR_CHILL_MODE,

    DECOR_COUNT            // Must be <= 64 (bitfield limit)
} decor_id_t;

typedef struct {
    decor_id_t equipped[DECOR_SLOT_COUNT];  // Currently equipped per slot
    uint64_t   unlocked;                     // Bitfield of unlocked items
    uint8_t    slots_available;              // Unlocked slots (1-4, increases with bond)
} decor_state_t;

// Slot availability by bond level
uint8_t decor_available_slots(bond_level_t level) {
    if (level >= BOND_SOULMATE)   return 4;  // All slots
    if (level >= BOND_BEST_FRIEND) return 3;
    if (level >= BOND_COMPANION)  return 1;
    return 0;  // No slots at Stranger/Acquaintance
}

void decor_equip(decor_state_t *state, decor_slot_t slot, decor_id_t item) {
    // Check unlocked
    if (!(state->unlocked & (1ULL << item))) return;
    // Check slot available
    if (slot >= state->slots_available) return;
    // Check item belongs in slot
    if (decor_get_slot(item) != slot) return;

    state->equipped[slot] = item;
    ui_mark_dirty();
}

void decor_unlock(decor_id_t item) {
    game.decor.unlocked |= (1ULL << item);
    event_fire(EVENT_DECOR_UNLOCK, &(event_data_t){ .value = item });
}

decor_slot_t decor_get_slot(decor_id_t item) {
    if (item >= 1  && item <= 15) return DECOR_SLOT_HAT;
    if (item >= 16 && item <= 31) return DECOR_SLOT_BACKGROUND;
    if (item >= 32 && item <= 47) return DECOR_SLOT_ACCESSORY;
    if (item >= 48 && item <= 63) return DECOR_SLOT_ANIM_STYLE;
    return DECOR_SLOT_HAT;  // Fallback
}
```

---

## 5. Unlock Gating

Feature availability controlled by bond level and achievements:

```c
typedef struct {
    const char  *feature;
    bond_level_t min_bond;
    int16_t      min_achievement;  // -1 = no achievement required
} feature_gate_t;

static const feature_gate_t FEATURE_GATES[] = {
    { "Basic feeding",         BOND_STRANGER,     -1 },
    { "Comfort response",      BOND_ACQUAINTANCE, -1 },
    { "Dialogue options",      BOND_COMPANION,    -1 },
    { "First decor slot",      BOND_COMPANION,    -1 },
    { "Mini-games",            BOND_FRIEND,       -1 },
    { "Nickname feature",      BOND_FRIEND,       -1 },
    { "Treat food item",       BOND_FRIEND,       -1 },
    { "Full dialogue tree",    BOND_BEST_FRIEND,  -1 },
    { "3 decor slots",         BOND_BEST_FRIEND,  -1 },
    { "Secret dialogue",       BOND_SOULMATE,     -1 },
    { "All decor + anims",     BOND_SOULMATE,     -1 },
    { "Dilder initiates talk", BOND_BONDED,       -1 },
    { "Elder wisdom mode",     BOND_LEGENDARY,    -1 },
    { "Step counter display",  BOND_STRANGER,     ACH_FIRST_STEPS },
    { "Emotion gallery",       BOND_STRANGER,     ACH_ALL_EMOTIONS },
};

bool feature_unlocked(const char *feature, const progression_t *prog) {
    for (int i = 0; i < ARRAY_SIZE(FEATURE_GATES); i++) {
        if (strcmp(FEATURE_GATES[i].feature, feature) == 0) {
            if (prog->bond_level < FEATURE_GATES[i].min_bond) return false;
            if (FEATURE_GATES[i].min_achievement >= 0 &&
                !(prog->achievements & (1ULL << FEATURE_GATES[i].min_achievement))) {
                return false;
            }
            return true;
        }
    }
    return false;
}
```

---

### Progression API Summary

```c
// ─── Public Interface (progress.h) ───────────────────────────

// XP & Leveling
void progression_add_xp(progression_t *prog, uint16_t amount);
float progression_level_progress(const progression_t *prog);

// Achievements
void progression_check_achievements(progression_t *prog, const stats_t *stats,
                                    const activity_t *activity,
                                    const life_state_t *life);
bool progression_achievement_unlocked(const progression_t *prog, achievement_id_t id);
void progression_on_emotion_change(emotion_id_t emotion);

// Decor
void decor_equip(decor_state_t *state, decor_slot_t slot, decor_id_t item);
void decor_unlock(decor_id_t item);
bool decor_is_unlocked(const decor_state_t *state, decor_id_t item);

// Feature gating
bool feature_unlocked(const char *feature, const progression_t *prog);

// Event handlers
void progression_on_event(event_type_t type, const event_data_t *data);
void progression_on_care_action(event_type_t type, const event_data_t *data);
void progression_on_step_milestone(event_type_t type, const event_data_t *data);
```

---

*Next: [08-dialogue-system.md](08-dialogue-system.md) — Quote selection, context triggers, and intelligence gating.*
