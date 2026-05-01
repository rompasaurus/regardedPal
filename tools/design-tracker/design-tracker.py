#!/usr/bin/env python3
"""
Dilder Design Tracker v2.0 — GUI for version history, print log, render
gallery, and print-package management for FreeCAD hardware iterations.

Usage:
  python3 design-tracker.py                  # launch GUI
  python3 design-tracker.py --cli            # legacy interactive menu
  python3 design-tracker.py snap "message"   # quick snapshot (CLI)
  python3 design-tracker.py log              # show timeline  (CLI)
  python3 design-tracker.py status           # current state  (CLI)
"""

import json
import os
import re
import sys
import hashlib
import shutil
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
HARDWARE_DIR = PROJECT_ROOT / "hardware-design"
FREECAD_DIR = HARDWARE_DIR / "freecad-mk2"
RENDERS_DIR = HARDWARE_DIR / "renders"
TRACKER_DIR = SCRIPT_DIR / ".design-tracker"
TRACKER_FILE = TRACKER_DIR / "history.json"
SNAPSHOTS_DIR = TRACKER_DIR / "snapshots"
PACKAGES_DIR = TRACKER_DIR / "packages"

APP_NAME = "Dilder Design Tracker"
APP_VERSION = "2.0"

# ─────────────────────────────────────────────────────────────────────────────
# Theme (Catppuccin Mocha — matches DesignTool)
# ─────────────────────────────────────────────────────────────────────────────

BG_DARK = "#1e1e2e"
BG_PANEL = "#282840"
BG_CANVAS = "#2a2a3a"
BG_INPUT = "#313244"
BG_HOVER = "#45475a"
FG_TEXT = "#cdd6f4"
FG_DIM = "#6c7086"
FG_ACCENT = "#89b4fa"
FG_MAGENTA = "#cba6f7"
FG_YELLOW = "#f9e2af"
FG_GREEN = "#a6e3a1"
FG_RED = "#f38ba8"
FG_PEACH = "#fab387"

# ─────────────────────────────────────────────────────────────────────────────
# Data layer
# ─────────────────────────────────────────────────────────────────────────────

def ensure_dirs():
    TRACKER_DIR.mkdir(exist_ok=True)
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    PACKAGES_DIR.mkdir(exist_ok=True)


