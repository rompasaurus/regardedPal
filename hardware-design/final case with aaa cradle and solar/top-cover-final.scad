// FINAL — TOP COVER WINDOWED SCREEN INLAY
// Preset "4-26-final-face-for-now" baked in.
//
// Forked from top-cover-windowed-screen-inlay-v3-2piece.scad. The only
// functional change: there's no middle platform anymore, so the 5 mm
// pedestal-protrusion reservation at the cover's bottom is removed.
// The display PCB now sits directly on the base's rim at global z = 14
// (= local cover z = 0).
//
// Local Z layout (cover-local; z = 0 is the cover's mating bottom,
// flush with the base's top rim at global z = 14):
//   0 ─────────── cover mating bottom (= base top rim)
//                  display PCB bottom rests here (and on the Pico
//                  headers below through the middle Y).
//   7 ─────────── display top (FPC fold clearance 7 mm above PCB)
//   8 ──────────── face plate top (1 mm face plate)
//   12 ────────── bullnose top — cover total height
//
// Every Y/X feature (display inlay, viewing window, joystick, pillars)
// is identical to the v2-46y cover — just shifted down by 5 mm in cover-
// local Z because the pedestal reservation is gone.
//
// Export:
//   openscad -o top-cover-final.3mf top-cover-final.scad

$fn = 48;

// ============================================================
// Outer shell (flush with base-v3-2piece at Y=46)
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 94.5;   // was 91.5 — +3 mm on -X side for TP4056
enclosure_outer_depth_along_y_axis_mm          = 46;
outer_case_top_view_corner_radius_mm           = 4;
outer_case_top_edge_bullnose_radius_mm         = 4;
// Sphere radius for the top-edge rollover. Controls how gently
// the face plate curves into the side walls.
// Larger = gentler, more gradual curve. Smaller = tighter curve.
// Must be >= outer_case_top_view_corner_radius_mm or the corners gap.
face_plate_outer_edge_curve_radius_mm          = 2.2; // [0.5:0.1:12]

// ============================================================
// Asymmetric ±X end walls — match base-v3
// ============================================================
minus_x_end_wall_thickness_mm                  = 3.0;
plus_x_end_wall_thickness_mm                   = 1.2;
perimeter_long_side_wall_thickness_y_mm_base   = 2;

// ============================================================
// Cover Z layout — NO middle-platform pedestal reservation
// ============================================================
// v2 had `middle_platform_pedestal_protrusion_into_cover_z_mm = 5` here;
// in the 2-piece design the display PCB sits directly on the base rim at
// local z = 0 (display's ±Y overhang rests on the base; its middle sits
// on the Pico W header stack below).
middle_platform_pedestal_protrusion_into_cover_z_mm = 0;

display_footprint_thickness_z_mm               = 7;
face_plate_thickness_z_mm                      = 1;

display_bottom_z_mm =
    middle_platform_pedestal_protrusion_into_cover_z_mm;      // = 0
display_top_z_mm =
    display_bottom_z_mm + display_footprint_thickness_z_mm;   // = 7
face_plate_bottom_z_mm                         = display_top_z_mm; // = 7
face_plate_top_z_mm =
    face_plate_bottom_z_mm + face_plate_thickness_z_mm;       // = 8
cover_total_height_z_mm =
    face_plate_top_z_mm + outer_case_top_edge_bullnose_radius_mm; // = 12
wall_extension_below_mating_mm                 = 5;       // extend walls 5 mm below z=0

// ============================================================
// Display footprint & screen inlay (unchanged from v2-46y)
// ============================================================
display_footprint_length_along_x_mm            = 65;
display_footprint_depth_along_y_mm             = 30;
print_fit_tolerance_slop_mm                    = 0.4;

display_minus_x_origin_mm =
    minus_x_end_wall_thickness_mm
      + print_fit_tolerance_slop_mm;
display_plus_x_end_mm =
    display_minus_x_origin_mm + display_footprint_length_along_x_mm;
display_y_centerline_mm =
    enclosure_outer_depth_along_y_axis_mm / 2;                // = 23
