// Dilder Rev 2 "extended with joystick" — BASE PLATE v1
//
// Shallow tray that sits BELOW the aaa-cradle-insert-v1 + top-cover-
// windowed-screen-inlay-v3-2piece stack. Holds the cradle from the
// bottom (cradle drops into the pocket) and snaps up into the top
// cover via 4 cylindrical pegs that slide into the cover's blind M3
// bores.
//
// Stack (global Z, base-plate-local Z shown in []; base plate top = cover mating bottom):
//
//   global 0      [0]      ────── base plate bottom (curved-bottom fillet)
//   global 1.7    [1.7]    ────── pocket floor (cradle's -5.1 bottom rests here)
//   global 7      [7]      ────── base plate top = cover mating bottom
//                                  (pegs extend UP from here)
//   global 11     [11]     ────── pegs tops (4 mm tall)
//   global 14     [14]     ────── cover face-plate bottom (cradle top meets here)
//   global 25.7   [25.7]   ────── cover top (bullnose peak)
//
// Outer footprint (91.5 × 46), corner radius, end-wall thicknesses, and
// corner-pillar screw-hole pattern all match base-v3-2piece / top-cover-
// windowed-screen-inlay-v3-2piece so the four outer sides print flush
// with the cover above.
//
// Export:
//   openscad -o base-plate-v1.3mf base-plate-v1.scad

$fn = 48;

// ============================================================
// Outer shell — match the cover / cradle 91.5 × 46 footprint so
// the base plate's four outer sides are flush with the cover above.
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 94.5;   // was 91.5 — +3 mm on -X side for TP4056
enclosure_outer_depth_along_y_axis_mm          = 46;
minus_x_end_wall_thickness_mm                  = 3;
plus_x_end_wall_thickness_mm                   = 1.2;
perimeter_long_side_wall_thickness_y_mm_base   = 2;
outer_case_top_view_corner_radius_mm           = 4;
outer_case_bottom_edge_fillet_radius_mm        = 4;       // was 2 — matches top cover bullnose for symmetry

// Plate Z: top flush with cover mating bottom. Pocket depth = cradle's
// below-cover-mating extension (5.1 mm) + 0.2 mm slop so the cradle
// settles cleanly on the pocket floor.
base_plate_total_height_z_mm                   = 11.5;   // 6.5 base + 5 mm raised mating edge
cradle_pocket_floor_thickness_mm                = 1.2;    // minimum printable floor
cradle_pocket_floor_z_mm                       = cradle_pocket_floor_thickness_mm; // = 1.2
cradle_pocket_depth_z_mm =
    base_plate_total_height_z_mm - cradle_pocket_floor_z_mm;                      // = 10.3

// ============================================================
// Cradle pocket — rectangle matching the cradle's outer footprint
// plus a small XY slop so the cradle drops in without binding.
// Cradle's outer footprint comes from aaa-cradle-insert-v1's
// plug_x_start/end and plug_y_start/end (3.3–90.0 × 2.3–43.7).
// ============================================================
cradle_plug_x_start_mm                         = 3.3;    // mirrors aaa-cradle
cradle_plug_x_end_mm                           = 93;   // was 90.0 — matches wider cradle
cradle_plug_y_start_mm                         = 2.3;
cradle_plug_y_end_mm                           = 43.7;
cradle_pocket_xy_slop_per_edge_mm              = 0.2;

cradle_pocket_x_start_mm =
    cradle_plug_x_start_mm - cradle_pocket_xy_slop_per_edge_mm;                   // = 3.1
cradle_pocket_x_end_mm =
    cradle_plug_x_end_mm + cradle_pocket_xy_slop_per_edge_mm;                     // = 90.2
cradle_pocket_y_start_mm =
    cradle_plug_y_start_mm - cradle_pocket_xy_slop_per_edge_mm;                   // = 2.1
cradle_pocket_y_end_mm =
    cradle_plug_y_end_mm + cradle_pocket_xy_slop_per_edge_mm;                     // = 43.9

