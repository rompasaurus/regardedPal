# Input, Menu & UI

> Button handling, debounce, menu state machine, screen composition, and rendering pipeline.

---

## Table of Contents

1. [Button Input System](#1-button-input-system)
2. [Menu State Machine](#2-menu-state-machine)
3. [Screen Composition](#3-screen-composition)
4. [Rendering Pipeline](#4-rendering-pipeline)
5. [Screen Types](#5-screen-types)

---

## 1. Button Input System

### Hardware Layout

```
┌─────────────────────────────────────┐
│          Dilder Device              │
│                                     │
│    [UP]                             │
│                                     │
│  [BACK]  [SELECT]  [ACTION]         │
│                                     │
│    [DOWN]                           │
│                                     │
└─────────────────────────────────────┘

GPIO Assignment (from keyboard-to-pico-input.md):
  SELECT  → GP2
  BACK    → GP3
  UP      → GP4
  DOWN    → GP5
  ACTION  → GP6
```

### Input Classification

```c
typedef enum {
    BTN_NONE,
    BTN_SELECT,
    BTN_BACK,
    BTN_UP,
    BTN_DOWN,
    BTN_ACTION,
} button_id_t;

typedef enum {
    PRESS_NONE,
    PRESS_SHORT,         // < 500ms
    PRESS_LONG,          // > 2000ms
    PRESS_DOUBLE,        // Two short presses within 300ms
} press_type_t;

typedef struct {
    button_id_t id;
    press_type_t type;
    uint32_t timestamp;
} button_event_t;

// ─── Debounce & Classification ───────────────────────────────

#define DEBOUNCE_MS        30     // Ignore bounces within 30ms
#define LONG_PRESS_MS    2000     // Hold for 2s = long press
#define DOUBLE_PRESS_MS   300     // Two presses within 300ms

typedef struct {
    uint32_t press_start_ms;     // When button was first pressed
    uint32_t release_ms;         // When button was released
    bool     is_pressed;         // Current physical state
    bool     long_fired;         // Long press already dispatched
    uint8_t  press_count;        // For double-press detection
} button_state_t;

static button_state_t btn_states[5];  // One per button

button_event_t input_classify(button_raw_event_t raw) {
    button_id_t id = gpio_to_button_id(raw.gpio);
    button_state_t *bs = &btn_states[id];
    uint32_t now = raw.timestamp;

    button_event_t evt = { .id = id, .type = PRESS_NONE, .timestamp = now };

    if (raw.edge == GPIO_EDGE_FALL) {  // Button pressed (active low)
        if (now - bs->release_ms < DEBOUNCE_MS) return evt;  // Bounce
        bs->press_start_ms = now;
        bs->is_pressed = true;
        bs->long_fired = false;
    }
    else if (raw.edge == GPIO_EDGE_RISE) {  // Button released
        if (!bs->is_pressed) return evt;
        bs->is_pressed = false;
        bs->release_ms = now;

        uint32_t duration = now - bs->press_start_ms;

        if (bs->long_fired) {
            // Long press already handled — ignore release
            return evt;
        }

        if (duration < DEBOUNCE_MS) return evt;  // Too short

        // Check for double press
        bs->press_count++;
        if (bs->press_count >= 2 && duration < 500) {
            evt.type = PRESS_DOUBLE;
            bs->press_count = 0;
        } else if (duration >= LONG_PRESS_MS) {
            evt.type = PRESS_LONG;
        } else {
            // Defer: might be first of a double-press
            // (For simplicity, dispatch immediately as SHORT)
            evt.type = PRESS_SHORT;
            // Reset double-press counter after timeout
        }
    }

    return evt;
}

// Long press detection (polled, not edge-triggered)
void input_check_long_press(void) {
    uint32_t now = time_mgr_now_ms();
    for (int i = 0; i < 5; i++) {
        if (btn_states[i].is_pressed && !btn_states[i].long_fired) {
            if (now - btn_states[i].press_start_ms >= LONG_PRESS_MS) {
                btn_states[i].long_fired = true;
                button_event_t evt = {
                    .id = i, .type = PRESS_LONG, .timestamp = now
                };
                ui_handle_input(evt);
            }
        }
    }
}
```

---

## 2. Menu State Machine

### Menu Tree

```c
typedef enum {
    MENU_NONE,             // Not in menu (main pet view)
    MENU_MAIN,             // Top-level menu
    MENU_FEED,             // Feed submenu
    MENU_PLAY,             // Play submenu
    MENU_CARE,             // Care submenu
    MENU_STATS,            // Stats viewer
    MENU_DECOR,            // Decor/cosmetics
    MENU_SETTINGS,         // Settings
} menu_id_t;

typedef struct {
    const char *label;
    menu_id_t   submenu;       // MENU_NONE if leaf action
    care_action_t action;      // Care action to execute (if leaf)
    bool (*visible)(void);     // Visibility gate (e.g., medicine only when sick)
} menu_item_t;

// ─── Menu Definitions ────────────────────────────────────────

static const menu_item_t MAIN_MENU[] = {
    { "Feed",     MENU_FEED,     0,               NULL },
    { "Play",     MENU_PLAY,     0,               NULL },
    { "Care",     MENU_CARE,     0,               NULL },
    { "Stats",    MENU_STATS,    0,               NULL },
    { "Decor",    MENU_DECOR,    0,               gate_decor_unlocked },
    { "Settings", MENU_SETTINGS, 0,               NULL },
};

static const menu_item_t FEED_MENU[] = {
    { "Meal",     MENU_NONE, CARE_FEED_MEAL,   NULL },
    { "Snack",    MENU_NONE, CARE_FEED_SNACK,  NULL },
    { "Treat",    MENU_NONE, CARE_FEED_TREAT,  gate_treat_unlocked },
};

static const menu_item_t PLAY_MENU[] = {
    { "Mini-game", MENU_NONE, CARE_PLAY,    NULL },
    { "Tickle",    MENU_NONE, CARE_TICKLE,  NULL },
};

static const menu_item_t CARE_MENU[] = {
    { "Clean",     MENU_NONE, CARE_CLEAN,        NULL },
    { "Medicine",  MENU_NONE, CARE_MEDICINE,      gate_is_sick },
    { "Light",     MENU_NONE, CARE_SLEEP_TOGGLE,  NULL },
};

// Visibility gates
bool gate_decor_unlocked(void) { return game.progression.bond_level >= BOND_COMPANION; }
bool gate_treat_unlocked(void) { return game.progression.bond_level >= BOND_FRIEND; }
bool gate_is_sick(void)        { return game.stats.primary.health < 30; }
```

### Menu State

```c
typedef struct {
    menu_id_t current_menu;       // Which menu is open
    uint8_t   cursor;             // Selected item index
    uint8_t   scroll_offset;      // For scrolling long menus
    uint8_t   stack_depth;        // How many submenus deep
    menu_id_t stack[4];           // Menu history for back navigation
} menu_state_t;

// ─── Navigation Logic ────────────────────────────────────────

void ui_handle_input(button_event_t btn) {
    switch (game.state) {
        case GAME_STATE_ACTIVE:
            handle_active_input(btn);
            break;
        case GAME_STATE_MENU:
            handle_menu_input(btn);
            break;
        case GAME_STATE_HUNT:
            handle_hunt_input(btn);
            break;
        case GAME_STATE_EVENT:
            handle_event_input(btn);
            break;
        case GAME_STATE_DEAD:
            handle_dead_input(btn);
            break;
        default:
            break;
    }
}

void handle_active_input(button_event_t btn) {
    switch (btn.id) {
        case BTN_SELECT:
            if (btn.type == PRESS_LONG) {
                // Open main menu
                menu_open(MENU_MAIN);
                game_state_transition(GAME_STATE_MENU);
            } else {
                // Short press: interact / dismiss dialogue
                if (game.dialogue.showing) {
                    dialogue_dismiss(&game.dialogue);
                }
            }
            break;

        case BTN_ACTION:
            if (btn.type == PRESS_SHORT) {
                // Context action: feed if hungry, pet otherwise
                care_action_t action = context_action_resolve(&game.stats);
                stat_apply_care(&game.stats, action, false);
            } else if (btn.type == PRESS_LONG) {
                // Scold
                stat_apply_care(&game.stats, CARE_SCOLD,
                                game.life.misbehaving);
            } else if (btn.type == PRESS_DOUBLE) {
                // Quick status view
                ui_show_quick_stats();
            }
            break;

        default:
            break;
    }
}

void handle_menu_input(button_event_t btn) {
    const menu_item_t *items = get_menu_items(menu.current_menu);
    uint8_t count = get_menu_item_count(menu.current_menu);

    switch (btn.id) {
        case BTN_UP:
            if (menu.cursor > 0) menu.cursor--;
            ui_mark_dirty();
            break;

        case BTN_DOWN:
            if (menu.cursor < count - 1) menu.cursor++;
            ui_mark_dirty();
            break;

        case BTN_SELECT:
            if (items[menu.cursor].submenu != MENU_NONE) {
                // Enter submenu
                menu.stack[menu.stack_depth++] = menu.current_menu;
                menu.current_menu = items[menu.cursor].submenu;
                menu.cursor = 0;
            } else {
                // Execute action
                stat_apply_care(&game.stats, items[menu.cursor].action, false);
                menu_close();
                game_state_transition(GAME_STATE_ACTIVE);
            }
            ui_mark_dirty();
            break;

        case BTN_BACK:
            if (menu.stack_depth > 0) {
                // Go back one level
                menu.current_menu = menu.stack[--menu.stack_depth];
                menu.cursor = 0;
            } else {
                // Close menu entirely
                menu_close();
                game_state_transition(GAME_STATE_ACTIVE);
            }
            ui_mark_dirty();
            break;

        default:
            break;
    }
}
```

---

## 3. Screen Composition

### Screen Layer Model

The display is composed in layers, bottom to top:

```
Layer 0: Background        (environment/decor background)
Layer 1: Octopus Body      (runtime-rendered pet with emotion)
Layer 2: Decor Overlay      (hat, accessories)
Layer 3: Header Bar         (time, stat icons)
Layer 4: Dialogue Box       (text overlay when dialogue showing)
Layer 5: Menu Overlay       (menu panel when in menu)
Layer 6: Special Screen     (full-screen: stats, compass, gift box)
```

```c
typedef enum {
    SCREEN_PET,            // Normal: pet view with header + optional dialogue
    SCREEN_MENU,           // Menu overlay on pet view
    SCREEN_STATS,          // Full stats display
    SCREEN_STEPS,          // Step counter / progress bars
    SCREEN_COMPASS,        // Treasure hunt compass
    SCREEN_GIFT,           // Gift box opening animation
    SCREEN_EVOLUTION,      // Evolution reveal animation
    SCREEN_WEEKLY_SUMMARY, // Weekly report
    SCREEN_ACHIEVEMENT,    // Achievement unlocked notification
    SCREEN_MEMORIAL,       // Death/rebirth screen
    SCREEN_EGG,            // Egg hatching screen
} screen_id_t;

typedef struct {
    screen_id_t current_screen;
    bool        dirty;              // Needs redraw
    uint32_t    last_refresh_ms;    // Last e-ink refresh timestamp
    uint32_t    min_refresh_ms;     // Minimum time between refreshes (300ms)
} ui_state_t;
```

### Composition

```c
void ui_render(void) {
    if (!ui_state.dirty) return;
    if (time_mgr_now_ms() - ui_state.last_refresh_ms < ui_state.min_refresh_ms) return;

    // Clear buffer
    Paint_Clear(WHITE);

    switch (ui_state.current_screen) {
        case SCREEN_PET:
            render_pet_screen();
            break;
        case SCREEN_MENU:
            render_pet_screen();         // Pet still visible behind menu
            render_menu_overlay();       // Menu panel on right side
            break;
        case SCREEN_STATS:
            render_stats_screen();
            break;
        case SCREEN_STEPS:
            render_steps_screen();
            break;
        case SCREEN_COMPASS:
            render_compass_screen();
            break;
        case SCREEN_GIFT:
            render_gift_screen();
            break;
        case SCREEN_EVOLUTION:
            render_evolution_screen();
            break;
        default:
            render_pet_screen();
            break;
    }

    // Partial refresh (faster than full, avoids flash)
    EPD_2in13_V3_Display_Partial(image_buffer);

    ui_state.dirty = false;
    ui_state.last_refresh_ms = time_mgr_now_ms();
}
```

---

## 4. Rendering Pipeline

### Pet Screen Layout (250 x 122 pixels)

```
┌──────────────────────────────────────────────────┐  y=0
│ 12:34 PM          ♥ ★ ⚡ 🫧 ✚                    │  Header (16px)
├──────────────────────────────────────────────────┤  y=16
│                                                  │
│                                                  │
│              [OCTOPUS BODY]                      │  Pet area
│              (runtime-rendered)                   │  (80px)
│              + equipped decor                    │
│                                                  │
│                                                  │
├──────────────────────────────────────────────────┤  y=96
│ "Good morning! I had the strangest dream..."     │  Dialogue (26px)
│                                                  │
└──────────────────────────────────────────────────┘  y=122
```

```c
#define HEADER_Y       0
#define HEADER_HEIGHT  16
#define PET_Y          16
#define PET_HEIGHT     80
#define DIALOG_Y       96
#define DIALOG_HEIGHT  26
#define SCREEN_W       250
#define SCREEN_H       122

void render_pet_screen(void) {
    // Layer 0: Background (if equipped)
    if (game.decor.equipped[DECOR_SLOT_BACKGROUND] != DECOR_NONE) {
        render_background(game.decor.equipped[DECOR_SLOT_BACKGROUND]);
    }

    // Layer 1: Octopus body
    // Uses existing sassy-octopus renderer — emotion_id selects body shape,
    // eye position, mouth frame, tentacle style
    render_octopus(game.emotion.current, game.life.stage,
                   game.emotion.in_transition ? game.emotion.previous : EMOTION_COUNT);

    // Layer 2: Decor overlays
    if (game.decor.equipped[DECOR_SLOT_HAT] != DECOR_NONE) {
        render_hat(game.decor.equipped[DECOR_SLOT_HAT]);
    }
    if (game.decor.equipped[DECOR_SLOT_ACCESSORY] != DECOR_NONE) {
        render_accessory(game.decor.equipped[DECOR_SLOT_ACCESSORY]);
    }

    // Layer 3: Header bar
    render_header();

    // Layer 4: Dialogue (if showing)
    if (game.dialogue.showing) {
        render_dialogue_box(game.dialogue.current_text);
    }
}

void render_header(void) {
    // Time display
    game_time_t gt = time_mgr_get();
    char time_str[16];
    snprintf(time_str, sizeof(time_str), "%d:%02d %s",
             gt.hour_12, gt.minute, gt.am_pm);
    Paint_DrawString(2, HEADER_Y + 2, time_str, &Font12, WHITE, BLACK);

    // Stat icons (right-aligned)
    // Each icon is 10x10px with fill level indicating stat value
    int x = SCREEN_W - 12;
    render_stat_icon(x,      HEADER_Y + 3, ICON_HEALTH,    game.stats.primary.health);
    render_stat_icon(x - 14, HEADER_Y + 3, ICON_HYGIENE,   game.stats.primary.hygiene);
    render_stat_icon(x - 28, HEADER_Y + 3, ICON_ENERGY,    game.stats.primary.energy);
    render_stat_icon(x - 42, HEADER_Y + 3, ICON_HAPPINESS, game.stats.primary.happiness);
    render_stat_icon(x - 56, HEADER_Y + 3, ICON_HUNGER,    game.stats.primary.hunger);
}

void render_stat_icon(int x, int y, uint8_t icon_type, int16_t value) {
    // Draw icon outline (10x10)
    Paint_DrawRectangle(x, y, x + 10, y + 10, BLACK, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);

    // Fill proportional to stat value
    int fill_height = (value * 8) / 100;  // 0-8 pixels
    Paint_DrawRectangle(x + 1, y + 9 - fill_height, x + 9, y + 9,
                        BLACK, DOT_PIXEL_1X1, DRAW_FILL_FULL);

    // Critical: flash/invert when < 20
    if (value < 20) {
        // Invert colors for attention
        Paint_DrawRectangle(x, y, x + 10, y + 10, BLACK, DOT_PIXEL_1X1, DRAW_FILL_FULL);
        Paint_DrawRectangle(x + 1, y + 1, x + 9, y + 9, WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
    }
}
```

### Menu Overlay Layout

```
┌──────────────────────────────────────────────────┐
│ 12:34 PM                          [MENU]         │
├──────────────────────────────────────────────────┤
│                    │ ┌─────────────────────────┐ │
│                    │ │  > Feed                 │ │
│   [PET visible     │ │    Play                 │ │
│    behind menu     │ │    Care                 │ │
│    at 50% width]   │ │    Stats                │ │
│                    │ │    Decor                 │ │
│                    │ │    Settings              │ │
│                    │ └─────────────────────────┘ │
│                                                  │
└──────────────────────────────────────────────────┘
```

```c
#define MENU_X       (SCREEN_W / 2)    // Right half of screen
#define MENU_WIDTH   (SCREEN_W / 2)
#define MENU_ITEM_H  14                // Height per menu item

void render_menu_overlay(void) {
    // White background for menu panel
    Paint_DrawRectangle(MENU_X, HEADER_HEIGHT, SCREEN_W, SCREEN_H,
                        WHITE, DOT_PIXEL_1X1, DRAW_FILL_FULL);
    // Border
    Paint_DrawLine(MENU_X, HEADER_HEIGHT, MENU_X, SCREEN_H,
                   BLACK, DOT_PIXEL_1X1, LINE_STYLE_SOLID);

    const menu_item_t *items = get_menu_items(menu.current_menu);
    uint8_t count = get_menu_item_count(menu.current_menu);

    for (int i = 0; i < count; i++) {
        // Skip hidden items
        if (items[i].visible && !items[i].visible()) continue;

        int y = HEADER_HEIGHT + 4 + (i * MENU_ITEM_H);

        if (i == menu.cursor) {
            // Highlight selected item
            Paint_DrawRectangle(MENU_X + 1, y - 1, SCREEN_W - 1, y + MENU_ITEM_H - 2,
                                BLACK, DOT_PIXEL_1X1, DRAW_FILL_FULL);
            Paint_DrawString(MENU_X + 16, y, items[i].label, &Font12, BLACK, WHITE);
            Paint_DrawString(MENU_X + 4, y, ">", &Font12, BLACK, WHITE);
        } else {
            Paint_DrawString(MENU_X + 16, y, items[i].label, &Font12, WHITE, BLACK);
        }
    }
}
```

---

## 5. Screen Types

### Stats Screen

```c
void render_stats_screen(void) {
    Paint_Clear(WHITE);
    Paint_DrawString(4, 2, "STATS", &Font16, WHITE, BLACK);

    // Stat bars (full width)
    int y = 22;
    render_stat_bar(4, y,      "HUN", game.stats.primary.hunger);    y += 18;
    render_stat_bar(4, y,      "HAP", game.stats.primary.happiness); y += 18;
    render_stat_bar(4, y,      "ENE", game.stats.primary.energy);    y += 18;
    render_stat_bar(4, y,      "HYG", game.stats.primary.hygiene);   y += 18;
    render_stat_bar(4, y,      "HEA", game.stats.primary.health);

    // Bond level and XP on right side
    char bond_str[32];
    snprintf(bond_str, sizeof(bond_str), "Bond: Lv%d", game.progression.bond_level);
    Paint_DrawString(140, 22, bond_str, &Font12, WHITE, BLACK);

    char age_str[32];
    uint32_t days = game.life.age_seconds / 86400;
    snprintf(age_str, sizeof(age_str), "Age: %lud", days);
    Paint_DrawString(140, 38, age_str, &Font12, WHITE, BLACK);
}

void render_stat_bar(int x, int y, const char *label, int16_t value) {
    Paint_DrawString(x, y, label, &Font12, WHITE, BLACK);
    // Bar outline
    int bar_x = x + 30;
    int bar_w = 100;
    Paint_DrawRectangle(bar_x, y, bar_x + bar_w, y + 12,
                        BLACK, DOT_PIXEL_1X1, DRAW_FILL_EMPTY);
    // Fill
    int fill_w = (value * (bar_w - 2)) / 100;
    Paint_DrawRectangle(bar_x + 1, y + 1, bar_x + 1 + fill_w, y + 11,
                        BLACK, DOT_PIXEL_1X1, DRAW_FILL_FULL);
    // Value text
    char val_str[8];
    snprintf(val_str, sizeof(val_str), "%d", value);
    Paint_DrawString(bar_x + bar_w + 4, y, val_str, &Font12, WHITE, BLACK);
}
```

### Steps Screen

```
┌──────────────────────────────────────────────────┐
│  Today's Steps: 6,247                            │
│  ██████████████░░░░░░░░ 8,000 Gold               │
│                                                  │
│  [check] Bronze  (2,000)                         │
│  [check] Silver  (5,000)                         │
│  [    ] Gold    (8,000) - 1,753 to go            │
│  [    ] Platinum (12,000)                        │
│  [    ] Diamond  (20,000)                        │
│                         Streak: 12 days          │
└──────────────────────────────────────────────────┘
```

### Compass Screen (Treasure Hunt)

```
┌──────────────────────────────────────────────────┐
│         N                                        │
│       /   \                                      │
│     W   ^   E          347m                      │
│       \   /                                      │
│         S                                        │
│                                                  │
│  "That way! I can smell something salty!"        │
│                                                  │
│  [SELECT: Collect]        [BACK: Cancel]         │
└──────────────────────────────────────────────────┘
```

---

### UI API Summary

```c
// ─── Public Interface (ui.h) ─────────────────────────────────

// Initialization
void ui_init(void);

// Input handling
void ui_handle_input(button_event_t btn);

// State
void ui_mark_dirty(void);
bool ui_needs_redraw(void);
void ui_set_screen(screen_id_t screen);

// Rendering
void ui_render(void);

// Menu
void menu_open(menu_id_t menu);
void menu_close(void);

// Convenience screens
void ui_show_quick_stats(void);
void ui_show_achievement(const achievement_t *ach);
void ui_show_gift_box(const treasure_reward_t *reward);
```

---

*Next: [06-life-stages-evolution.md](06-life-stages-evolution.md) — Life stage FSM, evolution branching algorithm.*
