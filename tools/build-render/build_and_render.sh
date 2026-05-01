#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────
# build_and_render.sh — Interactive render pipeline for Dilder FreeCAD models
#
# Usage:
#   ./build_and_render.sh              # full interactive menu
#   ./build_and_render.sh --rebuild    # rebuild from macro, then menu
# ─────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HARDWARE_DIR="$PROJECT_ROOT/hardware-design"
MACRO_DIR="$HARDWARE_DIR/freecad-mk2"
RENDER_DIR="$HARDWARE_DIR/renders"
ANIM_DIR="$RENDER_DIR/anim"
WEBSITE_IMG="$PROJECT_ROOT/website/docs/assets/images/enclosure"

MODEL_MACRO="$MACRO_DIR/dilder_rev2_mk2.FCMacro"
RENDER_MACRO="$MACRO_DIR/render_views.FCMacro"
ANIM_MACRO="$MACRO_DIR/animate_assembly.FCMacro"

REBUILD=false
for arg in "$@"; do
    case "$arg" in
        --rebuild) REBUILD=true ;;
        --help|-h)
            echo "Usage: $0 [--rebuild]"
            exit 0 ;;
    esac
done

# ─── Colors ───
B="\033[1m"
D="\033[2m"
C="\033[36m"
G="\033[32m"
Y="\033[33m"
R="\033[31m"
W="\033[97m"
M="\033[35m"
X="\033[0m"

hr() { echo -e "${C}  ──────────────────────────────────────────────────────${X}"; }
header() {
    clear
    echo -e "${B}${C}"
    echo "  ╔═══════════════════════════════════════════════════════╗"
    echo "  ║         Dilder Rev 2 Mk2 — Render Pipeline           ║"
    echo "  ╚═══════════════════════════════════════════════════════╝"
    echo -e "${X}"
}

prompt() { echo -ne "  ${B}${C}$1${X} "; }

# ─── State ───
FCSTD_FILE=""
RENDER_SET=""
RENDER_STYLE=""
RESOLUTION=""
BACKGROUND=""
COMPONENTS=""
INCLUDE_ANIM=false

# =====================================================================
# SCREEN 1 — Pick FCStd file
# =====================================================================
pick_file() {
    header
    echo -e "  ${B}${W}STEP 1 — Select FreeCAD Model${X}"
    echo -e "  ${D}Sorted by date modified (newest first)${X}"
    hr

    local files=()
    while IFS= read -r -d '' f; do
        files+=("$f")
    done < <(find "$MACRO_DIR" -maxdepth 1 -name "*.FCStd" -printf '%T@\t%p\0' \
             | sort -z -t$'\t' -k1 -rn \
             | cut -z -f2-)

    if [ ${#files[@]} -eq 0 ]; then
        echo -e "  ${Y}No .FCStd files found in $MACRO_DIR${X}"
        exit 1
    fi

    local i=1
    for f in "${files[@]}"; do
        local name mod_date size
        name="$(basename "$f" .FCStd)"
        mod_date="$(date -r "$f" '+%Y-%m-%d %H:%M')"
        size="$(du -h "$f" | cut -f1)"

        if [ $i -eq 1 ]; then
            echo -e "  ${G}${B}$i)${X} ${G}$name${X}"
            echo -e "     ${D}$mod_date  |  $size  |  ${G}newest${X}"
        elif [ $i -le 3 ]; then
            echo -e "  ${W}$i)${X} $name"
            echo -e "     ${D}$mod_date  |  $size${X}"
        else
            echo -e "  ${D}$i) $name${X}"
            echo -e "     ${D}$mod_date  |  $size${X}"
        fi
        ((i++))
    done

    hr
    echo -e "  ${M}r)${X} Rebuild from macro first"
    echo -e "  ${R}q)${X} Quit"
    echo ""

    while true; do
        prompt "Model [1-${#files[@]}/r/q]:"
        read -r choice
        case "$choice" in
            q|Q) exit 0 ;;
            r|R) REBUILD=true; FCSTD_FILE="$MACRO_DIR/Dilder_Rev2_Mk2.FCStd"; return ;;
            *)
                if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#files[@]} ]; then
                    FCSTD_FILE="${files[$((choice - 1))]}"
                    return
                fi
                echo -e "  ${Y}Invalid — enter 1-${#files[@]}, r, or q${X}"
                ;;
        esac
    done
}