display_minus_y_origin_mm =
    display_y_centerline_mm - display_footprint_depth_along_y_mm / 2;
display_plus_y_end_mm =
    display_minus_y_origin_mm + display_footprint_depth_along_y_mm;

screen_inlay_depth_z_mm                        = 3;
screen_inlay_xy_slop_per_edge_mm               = 0.3;
screen_inlay_y_slop_per_edge_mm                = 0.35;

screen_inlay_x_start_mm =
    display_minus_x_origin_mm - screen_inlay_xy_slop_per_edge_mm;
screen_inlay_x_end_mm =
    display_plus_x_end_mm + screen_inlay_xy_slop_per_edge_mm;
screen_inlay_y_start_mm =
    display_minus_y_origin_mm - screen_inlay_y_slop_per_edge_mm;
screen_inlay_y_end_mm =
    display_plus_y_end_mm + screen_inlay_y_slop_per_edge_mm;
screen_inlay_bottom_z_mm = face_plate_bottom_z_mm;
screen_inlay_top_z_mm =
    face_plate_bottom_z_mm + screen_inlay_depth_z_mm;

// ============================================================
// FPC ribbon divet (2 mm variant, unchanged)
// ============================================================
fpc_ribbon_divet_width_along_y_mm              = 13;
fpc_ribbon_divet_wall_remaining_thickness_mm   = 1.0;
fpc_ribbon_divet_z_extend_below_inlay_mm       = 2.0;
fpc_ribbon_divet_x_start_mm =
    fpc_ribbon_divet_wall_remaining_thickness_mm;
fpc_ribbon_divet_x_end_mm =
    screen_inlay_x_start_mm;
fpc_ribbon_divet_y_start_mm =
    display_y_centerline_mm - fpc_ribbon_divet_width_along_y_mm / 2;
fpc_ribbon_divet_y_end_mm =
    fpc_ribbon_divet_y_start_mm + fpc_ribbon_divet_width_along_y_mm;
fpc_ribbon_divet_z_bottom_mm =
    screen_inlay_bottom_z_mm - fpc_ribbon_divet_z_extend_below_inlay_mm;
fpc_ribbon_divet_z_top_mm =
    screen_inlay_top_z_mm;

// ============================================================
// Display viewing window (48 × 22, shift 2.8 — unchanged from v2-46y)
// ============================================================
display_viewing_window_length_along_x_mm       = 48;
display_viewing_window_depth_along_y_mm        = 22;
display_window_shift_toward_joystick_x_mm      = 2.8;
display_window_origin_x_mm =
    display_minus_x_origin_mm
      + (display_footprint_length_along_x_mm
          - display_viewing_window_length_along_x_mm) / 2
      + display_window_shift_toward_joystick_x_mm;
display_window_origin_y_mm =
    display_minus_y_origin_mm
      + (display_footprint_depth_along_y_mm
          - display_viewing_window_depth_along_y_mm) / 2;
display_window_top_taper_width_mm              = 2.0;

// ============================================================
// Joystick through-hole (+X half, centered on display Y centerline)
// ============================================================
joystick_through_hole_diameter_mm              = 12;
// Hardcoded to keep joystick at its original position despite the
// 3 mm -X enclosure extension (was the midpoint formula below).
joystick_through_hole_center_x_mm              = 79.35;
joystick_through_hole_center_y_mm              = display_y_centerline_mm;
joystick_hole_top_taper_width_mm               = 1.5;

// ============================================================
// Joystick PCB pocket (mount bores removed — see note)
// ============================================================
joystick_pcb_pocket_width_x_mm                 = 20;
joystick_pcb_pocket_depth_y_mm                 = 20;
joystick_pcb_pocket_depth_z_mm                 = screen_inlay_depth_z_mm;

joystick_pcb_pocket_x_start_mm =
    screen_inlay_x_end_mm;
joystick_pcb_pocket_x_end_mm =
    joystick_pcb_pocket_x_start_mm + joystick_pcb_pocket_width_x_mm;
joystick_pcb_pocket_y_start_mm =
    joystick_through_hole_center_y_mm - joystick_pcb_pocket_depth_y_mm / 2;
