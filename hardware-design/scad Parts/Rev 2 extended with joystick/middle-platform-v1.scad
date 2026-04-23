// Dilder Rev 2 "extended with joystick" — MIDDLE PLATFORM v1
//
// Mid-stack platform that sits on top of base-v1, under the top cover.
// Outer footprint is a uniform 8 mm-tall shell — no stepped outer
// profile. An internal solid pedestal on the -X end rises above the
// shell top.
//
// Walls:
//   - ±Y long side walls: 8 mm
//   - -X end wall: 3 mm (battery end, matches base-v1)
//   - +X end wall: 1.2 mm (USB-C end, matches base-v1's thin wall)
//
// Internal fill (only feature that goes above the 8 mm outer top):
//   - Solid block on the -X interior: 22 mm along X (from the -X inner
//     wall face inward), full interior Y (between the ±Y walls), from
//     the floor up to 5 mm above the shell top (so top sits at z = 13).
//
// Corner pillars stay at the same XY positions as base-v1 so the M3
// through-bolts align through the whole stack. All pillars are 8 mm
// tall (the fill block sits in a different Y band than the pillars, so
// they don't interact).
//
// Export:
//   openscad -o middle-platform-v1.3mf middle-platform-v1.scad

$fn = 48;

// ============================================================
// Outer shell dimensions (flush with base-v1)
// ============================================================
enclosure_outer_width_along_x_axis_mm           = 91.5;  // matches base (battery bay +2 mm)
enclosure_outer_depth_along_y_axis_mm           = 44;
middle_platform_short_portion_height_z_mm       = 8;
outer_case_top_view_corner_radius_mm            = 4;

// ============================================================
// Left-side internal fill (solid pedestal poking above the 8 mm top)
// ============================================================
// Interior fill depth along X, measured from the -X inner wall face.
left_fill_interior_depth_along_x_mm             = 22;
// How far the fill sticks up PAST the 8 mm shell top.
left_fill_height_above_shell_top_mm             = 5;

// ============================================================
// Wall thicknesses (only relevant around the hollow right portion)
// ============================================================
perimeter_long_side_wall_thickness_y_mm         = 8;    // ±Y long walls
minus_x_end_wall_thickness_mm                   = 3.0;  // battery end
plus_x_end_wall_thickness_mm                    = 1.2;  // USB-C end (thin)

// Interior X at which the fill block ends (its -X face sits at the -X
// inner wall). Also marks where the hollow right-side interior begins.
left_fill_end_x_mm =
    minus_x_end_wall_thickness_mm + left_fill_interior_depth_along_x_mm;  // = 25

// Absolute Z of the fill top (5 mm above the 8 mm shell top).
left_fill_top_z_mm =
    middle_platform_short_portion_height_z_mm
      + left_fill_height_above_shell_top_mm;  // = 13

// ============================================================
// Corner pillars (same XY origins as base-v1 so screws line up)
// ============================================================
corner_pillar_square_side_length_mm             = 5;
corner_pillar_inner_facing_corner_radius_mm     = 1;
m3_screw_clearance_hole_diameter_mm             = 3.2;

// Pillar Y origin uses base-v1's 2 mm long-wall thickness (NOT this
// file's 9 mm), so the screw centers don't shift sideways vs. the base.
perimeter_outer_wall_thickness_mm_base          = 2;

corner_pillar_xy_origin_positions_list = [
    [minus_x_end_wall_thickness_mm,
     perimeter_outer_wall_thickness_mm_base],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm,
     perimeter_outer_wall_thickness_mm_base],
    [minus_x_end_wall_thickness_mm,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_outer_wall_thickness_mm_base
       - corner_pillar_square_side_length_mm],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_outer_wall_thickness_mm_base
       - corner_pillar_square_side_length_mm],
];

// ========== Helpers (shared shape language with base-v1) ==========

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}

module pillar_one_round(w, l, h, r, round_x, round_y) {
    tiny = 0.01;
    hull() {
        for (ix = [0, 1])
            for (iy = [0, 1]) {
                cr = (ix == round_x && iy == round_y) ? r : tiny;
                translate([cr + ix * (w - 2*cr), cr + iy * (l - 2*cr), 0])
                    cylinder(r = cr, h = h, $fn = 48);
            }
    }
}