# =====================================================================
# SCREEN 2 — What to render
# =====================================================================
pick_render_set() {
    header
    echo -e "  ${B}${W}STEP 2 — What to Render${X}"
    echo -e "  ${D}Selected: $(basename "$FCSTD_FILE" .FCStd)${X}"
    hr
    echo ""
    echo -e "  ${B}${G}Full Sets${X}"
    echo -e "  ${W}1)${X}  Everything              ${D}— all assembly views + components + exploded (40+ images)${X}"
    echo -e "  ${W}2)${X}  Assembly only            ${D}— hero, 6 angles, cover-removed, opaque (10 images)${X}"
    echo -e "  ${W}3)${X}  Exploded views only      ${D}— iso, front, top (3 images)${X}"
    echo -e "  ${W}4)${X}  Component portraits      ${D}— isolated render of each body/peripheral (14 images)${X}"
    echo ""
    echo -e "  ${B}${C}Individual Bodies${X}"
    echo -e "  ${W}5)${X}  Base plate               ${D}— iso + top + bottom${X}"
    echo -e "  ${W}6)${X}  AAA cradle               ${D}— iso + top + bottom${X}"
    echo -e "  ${W}7)${X}  Top cover                ${D}— iso transparent + opaque + bottom (anchor pad)${X}"
    echo -e "  ${W}8)${X}  Thumbpiece               ${D}— iso close-up${X}"
    echo ""
    echo -e "  ${B}${M}Peripherals${X}"
    echo -e "  ${W}9)${X}  Joystick PCB             ${D}— K1-1506SN-01 breakout board${X}"
    echo -e "  ${W}10)${X} Pico 2 W + headers       ${D}— board with pin headers${X}"
    echo -e "  ${W}11)${X} Piezo speaker             ${D}— 20 mm FT-20T disc${X}"
    echo -e "  ${W}12)${X} IMU accelerometer         ${D}— GY-6500 MPU-6500 module${X}"
    echo -e "  ${W}13)${X} TP4056 charger            ${D}— USB-C charge module${X}"
    echo -e "  ${W}14)${X} Batteries + clips         ${D}— AAA cells with contact plates${X}"
    echo -e "  ${W}15)${X} E-ink display             ${D}— Waveshare 2.13\" module${X}"
    echo -e "  ${W}16)${X} Solar panel               ${D}— AK 62x36 panel + leads${X}"
    echo ""
    echo -e "  ${B}${Y}Special${X}"
    echo -e "  ${W}17)${X} Detail close-ups          ${D}— joystick, thumbpiece, display, sensors${X}"
    echo -e "  ${W}18)${X} Animation frames          ${D}— 13-step assembly drop animation${X}"
    echo -e "  ${W}19)${X} Custom combo              ${D}— pick exactly which components to show${X}"
    echo ""
    hr
    prompt "Render set [1-19]:"
    read -r choice
    RENDER_SET="$choice"
}

# =====================================================================
# SCREEN 3 — Render style
# =====================================================================
pick_style() {
    header
    echo -e "  ${B}${W}STEP 3 — Render Style${X}"
    hr
    echo ""
    echo -e "  ${B}${G}Resolution${X}"
    echo -e "  ${W}1)${X}  1920 x 1440  ${D}— high quality (default)${X}"
    echo -e "  ${W}2)${X}  2560 x 1920  ${D}— ultra high${X}"
    echo -e "  ${W}3)${X}  1280 x  960  ${D}— fast preview${X}"
    echo -e "  ${W}4)${X}   960 x  720  ${D}— thumbnail${X}"
    echo ""
    prompt "Resolution [1-4, default=1]:"
    read -r res_choice
    case "$res_choice" in
        2) RESOLUTION="2560 1920" ;;
        3) RESOLUTION="1280 960" ;;
        4) RESOLUTION="960 720" ;;
        *) RESOLUTION="1920 1440" ;;
    esac

    echo ""
    echo -e "  ${B}${C}Background${X}"
    echo -e "  ${W}1)${X}  Transparent  ${D}— PNG alpha channel (default)${X}"
    echo -e "  ${W}2)${X}  White        ${D}— solid white background${X}"
    echo -e "  ${W}3)${X}  Black        ${D}— solid black background${X}"
    echo -e "  ${W}4)${X}  Light gray   ${D}— #E8E8E8${X}"
    echo ""
    prompt "Background [1-4, default=1]:"
    read -r bg_choice
    case "$bg_choice" in
        2) BACKGROUND="White" ;;
        3) BACKGROUND="Black" ;;
        4) BACKGROUND="#E8E8E8" ;;
        *) BACKGROUND="Transparent" ;;
    esac

    echo ""
    echo -e "  ${B}${M}Cover Transparency${X}"
    echo -e "  ${W}1)${X}  40%    ${D}— default translucent (see internals)${X}"
    echo -e "  ${W}2)${X}  0%     ${D}— fully opaque (finished product look)${X}"
    echo -e "  ${W}3)${X}  70%    ${D}— very transparent (component focus)${X}"
    echo -e "  ${W}4)${X}  85%    ${D}— ghost mode (barely visible cover)${X}"
    echo ""
    prompt "Cover transparency [1-4, default=1]:"
    read -r trans_choice
    case "$trans_choice" in
        2) COVER_TRANS=0 ;;
        3) COVER_TRANS=70 ;;
        4) COVER_TRANS=85 ;;
        *) COVER_TRANS=40 ;;
    esac
}