// ============================================================
// Pegs — 4 cylindrical posts at the cover's screw-bore centers.
// Diameter is 0.2 mm under the cover's 3.2 mm M3 clearance bore
// (slip fit, can be pressed tighter by scaling peg diameter up).
// ============================================================
corner_pillar_square_side_length_mm            = 5;
m3_screw_clearance_bore_diameter_mm            = 3.2;
peg_diameter_mm                                = 3;
peg_height_above_pillar_mm                     = 3;    // was 4.0 above plate — now 3.0 above square pillar top
peg_tip_chamfer_mm                             = 0.4;

// ============================================================
// Pillar inward extensions — each corner pillar can be extended
// toward the board interior to act as a brace/shelf for the cradle
// or PCB above. Direction is automatic: -X pillars extend toward +X,
// +X pillars toward -X, etc. Set to 0 to disable each axis.
//
// Per-axis vs per-corner control: the *_uniform_mm knobs apply to
// all 4 corners. The per-corner override list can be set non-empty
// to override individual corners (4-element list, same order as
// peg_xy_positions_list: [-X-Y, +X-Y, -X+Y, +X+Y]). Each entry is
// [x_extension_mm, y_extension_mm].
// ============================================================
pillar_extension_x_inward_uniform_mm           = 5;     // all 4 pillars extend 5mm toward center along X
pillar_extension_y_inward_uniform_mm           = 5;     // all 4 pillars also extend 5mm along Y, hugging the long side walls
// Per-pillar overrides (4 entries, [x_inward, y_inward] each). Set to
// [] to use the uniform values above. Order: [-X-Y, +X-Y, -X+Y, +X+Y]
pillar_extension_per_corner_overrides          = [];    // e.g. [[5,0],[5,0],[5,0],[5,0]]

// ============================================================
// Battery cradle extrusions — curved shells along ±Y long sides
// that follow the AAA cylinder profile, rising above the base
// plate top to hold batteries flush from below when closed.
// ============================================================
aaa_bay_diameter_mm                            = 11.1;   // from cradle insert
aaa_bay_center_z_global_mm =
    base_plate_total_height_z_mm + 0.95;                  // = 7.95 (cradle bay center z=0.95 + base top)
aaa_bay_minus_y_center_y_mm                    = 7.85;   // from cradle insert
aaa_bay_plus_y_center_y_mm                     = 38.15;  // from cradle insert
// AAA bay X range — mirrored to +X side
aaa_bay_x_start_global_mm                      = 30.5;   // mirrored: 94.5 - 64.9
aaa_bay_length_along_x_mm                      = 47;   // from cradle insert
battery_cradle_extrusion_wall_mm               = 1.5;
battery_rail_height_reduction_mm               = 2.5;     // rails stop at Z = pocket_top - 2.5
battery_rail_depth_reduction_per_side_mm       = 2;       // shrink rail Y inward 2 mm each side (was 1)
// Lift the WHOLE rail (curved trough + cylinder cut) up by this amount.
// A solid support block fills the gap from pocket floor to lifted rail
// bottom, so the rail doesn't float. Increase to push the trough higher
// up the cylinder; set 0 to drop the rail back to the pocket floor.
battery_rail_z_lift_mm                         = 4;

// ============================================================
// Final Z clip — anything drawn above this Z gets sliced off.
// Catches battery rails / blocks / pegs that overshoot.
// Set to a very large number (e.g. 1000) to disable.
// ============================================================
max_z_clip_mm                                  = 14;

// ============================================================
// Height shave — keeps Z=0..shave_start_z untouched, deletes the
// next `shave_height_mm` band, and drops everything above down by
// the same amount. Net effect: total base height reduced by
// `shave_height_mm` while the curved bottom + first few mm of
// pocket walls are preserved exactly. Set shave_height_mm to 0 to
// disable.
// ============================================================
base_plate_shave_start_z_mm                    = 3;
base_plate_shave_height_mm                     = 2;

