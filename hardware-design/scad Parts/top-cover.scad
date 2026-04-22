// Dilder Top Cover — curved dome shell that sits on top of the base
//
// Same outer footprint as the base. Rounded vertical edges + spherical top corners.
// Open underneath with 4 corner pillar posts for screw-through assembly.
// Wire pass-through notch on the -Y short wall.
//
// Export:
//   openscad -o top-cover.3mf top-cover.scad

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
screw_head_d   = 6;
screw_head_h   = 3;

// ---- Rounding ----
case_corner_r  = 4;

// ---- Wire pass-through ----
wire_hole_len  = 30;
wire_hole_depth = 6;

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
z_cover_top    = z_cover_bot + plate_thk + top_gap;
total_h        = z_cover_top;

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


// ============== TOP COVER ==============

module cover_outer_shell(h) {
    r = case_corner_r;
    hull() {
        for (x = [r, outer_wid - r])
            for (y = [r, outer_len - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h - r, $fn = 48);
        for (x = [r, outer_wid - r])
            for (y = [r, outer_len - r])
                translate([x, y, h - r])
                    sphere(r = r, $fn = 24);
    }
}

module top_cover() {
    cover_h = plate_thk + top_gap;

    translate([0, 0, z_cover_bot])
    difference() {
        cover_outer_shell(cover_h);

        // Interior cavity — open underneath, pillar posts preserved
        difference() {
            translate([wall_thk, wall_thk, -0.1])
                cube([inner_wid, inner_len, cover_h + 0.2]);
            for (p = pillar_xy)
                translate([p[0] - 0.01, p[1] - 0.01, -0.2])
                    cube([pillar + 0.02, pillar + 0.02, cover_h + 0.4]);
        }

        // Wire pass-through notch on -Y short wall
        translate([(outer_wid - wire_hole_len) / 2, -0.1, -0.1])
            cube([wire_hole_len, wall_thk + 0.2, wire_hole_depth + 0.1]);

        // Screw holes with counterbores
        for (p = pillar_xy) {
            cx = p[0] + pillar/2;
            cy = p[1] + pillar/2;
            translate([cx, cy, -0.1])
                cylinder(h = cover_h + 0.2, d = screw_clr);
            translate([cx, cy, cover_h - screw_head_h])
                cylinder(h = screw_head_h + 0.2, d = screw_head_d);
        }
    }
}

top_cover();