# =====================================================================
# SCREEN 4 — Custom component picker (only for option 19)
# =====================================================================
pick_components() {
    header
    echo -e "  ${B}${W}STEP 3b — Pick Components to Show${X}"
    echo -e "  ${D}Enter numbers separated by spaces (e.g. 1 3 5 8)${X}"
    hr
    echo ""
    echo -e "  ${B}Bodies${X}"
    echo -e "  ${W}1)${X}  BasePlate"
    echo -e "  ${W}2)${X}  AAACradle"
    echo -e "  ${W}3)${X}  TopCover"
    echo -e "  ${W}4)${X}  Thumbpiece"
    echo ""
    echo -e "  ${B}Electronics${X}"
    echo -e "  ${W}5)${X}  Pico 2 W + Headers"
    echo -e "  ${W}6)${X}  JoystickPCB"
    echo -e "  ${W}7)${X}  TP4056 Module"
    echo -e "  ${W}8)${X}  E-Ink Display"
    echo ""
    echo -e "  ${B}Sensors${X}"
    echo -e "  ${W}9)${X}  Piezo Speaker"
    echo -e "  ${W}10)${X} IMU Module"
    echo ""
    echo -e "  ${B}Power${X}"
    echo -e "  ${W}11)${X} AAA Batteries + Clips"
    echo -e "  ${W}12)${X} Solar Panel + Leads"
    echo ""
    hr
    prompt "Components [e.g. 1 3 5 9 10]:"
    read -r comp_choices
    COMPONENTS="$comp_choices"
}

# =====================================================================
# SCREEN 5 — Confirmation
# =====================================================================
confirm() {
    header
    echo -e "  ${B}${W}RENDER SUMMARY${X}"
    hr
    echo ""
    echo -e "  ${B}Model:${X}        $(basename "$FCSTD_FILE" .FCStd)"
    echo -e "  ${B}Render set:${X}   $RENDER_SET_NAME"
    echo -e "  ${B}Resolution:${X}   ${RESOLUTION// /x}"
    echo -e "  ${B}Background:${X}   $BACKGROUND"
    echo -e "  ${B}Cover:${X}        ${COVER_TRANS}% transparent"
    if [ -n "$COMPONENTS" ]; then
        echo -e "  ${B}Components:${X}   $COMPONENTS"
    fi
    echo ""
    hr
    prompt "Proceed? [Y/n]:"
    read -r yn
    case "$yn" in
        n|N) echo "  Cancelled."; exit 0 ;;
    esac
}

