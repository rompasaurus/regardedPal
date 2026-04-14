#!/usr/bin/env python3
"""
Dilder PCB v7 — Research-informed optimized placement. No routing.

Board: 30mm x 80mm, 4-layer
ESP32-S3 at top, antenna overhanging board edge.
Joystick centered above USB-C at bottom.
Components placed near their connected pins for minimal trace length.

Pin mapping recap:
  LEFT pins 4-8:   Joystick (GPIO4-8) → joystick below, slightly left
  LEFT pins 9-10:  I2C (GPIO16-17) → IMU left of module
  LEFT pins 13-14: USB (GPIO19-20) → USB-C at bottom, route down left edge
  BOTTOM pins 15-20: SPI (ePaper) → 8-pin header below module
  RIGHT pins:      Unused (GND)

Module center will be at (15, 15) — antenna at y≈2 (overhangs top edge at y=0)
"""

import pcbnew, os, subprocess, json

def mm(v): return pcbnew.FromMM(v)
def pos(x, y): return pcbnew.VECTOR2I(mm(100+x), mm(100+y))

BOARD_W = 45.0
BOARD_H = 80.0
BOARD_FILE = os.path.join(os.path.dirname(__file__) or ".", "dilder.kicad_pcb")
CX = BOARD_W / 2  # 22.5mm

# ESP32 module center — antenna overhangs top board edge
# Module body: 18x25.5mm, pins on left/bottom/right
# Place center at y=15 so antenna area extends past y=0
MCU_Y = 13.0  # body top at y≈0.25, antenna extends above board edge

# Pin positions when module at (CX, MCU_Y):
# LEFT pins at x = CX - 8.75 = 8.75    (8.75mm from board left — room for passives)
# BOTTOM pins at y = MCU_Y + 12.5 = 27.5
# RIGHT pins at x = CX + 8.75 = 26.25  (8.75mm from board right)

