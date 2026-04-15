# Dialogue System

> Quote selection engine, context triggers, intelligence gating, recency filtering, and life-stage vocabulary.

---

## Table of Contents

1. [Data Structures](#1-data-structures)
2. [Quote Database Layout](#2-quote-database-layout)
3. [Selection Algorithm](#3-selection-algorithm)
4. [Context Triggers](#4-context-triggers)
5. [Intelligence Gating](#5-intelligence-gating)
6. [Recency Filter](#6-recency-filter)

---

## 1. Data Structures

```c
typedef struct {
    bool         showing;           // Dialogue box currently visible
    bool         pending;           // New dialogue queued for display
    const char  *current_text;      // Pointer to active quote string
    uint16_t     current_id;        // Index of current quote (for recency)
    uint32_t     show_start_ms;     // When dialogue appeared
    uint32_t     display_duration;  // Auto-dismiss after this (10-15s)
    uint8_t      priority;          // Higher priority overwrites lower
} dialogue_state_t;

// Recency tracking — prevent repeating recent quotes
#define QUOTE_HISTORY_SIZE 16

typedef struct {
    uint16_t ids[QUOTE_HISTORY_SIZE];
    uint8_t  head;
    uint8_t  count;
} quote_history_t;

static quote_history_t history = {0};
```

---

## 2. Quote Database Layout

Quotes are organized by two axes: **emotion** and **life stage**. A quote is eligible if it matches the current emotion AND the current life stage.

```c
typedef struct {
    const char  *text;
    uint8_t      emotion_mask;     // Bitfield: which emotions this quote fits
    uint8_t      stage_min;        // Minimum life stage (HATCHLING, JUVENILE, etc.)
    uint8_t      stage_max;        // Maximum life stage
    uint8_t      intelligence_min; // Minimum intelligence stat required
    uint8_t      context_tag;      // Context trigger tag (see Section 4)
} quote_entry_t;

// Context tags for situational quotes
typedef enum {
    CTX_GENERIC,           // No specific context — usable any time
    CTX_MORNING_GREETING,  // First interaction of the day
    CTX_LONG_ABSENCE,      // 8+ hours since last interaction
    CTX_STEP_MILESTONE,    // Step target just reached
    CTX_NEW_LOCATION,      // At a new WiFi fingerprint
    CTX_COLD_TEMP,         // Temperature < 15C
    CTX_HOT_TEMP,          // Temperature > 28C
    CTX_JUST_FED,          // Fed within last 30s
    CTX_OVERFED,           // Weight > 130
    CTX_JUST_PETTED,       // Petted within last 10s
    CTX_YELLED_AT,         // User yelled (mic spike)
    CTX_PERFECT_STATS,     // All stats > 60
    CTX_NIGHT_REFUSE_SLEEP,// Energy > 50 but it's dark
    CTX_MISBEHAVING,       // During discipline window
    CTX_TREASURE_NEAR,     // Treasure hunt in progress
    CTX_COUNT
} context_tag_t;

// ─── Quote Storage ───────────────────────────────────────────
// Quotes are compiled into flash as a const array.
// The existing firmware has 823 quotes — this system extends them
// with metadata for smarter selection.

// Example entries:
static const quote_entry_t QUOTE_DB[] = {
    // ─── Hatchling quotes (simple, one-line) ─────────────────
    { "mama?",
      (1 << EMOTION_NORMAL), LIFE_STAGE_HATCHLING, LIFE_STAGE_HATCHLING, 0, CTX_GENERIC },
    { "hungwy...",
      (1 << EMOTION_HUNGRY), LIFE_STAGE_HATCHLING, LIFE_STAGE_HATCHLING, 0, CTX_GENERIC },
    { "*happy bubbles*",
      (1 << EMOTION_EXCITED), LIFE_STAGE_HATCHLING, LIFE_STAGE_HATCHLING, 0, CTX_GENERIC },
    { "dark... scary...",
      (1 << EMOTION_SAD), LIFE_STAGE_HATCHLING, LIFE_STAGE_HATCHLING, 0, CTX_NIGHT_REFUSE_SLEEP },
    { "warm... nice...",
      (1 << EMOTION_CHILL), LIFE_STAGE_HATCHLING, LIFE_STAGE_HATCHLING, 0, CTX_GENERIC },

    // ─── Juvenile quotes (curious, short phrases) ────────────
    { "What's out there?",
      (1 << EMOTION_NORMAL), LIFE_STAGE_JUVENILE, LIFE_STAGE_JUVENILE, 0, CTX_GENERIC },
    { "Can we go somewhere new?",
      (1 << EMOTION_NORMAL), LIFE_STAGE_JUVENILE, LIFE_STAGE_ELDER, 10, CTX_GENERIC },
    { "Are you my person?",
      (1 << EMOTION_NORMAL), LIFE_STAGE_JUVENILE, LIFE_STAGE_JUVENILE, 0, CTX_GENERIC },

    // ─── Adolescent quotes (opinionated, moody) ─────────────
    { "Whatever.",
      (1 << EMOTION_LAZY) | (1 << EMOTION_ANGRY), LIFE_STAGE_ADOLESCENT, LIFE_STAGE_ADOLESCENT, 0, CTX_GENERIC },
    { "You don't understand me.",
      (1 << EMOTION_SAD) | (1 << EMOTION_ANGRY), LIFE_STAGE_ADOLESCENT, LIFE_STAGE_ADOLESCENT, 20, CTX_GENERIC },
    { "Leave me alone... wait, don't actually leave.",
      (1 << EMOTION_SAD), LIFE_STAGE_ADOLESCENT, LIFE_STAGE_ADOLESCENT, 30, CTX_LONG_ABSENCE },

    // ─── Adult quotes (full personality, context-aware) ──────
    { "Good morning! I had the strangest dream about the Mariana Trench.",
      (1 << EMOTION_NORMAL) | (1 << EMOTION_CHILL), LIFE_STAGE_ADULT, LIFE_STAGE_ELDER, 40, CTX_MORNING_GREETING },
    { "It's been 4 hours since you last checked in. I was starting to worry.",
      (1 << EMOTION_SAD) | (1 << EMOTION_HOMESICK), LIFE_STAGE_ADULT, LIFE_STAGE_ELDER, 40, CTX_LONG_ABSENCE },
    { "This new place smells different. I like it.",
      (1 << EMOTION_EXCITED), LIFE_STAGE_ADULT, LIFE_STAGE_ELDER, 30, CTX_NEW_LOCATION },

    // ─── Elder quotes (wise, reflective) ─────────────────────
    { "I've seen many sunrises through this screen. Each one different.",
      (1 << EMOTION_NOSTALGIC), LIFE_STAGE_ELDER, LIFE_STAGE_ELDER, 60, CTX_MORNING_GREETING },
    { "My tentacles may be slower, but my hearts are fuller.",
      (1 << EMOTION_CHILL), LIFE_STAGE_ELDER, LIFE_STAGE_ELDER, 60, CTX_GENERIC },
    { "Thank you for every step we've walked together.",
      (1 << EMOTION_NOSTALGIC), LIFE_STAGE_ELDER, LIFE_STAGE_ELDER, 50, CTX_STEP_MILESTONE },

    // ─── Context-specific (any stage) ────────────────────────
    { "Oh! You're here! I missed you.",
      0xFF, LIFE_STAGE_JUVENILE, LIFE_STAGE_ELDER, 0, CTX_MORNING_GREETING },
    { "I was starting to think you forgot about me...",
      (1 << EMOTION_SAD), LIFE_STAGE_JUVENILE, LIFE_STAGE_ELDER, 20, CTX_LONG_ABSENCE },
    { "Brrr... can you put me somewhere warmer?",
      (1 << EMOTION_SAD), LIFE_STAGE_JUVENILE, LIFE_STAGE_ELDER, 10, CTX_COLD_TEMP },
    { "I can't... eat... another... *burp*",
      (1 << EMOTION_FAT), LIFE_STAGE_JUVENILE, LIFE_STAGE_ELDER, 0, CTX_OVERFED },
    { "Mmm... keep doing that. Eight arms of relaxation.",
      (1 << EMOTION_CHILL), LIFE_STAGE_ADULT, LIFE_STAGE_ELDER, 30, CTX_JUST_PETTED },
    { "...that was loud. Are you okay?",
      (1 << EMOTION_SAD) | (1 << EMOTION_ANGRY), LIFE_STAGE_JUVENILE, LIFE_STAGE_ELDER, 20, CTX_YELLED_AT },
    { "You know what? Life is good. Really good.",
      (1 << EMOTION_CHILL), LIFE_STAGE_ADULT, LIFE_STAGE_ELDER, 40, CTX_PERFECT_STATS },

    // ... 800+ more quotes following this pattern
};

#define QUOTE_DB_SIZE (sizeof(QUOTE_DB) / sizeof(QUOTE_DB[0]))
```

---

## 3. Selection Algorithm

```c
const char* dialogue_select(emotion_id_t emotion, life_stage_t stage,
                            uint16_t intelligence, context_tag_t context) {
    // Phase 1: Build candidate list
    // (Use indices to avoid copying — RAM is precious)
    uint16_t candidates[32];
    uint8_t  candidate_count = 0;
    uint8_t  context_count = 0;     // How many match the specific context

    for (uint16_t i = 0; i < QUOTE_DB_SIZE && candidate_count < 32; i++) {
        const quote_entry_t *q = &QUOTE_DB[i];

        // Filter: emotion match (or 0xFF = any emotion)
        if (q->emotion_mask != 0xFF && !(q->emotion_mask & (1 << emotion))) continue;

        // Filter: life stage range
        if (stage < q->stage_min || stage > q->stage_max) continue;

        // Filter: intelligence gate
        if (intelligence < q->intelligence_min) continue;

        // Filter: recency (skip recently shown quotes)
        if (quote_in_history(i)) continue;

        candidates[candidate_count++] = i;
        if (q->context_tag == context) context_count++;
    }

    if (candidate_count == 0) return NULL;  // No eligible quotes

    // Phase 2: Prefer context-specific quotes
    // If we have context-matched quotes, pick from those (80% of the time)
    // Otherwise fall back to generic
    uint16_t selected;

    if (context != CTX_GENERIC && context_count > 0) {
        // Filter to context matches
        uint16_t ctx_candidates[16];
        uint8_t ctx_count = 0;
        for (uint8_t i = 0; i < candidate_count && ctx_count < 16; i++) {
            if (QUOTE_DB[candidates[i]].context_tag == context) {
                ctx_candidates[ctx_count++] = candidates[i];
            }
        }

        // 80% chance to use context-specific, 20% generic variety
        uint32_t roll = pseudo_random() % 100;
        if (roll < 80 && ctx_count > 0) {
            selected = ctx_candidates[pseudo_random() % ctx_count];
        } else {
            selected = candidates[pseudo_random() % candidate_count];
        }
    } else {
        selected = candidates[pseudo_random() % candidate_count];
    }

    // Record in history
    quote_history_push(selected);

    return QUOTE_DB[selected].text;
}

// Deterministic pseudo-random (no true RNG needed — variety, not security)
static uint32_t rng_state = 0;
uint32_t pseudo_random(void) {
    rng_state ^= time_mgr_now_ms();
    rng_state = rng_state * 1103515245 + 12345;
    return (rng_state >> 16) & 0x7FFF;
}
```

---

## 4. Context Triggers

The dialogue system checks for trigger conditions each cycle:

```c
void dialogue_check_triggers(dialogue_state_t *state,
                             const emotion_state_t *emotion,
                             const stats_t *stats,
                             const sensor_context_t *ctx,
                             const game_time_t *gt) {
    // Don't interrupt current dialogue
    if (state->showing) {
        // Auto-dismiss after duration
        if (time_mgr_now_ms() - state->show_start_ms > state->display_duration) {
            state->showing = false;
        }
        return;
    }

    // Determine current context
    context_tag_t context = CTX_GENERIC;
    uint8_t priority = 0;

    // Check in priority order (higher overrides lower)

    // Priority 5: Misbehavior
    if (game.life.misbehaving) {
        context = CTX_MISBEHAVING;
        priority = 5;
    }

    // Priority 4: Morning greeting (first interaction of day)
    if (priority < 4) {
        uint32_t idle = time_mgr_now_ms() - stats->hidden.last_interaction_ms;
        if (idle > 8 * 3600 * 1000) {  // 8+ hours
            context = CTX_LONG_ABSENCE;
            priority = 4;
        } else if (gt->hour >= 6 && gt->hour < 10 && !game.daily_greeting_done) {
            context = CTX_MORNING_GREETING;
            priority = 4;
            game.daily_greeting_done = true;
        }
    }

    // Priority 3: Environmental
    if (priority < 3) {
        if (ctx->temperature.celsius < 15.0f) {
            context = CTX_COLD_TEMP;
            priority = 3;
        } else if (ctx->temperature.celsius > 28.0f) {
            context = CTX_HOT_TEMP;
            priority = 3;
        }
    }

    // Priority 2: Recent events
    if (priority < 2) {
        if (event_recent(game.events, EVENT_STEP_MILESTONE, 30000)) {
            context = CTX_STEP_MILESTONE;
            priority = 2;
        } else if (event_recent(game.events, EVENT_NEW_LOCATION, 60000)) {
            context = CTX_NEW_LOCATION;
            priority = 2;
        } else if (event_recent(game.events, EVENT_LOUD_NOISE, 10000)) {
            context = CTX_YELLED_AT;
            priority = 2;
        }
    }

    // Priority 1: Stat-based
    if (priority < 1) {
        if (stat_all_balanced(&stats->primary)) {
            context = CTX_PERFECT_STATS;
            priority = 1;
        } else if (stats->secondary.weight > 130) {
            context = CTX_OVERFED;
            priority = 1;
        }
    }

    // Select and display
    const char *quote = dialogue_select(
        emotion->current,
        game.life.stage,
        stats->secondary.intelligence,
        context
    );

    if (quote) {
        state->current_text = quote;
        state->showing = true;
        state->pending = true;
        state->show_start_ms = time_mgr_now_ms();
        state->display_duration = dialogue_duration(quote);
        state->priority = priority;
        ui_mark_dirty();
    }
}

// Display duration scales with quote length
uint32_t dialogue_duration(const char *text) {
    size_t len = strlen(text);
    // ~3 seconds per 20 characters, minimum 5s, maximum 15s
    uint32_t ms = (len / 20 + 1) * 3000;
    if (ms < 5000) ms = 5000;
    if (ms > 15000) ms = 15000;
    return ms;
}
```

### Forced Dialogue

For immediate responses (care actions, events):

```c
void dialogue_force(dialogue_state_t *state, const char *text,
                    uint8_t priority) {
    // Only override if higher priority
    if (state->showing && priority <= state->priority) return;

    state->current_text = text;
    state->showing = true;
    state->pending = true;
    state->show_start_ms = time_mgr_now_ms();
    state->display_duration = dialogue_duration(text);
    state->priority = priority;
    ui_mark_dirty();
}
```

---

## 5. Intelligence Gating

Dialogue complexity increases as intelligence grows:

```
Intelligence 0-20:   Simple phrases, emotes, sound effects
                     "mama?" / "*bubbles*" / "hungwy..."

Intelligence 20-40:  Full sentences, basic opinions
                     "What's out there?" / "Are you my person?"

Intelligence 40-60:  Multi-sentence, questions back to user
                     "Where are we? Everything's different here!"
                     "This new place smells different. I like it."

Intelligence 60-80:  References past events, humor, preferences
                     "Remember when I was just a hatchling?"
                     "We've walked 3,247 steps. My tentacles are toned."

Intelligence 80-100: Philosophy, complex emotion, behavioral callbacks
                     "Discipline isn't about control. It's about trust."
                     "I've seen many sunrises through this screen."
```

This is enforced by the `intelligence_min` field in each `quote_entry_t`. Higher-intelligence quotes are never shown until the stat is reached, creating a natural progression of dialogue richness.

---

## 6. Recency Filter

Prevents the same quote from appearing twice within the last 16 selections:

```c
void quote_history_push(uint16_t quote_id) {
    history.ids[history.head] = quote_id;
    history.head = (history.head + 1) % QUOTE_HISTORY_SIZE;
    if (history.count < QUOTE_HISTORY_SIZE) history.count++;
}

bool quote_in_history(uint16_t quote_id) {
    for (uint8_t i = 0; i < history.count; i++) {
        if (history.ids[i] == quote_id) return true;
    }
    return false;
}

// History is NOT persisted — resets on reboot.
// This is intentional: re-hearing a favorite quote after a restart feels warm,
// not repetitive. Only within-session repetition feels bad.
```

---

### Dialogue API Summary

```c
// ─── Public Interface (dialog.h) ─────────────────────────────

// Per-tick trigger check
void dialogue_check_triggers(dialogue_state_t *state,
                             const emotion_state_t *emotion,
                             const stats_t *stats,
                             const sensor_context_t *ctx,
                             const game_time_t *gt);

// Force immediate dialogue
void dialogue_force(dialogue_state_t *state, const char *text, uint8_t priority);

// Dismiss current dialogue
void dialogue_dismiss(dialogue_state_t *state);

// Selection (internal, but documented)
const char* dialogue_select(emotion_id_t emotion, life_stage_t stage,
                            uint16_t intelligence, context_tag_t context);

// Event handlers
void dialogue_on_stage_change(event_type_t type, const event_data_t *data);
void dialogue_on_wake(event_type_t type, const event_data_t *data);
void dialogue_on_care_action(event_type_t type, const event_data_t *data);
```

---

*Next: [09-persistence-storage.md](09-persistence-storage.md) — Flash layout, save/load protocol.*
