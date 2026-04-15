# Persistence & Storage

> Flash layout, save/load protocol, data packing, wear leveling, and data integrity.

---

## Table of Contents

1. [Storage Strategy](#1-storage-strategy)
2. [Save Data Layout](#2-save-data-layout)
3. [Save / Load Protocol](#3-save--load-protocol)
4. [Data Packing](#4-data-packing)
5. [Wear Leveling & Integrity](#5-wear-leveling--integrity)
6. [Location Database](#6-location-database)

---

## 1. Storage Strategy

### LittleFS on Pico W Flash

The RP2040 has 2MB flash. Firmware uses ~200KB. The remaining ~1.8MB is partitioned:

```
Flash Map (2MB = 2,097,152 bytes)
─────────────────────────────────────────────
0x000000 - 0x030000   Firmware binary (~192 KB)
0x030000 - 0x038000   Quote data (~32 KB)
0x038000 - 0x03C000   Font data (~16 KB)
0x03C000 - 0x040000   Reserved (16 KB)
─────────────────────────────────────────────
0x040000 - 0x200000   LittleFS partition (~1.75 MB)
                       ├── save.dat       (~512 bytes)
                       ├── save.bak       (~512 bytes, backup)
                       ├── locations.dat  (~8 KB, WiFi fingerprints)
                       ├── memorials.dat  (~256 bytes, rebirth history)
                       └── (free space for future use)
─────────────────────────────────────────────
```

### Why LittleFS

- Designed for flash with limited write cycles (~100,000 per sector on Pico W)
- Built-in wear leveling (spreads writes across sectors)
- Power-loss resilient (copy-on-write with atomic pointer update)
- Small footprint (~4KB RAM overhead)
- Well-supported on RP2040 via `pico-littlefs` library

### Save Frequency

- **Periodic save**: Every 5 minutes during active gameplay
- **Event save**: On life stage transition, evolution, achievement unlock, rebirth
- **Shutdown save**: Before entering deep sleep (if battery low detected)
- **NOT every tick**: Flash write every second would wear out in ~27 hours

---

## 2. Save Data Layout

```c
#define SAVE_MAGIC    0x444C4452   // "DLDR" in ASCII
#define SAVE_VERSION  1

typedef struct __attribute__((packed)) {
    // ─── Header (8 bytes) ────────────────────────────────────
    uint32_t magic;              // SAVE_MAGIC for validation
    uint8_t  version;            // Save format version
    uint8_t  _pad[1];
    uint16_t checksum;           // CRC-16 of everything after header

    // ─── Timestamp (4 bytes) ─────────────────────────────────
    uint32_t timestamp;          // RTC epoch seconds at save time

    // ─── Primary Stats (10 bytes) ────────────────────────────
    int16_t  hunger;
    int16_t  happiness;
    int16_t  energy;
    int16_t  hygiene;
    int16_t  health;

    // ─── Secondary Stats (16 bytes) ──────────────────────────
    uint32_t bond_xp;
    uint16_t discipline;
    uint16_t intelligence;
    uint16_t fitness;
    uint16_t exploration;
    int16_t  weight;
    uint16_t _pad2;

    // ─── Hidden Stats (16 bytes) ─────────────────────────────
    uint16_t care_mistakes;
    uint16_t consecutive_days;
    uint16_t noise_exposure;
    uint16_t night_disturbances;
    uint32_t last_interaction_epoch;   // Epoch seconds
    uint32_t neglect_start_epoch;

    // ─── Life Stage (28 bytes) ───────────────────────────────
    uint8_t  stage;                  // life_stage_t
    uint8_t  adult_form;             // evolution_form_t
    uint16_t hatch_progress;
    uint32_t age_seconds;
    uint32_t stage_start_seconds;
    uint16_t total_care_quality;
    uint16_t total_discipline;
    uint16_t total_intelligence;
    uint16_t total_fitness;
    uint16_t total_exploration;
    uint16_t total_happiness_avg;
    uint16_t total_music_exposure;
    uint16_t total_scold_count;

    // ─── Rebirth (6 bytes) ───────────────────────────────────
    uint8_t  generation;
    uint8_t  heritage_form;
    uint32_t heritage_bond_xp;

    // ─── Progression (16 bytes) ──────────────────────────────
    uint8_t  bond_level;
    uint8_t  _pad3;
    uint16_t decor_slots_available;
    uint64_t achievements;           // 64-bit achievement bitfield

    // ─── Decor (12 bytes) ────────────────────────────────────
    uint8_t  equipped_hat;
    uint8_t  equipped_bg;
    uint8_t  equipped_accessory;
    uint8_t  equipped_anim;
    uint64_t decor_unlocked;         // 64-bit decor bitfield

    // ─── Activity (24 bytes) ─────────────────────────────────
    uint32_t today_steps;
    uint32_t week_steps;
    uint32_t month_steps;
    uint32_t lifetime_steps;
    uint16_t unique_locations;
    uint16_t daily_streak;
    uint16_t streak_grace_remaining;  // Free misses left this week
    uint16_t streak_freeze_items;

    // ─── Emotion (4 bytes) ───────────────────────────────────
    uint8_t  current_emotion;
    uint8_t  _pad4;
    uint16_t emotions_seen_bitfield;  // For all-emotions achievement

    // ─── Treasure (16 bytes) ─────────────────────────────────
    uint8_t  hunt_active;
    uint8_t  hunt_type;              // treasure rarity
    uint16_t _pad5;
    float    hunt_lat;
    float    hunt_lon;
    uint32_t hunt_spawn_epoch;

    // ─── Decay Accumulators (16 bytes) ───────────────────────
    uint32_t accum_hunger;
    uint32_t accum_happiness;
    uint32_t accum_energy;
    uint32_t accum_hygiene;

} save_data_t;

// Total: ~176 bytes (well under one flash sector = 4096 bytes)
// Padded to 256 bytes for alignment and future expansion

_Static_assert(sizeof(save_data_t) <= 256, "Save data exceeds 256 byte budget");
```

---

## 3. Save / Load Protocol

### Save

```c
bool persistence_save(void) {
    save_data_t save = {0};

    // Header
    save.magic = SAVE_MAGIC;
    save.version = SAVE_VERSION;

    // Timestamp
    save.timestamp = rtc_get_epoch();

    // Pack current game state into save struct
    save_pack_stats(&save, &game.stats);
    save_pack_life(&save, &game.life);
    save_pack_progression(&save, &game.progression);
    save_pack_decor(&save, &game.decor);
    save_pack_activity(&save, &game.activity);
    save_pack_emotion(&save, &game.emotion);
    save_pack_treasure(&save, &game.treasure);
    save_pack_accumulators(&save);

    // Checksum (CRC-16 of everything after header)
    save.checksum = crc16((uint8_t*)&save + 8, sizeof(save_data_t) - 8);

    // Write backup first (atomic: if power fails here, primary is still valid)
    lfs_file_t file;
    if (lfs_file_open(&lfs, &file, "save.bak", LFS_O_WRONLY | LFS_O_CREAT | LFS_O_TRUNC) < 0) {
        return false;
    }
    lfs_file_write(&lfs, &file, &save, sizeof(save_data_t));
    lfs_file_close(&lfs, &file);

    // Write primary
    if (lfs_file_open(&lfs, &file, "save.dat", LFS_O_WRONLY | LFS_O_CREAT | LFS_O_TRUNC) < 0) {
        return false;
    }
    lfs_file_write(&lfs, &file, &save, sizeof(save_data_t));
    lfs_file_close(&lfs, &file);

    return true;
}
```

### Load

```c
bool persistence_load(save_data_t *out) {
    // Try primary first
    if (persistence_load_file("save.dat", out)) return true;

    // Primary corrupt/missing — try backup
    if (persistence_load_file("save.bak", out)) return true;

    // No valid save found
    return false;
}

bool persistence_load_file(const char *path, save_data_t *out) {
    lfs_file_t file;
    if (lfs_file_open(&lfs, &file, path, LFS_O_RDONLY) < 0) {
        return false;  // File doesn't exist
    }

    lfs_ssize_t read = lfs_file_read(&lfs, &file, out, sizeof(save_data_t));
    lfs_file_close(&lfs, &file);

    if (read != sizeof(save_data_t)) return false;

    // Validate magic
    if (out->magic != SAVE_MAGIC) return false;

    // Validate version
    if (out->version != SAVE_VERSION) {
        // Future: migration logic for older save formats
        return false;
    }

    // Validate checksum
    uint16_t expected = crc16((uint8_t*)out + 8, sizeof(save_data_t) - 8);
    if (out->checksum != expected) return false;

    return true;
}
```

### Restore Game State from Save

```c
void game_restore_from_save(const save_data_t *save) {
    // Unpack stats
    game.stats.primary.hunger    = save->hunger;
    game.stats.primary.happiness = save->happiness;
    game.stats.primary.energy    = save->energy;
    game.stats.primary.hygiene   = save->hygiene;
    game.stats.primary.health    = save->health;

    game.stats.secondary.bond_xp       = save->bond_xp;
    game.stats.secondary.discipline    = save->discipline;
    game.stats.secondary.intelligence  = save->intelligence;
    game.stats.secondary.fitness       = save->fitness;
    game.stats.secondary.exploration   = save->exploration;
    game.stats.secondary.weight        = save->weight;

    game.stats.hidden.care_mistakes      = save->care_mistakes;
    game.stats.hidden.consecutive_days   = save->consecutive_days;
    game.stats.hidden.noise_exposure     = save->noise_exposure;
    game.stats.hidden.night_disturbances = save->night_disturbances;

    // Unpack life stage
    game.life.stage              = (life_stage_t)save->stage;
    game.life.adult_form         = (evolution_form_t)save->adult_form;
    game.life.age_seconds        = save->age_seconds;
    game.life.hatch_progress     = save->hatch_progress;
    game.life.stage_start_seconds = save->stage_start_seconds;
    game.life.generation         = save->generation;
    game.life.heritage_form      = (evolution_form_t)save->heritage_form;
    game.life.heritage_bond_xp   = save->heritage_bond_xp;

    // Evolution accumulators
    game.life.total_care_quality   = save->total_care_quality;
    game.life.total_discipline     = save->total_discipline;
    game.life.total_intelligence   = save->total_intelligence;
    game.life.total_fitness        = save->total_fitness;
    game.life.total_exploration    = save->total_exploration;
    game.life.total_happiness_avg  = save->total_happiness_avg;
    game.life.total_music_exposure = save->total_music_exposure;
    game.life.total_scold_count    = save->total_scold_count;

    // Unpack progression
    game.progression.bond_xp    = save->bond_xp;
    game.progression.bond_level = (bond_level_t)save->bond_level;
    game.progression.achievements = save->achievements;
    game.progression.decor_unlocked = save->decor_unlocked;

    // Unpack decor
    game.decor.equipped[DECOR_SLOT_HAT]       = save->equipped_hat;
    game.decor.equipped[DECOR_SLOT_BACKGROUND] = save->equipped_bg;
    game.decor.equipped[DECOR_SLOT_ACCESSORY]  = save->equipped_accessory;
    game.decor.equipped[DECOR_SLOT_ANIM_STYLE] = save->equipped_anim;
    game.decor.unlocked = save->decor_unlocked;

    // Unpack activity
    game.activity.today_steps    = save->today_steps;
    game.activity.week_steps     = save->week_steps;
    game.activity.month_steps    = save->month_steps;
    game.activity.lifetime_steps = save->lifetime_steps;
    game.activity.unique_locations = save->unique_locations;
    game.activity.daily_streak   = save->daily_streak;

    // Unpack emotion
    game.emotion.current = (emotion_id_t)save->current_emotion;

    // Unpack treasure
    if (save->hunt_active) {
        game.treasure.state      = HUNT_ACTIVE;
        game.treasure.target_lat = save->hunt_lat;
        game.treasure.target_lon = save->hunt_lon;
        game.treasure.rarity     = save->hunt_type;
    }

    // Restore decay accumulators
    accum.hunger_accum    = save->accum_hunger;
    accum.happiness_accum = save->accum_happiness;
    accum.energy_accum    = save->accum_energy;
    accum.hygiene_accum   = save->accum_hygiene;

    // Calculate and apply offline decay
    uint32_t now = rtc_get_epoch();
    uint32_t elapsed = now - save->timestamp;
    stat_apply_offline_decay(&game.stats, elapsed);
}
```

---

## 4. Data Packing

All save fields use fixed-size types with `__attribute__((packed))` to ensure consistent layout across compiler versions. No pointers stored — all data is value types.

### CRC-16 Implementation

```c
// CRC-16-CCITT (polynomial 0x1021)
uint16_t crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000)
                crc = (crc << 1) ^ 0x1021;
            else
                crc = crc << 1;
        }
    }
    return crc;
}
```

---

## 5. Wear Leveling & Integrity

### LittleFS Handles Wear Leveling

LittleFS internally spreads writes across flash sectors. With a ~1.75MB partition and saves of 256 bytes:

- Sector size: 4096 bytes
- Sectors available: ~448
- Write cycles per sector: ~100,000
- Total writes before wear-out: ~44,800,000
- At 1 save per 5 minutes: **~426 years**

Wear is not a practical concern for this application.

### Power-Loss Protection

```
Save sequence:
1. Write save.bak (complete backup)
2. Write save.dat (primary)

Load sequence:
1. Read save.dat → validate magic + checksum
2. If invalid: read save.bak → validate
3. If both invalid: new game

Failure modes:
- Power loss during step 1: save.dat still valid from previous save
- Power loss during step 2: save.bak valid from step 1
- Both files corrupt: extremely unlikely (two independent writes)
```

### Save Version Migration

```c
// Future-proofing: when save format changes, migrate old saves
bool persistence_migrate(save_data_t *save) {
    if (save->version == SAVE_VERSION) return true;  // Current version

    // Version 1 → 2 migration (example for future)
    // if (save->version == 1) {
    //     // Add new fields with defaults
    //     save->new_field = DEFAULT_VALUE;
    //     save->version = 2;
    // }

    return save->version == SAVE_VERSION;
}
```

---

## 6. Location Database

WiFi fingerprints stored separately (larger, less frequent updates):

```c
#define MAX_LOCATIONS 128
#define BSSID_SIZE    6       // MAC address bytes
#define SSID_MAX      32

typedef struct __attribute__((packed)) {
    uint8_t  bssid[BSSID_SIZE];   // WiFi access point MAC
    char     ssid[16];            // Truncated SSID (just for display)
    uint8_t  location_type;       // 0=unknown, 1=home, 2=work, 3=other
    uint8_t  visit_count;         // Times visited (caps at 255)
    uint32_t first_seen_epoch;    // When first discovered
    uint32_t last_seen_epoch;     // Most recent visit
} location_entry_t;  // 32 bytes each

typedef struct __attribute__((packed)) {
    uint32_t magic;               // Location DB magic
    uint16_t count;               // Number of entries
    uint16_t home_idx;            // Index of home location (-1 if unset)
    location_entry_t entries[MAX_LOCATIONS];
} location_db_t;  // ~4104 bytes

// Location DB is written only when a new location is discovered
// or visit count increments — much less frequent than save.dat

void location_db_add(const uint8_t *bssid, const char *ssid) {
    // Check if already known
    for (int i = 0; i < loc_db.count; i++) {
        if (memcmp(loc_db.entries[i].bssid, bssid, BSSID_SIZE) == 0) {
            loc_db.entries[i].visit_count++;
            loc_db.entries[i].last_seen_epoch = rtc_get_epoch();
            return;  // Known location
        }
    }

    // New location!
    if (loc_db.count >= MAX_LOCATIONS) {
        // Evict least-visited, oldest entry
        location_db_evict();
    }

    location_entry_t *entry = &loc_db.entries[loc_db.count++];
    memcpy(entry->bssid, bssid, BSSID_SIZE);
    strncpy(entry->ssid, ssid, 15);
    entry->ssid[15] = '\0';
    entry->location_type = 0;
    entry->visit_count = 1;
    entry->first_seen_epoch = rtc_get_epoch();
    entry->last_seen_epoch = entry->first_seen_epoch;

    // Fire new location event
    event_fire(EVENT_NEW_LOCATION, &(event_data_t){ .value = loc_db.count - 1 });

    // Persist
    location_db_save();
}
```

---

### Persistence API Summary

```c
// ─── Public Interface (persist.h) ────────────────────────────

// Save / Load
bool persistence_save(void);
bool persistence_load(save_data_t *out);
void game_restore_from_save(const save_data_t *save);

// Event-triggered saves
void persistence_save_on_event(event_type_t type, const event_data_t *data);

// Location database
void location_db_init(void);
void location_db_add(const uint8_t *bssid, const char *ssid);
bool location_db_is_home(const uint8_t *bssid);
void location_db_set_home(uint16_t index);
uint16_t location_db_unique_count(void);

// Memorial (rebirth history)
void persistence_save_memorial(const memorial_t *memorial);
bool persistence_load_memorials(memorial_t *out, uint8_t *count);

// LittleFS lifecycle
void persistence_init(void);    // Mount filesystem
void persistence_format(void);  // Factory reset
```

---

*Next: [10-activity-tracker.md](10-activity-tracker.md) — Steps, location, and treasure hunts.*
