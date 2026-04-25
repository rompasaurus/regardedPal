// Dilder Rev 2 "extended with joystick" — TOP COVER (windowed) v1
//
// Curved BULLNOSE top face (pattern from top-cover-v3-rounded-top) with
// a display viewing window and a joystick through-hole cut through the
// face plate + bullnose. No internal retention rails or lips — a
// separate retention plate bolting up through the 4 corner pillars is
// responsible for holding the display.
//
// Outer footprint (91.5 × 44) and corner-pillar XY positions match
// base-v1 and middle-platform-v1 so the M3 through-bolts line up through
// the entire stack. All 4 corner pillars run full-height from the cover
// floor up through the face plate.
//
// Display is offset as far -X as possible (over the battery half, which
// is ALSO the half supported from below by middle-platform-v1's solid
// fill pedestal). A separate through-hole punches the face plate on the
// +X half (center of the remaining right-hand region) — intended for a
// joystick shaft / control input above the ESP32 side.
//
// Export:
//   openscad -o top-cover-windowed-v1.3mf top-cover-windowed-v1.scad

$fn = 48;

// ============================================================
// Outer shell (flush with base-v1 and middle-platform-v1)
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 91.5;
enclosure_outer_depth_along_y_axis_mm          = 44;
outer_case_top_view_corner_radius_mm           = 4;   // matches base
// Bigger bullnose = more pronounced curve across the whole front face
// (see sketch IMG20260422215927.jpg — top edge rolls into the top face).
outer_case_top_edge_bullnose_radius_mm         = 4;   // curved TOP edge

// ============================================================
// Asymmetric ±X end walls — match base-v1 so pillar origins align
// ============================================================
minus_x_end_wall_thickness_mm                  = 3.0; // battery end
plus_x_end_wall_thickness_mm                   = 1.2; // USB-C end (thin)
perimeter_long_side_wall_thickness_y_mm_base   = 2;   // base's ±Y wall

// ============================================================
// Cover Z layout (cover-local: z=0 is the cover's mating bottom,
// flush with the middle-platform shell top at stack z = 22)
// ============================================================
// middle-platform-v1's -X solid fill pedestal pokes 5 mm above its
// 8 mm shell top. In cover-local coords that puts the pedestal top at
// z = 5, which is exactly where the display's underside sits — the
// pedestal supports the display's left half from below, while the
// snap lips catch the right half.
middle_platform_pedestal_protrusion_into_cover_z_mm = 5;

display_footprint_thickness_z_mm               = 5;   // Waveshare 2.13"
// Thin face plate — tapers further at the window edge via the chamfered
// window cut below, so the face over the screen reads as a thin bezel.
// Most of the visible "top-face taper" now happens inside the bullnose
// region above this plate; the plate itself is minimum-printable thin.
face_plate_thickness_z_mm                      = 0.5;

display_bottom_z_mm =
    middle_platform_pedestal_protrusion_into_cover_z_mm;      // = 5
display_top_z_mm =
    display_bottom_z_mm + display_footprint_thickness_z_mm;   // = 10
face_plate_bottom_z_mm                         = display_top_z_mm; // = 10, flush against display top
face_plate_top_z_mm =
    face_plate_bottom_z_mm + face_plate_thickness_z_mm;       // = 12
cover_total_height_z_mm =
    face_plate_top_z_mm + outer_case_top_edge_bullnose_radius_mm; // = 14

// ============================================================
// Display footprint — Waveshare 2.13", LANDSCAPE in Rev 2
// ============================================================
// Rev 1 had the display in portrait (30 × 65). For Rev 2 the enclosure
// long axis is X (91.5 mm), so the 65 mm side of the display lies along
// X and the 30 mm side along Y.
display_footprint_length_along_x_mm            = 65;
display_footprint_depth_along_y_mm             = 30;
print_fit_tolerance_slop_mm                    = 0.4;

// "Offset the window as far LEFT as possible" — display's -X edge butts
// against the -X inner wall face with just the print-slop gap.
display_minus_x_origin_mm =
    minus_x_end_wall_thickness_mm
      + print_fit_tolerance_slop_mm;                              // = 3.4
display_plus_x_end_mm =
    display_minus_x_origin_mm + display_footprint_length_along_x_mm; // = 68.4
display_y_centerline_mm =
    enclosure_outer_depth_along_y_axis_mm / 2;                    // = 22
display_minus_y_origin_mm =
    display_y_centerline_mm - display_footprint_depth_along_y_mm / 2; // = 7
display_plus_y_end_mm =
    display_minus_y_origin_mm + display_footprint_depth_along_y_mm;   // = 37