COMPONENTS = [
    # ═══ ESP32-S3 MODULE — top, antenna overhangs ═══
    ("U1", "RF_Module:ESP32-S3-WROOM-1", CX, MCU_Y, 0, "ESP32-S3-N16R8", "C2913196"),

    # ═══ LEFT of module — decoupling + EN (near LEFT pins 2-3) ═══
    # 13.5mm gap between board edge and module left pins
    ("C3", "Capacitor_SMD:C_0402_1005Metric", 6, 9, 90, "100nF", "C14663"),
    ("C4", "Capacitor_SMD:C_0402_1005Metric", 6, 13, 90, "10uF", "C19702"),
    ("R10", "Resistor_SMD:R_0402_1005Metric", 6, 17, 90, "10k", "C25744"),

    # ═══ RIGHT of module — charge LEDs (13.5mm gap on right) ═══
    ("D2", "LED_SMD:LED_0402_1005Metric", 39, 10, 90, "RED", "C84256"),
    ("R2", "Resistor_SMD:R_0402_1005Metric", 39, 14, 90, "1k", "C25585"),
    ("D3", "LED_SMD:LED_0402_1005Metric", 42, 10, 90, "GREEN", "C72043"),
    ("R3", "Resistor_SMD:R_0402_1005Metric", 42, 14, 90, "1k", "C25585"),

    # ═══ BELOW MODULE — IMU left, ePaper connector right ═══

    # IMU — left side, below module, well clear of courtyard
    ("U6", "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm",
                                              10, 35, 0, "MPU-6050", "C24112"),
    # I2C pull-ups — left of IMU
    ("R4", "Resistor_SMD:R_0402_1005Metric", 4, 33, 90, "10k", "C25744"),
    ("R5", "Resistor_SMD:R_0402_1005Metric", 4, 37, 90, "10k", "C25744"),
    # IMU decoupling — right of IMU
    ("C7", "Capacitor_SMD:C_0402_1005Metric", 16, 33, 0, "100nF", "C14663"),
    ("C9", "Capacitor_SMD:C_0402_1005Metric", 16, 37, 0, "100nF", "C14663"),

    # ePaper JST-SH — right side, below module
    ("J3", "Connector_JST:JST_SH_SM08B-SRSS-TB_1x08-1MP_P1.00mm_Horizontal",
                                              35, 35, 0, "ePaper", ""),

    # ═══ POWER SECTION (y=43-63) ═══
    ("U4", "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                                              CX, 47, 0, "AMS1117-3.3", "C6186"),
    ("C5", "Capacitor_SMD:C_0402_1005Metric", 8, 47, 0, "10uF", "C19702"),
    ("C6", "Capacitor_SMD:C_0402_1005Metric", 37, 47, 0, "10uF", "C19702"),

    ("U2", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                                              CX, 54, 0, "TP4056", "C382139"),
    ("R1", "Resistor_SMD:R_0402_1005Metric", 33, 52, 0, "1.2k", "C25752"),
    ("D1", "Diode_SMD:D_SMA", 8, 54, 0, "SS34", "C8678"),

    # Battery protection — wide spread
    ("U3", "Package_TO_SOT_SMD:SOT-23-6", 8, 61, 0, "DW01A", "C351410"),
    ("Q1", "Package_TO_SOT_SMD:SOT-23-6", 33, 61, 0, "FS8205A", "C908265"),

    # Battery connector — right edge
    ("J2", "Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
                                              40, 54, 270, "BAT", "C131337"),

    # ═══ BOTTOM (y=65-80) ═══
    ("R8", "Resistor_SMD:R_0402_1005Metric", 10, 68, 0, "5.1k", ""),
    ("R9", "Resistor_SMD:R_0402_1005Metric", 10, 70, 0, "5.1k", ""),
    # Joystick — centered, above USB-C
    ("SW1", "Button_Switch_SMD:SW_SPST_SKQG_WithStem",
                                              CX, 70, 0, "5-Way", "C139794"),
    # USB-C — bottom center, port facing down
    ("J1", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
                                              CX, 77, 0, "USB-C", "C2765186"),
]

PA = {
    ("U1","1"):"GND", ("U1","2"):"3V3", ("U1","3"):"EN",
    ("U1","4"):"JOY_UP", ("U1","5"):"JOY_DOWN",
    ("U1","6"):"JOY_LEFT", ("U1","7"):"JOY_RIGHT",
    ("U1","8"):"JOY_CENTER",
    ("U1","9"):"I2C_SDA", ("U1","10"):"I2C_SCL",
    ("U1","13"):"USB_DM", ("U1","14"):"USB_DP",
    ("U1","15"):"EPD_CLK", ("U1","16"):"EPD_MOSI",
    ("U1","17"):"EPD_DC", ("U1","18"):"EPD_RST",
    ("U1","19"):"EPD_CS", ("U1","20"):"EPD_BUSY",
    ("U1","31"):"GND", ("U1","32"):"GND",
    ("U1","40"):"GND", ("U1","41"):"GND",
    ("J1","A4"):"VBUS", ("J1","B4"):"VBUS",
    ("J1","A1"):"GND", ("J1","B1"):"GND",
    ("J1","A12"):"GND", ("J1","B12"):"GND",
    ("J1","A6"):"USB_DP", ("J1","A7"):"USB_DM",
    ("J1","B6"):"USB_DP", ("J1","B7"):"USB_DM",
    ("J1","A5"):"CC1", ("J1","B5"):"CC2",
    ("D1","1"):"VBUS", ("D1","2"):"VBUS_CHG",
    ("U2","8"):"VBUS_CHG", ("U2","3"):"VBAT", ("U2","2"):"PROG",
    ("U2","1"):"GND", ("U2","4"):"3V3", ("U2","5"):"GND",
    ("U2","7"):"CHRG_OUT", ("U2","6"):"STDBY_OUT",
    ("U3","1"):"OD", ("U3","2"):"CS_DRAIN", ("U3","3"):"OC",
    ("U3","4"):"VBAT", ("U3","5"):"VBAT", ("U3","6"):"GND",
    ("Q1","1"):"GND", ("Q1","2"):"OD", ("Q1","3"):"CS_DRAIN",
    ("Q1","4"):"CS_DRAIN", ("Q1","5"):"OC", ("Q1","6"):"BAT_PLUS",
    ("J2","1"):"BAT_PLUS", ("J2","2"):"GND",
    ("U4","1"):"GND", ("U4","2"):"3V3", ("U4","3"):"VBAT", ("U4","4"):"3V3",
    ("C3","1"):"3V3", ("C3","2"):"GND",
    ("C4","1"):"3V3", ("C4","2"):"GND",
    ("C5","1"):"VBAT", ("C5","2"):"GND",
    ("C6","1"):"3V3", ("C6","2"):"GND",
    ("C7","1"):"3V3", ("C7","2"):"GND",
    ("C9","1"):"REGOUT", ("C9","2"):"GND",
    ("R1","1"):"PROG", ("R1","2"):"GND",
    ("R2","1"):"3V3", ("R2","2"):"CHRG_LED",
    ("R3","1"):"3V3", ("R3","2"):"STDBY_LED",
    ("R4","1"):"3V3", ("R4","2"):"I2C_SDA",
    ("R5","1"):"3V3", ("R5","2"):"I2C_SCL",
    ("R8","1"):"CC1", ("R8","2"):"GND",
    ("R9","1"):"CC2", ("R9","2"):"GND",
    ("R10","1"):"3V3", ("R10","2"):"EN",
    ("D2","1"):"CHRG_LED", ("D2","2"):"CHRG_OUT",
    ("D3","1"):"STDBY_LED", ("D3","2"):"STDBY_OUT",
    ("SW1","1"):"GND", ("SW1","2"):"JOY_CENTER",
    ("J3","1"):"3V3", ("J3","2"):"GND",
    ("J3","3"):"EPD_MOSI", ("J3","4"):"EPD_CLK",
    ("J3","5"):"EPD_CS", ("J3","6"):"EPD_DC",
    ("J3","7"):"EPD_RST", ("J3","8"):"EPD_BUSY",
    ("U6","24"):"I2C_SDA", ("U6","23"):"I2C_SCL",
    ("U6","13"):"3V3", ("U6","1"):"3V3",
    ("U6","18"):"GND", ("U6","9"):"GND",
    ("U6","11"):"GND", ("U6","8"):"GND", ("U6","10"):"REGOUT",
}

ALL_NETS = sorted(set(v for v in PA.values() if v))

def main():
    print("=" * 55)
    print(f"  Dilder v7 — {BOARD_W}x{BOARD_H}mm, placement only")
    print("=" * 55)

    board = pcbnew.BOARD()
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_ViasMinDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.3)
    board.SetCopperLayerCount(4)

    # Board outline
    pts = [(0,0),(BOARD_W,0),(BOARD_W,BOARD_H),(0,BOARD_H)]
    for i in range(4):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(pos(*pts[i])); seg.SetEnd(pos(*pts[(i+1)%4]))
        seg.SetLayer(pcbnew.Edge_Cuts); seg.SetWidth(mm(0.15))
        board.Add(seg)

    # Nets
    nm = {}
    for i, n in enumerate(ALL_NETS, 1):
        net = pcbnew.NETINFO_ITEM(board, n, i)
        board.Add(net); nm[n] = net

    # Place components
    placed = 0
    skipped = []
    for ref, fp_lib, x, y, angle, value, lcsc in COMPONENTS:
        lib, name = fp_lib.split(":")
        path = f"/usr/share/kicad/footprints/{lib}.pretty"
        fp = pcbnew.FootprintLoad(path, name) if os.path.exists(path) else None
        if not fp:
            skipped.append(ref); continue
        fp.SetReference(ref); fp.SetValue(value)
        fp.SetPosition(pos(x, y))
        if angle: fp.SetOrientationDegrees(angle)
        fp.SetLayer(pcbnew.F_Cu)
        board.Add(fp); placed += 1
    print(f"  Placed {placed}/{len(COMPONENTS)} components")
    if skipped:
        print(f"  Skipped: {', '.join(skipped)}")

    # Assign nets
    assigned = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            key = (ref, str(pad.GetNumber()))
            if key in PA and PA[key] in nm:
                pad.SetNet(nm[PA[key]]); assigned += 1
    print(f"  Assigned {assigned} pad-net connections")

    # GND zones on F.Cu and B.Cu
    for layer in [pcbnew.F_Cu, pcbnew.B_Cu]:
        zone = pcbnew.ZONE(board)
        zone.SetNet(nm["GND"]); zone.SetLayer(layer)
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        zone.SetMinThickness(mm(0.2))
        zone.SetThermalReliefGap(mm(0.3))
        zone.SetThermalReliefSpokeWidth(mm(0.4))
        o = zone.Outline(); o.NewOutline()
        m = 0.3
        o.Append(mm(100+m), mm(100+m))
        o.Append(mm(100+BOARD_W-m), mm(100+m))
        o.Append(mm(100+BOARD_W-m), mm(100+BOARD_H-m))
        o.Append(mm(100+m), mm(100+BOARD_H-m))
        board.Add(zone)

    # Silkscreen
    for txt, x, y, sz in [("DILDER", CX, 78, 1.0), ("v0.7", CX+6, 78, 0.7)]:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(txt); t.SetPosition(pos(x, y)); t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(mm(sz), mm(sz)))
        t.SetTextThickness(mm(sz * 0.15))
        board.Add(t)

    board.Save(BOARD_FILE)
    print(f"  Saved: {BOARD_FILE}")
    print(f"  NO ROUTING — placement only")

    # DRC (just to check courtyard overlaps)
    print("  Checking placement (DRC)...")
    os.makedirs("/tmp/dilder-drc", exist_ok=True)
    subprocess.run(["kicad-cli", "pcb", "drc", "--output", "/tmp/dilder-drc/drc-report.json",
                    "--format", "json", "--severity-all", BOARD_FILE], capture_output=True)
    try:
        with open("/tmp/dilder-drc/drc-report.json") as f:
            drc = json.load(f)
        v = drc.get("violations", [])
        by_type = {}
        for x in v: by_type.setdefault(x["type"], 0); by_type[x["type"]] += 1
        # Only show placement-related issues
        for t in ["courtyards_overlap", "copper_edge_clearance", "silk_overlap"]:
            if t in by_type:
                print(f"    {t}: {by_type[t]}")
        uncon = len(drc.get("unconnected_items", []))
        print(f"    unconnected: {uncon} (expected — no routing yet)")
    except: pass

    # Render
    print("  Rendering...")
    os.makedirs("/tmp/dilder-routed", exist_ok=True)
    for args, out in [
        ([], "board-top.png"),
        (["--perspective", "--rotate", "-35,0,15"], "board-3d.png"),
    ]:
        subprocess.run(["kicad-cli", "pcb", "render", "--output", f"/tmp/dilder-routed/{out}",
                       "--width", "2400", "--height", "1600", "--quality", "basic",
                       *args, BOARD_FILE], capture_output=True)
    print("  Done!")

if __name__ == "__main__":
    main()