// USB-C port notch — on the +X wall (thin side), rounded to USB-C
// connector dimensions + 0.2 mm tolerance. Open on 3 sides (top + ±Y).
// Standard USB-C receptacle: 8.94 mm wide × 3.26 mm tall.
usb_c_connector_width_mm                       = 8.94;
usb_c_connector_height_mm                      = 3.26;
usb_c_tolerance_mm                             = 0.2;
usb_c_cutout_width_y_mm =
    usb_c_connector_width_mm + usb_c_tolerance_mm;         // = 9.14
usb_c_cutout_height_z_mm =
    usb_c_connector_height_mm + usb_c_tolerance_mm;        // = 3.46
usb_c_cutout_corner_r_mm =
    (usb_c_connector_height_mm + usb_c_tolerance_mm) / 2;  // = 1.73 (fully rounded ends)
usb_c_cutout_center_y_mm =
    enclosure_outer_depth_along_y_axis_mm / 2;              // = 23
usb_c_cutout_z_bottom_mm =
    base_plate_total_height_z_mm - usb_c_cutout_height_z_mm; // notch from top edge down
usb_c_wall_x_start_mm =
    enclosure_outer_width_along_x_axis_mm
      - plus_x_end_wall_thickness_mm;                       // +X wall inner face

// ============================================================
// USB-C support blocks — 2 small rectangular blocks under the USB-C
// cutout that brace the connector from below. Tweak the height knob
// below to raise/lower BOTH blocks together.
// ============================================================
usb_support_block_inset_from_wall_mm           = 5;       // -X inset of +X block from outer wall
usb_support_block_width_y_mm                   = 15;      // both blocks
usb_support_block_x_size_mm                    = 5;       // each block X depth
usb_support_block_x_gap_between_blocks_mm      = 5;       // -X gap between the two blocks
// Top of each block sits at: `usb_c_cutout_z_bottom_mm + usb_support_block_height_above_cutout_bottom_mm`.
// 0 = block tops flush with USB-C cutout bottom (just supports the connector).
// Negative = blocks shorter (sit below the cutout, leave a gap under the connector).
// Positive = blocks taller (poke into the USB-C cutout — only useful as alignment fingers).
usb_support_block_height_above_cutout_bottom_mm = 1;

// ============================================================
// USB sidewall brace — a single block bonded to the inner face of
// the +X end wall, sitting directly underneath the USB-C cutout.
// Acts as a structural brace for the USB-C connector body and the
// thin (1.2 mm) +X end wall. Y-centered on the USB-C cutout by
// default; depth (X) extends inward from the wall into the pocket.
//
// Z range: from `usb_sidewall_block_z_bottom_mm` up to a top that's
// `usb_sidewall_block_z_top_clearance_below_cutout_mm` below the
// USB-C cutout bottom (a small clearance keeps it from fouling the
// connector body — set to 0 to make the block flush against the
// cutout floor).
//
// Set `usb_sidewall_block_enabled = false` to omit it entirely.
// ============================================================
usb_sidewall_block_enabled                      = true;
usb_sidewall_block_width_y_mm                   = 10;     // Y extent of the block
usb_sidewall_block_depth_x_mm                   = 5;      // how far the block protrudes from the wall into the pocket
usb_sidewall_block_y_center_mm =
    usb_c_cutout_center_y_mm;                              // = 23 (matches USB cutout Y center)
usb_sidewall_block_z_bottom_mm                  = cradle_pocket_floor_z_mm; // pocket floor by default
usb_sidewall_block_z_top_clearance_below_cutout_mm = 0.2; // air gap between block top and USB-C cutout bottom

// ============================================================
// Pico retention block — single rectangular block sitting in the
// pocket to brace the Pico W from below. Positioned by the
// inset-from-(-X)-wall knob; size and height tunable below.
// Set the height knob to 0 to disable the block entirely.
// ============================================================
pico_retention_block_inset_from_minus_x_wall_mm = 18;     // distance from -X outer wall to -X edge of the block
pico_retention_block_width_y_mm                 = 15;     // Y width
pico_retention_block_x_size_mm                  = 5;      // X depth
pico_retention_block_y_center_mm =
    enclosure_outer_depth_along_y_axis_mm / 2;             // = 23 (dead-center Y by default)
