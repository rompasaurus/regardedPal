// Dilder Top-Mid Plate (windowed) v1 — display cover with viewing window + snap-fit rails
//
// Fits inside the top cover frame. Solid face plate all around (no wire gap in face).
// Rails extend to plate edges and retain a gap for wire pass-through below the face.
//
// Export:
//   openscad -o top-plate-windowed-v1.3mf top-plate-windowed-v1.scad

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

screw_clr      = 3.2;

// ---- Rounding ----
plate_corner_r = 1;

// ---- Display viewing window ----
topmid_window_w = 25;
topmid_window_l = 50;

// ---- Snap rails ----
snap_lip_d     = 1.0;       // lip protrusion inward under display
snap_lip_h     = 1.0;       // lip thickness — full printable layer
snap_rail_h    = 4.5;       // rail depth below face plate

// ---- Wire gap (rail only, not face plate) ----
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


// ============== TOP-MID PLATE (WINDOWED) v1 ==============

module top_plate_windowed() {
    plate_expand = 0.5;    // expand outer edge by 0.5mm per side
    plate_w = inner_wid - 2 * slop + 2 * plate_expand;
    plate_l = inner_len - 2 * slop + 2 * plate_expand;
    plate_x = wall_thk + slop - plate_expand;
    plate_y = wall_thk + slop - plate_expand;

    // Rails extend from display edge to plate edge
    rail_y_local      = disp_y - plate_y;
    rail_len          = disp_len;
    disp_x_local      = disp_x - plate_x;          // display left edge in local coords
    disp_x_right      = disp_x_local + disp_wid;    // display right edge

    // Rails flush with plate edges, thinned 0.5mm from display side
    rail_trim         = 0.5;
    rail_w_left       = disp_x_local - rail_trim;           // ~2.0mm
    rail_w_right      = plate_w - disp_x_right - rail_trim; // ~2.0mm

    // Lip positions (at display edges, protruding inward)
    lip_x_left        = disp_x_local;
    lip_x_right       = disp_x_right - snap_lip_d;

    // Display viewing window (centered on plate)
    win_x = (plate_w - topmid_window_w) / 2;
    win_y = (plate_l - topmid_window_l) / 2;

    // Wire gap in rail only (centered on Y)
    wire_y = (plate_l - wire_hole_len) / 2;

    translate([plate_x, plate_y, z_disp_top])
    difference() {
        union() {
            // Solid face plate
            rounded_v_box(plate_w, plate_l, plate_thk, plate_corner_r);

            // -X long rail (flush with plate edge, trimmed from display side)
            translate([0, rail_y_local, -snap_rail_h])
                cube([rail_w_left, rail_len, snap_rail_h]);
            // Lip: full-width shelf on rail bottom + inward protrusion
            translate([0, rail_y_local, -snap_rail_h - snap_lip_h])
                cube([rail_w_left + snap_lip_d, rail_len, snap_lip_h]);

            // +X long rail (flush with plate far edge, trimmed from display side)
            translate([disp_x_right + rail_trim, rail_y_local, -snap_rail_h])
                cube([rail_w_right, rail_len, snap_rail_h]);
            // Lip: full-width shelf on rail bottom + inward protrusion
            translate([disp_x_right + rail_trim - snap_lip_d, rail_y_local, -snap_rail_h - snap_lip_h])
                cube([rail_w_right + snap_lip_d, rail_len, snap_lip_h]);
        }

        // Screw clearance holes
        for (p = pillar_xy)
            translate([p[0] + pillar/2 - plate_x, p[1] + pillar/2 - plate_y,
                       -snap_rail_h - snap_lip_h - 1])
                cylinder(h = plate_thk + snap_rail_h + snap_lip_h + 2, d = screw_clr);

        // Display viewing window
        translate([win_x, win_y, -0.1])
            cube([topmid_window_w, topmid_window_l, plate_thk + 0.2]);

        // Wire gap — cuts through rail + lip ONLY (below face plate)
        translate([-0.1, wire_y, -snap_rail_h - snap_lip_h - 0.1])
            cube([wire_hole_depth + 0.1, wire_hole_len, snap_rail_h + snap_lip_h]);
    }
}

top_plate_windowed();
