// Dilder Rev 2 "extended with joystick" — BASE v4, 2-PIECE WITH BATTERY SLOTS
//
// Evolution of base-v3-2piece. Fixes the two problems with v3:
//   (1) Cells were trapped in sealed bays once the top cover was on — no
//       way to insert/swap them. Fix: two rectangular slots cut through
//       the -X end wall, one per cell bay, matching each bay's Y×Z
//       cross-section. Cells slide in from outside before cover install;
//       spring contacts at the -X end press them +X against the solid
//       +X stop. If you want a closed case, print a small battery-door
//       clip that snaps onto the -X end over the slots.
//   (2) No cover-base interlock. Fix: two raised lips running along X,
//       seated on the cell-bay ceiling material at the ±Y inner edge of
//       the Pico chamber (i.e., *where the battery won't be* — above the
//       cell bays, but against the Pico chamber's Y wall). The lips
//       protrude 1 mm above the case top at z = 14 → z = 15, so when
//       the cover drops on they extend into the cover's internal cavity
//       along the Pico chamber's ±Y edges, stiffening the joint and
//       providing a visual/alignment feature along the non-battery edges.
//
// Everything else is identical to base-v3-2piece.
//
// Export:
//   openscad -o base-v4-2piece-open.3mf base-v4-2piece-open.scad

$fn = 48;

// ============================================================
// Outer shell
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 91.5;
enclosure_outer_depth_along_y_axis_mm          = 46;
enclosure_total_height_along_z_axis_mm         = 14;
perimeter_outer_wall_thickness_mm              = 2;
base_floor_plate_thickness_mm                  = 2;
outer_case_top_view_corner_radius_mm           = 4;
outer_case_bottom_edge_fillet_radius_mm        = 2;

plus_x_usb_side_end_wall_thickness_mm          = 1.2;
minus_x_battery_side_end_wall_thickness_mm     = 3.0;

// ============================================================
// 10440 Li-ion cell bays
// ============================================================
cell_10440_diameter_mm                         = 10.0;
cell_10440_length_mm                           = 44.0;
cell_bay_radial_slop_mm                        = 0.3;
cell_bay_axial_slop_mm                         = 1.0;
cell_contact_space_per_end_mm                  = 2.0;

cell_bay_width_along_y_mm =
    cell_10440_diameter_mm + 2 * cell_bay_radial_slop_mm;    // = 10.6
cell_bay_length_along_x_mm =
    cell_10440_length_mm
      + 2 * cell_contact_space_per_end_mm
      + cell_bay_axial_slop_mm;                              // = 49.0
cell_bay_height_above_floor_mm =
    cell_10440_diameter_mm;                                  // = 10

cell_bay_start_x_position_mm                   =
    minus_x_battery_side_end_wall_thickness_mm;
cell_bay_end_x_position_mm =
    cell_bay_start_x_position_mm + cell_bay_length_along_x_mm;
cell_bay_ceiling_z_mm =
    base_floor_plate_thickness_mm + cell_bay_height_above_floor_mm; // = 12

// ============================================================
// Cell contact mounting slots (unchanged from v3)
// ============================================================
cell_contact_mount_slot_width_along_y_mm       = 3.5;
cell_contact_mount_slot_depth_along_x_mm       = 2.0;
cell_contact_mount_slot_height_along_z_mm      = 4.0;
cell_contact_mount_slot_center_z_mm =
    base_floor_plate_thickness_mm
      + cell_10440_diameter_mm / 2;                          // = 7

// ============================================================
// Pico W chamber
// ============================================================
pico_w_board_width_along_y_mm                  = 21.0;
pico_w_board_length_along_x_mm                 = 51.0;
print_fit_tolerance_slop_mm                    = 0.4;
pico_w_chamber_width_along_y_mm =
    pico_w_board_width_along_y_mm + 2 * print_fit_tolerance_slop_mm; // = 21.8
pico_w_shelf_top_z_mm                          = 8.0;