// ============================================================
// Display viewing window cut through the face plate + bullnose
// ============================================================
// Scaled from Rev 1's top-plate-windowed-v1 (25 × 50 opening on a
// 30 × 65 display), reoriented for landscape so the long axis of the
// window lies along X.
display_viewing_window_length_along_x_mm       = 50;
display_viewing_window_depth_along_y_mm        = 25;
// Nudge the window +X toward the joystick hole from the display-centered
// position. Asymmetric bezel: more material on the -X (battery) side,
// less on the +X (joystick) side.
display_window_shift_toward_joystick_x_mm      = 2;
display_window_origin_x_mm =
    display_minus_x_origin_mm
      + (display_footprint_length_along_x_mm
          - display_viewing_window_length_along_x_mm) / 2
      + display_window_shift_toward_joystick_x_mm;
display_window_origin_y_mm =
    display_minus_y_origin_mm
      + (display_footprint_depth_along_y_mm
          - display_viewing_window_depth_along_y_mm) / 2;        // centered on display in Y

// Top-of-window taper: the window opening widens from its true
// (display-matched) size at the face-plate bottom to a larger opening at
// the very top of the cover, so the bullnose + face-plate material visibly
// tapers DOWN into the screen edges (a shallow funnel around the window).
display_window_top_taper_width_mm              = 2.0;

// ============================================================
// Joystick through-hole on the +X half of the face plate
// ============================================================
// Centered in the open region between the display's +X end and the +X
// inner wall face, Y-centered on the enclosure axis. Default 12 mm Ø
// is a reasonable starting point for a thumb-joystick shaft with bezel
// clearance — tune to the real joystick module.
joystick_through_hole_diameter_mm              = 12;
joystick_through_hole_center_x_mm =
    (display_plus_x_end_mm
      + (enclosure_outer_width_along_x_axis_mm
          - plus_x_end_wall_thickness_mm)) / 2;
joystick_through_hole_center_y_mm              = display_y_centerline_mm;
// Chamfer on the joystick hole — matches the window taper language.
// The bore is true diameter at the face-plate bottom and widens by
// `joystick_hole_top_taper_width_mm` on radius at the top of the cover,
// so the bullnose rolls smoothly into the joystick opening instead of
// meeting it at a hard square edge.
joystick_hole_top_taper_width_mm               = 1.5;

// ============================================================
// Corner pillars — identical XY to base-v1 / middle-platform-v1
// ============================================================
corner_pillar_square_side_length_mm            = 5;
corner_pillar_inner_facing_corner_radius_mm    = 1;
m3_screw_clearance_hole_diameter_mm            = 3.2;

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

// Rounded-rectangle PRISM with a BULLNOSE top edge — the curved top
// face (lifted from top-cover-v3-rounded-top). Top face is clipped flat
// at `h`, and the transition from the vertical walls to the top face is
// a curve with radius ≈ `top_r`.
module shell_with_bullnose_top(w, l, h, case_r, top_r) {
    intersection() {
        hull() {
            for (x = [case_r, w - case_r])
                for (y = [case_r, l - case_r]) {
                    translate([x, y, 0])
                        cylinder(r = case_r, h = h - top_r, $fn = 48);
                    translate([x, y, h - top_r])
                        sphere(r = case_r, $fn = 24);
                }
        }
        translate([-1, -1, 0])
            cube([w + 2, l + 2, h]);
    }
}

// Cavity carve that preserves the 4 corner pillars (so M3 screw holes
// stay fully embedded in solid pillar material).
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


// ========== Top cover (windowed) ==========

module top_cover_windowed() {
    // Cavity extents (below the face plate, full inner footprint).
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
            shell_with_bullnose_top(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                cover_total_height_z_mm,
                outer_case_top_view_corner_radius_mm,
                outer_case_top_edge_bullnose_radius_mm);

            // Corner pillars — full-height from cover floor up through
            // the face plate so the M3 clearance bore is embedded in
            // solid material top-to-bottom and the face plate ties into
            // every pillar. Only the inward-facing corner is rounded.
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
                        face_plate_top_z_mm,
                        corner_pillar_inner_facing_corner_radius_mm,
                        pillar_rounds_positive_x_corner,
                        pillar_rounds_positive_y_corner);
            }
        }

        // Hollow interior below the face plate, preserving each corner
        // pillar's full-height column so the M3 bore stays in solid
        // material.
        chamber_carve_preserving_pillars(
            cavity_inner_x_start_mm,
            cavity_inner_y_start_mm,
            -0.1,
            cavity_inner_x_end_mm - cavity_inner_x_start_mm,
            cavity_inner_y_end_mm - cavity_inner_y_start_mm,
            face_plate_bottom_z_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // Display viewing window — tapered cut. Face-plate-bottom
        // opening matches the true window size; widens by
        // 2·taper at the top of the cover so the face plate + bullnose
        // read as a shallow funnel around the screen edges.
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

        // Joystick through-hole — tapered cut like the display window.
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

        // BLIND M3 bores — open at the cover's mating bottom, capped
        // at face_plate_bottom_z_mm so the face plate + bullnose above
        // hide the bore from the front view.
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
                cylinder(h = face_plate_bottom_z_mm + 0.1,
                         d = m3_screw_clearance_hole_diameter_mm);
        }
    }
}

top_cover_windowed();
