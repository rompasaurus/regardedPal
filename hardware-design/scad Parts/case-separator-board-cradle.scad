// Dilder Case Separator — board cradle variant
//
// Outer footprint matching the base (39.8 x 79.8mm, 4mm corner radius).
// Center cutout sized to the ESP32-S3 board + antenna projection.
// Raised cradle wall around the cutout holds the board in place.
//
// Export:
//   openscad -o case-separator-board-cradle.3mf case-separator-board-cradle.scad

$fn = 48;

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
antenna_proj   = 6;
usb_overhang   = 2;        // USB-C ports extend past PCB edge

// ---- Waveshare 2.13" display ----
disp_len       = 65;
disp_wid       = 30;

// ---- 1000 mAh battery ----
bat_len        = 52;
bat_wid        = 35;

// ---- Enclosure geometry ----
wall_thk       = 2;
plate_thk      = 1;        // base sheet thickness
pillar         = 5;
slop           = 0.4;
cradle_wall    = 1.5;      // raised wall thickness around the board cutout
cradle_h       = 2;        // wall height above the base sheet

screw_clr      = 3.2;

// ---- Rounding ----
case_corner_r  = 4;
cutout_r       = 1;        // rounded corners on board cutout

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

// Board cutout dimensions (board + antenna + USB overhang + clearance)
cutout_w       = board_wid + 2 * slop;
cutout_l       = board_len + antenna_proj + usb_overhang + 2 * slop;
cutout_x       = (outer_wid - cutout_w) / 2;
cutout_y       = (outer_len - cutout_l) / 2;

// Cradle wall outer dimensions
cradle_outer_w = cutout_w + 2 * cradle_wall;
cradle_outer_l = cutout_l + 2 * cradle_wall;
cradle_x       = cutout_x - cradle_wall;
cradle_y       = cutout_y - cradle_wall;


// ============== SHARED ==============

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}


// ============== CASE SEPARATOR — BOARD CRADLE ==============

module case_separator_board_cradle() {
    difference() {
        union() {
            // Base sheet — full outer footprint
            rounded_v_box(outer_wid, outer_len, plate_thk, case_corner_r);

            // Cradle wall — raised border around the board cutout
            translate([cradle_x, cradle_y, plate_thk])
            difference() {
                rounded_v_box(cradle_outer_w, cradle_outer_l, cradle_h, cutout_r + cradle_wall);
                translate([cradle_wall, cradle_wall, -0.1])
                    rounded_v_box(cutout_w, cutout_l, cradle_h + 0.2, cutout_r);
            }
        }

        // Board cutout through base sheet
        translate([cutout_x, cutout_y, -0.1])
            rounded_v_box(cutout_w, cutout_l, plate_thk + 0.2, cutout_r);

        // Screw clearance holes
        for (p = pillar_xy)
            translate([p[0] + pillar/2, p[1] + pillar/2, -0.1])
                cylinder(h = plate_thk + cradle_h + 0.2, d = screw_clr);
    }
}

case_separator_board_cradle();
