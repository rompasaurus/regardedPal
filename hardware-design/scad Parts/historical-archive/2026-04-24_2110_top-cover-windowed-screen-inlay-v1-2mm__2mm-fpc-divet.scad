// Dilder Rev 2 "extended with joystick" — TOP COVER (windowed, screen inlay, 2 mm divet) v1
//
// Variant of top-cover-windowed-screen-inlay-v1 with the FPC ribbon
// divet extending only 2 mm below the face-plate bottom (vs. 3 mm in
// the base file). Everything else — inlay, joystick hole, PCB pocket,
// mount bores, blind stack-bolt bores — is identical. Print both and
// compare fit before committing to a final divet depth.
//
// Export:
//   openscad -o top-cover-windowed-screen-inlay-v1-2mm.3mf top-cover-windowed-screen-inlay-v1-2mm.scad

$fn = 48;

// ============================================================
// Outer shell (flush with base-v1 and middle-platform-v1)
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 91.5;
enclosure_outer_depth_along_y_axis_mm          = 44;
outer_case_top_view_corner_radius_mm           = 4;
outer_case_top_edge_bullnose_radius_mm         = 4;

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
middle_platform_pedestal_protrusion_into_cover_z_mm = 5;

display_footprint_thickness_z_mm               = 7;   // was 5; +2 mm
                                                       // wiggle room for
                                                       // the display +
                                                       // FPC fold behind
                                                       // it before the
                                                       // face plate
// 0.5 mm was one perimeter + one thin top layer — the first print
// showed a hairline seam along the inlay's top edge where the face
// plate layer didn't fully close. Bumping to 0.7 mm gives the slicer
// enough material for a proper multi-layer top skin.
face_plate_thickness_z_mm                      = 0.7;

display_bottom_z_mm =
    middle_platform_pedestal_protrusion_into_cover_z_mm;      // = 5
display_top_z_mm =
    display_bottom_z_mm + display_footprint_thickness_z_mm;   // = 10
face_plate_bottom_z_mm                         = display_top_z_mm; // = 10
face_plate_top_z_mm =
    face_plate_bottom_z_mm + face_plate_thickness_z_mm;       // = 10.5
cover_total_height_z_mm =
    face_plate_top_z_mm + outer_case_top_edge_bullnose_radius_mm; // = 14.5

// ============================================================
// Display footprint — Waveshare 2.13", LANDSCAPE in Rev 2
// ============================================================
display_footprint_length_along_x_mm            = 65;
display_footprint_depth_along_y_mm             = 30;
print_fit_tolerance_slop_mm                    = 0.4;

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
// Screen inlay recess — carved UP into the face plate from the
// face-plate-bottom side, 3 mm deep. Lets the raw e-paper module
// (~1.18 mm glass + PCB) sit flush against the bezel material with
// room for the FPC fold-over behind it.
// ============================================================
screen_inlay_depth_z_mm                        = 3;
screen_inlay_xy_slop_per_edge_mm               = 0.3;  // press-fit clearance

screen_inlay_x_start_mm =
    display_minus_x_origin_mm - screen_inlay_xy_slop_per_edge_mm;
screen_inlay_x_end_mm =
    display_plus_x_end_mm + screen_inlay_xy_slop_per_edge_mm;
screen_inlay_y_start_mm =
    display_minus_y_origin_mm - screen_inlay_xy_slop_per_edge_mm;
screen_inlay_y_end_mm =
    display_plus_y_end_mm + screen_inlay_xy_slop_per_edge_mm;
screen_inlay_bottom_z_mm =
    face_plate_bottom_z_mm;                                         // = 10
screen_inlay_top_z_mm =
    face_plate_bottom_z_mm + screen_inlay_depth_z_mm;               // = 13

// ============================================================
// FPC ribbon divet — clearance pocket for the raw display's FPC
// cable, cut INTO the -X battery-end wall (on the opposite side of
// the display from the joystick hole). The cut thins the -X wall
// from 3 mm down to `fpc_ribbon_divet_wall_remaining_thickness_mm`
// in a 13 mm-wide Y band so the FPC has somewhere to exit the bay
// without blocking the board from seating flush in the inlay.
// ============================================================
fpc_ribbon_divet_width_along_y_mm              = 13;    // Y span
fpc_ribbon_divet_wall_remaining_thickness_mm   = 1.0;   // how much -X
                                                        // wall material
                                                        // remains under
                                                        // the divet
// Divet extends DOWN past the face-plate bottom by this much, so the
// FPC cable can bend down into the cavity without fighting the
// inlay ceiling / face-plate edge. Also clears any render clipping
// at the divet's Z-bottom edge where it would otherwise terminate
// exactly at the cavity's ceiling boundary.
fpc_ribbon_divet_z_extend_below_inlay_mm       = 2.0;
fpc_ribbon_divet_x_start_mm =
    fpc_ribbon_divet_wall_remaining_thickness_mm;       // inside the
                                                        // -X wall
