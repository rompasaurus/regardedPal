// Dilder Enclosure — stacked shell for ESP32-S3 board + Waveshare display + battery
//
// Pieces (each exported separately for printing):
//   base    — battery tray, walls, pillars, display rails, two shelves
//   middle  — board tray plate (drops in, rests on lower shelf at z=8)
//   topmid  — cover plate for display area (drops in, rests on upper shelf at z=20.8, flush with base top)
//   cover   — curved top, same footprint as base (flush with base top edge)
//   screws  — 4 plastic plugs that fit in the screw holes; heat-fuse to seal shut
//
// Export:
//   openscad -D 'part="base"'   -o base.3mf   esp32s3-enclosure.scad
//   openscad -D 'part="middle"' -o middle.3mf esp32s3-enclosure.scad
//   openscad -D 'part="topmid"' -o topmid.3mf esp32s3-enclosure.scad
//   openscad -D 'part="cover"'  -o cover.3mf  esp32s3-enclosure.scad
//   openscad -D 'part="screws"' -o screws.3mf esp32s3-enclosure.scad

$fn = 48;

// Which piece: "all" | "base" | "middle" | "topmid" | "cover" | "screws"
part = "all";

// ---- Board (Olimex ESP32-S3-DevKit-Lipo) ----
board_len      = 56;
board_wid      = 28;
board_thk      = 1.6;
wroom_h        = 3.2;
antenna_wid    = 18;
antenna_proj   = 6;
header_gap     = 22;

// ---- Waveshare 2.13" display ----
disp_len       = 65;
disp_wid       = 30;
disp_thk       = 5;
disp_window_w  = 25;
disp_window_l  = 50;

// ---- 1000 mAh battery ----
bat_len        = 52;
bat_wid        = 35;
bat_thk        = 5;

// ---- USB-C (2 ports on one short edge) ----
usbc_wid       = 9.5;
usbc_h         = 4;
usbc_n         = 2;
usbc_spacing   = 13;

// ---- Top-mid plate display window (opens the view down to the base) ----
topmid_window_w   = 25;      // viewing window width (matches display visible area)
topmid_window_l   = 50;      // viewing window length

// ---- Top-mid plate wire pass-through ----
wire_hole_len     = 30;      // along the long edge (Y direction)
wire_hole_depth   = 6;       // depth into the plate from the -X edge

// ---- Enclosure geometry ----
wall_thk       = 2;
plate_thk      = 2;
pillar         = 5;
slop           = 0.4;
bat_chamber_h  = 6;
disp_clear     = 1;
top_gap        = 5;

screw_clr      = 3.2;
screw_head_d   = 6;
screw_head_h   = 3;

// ---- Rounding ----
case_corner_r  = 4;      // vertical edge radius on base + cover
plate_corner_r = 1;      // vertical edge radius on plates
base_bot_cut   = 0;      // 0 = base bottom tapers fully to points (matches cover top); print base FLIPPED

// ---- Display rails ----
rail_size      = 2;      // 2x2 corner posts inside the base

// ---- Top-mid plate snap rails (two long rails on the underside) ----
snap_rail_w    = 2;      // rail thickness (in x)
snap_lip_d     = 0.5;    // how far the bottom lip protrudes inward under the display
snap_lip_h     = 0.5;    // lip thickness (in z)

// ---- Z layout ----
// Base walls rise to the top of the top-mid plate so the plate is flush with the base top edge.
// Cover sits on top of the base with the SAME outer footprint (edges aligned, no lip).
z_base_bot     = 0;
z_base_top     = plate_thk;                       // 2
z_mid_bot      = z_base_top + bat_chamber_h;      // 8
z_mid_top      = z_mid_bot + plate_thk;           // 10
z_board_bot    = z_mid_top;                       // 10
z_board_top    = z_board_bot + board_thk;         // 11.6
z_wroom_top    = z_board_top + wroom_h;           // 14.8
z_disp_bot     = z_wroom_top + disp_clear;        // 15.8
z_disp_top     = z_disp_bot + disp_thk;           // 20.8
base_wall_top  = z_disp_top + plate_thk;          // 22.8 — top-mid plate top flush with base top
z_cover_bot    = base_wall_top;                   // 22.8 — cover sits on base top, no lip
z_cover_top    = z_cover_bot + plate_thk + top_gap; // 29.8
total_h        = z_cover_top;