module chamber_carve_preserving_pillars(origin_x, origin_y, origin_z,
                                        width_x, depth_y, height_z,
                                        pillar_xy_list, pillar_side) {
    difference() {
        translate([origin_x, origin_y, origin_z])
            cube([width_x, depth_y, height_z]);
        for (pillar_origin_xy = pillar_xy_list)
            translate([pillar_origin_xy[0], pillar_origin_xy[1], origin_z - 0.5])
                cube([pillar_side, pillar_side, height_z + 1]);
    }
}

// ========== Middle platform ==========

module middle_platform() {
    right_interior_x_start_mm = left_fill_end_x_mm;
    right_interior_x_end_mm =
        enclosure_outer_width_along_x_axis_mm - plus_x_end_wall_thickness_mm;
    interior_y_start_mm = perimeter_long_side_wall_thickness_y_mm;
    interior_y_depth_mm =
        enclosure_outer_depth_along_y_axis_mm
          - 2 * perimeter_long_side_wall_thickness_y_mm;

    difference() {
        union() {
            // Outer shell — uniform 8 mm tall, flat top. The internal
            // fill block below is the only feature that pokes above this.
            rounded_v_box(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                middle_platform_short_portion_height_z_mm,
                outer_case_top_view_corner_radius_mm);

            // Internal fill pedestal on the -X interior. -X face flush
            // with the -X inner wall; ±Y faces flush with the ±Y inner
            // wall faces; top sits 5 mm above the 8 mm shell top.
            translate([minus_x_end_wall_thickness_mm,
                       interior_y_start_mm,
                       0])
                cube([left_fill_interior_depth_along_x_mm,
                      interior_y_depth_mm,
                      left_fill_top_z_mm]);

            // Corner pillars — all uniform 8 mm (the fill block is in a
            // different Y band than any pillar, so pillars stay short).
            for (corner_pillar_origin_xy = corner_pillar_xy_origin_positions_list) {
                pillar_rounds_positive_x_corner =
                    (corner_pillar_origin_xy[0]
                      < enclosure_outer_width_along_x_axis_mm / 2) ? 1 : 0;
                pillar_rounds_positive_y_corner =
                    (corner_pillar_origin_xy[1]
                      < enclosure_outer_depth_along_y_axis_mm / 2) ? 1 : 0;
                translate([corner_pillar_origin_xy[0],
                           corner_pillar_origin_xy[1],
                           0])
                    pillar_one_round(
                        corner_pillar_square_side_length_mm,
                        corner_pillar_square_side_length_mm,
                        middle_platform_short_portion_height_z_mm,
                        corner_pillar_inner_facing_corner_radius_mm,
                        pillar_rounds_positive_x_corner,
                        pillar_rounds_positive_y_corner);
            }
        }

        // Interior carve — only on the right (hollow) portion. The fill
        // block's X range (x < 25) is left untouched.
        chamber_carve_preserving_pillars(
            right_interior_x_start_mm,
            interior_y_start_mm,
            -0.1,
            right_interior_x_end_mm - right_interior_x_start_mm,
            interior_y_depth_mm,
            middle_platform_short_portion_height_z_mm + 0.2,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // Screw pass-through holes through every pillar (uniform 8 mm).
        for (corner_pillar_origin_xy = corner_pillar_xy_origin_positions_list) {
            screw_hole_center_x_mm =
                corner_pillar_origin_xy[0]
                  + corner_pillar_square_side_length_mm / 2;
            screw_hole_center_y_mm =
                corner_pillar_origin_xy[1]
                  + corner_pillar_square_side_length_mm / 2;
            translate([screw_hole_center_x_mm,
                       screw_hole_center_y_mm,
                       -0.1])
                cylinder(
                    h = middle_platform_short_portion_height_z_mm + 0.2,
                    d = m3_screw_clearance_hole_diameter_mm);
        }
    }
}

middle_platform();
