// Dilder Middle Plate — standalone board tray for ESP32-S3
//
// This is the middle plate extracted from esp32s3-enclosure.scad.
// It drops into the base shell and rests on the lower shelf at z=8.
// The plate holds the Olimex ESP32-S3-DevKit-Lipo board with header
// pin clearance slots on both long edges.
//
// Export:
//   openscad -o middle.3mf middle-plate.scad
//
// To override parameters from the command line:
//   openscad -D 'board_wid=30' -o middle.3mf middle-plate.scad

$fn = 48;

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
board_thk      = 1.6;
wroom_h        = 3.2;
antenna_wid    = 18;
antenna_proj   = 6;
header_gap     = 22;       // distance between the two header rows
header_slot_len = 56;      // slot length — full board length so headers clear
header_slot_wid = 4;       // slot width — wider than hdr_strip (3mm) for easy fit

// ---- Waveshare 2.13" display ----
disp_len       = 65;
disp_wid       = 30;

// ---- 1000 mAh battery ----
bat_len        = 52;
bat_wid        = 35;

// ---- Enclosure geometry ----
wall_thk       = 2;
plate_thk      = 2;
pillar         = 5;
slop           = 0.4;
bat_chamber_h  = 6;

screw_clr      = 3.2;

// ---- Z layout (only what we need) ----
z_base_top     = plate_thk;                       // 2
z_mid_bot      = z_base_top + bat_chamber_h;      // 8

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
board_y        = (outer_len - board_len - antenna_proj) / 2;


// ============== MIDDLE PLATE ==============

module middle_plate() {
    plate_w = inner_wid - 2 * slop;
    plate_l = inner_len - 2 * slop;
    plate_origin_x = wall_thk + slop;
    plate_origin_y = wall_thk + slop;
    hdr_strip = (board_wid - header_gap) / 2;
    header_slot_x_left  = board_x - plate_origin_x;
    header_slot_x_right = board_x + board_wid - header_slot_wid - plate_origin_x;
    // Center the slot along the plate length
    header_slot_y_start = (plate_l - header_slot_len) / 2;
    header_slot_y_len   = header_slot_len;

    translate([plate_origin_x, plate_origin_y, z_mid_bot])
    difference() {
        cube([plate_w, plate_l, plate_thk]);

        // Corner pillar clearance notches — overshoot plate edges by 1mm for clean booleans
        for (dx = [0, plate_w - pillar - slop])
            for (dy = [0, plate_l - pillar - slop]) {
                ox = (dx > 0) ? 1 : 0;   // overshoot +x on far-x corners
                oy = (dy > 0) ? 1 : 0;   // overshoot +y on far-y corners
                translate([dx - slop, dy - slop, -1])
                    cube([pillar + 2 * slop + ox, pillar + 2 * slop + oy, plate_thk + 2]);
            }

        // Left header pin slot
        translate([header_slot_x_left, header_slot_y_start, -1])
            cube([header_slot_wid, header_slot_y_len, plate_thk + 2]);

        // Right header pin slot
        translate([header_slot_x_right, header_slot_y_start, -1])
            cube([header_slot_wid, header_slot_y_len, plate_thk + 2]);

        // Screw clearance holes
        for (p = pillar_xy)
            translate([p[0] + pillar/2 - plate_origin_x, p[1] + pillar/2 - plate_origin_y, -1])
                cylinder(h = plate_thk + 2, d = screw_clr);
    }
}

middle_plate();