// ---- XY layout ----
// Interior must fit: board (28x62 w/antenna), display (30x65 + 2*pillar clearance), battery (35x52).
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
bat_x          = (outer_wid - bat_wid) / 2;
bat_y          = (outer_len - bat_len) / 2;
disp_x         = (outer_wid - disp_wid) / 2;
disp_y         = (outer_len - disp_len) / 2;


// ============== SHARED ==============

// Box with rounded vertical edges, flat top + bottom.
module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}

module screw_column(z_start, z_end) {
    for (p = pillar_xy)
        translate([p[0] + pillar/2, p[1] + pillar/2, z_start - 0.1])
            cylinder(h = z_end - z_start + 0.2, d = screw_clr);
}

module pillar_posts(z_start, z_end) {
    for (p = pillar_xy)
        translate([p[0], p[1], z_start])
            cube([pillar, pillar, z_end - z_start]);
}


// ============== BASE ==============

// Base outer shell: rounded vertical edges, flat top, curved bottom.
// Spheres sit at z=(r - bot_cut) so the z=0 cross-section is nonzero and prints upright
// with ~30° overhang from vertical (FDM-printable without supports).
module base_shell() {
    r = case_corner_r;
    sphere_z = r - base_bot_cut;
    intersection() {
        hull() {
            for (x = [r, outer_wid - r])
                for (y = [r, outer_len - r]) {
                    translate([x, y, sphere_z])
                        sphere(r = r, $fn = 24);
                    translate([x, y, sphere_z])
                        cylinder(r = r, h = base_wall_top - sphere_z, $fn = 48);
                }
        }
        translate([-1, -1, 0])
            cube([outer_wid + 2, outer_len + 2, base_wall_top + 1]);
    }
}

// Shelf for a plate at z_top_of_ledge.
// extend_to_floor: when true, the ledge material extends down to the base floor
// (turns the ledge into a vertical rib that prints cleanly without overhang).
// Short-wall ledges only — long-wall ledges would collide with the battery.
// tabs: 2.5×2.5 pillar-corner tabs at the top of the shelf for 4-point support.
module plate_shelf(z_top_of_ledge, tabs = true, extend_to_floor = false,
                   ledge_w = 2, ledge_h = 1, protrusion = 2, tab_overlap = 0.5) {
    z_ledge_bot = extend_to_floor ? plate_thk : (z_top_of_ledge - ledge_h);
    rib_h       = z_top_of_ledge - z_ledge_bot;

    translate([wall_thk + pillar, wall_thk, z_ledge_bot])
        cube([inner_wid - 2 * pillar, ledge_w, rib_h]);
    translate([wall_thk + pillar, outer_len - wall_thk - ledge_w, z_ledge_bot])
        cube([inner_wid - 2 * pillar, ledge_w, rib_h]);

    if (tabs) {
        tab_size  = protrusion + tab_overlap;
        z_tab_bot = z_top_of_ledge - ledge_h;
        for (p = pillar_xy) {
            inward_x = (p[0] < outer_wid/2) ? 1 : -1;
            inward_y = (p[1] < outer_len/2) ? 1 : -1;
            tab_x = (inward_x > 0) ? p[0] + pillar - tab_overlap : p[0] - protrusion;
            tab_y = (inward_y > 0) ? p[1] + pillar - tab_overlap : p[1] - protrusion;
            translate([tab_x, tab_y, z_tab_bot])
                cube([tab_size, tab_size, ledge_h]);
        }
    }
}

