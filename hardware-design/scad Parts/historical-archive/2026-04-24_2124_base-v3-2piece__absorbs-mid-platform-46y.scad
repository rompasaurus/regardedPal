// Dilder Rev 2 "extended with joystick" — BASE v3, 2-PIECE (no middle platform)
//
// Evolution of base-v2-thin-dual-10440: same Y = 46 outer footprint, same
// dual 10440 flanking-cell layout, but the base now extends UP to absorb
// what the middle platform used to do. The stack is now just BASE +
// TOP COVER (no mid-stack piece).
//
// Z stack-up (globals):
//   0 ─────────── base outer bottom
//   2 ─────────── floor plate top / cell bay floor
//   8 ─────────── Pico W shelf top (PCB rests here)
//   9 ─────────── Pico W PCB top surface
//   11.5 ──────── Pico W tallest components (USB-C, crystal)
//   12 ────────── cell bay ceiling (cells are trapped here)
//   14 ────────── base rim top (= display PCB bottom rests here)
//                  — rim at ±Y closes off the cell bays above z=12 and
//                    provides a 4 mm-wide ledge on each Y side for the
//                    Waveshare display's ±Y edges to rest on.
//                    Top cover bolts down onto this mating plane.
//
// "Inlay into the Pico": the Pico W drops into the centered chamber at
// Y = 12.1–33.9, X = 3–90.3 (carved from z = 8 upward). The shelf below
// and the ±Y cell-bay inner walls together form a Pico-shaped pocket.
//
// "Secure the back of the Waveshare": the display PCB is 30 mm wide in
// Y and centered in the 46 mm case, so its ±Y edges overhang the 21.8 mm
// Pico chamber by ~4.1 mm on each side. Those ±Y edges rest on the solid
// base rim at z = 14 (directly above the cell-bay ceilings). The top
// cover's display inlay presses down from above; the base rim presses up
// from below — display is trapped between.
//
// Cell hardware: two 10440 Li-ion in parallel, ~700 mAh total. Charge via
// existing TP4056 (drop R_prog to ~3.4 kΩ for 350 mA CC).
//
// Export:
//   openscad -o base-v3-2piece.3mf base-v3-2piece.scad

$fn = 48;

// ============================================================
// Outer shell
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 91.5;
enclosure_outer_depth_along_y_axis_mm          = 46;
enclosure_total_height_along_z_axis_mm         = 14;   // was 12 in base-v2; +2 mm to absorb the middle platform's display-support role
perimeter_outer_wall_thickness_mm              = 2;
base_floor_plate_thickness_mm                  = 2;
outer_case_top_view_corner_radius_mm           = 4;
outer_case_bottom_edge_fillet_radius_mm        = 2;

plus_x_usb_side_end_wall_thickness_mm          = 1.2;
minus_x_battery_side_end_wall_thickness_mm     = 3.0;

// ============================================================
// 10440 Li-ion cell bays (±Y, lie flat in X) — cells trapped at
// z = 12 by the rim material above. Bay height is decoupled from
// enclosure height so growing the case in Z doesn't loosen the
// cell's Z retention.
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
    cell_10440_diameter_mm;                                  // = 10 (cell Ø fills cavity exactly)

cell_bay_start_x_position_mm                   =
    minus_x_battery_side_end_wall_thickness_mm;
cell_bay_end_x_position_mm =
    cell_bay_start_x_position_mm + cell_bay_length_along_x_mm;
cell_bay_ceiling_z_mm =
    base_floor_plate_thickness_mm + cell_bay_height_above_floor_mm; // = 12

// ============================================================
// Cell contact mounting slots (generic; see base-v2 notes)
// ============================================================
cell_contact_mount_slot_width_along_y_mm       = 3.5;
cell_contact_mount_slot_depth_along_x_mm       = 2.0;
cell_contact_mount_slot_height_along_z_mm      = 4.0;
cell_contact_mount_slot_center_z_mm =
    base_floor_plate_thickness_mm
      + cell_10440_diameter_mm / 2;                          // = 7

// ============================================================
// Pico W chamber — centered in Y, open from shelf top to case top
// ============================================================
pico_w_board_width_along_y_mm                  = 21.0;
pico_w_board_length_along_x_mm                 = 51.0;
print_fit_tolerance_slop_mm                    = 0.4;
pico_w_chamber_width_along_y_mm =
    pico_w_board_width_along_y_mm + 2 * print_fit_tolerance_slop_mm; // = 21.8
pico_w_shelf_top_z_mm                          = 8.0;

// ============================================================
// USB-C cutout (single port on +X wall, centered on Y)
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
// Corner pillars (full-height, M3 pass-through bores)
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


// ========== Base v3 (2-piece) ==========

module base_v3_2piece() {
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

        // ---- -Y cell bay: 10 mm tall only, ceiling at z=12 ----
        chamber_carve_preserving_pillars(
            cell_bay_start_x_position_mm,
            minus_y_cell_bay_start_y_mm,
            base_floor_plate_thickness_mm,
            cell_bay_end_x_position_mm - cell_bay_start_x_position_mm,
            minus_y_cell_bay_end_y_mm - minus_y_cell_bay_start_y_mm,
            cell_bay_height_above_floor_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // ---- +Y cell bay: symmetric, ceiling at z=12 ----
        chamber_carve_preserving_pillars(
            cell_bay_start_x_position_mm,
            plus_y_cell_bay_start_y_mm,
            base_floor_plate_thickness_mm,
            cell_bay_end_x_position_mm - cell_bay_start_x_position_mm,
            plus_y_cell_bay_end_y_mm - plus_y_cell_bay_start_y_mm,
            cell_bay_height_above_floor_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // ---- Pico W chamber: from shelf top UP TO CASE TOP ----
        // This is the "Pico inlay" — the Pico drops in here, is surrounded
        // on ±Y by the solid cell-bay-ceiling walls from z=12 upward, and
        // on its -X / +X by the end walls / corner pillars.
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

        // ---- USB-C cutout on +X wall ----
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

        // ---- Cell contact mounting slots (4 total) ----
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
    }
}

base_v3_2piece();