// Block top Z = cradle_pocket_floor_z_mm + this. 0 = no block, fully sunk into the floor.
pico_retention_block_height_above_pocket_floor_mm = 8;

// Peg XY positions = cover screw-bore centers (pillar XY origin + pillar/2)
peg_xy_positions_list = [
    [minus_x_end_wall_thickness_mm
        + corner_pillar_square_side_length_mm / 2,
     perimeter_long_side_wall_thickness_y_mm_base
        + corner_pillar_square_side_length_mm / 2],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm / 2,
     perimeter_long_side_wall_thickness_y_mm_base
        + corner_pillar_square_side_length_mm / 2],
    [minus_x_end_wall_thickness_mm
        + corner_pillar_square_side_length_mm / 2,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_long_side_wall_thickness_y_mm_base
       - corner_pillar_square_side_length_mm / 2],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm / 2,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_long_side_wall_thickness_y_mm_base
       - corner_pillar_square_side_length_mm / 2],
];


// ========== Helpers (same shape language as base-v3-2piece) ==========

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}

module shell_with_curved_bottom(w, l, h, corner_r, fillet_r) {
    intersection() {
        minkowski() {
            translate([fillet_r, fillet_r, fillet_r])
                rounded_v_box(
                    w - 2 * fillet_r,
                    l - 2 * fillet_r,
                    h - fillet_r,
                    max(0.01, corner_r - fillet_r));
            sphere(r = fillet_r, $fn = 48);
        }
        translate([-1, -1, 0])
            cube([w + 2, l + 2, h]);
    }
}


// ========== Base plate v1 ==========

module base_plate_v1() {
    if (base_plate_shave_height_mm <= 0) {
        base_plate_v1_unshaved();
    } else {
        union() {
            // Bottom slab — preserved exactly: Z = 0 .. shave_start
            intersection() {
                base_plate_v1_unshaved();
                translate([-1, -1, -1])
                    cube([enclosure_outer_width_along_x_axis_mm + 2,
                          enclosure_outer_depth_along_y_axis_mm + 2,
                          base_plate_shave_start_z_mm + 1]);
            }
            // Upper portion — shifted down so the deleted band closes up.
            // 0.01 overlap into the bottom slab so the union seam is sealed.
            translate([0, 0, -base_plate_shave_height_mm])
                intersection() {
                    base_plate_v1_unshaved();
                    translate([-1, -1,
                               base_plate_shave_start_z_mm
                                 + base_plate_shave_height_mm
                                 - 0.01])
                        cube([enclosure_outer_width_along_x_axis_mm + 2,
                              enclosure_outer_depth_along_y_axis_mm + 2,
                              max_z_clip_mm + 10]);
                }
        }
    }
}

