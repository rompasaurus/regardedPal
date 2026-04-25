// Dilder Rev 2 "extended with joystick" — MIDDLE PLATFORM v2 (Y=46 variant)
//
// Forked from middle-platform-v1.scad to match base-v2-thin-dual-10440's
// +2 mm outer-Y bump (44 → 46 mm). Only difference from v1 is the outer
// Y dimension; everything else (fill block X extent, pillar XY pattern,
// wall thicknesses, pillar screw centers) is unchanged so the full stack
// bolts up with the same M3 hardware in the same positions.
//
// Export:
//   openscad -o middle-platform-v2-46y.3mf middle-platform-v2-46y.scad

$fn = 48;

// ============================================================
// Outer shell dimensions (flush with base-v2)
// ============================================================
enclosure_outer_width_along_x_axis_mm           = 91.5;
enclosure_outer_depth_along_y_axis_mm           = 46;   // was 44 in v1; matches base-v2
middle_platform_short_portion_height_z_mm       = 8;
outer_case_top_view_corner_radius_mm            = 4;

// ============================================================
// Left-side internal fill pedestal (unchanged from v1)
// ============================================================
left_fill_interior_depth_along_x_mm             = 22;
left_fill_height_above_shell_top_mm             = 5;

// ============================================================
// Wall thicknesses (unchanged from v1)
// ============================================================
perimeter_long_side_wall_thickness_y_mm         = 8;
minus_x_end_wall_thickness_mm                   = 3.0;
plus_x_end_wall_thickness_mm                    = 1.2;

left_fill_end_x_mm =
    minus_x_end_wall_thickness_mm + left_fill_interior_depth_along_x_mm;  // = 25
left_fill_top_z_mm =
    middle_platform_short_portion_height_z_mm
      + left_fill_height_above_shell_top_mm;  // = 13

// ============================================================
// Corner pillars (XY origins auto-track the wider Y so screws
// stay aligned with base-v2's pillars)
// ============================================================
corner_pillar_square_side_length_mm             = 5;
corner_pillar_inner_facing_corner_radius_mm     = 1;
m3_screw_clearance_hole_diameter_mm             = 3.2;
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

// ========== Helpers (shared shape language) ==========

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
            rounded_v_box(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                middle_platform_short_portion_height_z_mm,
                outer_case_top_view_corner_radius_mm);

            translate([minus_x_end_wall_thickness_mm,
                       interior_y_start_mm,
                       0])
                cube([left_fill_interior_depth_along_x_mm,
                      interior_y_depth_mm,
                      left_fill_top_z_mm]);

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

        chamber_carve_preserving_pillars(
            right_interior_x_start_mm,
            interior_y_start_mm,
            -0.1,
            right_interior_x_end_mm - right_interior_x_start_mm,
            interior_y_depth_mm,
            middle_platform_short_portion_height_z_mm + 0.2,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

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
