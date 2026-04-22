// Dilder Top Cover v3 — open border frame with rounded inner corners for flush plate seating
//
// No dome, no floor — just the perimeter wall ring + 4 corner pillar posts.
// Solid border all around (no wire notch).
// Inner corners and countersink pocket are rounded to match the windowed plate's corner radius,
// allowing it to slide in flush at the pillar junctions.
//
// Export:
//   openscad -o top-cover-v3.3mf top-cover-v3.scad

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
top_gap        = 10;       // +5mm height

screw_clr      = 3.2;

// ---- Rounding ----
case_corner_r  = 4;
plate_corner_r = 1;       // must match windowed plate's corner radius
top_edge_r     = 2;       // top edge bullnose radius

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

// Pillar with only one corner rounded (the exposed inner corner).
// round_x/round_y: 0=near edge, 1=far edge — selects which corner gets the radius.
module pillar_one_round(w, l, h, r, round_x, round_y) {
    tiny = 0.01;
    hull() {
        for (ix = [0, 1])
            for (iy = [0, 1]) {
                cr = (ix == round_x && iy == round_y) ? r : tiny;
                translate([cr + ix * (w - 2*cr), cr + iy * (l - 2*cr), 0])
                    cylinder(r = cr, h = h, $fn = 48);
            }
    }
}


// ============== TOP COVER v3 ==============

module top_cover() {
    translate([0, 0, z_cover_bot])
    difference() {
        union() {
            // Outer wall ring — rounded outer edges, bullnose top, rounded inner edges
            difference() {
                // Outer shell with rounded top edge
                intersection() {
                    hull() {
                        for (x = [case_corner_r, outer_wid - case_corner_r])
                            for (y = [case_corner_r, outer_len - case_corner_r]) {
                                translate([x, y, 0])
                                    cylinder(r = case_corner_r, h = cover_h - top_edge_r, $fn = 48);
                                translate([x, y, cover_h - top_edge_r])
                                    sphere(r = case_corner_r, $fn = 24);
                            }
                    }
                    // Clip bottom flat
                    cube([outer_wid, outer_len, cover_h]);
                }
                // Inner cavity with rounded corners
                translate([wall_thk, wall_thk, -0.1])
                    rounded_v_box(inner_wid, inner_len, cover_h + 0.2, plate_corner_r);
            }

            // Pillar posts — only the exposed inner corner is rounded
            for (p = pillar_xy) {
                rx = (p[0] < outer_wid/2) ? 1 : 0;
                ry = (p[1] < outer_len/2) ? 1 : 0;
                translate([p[0], p[1], 0])
                    pillar_one_round(pillar, pillar, cover_h, plate_corner_r, rx, ry);
            }
        }

        // Countersink — single rounded pocket matching plate footprint
        // Cuts into pillar tops with rounded inner corners so plate seats flush
        translate([wall_thk, wall_thk, cover_h - plate_thk])
            rounded_v_box(inner_wid, inner_len, plate_thk + 0.1, plate_corner_r);

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