// 4 internal corner posts that constrain the display at its 4 corners.
// Stop at z_disp_top (= top-mid plate bottom) so the top-mid plate stays solid above
// them with no through-holes (no visible gaps on the plate top).
module display_rails() {
    disp_x_edges = [(outer_wid - disp_wid) / 2, (outer_wid + disp_wid) / 2];
    disp_y_edges = [(outer_len - disp_len) / 2, (outer_len + disp_len) / 2];
    for (ex = disp_x_edges)
        for (ey = disp_y_edges) {
            is_left   = ex < outer_wid / 2;
            is_bottom = ey < outer_len / 2;
            rx = is_left   ? ex - rail_size : ex;
            ry = is_bottom ? ey - rail_size : ey;
            translate([rx, ry, plate_thk])
                cube([rail_size, rail_size, z_disp_top - plate_thk]);
        }
}

module base() {
    difference() {
        union() {
            difference() {
                base_shell();
                translate([wall_thk, wall_thk, plate_thk])
                    cube([inner_wid, inner_len, base_wall_top - plate_thk + 1]);
            }
            pillar_posts(plate_thk, base_wall_top);
            // Lower shelf — rib extends to the floor (printable without overhang)
            plate_shelf(z_mid_bot,   tabs = true,  extend_to_floor = true);
            // Upper shelf — stays a thin ledge (2mm bridge, FDM-safe). Tabs omitted (would hit display).
            plate_shelf(z_disp_top,  tabs = false, extend_to_floor = false);
            // Display rails (tall posts, also support the top-mid plate corners)
            display_rails();
        }

        screw_column(0, total_h);

        // USB-C cutouts on -Y short wall
        usbc_z_center = z_board_top + usbc_h / 2;
        usbc_row_x0 = (outer_wid - ((usbc_n - 1) * usbc_spacing)) / 2;
        for (i = [0 : usbc_n - 1]) {
            cx = usbc_row_x0 + i * usbc_spacing;
            translate([cx - usbc_wid/2 - slop, -0.1, usbc_z_center - usbc_h/2 - slop])
                cube([usbc_wid + 2 * slop, wall_thk + 1, usbc_h + 2 * slop]);
        }
    }
}


// ============== MIDDLE PLATE ==============

module middle_plate() {
    plate_w = inner_wid - 2 * slop;
    plate_l = inner_len - 2 * slop;
    plate_origin_x = wall_thk + slop;
    plate_origin_y = wall_thk + slop;
    hdr_strip = (board_wid - header_gap) / 2;
    header_slot_x_left  = board_x - plate_origin_x;
    header_slot_x_right = board_x + board_wid - hdr_strip - plate_origin_x;
    header_slot_y_start = board_y - plate_origin_y + pillar;
    header_slot_y_len   = board_len - 2 * pillar;

    translate([plate_origin_x, plate_origin_y, z_mid_bot])
    difference() {
        cube([plate_w, plate_l, plate_thk]);

        for (dx = [0, plate_w - pillar - slop])
            for (dy = [0, plate_l - pillar - slop])
                translate([dx - slop, dy - slop, -1])
                    cube([pillar + 2 * slop, pillar + 2 * slop, plate_thk + 2]);

        translate([header_slot_x_left, header_slot_y_start, -1])
            cube([hdr_strip, header_slot_y_len, plate_thk + 2]);
        translate([header_slot_x_right, header_slot_y_start, -1])
            cube([hdr_strip, header_slot_y_len, plate_thk + 2]);

        for (p = pillar_xy)
            translate([p[0] + pillar/2 - plate_origin_x, p[1] + pillar/2 - plate_origin_y, -1])
                cylinder(h = plate_thk + 2, d = screw_clr);
    }
}


// ============== TOP-MID PLATE ==============
// Solid plate (no edge slots, no through-holes for base posts since those posts
// now stop at z_disp_top). Two long rails hang from the underside and grip the
// display's long edges with a 0.5mm lip at the bottom — snap-fit when the plate
// is pressed down over a pre-placed display.

module top_mid_plate() {
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

    // Display viewing window (centered)
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

