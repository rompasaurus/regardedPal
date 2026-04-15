# Life Stages & Evolution

> Life stage finite state machine, evolution branching algorithm, stage-specific mechanics, and rebirth system.

---

## Table of Contents

1. [Data Structures](#1-data-structures)
2. [Life Stage FSM](#2-life-stage-fsm)
3. [Evolution Branching Algorithm](#3-evolution-branching-algorithm)
4. [Stage-Specific Mechanics](#4-stage-specific-mechanics)
5. [Misbehavior & Discipline Windows](#5-misbehavior--discipline-windows)
6. [Rebirth System](#6-rebirth-system)

---

## 1. Data Structures

```c
typedef enum {
    LIFE_STAGE_EGG,          // 0-1 day. Hatches with warmth and interaction.
    LIFE_STAGE_HATCHLING,    // 1-3 days. Very needy, limited expressions.
    LIFE_STAGE_JUVENILE,     // 3-7 days. Personality forming, first evolution branch.
    LIFE_STAGE_ADOLESCENT,   // 7-14 days. Moody, tests boundaries, full emotion set.
    LIFE_STAGE_ADULT,        // 14-30 days. Stable, full features, final form.
    LIFE_STAGE_ELDER,        // 30+ days. Slower decay, wise, rebirth option.
    LIFE_STAGE_COUNT
} life_stage_t;

typedef enum {
    EVOLUTION_NONE,               // Not yet evolved
    EVOLUTION_DEEP_SEA_SCHOLAR,   // High intelligence + bond + discipline
    EVOLUTION_REEF_GUARDIAN,       // High fitness + exploration
    EVOLUTION_TIDAL_TRICKSTER,    // Low discipline, high happiness
    EVOLUTION_ABYSSAL_HERMIT,     // High discipline, low social
    EVOLUTION_CORAL_DANCER,       // High happiness + music exposure
    EVOLUTION_STORM_KRAKEN,       // Lots of scolding but survived
    EVOLUTION_COUNT
} evolution_form_t;

typedef struct {
    life_stage_t    stage;
    uint32_t        age_seconds;          // Total time since hatch
    uint32_t        stage_start_seconds;  // When current stage began
    evolution_form_t adult_form;          // Determined at adolescent → adult

    // Egg-specific
    uint16_t        hatch_progress;       // 0-100. Touch/warmth fills this.

    // Evolution accumulators (tracked across stages)
    uint16_t        total_care_quality;   // Inverse of care_mistakes (higher = better)
    uint16_t        total_discipline;     // Accumulated discipline across stages
    uint16_t        total_intelligence;   // Accumulated intelligence
    uint16_t        total_fitness;        // Accumulated fitness
    uint16_t        total_exploration;    // Accumulated exploration
    uint16_t        total_happiness_avg;  // Running average happiness
    uint16_t        total_music_exposure; // Singing/music events
    uint16_t        total_scold_count;    // Times scolded (for Storm Kraken)

    // Misbehavior state
    bool            misbehaving;          // Currently in a discipline window
    uint32_t        misbehave_start_ms;   // When window opened
    uint32_t        misbehave_timeout_ms; // Window closes after this
    uint8_t         discipline_windows;   // Windows opened this stage (max 4)

    // Rebirth data
    uint8_t         generation;           // 0 = first life, 1+ = rebirth
    uint32_t        heritage_bond_xp;     // 10% of parent's bond XP
    evolution_form_t heritage_form;       // Parent's adult form (bias trait)
} life_state_t;
```

---

## 2. Life Stage FSM

### Transition Table

```c
typedef struct {
    life_stage_t from;
    life_stage_t to;
    bool (*condition)(const life_state_t *life, const stats_t *stats,
                      const game_time_t *gt);
    void (*on_enter)(life_state_t *life, stats_t *stats);
} stage_transition_t;

static const stage_transition_t TRANSITIONS[] = {
    { LIFE_STAGE_EGG,        LIFE_STAGE_HATCHLING,  cond_egg_hatch,        on_hatch },
    { LIFE_STAGE_HATCHLING,  LIFE_STAGE_JUVENILE,   cond_age_3_days,       on_juvenile },
    { LIFE_STAGE_JUVENILE,   LIFE_STAGE_ADOLESCENT, cond_age_7_days,       on_adolescent },
    { LIFE_STAGE_ADOLESCENT, LIFE_STAGE_ADULT,      cond_age_14_days,      on_adult },
    { LIFE_STAGE_ADULT,      LIFE_STAGE_ELDER,      cond_age_30_days,      on_elder },
};
```

### Transition Conditions

```c
bool cond_egg_hatch(const life_state_t *life, const stats_t *stats,
                    const game_time_t *gt) {
    // Hatch when progress reaches 100 (filled by touch and warmth)
    return life->hatch_progress >= 100;
}

bool cond_age_3_days(const life_state_t *life, const stats_t *stats,
                     const game_time_t *gt) {
    return life->age_seconds >= (3 * 86400);  // 3 days
}

bool cond_age_7_days(const life_state_t *life, const stats_t *stats,
                     const game_time_t *gt) {
    return life->age_seconds >= (7 * 86400);  // 7 days
}

bool cond_age_14_days(const life_state_t *life, const stats_t *stats,
                      const game_time_t *gt) {
    return life->age_seconds >= (14 * 86400);  // 14 days
}

bool cond_age_30_days(const life_state_t *life, const stats_t *stats,
                      const game_time_t *gt) {
    return life->age_seconds >= (30 * 86400);  // 30 days
}
```

### Transition Entry Handlers

```c
void on_hatch(life_state_t *life, stats_t *stats) {
    life->stage_start_seconds = life->age_seconds;
    life->discipline_windows = 0;

    // Fire stage transition event
    event_fire(EVENT_STAGE_TRANSITION, &(event_data_t){
        .value = LIFE_STAGE_HATCHLING
    });

    // Guaranteed treasure on life stage change
    event_fire(EVENT_TREASURE_SPAWNED, NULL);
}

void on_juvenile(life_state_t *life, stats_t *stats) {
    life->stage_start_seconds = life->age_seconds;
    life->discipline_windows = 0;

    // Unlock: basic dialogue, first decor slot
    event_fire(EVENT_STAGE_TRANSITION, &(event_data_t){
        .value = LIFE_STAGE_JUVENILE
    });
}

void on_adolescent(life_state_t *life, stats_t *stats) {
    life->stage_start_seconds = life->age_seconds;
    life->discipline_windows = 0;

    // All 16 emotions now available
    // Unlock: full dialogue, play mini-games
    event_fire(EVENT_STAGE_TRANSITION, &(event_data_t){
        .value = LIFE_STAGE_ADOLESCENT
    });
}

void on_adult(life_state_t *life, stats_t *stats) {
    life->stage_start_seconds = life->age_seconds;

    // DETERMINE EVOLUTION — this is the big moment
    life->adult_form = evolution_calculate(life, stats);

    // Unlock: all decor, advanced animations
    event_fire(EVENT_EVOLUTION, &(event_data_t){
        .value = life->adult_form
    });
    event_fire(EVENT_STAGE_TRANSITION, &(event_data_t){
        .value = LIFE_STAGE_ADULT
    });
}

void on_elder(life_state_t *life, stats_t *stats) {
    life->stage_start_seconds = life->age_seconds;

    // Unique elder-only animations, reflective dialogue
    event_fire(EVENT_STAGE_TRANSITION, &(event_data_t){
        .value = LIFE_STAGE_ELDER
    });
}
```

### Per-Tick Stage Check

```c
void life_stage_check(life_state_t *life, const stats_t *stats,
                      const game_time_t *gt) {
    // Increment age
    life->age_seconds++;

    // Egg special: accumulate hatch progress from touch/warmth
    if (life->stage == LIFE_STAGE_EGG) {
        egg_progress_update(life);
    }

    // Check transition conditions
    for (int i = 0; i < ARRAY_SIZE(TRANSITIONS); i++) {
        if (TRANSITIONS[i].from == life->stage) {
            if (TRANSITIONS[i].condition(life, stats, gt)) {
                // Snapshot evolution accumulators before transitioning
                life_accumulate_stats(life, stats);
                // Transition
                life->stage = TRANSITIONS[i].to;
                TRANSITIONS[i].on_enter(life, stats);
                return;  // Only one transition per tick
            }
        }
    }

    // Accumulate stats every hour for evolution tracking
    static uint32_t last_accumulate = 0;
    if (life->age_seconds - last_accumulate >= 3600) {
        last_accumulate = life->age_seconds;
        life_accumulate_stats(life, stats);
    }

    // Check for death (extreme sustained neglect)
    if (stats->primary.health == 0) {
        life_check_death(life, stats);
    }
}
```

---

## 3. Evolution Branching Algorithm

Deterministic — the player's accumulated care pattern determines the adult form:

```c
evolution_form_t evolution_calculate(const life_state_t *life,
                                    const stats_t *stats) {
    // Score each evolution path
    typedef struct {
        evolution_form_t form;
        int16_t score;
    } evolution_score_t;

    evolution_score_t scores[EVOLUTION_COUNT - 1];  // Exclude NONE

    // ─── Deep-Sea Scholar ────────────────────────────────────
    // High intelligence + high bond + moderate discipline
    scores[0] = (evolution_score_t){ EVOLUTION_DEEP_SEA_SCHOLAR, 0 };
    scores[0].score += stats->secondary.intelligence;          // 0-100
    scores[0].score += (stats->secondary.bond_xp / 500);      // 0-100 scaled
    scores[0].score += life->total_discipline / 2;             // 0-50

    // ─── Reef Guardian ───────────────────────────────────────
    // High fitness + high exploration + balanced stats
    scores[1] = (evolution_score_t){ EVOLUTION_REEF_GUARDIAN, 0 };
    scores[1].score += stats->secondary.fitness;               // 0-100
    scores[1].score += stats->secondary.exploration;           // 0-100
    scores[1].score += life->total_care_quality / 3;           // 0-33 (balanced care)

    // ─── Tidal Trickster ─────────────────────────────────────
    // Low discipline, high happiness, chaotic care
    scores[2] = (evolution_score_t){ EVOLUTION_TIDAL_TRICKSTER, 0 };
    scores[2].score += (100 - life->total_discipline);         // Inverse discipline
    scores[2].score += life->total_happiness_avg;              // 0-100
    scores[2].score += stats->hidden.care_mistakes;            // More mistakes = more chaos

    // ─── Abyssal Hermit ──────────────────────────────────────
    // High discipline, low interaction frequency, self-sufficient
    scores[3] = (evolution_score_t){ EVOLUTION_ABYSSAL_HERMIT, 0 };
    scores[3].score += life->total_discipline;                 // 0-100
    scores[3].score += (100 - (stats->secondary.bond_xp / 500)); // Low social
    scores[3].score += (100 - life->total_happiness_avg) / 2;    // Stoic

    // ─── Coral Dancer ────────────────────────────────────────
    // High happiness + lots of music/singing exposure
    scores[4] = (evolution_score_t){ EVOLUTION_CORAL_DANCER, 0 };
    scores[4].score += life->total_happiness_avg;              // 0-100
    scores[4].score += life->total_music_exposure * 5;         // Weighted heavily
    scores[4].score += stats->secondary.intelligence / 2;      // Artistic side

    // ─── Storm Kraken ────────────────────────────────────────
    // Lots of scolding but survived (high scold count + alive)
    scores[5] = (evolution_score_t){ EVOLUTION_STORM_KRAKEN, 0 };
    scores[5].score += life->total_scold_count * 3;            // Weighted heavily
    scores[5].score += stats->hidden.care_mistakes * 2;        // Rough upbringing
    scores[5].score += (stats->primary.health > 50) ? 50 : 0; // But survived

    // Heritage bias: slight bonus to parent's form
    if (life->generation > 0) {
        for (int i = 0; i < EVOLUTION_COUNT - 1; i++) {
            if (scores[i].form == life->heritage_form) {
                scores[i].score += 20;  // 10% bias toward parent's path
            }
        }
    }

    // Find winner
    evolution_form_t winner = EVOLUTION_DEEP_SEA_SCHOLAR;
    int16_t max_score = 0;
    for (int i = 0; i < EVOLUTION_COUNT - 1; i++) {
        if (scores[i].score > max_score) {
            max_score = scores[i].score;
            winner = scores[i].form;
        }
    }

    return winner;
}
```

### Accumulation Helper

```c
void life_accumulate_stats(life_state_t *life, const stats_t *stats) {
    // Running average of happiness (for evolution scoring)
    static uint32_t happiness_sum = 0;
    static uint32_t happiness_count = 0;
    happiness_sum += stats->primary.happiness;
    happiness_count++;
    life->total_happiness_avg = (uint16_t)(happiness_sum / happiness_count);

    // Care quality: inverse of care mistakes (higher = better)
    life->total_care_quality = (uint16_t)(100 - fminf(stats->hidden.care_mistakes * 5, 100));

    // Copy secondary stats for evolution use
    life->total_discipline = stats->secondary.discipline;
    life->total_intelligence = stats->secondary.intelligence;
    life->total_fitness = stats->secondary.fitness;
    life->total_exploration = stats->secondary.exploration;
}
```

---

## 4. Stage-Specific Mechanics

### Egg Stage

```c
void egg_progress_update(life_state_t *life) {
    // Touch advances hatch progress
    if (game.sensor.touch.any_zone_active) {
        life->hatch_progress += 2;  // ~50 seconds of touch to hatch
    }

    // Warmth (comfortable temperature) adds progress passively
    if (game.sensor.temperature.comfort_zone == COMFORT_GOOD) {
        life->hatch_progress += 1;  // Slow passive progress
    }

    // Talking to the egg
    if (game.sensor.mic.zone >= MIC_MODERATE) {
        life->hatch_progress += 1;
    }

    // Clamp
    if (life->hatch_progress > 100) life->hatch_progress = 100;

    // Visual: egg wobbles more as progress increases
    // UI renders cracks at 25%, 50%, 75%
}
```

### Hatchling Specifics

```c
// Stat decay is 2x normal (set via modifier stack MOD_LIFE_STAGE = 2.0)
// Limited emotion set: normal, hungry, tired, sad, excited
// Cries every 3 minutes if hunger < 30 (special dialogue trigger)
// 4 misbehavior windows during this stage

void hatchling_cry_check(const stats_t *stats, uint32_t now) {
    static uint32_t last_cry = 0;
    if (stats->primary.hunger < 30 && now - last_cry > 180000) {  // 3 min
        last_cry = now;
        dialogue_force("hungwy... *bubbles*");
        event_fire(EVENT_STAT_CRITICAL, &(event_data_t){ .stat_id = STAT_HUNGER });
    }
}
```

### Death Check

```c
void life_check_death(life_state_t *life, const stats_t *stats) {
    // Death only from sustained zero health (3+ days equivalent)
    // No sudden death — always recoverable with intervention
    static uint32_t zero_health_start = 0;

    if (stats->primary.health == 0) {
        if (zero_health_start == 0) {
            zero_health_start = time_mgr_now_ms();
        }

        uint32_t elapsed = time_mgr_now_ms() - zero_health_start;
        if (elapsed > 3 * 24 * 3600 * 1000) {  // 3 days of zero health
            // Death
            game_state_transition(GAME_STATE_DEAD);
            event_fire(EVENT_STAGE_TRANSITION, &(event_data_t){
                .value = -1  // Death signal
            });
        }
    } else {
        zero_health_start = 0;  // Reset if health recovers
    }
}
```

---

## 5. Misbehavior & Discipline Windows

Tamagotchi-inspired discipline system — 4 windows per life stage:

```c
void misbehavior_check(life_state_t *life, const stats_t *stats, uint32_t now) {
    if (life->misbehaving) {
        // Check if window expired (user didn't respond)
        if (now - life->misbehave_start_ms > life->misbehave_timeout_ms) {
            life->misbehaving = false;
            // Missed discipline window — no penalty, but no discipline gained
        }
        return;
    }

    // Only trigger during hatchling, juvenile, adolescent stages
    if (life->stage < LIFE_STAGE_HATCHLING || life->stage > LIFE_STAGE_ADOLESCENT) return;

    // Max 4 windows per stage
    if (life->discipline_windows >= 4) return;

    // Random trigger: ~1% chance per minute when stats aren't critical
    uint32_t tick = now / 60000;  // Per-minute
    bool trigger = ((tick * 2654435761u) % 100) == 0;

    // More likely when happiness is high (being bratty, not needy)
    if (stats->primary.happiness > 60 && stats->primary.hunger > 40) {
        trigger = trigger || ((tick * 2654435761u) % 50) == 0;  // 2% chance
    }

    if (trigger) {
        life->misbehaving = true;
        life->misbehave_start_ms = now;
        life->misbehave_timeout_ms = 60000;  // 1 minute to respond
        life->discipline_windows++;

        event_fire(EVENT_MISBEHAVIOR, NULL);
        // UI shows: "Dilder is being defiant!"
        // User must press ACTION (long press = scold) within window
    }
}

// Called when user scolds during misbehavior
void misbehavior_resolve(life_state_t *life, stats_t *stats, bool scolded) {
    if (!life->misbehaving) return;

    life->misbehaving = false;

    if (scolded) {
        // Correct scold
        stats->secondary.discipline += 25;
        clamp(&stats->secondary.discipline, 0, 100);
        emotion_force(&game.emotion, EMOTION_ANGRY, 5000);
        dialogue_force("Hmph... fine.");
    }
    // If not scolded (user just interacted normally), window just closes
    // No penalty for ignoring misbehavior — just no discipline gained
}
```

---

## 6. Rebirth System

After Elder stage (30+ days), user can choose rebirth:

```c
typedef struct {
    uint32_t         parent_bond_xp;     // Parent's total bond XP
    evolution_form_t parent_form;        // Parent's adult form
    uint8_t          parent_generation;  // Parent's generation number
    uint8_t          inherited_decor_id; // One decor item inherited
} rebirth_data_t;

void rebirth_initiate(life_state_t *life, stats_t *stats,
                      progression_t *prog) {
    // Snapshot parent data
    rebirth_data_t rebirth = {
        .parent_bond_xp    = stats->secondary.bond_xp,
        .parent_form       = life->adult_form,
        .parent_generation = life->generation,
        .inherited_decor_id = decor_select_inheritance(),
    };

    // Create memorial entry
    memorial_t memorial = {
        .generation  = life->generation,
        .adult_form  = life->adult_form,
        .age_days    = life->age_seconds / 86400,
        .bond_level  = prog->bond_level,
        .timestamp   = time_mgr_now_ms(),
    };
    persistence_save_memorial(&memorial);

    // Reset all game state
    game_new();

    // Apply inheritance
    life->generation     = rebirth.parent_generation + 1;
    life->heritage_bond_xp = rebirth.parent_bond_xp / 10;   // 10% carry-over
    life->heritage_form  = rebirth.parent_form;

    stats->secondary.bond_xp = life->heritage_bond_xp;      // Head start

    // Inherited decor already unlocked
    decor_unlock(rebirth.inherited_decor_id);

    // Save immediately
    persistence_save();
}

// Memorial display (viewable from stats menu)
typedef struct {
    uint8_t          generation;
    evolution_form_t adult_form;
    uint16_t         age_days;
    uint8_t          bond_level;
    uint32_t         timestamp;
} memorial_t;

#define MAX_MEMORIALS 8  // Store last 8 generations
```

---

### Life Stage API Summary

```c
// ─── Public Interface (life.h) ───────────────────────────────

// Initialization
void life_init(life_state_t *life);
void life_restore(life_state_t *life, const save_data_t *save);

// Per-tick processing
void life_stage_check(life_state_t *life, const stats_t *stats,
                      const game_time_t *gt);
void misbehavior_check(life_state_t *life, const stats_t *stats, uint32_t now);
void misbehavior_resolve(life_state_t *life, stats_t *stats, bool scolded);

// Evolution
evolution_form_t evolution_calculate(const life_state_t *life, const stats_t *stats);

// Rebirth
void rebirth_initiate(life_state_t *life, stats_t *stats, progression_t *prog);

// Queries
life_stage_t     life_current_stage(const life_state_t *life);
evolution_form_t life_adult_form(const life_state_t *life);
uint32_t         life_age_days(const life_state_t *life);
bool             life_is_misbehaving(const life_state_t *life);
float            life_stage_progress(const life_state_t *life);  // 0.0-1.0 within stage
```

---

*Next: [07-progression-unlocks.md](07-progression-unlocks.md) — XP, bond levels, achievements, and decor.*
