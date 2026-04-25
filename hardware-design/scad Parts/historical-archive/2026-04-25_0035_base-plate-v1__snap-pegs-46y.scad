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
enclosure_outer_width_along_x_axis_mm          = 91.5;
enclosure_outer_depth_along_y_axis_mm          = 46;
minus_x_end_wall_thickness_mm                  = 3.0;
plus_x_end_wall_thickness_mm                   = 1.2;
perimeter_long_side_wall_thickness_y_mm_base   = 2;
outer_case_top_view_corner_radius_mm           = 4;
outer_case_bottom_edge_fillet_radius_mm        = 2;

// Plate Z: top flush with cover mating bottom. Pocket depth = cradle's
// below-cover-mating extension (5.1 mm) + 0.2 mm slop so the cradle
// settles cleanly on the pocket floor.
base_plate_total_height_z_mm                   = 7.0;
cradle_below_cover_mating_mm                   = 5.1;   // = |cradle plug_bottom_z_mm| in cover-local
cradle_pocket_vertical_slop_mm                 = 0.2;
cradle_pocket_depth_z_mm =
    cradle_below_cover_mating_mm + cradle_pocket_vertical_slop_mm;                // = 5.3
cradle_pocket_floor_z_mm =
    base_plate_total_height_z_mm - cradle_pocket_depth_z_mm;                      // = 1.7

// ============================================================
// Cradle pocket — rectangle matching the cradle's outer footprint
// plus a small XY slop so the cradle drops in without binding.
// Cradle's outer footprint comes from aaa-cradle-insert-v1's
// plug_x_start/end and plug_y_start/end (3.3–90.0 × 2.3–43.7).
// ============================================================
cradle_plug_x_start_mm                         = 3.3;    // mirrors aaa-cradle
cradle_plug_x_end_mm                           = 90.0;
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
peg_diameter_mm                                = 3.0;
peg_height_above_base_plate_top_mm             = 4.0;
peg_tip_chamfer_mm                             = 0.4;

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
                      cradle_pocket_depth_z_mm + 0.1]);
        }

        // 4 pegs — rise from the pocket floor so they're integral
        // columns (not floating rods above the hollow pocket). The
        // portion from pocket floor to base-plate top (Z=1.7→7) runs
        // up inside the pocket through where the cradle's corner
        // pillar cutouts are; the portion above base-plate top
        // (Z=7→11) pokes up into the cover's blind M3 bore.
        peg_z_bottom_mm = cradle_pocket_floor_z_mm;                                // = 1.7
        peg_z_shank_top_mm =
            base_plate_total_height_z_mm
              + peg_height_above_base_plate_top_mm
              - peg_tip_chamfer_mm;                                                // = 10.6
        peg_z_tip_top_mm =
            peg_z_shank_top_mm + peg_tip_chamfer_mm;                               // = 11.0
        for (peg_xy = peg_xy_positions_list) {
            // Shank — full-diameter cylinder from pocket floor up to
            // just below the chamfered tip.
            translate([peg_xy[0], peg_xy[1], peg_z_bottom_mm])
                cylinder(
                    h = peg_z_shank_top_mm - peg_z_bottom_mm,
                    d = peg_diameter_mm);
            // Chamfered tip — self-guides the peg into the cover's
            // M3 bore during assembly.
            translate([peg_xy[0], peg_xy[1], peg_z_shank_top_mm])
                cylinder(
                    h = peg_tip_chamfer_mm,
                    d1 = peg_diameter_mm,
                    d2 = peg_diameter_mm - 2 * peg_tip_chamfer_mm);
        }
    }
}

base_plate_v1();
