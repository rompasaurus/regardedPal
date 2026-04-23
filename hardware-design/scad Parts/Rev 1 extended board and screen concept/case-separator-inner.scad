// Dilder Case Separator Sheet — thin divider plate with pass-through slots
//
// A flat sheet that sits between enclosure layers. Same inner footprint as the
// top cover (rounded corners), with two long rectangular slots matching the
// middle plate header slots and screw clearance holes at all 4 corners.
//
// Export:
//   openscad -o case-separator.3mf case-separator.scad

$fn = 48;

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
antenna_proj   = 6;
header_gap     = 22;
header_slot_len = 56.5;    // matches middle plate v2
header_slot_wid = 4;       // matches middle plate v2

// ---- Waveshare 2.13" display ----
disp_len       = 65;
disp_wid       = 30;

// ---- 1000 mAh battery ----
bat_len        = 52;
bat_wid        = 35;

// ---- Enclosure geometry ----
wall_thk       = 2;
plate_thk      = 1;        // thin separator sheet
pillar         = 5;
slop           = 0.4;

screw_clr      = 3.2;

// ---- Rounding ----
plate_corner_r = 1;        // matches top cover inner corners

// ---- XY layout ----
inner_wid      = max(board_wid, disp_wid, bat_wid) + 2 * slop;
inner_len      = max(board_len + antenna_proj, disp_len + 2 * pillar, bat_len) + 2 * slop;
outer_wid      = inner_wid + 2 * wall_thk;
outer_len      = inner_len + 2 * wall_thk;

plate_w = inner_wid - 2 * slop;
plate_l = inner_len - 2 * slop;
plate_origin_x = wall_thk + slop;
plate_origin_y = wall_thk + slop;

pillar_xy = [
    [wall_thk,                             wall_thk                            ],
    [outer_wid - wall_thk - pillar,        wall_thk                            ],
    [wall_thk,                             outer_len - wall_thk - pillar       ],
    [outer_wid - wall_thk - pillar,        outer_len - wall_thk - pillar       ],
];

board_x        = (outer_wid - board_wid) / 2;


// ============== SHARED ==============

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}


// ============== CASE SEPARATOR ==============

module case_separator() {
    hdr_strip = (board_wid - header_gap) / 2;
    header_slot_x_left  = board_x - plate_origin_x;
    header_slot_x_right = board_x + board_wid - header_slot_wid - plate_origin_x;
    header_slot_y_start = (plate_l - header_slot_len) / 2;

    translate([plate_origin_x, plate_origin_y, 0])
    difference() {
        // Flat sheet with rounded corners matching top cover inner profile
        rounded_v_box(plate_w, plate_l, plate_thk, plate_corner_r);

        // Left rectangular slot
        translate([header_slot_x_left, header_slot_y_start, -0.1])
            cube([header_slot_wid, header_slot_len, plate_thk + 0.2]);

        // Right rectangular slot
        translate([header_slot_x_right, header_slot_y_start, -0.1])
            cube([header_slot_wid, header_slot_len, plate_thk + 0.2]);

        // Screw clearance holes
        for (p = pillar_xy)
            translate([p[0] + pillar/2 - plate_origin_x, p[1] + pillar/2 - plate_origin_y, -0.1])
                cylinder(h = plate_thk + 0.2, d = screw_clr);
    }
}

case_separator();
