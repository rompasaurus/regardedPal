// Dilder Rev 2 "extended with joystick" — AAA CRADLE INSERT v1
//
// A drop-in plug shaped like the NEGATIVE SPACE of top-cover-windowed-
// screen-inlay-v3-2piece's interior. Slides up into the cover's mating
// bottom; top surface lands flush against the face-plate/display-back
// plane at cover-local z = 7 ("the plane of the screen face").
//
// Features carved INTO the plug:
//   - 3 mm-wide FPC gap on the -X (opposite-the-joystick) edge, full Y
//     and full Z, so the display's FPC cable can exit toward -X.
//   - 2 AAA cell indentations laid along X, stacked in Y, pushed to the
//     +X (joystick-side) end of the plug.
//   - Central rectangular cutout that lets the Pico W nest up against
//     the Waveshare's back, between the two AAA cells.
//
// Plug height is set by the AAA diameter (10.5 mm + 0.3 slop per side →
// 11.1 mm bay) rather than the cover's 7 mm inner cavity — so the plug
// is TALLER than the cover's cavity. Its top 7 mm slide into the cover
// cavity; the bottom 4.6 mm extends BELOW the cover mating plane, into
// the base's Pico-chamber region (Y = 12.1–33.9), which is open there.
//
// Export:
//   openscad -o aaa-cradle-insert-v1.3mf aaa-cradle-insert-v1.scad

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
      - plus_x_end_wall_thickness_mm;                                            // = 90.3
cavity_inner_y_start_mm = perimeter_long_side_wall_thickness_y_mm_base;          // = 2.0
cavity_inner_y_end_mm =
    enclosure_outer_depth_along_y_axis_mm
      - perimeter_long_side_wall_thickness_y_mm_base;                            // = 44.0

// Plug outer footprint = cavity − a tiny slide-in slop on every wall.
plug_wall_slop_mm                              = 0.3;
plug_x_start_mm = cavity_inner_x_start_mm + plug_wall_slop_mm;                   // = 3.3
plug_x_end_mm   = cavity_inner_x_end_mm   - plug_wall_slop_mm;                   // = 90.0
plug_y_start_mm = cavity_inner_y_start_mm + plug_wall_slop_mm;                   // = 2.3
plug_y_end_mm   = cavity_inner_y_end_mm   - plug_wall_slop_mm;                   // = 43.7

// ============================================================
// Plug Z — top meets the face-plate bottom (= display back = "plane of
// screen face"), bottom extends below cover mating bottom as needed to
// fully cradle the AAAs.
// ============================================================
face_plate_bottom_z_in_cover_local_mm          = 7;     // from cover-v3-2piece
aaa_cell_diameter_mm                           = 10.5;
aaa_cell_radial_slop_mm                        = 0.3;
aaa_bay_diameter_mm =
    aaa_cell_diameter_mm + 2 * aaa_cell_radial_slop_mm;  // = 11.1
aaa_bay_wall_above_and_below_mm                = 0.5;    // min wall at ±Z of cell

plug_thickness_mm =
    aaa_bay_diameter_mm + 2 * aaa_bay_wall_above_and_below_mm;  // = 12.1
plug_top_z_mm = face_plate_bottom_z_in_cover_local_mm;          // = 7
plug_bottom_z_mm = plug_top_z_mm - plug_thickness_mm;           // = -5.1 (extends
                                                                 // into base below)

// ============================================================
// AAA cells — 2 cells laying along X, stacked in Y, both pushed to
// +X (the joystick side). Cell-to-cell divider 1 mm thick.
// ============================================================
aaa_cell_length_mm                             = 44.5;
aaa_cell_axial_slop_mm                         = 1.0;
aaa_cell_contact_space_per_end_mm              = 2.0;
aaa_bay_length_along_x_mm =
    aaa_cell_length_mm
      + 2 * aaa_cell_contact_space_per_end_mm
      + aaa_cell_axial_slop_mm;                          // = 49.5

// +X end of the bay is pulled 3 mm -X past the +X corner-pillar
// cutout's -X edge, so the bays don't run into the pillar footprint.
plus_x_pillar_cutout_minus_x_edge_mm =
    (enclosure_outer_width_along_x_axis_mm
       - plus_x_end_wall_thickness_mm
       - corner_pillar_square_side_length_mm)
      - 0.4;                                                                      // = 84.9 (slop applied below)
aaa_bay_gap_from_pillar_cutout_mm              = 3.0;
aaa_bay_plus_x_end_mm =
    plus_x_pillar_cutout_minus_x_edge_mm
      - aaa_bay_gap_from_pillar_cutout_mm;                                         // = 81.9
