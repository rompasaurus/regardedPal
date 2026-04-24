// Dilder Rev 2 "extended with joystick" — BASE v1
//
// Bottom shell of the enclosure, sized for the extended joystick layout:
//   - Battery lies flat on the LEFT half (same 1000 mAh cell as top-cover-v3,
//     52 x 35 mm footprint).
//   - ESP32 stack sits on the RIGHT half and overhangs the battery top by 2 mm.
//     The ESP32 footprint is slightly thinner in Y than the battery, centered
//     on the same Y axis as the battery chamber.
//   - Two USB-C ports on the board pop out through the +X end wall.
//   - Four corner pillars with M3 pass-through holes, same convention as
//     enclosure-prints/base.3mf and the existing top-cover-v3.
//   - Rounded outer shell with a soft bottom fillet for the "curved bottom"
//     look.
//
// Source of measurements: ./design-plan.md (from hand-drawn sketch).
//
// Export:
//   openscad -o base-v1.3mf base-v1.scad

$fn = 48;

// ============================================================
// Outer shell dimensions (overall enclosure footprint and height)
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 91.5; // battery bay +2 mm (was 89.5)
enclosure_outer_depth_along_y_axis_mm          = 44;
enclosure_total_height_along_z_axis_mm         = 14;  // top perimeter +2 mm (was 12)
perimeter_outer_wall_thickness_mm              = 2;    // ±Y long walls
base_floor_plate_thickness_mm                  = 3;    // was 2; +1 mm so the -X-ward battery-floor pit (2 mm deep) leaves 1 mm of material below it
// Outer corner radius is bounded by the asymmetric end-wall geometry:
// with `plus_x_wall = 1.2` and `pillar = 5`, the outermost +X pillar
// corner sits √((r − 1.2)² + (r − 2)²) from the shell corner arc center
// and must be ≤ r. That constraint gives r ≤ 5.39, and the symmetric
// -X constraint gives r ≤ 4.34. Anything above 4.34 makes the +X pillar
// corners visibly poke past the rounded shell on the USB face.
outer_case_top_view_corner_radius_mm           = 4;
outer_case_bottom_edge_fillet_radius_mm        = 2;

// Asymmetric ±X end-wall thicknesses: the USB-C side is intentionally
// thinner so the two ports pop through a minimal amount of material, and
// the opposite (battery) side is a bit thicker for strength and balance.
plus_x_usb_side_end_wall_thickness_mm          = 1.2;  // +X, USB-C end
minus_x_battery_side_end_wall_thickness_mm     = 3.0;  // -X, battery end

// ============================================================
// Battery chamber (LEFT side, 1000 mAh cell — matches top-cover-v3)
// ============================================================
battery_cell_footprint_length_x_mm             = 61.5; // battery bay +2 mm (was 59.5)
battery_cell_footprint_depth_y_mm              = 35;

// ============================================================
// ESP32 chamber (RIGHT side — slightly thinner in Y than the battery)
// ============================================================
esp32_board_footprint_depth_y_mm               = 28;   // narrower than battery
esp32_overhang_shelf_height_above_battery_floor_mm = 5; // was 2; +3 = battery pit 3 mm deeper under the shelf

// ============================================================
// Two USB-C cutouts on the +X end wall (for the board's two USB-C ports)
// ============================================================
// Cutout shape is a stadium (pill) — rectangle in Y with rounded ±Y end
// caps — so the curved ends match the USB-C receptacle's shield profile
// and the PCB's port bodies drop cleanly through the +X wall during
// assembly (instead of binding on sharp rectangular corners).
//
// Y width: measured port length (7.8 mm) + 1 mm slop so the port body
// has room to move past the opening while seating the board.
// Z height: port body height (2.6 mm) + 0.2 mm seat allowance, plus a
// top-only 0.5 mm extension that raises ONLY the top edge of the
// cutout. The bottom edge stays put so the shelf alignment under each
// port is unchanged; the extra top clearance gives room for the port
// body's top radius to slip past the plastic during drop-in.
usb_c_panel_cutout_width_along_y_axis_mm       = 8.8;   // 7.8 port + 1 mm slop
usb_c_port_body_height_above_pcb_mm            = 2.6;   // typical USB-C receptacle body
usb_c_cutout_extra_height_allowance_mm         = 0.2;   // so board lies flat
usb_c_cutout_top_extra_height_mm               = 0.5;   // raises ONLY the top edge
usb_c_panel_cutout_height_along_z_axis_mm =
    usb_c_port_body_height_above_pcb_mm
      + usb_c_cutout_extra_height_allowance_mm
      + usb_c_cutout_top_extra_height_mm;               // = 3.3

