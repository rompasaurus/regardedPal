// Dilder Rev 2 "extended with joystick" — BASE v2, THINNER + DUAL 10440 Li-ion
//
// Forked from base-v1.scad. Designed from the 2026-04-24 photo study that
// showed two AA/AAA-sized cells flanking a Pico W with the Pico-ePaper-2.13
// display mounted above. This variant is sized for 10440 Li-ion cells
// (Ø 10 × 44 mm, 3.7 V ≈ 350 mAh ea, drop-in same-chemistry replacement
// for your LiPo pouches — works with the existing TP4056 unchanged).
//
// Key changes from base-v1:
//   - enclosure_outer_depth_along_y_axis_mm: 44 → 46 (+2 mm, smallest bump
//     that gives both 10440 cells positive radial slop flanking the 21 mm
//     Pico W centered in Y).
//   - enclosure_total_height_along_z_axis_mm: 14 → 12 (thinner by 2 mm —
//     cell Ø 10 exactly fills the 10 mm usable cavity above the 2 mm floor).
//   - base_floor_plate_thickness_mm: 3 → 2 (saves 1 mm of Z).
//   - REMOVED: single pouch-battery chamber, battery-floor pit, battery-
//     stop pillars, internal battery↔ESP32 divider, ESP32 overhang shelf,
//     BOOT/RESET button poke-throughs (Pico W BOOTSEL is top-side), and the
//     second USB-C cutout (Pico W has a single USB-C).
//   - ADDED: two flanking rectangular 10440 bays along ±Y, centered Pico W
//     shelf, one centered USB-C cutout on +X.
//
// Cell wiring: two 10440 Li-ion in PARALLEL → 3.7 V, ~700 mAh pack.
// Match cell model + batch + pre-charge voltage before first parallel
// hookup. Charge via existing TP4056 — derate to ~350 mA by swapping
// R_prog (default 1.2 kΩ → ~3.4 kΩ).
//
// ⚠ MATING NOTE: the +2 mm Y bump means the existing top-cover and middle-
// platform SCADs (both at outer Y = 44) need matching +2 mm Y updates
// before the full stack mates. They are NOT auto-updated by this file.
//
// Export:
//   openscad -o base-v2-thin-dual-10440.3mf base-v2-thin-dual-10440.scad

$fn = 48;

// ============================================================
// Outer shell
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 91.5;
enclosure_outer_depth_along_y_axis_mm          = 46;   // was 44; +2 mm so two 10440 cells fit with slop flanking the Pico W
enclosure_total_height_along_z_axis_mm         = 12;   // was 14; thinner, cell Ø 10 fills the 10 mm above-floor cavity exactly
perimeter_outer_wall_thickness_mm              = 2;    // ±Y long walls
base_floor_plate_thickness_mm                  = 2;    // was 3; -1 mm to claw back Z
outer_case_top_view_corner_radius_mm           = 4;
outer_case_bottom_edge_fillet_radius_mm        = 2;

plus_x_usb_side_end_wall_thickness_mm          = 1.2;  // +X, USB-C end (thin)
minus_x_battery_side_end_wall_thickness_mm     = 3.0;  // -X, battery end

// ============================================================
// 10440 Li-ion cell bays — two rectangular slots along ±Y, cells
// lie flat with their long axis along X. Each bay is sized so the
// cell is captured top-and-bottom in Z (no room to rattle) and has
// a small Y slop so it drops in without fight.
// ============================================================
cell_10440_diameter_mm                         = 10.0;
cell_10440_length_mm                           = 44.0;
cell_bay_radial_slop_mm                        = 0.3;   // per side → 0.6 mm total Y slop
cell_bay_axial_slop_mm                         = 1.0;   // total X slop for print tolerance
// Axial space at EACH end of the cell bay for spring-contact hardware
// (the metal coil / strip that touches the cell's + and - terminals).
// The cell itself occupies 44 mm; 2 mm at each end holds a standard
// stamped-strip battery contact, plus the 1 mm axial print slop.
cell_contact_space_per_end_mm                  = 2.0;

cell_bay_width_along_y_mm =
    cell_10440_diameter_mm + 2 * cell_bay_radial_slop_mm;    // = 10.6
