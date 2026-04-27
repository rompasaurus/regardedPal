// Dilder Rev 2 "extended with joystick" — AAA CRADLE WITH BATT CLIPS (2026-04-27)
//
// Fork of aaa-cradle-insert-v1.scad. Defaults are baked from the
// "working insert 4-26-26" preset (matched the existing constants
// exactly — no value changes vs parent SCAD). The new feature is
// 4 vertical drop-in slots sized for the smallest Swpeet 1.5V AAA
// battery contact plate (unipolar, 7 × 7 mm stamped sheet metal),
// one at each X end of each AAA bay.
//
// How the slots are used:
//   - Each plate drops in from the plug top face into a 7.4 × 7.4 mm
//     pocket, plate face perpendicular to the cell axis.
//   - The pocket is 0.9 mm thick along X (plate ~0.5 mm + 0.2 mm slop
//     per edge), so the plate is press-fit / friction-held by its own
//     thickness.
//   - The pocket extends from cell-axis level up to the plug top so
//     wires can exit upward and the plate is droppable post-print.
//   - Spring side faces INTO the bay; the cell pushes the plate's
//     contact face axially. Solder a wire to the plate's outer face
//     before insertion.
//
// Note: only unipolar plates are used (4 total = 2 bays × 2 ends).
// Wire the cells in PARALLEL — never in series, since 2S 10440 = 7.4 V
// would exceed the Pico W's 5.5 V VSYS max.
//
// Export:
//   openscad -o aaa-cradle-with-batt-clips.3mf aaa-cradle-with-batt-clips.scad

$fn = 48;

// ============================================================
// Match the cover / base shell parameters
// ============================================================
enclosure_outer_width_along_x_axis_mm          = 94.5;   // was 91.5 — +3 mm on -X side for TP4056
enclosure_outer_depth_along_y_axis_mm          = 46;
minus_x_end_wall_thickness_mm                  = 3.0;
plus_x_end_wall_thickness_mm                   = 1.2;
perimeter_long_side_wall_thickness_y_mm_base   = 2;
corner_pillar_square_side_length_mm            = 5;

// Cover cavity inner bounds (the space the plug fills)
cavity_inner_x_start_mm = minus_x_end_wall_thickness_mm;                         // = 3.0
cavity_inner_x_end_mm =
    enclosure_outer_width_along_x_axis_mm
      - plus_x_end_wall_thickness_mm;                                            // = 93.3
cavity_inner_y_start_mm = perimeter_long_side_wall_thickness_y_mm_base;          // = 2.0
cavity_inner_y_end_mm =
    enclosure_outer_depth_along_y_axis_mm
      - perimeter_long_side_wall_thickness_y_mm_base;                            // = 44.0

// Plug outer footprint = cavity − a tiny slide-in slop on every wall.
plug_wall_slop_mm                              = 0.3;
plug_x_start_mm = cavity_inner_x_start_mm + plug_wall_slop_mm;                   // = 3.3
plug_x_end_mm   = cavity_inner_x_end_mm   - plug_wall_slop_mm;                   // = 93.0
plug_y_start_mm = cavity_inner_y_start_mm + plug_wall_slop_mm;                   // = 2.3
plug_y_end_mm   = cavity_inner_y_end_mm   - plug_wall_slop_mm;                   // = 43.7

// ============================================================
// Plug Z
// ============================================================
face_plate_bottom_z_in_cover_local_mm          = 7;
aaa_cell_diameter_mm                           = 10.5;
aaa_cell_radial_slop_mm                        = 0.3;
aaa_bay_diameter_mm =
    aaa_cell_diameter_mm + 2 * aaa_cell_radial_slop_mm;  // = 11.1
aaa_bay_wall_above_and_below_mm                = 0.5;

plug_thickness_mm =
    aaa_bay_diameter_mm + 2 * aaa_bay_wall_above_and_below_mm;  // = 12.1
plug_top_z_mm = face_plate_bottom_z_in_cover_local_mm;          // = 7
plug_bottom_z_mm = plug_top_z_mm - plug_thickness_mm;           // = -5.1

// ============================================================
// AAA cells — 2 cells lying along X, stacked in Y
// ============================================================
aaa_cell_length_mm                             = 44.5;
aaa_cell_axial_slop_mm                         = 1.0;
aaa_cell_contact_space_per_end_mm              = 2.0;
aaa_bay_length_along_x_mm =
    aaa_cell_length_mm
      + 2 * aaa_cell_contact_space_per_end_mm
      + aaa_cell_axial_slop_mm;                          // = 49.5

plus_x_pillar_cutout_minus_x_edge_mm =
    (enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm)
      - 0.4;                                              // = 87.9