# =====================================================================
# Generate the render Python script on the fly
# =====================================================================
generate_render_script() {
    local script="$RENDER_DIR/_render_job.py"
    local w h
    w="${RESOLUTION%% *}"
    h="${RESOLUTION##* }"

    # Map component numbers to FreeCAD object names
    declare -A COMP_MAP=(
        [1]="BasePlate"
        [2]="AAACradle"
        [3]="TopCover"
        [4]="Thumbpiece"
        [5]="Pico2W_Board Pico2W_Headers"
        [6]="JoystickPCB"
        [7]="TP4056_Module"
        [8]="EInkDisplay_Module EInkDisplay_Panel"
        [9]="Piezo_Brass Piezo_Ceramic"
        [10]="IMU_Module"
        [11]="AAA_Battery_1 AAA_Battery_1_PosTerm AAA_Battery_2 AAA_Battery_2_PosTerm BatteryClips_Positive BatteryClips_Negative BatteryWiring_Positive BatteryWiring_Negative"
        [12]="Solar_Frame Solar_Cells Solar_Wire_Plus Solar_Wire_Minus"
    )

    # Build show list for custom combo
    local show_list=""
    if [ -n "$COMPONENTS" ]; then
        for num in $COMPONENTS; do
            if [ -n "${COMP_MAP[$num]:-}" ]; then
                show_list="$show_list ${COMP_MAP[$num]}"
            fi
        done
    fi

    cat > "$script" << PYEOF
"""Auto-generated render job — $(date '+%Y-%m-%d %H:%M')"""
import os, time
import FreeCAD as App
import FreeCADGui as Gui

doc = App.openDocument("$FCSTD_FILE")
Gui.ActiveDocument = Gui.getDocument(doc.Name)
view = Gui.ActiveDocument.activeView()

RENDER_DIR = "$RENDER_DIR"
W, H = $w, $h
BG = "$BACKGROUND"

def top_objects():
    """Return only top-level objects (Bodies + standalone Part::Features).
    Skip internal PartDesign features, sketches, and origin objects —
    toggling those hides the parent Body's rendered shape."""
    result = []
    # Collect names of all objects that live inside a Body's Group
    internal = set()
    for o in doc.Objects:
        if hasattr(o, "Group"):
            for child in o.Group:
                internal.add(child.Name)
    for o in doc.Objects:
        if o.Name in internal:
            continue
        if not hasattr(o, "ViewObject"):
            continue
        # Skip the spreadsheet
        if o.TypeId == "Spreadsheet::Sheet":
            continue
        result.append(o)
    return result

def flush(n=5, wait=0.3):
    """Pump the Qt event loop n times with wait between — gives the 3D
    viewport time to actually finish its OpenGL draw before we screenshot."""
    for _ in range(n):
        Gui.updateGui()
        time.sleep(wait)

def show(names):
    s = set(names)
    for o in top_objects():
        try: o.ViewObject.Visibility = (o.Name in s)
        except: pass
    flush()

def show_all():
    for o in top_objects():
        try: o.ViewObject.Visibility = True
        except: pass
    flush()

def hide_all():
    for o in top_objects():
        try: o.ViewObject.Visibility = False
        except: pass
    flush()

def set_trans(t):
    for o in top_objects():
        if o.Name == "TopCover":
            try: o.ViewObject.Transparency = t
            except: pass
    flush(2, 0.1)

def save(name, iso=True, fit=True):
    if iso:
        try: Gui.SendMsgToActiveView("ViewIsometric")
        except: pass
    if fit: Gui.SendMsgToActiveView("ViewFit")
    flush(5, 0.3)  # 1.5s total — let viewport fully render
    out = os.path.join(RENDER_DIR, name)
    view.saveImage(out, W, H, BG)
    print(f"  wrote {out}")

def set_camera(yaw, pitch, dist=250):
    """Set camera to a specific angle. yaw/pitch in degrees."""
    import math
    r = math.radians
    cx, cy, cz = 47.0, 23.0, 10.0  # model center approx
    x = cx + dist * math.cos(r(pitch)) * math.sin(r(yaw))
    y = cy + dist * math.cos(r(pitch)) * math.cos(r(yaw))
    z = cz + dist * math.sin(r(pitch))
    cam = view.getCameraNode()
    cam.position.setValue(x, y, z)
    cam.pointAt(App.Vector(cx, cy, cz).cast_to_vector() if hasattr(App.Vector, 'cast_to_vector') else (cx, cy, cz))
    Gui.SendMsgToActiveView("ViewFit")
    flush()

def vtop():
    Gui.SendMsgToActiveView("ViewTop"); Gui.SendMsgToActiveView("ViewFit"); flush()
def vfront():
    Gui.SendMsgToActiveView("ViewFront"); Gui.SendMsgToActiveView("ViewFit"); flush()
def vrear():
    Gui.SendMsgToActiveView("ViewRear"); Gui.SendMsgToActiveView("ViewFit"); flush()
def vleft():
    Gui.SendMsgToActiveView("ViewLeft"); Gui.SendMsgToActiveView("ViewFit"); flush()
def vright():
    Gui.SendMsgToActiveView("ViewRight"); Gui.SendMsgToActiveView("ViewFit"); flush()
def vbottom():
    Gui.SendMsgToActiveView("ViewBottom"); Gui.SendMsgToActiveView("ViewFit"); flush()

set_trans($COVER_TRANS)
os.makedirs(RENDER_DIR, exist_ok=True)
print("Rendering...")

PYEOF

    # Append render commands based on RENDER_SET
    case "$RENDER_SET" in
        1) # Everything
            cat >> "$script" << 'PYEOF'
# ── Full assembly views ──
show_all(); save("var-01-hero-iso.png")
vtop();     save("var-02-top-translucent.png", iso=False, fit=False)
vfront();   save("var-03-front-elevation.png", iso=False, fit=False)
vleft();    save("var-04-side-left.png", iso=False, fit=False)
vright();   save("var-05-side-right.png", iso=False, fit=False)
vrear();    save("var-06-rear-elevation.png", iso=False, fit=False)

# ── Angled hero shots (set camera via Coin3D rotation) ──
import math
from pivy import coin

def angled_view(yaw_deg, pitch_deg):
    """Set camera orientation via yaw (left-right) and pitch (up-down)."""
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    # Build rotation: first yaw around Z, then pitch around X
    ry = coin.SbRotation(coin.SbVec3f(0, 0, 1), yaw)
    rp = coin.SbRotation(coin.SbVec3f(1, 0, 0), -pitch)
    cam = view.getCameraNode()
    cam.orientation.setValue(rp * ry)
    Gui.SendMsgToActiveView("ViewFit")
    flush()

