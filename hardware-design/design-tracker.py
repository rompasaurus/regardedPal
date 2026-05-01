#!/usr/bin/env python3
"""
Dilder Design Tracker — version history, print log, and before/after
tracking for FreeCAD hardware iterations.

Usage:
  python3 design-tracker.py                  # interactive menu
  python3 design-tracker.py log              # show full timeline
  python3 design-tracker.py snap "message"   # quick snapshot of current state
  python3 design-tracker.py prints           # show print history
  python3 design-tracker.py diff 3 7         # compare two snapshots
"""

import json
import os
import re
import sys
import hashlib
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
FREECAD_DIR = SCRIPT_DIR / "freecad-mk2"
RENDERS_DIR = SCRIPT_DIR / "renders"
TRACKER_DIR = SCRIPT_DIR / ".design-tracker"
TRACKER_FILE = TRACKER_DIR / "history.json"
SNAPSHOTS_DIR = TRACKER_DIR / "snapshots"

# ── Colors ──
B = "\033[1m"
D = "\033[2m"
C = "\033[36m"
G = "\033[32m"
Y = "\033[33m"
R = "\033[31m"
M = "\033[35m"
W = "\033[97m"
X = "\033[0m"


def ensure_dirs():
    TRACKER_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)


def load_history():
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text())
    return {"snapshots": [], "prints": []}


def save_history(data):
    ensure_dirs()
    TRACKER_FILE.write_text(json.dumps(data, indent=2, default=str))


def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


def scan_fcstd():
    """Scan all FCStd files, return sorted by mtime (newest first)."""
    files = []
    for f in FREECAD_DIR.glob("*.FCStd"):
        stat = f.stat()
        files.append({
            "name": f.name,
            "path": str(f),
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "hash": file_hash(f),
        })
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


def scan_3mf():
    """Scan all 3MF files."""
    files = []
    for f in FREECAD_DIR.glob("*.3mf"):
        stat = f.stat()
        files.append({
            "name": f.name,
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    for f in (SCRIPT_DIR / "prints").glob("*.3mf"):
        stat = f.stat()
        files.append({
            "name": f.name,
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        })
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


def scan_renders():
    """Scan current render files."""
    files = []
    for f in RENDERS_DIR.glob("*.png"):
        files.append(f.name)
    return sorted(files)


def get_git_hash():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, cwd=SCRIPT_DIR
        )
        return result.stdout.strip().split()[0] if result.stdout.strip() else "unknown"
    except Exception:
        return "unknown"


def get_git_diff_stat():
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD", "--", "*.FCStd", "*.FCMacro"],
            capture_output=True, text=True, cwd=SCRIPT_DIR
        )
        return result.stdout.strip() if result.stdout.strip() else "clean"
    except Exception:
        return "unknown"


# =====================================================================
# COMMANDS
# =====================================================================

def cmd_snapshot(message=None):
    """Take a snapshot of the current design state."""
    ensure_dirs()
    history = load_history()

    snap_id = len(history["snapshots"]) + 1
    timestamp = datetime.now().isoformat()
    git_hash = get_git_hash()
    fcstd_files = scan_fcstd()
    mf_files = scan_3mf()
    renders = scan_renders()

    if not message:
        print(f"\n  {B}{W}Take Design Snapshot #{snap_id}{X}")
        print(f"  {D}Git: {git_hash}{X}")
        print(f"  {D}FCStd files: {len(fcstd_files)}, 3MF files: {len(mf_files)}, Renders: {len(renders)}{X}")
        message = input(f"\n  {B}{C}Description:{X} ")
        if not message.strip():
            message = f"Snapshot #{snap_id}"

    # Copy the newest FCStd as a reference
    snap_dir = SNAPSHOTS_DIR / f"snap-{snap_id:04d}"
    snap_dir.mkdir(exist_ok=True)

    newest_fcstd = fcstd_files[0] if fcstd_files else None
    if newest_fcstd:
        src = Path(newest_fcstd["path"])
        dst = snap_dir / src.name
        shutil.copy2(src, dst)

    # Copy current renders list (not the files — just names for reference)
    snapshot = {
        "id": snap_id,
        "timestamp": timestamp,
        "git_hash": git_hash,
        "message": message,
        "fcstd_count": len(fcstd_files),
        "fcstd_newest": newest_fcstd["name"] if newest_fcstd else None,
        "fcstd_newest_hash": newest_fcstd["hash"] if newest_fcstd else None,
        "mf_count": len(mf_files),
        "render_count": len(renders),
        "renders": renders[:10],  # first 10 for reference
        "macro_hash": file_hash(FREECAD_DIR / "dilder_rev2_mk2.FCMacro")
            if (FREECAD_DIR / "dilder_rev2_mk2.FCMacro").exists() else None,
    }

    history["snapshots"].append(snapshot)
    save_history(history)

    print(f"\n  {G}Snapshot #{snap_id} saved{X}")
    print(f"  {D}FCStd: {snapshot['fcstd_newest']}{X}")
    print(f"  {D}Backed up to: {snap_dir}{X}")


