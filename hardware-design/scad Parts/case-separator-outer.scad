// Dilder Case Separator Sheet (outer) — thin divider matching base outer footprint
//
// Same as the inner separator but sized to the full outer enclosure dimensions
// with the base's 4mm corner radius. Two long rectangular slots and screw holes.
//
// Export:
//   openscad -o case-separator-outer.3mf case-separator-outer.scad

$fn = 48;

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
antenna_proj   = 6;
header_gap     = 22;
header_slot_len = 56.5;
header_slot_wid = 4;

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
case_corner_r  = 4;        // matches base outer corners

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


// ============== CASE SEPARATOR (OUTER) ==============

module case_separator_outer() {
    header_slot_x_left  = board_x - (header_slot_wid + (board_wid - header_gap) / 2 - header_slot_wid);
    // Simpler: match the middle plate slot positions relative to full outer sheet
    hdr_strip = (board_wid - header_gap) / 2;
    slot_x_left  = board_x;
    slot_x_right = board_x + board_wid - header_slot_wid;
    slot_y_start = (outer_len - header_slot_len) / 2;

    difference() {
        // Full outer footprint with base corner radius
        rounded_v_box(outer_wid, outer_len, plate_thk, case_corner_r);

        // Left rectangular slot
        translate([slot_x_left, slot_y_start, -0.1])
            cube([header_slot_wid, header_slot_len, plate_thk + 0.2]);

        // Right rectangular slot
        translate([slot_x_right, slot_y_start, -0.1])
            cube([header_slot_wid, header_slot_len, plate_thk + 0.2]);

        // Screw clearance holes
        for (p = pillar_xy)
            translate([p[0] + pillar/2, p[1] + pillar/2, -0.1])
                cylinder(h = plate_thk + 0.2, d = screw_clr);
    }
}

case_separator_outer();
