#!/usr/bin/env python3
"""
Dilder DesignTool — SCAD Design Management Companion

Tkinter GUI for managing OpenSCAD hardware design files: browsing,
preset diffing, exporting to STL/3MF/FreeCAD, 3D preview, and
tracking the evolution of every export.

Usage:
  python3 hardware-design/DesignTool/designtool.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

TOOL_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = TOOL_DIR.parent.parent.resolve()
HARDWARE_DIR = PROJECT_ROOT / "hardware-design"
SCAD_SEARCH_ROOT = HARDWARE_DIR / "scad Parts"
EXPORTS_DIR = TOOL_DIR / "exports"
HISTORY_FILE = TOOL_DIR / "history.json"

APP_NAME = "Dilder DesignTool"
APP_VERSION = "0.1.0"

# ─────────────────────────────────────────────────────────────────────────────
# Theme (Catppuccin Mocha — matches DevTool)
# ─────────────────────────────────────────────────────────────────────────────

BG_DARK = "#1e1e2e"
BG_PANEL = "#282840"
BG_CANVAS = "#2a2a3a"
FG_TEXT = "#cdd6f4"
FG_DIM = "#6c7086"
FG_ACCENT = "#89b4fa"
FG_MAGENTA = "#cba6f7"
FG_YELLOW = "#f9e2af"
FG_GREEN = "#a6e3a1"
FG_RED = "#f38ba8"

# ─────────────────────────────────────────────────────────────────────────────
# OpenSCAD camera presets for orthographic views
# ─────────────────────────────────────────────────────────────────────────────

# Camera tuples: (tx, ty, tz, rot_x, rot_y, rot_z)
# OpenSCAD --camera format: tx,ty,tz,rot_x,rot_y,rot_z,distance
ORTHO_CAMERAS = {
    "Front":  (0, 0, 0, 90, 0, 0),
    "Back":   (0, 0, 0, 90, 0, 180),
    "Right":  (0, 0, 0, 90, 0, 270),
    "Left":   (0, 0, 0, 90, 0, 90),
    "Top":    (0, 0, 0, 0, 0, 0),
    "Bottom": (0, 0, 0, 180, 0, 0),
}

DEFAULT_3D_CAMERA = (0, 0, 0, 55, 0, 25)  # isometric-ish
DEFAULT_CAMERA_DIST = 200

# ─────────────────────────────────────────────────────────────────────────────
# Utility functions (absorbed from export-preset.py, bake-preset.py, etc.)
# ─────────────────────────────────────────────────────────────────────────────

def find_openscad():
    return shutil.which("openscad") or shutil.which("openscad-nightly")


def slugify(name):
    s = re.sub(r"[^\w\-.]+", "_", name).strip("_")
    return s or "preset"


def _keep_first_pairs(pairs):
    """JSON object_pairs_hook that keeps the FIRST value for duplicate keys.

    OpenSCAD sometimes writes a second empty `"parameterSets": ""` after
    the real one. Python's default JSON parser keeps the last value,
    which clobbers the presets. This hook keeps the first.
    """
    d = {}
    for k, v in pairs:
        if k not in d:
            d[k] = v
    return d


def load_presets(json_path):
    if not json_path.exists():
        return {}
    try:
        data = json.loads(json_path.read_text(), object_pairs_hook=_keep_first_pairs)
        if not isinstance(data, dict):
            return {}
        ps = data.get("parameterSets", {})
        if not isinstance(ps, dict):
            return {}
        return ps
    except Exception:
        return {}


def find_scad_files(root):
    files = []
    seen = set()
    if not root.is_dir():
        return files
    for f in sorted(root.rglob("*.scad")):
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            files.append(resolved)
    return files


def collect_scads_with_presets(root):
    out = []
    for scad in sorted(root.rglob("*.scad")):
        json_path = scad.with_suffix(".json")
        if not json_path.exists():
            continue
        try:
            data = json.loads(json_path.read_text())
        except Exception:
            continue
        presets = list(data.get("parameterSets", {}).keys())
        if presets:
            out.append((scad, presets))
    return out


# Regex from bake-preset.py for parsing SCAD parameter declarations
_PARAM_RE = re.compile(
    r"^(?P<lead>\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*)"
    r"(?P<value>[^;]+?)"
    r"(?P<tail>\s*;.*)$"
)


def parse_scad_defaults(scad_path):
    """Extract top-level parameter = value declarations from a SCAD file."""
    params = {}
    try:
        for line in scad_path.read_text(errors="replace").splitlines():
            m = _PARAM_RE.match(line)
            if m:
                params[m.group("name")] = m.group("value").strip()
    except Exception:
        pass
    return params


def diff_params(base, other):
    """Compare two param dicts. Returns list of (name, status, base_val, other_val)."""
    all_keys = sorted(set(list(base.keys()) + list(other.keys())))
    result = []
    for k in all_keys:
        in_base = k in base
        in_other = k in other
        if in_base and in_other:
            if str(base[k]) == str(other[k]):
                result.append((k, "unchanged", str(base[k]), str(other[k])))
            else:
                result.append((k, "changed", str(base[k]), str(other[k])))
        elif in_base:
            result.append((k, "removed", str(base[k]), ""))
        else:
            result.append((k, "added", "", str(other[k])))
    return result


def generate_description_md(scad_path, preset_name, preset_params, defaults, formats, ts):
    lines = [
        f"# Export: {scad_path.stem} / {preset_name}",
        f"",
        f"- **Date:** {ts}",
        f"- **SCAD:** `{scad_path.name}`",
        f"- **Preset:** `{preset_name}`",
        f"- **Formats:** {', '.join(formats)}",
        f"",
        f"## Parameters",
        f"",
        f"| Parameter | Value | Default | Changed |",
        f"|-----------|-------|---------|---------|",
    ]
    for k in sorted(preset_params.keys()):
        val = str(preset_params[k])
        default = str(defaults.get(k, ""))
        changed = "**yes**" if val != default else ""
        lines.append(f"| `{k}` | {val} | {default} | {changed} |")
    return "\n".join(lines) + "\n"


def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return []
    return []


def append_history(entry):
    history = load_history()
    history.append(entry)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1: SCAD Browser
# ─────────────────────────────────────────────────────────────────────────────

class ScadBrowserTab(ttk.Frame):
    """Browse, filter, and sort all SCAD files in the hardware-design tree."""

    POLL_INTERVAL_MS = 3000  # check for filesystem changes every 3 seconds

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._file_data = []
        self._sort_col = "modified"
        self._sort_reverse = True
        self._last_fingerprint = ""
        self._build_ui()
        self._scan_files()
        self._start_file_watcher()

    def _build_ui(self):
        # Search bar
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", lambda e: self._populate_tree())
        ttk.Button(search_frame, text="Refresh", command=self._manual_refresh).pack(side=tk.RIGHT, padx=5)

        # Main paned: tree + detail
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Treeview
        tree_frame = ttk.Frame(paned)
        paned.add(tree_frame, weight=3)

        cols = ("name", "path", "presets", "modified", "size")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("name", text="File Name", command=lambda: self._sort_by("name"))
        self.tree.heading("path", text="Path", command=lambda: self._sort_by("path"))
        self.tree.heading("presets", text="Presets", command=lambda: self._sort_by("presets"))
        self.tree.heading("modified", text="Modified", command=lambda: self._sort_by("modified"))
        self.tree.heading("size", text="Size", command=lambda: self._sort_by("size"))
        self.tree.column("name", width=220, minwidth=120)
        self.tree.column("path", width=260, minwidth=100)
        self.tree.column("presets", width=60, minwidth=40, anchor=tk.CENTER)
        self.tree.column("modified", width=140, minwidth=90)
        self.tree.column("size", width=70, minwidth=40, anchor=tk.E)

        scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Detail panel
        detail_frame = ttk.Frame(paned)
        paned.add(detail_frame, weight=2)

        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, bg=BG_DARK, fg=FG_TEXT,
                                   font=("JetBrains Mono", 10), state=tk.DISABLED,
                                   padx=10, pady=10)
        self.detail_text.pack(fill=tk.BOTH, expand=True)

    def _scan_files(self):
        self._file_data = []
        all_scads = find_scad_files(SCAD_SEARCH_ROOT)
        for scad in all_scads:
            json_path = scad.with_suffix(".json")
            presets = load_presets(json_path) if json_path.exists() else {}
            try:
                stat = scad.stat()
            except OSError:
                continue
            try:
                rel_path = str(scad.relative_to(PROJECT_ROOT))
            except ValueError:
                rel_path = str(scad)
            self._file_data.append({
                "path": scad,
                "rel_path": rel_path,
                "name": scad.name,
                "mtime": stat.st_mtime,
                "size": stat.st_size,
                "preset_count": len(presets),
                "preset_names": list(presets.keys()),
            })
        self._last_fingerprint = self._compute_fingerprint()
        self._populate_tree()
        self.app.log(f"[browser] Scanned {len(self._file_data)} SCAD files")

    def _compute_fingerprint(self):
        """Build a lightweight fingerprint of all SCAD+JSON files for change detection."""
        parts = []
        try:
            for f in sorted(SCAD_SEARCH_ROOT.rglob("*.scad")):
                try:
                    s = f.stat()
                    parts.append(f"{f}:{s.st_mtime}:{s.st_size}")
                except OSError:
                    pass
            for f in sorted(SCAD_SEARCH_ROOT.rglob("*.json")):
                try:
                    s = f.stat()
                    parts.append(f"{f}:{s.st_mtime}:{s.st_size}")
                except OSError:
                    pass
        except OSError:
            pass
        return "|".join(parts)

    def _start_file_watcher(self):
        """Poll for filesystem changes and auto-refresh when SCAD/JSON files change."""
        self._check_for_changes()

    def _check_for_changes(self):
        try:
            current = self._compute_fingerprint()
            if current != self._last_fingerprint:
                self._scan_files()
                self.app.log("[browser] Files changed on disk — auto-refreshed")
                self._refresh_dependent_tabs()
        except Exception as e:
            self.app.log(f"[browser] Watch error: {e}")
        self.after(self.POLL_INTERVAL_MS, self._check_for_changes)

    def _refresh_dependent_tabs(self):
        """Refresh preset manager and export tab if a SCAD is active."""
        scad = self.app.selected_scad
        if scad and scad.exists():
            try:
                self.app.preset_tab.refresh_for_scad(scad)
                self.app.export_tab.refresh_for_scad(scad)
            except Exception:
                pass

    def _manual_refresh(self):
        """Refresh button handler — rescan files and update all tabs."""
        self._scan_files()
        self._refresh_dependent_tabs()
        self.app.log("[browser] Manual refresh")

    def _populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        filt = self.search_var.get().lower()
        data = self._file_data
        if filt:
            data = [d for d in data if filt in d["name"].lower()]

        # Sort
        key_map = {
            "name": lambda d: d["name"].lower(),
            "path": lambda d: d["rel_path"].lower(),
            "presets": lambda d: d["preset_count"],
            "modified": lambda d: d["mtime"],
            "size": lambda d: d["size"],
        }
        data.sort(key=key_map.get(self._sort_col, key_map["modified"]),
                  reverse=self._sort_reverse)

        for d in data:
            mtime_str = datetime.fromtimestamp(d["mtime"]).strftime("%Y-%m-%d %H:%M")
            size_str = f"{d['size'] / 1024:.1f} KB"
            self.tree.insert("", tk.END, values=(
                d["name"], d["rel_path"], d["preset_count"], mtime_str, size_str
            ), tags=(str(d["path"]),))

    def _sort_by(self, col):
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = col in ("modified", "size", "presets")  # desc by default
        self._populate_tree()

    def _on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], "tags")
        if not tags:
            return
        scad_path = Path(tags[0])
        self.app.set_active_scad(scad_path)

        # Show detail
        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)

        try:
            rel = scad_path.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = scad_path

        lines = [f"Path: {rel}\n"]
        stat = scad_path.stat()
        lines.append(f"Size: {stat.st_size / 1024:.1f} KB")
        lines.append(f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Presets
        json_path = scad_path.with_suffix(".json")
        presets = load_presets(json_path) if json_path.exists() else {}
        if presets:
            lines.append(f"Presets ({len(presets)}):")
            for name in presets:
                lines.append(f"  - {name}")
        else:
            lines.append("No presets (no JSON sidecar)")
        lines.append("")

        # Header comments from SCAD
        try:
            scad_text = scad_path.read_text(errors="replace")
            header = []
            for line in scad_text.splitlines()[:30]:
                if line.startswith("//"):
                    header.append(line)
                elif header:
                    break
            if header:
                lines.append("Header:")
                lines.extend(header)
        except Exception:
            pass

        self.detail_text.insert(tk.END, "\n".join(lines))
        self.detail_text.configure(state=tk.DISABLED)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2: Preset Manager & Diff
# ─────────────────────────────────────────────────────────────────────────────

class PresetManagerTab(ttk.Frame):
    """View presets for the active SCAD and diff any two parameter sets."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._presets = {}
        self._defaults = {}
        self._build_ui()

    def _build_ui(self):
        # Top: preset list
        list_frame = ttk.LabelFrame(self, text="Presets", padding=8)
        list_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.preset_list = tk.Listbox(list_frame, height=6, bg=BG_DARK, fg=FG_TEXT,
                                       selectbackground=FG_ACCENT, selectforeground=BG_DARK,
                                       font=("JetBrains Mono", 10), activestyle="none")
        self.preset_list.pack(fill=tk.X)
        self.preset_list.bind("<<ListboxSelect>>", self._on_preset_select)

        # Diff controls
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(ctrl_frame, text="Diff A:").pack(side=tk.LEFT, padx=(0, 3))
        self.diff_a_var = tk.StringVar()
        self.diff_a_combo = ttk.Combobox(ctrl_frame, textvariable=self.diff_a_var,
                                          state="readonly", width=35, font=("JetBrains Mono", 9))
        self.diff_a_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(ctrl_frame, text="Diff B:").pack(side=tk.LEFT, padx=(0, 3))
        self.diff_b_var = tk.StringVar()
        self.diff_b_combo = ttk.Combobox(ctrl_frame, textvariable=self.diff_b_var,
                                          state="readonly", width=35, font=("JetBrains Mono", 9))
        self.diff_b_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(ctrl_frame, text="Compute Diff", command=self._compute_diff).pack(side=tk.LEFT, padx=5)

        # Diff view
        diff_frame = ttk.LabelFrame(self, text="Parameter Diff", padding=8)
        diff_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.diff_text = tk.Text(diff_frame, wrap=tk.NONE, bg=BG_DARK, fg=FG_TEXT,
                                  font=("JetBrains Mono", 10), state=tk.DISABLED,
                                  padx=10, pady=10)
        diff_scroll_y = ttk.Scrollbar(diff_frame, orient=tk.VERTICAL, command=self.diff_text.yview)
        diff_scroll_x = ttk.Scrollbar(diff_frame, orient=tk.HORIZONTAL, command=self.diff_text.xview)
        self.diff_text.configure(yscrollcommand=diff_scroll_y.set, xscrollcommand=diff_scroll_x.set)
        diff_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        diff_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.diff_text.pack(fill=tk.BOTH, expand=True)

        self.diff_text.tag_configure("added", foreground=FG_GREEN)
        self.diff_text.tag_configure("removed", foreground=FG_RED)
        self.diff_text.tag_configure("changed", foreground=FG_YELLOW)
        self.diff_text.tag_configure("unchanged", foreground=FG_DIM)
        self.diff_text.tag_configure("header", foreground=FG_ACCENT, font=("JetBrains Mono", 11, "bold"))

    def refresh_for_scad(self, scad_path):
        self._defaults = parse_scad_defaults(scad_path)
        json_path = scad_path.with_suffix(".json")
        self._presets = load_presets(json_path)

        self.preset_list.delete(0, tk.END)
        names = ["(SCAD Defaults)"] + list(self._presets.keys())
        for name in names:
            self.preset_list.insert(tk.END, name)

        self.diff_a_combo["values"] = names
        self.diff_b_combo["values"] = names
        if len(names) >= 2:
            self.diff_a_var.set(names[0])
            self.diff_b_var.set(names[1])

        # Clear diff
        self.diff_text.configure(state=tk.NORMAL)
        self.diff_text.delete("1.0", tk.END)
        self.diff_text.insert(tk.END, f"{len(self._presets)} preset(s) loaded. Select two to diff.\n", "header")
        self.diff_text.configure(state=tk.DISABLED)

    def _on_preset_select(self, event=None):
        sel = self.preset_list.curselection()
        if not sel:
            return
        name = self.preset_list.get(sel[0])
        if name != "(SCAD Defaults)":
            self.app.set_active_preset(name)

    def _get_params(self, name):
        if name == "(SCAD Defaults)":
            return self._defaults
        return self._presets.get(name, {})

    def _compute_diff(self):
        a_name = self.diff_a_var.get()
        b_name = self.diff_b_var.get()
        if not a_name or not b_name:
            return

        a_params = self._get_params(a_name)
        b_params = self._get_params(b_name)
        diffs = diff_params(a_params, b_params)

        self.diff_text.configure(state=tk.NORMAL)
        self.diff_text.delete("1.0", tk.END)
        self.diff_text.insert(tk.END, f"  {a_name}  vs  {b_name}\n\n", "header")

        changed_count = 0
        # Show changes first, then unchanged
        for status in ("changed", "added", "removed", "unchanged"):
            items = [(n, s, bv, ov) for n, s, bv, ov in diffs if s == status]
            if not items:
                continue
            label = {"changed": "CHANGED", "added": "ADDED (in B only)",
                     "removed": "REMOVED (in A only)", "unchanged": "UNCHANGED"}[status]
            self.diff_text.insert(tk.END, f"--- {label} ({len(items)}) ---\n", status)
            for name, st, base_val, other_val in items:
                if st == "changed":
                    self.diff_text.insert(tk.END, f"  {name}: {base_val} -> {other_val}\n", st)
                    changed_count += 1
                elif st == "added":
                    self.diff_text.insert(tk.END, f"  + {name}: {other_val}\n", st)
                elif st == "removed":
                    self.diff_text.insert(tk.END, f"  - {name}: {base_val}\n", st)
                else:
                    self.diff_text.insert(tk.END, f"  {name}: {base_val}\n", st)
            self.diff_text.insert(tk.END, "\n")

        self.diff_text.configure(state=tk.DISABLED)
        self.app.log(f"[diff] {a_name} vs {b_name}: {changed_count} changed params")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3: Export