// How far the USB-C port body extends INTO the enclosure from the outer
// wall (typical SMT receptacle: ~7.3 mm body depth on the PCB). Each
// cutout carves this far into the body so the port bodies have an
// explicit aligned pocket, not just open chamber space.
usb_c_port_body_recess_depth_into_enclosure_mm = 8.0;

// Shelf divet under each USB-C port. The board sits on the ESP32 shelf
// with the USB-C receptacle straddling the PCB edge; a small shield tab
// on the port body extends ~0.2 mm BELOW the PCB, so without this divet
// the board would rock on that tab. The divet is carved into the top of
// the shelf (z just below the shelf face) at each port's Y position.
usb_c_shelf_divet_depth_into_shelf_z_mm        = 0.7;
usb_c_shelf_divet_length_along_x_axis_mm       = 8.0;
usb_c_shelf_divet_width_along_y_axis_mm        = 7.8;

// Vertical center of the USB-C port cutout (z).
// The board sits INSIDE the base on the ESP32 shelf (component-side UP,
// headers facing up), so the USB-C ports sit low — close to the base
// floor. Tracks the shelf: raised +1 mm when the base floor went from
// 2 to 3 mm (shelf shifted z=7 → z=8), so the cutout still clears the
// shelf top and sits fully above it (cutout now spans z=7.6 to z=10.9
// with the top-only +0.5 mm extension, shelf top at z=8).
usb_c_port_vertical_center_z_mm                = 9;

// Effective cutout Z center is shifted up by half the top-only extra so
// the added height sits entirely above the original cutout top edge
// (bottom Z stays the same as before this pass).
usb_c_cutout_effective_center_z_mm =
    usb_c_port_vertical_center_z_mm
      + usb_c_cutout_top_extra_height_mm / 2;           // = 8.25

// Y centers of the TWO USB-C ports on the board's end edge. Default layout
// assumes the two ports sit symmetrically about the ESP32 Y centerline,
// ~6 mm apart center-to-center (tweak to match the real board).
usb_c_port_center_y_positions_list = [
    enclosure_outer_depth_along_y_axis_mm / 2 - 6,   // lower port
    enclosure_outer_depth_along_y_axis_mm / 2 + 6,   // upper port
];

// ============================================================
// Internal layout (divider between chambers, fit tolerance)
// ============================================================
print_fit_tolerance_slop_mm                    = 0.4;
battery_to_esp32_internal_divider_wall_thickness_mm = 2;
esp32_cavity_overhang_onto_battery_length_x_mm = 4;   // PCB overhangs battery in X

// ============================================================
// Corner pillars (support posts for screws through the stack)
// ============================================================
corner_pillar_square_side_length_mm            = 5;
corner_pillar_inner_facing_corner_radius_mm    = 1;
m3_screw_clearance_hole_diameter_mm            = 3.2;

// ============================================================
// BOOT / RESET button poke-through holes in the BASE FLOOR
// ============================================================
// Two small Ø 1 mm vertical through-holes in the bottom of the case,
// going straight up through the 2 mm base plate and the 5 mm shelf
// material so a paperclip inserted from below reaches the BOOT and
// RESET buttons on the ESP32 dev board (which is mounted COMPONENT-
// SIDE DOWN in the ESP32 chamber, so buttons face the floor).
//
// X positions are measured from the +X (USB-end) inner wall face.
// Y position is measured INWARD from the +Y outer long edge of the
// floor (11.5 mm inset lands the hole inside the ESP32 chamber under
// where the flipped-board buttons sit).
button_poke_hole_diameter_mm                          = 2.0;
button_poke_hole_1_distance_from_plus_x_inner_wall_mm = 17.0;  // nearest the USB end
button_poke_hole_2_offset_to_left_of_hole_1_mm        = 12.5;  // further into the case
button_poke_hole_distance_from_plus_y_outer_edge_mm   = 11.5;  // Y inset from +Y outer edge

// ============================================================
// Battery-floor pit (just past the ESP32 shelf / divider, inside
// the battery chamber)
// ============================================================
// A rectangular pit dug INTO the battery chamber floor, flush with
// the +X end of the battery cavity (against the divider wall) and
// centered on the enclosure Y axis. Purpose: recess for a battery-
// side component / connector hanging below the cell. Depth is
// measured DOWNWARD from the battery floor (top of the floor plate).
battery_floor_pit_width_along_x_mm             = 10.0;
battery_floor_pit_width_along_y_mm             = 35.5;
battery_floor_pit_depth_below_battery_floor_mm = 2.0;