cell_bay_length_along_x_mm =
    cell_10440_length_mm
      + 2 * cell_contact_space_per_end_mm
      + cell_bay_axial_slop_mm;                              // = 49.0

// Cell bay X origin — cells pushed against -X battery wall for weight
// balance and to keep them out from under the USB-C port area.
cell_bay_start_x_position_mm                   =
    minus_x_battery_side_end_wall_thickness_mm;
cell_bay_end_x_position_mm =
    cell_bay_start_x_position_mm + cell_bay_length_along_x_mm;

// ============================================================
// Cell contact mounting slots — rectangular cuts at each ±X end
// of each cell bay, sized for a typical stamped-strip battery
// contact tab (~3 mm wide × ~0.3 mm thick). The -X slot carves
// INTO the -X end wall from the cavity side (leaving ~1 mm of
// outer wall material); the +X slot carves INTO the solid region
// between the cell bay's +X end and the +X USB wall. Sized
// generically — tweak width/depth to match your actual contact
// part, or ignore and solder wires directly to the cell cans.
// ============================================================
cell_contact_mount_slot_width_along_y_mm       = 3.5;   // Y width of tab slot
cell_contact_mount_slot_depth_along_x_mm       = 2.0;   // how far tab inserts into material
cell_contact_mount_slot_height_along_z_mm      = 4.0;   // Z height of slot
cell_contact_mount_slot_center_z_mm =
    base_floor_plate_thickness_mm
      + cell_10440_diameter_mm / 2;                     // = 7 (cell Z center)

// ============================================================
// Pico W chamber (centered in Y, on a solid support shelf)
// ============================================================
pico_w_board_width_along_y_mm                  = 21.0;
pico_w_board_length_along_x_mm                 = 51.0;
print_fit_tolerance_slop_mm                    = 0.4;
pico_w_chamber_width_along_y_mm =
    pico_w_board_width_along_y_mm + 2 * print_fit_tolerance_slop_mm; // = 21.8
// Shelf top z — where the Pico W PCB rests. Matches the legacy
// ESP32 shelf height (z = 8) so the USB-C cutout at z ≈ 9 still
// lands at the port body's vertical center.
pico_w_shelf_top_z_mm                          = 8.0;

// ============================================================
// USB-C cutout on +X wall (single port, centered on Y)
// ============================================================
usb_c_panel_cutout_width_along_y_axis_mm       = 8.8;   // 7.8 port + 1 mm slop
usb_c_port_body_height_above_pcb_mm            = 2.6;   // USB-C receptacle body
usb_c_cutout_extra_height_allowance_mm         = 0.2;   // board sits flat
usb_c_cutout_top_extra_height_mm               = 0.5;   // raise TOP edge only
usb_c_panel_cutout_height_along_z_axis_mm =
    usb_c_port_body_height_above_pcb_mm
      + usb_c_cutout_extra_height_allowance_mm
      + usb_c_cutout_top_extra_height_mm;               // = 3.3
usb_c_port_body_recess_depth_into_enclosure_mm = 8.0;
usb_c_port_vertical_center_z_mm                = 9;     // unchanged from base-v1
usb_c_cutout_effective_center_z_mm =
    usb_c_port_vertical_center_z_mm
      + usb_c_cutout_top_extra_height_mm / 2;           // = 9.25

// Pico W has ONE USB-C port, centered on its long edge.
usb_c_port_center_y_positions_list = [
    enclosure_outer_depth_along_y_axis_mm / 2,          // = 23
];

// ============================================================
// Corner pillars — same convention as base-v1 (5×5 square, one
// rounded inner corner, full-height M3 clearance bore).
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


// ========== Base v2 (thinner, dual 10440) ==========

