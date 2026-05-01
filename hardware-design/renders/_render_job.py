"""Auto-generated render job — 2026-05-01 08:14"""
import os, time
import FreeCAD as App
import FreeCADGui as Gui

doc = App.openDocument("/home/rompasaurus/COdingProjects/Dilder/hardware-design/freecad-mk2/Dilder_Rev2_Mk2-proper-joystick-solar-pcbclamp-speeker-inlay-accelerameter inlay-widenenedinlayby.2mmforv3board 30-04-2026-1734.FCStd")
Gui.ActiveDocument = Gui.getDocument(doc.Name)
view = Gui.ActiveDocument.activeView()

RENDER_DIR = "/home/rompasaurus/COdingProjects/Dilder/hardware-design/renders"
W, H = 1920, 1440
BG = "#E8E8E8"

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

set_trans(40)
os.makedirs(RENDER_DIR, exist_ok=True)
print("Rendering...")

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
set_trans(40)
show_all(); save("var-19-joystick-detail.png")
vtop(); save("var-20-joystick-aligned-top.png", iso=False, fit=False)
show_all(); set_trans(85); save("var-21-thumbpiece-hero.png")

# ── Exploded ──
show_all()
set_trans(40)
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
set_trans(40)
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

print("Done.")
App.closeDocument(doc.Name)