aaa_bay_gap_from_pillar_cutout_mm              = 3.0;
aaa_bay_shift_toward_minus_x_mm               = 20;      // shift bays 20 mm toward origin
aaa_bay_plus_x_end_mm =
    plus_x_pillar_cutout_minus_x_edge_mm
      - aaa_bay_gap_from_pillar_cutout_mm
      - aaa_bay_shift_toward_minus_x_mm;                  // = 69.9
aaa_bay_minus_x_start_mm =
    aaa_bay_plus_x_end_mm - aaa_bay_length_along_x_mm;   // = 20.4

aaa_bay_minus_y_center_y_mm =
    plug_y_start_mm + aaa_bay_diameter_mm / 2;            // = 7.85
aaa_bay_plus_y_center_y_mm =
    plug_y_end_mm - aaa_bay_diameter_mm / 2;              // = 38.15
aaa_bay_center_z_mm =
    (plug_top_z_mm + plug_bottom_z_mm) / 2;               // ≈ 0.95

aaa_bay_top_open_z_bottom_mm                   = aaa_bay_center_z_mm;
aaa_bay_top_open_z_top_mm                      = plug_top_z_mm + 0.1;

// ============================================================
// Battery contact-plate slots — Swpeet 1.5 V AAA battery spring kit,
// smallest unipolar plate (7 × 7 mm stamped sheet metal). Four slots
// total (2 bays × 2 ends). Plates drop in from above; wires exit
// through the top of the slot.
//
// Slot orientation: plate sits in the YZ plane, perpendicular to the
// cell axis. Plate face flush with the bay's X end. Slot is centered
// on the bay Y center and on the cell axis Z.
// ============================================================
batt_clip_plate_size_y_mm                      = 7.0;     // smallest Swpeet unipolar plate
batt_clip_plate_size_z_mm                      = 7.0;     // smallest Swpeet unipolar plate
batt_clip_plate_thickness_x_mm                 = 0.5;     // sheet metal thickness
batt_clip_slot_slop_per_edge_mm                = 0.2;     // print tolerance per edge

batt_clip_slot_y_size_mm =
    batt_clip_plate_size_y_mm + 2 * batt_clip_slot_slop_per_edge_mm;            // = 7.4
batt_clip_slot_x_size_mm =
    batt_clip_plate_thickness_x_mm + 2 * batt_clip_slot_slop_per_edge_mm;       // = 0.9
batt_clip_slot_z_bottom_mm =
    aaa_bay_center_z_mm
      - batt_clip_plate_size_z_mm / 2
      - batt_clip_slot_slop_per_edge_mm;                                         // ≈ -2.75
batt_clip_slot_z_top_mm                        = plug_top_z_mm + 0.1;            // = 7.1

// ============================================================
// FPC gap
// ============================================================
fpc_gap_width_along_x_mm                       = 3;

// ============================================================
// Pico nest
// ============================================================
pico_w_board_width_along_y_mm                  = 21.0;
pico_w_board_length_along_x_mm                 = 78;   // was 61 — nest extends to x≈87.3 for 55 mm past connecting block
print_fit_tolerance_slop_mm                    = 0.4;
pico_nest_width_along_y_mm =
    pico_w_board_width_along_y_mm + 2 * print_fit_tolerance_slop_mm;              // = 21.8
pico_nest_length_along_x_mm =
    pico_w_board_length_along_x_mm + 2 * print_fit_tolerance_slop_mm;             // = 61.8
pico_nest_depth_along_z_mm                     = plug_thickness_mm;

pico_nest_x_region_start_mm =
    plug_x_start_mm + fpc_gap_width_along_x_mm;                                   // = 6.3
pico_nest_x_region_end_mm   = aaa_bay_minus_x_start_mm;                           // = 35.4
pico_nest_x_start_mm =
    (pico_nest_x_region_start_mm + pico_nest_x_region_end_mm) / 2
      - pico_nest_length_along_x_mm / 2;
pico_nest_x_start_clamped_mm =
    max(pico_nest_x_start_mm, pico_nest_x_region_start_mm);
pico_nest_y_start_mm =
    enclosure_outer_depth_along_y_axis_mm / 2
      - pico_nest_width_along_y_mm / 2;                                           // = 12.1

// ============================================================
// -X middle inset — extended to 29 mm / full height for TP4056
// ============================================================
minus_x_inset_length_along_x_mm                = 29;
minus_x_inset_height_reduction_from_plug_mm    = 0;
minus_x_inset_depth_along_z_mm =
    plug_thickness_mm - minus_x_inset_height_reduction_from_plug_mm;