fpc_ribbon_divet_x_end_mm =
    screen_inlay_x_start_mm;                            // flush with the
                                                        // inlay's -X edge
fpc_ribbon_divet_y_start_mm =
    display_y_centerline_mm - fpc_ribbon_divet_width_along_y_mm / 2;
fpc_ribbon_divet_y_end_mm =
    fpc_ribbon_divet_y_start_mm + fpc_ribbon_divet_width_along_y_mm;
fpc_ribbon_divet_z_bottom_mm =
    screen_inlay_bottom_z_mm - fpc_ribbon_divet_z_extend_below_inlay_mm;
fpc_ribbon_divet_z_top_mm =
    screen_inlay_top_z_mm;

// ============================================================
// Display viewing window cut through the face plate + bullnose
// ============================================================
// Dimensions matched to the Waveshare 2.13" module's actual VIEWABLE
// pixel area (measured against the first print, not the glass / bezel).
// Relative to the 50 × 25 window on the first print, the -X short side
// was moved INWARD by 2 mm (the +X short side stays put — the shift
// param is bumped +1 to compensate for the shorter length so only the
// -X edge moves), and the ±Y long sides each extend OUTWARD by 1 mm.
display_viewing_window_length_along_x_mm       = 48;  // was 50
display_viewing_window_depth_along_y_mm        = 24
;  // was 25
display_window_shift_toward_joystick_x_mm      = 2.8;   // was 2
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
// Joystick through-hole on the +X half of the face plate
// ============================================================
joystick_through_hole_diameter_mm              = 12;
joystick_through_hole_center_x_mm =
    (display_plus_x_end_mm
      + (enclosure_outer_width_along_x_axis_mm
          - plus_x_end_wall_thickness_mm)) / 2;
joystick_through_hole_center_y_mm              = display_y_centerline_mm;
joystick_hole_top_taper_width_mm               = 1.5;

// ============================================================
// Joystick PCB pocket — square indent on the face-plate underside
// centered on the joystick through-hole. A custom PCB carrying the
// joystick header drops UP into this pocket; 4 blind M3 bores at
// the pocket's corners take self-tapping screws (or heat-set inserts)
// from the PCB side.
// ============================================================
joystick_pcb_pocket_width_x_mm                 = 20;  // PCB X-span
joystick_pcb_pocket_depth_y_mm                 = 20;  // PCB Y-span
// Pocket depth matches the screen inlay depth so the pocket's ceiling
// sits flush with the inlay's ceiling — no visible step / fin between
// them where they meet at X = screen_inlay_x_end_mm.
joystick_pcb_pocket_depth_z_mm                 = screen_inlay_depth_z_mm;
joystick_pcb_mount_bore_diameter_mm            = 3.2; // M3 clearance
// Blind bore depth is bounded by the 1.5 mm of bullnose material
// remaining above the (now-flush) pocket/inlay ceiling. Leave a
// 0.3 mm cap above the bore top so no hole shows on the front face.
joystick_pcb_mount_bore_depth_z_mm             = 1.2;
joystick_pcb_mount_screw_inset_from_corner_mm  = 2.5; // inset of the 4
                                                      // bore centers from
                                                      // the pocket corners

// Pocket's -X edge is pulled flush with the inlay's +X edge (instead
// of being centered on the joystick hole) so there's no thin sliver
// of uncut material between the inlay and pocket. The PCB then has
// the joystick component slightly off-center from its geometric middle
// to line up with the joystick through-hole.
joystick_pcb_pocket_x_start_mm =
    screen_inlay_x_end_mm;
joystick_pcb_pocket_x_end_mm =
    joystick_pcb_pocket_x_start_mm + joystick_pcb_pocket_width_x_mm;
joystick_pcb_pocket_y_start_mm =
    joystick_through_hole_center_y_mm - joystick_pcb_pocket_depth_y_mm / 2;
joystick_pcb_pocket_y_end_mm =
    joystick_pcb_pocket_y_start_mm + joystick_pcb_pocket_depth_y_mm;
joystick_pcb_pocket_ceiling_z_mm =
    face_plate_bottom_z_mm + joystick_pcb_pocket_depth_z_mm;

joystick_pcb_mount_bore_xy_positions_list = [
    [joystick_pcb_pocket_x_start_mm + joystick_pcb_mount_screw_inset_from_corner_mm,
     joystick_pcb_pocket_y_start_mm + joystick_pcb_mount_screw_inset_from_corner_mm],
    [joystick_pcb_pocket_x_end_mm   - joystick_pcb_mount_screw_inset_from_corner_mm,
     joystick_pcb_pocket_y_start_mm + joystick_pcb_mount_screw_inset_from_corner_mm],
    [joystick_pcb_pocket_x_start_mm + joystick_pcb_mount_screw_inset_from_corner_mm,
     joystick_pcb_pocket_y_end_mm   - joystick_pcb_mount_screw_inset_from_corner_mm],
    [joystick_pcb_pocket_x_end_mm   - joystick_pcb_mount_screw_inset_from_corner_mm,
     joystick_pcb_pocket_y_end_mm   - joystick_pcb_mount_screw_inset_from_corner_mm],
];