module base_v2_thin_dual_10440() {
    // -------- Y positions (Pico chamber centered; cell bays flank) --------
    pico_w_chamber_start_y_mm =
        (enclosure_outer_depth_along_y_axis_mm
          - pico_w_chamber_width_along_y_mm) / 2;             // = 12.1
    pico_w_chamber_end_y_mm =
        pico_w_chamber_start_y_mm + pico_w_chamber_width_along_y_mm; // = 33.9
    minus_y_cell_bay_start_y_mm = perimeter_outer_wall_thickness_mm;   // = 2
    minus_y_cell_bay_end_y_mm   = pico_w_chamber_start_y_mm;           // = 12.1 → 10.1 wide
    plus_y_cell_bay_start_y_mm  = pico_w_chamber_end_y_mm;             // = 33.9
    plus_y_cell_bay_end_y_mm =
        enclosure_outer_depth_along_y_axis_mm
          - perimeter_outer_wall_thickness_mm;                // = 44 → 10.1 wide

    // -------- X positions --------
    inner_x_start_mm = minus_x_battery_side_end_wall_thickness_mm;    // = 3
    inner_x_end_mm =
        enclosure_outer_width_along_x_axis_mm
          - plus_x_usb_side_end_wall_thickness_mm;                    // = 90.3

    difference() {
        union() {
            // Outer shell with curved bottom fillet (same contour as base-v1)
            shell_with_curved_bottom(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                enclosure_total_height_along_z_axis_mm,
                outer_case_top_view_corner_radius_mm,
                outer_case_bottom_edge_fillet_radius_mm);

            // Corner pillars, clipped to the outer shell bottom fillet so
            // their outer bottom corners follow the curve rather than poking
            // past it.
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

        // ---- -Y cell bay: full cavity above the floor, pushed to -X wall ----
        chamber_carve_preserving_pillars(
            cell_bay_start_x_position_mm,
            minus_y_cell_bay_start_y_mm,
            base_floor_plate_thickness_mm,
            cell_bay_end_x_position_mm - cell_bay_start_x_position_mm,
            minus_y_cell_bay_end_y_mm - minus_y_cell_bay_start_y_mm,
            enclosure_total_height_along_z_axis_mm
              - base_floor_plate_thickness_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // ---- +Y cell bay: symmetric ----
        chamber_carve_preserving_pillars(
            cell_bay_start_x_position_mm,
            plus_y_cell_bay_start_y_mm,
            base_floor_plate_thickness_mm,
            cell_bay_end_x_position_mm - cell_bay_start_x_position_mm,
            plus_y_cell_bay_end_y_mm - plus_y_cell_bay_start_y_mm,
            enclosure_total_height_along_z_axis_mm
              - base_floor_plate_thickness_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // ---- Pico W chamber: above the shelf (solid z=2 to z=8 supports the board) ----
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

        // ---- Screw pass-through bores through every corner pillar ----
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

        // ---- USB-C cutout on +X end wall (stadium profile, single port) ----
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

        // ---- Cell contact mounting slots (4 total: one at each ±X end of each cell bay) ----
        for (cell_y_center_mm = [
                (minus_y_cell_bay_start_y_mm + minus_y_cell_bay_end_y_mm) / 2,
                (plus_y_cell_bay_start_y_mm + plus_y_cell_bay_end_y_mm) / 2]) {
            slot_y_start_mm =
                cell_y_center_mm - cell_contact_mount_slot_width_along_y_mm / 2;
            slot_z_start_mm =
                cell_contact_mount_slot_center_z_mm
                  - cell_contact_mount_slot_height_along_z_mm / 2;
            // -X end slot — carved INTO the -X end wall, open on the bay side
            translate([cell_bay_start_x_position_mm
                         - cell_contact_mount_slot_depth_along_x_mm,
                       slot_y_start_mm,
                       slot_z_start_mm])
                cube([cell_contact_mount_slot_depth_along_x_mm + 0.1,
                      cell_contact_mount_slot_width_along_y_mm,
                      cell_contact_mount_slot_height_along_z_mm]);
            // +X end slot — carved INTO the solid +X-of-bay region
            translate([cell_bay_end_x_position_mm - 0.1,
                       slot_y_start_mm,
                       slot_z_start_mm])
                cube([cell_contact_mount_slot_depth_along_x_mm + 0.1,
                      cell_contact_mount_slot_width_along_y_mm,
                      cell_contact_mount_slot_height_along_z_mm]);
        }
    }
}

base_v2_thin_dual_10440();