minus_x_inset_x_start_mm                       = plug_x_start_mm;
minus_x_inset_x_end_mm =
    minus_x_inset_x_start_mm + minus_x_inset_length_along_x_mm;
minus_x_inset_y_start_mm                       = pico_nest_y_start_mm;
minus_x_inset_y_end_mm =
    minus_x_inset_y_start_mm + pico_nest_width_along_y_mm;
minus_x_inset_z_top_mm                         = plug_top_z_mm;
minus_x_inset_z_bottom_mm =
    minus_x_inset_z_top_mm - minus_x_inset_depth_along_z_mm;

// ============================================================
// Connecting block — fills the -X inset, 29 mm X / full height
// ============================================================
connecting_block_length_along_x_mm             = 29;
connecting_block_height_reduction_from_plug_mm = 0;
connecting_block_height_along_z_mm =
    plug_thickness_mm - connecting_block_height_reduction_from_plug_mm;
connecting_block_x_start_mm                    = minus_x_inset_x_start_mm;
connecting_block_x_end_mm =
    connecting_block_x_start_mm + connecting_block_length_along_x_mm;
connecting_block_y_start_mm                    = minus_x_inset_y_start_mm;
connecting_block_y_end_mm                      = minus_x_inset_y_end_mm;
connecting_block_z_top_mm                      = plug_top_z_mm;
connecting_block_z_bottom_mm =
    connecting_block_z_top_mm - connecting_block_height_along_z_mm;

// ============================================================
// TP4056 indent — 1 mm recess on connecting block top face
// ============================================================
tp4056_board_length_along_x_mm                 = 28;
tp4056_board_width_along_y_mm                  = 17;
tp4056_indent_depth_z_mm                       = 1.0;
tp4056_indent_slop_per_edge_mm                 = 0.2;

tp4056_indent_x_start_mm                       = connecting_block_x_start_mm;
tp4056_indent_length_mm =
    tp4056_board_length_along_x_mm + 2 * tp4056_indent_slop_per_edge_mm;
tp4056_indent_width_mm =
    tp4056_board_width_along_y_mm + 2 * tp4056_indent_slop_per_edge_mm;
tp4056_indent_y_start_mm =
    (connecting_block_y_start_mm + connecting_block_y_end_mm) / 2
      - tp4056_indent_width_mm / 2;
tp4056_indent_z_bottom_mm =
    plug_top_z_mm - tp4056_indent_depth_z_mm;

// ============================================================
// +X display connector cutout — 3 mm from bottom face
// ============================================================
plus_x_cutout_depth_z_mm                       = 3;
plus_x_cutout_z_bottom_mm                      = plug_bottom_z_mm;
plus_x_cutout_z_top_mm =
    plug_bottom_z_mm + plus_x_cutout_depth_z_mm;
plus_x_cutout_x_start_mm                       = aaa_bay_plus_x_end_mm;
plus_x_cutout_x_end_mm                         = plug_x_end_mm;