// ============================================================
// Corner pillars — M3 bolt anchors. Bores are BLIND from below so
// no hole is visible on the cover's top face.
// ============================================================
corner_pillar_square_side_length_mm            = 5;
corner_pillar_inner_facing_corner_radius_mm    = 1;
m3_screw_clearance_hole_diameter_mm            = 3.2;
// Blind-hole ceiling: hole extends from the cover's mating bottom up
// to face_plate_bottom_z_mm, leaving the face plate + bullnose above
// as solid material hiding the bore from the front.
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


// ========== Helpers (shared shape language with base-v1) ==========

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


// ========== Top cover (windowed + screen inlay) ==========

module top_cover_windowed_screen_inlay() {
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

            // Corner pillars — full-height; the blind M3 bore is cut
            // later in the same difference().
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

        // Hollow interior below the face plate (preserving pillars).
        chamber_carve_preserving_pillars(
            cavity_inner_x_start_mm,
            cavity_inner_y_start_mm,
            -0.1,
            cavity_inner_x_end_mm - cavity_inner_x_start_mm,
            cavity_inner_y_end_mm - cavity_inner_y_start_mm,
            face_plate_bottom_z_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // Screen inlay recess — carved UP into the face-plate/bullnose
        // material from the face-plate-bottom side. 3 mm deep, sized
        // to the display footprint + inlay slop on every edge.
        translate([screen_inlay_x_start_mm,
                   screen_inlay_y_start_mm,
                   screen_inlay_bottom_z_mm - 0.1])
            cube([screen_inlay_x_end_mm - screen_inlay_x_start_mm,
                  screen_inlay_y_end_mm - screen_inlay_y_start_mm,
                  (screen_inlay_top_z_mm + 0.001)
                    - (screen_inlay_bottom_z_mm - 0.1)]);

        // FPC ribbon divet — cuts INTO the -X battery-end wall,
        // thinning it from 3 mm to ~1 mm over a 13 mm Y span
        // centered on the display Y centerline. Extends DOWN past
        // the face-plate bottom by fpc_ribbon_divet_z_extend_below_inlay_mm
        // into the cavity so the FPC can drop down behind the board
        // without hitting the inlay ceiling edge. Top of divet
        // punches 0.1 mm past the inlay ceiling to guarantee a
        // clean render boundary there.
        translate([fpc_ribbon_divet_x_start_mm,
                   fpc_ribbon_divet_y_start_mm,
                   fpc_ribbon_divet_z_bottom_mm - 0.1])
            cube([fpc_ribbon_divet_x_end_mm - fpc_ribbon_divet_x_start_mm,
                  fpc_ribbon_divet_y_end_mm - fpc_ribbon_divet_y_start_mm,
                  (fpc_ribbon_divet_z_top_mm + 0.1)
                    - (fpc_ribbon_divet_z_bottom_mm - 0.1)]);

        // Display viewing window — tapered cut through the remaining
        // material ABOVE the inlay recess (recess ceiling at z=13 up
        // through the bullnose top).
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

        // Joystick through-hole — tapered cut.
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
        // at face_plate_bottom_z_mm so the face plate + bullnose hide
        // the bore from the front.
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
                cylinder(h = m3_bore_top_z_mm + 0.1,
                         d = m3_screw_clearance_hole_diameter_mm);
        }

        // Joystick-PCB pocket — square indent carved UP into the
        // face-plate underside, centered on the joystick hole.
        translate([joystick_pcb_pocket_x_start_mm,
                   joystick_pcb_pocket_y_start_mm,
                   face_plate_bottom_z_mm - 0.1])
            cube([joystick_pcb_pocket_width_x_mm,
                  joystick_pcb_pocket_depth_y_mm,
                  joystick_pcb_pocket_depth_z_mm + 0.1]);

        // NOTE: the 4 blind joystick-PCB mount bores that used to sit
        // at the pocket's corners have been removed. On the first print
        // they showed as a circle of dimples around the joystick cutout
        // from below, and the joystick-PCB retention strategy hasn't
        // been decided yet (glue / press-fit / heat-set inserts are all
        // still on the table). Re-add here when the retention plan
        // lands — the params above (`joystick_pcb_mount_bore_*`,
        // `joystick_pcb_mount_bore_xy_positions_list`) are intentionally
        // kept so the geometry is one block away from returning.
    }
}

top_cover_windowed_screen_inlay();