// ============================================================
// USB-C cutout
// ============================================================
usb_c_panel_cutout_width_along_y_axis_mm       = 8.8;
usb_c_port_body_height_above_pcb_mm            = 2.6;
usb_c_cutout_extra_height_allowance_mm         = 0.2;
usb_c_cutout_top_extra_height_mm               = 0.5;
usb_c_panel_cutout_height_along_z_axis_mm =
    usb_c_port_body_height_above_pcb_mm
      + usb_c_cutout_extra_height_allowance_mm
      + usb_c_cutout_top_extra_height_mm;                    // = 3.3
usb_c_port_body_recess_depth_into_enclosure_mm = 8.0;
usb_c_port_vertical_center_z_mm                = 9;
usb_c_cutout_effective_center_z_mm =
    usb_c_port_vertical_center_z_mm
      + usb_c_cutout_top_extra_height_mm / 2;                // = 9.25
usb_c_port_center_y_positions_list = [
    enclosure_outer_depth_along_y_axis_mm / 2,
];

// ============================================================
// Corner pillars
// ============================================================
corner_pillar_square_side_length_mm            = 5;
corner_pillar_inner_facing_corner_radius_mm    = 1;
m3_screw_clearance_hole_diameter_mm            = 3.2;

corner_pillar_xy_origin_positions_list = [
    [minus_x_battery_side_end_wall_thickness_mm,
     perimeter_outer_wall_thickness_mm],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_usb_side_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm,
     perimeter_outer_wall_thickness_mm],
    [minus_x_battery_side_end_wall_thickness_mm,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_outer_wall_thickness_mm
       - corner_pillar_square_side_length_mm],
    [enclosure_outer_width_along_x_axis_mm
       - plus_x_usb_side_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm,
     enclosure_outer_depth_along_y_axis_mm
       - perimeter_outer_wall_thickness_mm
       - corner_pillar_square_side_length_mm],
];

// ============================================================
// NEW in v4: raised lips along the Pico chamber ±Y boundary,
// seated on the cell-bay ceiling (i.e., NOT above the cells).
// These protrude 1 mm above the case top rim into the top
// cover's internal cavity on the non-battery edges.
// ============================================================
raised_lip_height_above_case_top_mm            = 1.0;
raised_lip_width_along_y_mm                    = 1.5;   // 1.5 mm thick (Y)
// Lips sit on the cell-bay ceiling, with their +Y edge flush with the
// Pico chamber Y boundary (so they don't overhang into the chamber).


// ========== Helpers ==========

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

module shell_with_curved_bottom(w, l, h, corner_r, fillet_r) {
    intersection() {
        minkowski() {
            translate([fillet_r, fillet_r, fillet_r])
                rounded_v_box(w - 2 * fillet_r,
                              l - 2 * fillet_r,
                              h - fillet_r,
                              max(0.01, corner_r - fillet_r));
            sphere(r = fillet_r, $fn = 48);
        }
        translate([-1, -1, 0])
            cube([w + 2, l + 2, h]);
    }
}