// ============================================================
// Corner pillar cutouts
// ============================================================
corner_pillar_cutout_slop_mm                   = 0.4;
corner_pillar_cutout_xy_positions = [
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


// ========== Battery clip slot helper ==========

// Drops a thin YZ slot at the X-end of a bay, sized for a Swpeet
// unipolar contact plate. is_plus_x_end = true puts the slot just
// outside the bay on the +X side; false on the -X side. The slot
// extends upward to plug_top so plates drop in from above.
module batt_clip_slot(bay_y_center_mm, bay_x_end_mm, is_plus_x_end) {
    slot_x_start =
        is_plus_x_end
          ? bay_x_end_mm
          : bay_x_end_mm - batt_clip_slot_x_size_mm;
    slot_y_start = bay_y_center_mm - batt_clip_slot_y_size_mm / 2;
    translate([slot_x_start, slot_y_start, batt_clip_slot_z_bottom_mm])
        cube([batt_clip_slot_x_size_mm,
              batt_clip_slot_y_size_mm,
              batt_clip_slot_z_top_mm - batt_clip_slot_z_bottom_mm]);
}


// ========== AAA cradle insert ==========

module aaa_cradle_insert() {
    union() {
    difference() {
        // Main plug body
        translate([plug_x_start_mm, plug_y_start_mm, plug_bottom_z_mm])
            cube([plug_x_end_mm - plug_x_start_mm,
                  plug_y_end_mm - plug_y_start_mm,
                  plug_thickness_mm]);

        // Corner pillar cutouts (4)
        for (xy = corner_pillar_cutout_xy_positions) {
            translate([xy[0] - corner_pillar_cutout_slop_mm,
                       xy[1] - corner_pillar_cutout_slop_mm,
                       plug_bottom_z_mm - 0.1])
                cube([corner_pillar_square_side_length_mm + 2 * corner_pillar_cutout_slop_mm,
                      corner_pillar_square_side_length_mm + 2 * corner_pillar_cutout_slop_mm,
                      plug_thickness_mm + 0.2]);
        }

        // FPC gap
        translate([plug_x_start_mm - 0.1,
                   plug_y_start_mm - 0.1,
                   plug_bottom_z_mm - 0.1])
            cube([fpc_gap_width_along_x_mm + 0.1,
                  plug_y_end_mm - plug_y_start_mm + 0.2,
                  plug_thickness_mm + 0.2]);

        // AAA cell bays
        for (bay_y_center_mm = [aaa_bay_minus_y_center_y_mm,
                                aaa_bay_plus_y_center_y_mm]) {
            translate([aaa_bay_minus_x_start_mm - 0.1,
                       bay_y_center_mm,
                       aaa_bay_center_z_mm])
                rotate([0, 90, 0])
                    cylinder(h = aaa_bay_length_along_x_mm + 0.2,
                             d = aaa_bay_diameter_mm);

            bay_y_start_mm = bay_y_center_mm - aaa_bay_diameter_mm / 2;
            translate([aaa_bay_minus_x_start_mm - 0.1,
                       bay_y_start_mm,
                       aaa_bay_top_open_z_bottom_mm])
                cube([aaa_bay_length_along_x_mm + 0.2,
                      aaa_bay_diameter_mm,
                      aaa_bay_top_open_z_top_mm - aaa_bay_top_open_z_bottom_mm]);
        }

        // Battery contact-plate slots — 4 total (2 bays × 2 ends)
        for (bay_y_center_mm = [aaa_bay_minus_y_center_y_mm,
                                aaa_bay_plus_y_center_y_mm]) {
            batt_clip_slot(bay_y_center_mm, aaa_bay_minus_x_start_mm, false);
            batt_clip_slot(bay_y_center_mm, aaa_bay_plus_x_end_mm, true);
        }

        // Pico nest
        translate([pico_nest_x_start_clamped_mm,
                   pico_nest_y_start_mm,
                   plug_bottom_z_mm - 0.1])
            cube([pico_nest_length_along_x_mm,
                  pico_nest_width_along_y_mm,
                  plug_thickness_mm + 0.2]);

        // -X middle inset
        translate([minus_x_inset_x_start_mm,
                   minus_x_inset_y_start_mm,
                   minus_x_inset_z_bottom_mm])
            cube([minus_x_inset_x_end_mm - minus_x_inset_x_start_mm,
                  minus_x_inset_y_end_mm - minus_x_inset_y_start_mm,
                  minus_x_inset_z_top_mm - minus_x_inset_z_bottom_mm + 0.1]);

        // +X display connector cutout — 3 mm from bottom face
        translate([plus_x_cutout_x_start_mm,
                   pico_nest_y_start_mm,
                   plus_x_cutout_z_bottom_mm - 0.1])
            cube([plus_x_cutout_x_end_mm - plus_x_cutout_x_start_mm + 0.1,
                  pico_nest_width_along_y_mm,
                  plus_x_cutout_depth_z_mm + 0.1]);
    }

    // Connecting block with battery arcs and TP4056 indent
    difference() {
        translate([connecting_block_x_start_mm,
                   connecting_block_y_start_mm,
                   connecting_block_z_bottom_mm])
            cube([connecting_block_x_end_mm - connecting_block_x_start_mm,
                  connecting_block_y_end_mm - connecting_block_y_start_mm,
                  connecting_block_z_top_mm - connecting_block_z_bottom_mm]);

        // Concave battery arcs on ±Y faces
        for (bay_y_center = [aaa_bay_minus_y_center_y_mm,
                             aaa_bay_plus_y_center_y_mm]) {
            translate([connecting_block_x_start_mm - 0.1,
                       bay_y_center,
                       aaa_bay_center_z_mm])
                rotate([0, 90, 0])
                    cylinder(h = connecting_block_x_end_mm
                                   - connecting_block_x_start_mm + 0.2,
                             r = aaa_bay_diameter_mm / 2);
        }

        // TP4056 indent
        translate([tp4056_indent_x_start_mm,
                   tp4056_indent_y_start_mm,
                   tp4056_indent_z_bottom_mm])
            cube([tp4056_indent_length_mm,
                  tp4056_indent_width_mm,
                  tp4056_indent_depth_z_mm + 0.1]);
    }
    }
}

aaa_cradle_insert();