# ─────────────────────────────────────────────────────────────────────────────

class ExportTab(ttk.Frame):
    """Export the active SCAD+preset to STL, 3MF, and/or FreeCAD."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._exporting = False
        self._build_ui()

    def _build_ui(self):
        # Selection summary
        sel_frame = ttk.LabelFrame(self, text="Current Selection", padding=8)
        sel_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.scad_label = ttk.Label(sel_frame, text="SCAD: (none)", font=("JetBrains Mono", 10))
        self.scad_label.pack(anchor=tk.W)

        preset_row = ttk.Frame(sel_frame)
        preset_row.pack(fill=tk.X, pady=(4, 0))
        ttk.Label(preset_row, text="Preset:", font=("JetBrains Mono", 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.preset_var = tk.StringVar(value="(SCAD Defaults)")
        self.preset_combo = ttk.Combobox(preset_row, textvariable=self.preset_var,
                                          state="readonly", width=45, font=("JetBrains Mono", 9))
        self.preset_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_changed)

        # Format options
        fmt_frame = ttk.LabelFrame(self, text="Export Formats", padding=8)
        fmt_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stl_var = tk.BooleanVar(value=True)
        self.mf3_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(fmt_frame, text="STL", variable=self.stl_var).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(fmt_frame, text="3MF", variable=self.mf3_var).pack(side=tk.LEFT, padx=10)

        # Embedded label options
        label_frame = ttk.LabelFrame(self, text="Embedded Label", padding=8)
        label_frame.pack(fill=tk.X, padx=10, pady=5)

        row1 = ttk.Frame(label_frame)
        row1.pack(fill=tk.X, pady=(0, 4))

        self.label_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row1, text="Embed label on vertical face",
                        variable=self.label_enabled_var,
                        command=self._toggle_label_controls).pack(side=tk.LEFT)

        self.label_mode_var = tk.StringVar(value="recessed")
        self.label_raised_rb = ttk.Radiobutton(row1, text="Raised", variable=self.label_mode_var,
                                                value="raised")
        self.label_raised_rb.pack(side=tk.RIGHT, padx=5)
        self.label_recessed_rb = ttk.Radiobutton(row1, text="Recessed", variable=self.label_mode_var,
                                                  value="recessed")
        self.label_recessed_rb.pack(side=tk.RIGHT, padx=5)

        row2 = ttk.Frame(label_frame)
        row2.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(row2, text="Text:").pack(side=tk.LEFT, padx=(0, 5))
        self.label_text_var = tk.StringVar(value="(auto: filename)")
        self.label_text_entry = ttk.Entry(row2, textvariable=self.label_text_var,
                                           font=("JetBrains Mono", 10))
        self.label_text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ttk.Label(row2, text="Size:").pack(side=tk.LEFT, padx=(0, 3))
        self.label_size_var = tk.DoubleVar(value=3.0)
        self.label_size_spin = ttk.Spinbox(row2, from_=1.0, to=12.0, increment=0.5,
                                            textvariable=self.label_size_var, width=5,
                                            font=("JetBrains Mono", 9))
        self.label_size_spin.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row2, text="Depth:").pack(side=tk.LEFT, padx=(0, 3))
        self.label_depth_var = tk.DoubleVar(value=0.4)
        self.label_depth_spin = ttk.Spinbox(row2, from_=0.2, to=2.0, increment=0.1,
                                             textvariable=self.label_depth_var, width=5,
                                             font=("JetBrains Mono", 9))
        self.label_depth_spin.pack(side=tk.LEFT)

        row3 = ttk.Frame(label_frame)
        row3.pack(fill=tk.X)

        ttk.Label(row3, text="Face:").pack(side=tk.LEFT, padx=(0, 5))
        self.label_face_var = tk.StringVar(value="front (-Y)")
        self.label_face_combo = ttk.Combobox(row3, textvariable=self.label_face_var,
                                              state="readonly", width=14,
                                              values=["front (-Y)", "back (+Y)",
                                                      "left (-X)", "right (+X)"],
                                              font=("JetBrains Mono", 9))
        self.label_face_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row3, text="Z offset:").pack(side=tk.LEFT, padx=(0, 3))
        self.label_z_var = tk.DoubleVar(value=4.0)
        self.label_z_spin = ttk.Spinbox(row3, from_=-20.0, to=60.0, increment=1.0,
                                         textvariable=self.label_z_var, width=5,
                                         font=("JetBrains Mono", 9))
        self.label_z_spin.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row3, text="Along-face offset:").pack(side=tk.LEFT, padx=(0, 3))
        self.label_lateral_var = tk.DoubleVar(value=0.0)
        self.label_lateral_spin = ttk.Spinbox(row3, from_=-50.0, to=50.0, increment=1.0,
                                               textvariable=self.label_lateral_var, width=5,
                                               font=("JetBrains Mono", 9))
        self.label_lateral_spin.pack(side=tk.LEFT)

        # Start with label controls dimmed
        self._toggle_label_controls()

        # Description
        desc_frame = ttk.LabelFrame(self, text="Description (optional)", padding=8)
        desc_frame.pack(fill=tk.X, padx=10, pady=5)

        self.desc_entry = ttk.Entry(desc_frame, font=("JetBrains Mono", 10))
        self.desc_entry.pack(fill=tk.X)

        # Export button
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        self.export_btn = ttk.Button(btn_frame, text="Export", command=self._start_export)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Log
        log_frame = ttk.LabelFrame(self, text="Export Log", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, bg=BG_DARK, fg=FG_TEXT,
                                 font=("JetBrains Mono", 9), state=tk.DISABLED, height=10)
        scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def refresh_for_scad(self, scad_path):
        self.scad_label.config(text=f"SCAD: {scad_path.name}")
        # Populate preset dropdown
        json_path = scad_path.with_suffix(".json")
        presets = load_presets(json_path)
        names = ["(SCAD Defaults)"] + list(presets.keys())
        self.preset_combo["values"] = names
        self.preset_var.set("(SCAD Defaults)")
        # Update label text placeholder
        self.label_text_var.set(scad_path.stem)

    def refresh_for_preset(self, preset_name):
        self.preset_var.set(preset_name)

    def _on_preset_changed(self, event=None):
        name = self.preset_var.get()
        if name and name != "(SCAD Defaults)":
            self.app.set_active_preset(name)

    def _toggle_label_controls(self):
        enabled = self.label_enabled_var.get()
        state = "normal" if enabled else "disabled"
        ro_state = "readonly" if enabled else "disabled"
        for w in (self.label_text_entry, self.label_size_spin,
                  self.label_depth_spin, self.label_z_spin,
                  self.label_lateral_spin):
            w.configure(state=state)
        self.label_face_combo.configure(state=ro_state)
        self.label_raised_rb.configure(state=state)
        self.label_recessed_rb.configure(state=state)

    def _generate_label_wrapper(self, stl_path, label_text, size, depth, mode, face, z_off, lateral_off):
        """Generate a temporary SCAD that imports the STL and embosses/debosses a label.

        The text is placed at the origin plane of the chosen face and offset by
        the user's Z and lateral controls. The boolean op with the model does the
        rest:
          - recessed: difference() cuts `depth` mm into the wall
          - raised:   union() adds `depth` mm protruding from the wall

        For "front (-Y)":  text sits at y=0, extruded in +Y (into model)
        For "back (+Y)":   text sits at y=0, extruded in -Y (into model)
        For "left (-X)":   text sits at x=0, extruded in +X
        For "right (+X)":  text sits at x=0, extruded in -X

        The user positions the label on the wall using Z offset (height) and
        lateral offset (slide along the face).
        """
        safe_text = label_text.replace("\\", "\\\\").replace('"', '\\"')

        # Face config: rotation to orient text in the face's plane, and
        # translate components.  After rotation the text's local +Z aims
        # INTO the model (for recessed) or needs to be flipped for raised.
        #
        # OpenSCAD text() lives in XY, linear_extrude goes along +Z.
        # rotate([90,0,0]) maps local +Z → world -Y.
        # We want +Z → +Y (into model at front face), so rotate([-90,0,0]).
        face_cfg = {
            #                         rotation             tx              ty              tz
            "front (-Y)": {"rot": [-90, 0, 0],  "tx": lateral_off, "ty": 0,           "tz": z_off},
            "back (+Y)":  {"rot": [90, 0, 0],   "tx": lateral_off, "ty": 0,           "tz": z_off},
            "left (-X)":  {"rot": [0, 90, 0],   "tx": 0,           "ty": lateral_off, "tz": z_off},
            "right (+X)": {"rot": [0, -90, 0],  "tx": 0,           "ty": lateral_off, "tz": z_off},
        }
        cfg = face_cfg.get(face, face_cfg["front (-Y)"])
        rx, ry, rz = cfg["rot"]
        tx, ty, tz = cfg["tx"], cfg["ty"], cfg["tz"]

        # Extrude depth: for recessed, cut `depth` mm into the wall.
        # For raised, protrude `depth` mm outward. We handle raised by
        # union-ing only the part of the text slab that is OUTSIDE the
        # original model.
        if mode == "recessed":
            scad = f'''// Auto-generated label wrapper — DesignTool
$fn = 48;

difference() {{
    import("{stl_path.as_posix()}", convexity=10);

    // Text slab: starts at the {face} wall plane, extrudes {depth}mm inward
    translate([{tx}, {ty}, {tz}])
    rotate([{rx}, {ry}, {rz}])
    linear_extrude({depth + 0.01})
        text("{safe_text}", size={size},
             font="Liberation Sans:style=Bold",
             halign="center", valign="center");
}}
'''
        else:  # raised
            scad = f'''// Auto-generated label wrapper — DesignTool
$fn = 48;

union() {{
    import("{stl_path.as_posix()}", convexity=10);

    // Text slab that protrudes {depth}mm from {face} face.
    // We extrude a thick slab inward+outward, then subtract
    // the original model to keep only the protruding part.
    difference() {{
        translate([{tx}, {ty}, {tz}])
        rotate([{rx}, {ry}, {rz}])
        // Extrude from -{depth} (outward) to +20 (deep inside) so the
        // slab definitely spans the wall, then we clip below.
        translate([0, 0, -{depth}])
        linear_extrude({depth + 20})
            text("{safe_text}", size={size},
                 font="Liberation Sans:style=Bold",
                 halign="center", valign="center");

        // Remove everything inside the original solid → only the
        // outward-protruding {depth}mm shell of text remains
        import("{stl_path.as_posix()}", convexity=10);
    }}
}}
'''

        wrapper = stl_path.parent / "_label_wrapper.scad"
        wrapper.write_text(scad)
        return wrapper

    def _log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _start_export(self):
        scad = self.app.selected_scad
        if not scad:
            messagebox.showwarning("No SCAD", "Select a SCAD file in the Browser tab first.")
            return
        if self._exporting:
            return

        # Use the export tab's own preset combo (not the app-wide selection)
        preset = self.preset_var.get()
        if not preset or preset == "(SCAD Defaults)":
            preset = None  # export with SCAD defaults, no -p/-P flags

        openscad = find_openscad()
        if not openscad:
            messagebox.showerror("OpenSCAD Not Found", "openscad is not on PATH.")
            return

        formats = []
        if self.stl_var.get():
            formats.append("stl")
        if self.mf3_var.get():
            formats.append("3mf")
        if not formats:
            messagebox.showwarning("No Format", "Select at least one export format.")
            return

        self._exporting = True
        self.export_btn.config(state=tk.DISABLED)
        self.progress.start(15)

        t = threading.Thread(target=self._do_export,
                             args=(scad, preset, formats, openscad),
                             daemon=True)
        t.start()

    def _do_export(self, scad_path, preset_name, formats, openscad):
        """preset_name is None for SCAD defaults, or a string for a named preset."""
        try:
            ts = datetime.now()
            ts_str = ts.strftime("%Y-%m-%d_%H%M")
            preset_slug = slugify(preset_name) if preset_name else "defaults"
            preset_display = preset_name or "(SCAD Defaults)"
            folder_name = f"{ts_str}_{slugify(scad_path.stem)}__{preset_slug}"
            folder = EXPORTS_DIR / folder_name
            folder.mkdir(parents=True, exist_ok=True)

            self.after(0, lambda: self._log(f"Export folder: {folder.name}"))

            json_path = scad_path.with_suffix(".json")
            presets = load_presets(json_path)
            preset_params = presets.get(preset_name, {}) if preset_name else {}
            defaults = parse_scad_defaults(scad_path)

            # Snapshot SCAD source
            shutil.copy2(scad_path, folder / scad_path.name)
            if json_path.exists():
                shutil.copy2(json_path, folder / json_path.name)
            self.after(0, lambda: self._log("Copied SCAD + JSON snapshot"))

            # Read label settings (from UI thread vars, safe because they don't change mid-export)
            embed_label = self.label_enabled_var.get()
            label_text = self.label_text_var.get().strip()
            if embed_label and (not label_text or label_text == "(auto: filename)"):
                label_text = scad_path.stem
            label_size = self.label_size_var.get()
            label_depth = self.label_depth_var.get()
            label_mode = self.label_mode_var.get()
            label_face = self.label_face_var.get()
            label_z = self.label_z_var.get()
            label_lateral = self.label_lateral_var.get()

            # Build base OpenSCAD command (with or without preset flags)
            def _scad_cmd(output_path, source=None):
                src = source or scad_path
                cmd = [openscad, "-o", str(output_path)]
                if source is None and preset_name and json_path.exists():
                    cmd.extend(["-p", str(json_path), "-P", preset_name])
                cmd.append(str(src))
                return cmd

            if embed_label:
                # Two-pass: first export a plain STL, then wrap it with the label
                plain_stl = folder / f"_plain_{scad_path.stem}.stl"
                self.after(0, lambda: self._log("Pass 1: Rendering plain STL for label..."))
                cmd = _scad_cmd(plain_stl)
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    err = (result.stderr or "")[-300:]
                    self.after(0, lambda e=err: self._log(f"Plain STL FAILED: {e}"))
                    raise RuntimeError("Label pass 1 failed")

                self.after(0, lambda: self._log(f"Pass 2: Adding {label_mode} label \"{label_text}\"..."))
                wrapper = self._generate_label_wrapper(
                    plain_stl, label_text, label_size, label_depth,
                    label_mode, label_face, label_z, label_lateral)

                for fmt in formats:
                    if fmt == "FCStd":
                        continue
                    out_file = folder / f"{scad_path.stem}.{fmt}"
                    cmd = _scad_cmd(out_file, source=wrapper)
                    self.after(0, lambda f=fmt: self._log(f"Rendering labeled {f.upper()}..."))
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        err = (result.stderr or "")[-300:]
                        self.after(0, lambda e=err, f=fmt: self._log(f"{f.upper()} FAILED: {e}"))
                    else:
                        size = out_file.stat().st_size / 1024
                        self.after(0, lambda f=fmt, s=size: self._log(f"{f.upper()} done ({s:.1f} KB)"))

                # Clean up intermediate files
                try:
                    plain_stl.unlink()
                    wrapper.unlink()
                except OSError:
                    pass
            else:
                # Single-pass: normal export
                for fmt in formats:
                    if fmt == "FCStd":
                        continue
                    out_file = folder / f"{scad_path.stem}.{fmt}"
                    cmd = _scad_cmd(out_file)
                    self.after(0, lambda f=fmt: self._log(f"Rendering {f.upper()}..."))
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode != 0:
                        err = (result.stderr or "")[-300:]
                        self.after(0, lambda e=err, f=fmt: self._log(f"{f.upper()} FAILED: {e}"))
                    else:
                        size = out_file.stat().st_size / 1024
                        self.after(0, lambda f=fmt, s=size: self._log(f"{f.upper()} done ({s:.1f} KB)"))

            # Generate description.md
            desc_text = generate_description_md(
                scad_path, preset_display, preset_params or defaults, defaults,
                formats, ts.strftime("%Y-%m-%d %H:%M:%S"))
            if embed_label:
                desc_text += (
                    f"\n## Embedded Label\n\n"
                    f"- **Text:** `{label_text}`\n"
                    f"- **Mode:** {label_mode}\n"
                    f"- **Size:** {label_size} mm\n"
                    f"- **Depth:** {label_depth} mm\n"
                    f"- **Face:** {label_face}\n"
                    f"- **Z offset:** {label_z} mm\n"
                    f"- **Lateral offset:** {label_lateral} mm\n"
                )
            user_desc = self.desc_entry.get().strip()
            if user_desc:
                desc_text += f"\n## Notes\n\n{user_desc}\n"
            (folder / "description.md").write_text(desc_text)

            # Append to history
            history_entry = {
                "timestamp": ts.isoformat(),
                "scad": str(scad_path.relative_to(PROJECT_ROOT)),
                "preset": preset_display,
                "formats": formats,
                "folder": str(folder.relative_to(TOOL_DIR)),
                "params": preset_params or defaults,
            }
            if embed_label:
                history_entry["label"] = {
                    "text": label_text, "mode": label_mode,
                    "size": label_size, "depth": label_depth,
                    "face": label_face, "z_offset": label_z,
                    "lateral_offset": label_lateral,
                }
            append_history(history_entry)

            self.after(0, lambda: self._log(f"Export complete: {folder.name}"))
            self.after(0, lambda: self.app.log(f"[export] {folder.name}"))

            # Refresh history tab
            if hasattr(self.app, "history_tab"):
                self.after(0, self.app.history_tab.refresh)

        except subprocess.TimeoutExpired:
            self.after(0, lambda: self._log("Export timed out (5 min limit)"))
        except Exception as e:
            self.after(0, lambda: self._log(f"Error: {e}"))
        finally:
            self.after(0, lambda: self.progress.stop())
            self.after(0, lambda: self.export_btn.config(state=tk.NORMAL))
            self._exporting = False


# ─────────────────────────────────────────────────────────────────────────────
# Tab 4: 3D Preview
# ─────────────────────────────────────────────────────────────────────────────

class PreviewTab(ttk.Frame):
    """Render 3D previews via OpenSCAD CLI and display as images."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._render_timer = None
        self._preview_photo = None
        self._ortho_photos = {}
        self._build_ui()

    def _build_ui(self):
        # Controls
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(ctrl_frame, text="Rot X:").pack(side=tk.LEFT, padx=(0, 3))
        self.rx_var = tk.DoubleVar(value=55)
        ttk.Scale(ctrl_frame, from_=0, to=360, variable=self.rx_var, orient=tk.HORIZONTAL,
                  length=120, command=self._on_slider).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(ctrl_frame, text="Rot Z:").pack(side=tk.LEFT, padx=(0, 3))
        self.rz_var = tk.DoubleVar(value=25)
        ttk.Scale(ctrl_frame, from_=0, to=360, variable=self.rz_var, orient=tk.HORIZONTAL,
                  length=120, command=self._on_slider).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(ctrl_frame, text="Dist:").pack(side=tk.LEFT, padx=(0, 3))
        self.dist_var = tk.DoubleVar(value=200)
        ttk.Scale(ctrl_frame, from_=50, to=500, variable=self.dist_var, orient=tk.HORIZONTAL,
                  length=120, command=self._on_slider).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(ctrl_frame, text="Render", command=self._render_main).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="Reset", command=self._reset_camera).pack(side=tk.LEFT, padx=5)

        # Quick view buttons
        quick_frame = ttk.Frame(self)
        quick_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        for name in ORTHO_CAMERAS:
            ttk.Button(quick_frame, text=name, width=7,
                       command=lambda n=name: self._quick_view(n)).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_frame, text="All Ortho", command=self._render_all_ortho).pack(side=tk.RIGHT, padx=5)

        # Main content: preview + ortho thumbnails
        content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Main preview
        preview_frame = ttk.Frame(content)
        content.add(preview_frame, weight=3)
        self.preview_label = tk.Label(preview_frame, bg=BG_CANVAS, text="Select a SCAD and click Render",
                                       fg=FG_DIM, font=("JetBrains Mono", 12))
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Ortho thumbnails
        ortho_frame = ttk.LabelFrame(content, text="Orthographic Views", padding=4)
        content.add(ortho_frame, weight=1)
        self._ortho_labels = {}
        for i, name in enumerate(ORTHO_CAMERAS):
            f = ttk.Frame(ortho_frame)
            f.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="nsew")
            ttk.Label(f, text=name, font=("JetBrains Mono", 8)).pack()
            lbl = tk.Label(f, bg=BG_DARK, width=22, height=8, text="---", fg=FG_DIM)
            lbl.pack(fill=tk.BOTH, expand=True)
            self._ortho_labels[name] = lbl
        for i in range(3):
            ortho_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            ortho_frame.grid_columnconfigure(i, weight=1)

    def _on_slider(self, *_):
        if self._render_timer:
            self.after_cancel(self._render_timer)
        self._render_timer = self.after(600, self._render_main)

    def _reset_camera(self):
        self.rx_var.set(55)
        self.rz_var.set(25)
        self.dist_var.set(200)

    def _quick_view(self, name):
        cam = ORTHO_CAMERAS[name]
        self.rx_var.set(cam[3])
        self.rz_var.set(cam[5])
        # Main preview uses rx/rz sliders but quick view renders directly
        # with the full camera tuple for accuracy
        self._render_with_camera(cam)

    def _render_with_camera(self, cam):
        """Render the main preview with a specific (tx,ty,tz,rx,ry,rz) camera tuple."""
        scad = self.app.selected_scad
        if not scad:
            return
        openscad = find_openscad()
        if not openscad:
            return

        dist = self.dist_var.get()
        self.preview_label.config(text="Rendering...", image="")

        def _do():
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            camera = f"{cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},{dist}"
            cmd = [openscad, "--render", f"--camera={camera}",
                   "--imgsize=800,600", "--colorscheme=Tomorrow Night",
                   "--viewall", "--view=axes,scales,crosshairs",
                   "-o", tmp.name]
            preset = self.app.selected_preset
            json_path = scad.with_suffix(".json")
            if preset and json_path.exists():
                cmd.extend(["-p", str(json_path), "-P", preset])
            cmd.append(str(scad))
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and Path(tmp.name).stat().st_size > 0:
                self.after(0, lambda: self._show_preview(tmp.name))
            else:
                self.after(0, lambda: self.preview_label.config(text="Render failed", image=""))

        threading.Thread(target=_do, daemon=True).start()

    def _render_main(self):
        scad = self.app.selected_scad
        if not scad:
            return
        openscad = find_openscad()
        if not openscad:
            return

        rx = self.rx_var.get()
        rz = self.rz_var.get()
        dist = self.dist_var.get()

        self.preview_label.config(text="Rendering...", image="")
        self.app.log(f"[preview] Rendering ({rx:.0f}, {rz:.0f}, {dist:.0f})...")

        def _do():
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            camera = f"0,0,0,{rx},0,{rz},{dist}"
            cmd = [openscad, "--render", f"--camera={camera}",
                   "--imgsize=800,600", "--colorscheme=Tomorrow Night",
                   "--viewall", "--view=axes,scales,crosshairs",
                   "-o", tmp.name]

            # Add preset if selected
            preset = self.app.selected_preset
            json_path = scad.with_suffix(".json")
            if preset and json_path.exists():
                cmd.extend(["-p", str(json_path), "-P", preset])

            cmd.append(str(scad))
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0 and Path(tmp.name).stat().st_size > 0:
                self.after(0, lambda: self._show_preview(tmp.name))
            else:
                self.after(0, lambda: self.preview_label.config(text="Render failed", image=""))
                err = (result.stderr or "")[-200:]
                self.after(0, lambda: self.app.log(f"[preview] Failed: {err}"))

        threading.Thread(target=_do, daemon=True).start()

    def _show_preview(self, png_path):
        try:
            self._preview_photo = tk.PhotoImage(file=png_path)
            self.preview_label.config(image=self._preview_photo, text="")
        except Exception as e:
            self.preview_label.config(text=f"Load error: {e}", image="")
        finally:
            try:
                os.unlink(png_path)
            except OSError:
                pass

    def _render_all_ortho(self):
        scad = self.app.selected_scad
        if not scad:
            return
        openscad = find_openscad()
        if not openscad:
            return

        self.app.log("[preview] Rendering 6 orthographic views...")

        def _do():
            for name, cam in ORTHO_CAMERAS.items():
                self.after(0, lambda n=name: self._ortho_labels[n].config(text="..."))
                tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                tmp.close()
                camera = f"{cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},200"
                cmd = [openscad, "--render", f"--camera={camera}",
                       "--imgsize=300,225", "--projection=o",
                       "--colorscheme=Tomorrow Night", "--viewall",
                       "--view=axes,scales",
                       "-o", tmp.name]

                preset = self.app.selected_preset
                json_path = scad.with_suffix(".json")
                if preset and json_path.exists():
                    cmd.extend(["-p", str(json_path), "-P", preset])
                cmd.append(str(scad))

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0 and Path(tmp.name).stat().st_size > 0:
                    self.after(0, lambda n=name, p=tmp.name: self._show_ortho(n, p))
                else:
                    self.after(0, lambda n=name: self._ortho_labels[n].config(text="fail"))

            self.after(0, lambda: self.app.log("[preview] Ortho views complete"))

        threading.Thread(target=_do, daemon=True).start()

    def _show_ortho(self, name, png_path):
        try:
            photo = tk.PhotoImage(file=png_path)
            # Subsample for thumbnail
            w, h = photo.width(), photo.height()
            factor = max(1, w // 160)
            thumb = photo.subsample(factor, factor)
            self._ortho_photos[name] = thumb  # prevent GC
            self._ortho_labels[name].config(image=thumb, text="")
        except Exception:
            self._ortho_labels[name].config(text="err")
        finally:
            try:
                os.unlink(png_path)
            except OSError:
                pass

    def refresh_for_scad(self, scad_path):
        self.preview_label.config(text=f"Ready: {scad_path.name}\nClick Render", image="")

    def refresh_for_preset(self, preset_name):
        pass  # Could auto-render here if desired


# ─────────────────────────────────────────────────────────────────────────────
# Tab 5: History / Evolution
# ─────────────────────────────────────────────────────────────────────────────

class HistoryTab(ttk.Frame):
    """View export history and diff between past exports."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # History list
        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=2)

        cols = ("date", "scad", "preset", "formats")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("date", text="Date")
        self.tree.heading("scad", text="SCAD")
        self.tree.heading("preset", text="Preset")
        self.tree.heading("formats", text="Formats")
        self.tree.column("date", width=140)
        self.tree.column("scad", width=200)
        self.tree.column("preset", width=180)
        self.tree.column("formats", width=100)

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Detail panel
        detail_frame = ttk.Frame(paned)
        paned.add(detail_frame, weight=3)

        btn_row = ttk.Frame(detail_frame)
        btn_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Button(btn_row, text="Open Folder", command=self._open_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="Diff with Previous", command=self._diff_previous).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="Refresh", command=self.refresh).pack(side=tk.RIGHT, padx=5)

        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, bg=BG_DARK, fg=FG_TEXT,
                                    font=("JetBrains Mono", 10), state=tk.DISABLED,
                                    padx=10, pady=10)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        self.detail_text.tag_configure("changed", foreground=FG_YELLOW)
        self.detail_text.tag_configure("header", foreground=FG_ACCENT, font=("JetBrains Mono", 11, "bold"))

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        history = load_history()
        for i, entry in enumerate(reversed(history)):
            ts = entry.get("timestamp", "")[:16].replace("T", " ")
            scad = Path(entry.get("scad", "")).name
            preset = entry.get("preset", "")
            fmts = ", ".join(entry.get("formats", []))
            self.tree.insert("", tk.END, values=(ts, scad, preset, fmts),
                             tags=(str(len(history) - 1 - i),))

    def _get_selected_entry(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        tags = self.tree.item(sel[0], "tags")
        idx = int(tags[0]) if tags else -1
        history = load_history()
        if 0 <= idx < len(history):
            return idx, history[idx]
        return None, None

    def _on_select(self, event=None):
        idx, entry = self._get_selected_entry()
        if not entry:
            return

        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)

        folder = TOOL_DIR / entry.get("folder", "")
        desc_file = folder / "description.md"
        if desc_file.exists():
            self.detail_text.insert(tk.END, desc_file.read_text())
        else:
            self.detail_text.insert(tk.END, f"Folder: {entry.get('folder', '?')}\n")
            self.detail_text.insert(tk.END, f"SCAD: {entry.get('scad', '?')}\n")
            self.detail_text.insert(tk.END, f"Preset: {entry.get('preset', '?')}\n")

        self.detail_text.configure(state=tk.DISABLED)

    def _open_folder(self):
        idx, entry = self._get_selected_entry()
        if not entry:
            return
        folder = TOOL_DIR / entry.get("folder", "")
        if folder.is_dir():
            subprocess.Popen(["xdg-open", str(folder)])

    def _diff_previous(self):
        idx, entry = self._get_selected_entry()
        if not entry:
            return

        history = load_history()
        scad_name = Path(entry.get("scad", "")).name

        # Find previous export of same SCAD
        prev = None
        for i in range(idx - 1, -1, -1):
            if Path(history[i].get("scad", "")).name == scad_name:
                prev = history[i]
                break

        if not prev:
            messagebox.showinfo("No Previous", f"No earlier export found for {scad_name}")
            return

        current_params = entry.get("params", {})
        prev_params = prev.get("params", {})
        diffs = diff_params(prev_params, current_params)

        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END,
            f"Diff: {prev.get('preset', '?')} ({prev.get('timestamp', '')[:10]}) "
            f"-> {entry.get('preset', '?')} ({entry.get('timestamp', '')[:10]})\n\n", "header")

        for name, status, base_val, other_val in diffs:
            if status == "changed":
                self.detail_text.insert(tk.END, f"  {name}: {base_val} -> {other_val}\n", "changed")
            elif status == "added":
                self.detail_text.insert(tk.END, f"  + {name}: {other_val}\n", "changed")
            elif status == "removed":
                self.detail_text.insert(tk.END, f"  - {name}: {base_val}\n", "changed")

        self.detail_text.configure(state=tk.DISABLED)


# ─────────────────────────────────────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────────────────────────────────────

class DilderDesignTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1200x800")
        self.minsize(1000, 650)
        self.configure(bg=BG_DARK)

        self.selected_scad = None
        self.selected_preset = None

        self._apply_theme()
        self._build_ui()

    def _apply_theme(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=BG_PANEL, foreground=FG_TEXT,
                        font=("JetBrains Mono", 10))
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_DARK, foreground=FG_DIM,
                        padding=[12, 4])
        style.map("TNotebook.Tab",
                  background=[("selected", BG_PANEL)],
                  foreground=[("selected", FG_ACCENT)])
        style.configure("TFrame", background=BG_PANEL)
        style.configure("TLabel", background=BG_PANEL, foreground=FG_TEXT)
        style.configure("TButton", background=BG_DARK, foreground=FG_TEXT)
        style.configure("TLabelframe", background=BG_PANEL, foreground=FG_ACCENT)
        style.configure("TLabelframe.Label", background=BG_PANEL, foreground=FG_ACCENT)
        style.configure("TCheckbutton", background=BG_PANEL, foreground=FG_TEXT)
        style.configure("TCombobox", fieldbackground=BG_DARK, background=BG_DARK,
                        foreground=FG_TEXT, selectbackground=FG_ACCENT,
                        selectforeground=BG_DARK, arrowcolor=FG_TEXT)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG_DARK)],
                  foreground=[("readonly", FG_TEXT)])
        style.configure("Treeview", background=BG_DARK, foreground=FG_TEXT,
                        fieldbackground=BG_DARK, font=("JetBrains Mono", 10))
        style.configure("Treeview.Heading", background=BG_PANEL, foreground=FG_ACCENT,
                        font=("JetBrains Mono", 10, "bold"))
        style.map("Treeview", background=[("selected", FG_ACCENT)],
                  foreground=[("selected", BG_DARK)])

    def _build_ui(self):
        # Main paned: notebook + log
        paned = tk.PanedWindow(self, orient=tk.VERTICAL, bg=BG_DARK,
                                sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        # Notebook
        self.notebook = ttk.Notebook(paned)
        paned.add(self.notebook, stretch="always")

        self.browser_tab = ScadBrowserTab(self.notebook, self)
        self.notebook.add(self.browser_tab, text="  Browser  ")

        self.preset_tab = PresetManagerTab(self.notebook, self)
        self.notebook.add(self.preset_tab, text="  Presets & Diff  ")

        self.export_tab = ExportTab(self.notebook, self)
        self.notebook.add(self.export_tab, text="  Export  ")

        self.preview_tab = PreviewTab(self.notebook, self)
        self.notebook.add(self.preview_tab, text="  3D Preview  ")

        self.history_tab = HistoryTab(self.notebook, self)
        self.notebook.add(self.history_tab, text="  History  ")

        # Log panel
        log_frame = ttk.Frame(paned)
        paned.add(log_frame, stretch="never")

        log_bar = ttk.Frame(log_frame)
        log_bar.pack(fill=tk.X)
        ttk.Label(log_bar, text="Log", font=("JetBrains Mono", 9, "bold"),
                  foreground=FG_ACCENT).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_bar, text="Clear", command=self._clear_log).pack(side=tk.RIGHT, padx=5)

        self.log_text = tk.Text(log_frame, height=5, wrap=tk.WORD, bg=BG_DARK,
                                 fg=FG_DIM, font=("JetBrains Mono", 9), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

    def log(self, msg):
        if not hasattr(self, "log_text"):
            return  # log panel not built yet (during tab init)
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def set_active_scad(self, scad_path):
        self.selected_scad = scad_path
        self.selected_preset = None
        self.log(f"[scad] Active: {scad_path.name}")
        self.preset_tab.refresh_for_scad(scad_path)
        self.export_tab.refresh_for_scad(scad_path)
        self.preview_tab.refresh_for_scad(scad_path)

    def set_active_preset(self, preset_name):
        self.selected_preset = preset_name
        self.log(f"[preset] Active: {preset_name}")
        self.export_tab.refresh_for_preset(preset_name)
        self.preview_tab.refresh_for_preset(preset_name)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import signal
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    app = DilderDesignTool()
    app.mainloop()


if __name__ == "__main__":
    main()
