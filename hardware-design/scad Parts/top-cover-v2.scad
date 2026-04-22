// Dilder Top Cover v2 — open border frame with square pillar screw posts
//
// No dome, no floor — just the perimeter wall ring + 4 corner pillar posts.
// Solid border all around (no wire notch).
//
// Export:
//   openscad -o top-cover-v2.3mf top-cover-v2.scad

$fn = 48;

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
antenna_proj   = 6;

// ---- Waveshare 2.13" display ----
disp_len       = 65;
disp_wid       = 30;
disp_thk       = 5;

// ---- 1000 mAh battery ----
bat_len        = 52;
bat_wid        = 35;

// ---- Enclosure geometry ----
wall_thk       = 2;
plate_thk      = 2;
pillar         = 5;
slop           = 0.4;
bat_chamber_h  = 6;
disp_clear     = 1;
board_thk      = 1.6;
wroom_h        = 3.2;
top_gap        = 5;

screw_clr      = 3.2;

// ---- Rounding ----
case_corner_r  = 4;

// ---- Z layout ----
z_base_top     = plate_thk;
z_mid_bot      = z_base_top + bat_chamber_h;
z_mid_top      = z_mid_bot + plate_thk;
z_board_bot    = z_mid_top;
z_board_top    = z_board_bot + board_thk;
z_wroom_top    = z_board_top + wroom_h;
z_disp_bot     = z_wroom_top + disp_clear;
z_disp_top     = z_disp_bot + disp_thk;
base_wall_top  = z_disp_top + plate_thk;
z_cover_bot    = base_wall_top;
cover_h        = plate_thk + top_gap;

// ---- XY layout ----
inner_wid      = max(board_wid, disp_wid, bat_wid) + 2 * slop;
inner_len      = max(board_len + antenna_proj, disp_len + 2 * pillar, bat_len) + 2 * slop;
outer_wid      = inner_wid + 2 * wall_thk;
outer_len      = inner_len + 2 * wall_thk;

pillar_xy = [
    [wall_thk,                             wall_thk                            ],
    [outer_wid - wall_thk - pillar,        wall_thk                            ],
    [wall_thk,                             outer_len - wall_thk - pillar       ],
    [outer_wid - wall_thk - pillar,        outer_len - wall_thk - pillar       ],
];


// ============== SHARED ==============

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}


// ============== TOP COVER v2 ==============

module top_cover() {
    translate([0, 0, z_cover_bot])
    difference() {
        union() {
            // Outer wall ring — rounded vertical edges, flat top, open inside
            difference() {
                rounded_v_box(outer_wid, outer_len, cover_h, case_corner_r);
                translate([wall_thk, wall_thk, -0.1])
                    cube([inner_wid, inner_len, cover_h + 0.2]);
            }

            // Square pillar posts at 4 corners
            for (p = pillar_xy)
                translate([p[0], p[1], 0])
                    cube([pillar, pillar, cover_h]);
        }

        // Countersink at top of each pillar — plate_thk deep so windowed plate sits flush
        for (p = pillar_xy)
            translate([p[0], p[1], cover_h - plate_thk])
                cube([pillar, pillar, plate_thk + 0.1]);

        // Screw clearance holes through pillars
        for (p = pillar_xy) {
            cx = p[0] + pillar/2;
            cy = p[1] + pillar/2;
            translate([cx, cy, -0.1])
                cylinder(h = cover_h + 0.2, d = screw_clr);
        }
    }
}

top_cover();