def load_history():
    if TRACKER_FILE.exists():
        return json.loads(TRACKER_FILE.read_text())
    return {"snapshots": [], "prints": [], "packages": []}


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
    files = []
    for d in [FREECAD_DIR, PACKAGES_DIR]:
        for f in d.glob("**/*.3mf"):
            stat = f.stat()
            files.append({
                "name": f.name,
                "path": str(f),
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


def scan_renders():
    files = []
    if RENDERS_DIR.exists():
        for f in RENDERS_DIR.glob("*.png"):
            stat = f.stat()
            files.append({
                "name": f.name,
                "path": str(f),
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


def get_git_hash():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        return result.stdout.strip().split()[0] if result.stdout.strip() else "unknown"
    except Exception:
        return "unknown"


def get_git_diff_stat():
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD", "--", "*.FCStd", "*.FCMacro"],
            capture_output=True, text=True, cwd=PROJECT_ROOT
        )
        return result.stdout.strip() if result.stdout.strip() else "clean"
    except Exception:
        return "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# Core actions (used by both CLI and GUI)
# ─────────────────────────────────────────────────────────────────────────────

def take_snapshot(message):
    ensure_dirs()
    history = load_history()
    snap_id = len(history["snapshots"]) + 1
    timestamp = datetime.now().isoformat()
    git_hash = get_git_hash()
    fcstd_files = scan_fcstd()
    mf_files = scan_3mf()
    renders = scan_renders()

    snap_dir = SNAPSHOTS_DIR / f"snap-{snap_id:04d}"
    snap_dir.mkdir(exist_ok=True)

    newest_fcstd = fcstd_files[0] if fcstd_files else None
    if newest_fcstd:
        src = Path(newest_fcstd["path"])
        shutil.copy2(src, snap_dir / src.name)

    macro_path = FREECAD_DIR / "dilder_rev2_mk2.FCMacro"
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
        "renders": [r["name"] for r in renders[:10]],
        "macro_hash": file_hash(macro_path) if macro_path.exists() else None,
    }

    history["snapshots"].append(snapshot)
    save_history(history)
    return snapshot


def log_print_entry(message, files, result, notes, snapshot_id=None,
                    camera_photos=None):
    history = load_history()
    prints = history.get("prints", [])
    pid = len(prints) + 1

    entry = {
        "id": pid,
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "files": files,
        "result": result,
        "notes": notes,
        "git_hash": get_git_hash(),
        "snapshot_id": snapshot_id,
        "camera_photos": camera_photos or [],
    }
    prints.append(entry)
    history["prints"] = prints
    save_history(history)
    return entry


def create_package(name, fcstd_path=None, mf_paths=None, render_paths=None,
                   camera_paths=None, changelog_text="", snapshot_id=None,
                   print_id=None):
    """Bundle files into a tracked package folder."""
    ensure_dirs()
    history = load_history()
    packages = history.get("packages", [])
    pkg_id = len(packages) + 1
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    slug = re.sub(r"[^\w\-]+", "_", name).strip("_")[:60]
    folder_name = f"pkg-{pkg_id:04d}_{ts}_{slug}"
    pkg_dir = PACKAGES_DIR / folder_name
    pkg_dir.mkdir(parents=True, exist_ok=True)

    copied = []

    # Copy FCStd
    if fcstd_path and Path(fcstd_path).exists():
        dst = pkg_dir / Path(fcstd_path).name
        shutil.copy2(fcstd_path, dst)
        copied.append(dst.name)

    # Copy 3MF files
    for p in (mf_paths or []):
        if Path(p).exists():
            dst = pkg_dir / Path(p).name
            shutil.copy2(p, dst)
            copied.append(dst.name)

    # Copy renders
    renders_sub = pkg_dir / "renders"
    for p in (render_paths or []):
        if Path(p).exists():
            renders_sub.mkdir(exist_ok=True)
            dst = renders_sub / Path(p).name
            shutil.copy2(p, dst)
            copied.append(f"renders/{dst.name}")

    # Copy camera photos
    photos_sub = pkg_dir / "photos"
    for p in (camera_paths or []):
        if Path(p).exists():
            photos_sub.mkdir(exist_ok=True)
            dst = photos_sub / Path(p).name
            shutil.copy2(p, dst)
            copied.append(f"photos/{dst.name}")

    # Write changelog
    changelog_path = pkg_dir / "CHANGES.md"
    header = f"# {name}\n\n"
    header += f"**Date:** {ts}  \n"
    header += f"**Package:** {folder_name}  \n"
    if snapshot_id:
        header += f"**Snapshot:** #{snapshot_id}  \n"
    if print_id:
        header += f"**Print:** #{print_id}  \n"
    header += f"**Git:** {get_git_hash()}  \n\n"
    header += "## Changes\n\n"
    header += changelog_text if changelog_text else "_No changes noted._\n"
    header += "\n\n## Files\n\n"
    for c in copied:
        header += f"- `{c}`\n"
    changelog_path.write_text(header)

    entry = {
        "id": pkg_id,
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "folder": folder_name,
        "files": copied,
        "snapshot_id": snapshot_id,
        "print_id": print_id,
        "git_hash": get_git_hash(),
    }
    packages.append(entry)
    history["packages"] = packages
    save_history(history)
    return entry, pkg_dir


# ═══════════════════════════════════════════════════════════════════════════════
# GUI
# ═══════════════════════════════════════════════════════════════════════════════

class DesignTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1280x820")
        self.configure(bg=BG_DARK)
        self.minsize(960, 640)
        self._image_cache = {}

        self._apply_theme()
        self._build_ui()
        self._refresh_all()

    # ── Theme ─────────────────────────────────────────────────────────────

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background=BG_DARK, foreground=FG_TEXT,
                         fieldbackground=BG_INPUT, borderwidth=0,
                         font=("monospace", 10))
        style.configure("TFrame", background=BG_DARK)
        style.configure("TLabel", background=BG_DARK, foreground=FG_TEXT)
        style.configure("TButton", background=BG_PANEL, foreground=FG_TEXT,
                         padding=(10, 5))
        style.map("TButton",
                  background=[("active", BG_HOVER)],
                  foreground=[("active", FG_ACCENT)])
        style.configure("Accent.TButton", background=FG_ACCENT,
                         foreground=BG_DARK, font=("monospace", 10, "bold"))
        style.map("Accent.TButton",
                  background=[("active", FG_MAGENTA)])
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL,
                         foreground=FG_DIM, padding=(14, 6),
                         font=("monospace", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_DARK)],
                  foreground=[("selected", FG_ACCENT)])
        style.configure("Treeview", background=BG_CANVAS,
                         foreground=FG_TEXT, fieldbackground=BG_CANVAS,
                         rowheight=24, font=("monospace", 9))
        style.configure("Treeview.Heading", background=BG_PANEL,
                         foreground=FG_ACCENT, font=("monospace", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", BG_HOVER)],
                  foreground=[("selected", FG_ACCENT)])
        style.configure("TLabelframe", background=BG_DARK,
                         foreground=FG_ACCENT)
        style.configure("TLabelframe.Label", background=BG_DARK,
                         foreground=FG_ACCENT, font=("monospace", 10, "bold"))
        style.configure("Dim.TLabel", foreground=FG_DIM)
        style.configure("Green.TLabel", foreground=FG_GREEN)
        style.configure("Yellow.TLabel", foreground=FG_YELLOW)
        style.configure("Red.TLabel", foreground=FG_RED)
        style.configure("Accent.TLabel", foreground=FG_ACCENT,
                         font=("monospace", 11, "bold"))
        style.configure("Title.TLabel", foreground=FG_ACCENT,
                         font=("monospace", 14, "bold"))
        style.configure("TEntry", fieldbackground=BG_INPUT,
                         foreground=FG_TEXT)
        style.configure("Vertical.TScrollbar", background=BG_PANEL,
                         troughcolor=BG_DARK, borderwidth=0)
        style.configure("TCombobox", fieldbackground=BG_INPUT,
                         foreground=FG_TEXT, selectbackground=BG_HOVER)

    # ── Main layout ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = ttk.Frame(self)
        hdr.pack(fill="x", padx=12, pady=(10, 0))
        ttk.Label(hdr, text=f"{APP_NAME}", style="Title.TLabel").pack(
            side="left")
        ttk.Label(hdr, text=f"v{APP_VERSION}", style="Dim.TLabel").pack(
            side="left", padx=(8, 0))

        # Status bar at bottom
        self._status_var = tk.StringVar(value="Ready")
        sbar = ttk.Label(self, textvariable=self._status_var,
                         style="Dim.TLabel")
        sbar.pack(side="bottom", fill="x", padx=12, pady=4)

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=6)

        self._build_dashboard_tab()
        self._build_models_tab()
        self._build_prints_tab()
        self._build_renders_tab()
        self._build_packages_tab()
        self._build_guide_tab()

    # ── 1. Dashboard ──────────────────────────────────────────────────────

    def _build_dashboard_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text=" Dashboard ")

        # Top row: stats
        stats_frame = ttk.LabelFrame(tab, text="Current State")
        stats_frame.pack(fill="x", padx=10, pady=(10, 5))

        self._dash_labels = {}
        cols = [("Git Hash", "git"), ("FCStd Files", "fcstd"),
                ("3MF Exports", "mf"), ("Renders", "renders"),
                ("Snapshots", "snaps"), ("Prints", "prints")]
        for i, (label, key) in enumerate(cols):
            f = ttk.Frame(stats_frame)
            f.pack(side="left", expand=True, padx=12, pady=8)
            ttk.Label(f, text=label, style="Dim.TLabel").pack()
            lbl = ttk.Label(f, text="--", style="Accent.TLabel")
            lbl.pack()
            self._dash_labels[key] = lbl

        # Middle: timeline
        tl_frame = ttk.LabelFrame(tab, text="Timeline")
        tl_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self._timeline_tree = ttk.Treeview(
            tl_frame,
            columns=("type", "date", "message", "details"),
            show="headings", selectmode="browse")
        self._timeline_tree.heading("type", text="Type")
        self._timeline_tree.heading("date", text="Date")
        self._timeline_tree.heading("message", text="Message")
        self._timeline_tree.heading("details", text="Details")
        self._timeline_tree.column("type", width=70, minwidth=60)
        self._timeline_tree.column("date", width=140, minwidth=120)
        self._timeline_tree.column("message", width=400, minwidth=200)
        self._timeline_tree.column("details", width=300, minwidth=150)

        sb = ttk.Scrollbar(tl_frame, orient="vertical",
                           command=self._timeline_tree.yview)
        self._timeline_tree.configure(yscrollcommand=sb.set)
        self._timeline_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Bottom: action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btn_frame, text="Take Snapshot",
                   style="Accent.TButton",
                   command=self._action_snapshot).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Refresh",
                   command=self._refresh_all).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Compare Snapshots",
                   command=self._action_compare).pack(side="left", padx=4)

    # ── 2. Models & Exports ───────────────────────────────────────────────

    def _build_models_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text=" Models & Exports ")

        pw = ttk.PanedWindow(tab, orient="horizontal")
        pw.pack(fill="both", expand=True, padx=10, pady=10)

        # Left: FCStd table
        left = ttk.LabelFrame(pw, text="FreeCAD Models (.FCStd)")
        pw.add(left, weight=1)

        self._fcstd_tree = ttk.Treeview(
            left, columns=("name", "date", "size", "hash"),
            show="headings", selectmode="browse")
        self._fcstd_tree.heading("name", text="File Name")
        self._fcstd_tree.heading("date", text="Modified")
        self._fcstd_tree.heading("size", text="Size")
        self._fcstd_tree.heading("hash", text="Hash")
        self._fcstd_tree.column("name", width=300, minwidth=200)
        self._fcstd_tree.column("date", width=130, minwidth=100)
        self._fcstd_tree.column("size", width=70, minwidth=60)
        self._fcstd_tree.column("hash", width=100, minwidth=80)
        sb = ttk.Scrollbar(left, orient="vertical",
                           command=self._fcstd_tree.yview)
        self._fcstd_tree.configure(yscrollcommand=sb.set)
        self._fcstd_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Right: 3MF table
        right = ttk.LabelFrame(pw, text="3MF Exports")
        pw.add(right, weight=1)

        self._mf_tree = ttk.Treeview(
            right, columns=("name", "date", "size"),
            show="headings", selectmode="extended")
        self._mf_tree.heading("name", text="File Name")
        self._mf_tree.heading("date", text="Modified")
        self._mf_tree.heading("size", text="Size")
        self._mf_tree.column("name", width=350, minwidth=200)
        self._mf_tree.column("date", width=130, minwidth=100)
        self._mf_tree.column("size", width=70, minwidth=60)
        sb2 = ttk.Scrollbar(right, orient="vertical",
                            command=self._mf_tree.yview)
        self._mf_tree.configure(yscrollcommand=sb2.set)
        self._mf_tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="right", fill="y")

    # ── 3. Prints ─────────────────────────────────────────────────────────

    def _build_prints_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text=" Prints ")

        top = ttk.Frame(tab)
        top.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Button(top, text="Log New Print", style="Accent.TButton",
                   command=self._action_log_print).pack(side="left", padx=4)
        ttk.Button(top, text="Attach Photo to Print",
                   command=self._action_attach_photo).pack(side="left", padx=4)

        self._prints_tree = ttk.Treeview(
            tab,
            columns=("id", "date", "message", "files", "result", "photos"),
            show="headings", selectmode="browse")
        self._prints_tree.heading("id", text="#")
        self._prints_tree.heading("date", text="Date")
        self._prints_tree.heading("message", text="Description")
        self._prints_tree.heading("files", text="Files")
        self._prints_tree.heading("result", text="Result")
        self._prints_tree.heading("photos", text="Photos")
        self._prints_tree.column("id", width=40, minwidth=35)
        self._prints_tree.column("date", width=130, minwidth=100)
        self._prints_tree.column("message", width=300, minwidth=200)
        self._prints_tree.column("files", width=250, minwidth=150)
        self._prints_tree.column("result", width=80, minwidth=60)
        self._prints_tree.column("photos", width=60, minwidth=50)
        sb = ttk.Scrollbar(tab, orient="vertical",
                           command=self._prints_tree.yview)
        self._prints_tree.configure(yscrollcommand=sb.set)
        self._prints_tree.pack(fill="both", expand=True, padx=10, pady=5)
        sb.pack(side="right", fill="y")

        # Detail panel
        det = ttk.LabelFrame(tab, text="Print Details")
        det.pack(fill="x", padx=10, pady=(0, 10))
        self._print_detail = tk.Text(det, height=5, bg=BG_CANVAS,
                                     fg=FG_TEXT, font=("monospace", 9),
                                     wrap="word", borderwidth=0)
        self._print_detail.pack(fill="x", padx=6, pady=6)
        self._prints_tree.bind("<<TreeviewSelect>>", self._on_print_select)

    # ── 4. Renders ────────────────────────────────────────────────────────

    def _build_renders_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text=" Renders ")

        top = ttk.Frame(tab)
        top.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Label(top, text="Render Gallery", style="Accent.TLabel").pack(
            side="left")
        ttk.Button(top, text="Open Renders Folder",
                   command=lambda: self._open_folder(RENDERS_DIR)).pack(
            side="right", padx=4)

        pw = ttk.PanedWindow(tab, orient="horizontal")
        pw.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: file list
        left = ttk.Frame(pw)
        pw.add(left, weight=1)
        self._render_tree = ttk.Treeview(
            left, columns=("name", "date"),
            show="headings", selectmode="browse")
        self._render_tree.heading("name", text="Render")
        self._render_tree.heading("date", text="Modified")
        self._render_tree.column("name", width=280, minwidth=200)
        self._render_tree.column("date", width=130, minwidth=100)
        sb = ttk.Scrollbar(left, orient="vertical",
                           command=self._render_tree.yview)
        self._render_tree.configure(yscrollcommand=sb.set)
        self._render_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Right: preview
        right = ttk.LabelFrame(pw, text="Preview")
        pw.add(right, weight=2)
        self._render_preview = tk.Label(right, bg=BG_CANVAS, text="",
                                        anchor="center")
        self._render_preview.pack(fill="both", expand=True, padx=4, pady=4)
        self._render_tree.bind("<<TreeviewSelect>>", self._on_render_select)

    # ── 5. Packages ───────────────────────────────────────────────────────

    def _build_packages_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text=" Packages ")

        top = ttk.Frame(tab)
        top.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Button(top, text="Create Package", style="Accent.TButton",
                   command=self._action_create_package).pack(side="left",
                                                             padx=4)
        ttk.Button(top, text="Open Packages Folder",
                   command=lambda: self._open_folder(PACKAGES_DIR)).pack(
            side="right", padx=4)

        self._pkg_tree = ttk.Treeview(
            tab,
            columns=("id", "date", "name", "files", "snap", "print"),
            show="headings", selectmode="browse")
        self._pkg_tree.heading("id", text="#")
        self._pkg_tree.heading("date", text="Date")
        self._pkg_tree.heading("name", text="Package Name")
        self._pkg_tree.heading("files", text="Files")
        self._pkg_tree.heading("snap", text="Snapshot")
        self._pkg_tree.heading("print", text="Print")
        self._pkg_tree.column("id", width=40, minwidth=35)
        self._pkg_tree.column("date", width=130, minwidth=100)
        self._pkg_tree.column("name", width=300, minwidth=200)
        self._pkg_tree.column("files", width=60, minwidth=50)
        self._pkg_tree.column("snap", width=70, minwidth=60)
        self._pkg_tree.column("print", width=70, minwidth=60)
        sb = ttk.Scrollbar(tab, orient="vertical",
                           command=self._pkg_tree.yview)
        self._pkg_tree.configure(yscrollcommand=sb.set)
        self._pkg_tree.pack(fill="both", expand=True, padx=10, pady=5)
        sb.pack(side="right", fill="y")

        # Package contents
        det = ttk.LabelFrame(tab, text="Package Contents (CHANGES.md)")
        det.pack(fill="x", padx=10, pady=(0, 10))
        self._pkg_detail = tk.Text(det, height=8, bg=BG_CANVAS,
                                   fg=FG_TEXT, font=("monospace", 9),
                                   wrap="word", borderwidth=0)
        self._pkg_detail.pack(fill="x", padx=6, pady=6)
        self._pkg_tree.bind("<<TreeviewSelect>>", self._on_pkg_select)

    # ── 6. Guide ──────────────────────────────────────────────────────────

    def _build_guide_tab(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text=" Guide ")

        canvas = tk.Canvas(tab, bg=BG_DARK, highlightthickness=0)
        sb = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)

        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        sb.pack(side="right", fill="y")

        # Mousewheel scrolling
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        def _on_linux_scroll_up(e):
            canvas.yview_scroll(-3, "units")
        def _on_linux_scroll_down(e):
            canvas.yview_scroll(3, "units")
        canvas.bind_all("<Button-4>", _on_linux_scroll_up)
        canvas.bind_all("<Button-5>", _on_linux_scroll_down)

        guide_text = GUIDE_TEXT
        sections = guide_text.split("\n## ")
        for i, section in enumerate(sections):
            if i == 0:
                # Title
                lines = section.strip().split("\n")
                ttk.Label(inner, text=lines[0].lstrip("# "),
                          style="Title.TLabel").pack(anchor="w", pady=(0, 4))
                for line in lines[1:]:
                    ttk.Label(inner, text=line,
                              style="Dim.TLabel").pack(anchor="w")
            else:
                title = section.split("\n")[0]
                body = "\n".join(section.split("\n")[1:]).strip()
                ttk.Label(inner, text=f"  {title}",
                          style="Accent.TLabel").pack(
                    anchor="w", pady=(14, 2))
                txt = tk.Text(inner, bg=BG_DARK, fg=FG_TEXT,
                              font=("monospace", 9), wrap="word",
                              borderwidth=0, height=body.count("\n") + 2)
                txt.insert("1.0", body)
                txt.configure(state="disabled")
                txt.pack(fill="x", padx=20, pady=(0, 4))

    # ── Data refresh ──────────────────────────────────────────────────────

    def _refresh_all(self):
        self._status("Refreshing...")
        history = load_history()
        fcstd = scan_fcstd()
        mf = scan_3mf()
        renders = scan_renders()

        # Dashboard stats
        self._dash_labels["git"].config(text=get_git_hash())
        self._dash_labels["fcstd"].config(text=str(len(fcstd)))
        self._dash_labels["mf"].config(text=str(len(mf)))
        self._dash_labels["renders"].config(text=str(len(renders)))
        self._dash_labels["snaps"].config(
            text=str(len(history.get("snapshots", []))))
        self._dash_labels["prints"].config(
            text=str(len(history.get("prints", []))))

        # Timeline
        self._timeline_tree.delete(*self._timeline_tree.get_children())
        events = []
        for s in history.get("snapshots", []):
            details = (f"{s['fcstd_count']} models, {s['mf_count']} exports, "
                       f"{s['render_count']} renders")
            events.append((s["timestamp"], "SNAP", s["message"], details))
        for p in history.get("prints", []):
            files = ", ".join(p.get("files", [])[:2])
            result = p.get("result", "?")
            events.append((p["timestamp"], "PRINT",
                           p["message"], f"{result} | {files}"))
        for pkg in history.get("packages", []):
            events.append((pkg["timestamp"], "PKG",
                           pkg["name"], f"{len(pkg.get('files', []))} files"))
        events.sort(key=lambda x: x[0], reverse=True)
        for ts, kind, msg, det in events:
            date = ts[:16].replace("T", " ")
            tag = kind.lower()
            self._timeline_tree.insert("", "end",
                                        values=(kind, date, msg, det),
                                        tags=(tag,))
        self._timeline_tree.tag_configure("snap", foreground=FG_GREEN)
        self._timeline_tree.tag_configure("print", foreground=FG_MAGENTA)
        self._timeline_tree.tag_configure("pkg", foreground=FG_PEACH)

        # Models table
        self._fcstd_tree.delete(*self._fcstd_tree.get_children())
        for f in fcstd:
            date = f["mtime"][:16].replace("T", " ")
            size = f"{f['size'] / 1024 / 1024:.1f} MB"
            self._fcstd_tree.insert("", "end",
                                     values=(f["name"], date, size, f["hash"]))

        # 3MF table
        self._mf_tree.delete(*self._mf_tree.get_children())
        self._mf_data = mf
        for f in mf:
            date = f["mtime"][:16].replace("T", " ")
            size = f"{f['size'] / 1024:.0f} KB"
            self._mf_tree.insert("", "end",
                                  values=(f["name"], date, size))

        # Prints table
        self._prints_tree.delete(*self._prints_tree.get_children())
        for p in history.get("prints", []):
            date = p["timestamp"][:16].replace("T", " ")
            files = ", ".join(p.get("files", [])[:2])
            n_photos = len(p.get("camera_photos", []))
            self._prints_tree.insert("", "end",
                                      values=(p["id"], date, p["message"],
                                              files, p.get("result", "?"),
                                              n_photos))

        # Renders list
        self._render_tree.delete(*self._render_tree.get_children())
        self._render_data = renders
        for r in renders:
            date = r["mtime"][:16].replace("T", " ")
            self._render_tree.insert("", "end", values=(r["name"], date))

        # Packages table
        self._pkg_tree.delete(*self._pkg_tree.get_children())
        for pkg in history.get("packages", []):
            date = pkg["timestamp"][:16].replace("T", " ")
            snap = f"#{pkg['snapshot_id']}" if pkg.get("snapshot_id") else "-"
            prt = f"#{pkg['print_id']}" if pkg.get("print_id") else "-"
            self._pkg_tree.insert("", "end",
                                   values=(pkg["id"], date, pkg["name"],
                                           len(pkg.get("files", [])),
                                           snap, prt))

        self._status("Ready")

    # ── Actions ───────────────────────────────────────────────────────────

    def _action_snapshot(self):
        dlg = tk.Toplevel(self)
        dlg.title("Take Snapshot")
        dlg.geometry("480x160")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Snapshot Description:",
                  style="Accent.TLabel").pack(padx=16, pady=(16, 4),
                                              anchor="w")
        entry = ttk.Entry(dlg, width=60)
        entry.pack(padx=16, fill="x")
        entry.focus_set()

        def do_snap():
            msg = entry.get().strip()
            if not msg:
                msg = f"Snapshot {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            snap = take_snapshot(msg)
            dlg.destroy()
            self._refresh_all()
            self._status(f"Snapshot #{snap['id']} saved")

        entry.bind("<Return>", lambda e: do_snap())
        bf = ttk.Frame(dlg)
        bf.pack(pady=12)
        ttk.Button(bf, text="Save Snapshot", style="Accent.TButton",
                   command=do_snap).pack(side="left", padx=4)
        ttk.Button(bf, text="Cancel",
                   command=dlg.destroy).pack(side="left", padx=4)

    def _action_compare(self):
        history = load_history()
        snaps = history.get("snapshots", [])
        if len(snaps) < 2:
            messagebox.showinfo("Compare", "Need at least 2 snapshots.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Compare Snapshots")
        dlg.geometry("600x500")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        top = ttk.Frame(dlg)
        top.pack(fill="x", padx=16, pady=12)

        snap_labels = [f"#{s['id']} — {s['message'][:40]}" for s in snaps]
        ttk.Label(top, text="Snapshot A:").pack(anchor="w")
        combo_a = ttk.Combobox(top, values=snap_labels, state="readonly",
                               width=50)
        combo_a.current(0)
        combo_a.pack(fill="x", pady=(0, 8))

        ttk.Label(top, text="Snapshot B:").pack(anchor="w")
        combo_b = ttk.Combobox(top, values=snap_labels, state="readonly",
                               width=50)
        combo_b.current(min(1, len(snaps) - 1))
        combo_b.pack(fill="x")

        result_text = tk.Text(dlg, bg=BG_CANVAS, fg=FG_TEXT,
                              font=("monospace", 10), wrap="word",
                              borderwidth=0)
        result_text.pack(fill="both", expand=True, padx=16, pady=8)

        def do_compare():
            idx_a = combo_a.current()
            idx_b = combo_b.current()
            s1, s2 = snaps[idx_a], snaps[idx_b]
            result_text.delete("1.0", "end")

            lines = []
            lines.append(f"Comparing #{s1['id']} vs #{s2['id']}\n")
            lines.append(f"  A: {s1['message']}")
            lines.append(f"  B: {s2['message']}\n")

            for label, k in [("FCStd files", "fcstd_count"),
                             ("3MF exports", "mf_count"),
                             ("Renders", "render_count")]:
                v1, v2 = s1.get(k, 0), s2.get(k, 0)
                delta = v2 - v1
                sign = "+" if delta > 0 else ""
                lines.append(f"  {label}: {v1} -> {v2}  ({sign}{delta})")

            if s1.get("fcstd_newest_hash") != s2.get("fcstd_newest_hash"):
                lines.append(f"\n  FCStd CHANGED:")
                lines.append(f"    A: {s1.get('fcstd_newest', '?')}")
                lines.append(f"    B: {s2.get('fcstd_newest', '?')}")
            else:
                lines.append(f"\n  FCStd unchanged")

            if s1.get("macro_hash") != s2.get("macro_hash"):
                lines.append("  Macro CHANGED")
            else:
                lines.append("  Macro unchanged")

            r1 = set(s1.get("renders", []))
            r2 = set(s2.get("renders", []))
            added = r2 - r1
            removed = r1 - r2
            if added:
                lines.append(f"\n  New renders:")
                for r in sorted(added):
                    lines.append(f"    + {r}")
            if removed:
                lines.append(f"\n  Removed renders:")
                for r in sorted(removed):
                    lines.append(f"    - {r}")

            result_text.insert("1.0", "\n".join(lines))

        bf = ttk.Frame(dlg)
        bf.pack(pady=(0, 12))
        ttk.Button(bf, text="Compare", style="Accent.TButton",
                   command=do_compare).pack(side="left", padx=4)
        ttk.Button(bf, text="Close",
                   command=dlg.destroy).pack(side="left", padx=4)

    def _action_log_print(self):
        dlg = tk.Toplevel(self)
        dlg.title("Log Print")
        dlg.geometry("600x520")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Log a 3D Print", style="Accent.TLabel").pack(
            padx=16, pady=(12, 8), anchor="w")

        form = ttk.Frame(dlg)
        form.pack(fill="x", padx=16)

        ttk.Label(form, text="Description:").grid(row=0, column=0, sticky="w",
                                                   pady=4)
        msg_entry = ttk.Entry(form, width=50)
        msg_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))
        msg_entry.focus_set()

        ttk.Label(form, text="Result:").grid(row=1, column=0, sticky="w",
                                              pady=4)
        result_var = tk.StringVar(value="success")
        result_combo = ttk.Combobox(form, textvariable=result_var,
                                    values=["success", "partial", "failed"],
                                    state="readonly", width=20)
        result_combo.grid(row=1, column=1, sticky="w", pady=4, padx=(8, 0))

        ttk.Label(form, text="Notes:").grid(row=2, column=0, sticky="nw",
                                             pady=4)
        notes_text = tk.Text(form, height=3, bg=BG_INPUT, fg=FG_TEXT,
                             font=("monospace", 9), wrap="word")
        notes_text.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 0))

        form.columnconfigure(1, weight=1)

        # 3MF file selector
        ttk.Label(dlg, text="Select printed files:",
                  style="Dim.TLabel").pack(padx=16, pady=(8, 2), anchor="w")
        mf_files = scan_3mf()
        file_frame = ttk.Frame(dlg)
        file_frame.pack(fill="both", expand=True, padx=16, pady=4)

        file_list = tk.Listbox(file_frame, selectmode="extended",
                               bg=BG_CANVAS, fg=FG_TEXT,
                               font=("monospace", 9),
                               selectbackground=BG_HOVER)
        sb = ttk.Scrollbar(file_frame, orient="vertical",
                           command=file_list.yview)
        file_list.configure(yscrollcommand=sb.set)
        file_list.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        for f in mf_files:
            file_list.insert("end", f["name"])

        # Camera photo attachment
        photo_paths = []
        photo_label = ttk.Label(dlg, text="Photos: none",
                                style="Dim.TLabel")
        photo_label.pack(padx=16, anchor="w")

        def add_photos():
            paths = filedialog.askopenfilenames(
                title="Select camera photos",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
            photo_paths.extend(paths)
            photo_label.config(text=f"Photos: {len(photo_paths)} attached")

        ttk.Button(dlg, text="Attach Camera Photos",
                   command=add_photos).pack(padx=16, pady=4, anchor="w")

        def do_log():
            msg = msg_entry.get().strip()
            if not msg:
                messagebox.showwarning("Missing", "Enter a description.")
                return
            sel = file_list.curselection()
            files = [mf_files[i]["name"] for i in sel]
            result = result_var.get()
            notes = notes_text.get("1.0", "end").strip()
            entry = log_print_entry(msg, files, result, notes,
                                    camera_photos=list(photo_paths))
            dlg.destroy()
            self._refresh_all()
            self._status(f"Print #{entry['id']} logged")

        bf = ttk.Frame(dlg)
        bf.pack(pady=(4, 12))
        ttk.Button(bf, text="Log Print", style="Accent.TButton",
                   command=do_log).pack(side="left", padx=4)
        ttk.Button(bf, text="Cancel",
                   command=dlg.destroy).pack(side="left", padx=4)

    def _action_attach_photo(self):
        """Attach a camera photo to an existing print entry."""
        history = load_history()
        prints = history.get("prints", [])
        if not prints:
            messagebox.showinfo("Attach Photo", "No prints logged yet.")
            return

        sel = self._prints_tree.selection()
        if not sel:
            messagebox.showinfo("Attach Photo",
                                "Select a print from the table first.")
            return

        vals = self._prints_tree.item(sel[0], "values")
        pid = int(vals[0])

        paths = filedialog.askopenfilenames(
            title=f"Select photos for Print #{pid}",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if not paths:
            return

        for p in prints:
            if p["id"] == pid:
                existing = p.get("camera_photos", [])
                existing.extend(paths)
                p["camera_photos"] = existing
                break
        save_history(history)
        self._refresh_all()
        self._status(f"Added {len(paths)} photo(s) to Print #{pid}")

    def _action_create_package(self):
        dlg = tk.Toplevel(self)
        dlg.title("Create Package")
        dlg.geometry("700x680")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self)
        dlg.grab_set()

        ttk.Label(dlg, text="Create Print Package",
                  style="Accent.TLabel").pack(padx=16, pady=(12, 8),
                                              anchor="w")
        ttk.Label(dlg, text="Bundle a FreeCAD model, 3MF exports, renders, "
                  "and photos into a tracked folder with a changelog.",
                  style="Dim.TLabel").pack(padx=16, anchor="w")

        form = ttk.Frame(dlg)
        form.pack(fill="x", padx=16, pady=(8, 0))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Package name:").grid(row=0, column=0,
                                                    sticky="w", pady=4)
        name_entry = ttk.Entry(form, width=50)
        name_entry.grid(row=0, column=1, sticky="ew", pady=4, padx=(8, 0))
        name_entry.focus_set()

        # Link to snapshot
        history = load_history()
        snap_labels = ["(none)"] + [
            f"#{s['id']} — {s['message'][:40]}"
            for s in history.get("snapshots", [])]
        ttk.Label(form, text="Link snapshot:").grid(row=1, column=0,
                                                     sticky="w", pady=4)
        snap_combo = ttk.Combobox(form, values=snap_labels, state="readonly",
                                  width=50)
        snap_combo.current(0)
        snap_combo.grid(row=1, column=1, sticky="ew", pady=4, padx=(8, 0))

        # Link to print
        print_labels = ["(none)"] + [
            f"#{p['id']} — {p['message'][:40]}"
            for p in history.get("prints", [])]
        ttk.Label(form, text="Link print:").grid(row=2, column=0,
                                                  sticky="w", pady=4)
        print_combo = ttk.Combobox(form, values=print_labels, state="readonly",
                                   width=50)
        print_combo.current(0)
        print_combo.grid(row=2, column=1, sticky="ew", pady=4, padx=(8, 0))

        # FCStd selector
        fcstd_files = scan_fcstd()
        fcstd_labels = ["(none)"] + [f["name"] for f in fcstd_files]
        ttk.Label(form, text="FCStd file:").grid(row=3, column=0,
                                                  sticky="w", pady=4)
        fcstd_combo = ttk.Combobox(form, values=fcstd_labels,
                                   state="readonly", width=50)
        fcstd_combo.current(0)
        fcstd_combo.grid(row=3, column=1, sticky="ew", pady=4, padx=(8, 0))

        # 3MF file selector
        ttk.Label(dlg, text="Select 3MF files to include:",
                  style="Dim.TLabel").pack(padx=16, pady=(8, 2), anchor="w")
        mf_files = scan_3mf()
        mf_frame = ttk.Frame(dlg)
        mf_frame.pack(fill="x", padx=16, pady=2)
        mf_list = tk.Listbox(mf_frame, selectmode="extended", height=5,
                             bg=BG_CANVAS, fg=FG_TEXT, font=("monospace", 9),
                             selectbackground=BG_HOVER)
        sb = ttk.Scrollbar(mf_frame, orient="vertical",
                           command=mf_list.yview)
        mf_list.configure(yscrollcommand=sb.set)
        mf_list.pack(side="left", fill="x", expand=True)
        sb.pack(side="right", fill="y")
        for f in mf_files:
            mf_list.insert("end", f["name"])

        # Render / photo file pickers
        render_paths = []
        camera_paths = []
        rlabel = ttk.Label(dlg, text="Renders: 0 selected",
                           style="Dim.TLabel")
        rlabel.pack(padx=16, anchor="w", pady=(4, 0))
        clabel = ttk.Label(dlg, text="Photos: 0 selected",
                           style="Dim.TLabel")
        clabel.pack(padx=16, anchor="w")

        pick_frame = ttk.Frame(dlg)
        pick_frame.pack(fill="x", padx=16, pady=4)

        def pick_renders():
            paths = filedialog.askopenfilenames(
                title="Select renders", initialdir=str(RENDERS_DIR),
                filetypes=[("Images", "*.png *.jpg")])
            render_paths.extend(paths)
            rlabel.config(text=f"Renders: {len(render_paths)} selected")

        def pick_photos():
            paths = filedialog.askopenfilenames(
                title="Select camera photos",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
            camera_paths.extend(paths)
            clabel.config(text=f"Photos: {len(camera_paths)} selected")

        ttk.Button(pick_frame, text="Add Renders",
                   command=pick_renders).pack(side="left", padx=4)
        ttk.Button(pick_frame, text="Add Camera Photos",
                   command=pick_photos).pack(side="left", padx=4)

        # Changelog
        ttk.Label(dlg, text="Changelog (what changed in this iteration):",
                  style="Dim.TLabel").pack(padx=16, pady=(8, 2), anchor="w")
        changelog = tk.Text(dlg, height=5, bg=BG_INPUT, fg=FG_TEXT,
                            font=("monospace", 9), wrap="word")
        changelog.pack(fill="x", padx=16, pady=2)

        def do_create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing", "Enter a package name.")
                return

            fcstd_idx = fcstd_combo.current()
            fcstd_path = (fcstd_files[fcstd_idx - 1]["path"]
                          if fcstd_idx > 0 else None)

            mf_sel = mf_list.curselection()
            mf_paths = [mf_files[i]["path"] for i in mf_sel]

            snap_idx = snap_combo.current()
            snap_id = (history["snapshots"][snap_idx - 1]["id"]
                       if snap_idx > 0 else None)

            print_idx = print_combo.current()
            print_id = (history["prints"][print_idx - 1]["id"]
                        if print_idx > 0 else None)

            cl_text = changelog.get("1.0", "end").strip()

            entry, pkg_dir = create_package(
                name, fcstd_path=fcstd_path, mf_paths=mf_paths,
                render_paths=render_paths, camera_paths=camera_paths,
                changelog_text=cl_text, snapshot_id=snap_id,
                print_id=print_id)

            dlg.destroy()
            self._refresh_all()
            self._status(f"Package #{entry['id']} created at {pkg_dir.name}")

        bf = ttk.Frame(dlg)
        bf.pack(pady=(8, 12))
        ttk.Button(bf, text="Create Package", style="Accent.TButton",
                   command=do_create).pack(side="left", padx=4)
        ttk.Button(bf, text="Cancel",
                   command=dlg.destroy).pack(side="left", padx=4)

    # ── Event handlers ────────────────────────────────────────────────────

    def _on_print_select(self, event):
        sel = self._prints_tree.selection()
        self._print_detail.delete("1.0", "end")
        if not sel:
            return
        vals = self._prints_tree.item(sel[0], "values")
        pid = int(vals[0])
        history = load_history()
        for p in history.get("prints", []):
            if p["id"] == pid:
                lines = [
                    f"Print #{pid}: {p['message']}",
                    f"Date:   {p['timestamp'][:16].replace('T', ' ')}",
                    f"Result: {p.get('result', '?')}",
                    f"Git:    {p.get('git_hash', '?')}",
                    f"Files:  {', '.join(p.get('files', []))}",
                    f"Notes:  {p.get('notes', '')}",
                ]
                photos = p.get("camera_photos", [])
                if photos:
                    lines.append(f"Photos: {len(photos)}")
                    for ph in photos:
                        lines.append(f"  - {ph}")
                self._print_detail.insert("1.0", "\n".join(lines))
                break

    def _on_render_select(self, event):
        if not HAS_PIL:
            return
        sel = self._render_tree.selection()
        if not sel:
            return
        idx = self._render_tree.index(sel[0])
        if idx >= len(self._render_data):
            return
        path = self._render_data[idx]["path"]
        self._show_image_preview(path, self._render_preview)

    def _on_pkg_select(self, event):
        sel = self._pkg_tree.selection()
        self._pkg_detail.delete("1.0", "end")
        if not sel:
            return
        vals = self._pkg_tree.item(sel[0], "values")
        pkg_id = int(vals[0])
        history = load_history()
        for pkg in history.get("packages", []):
            if pkg["id"] == pkg_id:
                changes_path = PACKAGES_DIR / pkg["folder"] / "CHANGES.md"
                if changes_path.exists():
                    self._pkg_detail.insert("1.0", changes_path.read_text())
                else:
                    self._pkg_detail.insert("1.0",
                        f"Package: {pkg['name']}\n"
                        f"Folder: {pkg['folder']}\n"
                        f"Files: {', '.join(pkg.get('files', []))}")
                break

    # ── Helpers ────────────────────────────────────────────────────────────

    def _show_image_preview(self, path, label_widget):
        if not HAS_PIL:
            label_widget.config(text="PIL not available")
            return
        try:
            img = Image.open(path)
            # Fit to preview area
            lw = label_widget.winfo_width() or 600
            lh = label_widget.winfo_height() or 400
            if lw < 50:
                lw = 600
            if lh < 50:
                lh = 400
            img.thumbnail((lw, lh), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label_widget.config(image=photo, text="")
            self._image_cache[path] = photo  # prevent GC
        except Exception as e:
            label_widget.config(text=f"Cannot load: {e}", image="")

    def _open_folder(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        subprocess.Popen(["xdg-open", str(path)])

    def _status(self, text):
        self._status_var.set(text)
        self.update_idletasks()


# ─────────────────────────────────────────────────────────────────────────────
# Guide text
# ─────────────────────────────────────────────────────────────────────────────

GUIDE_TEXT = """# Dilder Design Tracker Guide
A tool for managing FreeCAD hardware design iterations, print logs, renders, and packaged releases.

## Dashboard
The Dashboard shows a live summary of your design state:
  - Git Hash: current commit of the repository
  - FCStd Files: number of FreeCAD model files in freecad-mk2/
  - 3MF Exports: number of 3MF sliceable exports
  - Renders: number of PNG renders in hardware-design/renders/
  - Snapshots: number of saved design snapshots
  - Prints: number of logged 3D prints

Actions:
  - Take Snapshot: saves the current state (file counts, hashes, git ref)
    and backs up the newest FCStd file for later comparison
  - Refresh: re-scans all directories for changes
  - Compare Snapshots: diff two snapshots side-by-side to see what changed

## Models & Exports
Two tables showing all FreeCAD source files and 3MF exports:

FreeCAD Models (.FCStd):
  - Shows file name, modification date, file size, and MD5 hash
  - Newest files appear first
  - Use this to track which model iteration you are working with

3MF Exports:
  - Shows all 3MF files from freecad-mk2/ and the packages directory
  - These are the files you send to your slicer for printing
  - Select files here when logging a print or creating a package

## Prints
Track every 3D print attempt with full context:

Log New Print:
  1. Enter a description of what you printed
  2. Select the result: success, partial, or failed
  3. Add any notes about print settings or issues
  4. Select which 3MF files were used
  5. Optionally attach camera photos of the printout

Attach Photo to Print:
  - Select a print entry in the table
  - Click "Attach Photo" to add camera pictures (PNG/JPG)
  - Photos are tracked by file path for reference

Print Detail Panel:
  - Click any print entry to see full details including
    files, notes, git hash, and attached photos

## Renders
A gallery view of all render images in hardware-design/renders/:

  - Left panel: list of all render PNGs sorted by date
  - Right panel: live image preview of the selected render
  - Click any render to see it at full preview size
  - "Open Renders Folder" launches your system file manager

These renders are generated by the build_and_render.sh tool which
creates publication-quality orthographic and isometric views of
the FreeCAD assembly.

## Packages
Bundle related files into tracked folders for easy archival:

Creating a Package:
  1. Enter a descriptive name (e.g., "Rev2 Mk2 — widened USB cutout")
  2. Optionally link to a snapshot and/or print entry
  3. Select a FreeCAD model file to include
  4. Select 3MF export files to include
  5. Add render images from the renders folder
  6. Add camera photos of physical prints
  7. Write a changelog describing what changed

Each package creates a folder in .design-tracker/packages/ containing:
  - The FCStd model file (frozen copy)
  - Selected 3MF exports
  - renders/ subfolder with selected render images
  - photos/ subfolder with camera pictures
  - CHANGES.md with your changelog, metadata, and file manifest

Use packages to create a complete record of each design iteration
that you can revisit, share, or compare later.

## Workflow: Design-Print-Review Cycle
A recommended workflow for each design iteration:

  1. Make changes in FreeCAD (edit the macro, rebuild the model)
  2. Take a Snapshot (Dashboard tab) to record the state
  3. Export 3MF files for printing
  4. Log the Print (Prints tab) with result and notes
  5. Take camera photos of the physical print
  6. Attach Photos to the print entry
  7. Create a Package linking the snapshot, print, renders, and photos
  8. Commit to git when satisfied

## Naming Conventions
Recommended file naming for FreeCAD models:

  Pattern: Dilder_Rev2_Mk2-<changes>-<DD-MM-YYYY-HHMM>.FCStd

  Examples:
    Dilder_Rev2_Mk2-joystick-anchor-piezo-30-04-2026-1617.FCStd
    Dilder_Rev2_Mk2-widened-inlay-01-05-2026-0930.FCStd

  Rules:
    1. Always start with Dilder_Rev2_Mk2-
    2. List key changes separated by hyphens
    3. End with date and time (DD-MM-YYYY-HHMM)
    4. Keep descriptions short (2-4 words)
    5. Use lowercase with hyphens (no spaces)

## CLI Commands
The tracker also works from the command line:

  python3 design-tracker.py               # launch GUI (default)
  python3 design-tracker.py --cli         # interactive terminal menu
  python3 design-tracker.py snap "msg"    # quick snapshot
  python3 design-tracker.py log           # show timeline
  python3 design-tracker.py status        # current design state
  python3 design-tracker.py diff 1 2      # compare snapshots 1 and 2
  python3 design-tracker.py naming        # naming convention guide
"""


# ═══════════════════════════════════════════════════════════════════════════════
# CLI (legacy)
# ═══════════════════════════════════════════════════════════════════════════════

# ANSI colors for CLI
_B = "\033[1m"
_D = "\033[2m"
_C = "\033[36m"
_G = "\033[32m"
_Y = "\033[33m"
_R = "\033[31m"
_M = "\033[35m"
_W = "\033[97m"
_X = "\033[0m"


def cli_status():
    fcstd = scan_fcstd()
    mf = scan_3mf()
    renders = scan_renders()
    git_hash = get_git_hash()
    git_diff = get_git_diff_stat()
    history = load_history()

    print(f"\n  {_B}{_C}Design Status{_X}")
    print(f"  {_C}{'─' * 56}{_X}")
    print(f"  {_B}Git:{_X}       {git_hash}")
    print(f"  {_B}FCStd:{_X}     {len(fcstd)} files")
    print(f"  {_B}3MF:{_X}       {len(mf)} exports")
    print(f"  {_B}Renders:{_X}   {len(renders)} PNGs")
    print(f"  {_B}Snapshots:{_X} {len(history.get('snapshots', []))}")
    print(f"  {_B}Prints:{_X}    {len(history.get('prints', []))}")

    if fcstd:
        n = fcstd[0]
        date = n["mtime"][:16].replace("T", " ")
        size_mb = n["size"] / 1024 / 1024
        print(f"\n  {_B}Newest model:{_X}")
        print(f"  {_G}{n['name']}{_X}")
        print(f"  {_D}{date}  |  {size_mb:.1f} MB  |  hash: {n['hash']}{_X}")

    if git_diff != "clean":
        print(f"\n  {_Y}Uncommitted design changes:{_X}")
        print(f"  {_D}{git_diff}{_X}")


def cli_log():
    history = load_history()
    snaps = history.get("snapshots", [])
    prints = history.get("prints", [])

    events = []
    for s in snaps:
        events.append(("snap", s["timestamp"], s))
    for p in prints:
        events.append(("print", p["timestamp"], p))
    events.sort(key=lambda x: x[1], reverse=True)

    print(f"\n  {_B}{_C}Design Timeline{_X}")
    print(f"  {_D}{len(snaps)} snapshots, {len(prints)} prints{_X}")
    print(f"  {_C}{'─' * 56}{_X}")

    if not events:
        print(f"\n  {_D}No history yet. Run: python3 design-tracker.py snap{_X}")
        return

    for kind, ts, data in events:
        date = ts[:16].replace("T", " ")
        if kind == "snap":
            sid = data["id"]
            msg = data["message"]
            git = data.get("git_hash", "")[:7]
            print(f"\n  {_G}#{sid:04d}{_X}  {_B}{date}{_X}  {_D}({git}){_X}")
            print(f"        {_W}{msg}{_X}")
            print(f"        {_D}{data['fcstd_count']} models, "
                  f"{data['mf_count']} exports, "
                  f"{data['render_count']} renders{_X}")
        elif kind == "print":
            pid = data["id"]
            msg = data["message"]
            files = ", ".join(data.get("files", [])[:3])
            result = data.get("result", "unknown")
            color = _G if result == "success" else _Y if result == "partial" else _R
            print(f"\n  {_M}P{pid:04d}{_X}  {_B}{date}{_X}")
            print(f"        {_W}{msg}{_X}")
            print(f"        {_D}Files: {files}{_X}")
            print(f"        Result: {color}{result}{_X}")


def cli_diff(id1, id2):
    history = load_history()
    snaps = {s["id"]: s for s in history.get("snapshots", [])}
    if id1 not in snaps or id2 not in snaps:
        print(f"  {_R}Snapshot #{id1} or #{id2} not found{_X}")
        return
    s1, s2 = snaps[id1], snaps[id2]
    print(f"\n  {_B}{_C}Comparing Snapshot #{id1} vs #{id2}{_X}")
    print(f"  {_C}{'─' * 56}{_X}")
    print(f"\n  {_B}#{id1}{_X} ({s1['timestamp'][:16]}): {s1['message']}")
    print(f"  {_B}#{id2}{_X} ({s2['timestamp'][:16]}): {s2['message']}")
    for label, k in [("FCStd files", "fcstd_count"),
                     ("3MF exports", "mf_count"),
                     ("Renders", "render_count")]:
        v1, v2 = s1.get(k, 0), s2.get(k, 0)
        delta = v2 - v1
        color = _G if delta > 0 else _R if delta < 0 else _D
        sign = "+" if delta > 0 else ""
        print(f"  {label}: {v1} -> {v2}  {color}({sign}{delta}){_X}")
    if s1.get("fcstd_newest_hash") != s2.get("fcstd_newest_hash"):
        print(f"\n  {_Y}FCStd changed{_X}")
    else:
        print(f"\n  {_D}FCStd unchanged{_X}")
    if s1.get("macro_hash") != s2.get("macro_hash"):
        print(f"  {_Y}Macro changed{_X}")
    else:
        print(f"  {_D}Macro unchanged{_X}")


def cli_naming():
    print(f"""
  {_B}{_C}Recommended CAD File Naming Convention{_X}
  {_C}{'─' * 56}{_X}

  {_B}Pattern:{_X}
  Dilder_Rev2_Mk2-<changes>-<DD-MM-YYYY-HHMM>.FCStd

  {_B}Examples:{_X}
  {_G}Dilder_Rev2_Mk2-joystick-anchor-piezo-30-04-2026-1617.FCStd{_X}
  {_G}Dilder_Rev2_Mk2-widened-inlay-01-05-2026-0930.FCStd{_X}

  {_B}Rules:{_X}
  1. Always start with {_W}Dilder_Rev2_Mk2-{_X}
  2. List the {_W}key changes{_X} separated by hyphens
  3. End with the {_W}date and time{_X} (DD-MM-YYYY-HHMM)
  4. Keep change descriptions {_W}short{_X} (2-4 words)
  5. Use {_W}lowercase{_X} with hyphens (no spaces)
""")


def cli_menu():
    while True:
        print(f"\n  {_B}{_C}{'═' * 41}{_X}")
        print(f"  {_B}{_C}  Dilder Design Tracker v{APP_VERSION}  {_X}")
        print(f"  {_B}{_C}{'═' * 41}{_X}")
        print(f"""
  {_W}1){_X}  Status          {_D}— current design state{_X}
  {_W}2){_X}  Take snapshot    {_D}— save current state{_X}
  {_W}3){_X}  Timeline         {_D}— full design history{_X}
  {_W}4){_X}  Log a print      {_D}— record what you printed{_X}
  {_W}5){_X}  Compare          {_D}— diff two snapshots{_X}
  {_W}6){_X}  Naming guide     {_D}— file naming convention{_X}
  {_W}g){_X}  Launch GUI       {_D}— open graphical interface{_X}
  {_W}q){_X}  Quit
""")
        choice = input(f"  {_B}{_C}Choice [1-6/g/q]:{_X} ").strip()

        if choice == "1":
            cli_status()
        elif choice == "2":
            msg = input(f"\n  {_B}{_C}Description:{_X} ").strip()
            if not msg:
                msg = f"Snapshot {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            snap = take_snapshot(msg)
            print(f"\n  {_G}Snapshot #{snap['id']} saved{_X}")
        elif choice == "3":
            cli_log()
        elif choice == "4":
            # Simple CLI print log
            mf_files = scan_3mf()
            if mf_files:
                print(f"\n  {_D}Recent 3MF exports:{_X}")
                for i, f in enumerate(mf_files[:8]):
                    print(f"  {_W}{i+1}){_X} {f['name'][:60]}")
            msg = input(f"\n  {_B}{_C}What did you print?{_X} ")
            files_str = input(f"  {_B}{_C}Which files? (names or numbers):{_X} ")
            result = input(f"  {_B}{_C}Result (success/partial/failed):{_X} ") or "success"
            notes = input(f"  {_B}{_C}Notes:{_X} ")
            printed = []
            for part in files_str.split(","):
                part = part.strip()
                if part.isdigit() and int(part) <= len(mf_files):
                    printed.append(mf_files[int(part) - 1]["name"])
                elif part:
                    printed.append(part)
            entry = log_print_entry(msg, printed, result, notes)
            print(f"\n  {_G}Print #{entry['id']} logged{_X}")
        elif choice == "5":
            id1 = input(f"  {_C}First snapshot #:{_X} ").strip()
            id2 = input(f"  {_C}Second snapshot #:{_X} ").strip()
            try:
                cli_diff(int(id1), int(id2))
            except ValueError:
                print(f"  {_R}Enter valid snapshot numbers{_X}")
        elif choice == "6":
            cli_naming()
        elif choice in ("g", "G"):
            app = DesignTrackerApp()
            app.mainloop()
        elif choice in ("q", "Q"):
            break


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    ensure_dirs()

    if len(sys.argv) < 2:
        # Default: launch GUI
        app = DesignTrackerApp()
        app.mainloop()
    elif sys.argv[1] == "--cli":
        cli_menu()
    elif sys.argv[1] == "log":
        cli_log()
    elif sys.argv[1] == "snap":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        if not msg:
            msg = f"Snapshot {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        snap = take_snapshot(msg)
        print(f"Snapshot #{snap['id']} saved")
    elif sys.argv[1] == "prints":
        cli_log()
    elif sys.argv[1] == "status":
        cli_status()
    elif sys.argv[1] == "diff" and len(sys.argv) >= 4:
        cli_diff(int(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "naming":
        cli_naming()
    else:
        print(__doc__)
