#!/usr/bin/env python3
"""
Export an OpenSCAD customizer preset to 3MF without baking the values
back into the SCAD source.

Same SCAD/preset discovery as `bake-preset.py` (only lists SCADs that
have a sidecar `<scadname>.json` with `parameterSets`). Pick a SCAD →
pick a preset → script invokes OpenSCAD with `-p <json> -P <preset>` and
writes `<scadname>__<preset>.3mf` next to the SCAD.

Usage
-----
    python3 export-preset.py                         # interactive menu
    python3 export-preset.py <scad> <preset>         # one-shot export
    python3 export-preset.py <scad> <preset> -o OUT  # custom output path
    python3 export-preset.py --list                  # list SCADs + presets
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def load_presets(json_path: Path) -> dict:
    if not json_path.exists():
        sys.exit(f"error: no preset JSON next to {json_path.name} — did you save a preset in OpenSCAD's customizer?")
    data = json.loads(json_path.read_text())
    return data.get("parameterSets", {})


def collect_scads_with_presets(root: Path) -> list:
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


def prompt_choice(prompt: str, options: list, fmt=lambda o: str(o)) -> "int|None":
    if not options:
        return None
    while True:
        print()
        for i, opt in enumerate(options, start=1):
            print(f"  [{i:>2}] {fmt(opt)}")
        print(f"  [ q] quit")
        raw = input(f"\n{prompt} ").strip().lower()
        if raw in ("q", "quit", "exit", ""):
            return None
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return idx
        except ValueError:
            pass
        print(f"  ? '{raw}' isn't a valid choice")


def slugify(name: str) -> str:
    """Make a preset name filename-safe."""
    s = re.sub(r"[^\w\-.]+", "_", name).strip("_")
    return s or "preset"


def default_output_path(scad_path: Path, preset_name: str) -> Path:
    return scad_path.with_name(f"{scad_path.stem}__{slugify(preset_name)}.3mf")


def export(scad_path: Path, preset_name: str, output_path: "Path|None" = None) -> Path:
    json_path = scad_path.with_suffix(".json")
    presets = load_presets(json_path)
    if preset_name not in presets:
        print(f"error: preset '{preset_name}' not found in {json_path.name}.")
        if presets:
            print("Available presets:")
            for name in presets:
                print(f"  - {name}")
        sys.exit(1)

    out = output_path or default_output_path(scad_path, preset_name)
    openscad = shutil.which("openscad") or shutil.which("openscad-nightly")
    if not openscad:
        sys.exit("error: 'openscad' not found on PATH")

    cmd = [
        openscad,
        "-o", str(out),
        "-p", str(json_path),
        "-P", preset_name,
        str(scad_path),
    ]
    print(f"running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"openscad exited with {result.returncode}")
    print(f"\nwrote {out}")
    return out


def interactive_menu(root: Path) -> None:
    found = collect_scads_with_presets(root)
    if not found:
        print(f"No SCAD files with customizer presets under {root}.")
        print("Save a preset in OpenSCAD's customizer panel first, then re-run.")
        return

    print(f"\n=== export-preset interactive ({len(found)} SCAD file(s) with presets under {root}) ===")

    scad_idx = prompt_choice(
        "Pick a SCAD file (number, or q to quit):",
        found,
        fmt=lambda item: f"{item[0].relative_to(root)}  ({len(item[1])} preset(s))",
    )
    if scad_idx is None:
        return
    scad_path, preset_names = found[scad_idx]

    preset_idx = prompt_choice(
        f"Pick a preset to export from '{scad_path.name}' (number, or q to quit):",
        preset_names,
    )
    if preset_idx is None:
        return
    preset_name = preset_names[preset_idx]

    out = default_output_path(scad_path, preset_name)
    confirm_idx = prompt_choice(
        f"Export '{preset_name}' → {out.name}?",
        ["yes, export", "no, cancel"],
    )
    if confirm_idx != 0:
        return

    print()
    export(scad_path, preset_name, out)


def list_scads_with_presets(root: Path) -> None:
    found = collect_scads_with_presets(root)
    print(f"SCAD files with customizer presets under {root}:\n")
    if not found:
        print("  (none — save a preset in OpenSCAD's customizer panel first)")
        return
    for scad, presets in found:
        print(f"  {scad.relative_to(root)}")
        for name in presets:
            print(f"      preset: {name}")
        print()
    print("Run with a path + preset to export, OR with --menu for an interactive picker:")
    print(f'  python3 {Path(__file__).name} "<scad-path>" "<preset-name>"')
    print(f'  python3 {Path(__file__).name} --menu')


def main():
    p = argparse.ArgumentParser(
        description="Export an OpenSCAD customizer preset to a 3MF file (preset name appended to filename).",
        epilog="With no arguments, drops into an interactive menu that walks SCAD → preset → confirm.",
    )
    p.add_argument("scad", type=Path, nargs="?",
                   help="path to the .scad file (the .json sits next to it). Omit for menu.")
    p.add_argument("preset", nargs="?",
                   help="preset name to export (omit to list available presets)")
    p.add_argument("-o", "--output", type=Path,
                   help="output 3MF path (defaults to <scadstem>__<preset>.3mf next to the SCAD)")
    p.add_argument("--menu", "-m", action="store_true", help="force interactive menu")
    p.add_argument("--list", "-l", action="store_true", help="list SCADs + presets and exit")
    args = p.parse_args()

    if args.menu or (args.scad is None and not args.list):
        interactive_menu(Path.cwd())
        return

    if args.list or args.scad is None:
        list_scads_with_presets(Path.cwd())
        return

    scad_path = args.scad.expanduser().resolve()
    if not scad_path.exists():
        sys.exit(f"error: {scad_path} does not exist")

    if args.preset is None:
        presets = load_presets(scad_path.with_suffix(".json"))
        if not presets:
            print("(no presets in JSON)")
        else:
            print("Available presets:")
            for name in presets:
                print(f"  - {name}")
        return

    export(scad_path, args.preset, args.output)


if __name__ == "__main__":
    main()