aaa_bay_minus_x_start_mm =
    aaa_bay_plus_x_end_mm - aaa_bay_length_along_x_mm;                             // = 32.4

// Bays pushed apart until each cell's outer surface touches the plug's
// long-side edge. Cover / base inner wall provides +/-Y retention
// outside the plug.
aaa_bay_minus_y_center_y_mm =
    plug_y_start_mm + aaa_bay_diameter_mm / 2;                                     // = 7.85
aaa_bay_plus_y_center_y_mm =
    plug_y_end_mm - aaa_bay_diameter_mm / 2;                                       // = 38.15
aaa_bay_center_z_mm =
    (plug_top_z_mm + plug_bottom_z_mm) / 2;                                        // ≈ 0.95

// Top-open cut: the plug material from the cell's equator up through
// the plug top gets removed in each bay's XY bounding box, so the cell
// can be placed INTO the bay from above rather than slid in end-on.
aaa_bay_top_open_z_bottom_mm                   = aaa_bay_center_z_mm;
aaa_bay_top_open_z_top_mm                      = plug_top_z_mm + 0.1;

// ============================================================
// FPC gap — 3 mm of -X edge material shaved off, full Y, full plug Z,
// so the display's FPC cable can exit straight toward -X.
// ============================================================
fpc_gap_width_along_x_mm                       = 3;

// ============================================================
// Pico nest — central rectangular cutout from the TOP of the plug
// downward. Gives the Pico W somewhere to sit against the Waveshare's
// back (between the two AAA cells).
// ============================================================
pico_w_board_width_along_y_mm                  = 21.0;
// Pico nest length reduced 10 mm (from 51 to 41) so the middle block
// doesn't eat quite as far +X into the plug.
pico_w_board_length_along_x_mm                 = 61.0;
print_fit_tolerance_slop_mm                    = 0.4;
pico_nest_width_along_y_mm =
    pico_w_board_width_along_y_mm + 2 * print_fit_tolerance_slop_mm;              // = 21.8
pico_nest_length_along_x_mm =
    pico_w_board_length_along_x_mm + 2 * print_fit_tolerance_slop_mm;             // = 51.8
// Pico board + its tallest stacked components (headers) — full plug Z
// so the Pico nests all the way through vertically, free to sit against
// the Waveshare's back above and extend down toward the base below.
pico_nest_depth_along_z_mm                     = plug_thickness_mm;

// Pico nest is X-centered between the FPC gap and the AAA bays (so the
// Pico sits in the middle of the -X / +X extent of the plug).
pico_nest_x_region_start_mm =
    plug_x_start_mm + fpc_gap_width_along_x_mm;                                   // = 6.3
pico_nest_x_region_end_mm   = aaa_bay_minus_x_start_mm;                           // = 40.5
pico_nest_x_start_mm =
    (pico_nest_x_region_start_mm + pico_nest_x_region_end_mm) / 2
      - pico_nest_length_along_x_mm / 2;                                          // = -2.5 (overshoots)
// If the Pico's 51.8 mm footprint doesn't fit between the FPC gap end
// (x = 6.3) and the AAA bays' -X start (x = 40.5 → 34.2 mm of X), the
// nest gets clamped to start at the FPC gap end and extends as far +X
// as the board needs. The Pico ends up passing UNDER the AAA bays'
// footprint; since the bay pockets are higher in Z than the Pico nest
// bottom, that's fine — the Pico's -X end fills the plug's center and
// its +X end slides under the AAA bays.
pico_nest_x_start_clamped_mm =
    max(pico_nest_x_start_mm, pico_nest_x_region_start_mm);
pico_nest_y_start_mm =
    enclosure_outer_depth_along_y_axis_mm / 2
      - pico_nest_width_along_y_mm / 2;                                           // = 12.1

// ============================================================
// -X middle inset — a shallow pocket on the -X end of the plug's long
// axis, mirroring the Pico-nest footprint but only 9.5 mm long in X
// and 3 mm shorter in height than the full plug so it's a blind pocket
// rather than a through-slot. Opens from the top.
// ============================================================
minus_x_inset_length_along_x_mm                = 29;     // was 9.5 — extended for TP4056 board (28 mm + margin)
minus_x_inset_height_reduction_from_plug_mm    = 0;      // was 3.0 — full plug height now
minus_x_inset_depth_along_z_mm =
    plug_thickness_mm - minus_x_inset_height_reduction_from_plug_mm;               // = 9.1
minus_x_inset_x_start_mm                       = plug_x_start_mm;                  // = 3.3
minus_x_inset_x_end_mm =
    minus_x_inset_x_start_mm + minus_x_inset_length_along_x_mm;                    // = 12.8