// ============================================================
// Battery-stop pillars (two positive blocks INSIDE the battery
// chamber, flush to the ±Y inner walls and to the divider wall)
// ============================================================
// The ESP32 PCB overhangs onto the battery chamber top, and its
// under-board connector sits near the battery-facing PCB edge. These
// two short pillars act as physical stops so the cell cannot slide
// far enough toward +X to contact that connector. Each pillar grows
// out of the divider (battery-side face) by the X-width below, runs
// along the ±Y inner wall for the Y-width below, and rises from the
// battery floor by the Z-height below. A wide gap stays open in the
// middle for the connector to hang down without fouling.
battery_stop_pillar_width_along_x_mm   = 9.0;    // extends -X from divider (was 5; +4 mm so the block reaches further into the battery chamber)
battery_stop_pillar_width_along_y_mm   = 6.0;    // per pillar, along ±Y walls (was 9; −3 mm so it sticks out less toward the chamber centerline)
battery_stop_pillar_height_along_z_mm  = 5.0;    // from pit floor up (7 − 2 = 5; top now at z = 6, below the ESP32 shelf at z = 8)

// ============================================================
// Derived cavity dimensions (cell + slop on every side)
// ============================================================
battery_chamber_inner_length_along_x_axis_mm =
    battery_cell_footprint_length_x_mm + 2 * print_fit_tolerance_slop_mm;
battery_chamber_inner_depth_along_y_axis_mm =
    battery_cell_footprint_depth_y_mm + 2 * print_fit_tolerance_slop_mm;
esp32_chamber_inner_depth_along_y_axis_mm =
    esp32_board_footprint_depth_y_mm + 2 * print_fit_tolerance_slop_mm;

// ESP32 chamber X length is derived so the cavity reaches the thin +X wall
// (otherwise the USB-C cutouts would terminate in solid material before
// breaking through into the chamber).
esp32_chamber_inner_length_along_x_axis_mm =
    enclosure_outer_width_along_x_axis_mm
      - minus_x_battery_side_end_wall_thickness_mm
      - battery_chamber_inner_length_along_x_axis_mm
      - battery_to_esp32_internal_divider_wall_thickness_mm
      - plus_x_usb_side_end_wall_thickness_mm;

// Corner pillar positions — flush to the inside of the outer wall.
// The ±X positions use the asymmetric end-wall thicknesses so the pillars
// sit hard against whichever wall they belong to.
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

// ========== Helpers (shared with top-cover-v3 family) ==========

module rounded_v_box(w, l, h, r, fn = 48) {
    hull() {
        for (x = [r, w - r])
            for (y = [r, l - r])
                translate([x, y, 0])
                    cylinder(r = r, h = h, $fn = fn);
    }
}

// Pillar with only one corner rounded (the exposed inner corner).
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

// Rounded-rectangle PRISM with a filleted BOTTOM edge — the "curved bottom"
// look. Minkowski sum of a shrunken rounded box with a hemisphere.
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

// Stadium (pill) shape cutout — rectangle in Y with semicircular end
// caps on the ±Y ends — extruded along +X. Origin is at the stadium's
// geometric center (Y=0, Z=0); the extrusion runs from X=0 to X=depth.
// Used for the USB-C panel cutouts so the curved ends match the
// receptacle shield and the PCB can be dropped in without the port
// body catching on a sharp corner.
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

// A chamber carve that preserves the corner pillars — the cavity box with
// square notches cut out where each pillar stands. Ensures the screw holes
// through the pillars stay fully embedded in solid material, with no open
// slice exposing them to the chamber.
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

// ========== Base ==========

module base() {
    // -------- Z heights --------
    battery_chamber_floor_z_height_mm =
        base_floor_plate_thickness_mm;
    esp32_chamber_shelf_floor_z_height_mm =
        base_floor_plate_thickness_mm
          + esp32_overhang_shelf_height_above_battery_floor_mm;

    // -------- X positions --------
    battery_cavity_start_x_position_mm =
        minus_x_battery_side_end_wall_thickness_mm;
    battery_cavity_end_x_position_mm =
        battery_cavity_start_x_position_mm
          + battery_chamber_inner_length_along_x_axis_mm;

    divider_wall_start_x_position_mm = battery_cavity_end_x_position_mm;
    divider_wall_end_x_position_mm =
        divider_wall_start_x_position_mm
          + battery_to_esp32_internal_divider_wall_thickness_mm;

    esp32_cavity_start_x_position_mm =
        divider_wall_end_x_position_mm
          - esp32_cavity_overhang_onto_battery_length_x_mm;
    esp32_cavity_end_x_position_mm =
        divider_wall_end_x_position_mm
          + esp32_chamber_inner_length_along_x_axis_mm;