joystick_pcb_pocket_y_end_mm =
    joystick_pcb_pocket_y_start_mm + joystick_pcb_pocket_depth_y_mm;

// ============================================================
// Corner pillars — blind M3 bores capped at face plate bottom
// ============================================================
corner_pillar_square_side_length_mm            = 5;
corner_pillar_inner_facing_corner_radius_mm    = 1;
m3_screw_clearance_hole_diameter_mm            = 3.2;
m3_bore_top_z_mm                               = face_plate_bottom_z_mm;

corner_pillar_xy_origin_positions_list = [
    [minus_x_end_wall_thickness_mm,
     perimeter_long_side_wall_thickness_y_mm_base],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm,
     perimeter_long_side_wall_thickness_y_mm_base],
    [minus_x_end_wall_thickness_mm,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_long_side_wall_thickness_y_mm_base
       - corner_pillar_square_side_length_mm],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_long_side_wall_thickness_y_mm_base
       - corner_pillar_square_side_length_mm],
];


// ========== Helpers ==========

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

module shell_with_bullnose_top(w, l, h, case_r, top_r, edge_r = -1) {
    // edge_r controls the roundover where the flat face meets the
    // vertical walls. Smaller = flatter face, tighter edge radius.
    // 0.01 = basically flat with sharp edges.
    // case_r = original fully-domed top (sphere look).
    er = (edge_r < 0) ? case_r : edge_r;
    intersection() {
        minkowski() {
            // Core box: rounded XY corners, flat top, shrunk by er
            // so the minkowski sphere brings it back to full size.
            hull() {
                for (x = [case_r, w - case_r])
                    for (y = [case_r, l - case_r])
                        translate([x, y, 0])
                            cylinder(r = case_r - er, h = max(0.01, h - er), $fn = 48);
            }
            // Roundover sphere — only er radius, so only the edges curve.
            sphere(r = er, $fn = 24);
        }
        // Clip below z=0 (minkowski expands downward too)
        translate([-1, -1, 0])
            cube([w + 2, l + 2, h]);
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


// ========== Top cover (2-piece, 46 mm Y) ==========

module top_cover_windowed_screen_inlay_v3_2piece() {
    cavity_inner_x_start_mm = minus_x_end_wall_thickness_mm;
    cavity_inner_x_end_mm =
        enclosure_outer_width_along_x_axis_mm
          - plus_x_end_wall_thickness_mm;
    cavity_inner_y_start_mm = perimeter_long_side_wall_thickness_y_mm_base;
    cavity_inner_y_end_mm =
        enclosure_outer_depth_along_y_axis_mm
          - perimeter_long_side_wall_thickness_y_mm_base;

    difference() {
        union() {
            // Shell extended 5 mm below z=0 (the mating plane) so
            // the walls wrap further down around the base plate.
            translate([0, 0, -wall_extension_below_mating_mm])
            shell_with_bullnose_top(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                cover_total_height_z_mm + wall_extension_below_mating_mm,
                outer_case_top_view_corner_radius_mm,
                outer_case_top_edge_bullnose_radius_mm,
                face_plate_outer_edge_curve_radius_mm);

            for (corner_pillar_origin_xy = corner_pillar_xy_origin_positions_list) {
                pillar_rounds_positive_x_corner =
                    (corner_pillar_origin_xy[0]
                      < enclosure_outer_width_along_x_axis_mm / 2) ? 1 : 0;
                pillar_rounds_positive_y_corner =
                    (corner_pillar_origin_xy[1]
                      < enclosure_outer_depth_along_y_axis_mm / 2) ? 1 : 0;
                translate([corner_pillar_origin_xy[0],
                           corner_pillar_origin_xy[1],
                           -wall_extension_below_mating_mm])
                    pillar_one_round(
                        corner_pillar_square_side_length_mm,
                        corner_pillar_square_side_length_mm,
                        face_plate_top_z_mm + wall_extension_below_mating_mm,
                        corner_pillar_inner_facing_corner_radius_mm,
                        pillar_rounds_positive_x_corner,
                        pillar_rounds_positive_y_corner);
            }
        }

        chamber_carve_preserving_pillars(
            cavity_inner_x_start_mm,
            cavity_inner_y_start_mm,
            -wall_extension_below_mating_mm - 0.1,
            cavity_inner_x_end_mm - cavity_inner_x_start_mm,
            cavity_inner_y_end_mm - cavity_inner_y_start_mm,
            face_plate_bottom_z_mm + wall_extension_below_mating_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        translate([screen_inlay_x_start_mm,
                   screen_inlay_y_start_mm,
                   screen_inlay_bottom_z_mm - 0.1])
            cube([screen_inlay_x_end_mm - screen_inlay_x_start_mm,
                  screen_inlay_y_end_mm - screen_inlay_y_start_mm,
                  (screen_inlay_top_z_mm + 0.001)
                    - (screen_inlay_bottom_z_mm - 0.1)]);

        translate([fpc_ribbon_divet_x_start_mm,
                   fpc_ribbon_divet_y_start_mm,
                   fpc_ribbon_divet_z_bottom_mm - 0.1])
            cube([fpc_ribbon_divet_x_end_mm - fpc_ribbon_divet_x_start_mm,
                  fpc_ribbon_divet_y_end_mm - fpc_ribbon_divet_y_start_mm,
                  (fpc_ribbon_divet_z_top_mm + 0.1)
                    - (fpc_ribbon_divet_z_bottom_mm - 0.1)]);

        hull() {
            translate([display_window_origin_x_mm,
                       display_window_origin_y_mm,
                       face_plate_bottom_z_mm - 0.1])
                cube([display_viewing_window_length_along_x_mm,
                      display_viewing_window_depth_along_y_mm,
                      0.001]);
            translate([display_window_origin_x_mm
                         - display_window_top_taper_width_mm,
                       display_window_origin_y_mm
                         - display_window_top_taper_width_mm,
                       cover_total_height_z_mm + 0.1 - 0.001])
                cube([display_viewing_window_length_along_x_mm
                        + 2 * display_window_top_taper_width_mm,
                      display_viewing_window_depth_along_y_mm
                        + 2 * display_window_top_taper_width_mm,
                      0.001]);
        }

        translate([joystick_through_hole_center_x_mm,
                   joystick_through_hole_center_y_mm,
                   0])
            hull() {
                translate([0, 0, face_plate_bottom_z_mm - 0.1])
                    cylinder(
                        h = 0.001,
                        d = joystick_through_hole_diameter_mm);
                translate([0, 0,
                           cover_total_height_z_mm + 0.1 - 0.001])
                    cylinder(
                        h = 0.001,
                        d = joystick_through_hole_diameter_mm
                              + 2 * joystick_hole_top_taper_width_mm);
            }

        for (corner_pillar_origin_xy = corner_pillar_xy_origin_positions_list) {
            screw_hole_center_x_mm =
                corner_pillar_origin_xy[0]
                  + corner_pillar_square_side_length_mm / 2;
            screw_hole_center_y_mm =
                corner_pillar_origin_xy[1]
                  + corner_pillar_square_side_length_mm / 2;
            translate([screw_hole_center_x_mm,
                       screw_hole_center_y_mm,
                       -wall_extension_below_mating_mm - 0.1])
                cylinder(h = m3_bore_top_z_mm + wall_extension_below_mating_mm + 0.1,
                         d = m3_screw_clearance_hole_diameter_mm);
        }

        translate([joystick_pcb_pocket_x_start_mm,
                   joystick_pcb_pocket_y_start_mm,
                   face_plate_bottom_z_mm - 0.1])
            cube([joystick_pcb_pocket_width_x_mm,
                  joystick_pcb_pocket_depth_y_mm,
                  joystick_pcb_pocket_depth_z_mm + 0.1]);

        // NOTE: joystick-PCB mount bores remain removed (kept consistent
        // with the v1-2mm / pico2-v2-2mm / v2-46y lineage). Re-add when
        // the joystick-PCB retention plan lands.

    }
}

top_cover_windowed_screen_inlay_v3_2piece();