        // Screw clearance holes at the 4 plate corners (on the rim)
        for (p = pillar_xy)
            translate([p[0] + pillar/2 - plate_x, p[1] + pillar/2 - plate_y,
                       -snap_rail_h - snap_lip_h - 1])
                cylinder(h = plate_thk + snap_rail_h + snap_lip_h + 2, d = screw_clr);

        // Display viewing window — cuts through the plate so the base is visible
        translate([win_x, win_y, -0.1])
            cube([topmid_window_w, topmid_window_l, plate_thk + 0.2]);

        // Wire pass-through hole — cuts through plate AND the -X rail + lip
        translate([-0.1, wire_y, -snap_rail_h - snap_lip_h - 0.1])
            cube([wire_hole_depth + 0.1, wire_hole_len,
                  plate_thk + snap_rail_h + snap_lip_h + 0.2]);
    }
}


// ============== TOP COVER ==============
// Same outer footprint as the base. Sits flush on the base top edge.
// Rounded vertical edges match the base for a continuous curve.

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

        // Open top: interior cavity cut extends the FULL height of the cover
        // (no top plate), but leaves 4 corner posts intact for the screws.
        difference() {
            translate([wall_thk, wall_thk, -0.1])
                cube([inner_wid, inner_len, cover_h + 0.2]);
            for (p = pillar_xy)
                translate([p[0] - 0.01, p[1] - 0.01, -0.2])
                    cube([pillar + 0.02, pillar + 0.02, cover_h + 0.4]);
        }

        // Wire pass-through notch on the -Y short wall at the base of the cover
        translate([(outer_wid - wire_hole_len) / 2, -0.1, -0.1])
            cube([wire_hole_len, wall_thk + 0.2, wire_hole_depth + 0.1]);

        // Screw holes with counterbores at the 4 corner posts
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


// ============== SCREW PLUGS ==============
// Plastic "screw" plugs that fit in the clearance holes. Head seats in the
// cover counterbore, shank drops all the way through to the base floor.
// After assembly, heat the head with a soldering iron to fuse it into the
// cover — permanent one-way seal.

module screw_plug() {
    shank_d = screw_clr - 0.2;         // 3.0mm fits with slight clearance
    shank_l = total_h - screw_head_h;  // stops at counterbore
    head_d  = screw_head_d - 0.4;      // slight clearance in counterbore
    head_h  = screw_head_h - 0.3;      // sits slightly below cover top

    cylinder(h = shank_l, d = shank_d, $fn = 32);
    translate([0, 0, shank_l])
        cylinder(h = head_h, d = head_d, $fn = 32);
}

module screw_plug_array() {
    spacing = screw_head_d + 4;
    for (i = [0 : 3])
        translate([i * spacing, 0, 0])
            screw_plug();
}


// ============== PREVIEW ==============

module board_preview() {
    color("darkgreen", 0.5)
        translate([board_x, board_y, z_board_bot])
            cube([board_wid, board_len, board_thk]);
    color("gray", 0.7)
        translate([board_x + (board_wid - 18)/2, board_y + 25, z_board_top])
            cube([18, 25.5, wroom_h]);
    color("silver", 0.6)
        translate([board_x + (board_wid - antenna_wid)/2, board_y + board_len, z_board_top])
            cube([antenna_wid, antenna_proj, 0.5]);
}

module display_preview() {
    color("white", 0.5)
        translate([disp_x, disp_y, z_disp_bot])
            cube([disp_wid, disp_len, disp_thk]);
}

module battery_preview() {
    color("orange", 0.4)
        translate([bat_x, bat_y, z_base_top])
            cube([bat_wid, bat_len, bat_thk]);
}


// ============== RENDER ==============

if (part == "all" || part == "base")    base();
if (part == "all" || part == "middle")  middle_plate();
if (part == "all" || part == "topmid")  top_mid_plate();
if (part == "all" || part == "cover")   top_cover();
if (part == "screws")                   screw_plug_array();

if (part == "all") {
    %board_preview();
    %display_preview();
    %battery_preview();
}