minus_x_inset_y_start_mm                       = pico_nest_y_start_mm;             // = 12.1
minus_x_inset_y_end_mm =
    minus_x_inset_y_start_mm + pico_nest_width_along_y_mm;                         // = 33.9
minus_x_inset_z_top_mm                         = plug_top_z_mm;                    // = 7.0
minus_x_inset_z_bottom_mm =
    minus_x_inset_z_top_mm - minus_x_inset_depth_along_z_mm;                       // = -2.1

// ============================================================
// Connecting block — solid material ADDED on the +X edge of the -X
// inset (the edge opposite the plug edge closest to the origin).
// Bridges the -X inset region into the rest of the plug, filling part
// of the Pico-nest footprint back in. Same Y band and Z depth as the
// -X inset; 9.5 mm long in X; 9.1 mm tall (3 mm shorter than full
// plug Z), so it leaves a 3 mm gap below the block inside the Pico
// nest (a small cable-pass channel at the bottom).
// ============================================================
connecting_block_length_along_x_mm             = 29;     // was 9.5 — accommodate TP4056 (28 mm board + margin)
connecting_block_height_reduction_from_plug_mm = 0;      // was 3.0 — extend to full plug height
connecting_block_height_along_z_mm =
    plug_thickness_mm - connecting_block_height_reduction_from_plug_mm;            // = 9.1
// Block placed AT the -X inset's short side closest to the origin
// (the inset's -X face at X=3.3). Block X range matches the inset's
// X range so the block fills the inset with solid material from
// the -X side.
connecting_block_x_start_mm                    = minus_x_inset_x_start_mm;         // = 3.3
connecting_block_x_end_mm =
    connecting_block_x_start_mm + connecting_block_length_along_x_mm;              // = 12.8
connecting_block_y_start_mm                    = minus_x_inset_y_start_mm;         // = 12.1
connecting_block_y_end_mm                      = minus_x_inset_y_end_mm;           // = 33.9
connecting_block_z_top_mm                      = plug_top_z_mm;                    // = 7.0
connecting_block_z_bottom_mm =
    connecting_block_z_top_mm - connecting_block_height_along_z_mm;                // = -2.1

// ============================================================
// +X display connector cutout — 3 mm pocket from the plug top on
// the +X short face (furthest from origin), same Y band as the
// Pico nest. Gives clearance for the Waveshare display's FPC
// connector and ribbon cable.
// ============================================================
plus_x_cutout_depth_z_mm                       = 3;
plus_x_cutout_z_bottom_mm                      = plug_bottom_z_mm;        // = -5.1
plus_x_cutout_z_top_mm =
    plug_bottom_z_mm + plus_x_cutout_depth_z_mm;                          // = -2.1
plus_x_cutout_x_start_mm                       = aaa_bay_plus_x_end_mm;   // starts where bays end
plus_x_cutout_x_end_mm                         = plug_x_end_mm;

// ============================================================
// TP4056 USB-C charge board — 1 mm indent on the connecting block's
// top face so the board sits recessed.
// ============================================================
tp4056_board_length_along_x_mm                 = 28;
tp4056_board_width_along_y_mm                  = 17;
tp4056_indent_depth_z_mm                       = 1.0;
tp4056_indent_slop_per_edge_mm                 = 0.2;

tp4056_indent_x_start_mm                       = connecting_block_x_start_mm;
tp4056_indent_length_mm =
    tp4056_board_length_along_x_mm + 2 * tp4056_indent_slop_per_edge_mm;   // = 28.4
tp4056_indent_width_mm =
    tp4056_board_width_along_y_mm + 2 * tp4056_indent_slop_per_edge_mm;    // = 17.4
tp4056_indent_y_start_mm =
    (connecting_block_y_start_mm + connecting_block_y_end_mm) / 2
      - tp4056_indent_width_mm / 2;                                        // ≈ 14.3
tp4056_indent_z_bottom_mm =
    plug_top_z_mm - tp4056_indent_depth_z_mm;                              // = 6.0

// USB-C port cutout through the connecting block's -X face
usb_c_port_cutout_width_y_mm                   = 10;
usb_c_port_cutout_height_z_mm                  = 5;
usb_c_port_cutout_center_y_mm =
    enclosure_outer_depth_along_y_axis_mm / 2;                             // = 23
usb_c_port_cutout_center_z_mm                  = 5.5;

// ============================================================
// Corner pillar cutouts — plug wraps around the cover's 4 corner
// pillars. Cut generously so the plug doesn't bind on pillars during
// slide-in.
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


// ========== AAA cradle insert ==========