# 3/4 front-right (classic product shot)
show_all()
angled_view(35, 25)
save("var-06a-angle-front-right.png", iso=False, fit=False)

# 3/4 front-left
show_all()
angled_view(-35, 25)
save("var-06b-angle-front-left.png", iso=False, fit=False)

# Low angle (looking slightly up)
show_all()
angled_view(30, 10)
save("var-06c-angle-low.png", iso=False, fit=False)

# 3/4 rear elevated
show_all()
angled_view(150, 35)
save("var-06d-angle-rear.png", iso=False, fit=False)

# ── Cover removed ──
for o in top_objects():
    if o.Name in ("TopCover","Thumbpiece"):
        try: o.ViewObject.Visibility = False
        except: pass
Gui.updateGui()
save("var-07-cover-removed-iso.png")
vtop(); save("var-08-cover-removed-top.png", iso=False, fit=False)

# ── Individual bodies ──
show(["BasePlate","Piezo_Brass","Piezo_Ceramic","IMU_Module"])
save("var-11-pico-sensors-on-base.png")
vtop(); save("var-12-baseplate-sensors-top.png", iso=False, fit=False)
save("var-13-baseplate-sensors-iso.png")

show(["BasePlate","Solar_Frame","Solar_Cells","Solar_Wire_Plus","Solar_Wire_Minus"])
vbottom(); save("var-14-baseplate-bottom.png", iso=False, fit=False)

show(["BasePlate"])
vtop(); save("var-15-baseplate-top-bare.png", iso=False, fit=False)

show(["AAACradle"])
vbottom(); save("var-16-cradle-bottom.png", iso=False, fit=False)

show(["TopCover"]); set_trans(0)
vbottom(); save("var-17-cover-bottom.png", iso=False, fit=False)
save("var-18-cover-anchor-iso.png")

# ── Details ──
PYEOF
            cat >> "$script" << PYEOF
set_trans($COVER_TRANS)
PYEOF
            cat >> "$script" << 'PYEOF'
show_all(); save("var-19-joystick-detail.png")
vtop(); save("var-20-joystick-aligned-top.png", iso=False, fit=False)
show_all(); set_trans(85); save("var-21-thumbpiece-hero.png")

# ── Exploded ──
show_all()
PYEOF
            cat >> "$script" << PYEOF
set_trans($COVER_TRANS)
PYEOF
            cat >> "$script" << 'PYEOF'
saved = {}
for o in top_objects():
    if o.Name in ("TopCover","AAACradle","BasePlate","Thumbpiece"):
        saved[o.Name] = App.Placement(o.Placement)
for nm, dz in [("TopCover",30),("Thumbpiece",40),("AAACradle",0),("BasePlate",-25)]:
    obj = doc.getObject(nm)
    if obj:
        p = App.Placement(saved.get(nm, obj.Placement))
        p.Base = p.Base + App.Vector(0,0,dz); obj.Placement = p
doc.recompute()
save("var-23-exploded-iso.png")
vfront(); save("var-24-exploded-front.png", iso=False, fit=False)
vtop(); save("var-25-exploded-top.png", iso=False, fit=False)
for nm, p in saved.items():
    obj = doc.getObject(nm)
    if obj: obj.Placement = p
doc.recompute()

# ── Opaque assembled ──
show_all(); set_trans(0)
save("var-26-assembled-opaque-iso.png")
vfront(); save("var-27-assembled-opaque-front.png", iso=False, fit=False)

# ── Component portraits ──
PYEOF
            cat >> "$script" << PYEOF
set_trans($COVER_TRANS)
PYEOF
            cat >> "$script" << 'PYEOF'
show(["BasePlate"]); save("comp-baseplate-iso.png")
vtop(); save("comp-baseplate-top.png", iso=False, fit=False)
vbottom(); save("comp-baseplate-bottom.png", iso=False, fit=False)

show(["AAACradle"]); save("comp-cradle-iso.png")
vtop(); save("comp-cradle-top.png", iso=False, fit=False)
vbottom(); save("comp-cradle-bottom.png", iso=False, fit=False)

show(["TopCover"]); set_trans(40); save("comp-cover-iso.png")
set_trans(0); save("comp-cover-iso-opaque.png")
vbottom(); save("comp-cover-bottom.png", iso=False, fit=False)
vtop(); save("comp-cover-top.png", iso=False, fit=False)