def cmd_log():
    """Show the full design timeline."""
    history = load_history()
    snaps = history.get("snapshots", [])
    prints = history.get("prints", [])

    # Merge into a timeline
    events = []
    for s in snaps:
        events.append(("snap", s["timestamp"], s))
    for p in prints:
        events.append(("print", p["timestamp"], p))
    events.sort(key=lambda x: x[1], reverse=True)

    print(f"\n  {B}{C}Design Timeline{X}")
    print(f"  {D}{len(snaps)} snapshots, {len(prints)} prints{X}")
    print(f"  {C}{'─' * 56}{X}")

    if not events:
        print(f"\n  {D}No history yet. Run: python3 design-tracker.py snap{X}")
        return

    for kind, ts, data in events:
        date = ts[:16].replace("T", " ")
        if kind == "snap":
            sid = data["id"]
            msg = data["message"]
            git = data.get("git_hash", "")[:7]
            fcstd = data.get("fcstd_newest", "")
            short_name = fcstd[:50] + "..." if len(fcstd) > 50 else fcstd
            print(f"\n  {G}#{sid:04d}{X}  {B}{date}{X}  {D}({git}){X}")
            print(f"        {W}{msg}{X}")
            print(f"        {D}FCStd: {short_name}{X}")
            print(f"        {D}{data['fcstd_count']} models, {data['mf_count']} exports, {data['render_count']} renders{X}")
        elif kind == "print":
            pid = data["id"]
            msg = data["message"]
            files = ", ".join(data.get("files", [])[:3])
            result = data.get("result", "unknown")
            color = G if result == "success" else Y if result == "partial" else R
            print(f"\n  {M}P{pid:04d}{X}  {B}{date}{X}")
            print(f"        {W}{msg}{X}")
            print(f"        {D}Files: {files}{X}")
            print(f"        Result: {color}{result}{X}")


def cmd_print_log():
    """Log a 3D print."""
    history = load_history()
    prints = history.get("prints", [])
    pid = len(prints) + 1

    print(f"\n  {B}{M}Log Print #{pid}{X}")

    # Show recent 3MF files
    mf_files = scan_3mf()
    if mf_files:
        print(f"\n  {D}Recent 3MF exports:{X}")
        for i, f in enumerate(mf_files[:8]):
            date = f["mtime"][:16].replace("T", " ")
            print(f"  {W}{i+1}){X} {f['name'][:60]}")
            print(f"     {D}{date}{X}")

    message = input(f"\n  {B}{C}What did you print?{X} ")
    files_str = input(f"  {B}{C}Which files? (names or numbers):{X} ")
    result = input(f"  {B}{C}Result (success/partial/failed):{X} ") or "success"
    notes = input(f"  {B}{C}Notes (optional):{X} ")

    # Parse file references
    printed_files = []
    for part in files_str.split(","):
        part = part.strip()
        if part.isdigit() and int(part) <= len(mf_files):
            printed_files.append(mf_files[int(part) - 1]["name"])
        elif part:
            printed_files.append(part)

    entry = {
        "id": pid,
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "files": printed_files,
        "result": result,
        "notes": notes,
        "git_hash": get_git_hash(),
    }

    prints.append(entry)
    history["prints"] = prints
    save_history(history)
    print(f"\n  {G}Print #{pid} logged{X}")


def cmd_diff(id1, id2):
    """Compare two snapshots."""
    history = load_history()
    snaps = {s["id"]: s for s in history.get("snapshots", [])}

    if id1 not in snaps or id2 not in snaps:
        print(f"  {R}Snapshot #{id1} or #{id2} not found{X}")
        return

    s1, s2 = snaps[id1], snaps[id2]

    print(f"\n  {B}{C}Comparing Snapshot #{id1} vs #{id2}{X}")
    print(f"  {C}{'─' * 56}{X}")

    print(f"\n  {B}#{id1}{X} ({s1['timestamp'][:16]}): {s1['message']}")
    print(f"  {B}#{id2}{X} ({s2['timestamp'][:16]}): {s2['message']}")

    # Compare counts
    for label, k in [("FCStd files", "fcstd_count"), ("3MF exports", "mf_count"), ("Renders", "render_count")]:
        v1, v2 = s1.get(k, 0), s2.get(k, 0)
        delta = v2 - v1
        color = G if delta > 0 else R if delta < 0 else D
        sign = "+" if delta > 0 else ""
        print(f"  {label}: {v1} -> {v2}  {color}({sign}{delta}){X}")

    # Compare file hashes
    if s1.get("fcstd_newest_hash") != s2.get("fcstd_newest_hash"):
        print(f"\n  {Y}FCStd changed:{X}")
        print(f"    #{id1}: {s1.get('fcstd_newest', '?')}")
        print(f"    #{id2}: {s2.get('fcstd_newest', '?')}")
    else:
        print(f"\n  {D}FCStd unchanged{X}")

    if s1.get("macro_hash") != s2.get("macro_hash"):
        print(f"  {Y}Macro changed{X}")
    else:
        print(f"  {D}Macro unchanged{X}")

    # Compare render lists
    r1 = set(s1.get("renders", []))
    r2 = set(s2.get("renders", []))
    added = r2 - r1
    removed = r1 - r2
    if added:
        print(f"\n  {G}New renders:{X}")
        for r in sorted(added):
            print(f"    + {r}")
    if removed:
        print(f"\n  {R}Removed renders:{X}")
        for r in sorted(removed):
            print(f"    - {r}")