module base_plate_v1_unshaved() {
    // Final Z clip — everything in the union below is intersected
    // with this slab so nothing renders above max_z_clip_mm.
    intersection() {
    translate([-1, -1, -1])
        cube([enclosure_outer_width_along_x_axis_mm + 2,
              enclosure_outer_depth_along_y_axis_mm + 2,
              max_z_clip_mm + 1]);
    union() {
        // Shell with curved bottom fillet (matches base-v3-2piece
        // outer profile so the stack reads as one continuous case).
        difference() {
            shell_with_curved_bottom(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                base_plate_total_height_z_mm,
                outer_case_top_view_corner_radius_mm,
                outer_case_bottom_edge_fillet_radius_mm);

            // Cradle pocket — rectangular, opens UP from the base
            // plate top, stops 1.7 mm above the bottom so there's a
            // floor to support the cradle.
            translate([cradle_pocket_x_start_mm,
                       cradle_pocket_y_start_mm,
                       cradle_pocket_floor_z_mm])
                cube([cradle_pocket_x_end_mm - cradle_pocket_x_start_mm,
                      cradle_pocket_y_end_mm - cradle_pocket_y_start_mm,
                      base_plate_total_height_z_mm
                        - cradle_pocket_floor_z_mm + 0.1]);

            // USB-C port notch on +X wall — rounded to connector shape,
            // open on top, cut from the mating surface down.
            translate([usb_c_wall_x_start_mm - 0.1, 0, 0])
            hull() {
                // -Y rounded end
                translate([0,
                           usb_c_cutout_center_y_mm
                             - usb_c_cutout_width_y_mm / 2
                             + usb_c_cutout_corner_r_mm,
                           usb_c_cutout_z_bottom_mm + usb_c_cutout_corner_r_mm])
                    rotate([0, 90, 0])
                        cylinder(h = plus_x_end_wall_thickness_mm + 0.2,
                                 r = usb_c_cutout_corner_r_mm, $fn = 48);
                // +Y rounded end
                translate([0,
                           usb_c_cutout_center_y_mm
                             + usb_c_cutout_width_y_mm / 2
                             - usb_c_cutout_corner_r_mm,
                           usb_c_cutout_z_bottom_mm + usb_c_cutout_corner_r_mm])
                    rotate([0, 90, 0])
                        cylinder(h = plus_x_end_wall_thickness_mm + 0.2,
                                 r = usb_c_cutout_corner_r_mm, $fn = 48);
                // Top edge — extends past mating surface
                translate([0,
                           usb_c_cutout_center_y_mm - usb_c_cutout_width_y_mm / 2,
                           base_plate_total_height_z_mm])
                    cube([plus_x_end_wall_thickness_mm + 0.2,
                          usb_c_cutout_width_y_mm,
                          0.1]);
            }
        }

        // 4 square pillar bases — rise from the pocket floor to the
        // base plate top. Each pillar can be extended INWARD (toward
        // the board interior) along X and/or Y via the
        // `pillar_extension_*_inward_*` knobs at the top of the file —
        // useful as a brace/shelf for the cradle or PCB above.
        // Cylindrical pegs extend 3 mm above each pillar's footprint
        // CORNER (the original 5×5 mm pad) into the cover's blind M3
        // bore — peg XY is unchanged regardless of pillar extension.
        pillar_base_side_mm = corner_pillar_square_side_length_mm;                 // = 5
        peg_z_bottom_mm = base_plate_total_height_z_mm;                            // pegs start at plate top
        peg_z_shank_top_mm =
            peg_z_bottom_mm + peg_height_above_pillar_mm - peg_tip_chamfer_mm;    // = 9.6
        board_x_center_mm = enclosure_outer_width_along_x_axis_mm / 2;
        board_y_center_mm = enclosure_outer_depth_along_y_axis_mm / 2;
        for (i = [0 : len(peg_xy_positions_list) - 1]) {
            peg_xy      = peg_xy_positions_list[i];
            // Per-corner extension override — fall back to uniform values
            // when the override list is empty or shorter than 4.
            override_entry =
                len(pillar_extension_per_corner_overrides) > i
                  ? pillar_extension_per_corner_overrides[i]
                  : [pillar_extension_x_inward_uniform_mm,
                     pillar_extension_y_inward_uniform_mm];
            ext_x = override_entry[0];
            ext_y = override_entry[1];
            // Direction: pillars on -X half extend in +X; +X half in -X.
            // Same for Y.
            is_minus_x_pillar = peg_xy[0] < board_x_center_mm;
            is_minus_y_pillar = peg_xy[1] < board_y_center_mm;
            // Footprint origin (smaller XY corner) and size after extension.
            // For a -X pillar, the original 5x5 footprint stays anchored to
            // the wall (smaller X), and ext_x is added to the +X side, so
            // origin_x is unchanged and size_x = pillar_base + ext_x.
            // For a +X pillar, origin_x shifts -X by ext_x and size_x grows.
            pillar_origin_x = is_minus_x_pillar
                ? peg_xy[0] - pillar_base_side_mm / 2
                : peg_xy[0] - pillar_base_side_mm / 2 - ext_x;
            pillar_origin_y = is_minus_y_pillar
                ? peg_xy[1] - pillar_base_side_mm / 2
                : peg_xy[1] - pillar_base_side_mm / 2 - ext_y;
            pillar_size_x = pillar_base_side_mm + ext_x;
            pillar_size_y = pillar_base_side_mm + ext_y;

            // Pillar base — from pocket floor to plate top, with
            // optional inward extension toward the board center.
            translate([pillar_origin_x,
                       pillar_origin_y,
                       cradle_pocket_floor_z_mm])
                cube([pillar_size_x,
                      pillar_size_y,
                      base_plate_total_height_z_mm - cradle_pocket_floor_z_mm]);   // 5.3 mm

            // Cylindrical peg shank — 3 mm above plate top
            translate([peg_xy[0], peg_xy[1], peg_z_bottom_mm])
                cylinder(
                    h = peg_z_shank_top_mm - peg_z_bottom_mm,
                    d = peg_diameter_mm);

            // Chamfered peg tip
            translate([peg_xy[0], peg_xy[1], peg_z_shank_top_mm])
                cylinder(
                    h = peg_tip_chamfer_mm,
                    d1 = peg_diameter_mm,
                    d2 = peg_diameter_mm - 2 * peg_tip_chamfer_mm);
        }

        // Battery cradle troughs along ±Y long sides — solid fills
        // inside the pocket along each wall, with the battery cylinder
        // subtracted downward to carve concave channels into the plate
        // body. The cells drop down into the troughs from above.
        for (bay_params = [[aaa_bay_minus_y_center_y_mm, 0],
                           [aaa_bay_plus_y_center_y_mm, 1]]) {
            bay_y_center = bay_params[0];
            is_plus_y    = bay_params[1];
            inner_r = aaa_bay_diameter_mm / 2;
            // Fill from the enclosure wall inward past the battery edge,
            // reduced 1 mm per side in Y depth
            fill_y_start = is_plus_y
                ? bay_y_center - inner_r - 0.1 + battery_rail_depth_reduction_per_side_mm
                : perimeter_long_side_wall_thickness_y_mm_base;
            fill_y_end = is_plus_y
                ? enclosure_outer_depth_along_y_axis_mm
                    - perimeter_long_side_wall_thickness_y_mm_base
                : bay_y_center + inner_r + 0.1 - battery_rail_depth_reduction_per_side_mm;
            // Rail top — base plate top minus reduction, plus the lift.
            fill_z_top = base_plate_total_height_z_mm
                           - battery_rail_height_reduction_mm
                           + battery_rail_z_lift_mm;
            rail_z_bottom = cradle_pocket_floor_z_mm + battery_rail_z_lift_mm;

            // Support block — solid cube from pocket floor up to the
            // lifted rail bottom, same XY footprint as the rail.
            if (battery_rail_z_lift_mm > 0)
                translate([aaa_bay_x_start_global_mm,
                           fill_y_start,
                           cradle_pocket_floor_z_mm])
                    cube([aaa_bay_length_along_x_mm,
                          fill_y_end - fill_y_start,
                          battery_rail_z_lift_mm + 0.1]);

            difference() {
                // Rail body — solid cube from lifted floor up to top
                translate([aaa_bay_x_start_global_mm,
                           fill_y_start,
                           rail_z_bottom])
                    cube([aaa_bay_length_along_x_mm,
                          fill_y_end - fill_y_start,
                          fill_z_top - rail_z_bottom + 0.1]);

                // Subtract battery cylinder — also lifted by the same
                // amount so the trough rides higher up the cylinder.
                translate([aaa_bay_x_start_global_mm - 0.1,
                           bay_y_center,
                           aaa_bay_center_z_global_mm + battery_rail_z_lift_mm])
                    rotate([0, 90, 0])
                        cylinder(h = aaa_bay_length_along_x_mm + 0.2,
                                 r = inner_r);
            }
        }

        // USB-C support blocks — see top-of-file
        // `usb_support_block_height_above_cutout_bottom_mm` for the
        // tweakable height parameter (raises/lowers both blocks).
        usb_support_block_x_start =
            enclosure_outer_width_along_x_axis_mm
              - usb_support_block_inset_from_wall_mm
              - 2 * usb_support_block_x_size_mm;
        usb_support_block_y_start =
            usb_c_cutout_center_y_mm - usb_support_block_width_y_mm / 2;
        usb_support_block_z_height =
            usb_c_cutout_z_bottom_mm - cradle_pocket_floor_z_mm
              + usb_support_block_height_above_cutout_bottom_mm;
        // +X block (closer to the USB-C wall)
        translate([usb_support_block_x_start,
                   usb_support_block_y_start,
                   cradle_pocket_floor_z_mm])
            cube([usb_support_block_x_size_mm,
                  usb_support_block_width_y_mm,
                  usb_support_block_z_height]);
        // -X block (further from the USB-C wall, separated by gap)
        translate([usb_support_block_x_start
                     - usb_support_block_x_gap_between_blocks_mm
                     - usb_support_block_x_size_mm,
                   usb_support_block_y_start,
                   cradle_pocket_floor_z_mm])
            cube([usb_support_block_x_size_mm,
                  usb_support_block_width_y_mm,
                  usb_support_block_z_height]);

        // USB sidewall brace — single block bonded to the inner face of
        // the +X end wall, sitting directly underneath the USB-C cutout.
        // See top-of-file `usb_sidewall_block_*` for tunable knobs
        // (width Y, depth X, Y center, Z bottom, clearance below cutout).
        if (usb_sidewall_block_enabled) {
            usb_sidewall_inner_x_face_mm =
                enclosure_outer_width_along_x_axis_mm
                  - plus_x_end_wall_thickness_mm;             // = 93.3
            usb_sidewall_block_x_start =
                usb_sidewall_inner_x_face_mm
                  - usb_sidewall_block_depth_x_mm;
            usb_sidewall_block_y_start =
                usb_sidewall_block_y_center_mm
                  - usb_sidewall_block_width_y_mm / 2;
            usb_sidewall_block_z_top =
                usb_c_cutout_z_bottom_mm
                  - usb_sidewall_block_z_top_clearance_below_cutout_mm;
            usb_sidewall_block_z_size =
                usb_sidewall_block_z_top - usb_sidewall_block_z_bottom_mm;
            // Guard against degenerate / inverted blocks (e.g. if
            // someone sets z_bottom above the cutout bottom).
            if (usb_sidewall_block_z_size > 0)
                translate([usb_sidewall_block_x_start,
                           usb_sidewall_block_y_start,
                           usb_sidewall_block_z_bottom_mm])
                    cube([usb_sidewall_block_depth_x_mm,
                          usb_sidewall_block_width_y_mm,
                          usb_sidewall_block_z_size]);
        }

        // Pico retention block — single rectangular block in the pocket.
        // See top-of-file `pico_retention_block_*` for the tunable knobs
        // (X position via inset, Y center, dimensions, height).
        pico_retention_block_x_start =
            minus_x_end_wall_thickness_mm
              + pico_retention_block_inset_from_minus_x_wall_mm;
        pico_retention_block_y_start =
            pico_retention_block_y_center_mm
              - pico_retention_block_width_y_mm / 2;
        translate([pico_retention_block_x_start,
                   pico_retention_block_y_start,
                   cradle_pocket_floor_z_mm])
            cube([pico_retention_block_x_size_mm,
                  pico_retention_block_width_y_mm,
                  pico_retention_block_height_above_pocket_floor_mm]);
    }
    }  // close intersection (final Z clip at max_z_clip_mm)
}

base_plate_v1();