show(["Thumbpiece"]); save("comp-thumbpiece-iso.png")
show(["JoystickPCB"]); save("comp-joystick-pcb-iso.png")
show(["Pico2W_Board","Pico2W_Headers"]); save("comp-pico-iso.png")
show(["Piezo_Brass","Piezo_Ceramic"]); save("comp-piezo-iso.png")
show(["IMU_Module"]); save("comp-imu-iso.png")
show(["Solar_Frame","Solar_Cells","Solar_Wire_Plus","Solar_Wire_Minus"])
vbottom(); save("comp-solar-bottom.png", iso=False, fit=False)
save("comp-solar-iso.png")
show(["TP4056_Module"]); save("comp-tp4056-iso.png")
show(["AAA_Battery_1","AAA_Battery_1_PosTerm","AAA_Battery_2","AAA_Battery_2_PosTerm",
      "BatteryClips_Positive","BatteryClips_Negative","BatteryWiring_Positive","BatteryWiring_Negative"])
save("comp-batteries-iso.png")
show(["EInkDisplay_Module","EInkDisplay_Panel"]); save("comp-display-iso.png")
PYEOF
            ;;

        2) # Assembly only
            cat >> "$script" << 'PYEOF'
show_all(); save("var-01-hero-iso.png")
vtop(); save("var-02-top-translucent.png", iso=False, fit=False)
vfront(); save("var-03-front-elevation.png", iso=False, fit=False)
vleft(); save("var-04-side-left.png", iso=False, fit=False)
vright(); save("var-05-side-right.png", iso=False, fit=False)
vrear(); save("var-06-rear-elevation.png", iso=False, fit=False)
# Angled shots
import math
from pivy import coin
def angled_view(yaw_deg, pitch_deg):
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    ry = coin.SbRotation(coin.SbVec3f(0, 0, 1), yaw)
    rp = coin.SbRotation(coin.SbVec3f(1, 0, 0), -pitch)
    cam = view.getCameraNode()
    cam.orientation.setValue(rp * ry)
    Gui.SendMsgToActiveView("ViewFit")
    flush()
show_all(); angled_view(35, 25)
save("var-06a-angle-front-right.png", iso=False, fit=False)
show_all(); angled_view(-35, 25)
save("var-06b-angle-front-left.png", iso=False, fit=False)
# Cover removed
for o in top_objects():
    if o.Name in ("TopCover","Thumbpiece"):
        try: o.ViewObject.Visibility = False
        except: pass
flush()
save("var-07-cover-removed-iso.png")
vtop(); save("var-08-cover-removed-top.png", iso=False, fit=False)
show_all(); set_trans(0)
save("var-26-assembled-opaque-iso.png")
vfront(); save("var-27-assembled-opaque-front.png", iso=False, fit=False)
PYEOF
            ;;

        3) # Exploded only
            cat >> "$script" << 'PYEOF'
show_all()
saved = {}
for o in top_objects():
    if o.Name in ("TopCover","AAACradle","BasePlate","Thumbpiece"):
        saved[o.Name] = App.Placement(o.Placement)
for nm, dz in [("TopCover",30),("Thumbpiece",40),("AAACradle",0),("BasePlate",-25)]:
    obj = doc.getObject(nm)
    if obj:
        p = App.Placement(saved.get(nm, obj.Placement))
        p.Base = p.Base + App.Vector(0,0,dz); obj.Placement = p
doc.recompute()
save("var-23-exploded-iso.png")
vfront(); save("var-24-exploded-front.png", iso=False, fit=False)
vtop(); save("var-25-exploded-top.png", iso=False, fit=False)
for nm, p in saved.items():
    obj = doc.getObject(nm)
    if obj: obj.Placement = p
doc.recompute()
PYEOF
            ;;

        4) # Component portraits
            cat >> "$script" << 'PYEOF'
show(["BasePlate"]); save("comp-baseplate-iso.png")
vtop(); save("comp-baseplate-top.png", iso=False, fit=False)
vbottom(); save("comp-baseplate-bottom.png", iso=False, fit=False)
show(["AAACradle"]); save("comp-cradle-iso.png")
vtop(); save("comp-cradle-top.png", iso=False, fit=False)
vbottom(); save("comp-cradle-bottom.png", iso=False, fit=False)
show(["TopCover"]); set_trans(40); save("comp-cover-iso.png")
set_trans(0); save("comp-cover-iso-opaque.png")
vbottom(); save("comp-cover-bottom.png", iso=False, fit=False)
vtop(); save("comp-cover-top.png", iso=False, fit=False)
show(["Thumbpiece"]); save("comp-thumbpiece-iso.png")
show(["JoystickPCB"]); save("comp-joystick-pcb-iso.png")
show(["Pico2W_Board","Pico2W_Headers"]); save("comp-pico-iso.png")
show(["Piezo_Brass","Piezo_Ceramic"]); save("comp-piezo-iso.png")
show(["IMU_Module"]); save("comp-imu-iso.png")
show(["Solar_Frame","Solar_Cells","Solar_Wire_Plus","Solar_Wire_Minus"])
vbottom(); save("comp-solar-bottom.png", iso=False, fit=False)
save("comp-solar-iso.png")
show(["TP4056_Module"]); save("comp-tp4056-iso.png")
show(["AAA_Battery_1","AAA_Battery_1_PosTerm","AAA_Battery_2","AAA_Battery_2_PosTerm",
      "BatteryClips_Positive","BatteryClips_Negative","BatteryWiring_Positive","BatteryWiring_Negative"])
