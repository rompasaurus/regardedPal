// ESP32-S3-WROOM DevKit — 3-plate sandwich mount
// Top plate + middle plate (under board, between header pins) + bottom plate
// 4 corner pillars clamp the stack with M3 screws.

$fn = 48;

// ---- Board dimensions (Olimex ESP32-S3-DevKit-Lipo) ----
board_len       = 56;
board_wid       = 28;
board_thk       = 1.6;
antenna_wid     = 18;
antenna_proj    = 6;
header_gap      = 22;   // inner span between header pin rows

// ---- Mount geometry ----
pillar          = 5;    // 5mm square corner pillars
plate_thk       = 3;
top_gap         = 5;    // top plate sits 5mm above mid plate
pin_gap         = 6;    // bottom plate sits 6mm below mid plate
center_window   = 20;   // top-plate cutout width (runs along length)

// ---- Hardware ----
screw_clr       = 3.2;  // M3 clearance hole
slop            = 0.3;

// ---- Z anchors (z=0 is top face of mid plate = board bottom) ----
z_mid_top       = 0;
z_mid_bot       = -plate_thk;
z_top_bot       = top_gap;
z_top_top       = top_gap + plate_thk;
z_bot_top       = -plate_thk - pin_gap;
z_bot_bot       = -plate_thk - pin_gap - plate_thk;
pillar_h        = z_top_top - z_bot_bot;

// ---- Corner pillar positions (lower-left, in board coords) ----
// Top pair sit in the 5mm strips flanking the antenna.
// Bottom pair sit at the far short edge.
header_strip    = (board_wid - header_gap) / 2;  // 3mm on each long edge

pillar_xy = [
    [0,                  0                 ],   // bottom-left
    [board_wid - pillar, 0                 ],   // bottom-right
    [0,                  board_len - pillar],   // top-left (beside antenna)
    [board_wid - pillar, board_len - pillar],   // top-right (beside antenna)
];

// ---- Modules ----
module pillars() {
    for (p = pillar_xy)
        translate([p[0], p[1], z_bot_bot])
            difference() {
                cube([pillar, pillar, pillar_h]);
                translate([pillar/2, pillar/2, -1])
                    cylinder(h = pillar_h + 2, d = screw_clr);
            }
}

// 28x56 plate with 5x5 corner notches so pillars pass through.
module plate_base() {
    difference() {
        cube([board_wid, board_len, plate_thk]);
        for (p = pillar_xy)
            translate([p[0] - slop, p[1] - slop, -1])
                cube([pillar + 2*slop, pillar + 2*slop, plate_thk + 2]);
    }
}

// Middle plate: full footprint minus header pin slots so pins clear the plate.
module mid_plate() {
    translate([0, 0, z_mid_bot])
        difference() {
            plate_base();
            translate([0, pillar + slop, -1])
                cube([header_strip, board_len - 2*pillar - 2*slop, plate_thk + 2]);
            translate([board_wid - header_strip, pillar + slop, -1])
                cube([header_strip, board_len - 2*pillar - 2*slop, plate_thk + 2]);
        }
}

// Top plate: full footprint minus a 20mm-wide window over the WROOM module.
module top_plate() {
    translate([0, 0, z_top_bot])
        difference() {
            plate_base();
            translate([(board_wid - center_window)/2, pillar + slop, -1])
                cube([center_window, board_len - 2*pillar - 2*slop, plate_thk + 2]);
        }
}

// Bottom plate: solid, 6mm below mid plate (header pins clear it).
module bot_plate() {
    translate([0, 0, z_bot_bot])
        plate_base();
}

// ---- Preview: translucent board + antenna ----
module board_preview() {
    color("darkgreen", 0.4)
        difference() {
            cube([board_wid, board_len, board_thk]);
            for (p = pillar_xy)
                translate([p[0] - slop, p[1] - slop, -1])
                    cube([pillar + 2*slop, pillar + 2*slop, board_thk + 2]);
        }
    color("silver", 0.5)
        translate([(board_wid - antenna_wid)/2, board_len, board_thk - 0.5])
            cube([antenna_wid, antenna_proj, 0.5]);
}

// ---- Assembly ----
pillars();
mid_plate();
top_plate();
bot_plate();
%board_preview();