def cmd_status():
    """Show current design state."""
    fcstd = scan_fcstd()
    mf = scan_3mf()
    renders = scan_renders()
    git_hash = get_git_hash()
    git_diff = get_git_diff_stat()
    history = load_history()

    print(f"\n  {B}{C}Design Status{X}")
    print(f"  {C}{'─' * 56}{X}")
    print(f"  {B}Git:{X}       {git_hash}")
    print(f"  {B}FCStd:{X}     {len(fcstd)} files")
    print(f"  {B}3MF:{X}       {len(mf)} exports")
    print(f"  {B}Renders:{X}   {len(renders)} PNGs")
    print(f"  {B}Snapshots:{X} {len(history.get('snapshots', []))}")
    print(f"  {B}Prints:{X}    {len(history.get('prints', []))}")

    if fcstd:
        newest = fcstd[0]
        date = newest["mtime"][:16].replace("T", " ")
        size_mb = newest["size"] / 1024 / 1024
        print(f"\n  {B}Newest model:{X}")
        print(f"  {G}{newest['name']}{X}")
        print(f"  {D}{date}  |  {size_mb:.1f} MB  |  hash: {newest['hash']}{X}")

    if git_diff != "clean":
        print(f"\n  {Y}Uncommitted design changes:{X}")
        print(f"  {D}{git_diff}{X}")


def cmd_naming():
    """Show the recommended naming convention."""
    print(f"""
  {B}{C}Recommended CAD File Naming Convention{X}
  {C}{'─' * 56}{X}

  {B}Pattern:{X}
  Dilder_Rev2_Mk2-<changes>-<DD-MM-YYYY-HHMM>.FCStd

  {B}Examples:{X}
  {G}Dilder_Rev2_Mk2-joystick-anchor-piezo-30-04-2026-1617.FCStd{X}
  {G}Dilder_Rev2_Mk2-widened-inlay-01-05-2026-0930.FCStd{X}

  {B}Rules:{X}
  1. Always start with {W}Dilder_Rev2_Mk2-{X}
  2. List the {W}key changes{X} separated by hyphens
  3. End with the {W}date and time{X} (DD-MM-YYYY-HHMM)
  4. Keep change descriptions {W}short{X} (2-4 words)
  5. Use {W}lowercase{X} with hyphens (no spaces)
  6. Take a {W}snapshot{X} after each significant change

  {B}Before printing:{X}
  1. Take a snapshot: {W}python3 design-tracker.py snap{X}
  2. Export 3MF files
  3. Log the print: {W}python3 design-tracker.py print{X}

  {B}After a session:{X}
  1. Take a final snapshot with a summary message
  2. Commit to git
  3. Renders auto-copy to website via build_and_render.sh
""")


# =====================================================================
# INTERACTIVE MENU
# =====================================================================

def menu():
    while True:
        print(f"\n  {B}{C}╔═══════════════════════════════════════╗{X}")
        print(f"  {B}{C}║     Dilder Design Tracker v0.1        ║{X}")
        print(f"  {B}{C}╚═══════════════════════════════════════╝{X}")
        print(f"""
  {W}1){X}  Status          {D}— current design state{X}
  {W}2){X}  Take snapshot    {D}— save current state with a message{X}
  {W}3){X}  Timeline         {D}— full design history{X}
  {W}4){X}  Log a print      {D}— record what you printed{X}
  {W}5){X}  Compare          {D}— diff two snapshots{X}
  {W}6){X}  Naming guide     {D}— recommended file naming convention{X}
  {W}q){X}  Quit
""")
        choice = input(f"  {B}{C}Choice [1-6/q]:{X} ").strip()

        if choice == "1":
            cmd_status()
        elif choice == "2":
            cmd_snapshot()
        elif choice == "3":
            cmd_log()
        elif choice == "4":
            cmd_print_log()
        elif choice == "5":
            id1 = input(f"  {C}First snapshot #:{X} ").strip()
            id2 = input(f"  {C}Second snapshot #:{X} ").strip()
            try:
                cmd_diff(int(id1), int(id2))
            except ValueError:
                print(f"  {R}Enter valid snapshot numbers{X}")
        elif choice == "6":
            cmd_naming()
        elif choice in ("q", "Q"):
            break


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    ensure_dirs()

    if len(sys.argv) < 2:
        menu()
    elif sys.argv[1] == "log":
        cmd_log()
    elif sys.argv[1] == "snap":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        cmd_snapshot(msg)
    elif sys.argv[1] == "prints":
        cmd_log()  # shows prints in timeline
    elif sys.argv[1] == "status":
        cmd_status()
    elif sys.argv[1] == "diff" and len(sys.argv) >= 4:
        cmd_diff(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "naming":
        cmd_naming()
    else:
        print(__doc__)