module aaa_cradle_insert() {
    // Outer difference: AAA bay cuts applied LAST so they cut through
    // both the main plug body AND the connecting block (no residual
    // walls at the junction).
    difference() {
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

        // FPC gap — shave 3 mm off the -X edge, full Y, full plug Z.
        translate([plug_x_start_mm - 0.1,
                   plug_y_start_mm - 0.1,
                   plug_bottom_z_mm - 0.1])
            cube([fpc_gap_width_along_x_mm + 0.1,
                  plug_y_end_mm - plug_y_start_mm + 0.2,
                  plug_thickness_mm + 0.2]);

        // Pico nest — central rectangular through-slot (full plug Z),
        // between the two AAA bays in Y, starting past the FPC gap in X.
        translate([pico_nest_x_start_clamped_mm,
                   pico_nest_y_start_mm,
                   plug_bottom_z_mm - 0.1])
            cube([pico_nest_length_along_x_mm,
                  pico_nest_width_along_y_mm,
                  plug_thickness_mm + 0.2]);

        // -X middle inset — pocket opening from the top of the plug,
        // on the -X end of the plug's long axis.
        translate([minus_x_inset_x_start_mm,
                   minus_x_inset_y_start_mm,
                   minus_x_inset_z_bottom_mm])
            cube([minus_x_inset_x_end_mm - minus_x_inset_x_start_mm,
                  minus_x_inset_y_end_mm - minus_x_inset_y_start_mm,
                  minus_x_inset_z_top_mm - minus_x_inset_z_bottom_mm + 0.1]);
    }

    // Connecting block — added AFTER the plug cuts so it survives
    // inside the Pico nest's footprint. Battery curves, TP4056
    // indent, and USB-C cutout are subtracted from the block itself.
    difference() {
        translate([connecting_block_x_start_mm,
                   connecting_block_y_start_mm,
                   connecting_block_z_bottom_mm])
            cube([connecting_block_x_end_mm - connecting_block_x_start_mm,
                  connecting_block_y_end_mm - connecting_block_y_start_mm,
                  connecting_block_z_top_mm - connecting_block_z_bottom_mm]);

        // Concave battery-following curves on ±Y faces
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

        // TP4056 indent — 1 mm recess on the top face
        translate([tp4056_indent_x_start_mm,
                   tp4056_indent_y_start_mm,
                   tp4056_indent_z_bottom_mm])
            cube([tp4056_indent_length_mm,
                  tp4056_indent_width_mm,
                  tp4056_indent_depth_z_mm + 0.1]);

        // USB-C port cutout through the -X face
        translate([connecting_block_x_start_mm - 1,
                   usb_c_port_cutout_center_y_mm
                     - usb_c_port_cutout_width_y_mm / 2,
                   usb_c_port_cutout_center_z_mm
                     - usb_c_port_cutout_height_z_mm / 2])
            cube([fpc_gap_width_along_x_mm + 2,
                  usb_c_port_cutout_width_y_mm,
                  usb_c_port_cutout_height_z_mm]);
    }
    } // end union

    // AAA cell bays — cut AFTER the connecting block is added so the
    // battery channels pass cleanly through everything including
    // the connecting block's ±Y overlap strips.
    aaa_bay_extended_minus_x_mm = plug_x_start_mm;
    aaa_bay_extended_length_mm =
        aaa_bay_plus_x_end_mm - aaa_bay_extended_minus_x_mm;
    for (bay_y_center_mm = [aaa_bay_minus_y_center_y_mm,
                            aaa_bay_plus_y_center_y_mm]) {
        // Cylinder cut
        translate([aaa_bay_extended_minus_x_mm - 0.1,
                   bay_y_center_mm,
                   aaa_bay_center_z_mm])
            rotate([0, 90, 0])
                cylinder(h = aaa_bay_extended_length_mm + 0.2,
                         d = aaa_bay_diameter_mm);

        // Top-open rectangular cut
        bay_y_start_mm = bay_y_center_mm - aaa_bay_diameter_mm / 2;
        translate([aaa_bay_extended_minus_x_mm - 0.1,
                   bay_y_start_mm,
                   aaa_bay_top_open_z_bottom_mm])
            cube([aaa_bay_extended_length_mm + 0.2,
                  aaa_bay_diameter_mm,
                  aaa_bay_top_open_z_top_mm - aaa_bay_top_open_z_bottom_mm]);
    }
    // +X display connector cutout — 3 mm pocket from the bottom face
    // at the +X short side for FPC connector / cable clearance.
    translate([plus_x_cutout_x_start_mm,
               pico_nest_y_start_mm,
               plus_x_cutout_z_bottom_mm - 0.1])
        cube([plus_x_cutout_x_end_mm - plus_x_cutout_x_start_mm + 0.1,
              pico_nest_width_along_y_mm,
              plus_x_cutout_depth_z_mm + 0.1]);

    } // end outer difference
}

aaa_cradle_insert();
