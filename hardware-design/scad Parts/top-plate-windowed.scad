// Dilder Top-Mid Plate (windowed) — display cover plate with viewing window + snap-fit rails
//
// Drops into the base shell, rests on the upper shelf at z=20.8.
// Two long rails on the underside grip the display edges with a snap-fit lip.
// Has a 25×50mm viewing window centered over the display.
//
// Export:
//   openscad -o top-plate-windowed.3mf top-plate-windowed.scad

$fn = 48;

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
antenna_proj   = 6;

// ---- Waveshare 2.13" display ----
disp_len       = 65;
disp_wid       = 30;
disp_thk       = 5;
disp_window_w  = 25;
disp_window_l  = 50;

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

screw_clr      = 3.2;

// ---- Rounding ----
plate_corner_r = 1;

// ---- Display viewing window ----
topmid_window_w = 25;
topmid_window_l = 50;

// ---- Snap rails ----
snap_rail_w    = 2;
snap_lip_d     = 0.5;
snap_lip_h     = 0.5;

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

disp_x         = (outer_wid - disp_wid) / 2;
disp_y         = (outer_len - disp_len) / 2;


// ============== SHARED ==============

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}


// ============== TOP-MID PLATE (WINDOWED) ==============

module top_plate_windowed() {
    plate_w = inner_wid - 2 * slop;
    plate_l = inner_len - 2 * slop;
    plate_x = wall_thk + slop;
    plate_y = wall_thk + slop;

    rail_y_local      = disp_y - plate_y;
    rail_len          = disp_len;
    rail_x_left       = disp_x - plate_x - snap_rail_w;
    rail_x_right      = disp_x - plate_x + disp_wid;
    lip_x_left        = disp_x - plate_x;
    lip_x_right       = disp_x - plate_x + disp_wid - snap_lip_d;
    snap_rail_h       = disp_thk;

    // Display viewing window (centered on plate)
    win_x = (plate_w - topmid_window_w) / 2;
    win_y = (plate_l - topmid_window_l) / 2;

    // Wire pass-through hole (-X long side, centered on Y)
    wire_y = (plate_l - wire_hole_len) / 2;

    translate([plate_x, plate_y, z_disp_top])
    difference() {
        union() {
            rounded_v_box(plate_w, plate_l, plate_thk, plate_corner_r);

            // -X long rail (body + bottom lip)
            translate([rail_x_left, rail_y_local, -snap_rail_h])
                cube([snap_rail_w, rail_len, snap_rail_h]);
            translate([lip_x_left - 0.01, rail_y_local, -snap_rail_h - snap_lip_h])
                cube([snap_lip_d + 0.01, rail_len, snap_lip_h + 0.01]);

            // +X long rail
            translate([rail_x_right, rail_y_local, -snap_rail_h])
                cube([snap_rail_w, rail_len, snap_rail_h]);
            translate([lip_x_right, rail_y_local, -snap_rail_h - snap_lip_h])
                cube([snap_lip_d + 0.01, rail_len, snap_lip_h + 0.01]);
        }

        // Screw clearance holes
        for (p = pillar_xy)
            translate([p[0] + pillar/2 - plate_x, p[1] + pillar/2 - plate_y,
                       -snap_rail_h - snap_lip_h - 1])
                cylinder(h = plate_thk + snap_rail_h + snap_lip_h + 2, d = screw_clr);

        // Display viewing window
        translate([win_x, win_y, -0.1])
            cube([topmid_window_w, topmid_window_l, plate_thk + 0.2]);

        // Wire pass-through hole
        translate([-0.1, wire_y, -snap_rail_h - snap_lip_h - 0.1])
            cube([wire_hole_depth + 0.1, wire_hole_len,
                  plate_thk + snap_rail_h + snap_lip_h + 0.2]);
    }
}

top_plate_windowed();