save("comp-batteries-iso.png")
show(["EInkDisplay_Module","EInkDisplay_Panel"]); save("comp-display-iso.png")
PYEOF
            ;;

        5) # Base plate
            cat >> "$script" << 'PYEOF'
show(["BasePlate"]); save("comp-baseplate-iso.png")
vtop(); save("comp-baseplate-top.png", iso=False, fit=False)
vbottom(); save("comp-baseplate-bottom.png", iso=False, fit=False)
vfront(); save("comp-baseplate-front.png", iso=False, fit=False)
show(["BasePlate","Piezo_Brass","Piezo_Ceramic","IMU_Module"])
save("comp-baseplate-sensors-iso.png")
vtop(); save("comp-baseplate-sensors-top.png", iso=False, fit=False)
PYEOF
            ;;

        6) # Cradle
            cat >> "$script" << 'PYEOF'
show(["AAACradle"]); save("comp-cradle-iso.png")
vtop(); save("comp-cradle-top.png", iso=False, fit=False)
vbottom(); save("comp-cradle-bottom.png", iso=False, fit=False)
vfront(); save("comp-cradle-front.png", iso=False, fit=False)
PYEOF
            ;;

        7) # Top cover
            cat >> "$script" << 'PYEOF'
show(["TopCover"]); set_trans(40); save("comp-cover-iso.png")
set_trans(0); save("comp-cover-iso-opaque.png")
vbottom(); save("comp-cover-bottom.png", iso=False, fit=False)
vtop(); save("comp-cover-top.png", iso=False, fit=False)
vfront(); save("comp-cover-front.png", iso=False, fit=False)
set_trans(40)
PYEOF
            ;;

        8)  echo 'show(["Thumbpiece"]); save("comp-thumbpiece-iso.png")' >> "$script" ;;
        9)  echo 'show(["JoystickPCB"]); save("comp-joystick-pcb-iso.png")' >> "$script" ;;
        10) echo 'show(["Pico2W_Board","Pico2W_Headers"]); save("comp-pico-iso.png")' >> "$script" ;;
        11) echo 'show(["Piezo_Brass","Piezo_Ceramic"]); save("comp-piezo-iso.png")' >> "$script" ;;
        12) echo 'show(["IMU_Module"]); save("comp-imu-iso.png")' >> "$script" ;;
        13) echo 'show(["TP4056_Module"]); save("comp-tp4056-iso.png")' >> "$script" ;;
        14) cat >> "$script" << 'PYEOF'
show(["AAA_Battery_1","AAA_Battery_1_PosTerm","AAA_Battery_2","AAA_Battery_2_PosTerm",
      "BatteryClips_Positive","BatteryClips_Negative","BatteryWiring_Positive","BatteryWiring_Negative"])
save("comp-batteries-iso.png")
PYEOF
            ;;
        15) echo 'show(["EInkDisplay_Module","EInkDisplay_Panel"]); save("comp-display-iso.png")' >> "$script" ;;
        16) cat >> "$script" << 'PYEOF'
show(["Solar_Frame","Solar_Cells","Solar_Wire_Plus","Solar_Wire_Minus"])
vbottom(); save("comp-solar-bottom.png", iso=False, fit=False)
save("comp-solar-iso.png")
PYEOF
            ;;

        17) # Detail close-ups
            cat >> "$script" << 'PYEOF'
show_all(); save("var-19-joystick-detail.png")
vtop(); save("var-20-joystick-aligned-top.png", iso=False, fit=False)
show_all(); set_trans(85); save("var-21-thumbpiece-hero.png")
show(["BasePlate","Piezo_Brass","Piezo_Ceramic","IMU_Module"])
save("var-sensor-detail-iso.png")
vtop(); save("var-sensor-detail-top.png", iso=False, fit=False)
show_all(); save("var-22-display-detail.png")
PYEOF
            ;;

        18) # Animation — handled separately
            INCLUDE_ANIM=true
            ;;

        19) # Custom combo
            cat >> "$script" << PYEOF