module stadium_cutout_extruded_along_x(depth_along_x_mm,
                                       total_width_along_y_mm,
                                       total_height_along_z_mm) {
    end_cap_radius_mm = total_height_along_z_mm / 2;
    end_cap_y_offset_from_center_mm =
        total_width_along_y_mm / 2 - end_cap_radius_mm;
    hull() {
        for (side_sign = [-1, 1])
            translate([0,
                       side_sign * end_cap_y_offset_from_center_mm,
                       0])
                rotate([0, 90, 0])
                    cylinder(r = end_cap_radius_mm,
                             h = depth_along_x_mm,
                             $fn = 48);
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


// ========== Base v4 ==========

module base_v4_2piece_open() {
    pico_w_chamber_start_y_mm =
        (enclosure_outer_depth_along_y_axis_mm
          - pico_w_chamber_width_along_y_mm) / 2;             // = 12.1
    pico_w_chamber_end_y_mm =
        pico_w_chamber_start_y_mm + pico_w_chamber_width_along_y_mm; // = 33.9
    minus_y_cell_bay_start_y_mm = perimeter_outer_wall_thickness_mm;   // = 2
    minus_y_cell_bay_end_y_mm   = pico_w_chamber_start_y_mm;           // = 12.1
    plus_y_cell_bay_start_y_mm  = pico_w_chamber_end_y_mm;             // = 33.9
    plus_y_cell_bay_end_y_mm =
        enclosure_outer_depth_along_y_axis_mm
          - perimeter_outer_wall_thickness_mm;                // = 44

    inner_x_start_mm = minus_x_battery_side_end_wall_thickness_mm;    // = 3
    inner_x_end_mm =
        enclosure_outer_width_along_x_axis_mm
          - plus_x_usb_side_end_wall_thickness_mm;                    // = 90.3

    union() {
        difference() {
            union() {
                shell_with_curved_bottom(
                    enclosure_outer_width_along_x_axis_mm,
                    enclosure_outer_depth_along_y_axis_mm,
                    enclosure_total_height_along_z_axis_mm,
                    outer_case_top_view_corner_radius_mm,
                    outer_case_bottom_edge_fillet_radius_mm);

                intersection() {
                    union() {
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
                                    enclosure_total_height_along_z_axis_mm,
                                    corner_pillar_inner_facing_corner_radius_mm,
                                    pillar_rounds_positive_x_corner,
                                    pillar_rounds_positive_y_corner);
                        }
                    }
                    shell_with_curved_bottom(
                        enclosure_outer_width_along_x_axis_mm,
                        enclosure_outer_depth_along_y_axis_mm,
                        enclosure_total_height_along_z_axis_mm,
                        outer_case_top_view_corner_radius_mm,
                        outer_case_bottom_edge_fillet_radius_mm);
                }
            }

            // ---- -Y cell bay (z=2 → z=12, ceiling at 12) ----
            chamber_carve_preserving_pillars(
                cell_bay_start_x_position_mm,
                minus_y_cell_bay_start_y_mm,
                base_floor_plate_thickness_mm,
                cell_bay_end_x_position_mm - cell_bay_start_x_position_mm,
                minus_y_cell_bay_end_y_mm - minus_y_cell_bay_start_y_mm,
                cell_bay_height_above_floor_mm + 0.1,
                corner_pillar_xy_origin_positions_list,
                corner_pillar_square_side_length_mm);

            // ---- +Y cell bay ----
            chamber_carve_preserving_pillars(
                cell_bay_start_x_position_mm,
                plus_y_cell_bay_start_y_mm,
                base_floor_plate_thickness_mm,
                cell_bay_end_x_position_mm - cell_bay_start_x_position_mm,
                plus_y_cell_bay_end_y_mm - plus_y_cell_bay_start_y_mm,
                cell_bay_height_above_floor_mm + 0.1,
                corner_pillar_xy_origin_positions_list,
                corner_pillar_square_side_length_mm);

            // ---- Pico W chamber (z=8 → case top z=14) ----
            chamber_carve_preserving_pillars(
                inner_x_start_mm,
                pico_w_chamber_start_y_mm,
                pico_w_shelf_top_z_mm,
                inner_x_end_mm - inner_x_start_mm,
                pico_w_chamber_width_along_y_mm,
                enclosure_total_height_along_z_axis_mm
                  - pico_w_shelf_top_z_mm + 0.1,
                corner_pillar_xy_origin_positions_list,
                corner_pillar_square_side_length_mm);

            // ---- M3 pass-throughs ----
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
                        h = enclosure_total_height_along_z_axis_mm + 0.2,
                        d = m3_screw_clearance_hole_diameter_mm);
            }

            // ---- USB-C cutout ----
            for (usb_c_port_center_y_mm = usb_c_port_center_y_positions_list) {
                usb_c_cutout_total_depth_x_mm =
                    plus_x_usb_side_end_wall_thickness_mm
                      + usb_c_port_body_recess_depth_into_enclosure_mm
                      + 0.2;
                translate([enclosure_outer_width_along_x_axis_mm
                             - plus_x_usb_side_end_wall_thickness_mm
                             - usb_c_port_body_recess_depth_into_enclosure_mm,
                           usb_c_port_center_y_mm,
                           usb_c_cutout_effective_center_z_mm])
                    stadium_cutout_extruded_along_x(
                        usb_c_cutout_total_depth_x_mm,
                        usb_c_panel_cutout_width_along_y_axis_mm,
                        usb_c_panel_cutout_height_along_z_axis_mm);
            }

            // ---- Cell contact mounting slots ----
            for (cell_y_center_mm = [
                    (minus_y_cell_bay_start_y_mm + minus_y_cell_bay_end_y_mm) / 2,
                    (plus_y_cell_bay_start_y_mm + plus_y_cell_bay_end_y_mm) / 2]) {
                slot_y_start_mm =
                    cell_y_center_mm - cell_contact_mount_slot_width_along_y_mm / 2;
                slot_z_start_mm =
                    cell_contact_mount_slot_center_z_mm
                      - cell_contact_mount_slot_height_along_z_mm / 2;
                translate([cell_bay_start_x_position_mm
                             - cell_contact_mount_slot_depth_along_x_mm,
                           slot_y_start_mm,
                           slot_z_start_mm])
                    cube([cell_contact_mount_slot_depth_along_x_mm + 0.1,
                          cell_contact_mount_slot_width_along_y_mm,
                          cell_contact_mount_slot_height_along_z_mm]);
                translate([cell_bay_end_x_position_mm - 0.1,
                           slot_y_start_mm,
                           slot_z_start_mm])
                    cube([cell_contact_mount_slot_depth_along_x_mm + 0.1,
                          cell_contact_mount_slot_width_along_y_mm,
                          cell_contact_mount_slot_height_along_z_mm]);
            }

            // ---- NEW: battery insertion slots through -X end wall ----
            // Each slot matches its cell bay Y×Z cross-section and punches
            // through the full 3 mm -X wall thickness. Cells slide in
            // from outside at X < 0 through the slot, into the bay
            // behind. Cells are retained by a spring contact at the -X
            // end (pressing them +X against the +X stop).
            for (cell_bay_ys = [
                    [minus_y_cell_bay_start_y_mm, minus_y_cell_bay_end_y_mm],
                    [plus_y_cell_bay_start_y_mm,  plus_y_cell_bay_end_y_mm]]) {
                translate([-0.1,
                           cell_bay_ys[0],
                           base_floor_plate_thickness_mm])
                    cube([minus_x_battery_side_end_wall_thickness_mm + 0.2,
                          cell_bay_ys[1] - cell_bay_ys[0],
                          cell_bay_height_above_floor_mm + 0.1]);
            }
        }

        // ---- NEW: raised lips along Pico chamber ±Y boundary ----
        // Seated on the cell-bay ceiling (Y just *outside* the Pico
        // chamber Y boundary), extending 1 mm above the case top into
        // the top cover's interior cavity on the non-battery edges.
        // These stiffen the cover mating on the long edges without
        // interfering with cell insertion at the -X end or the display
        // PCB sitting at z = 14 (display overhangs the cells at
        // Y = 8-12.1 and Y = 33.9-38, i.e., the lip Y range is
        // 10.6-12.1, which is just at the cell-bay ceiling edge).
        for (lip_y_outer_edge_mm = [pico_w_chamber_start_y_mm,
                                    pico_w_chamber_end_y_mm
                                      + raised_lip_width_along_y_mm]) {
            lip_y_start_mm =
                lip_y_outer_edge_mm - raised_lip_width_along_y_mm;
            translate([inner_x_start_mm,
                       lip_y_start_mm,
                       enclosure_total_height_along_z_axis_mm])
                cube([inner_x_end_mm - inner_x_start_mm,
                      raised_lip_width_along_y_mm,
                      raised_lip_height_above_case_top_mm]);
        }
    }
}

base_v4_2piece_open();