    // -------- Y positions (both cavities centered on the enclosure Y axis) --------
    battery_cavity_start_y_position_mm =
        (enclosure_outer_depth_along_y_axis_mm
          - battery_chamber_inner_depth_along_y_axis_mm) / 2;
    esp32_cavity_start_y_position_mm =
        (enclosure_outer_depth_along_y_axis_mm
          - esp32_chamber_inner_depth_along_y_axis_mm) / 2;

    difference() {
        union() {
            shell_with_curved_bottom(
                enclosure_outer_width_along_x_axis_mm,
                enclosure_outer_depth_along_y_axis_mm,
                enclosure_total_height_along_z_axis_mm,
                outer_case_top_view_corner_radius_mm,
                outer_case_bottom_edge_fillet_radius_mm);

            // Corner pillars, CLIPPED to the outer shell so their outer
            // bottom corners inherit the fillet curve instead of poking
            // past it (without this, the pillar's flat corner at z≈0 sits
            // outside the shrunken z=0 shell outline and shows as a
            // clipped plane at the base of the front panel).
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

            // Internal divider between battery and ESP32 chambers.
            // Spans the battery chamber Y width so it fully closes the
            // battery pocket; the ESP32 cut later carves it back above the
            // overhang shelf.
            translate([divider_wall_start_x_position_mm,
                       battery_cavity_start_y_position_mm,
                       base_floor_plate_thickness_mm])
                cube([battery_to_esp32_internal_divider_wall_thickness_mm,
                      battery_chamber_inner_depth_along_y_axis_mm,
                      enclosure_total_height_along_z_axis_mm
                        - base_floor_plate_thickness_mm]);
        }

        // ----- Hollow out the chambers (pillars preserved) -----

        // Battery chamber: full height from battery floor up. Pillar
        // corners are NOT carved out, so the screw holes stay fully
        // inside solid pillar material with no opening into the chamber.
        chamber_carve_preserving_pillars(
            battery_cavity_start_x_position_mm,
            battery_cavity_start_y_position_mm,
            battery_chamber_floor_z_height_mm,
            battery_chamber_inner_length_along_x_axis_mm,
            battery_chamber_inner_depth_along_y_axis_mm,
            enclosure_total_height_along_z_axis_mm
              - battery_chamber_floor_z_height_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // ESP32 chamber: starts 2 mm higher (overlap step) and extends
        // `overhang` back over the battery cavity — the overhang shelf.
        chamber_carve_preserving_pillars(
            esp32_cavity_start_x_position_mm,
            esp32_cavity_start_y_position_mm,
            esp32_chamber_shelf_floor_z_height_mm,
            esp32_cavity_end_x_position_mm
              - esp32_cavity_start_x_position_mm,
            esp32_chamber_inner_depth_along_y_axis_mm,
            enclosure_total_height_along_z_axis_mm
              - esp32_chamber_shelf_floor_z_height_mm + 0.1,
            corner_pillar_xy_origin_positions_list,
            corner_pillar_square_side_length_mm);

        // Screw pass-through holes through every pillar.
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

        // Shelf divet under each USB-C port, so the shield tab on the
        // port body (which pokes ~0.2 mm below the PCB) has somewhere to
        // live and the board rests flat on the shelf. One divet per port,
        // carved INTO the top of the ESP32 shelf at the +X end.
        for (usb_c_port_center_y_mm = usb_c_port_center_y_positions_list) {
            divet_origin_x_mm =
                enclosure_outer_width_along_x_axis_mm
                  - plus_x_usb_side_end_wall_thickness_mm
                  - usb_c_shelf_divet_length_along_x_axis_mm;
            divet_origin_y_mm =
                usb_c_port_center_y_mm
                  - usb_c_shelf_divet_width_along_y_axis_mm / 2;
            divet_origin_z_mm =
                esp32_chamber_shelf_floor_z_height_mm
                  - usb_c_shelf_divet_depth_into_shelf_z_mm;
            // Divet stops AT the inner face of the +X wall so it never
            // breaks through to the outside (which would show up as a
            // thin slit under each USB-C cutout and look like clipping).
            translate([divet_origin_x_mm,
                       divet_origin_y_mm,
                       divet_origin_z_mm])
                cube([usb_c_shelf_divet_length_along_x_axis_mm,
                      usb_c_shelf_divet_width_along_y_axis_mm,
                      usb_c_shelf_divet_depth_into_shelf_z_mm + 0.01]);
        }

        // Two USB-C cutouts through the +X end wall at the ESP32 chamber.
        // Each cutout is a STADIUM (pill) shape — rounded ±Y ends that
        // match the USB-C receptacle shield profile — passing through the
        // THIN +X wall AND extending inward into the enclosure by the
        // USB-C port body depth, so each port has an explicit, aligned
        // pocket (not just an incidental gap in the open chamber).
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

        // BOOT / RESET paperclip poke-through holes in the BASE FLOOR.
        // Board is mounted component-side DOWN on the ESP32 shelf, so
        // BOOT/RST buttons face the floor. Two Ø 1 mm vertical holes
        // drill straight up from the outside bottom through the base
        // plate and the shelf material so a paperclip inserted from
        // below can reach the button contacts.
        button_poke_hole_1_center_x_mm =
            enclosure_outer_width_along_x_axis_mm
              - plus_x_usb_side_end_wall_thickness_mm
              - button_poke_hole_1_distance_from_plus_x_inner_wall_mm;
        button_poke_hole_2_center_x_mm =
            button_poke_hole_1_center_x_mm
              - button_poke_hole_2_offset_to_left_of_hole_1_mm;
        button_poke_hole_center_y_mm =
            enclosure_outer_depth_along_y_axis_mm
              - button_poke_hole_distance_from_plus_y_outer_edge_mm; // 44 − 11.5 = 32.5
        // Cylinder starts just below the outer bottom and extends all
        // the way through to above the shelf so the full bore is
        // punched in one subtract (floor + shelf material both go).
        for (button_poke_hole_center_x_mm =
               [button_poke_hole_1_center_x_mm,
                button_poke_hole_2_center_x_mm]) {
            translate([button_poke_hole_center_x_mm,
                       button_poke_hole_center_y_mm,
                       -0.5])
                cylinder(h = enclosure_total_height_along_z_axis_mm + 1,
                         d = button_poke_hole_diameter_mm,
                         $fn = 24);
        }

        // Battery-floor pit at the +X end of the battery chamber (just
        // past the ESP32 shelf / divider). Carves down from the battery
        // floor into the floor plate; with floor_plate=3 and pit=2, a
        // 1 mm material layer remains under the pit so it does NOT
        // break through to the outside bottom.
        battery_floor_pit_plus_x_edge_mm  = battery_cavity_end_x_position_mm;
        battery_floor_pit_start_x_mm      =
            battery_floor_pit_plus_x_edge_mm
              - battery_floor_pit_width_along_x_mm;
        battery_floor_pit_start_y_mm      =
            (enclosure_outer_depth_along_y_axis_mm
              - battery_floor_pit_width_along_y_mm) / 2;
        battery_floor_pit_start_z_mm      =
            battery_chamber_floor_z_height_mm
              - battery_floor_pit_depth_below_battery_floor_mm;
        translate([battery_floor_pit_start_x_mm,
                   battery_floor_pit_start_y_mm,
                   battery_floor_pit_start_z_mm])
            cube([battery_floor_pit_width_along_x_mm,
                  battery_floor_pit_width_along_y_mm,
                  battery_floor_pit_depth_below_battery_floor_mm + 0.01]);
    }

    // Battery-stop pillars — two positive blocks added AFTER the
    // chamber carves so they survive as solid material inside the
    // hollowed battery chamber. Each attaches to the divider's
    // battery-facing face on its +X side and to the ±Y inner wall
    // on its outer Y side. Center Y stays clear for the ESP32
    // board's under-side connector.
    battery_stop_pillar_plus_x_edge_mm =
        battery_cavity_end_x_position_mm;                    // flush to divider
    battery_stop_pillar_minus_x_start_mm =
        battery_stop_pillar_plus_x_edge_mm
          - battery_stop_pillar_width_along_x_mm;
    battery_stop_pillar_bottom_z_mm =
        battery_chamber_floor_z_height_mm
          - battery_floor_pit_depth_below_battery_floor_mm;  // reaches pit floor (z = 1)
    for (pillar_side_is_plus_y = [0, 1]) {
        battery_stop_pillar_start_y_mm =
            (pillar_side_is_plus_y == 0)
              ? battery_cavity_start_y_position_mm           // flush to -Y inner wall
              : battery_cavity_start_y_position_mm
                  + battery_chamber_inner_depth_along_y_axis_mm
                  - battery_stop_pillar_width_along_y_mm;    // flush to +Y inner wall
        translate([battery_stop_pillar_minus_x_start_mm,
                   battery_stop_pillar_start_y_mm,
                   battery_stop_pillar_bottom_z_mm])
            cube([battery_stop_pillar_width_along_x_mm,
                  battery_stop_pillar_width_along_y_mm,
                  battery_stop_pillar_height_along_z_mm]);
    }
}

base();