show([$(echo $show_list | tr ' ' '\n' | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//')])
save("custom-combo-iso.png")
vtop(); save("custom-combo-top.png", iso=False, fit=False)
vfront(); save("custom-combo-front.png", iso=False, fit=False)
vbottom(); save("custom-combo-bottom.png", iso=False, fit=False)
vleft(); save("custom-combo-left.png", iso=False, fit=False)
vright(); save("custom-combo-right.png", iso=False, fit=False)
PYEOF
            ;;
    esac

    # Close doc
    echo '' >> "$script"
    echo 'print("Done.")' >> "$script"
    echo 'App.closeDocument(doc.Name)' >> "$script"

    echo "$script"
}

# =====================================================================
# SCREEN 6 — Execute
# =====================================================================
run_render() {
    local script="$1"

    echo ""
    echo -e "  ${B}Rendering...${X}"
    hr

    # FreeCAD GUI must open to render (saveImage needs the 3D viewport)
    freecad "$script" 2>&1 | grep -E "wrote|Done|Error" || true

    echo -e "  ${G}Renders complete${X}"

    # Animation if requested
    if [ "$INCLUDE_ANIM" = true ]; then
        echo ""
        echo -e "  ${B}Generating animation frames...${X}"
        export DILDER_FCSTD="$FCSTD_FILE"
        freecad "$ANIM_MACRO" 2>&1 | tail -5 || true
        if command -v ffmpeg &>/dev/null; then
            ffmpeg -y -framerate 12 \
                -i "$ANIM_DIR/frame-%04d.png" \
                -vf "scale=960:720:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
                -loop 0 \
                "$RENDER_DIR/assembly-animation.gif" 2>/dev/null
            echo -e "  ${G}Animation saved${X}: $RENDER_DIR/assembly-animation.gif"
        fi
    fi

    # Copy to website
    echo ""
    echo -e "  ${B}Copying to website...${X}"
    mkdir -p "$WEBSITE_IMG"
    cp "$RENDER_DIR"/var-*.png "$WEBSITE_IMG/" 2>/dev/null || true
    cp "$RENDER_DIR"/comp-*.png "$WEBSITE_IMG/" 2>/dev/null || true
    cp "$RENDER_DIR"/custom-*.png "$WEBSITE_IMG/" 2>/dev/null || true
    [ -f "$RENDER_DIR/assembly-animation.gif" ] && cp "$RENDER_DIR/assembly-animation.gif" "$WEBSITE_IMG/" || true

    echo -e "  ${G}Done${X}"
}

# =====================================================================
# MAIN FLOW
# =====================================================================

# Rebuild first if requested
if [ "$REBUILD" = true ]; then
    header
    echo -e "  ${B}Rebuilding model from macro...${X}"
    freecad "$MODEL_MACRO" 2>&1 | tail -10
    echo -e "  ${G}Done${X}"
    FCSTD_FILE="$MACRO_DIR/Dilder_Rev2_Mk2.FCStd"
else
    pick_file
fi

# Render set names for summary
declare -A SET_NAMES=(
    [1]="Everything (40+ images)"
    [2]="Assembly only (10 images)"
    [3]="Exploded views (3 images)"
    [4]="Component portraits (14 images)"
    [5]="Base plate (6 images)"
    [6]="AAA cradle (4 images)"
    [7]="Top cover (5 images)"
    [8]="Thumbpiece (1 image)"
    [9]="Joystick PCB (1 image)"
    [10]="Pico 2 W (1 image)"
    [11]="Piezo speaker (1 image)"
    [12]="IMU accelerometer (1 image)"
    [13]="TP4056 charger (1 image)"
    [14]="Batteries + clips (1 image)"
    [15]="E-ink display (1 image)"
    [16]="Solar panel (2 images)"
    [17]="Detail close-ups (5 images)"
    [18]="Animation frames"
    [19]="Custom combo (6 images)"
)

pick_render_set

# Custom combo needs component picker
if [ "$RENDER_SET" = "19" ]; then
    pick_components
fi

pick_style

RENDER_SET_NAME="${SET_NAMES[$RENDER_SET]:-Unknown}"
confirm

mkdir -p "$RENDER_DIR" "$ANIM_DIR"
SCRIPT=$(generate_render_script)
run_render "$SCRIPT"

# Final summary
echo ""
echo -e "${B}${C}═══════════════════════════════════════════════════════════${X}"
echo -e "  ${G}All done.${X}"
echo -e "  Renders:  ${W}$RENDER_DIR${X}"
echo -e "  Website:  ${W}$WEBSITE_IMG${X}"
echo -e "${B}${C}═══════════════════════════════════════════════════════════${X}"
echo ""
