#!/usr/bin/env python3
"""
Bake an OpenSCAD customizer preset back into the SCAD source.

OpenSCAD stores customizer presets in `<scadname>.json` and applies them at
render time WITHOUT modifying the source. This script reads a chosen preset
and overwrites every matching parameter declaration in the SCAD file with
the preset's value, so you don't have to manage the JSON or re-enter
numbers manually.

Usage
-----
    python3 bake-preset.py <scad-file>                          # list presets
    python3 bake-preset.py <scad-file> <preset-name>            # bake (with backup)
    python3 bake-preset.py <scad-file> <preset-name> --dry-run  # preview diff

What it changes
---------------
For every parameter in the chosen preset, the script finds a line in the SCAD
that looks like:

    name <whitespace> = <whitespace> <old-value>; [optional // comment]

and replaces `<old-value>` with the preset's value. Comments, whitespace,
and unrelated lines are preserved. If a parameter appears in the JSON but
not in the SCAD, it's skipped with a warning.

Limitations
-----------
- Only top-level numeric / boolean parameters. Vectors and strings work too,
  but multi-line parameter values aren't handled.
- The script assumes one parameter per line. Compound declarations on the
  same line aren't recognized.
- A `.bak` is written next to the SCAD before any changes.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


def load_presets(json_path: Path) -> dict:
    if not json_path.exists():
        sys.exit(f"error: no preset JSON next to {json_path.name} — did you save a preset in OpenSCAD's customizer?")
    data = json.loads(json_path.read_text())
    return data.get("parameterSets", {})


def list_presets(presets: dict) -> None:
    if not presets:
        print("(no presets in JSON)")
        return
    print("Available presets:")
    for name in presets:
        print(f"  - {name}")


def bake(scad_path: Path, preset_name: str, dry_run: bool) -> None:
    json_path = scad_path.with_suffix(".json")
    presets = load_presets(json_path)
    if preset_name not in presets:
        print(f"error: preset '{preset_name}' not found.")
        list_presets(presets)
        sys.exit(1)

    preset = presets[preset_name]
    text = scad_path.read_text()
    lines = text.splitlines(keepends=True)

    # Match a parameter declaration. Capture: (whole line up to value)(value)(rest).
    # Allows leading whitespace, alignment spaces around =, and trailing comments.
    param_re = re.compile(
        r"^(?P<lead>\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*)"
        r"(?P<value>[^;]+?)"
        r"(?P<tail>\s*;.*)$"
    )

    changes = []  # (lineno, name, old, new, line_idx)
    unmatched = set(preset.keys())

    for i, line in enumerate(lines):
        m = param_re.match(line)
        if not m:
            continue
        name = m.group("name")
        if name not in preset:
            continue
        old_value = m.group("value").strip()
        new_value_raw = preset[name]
        # OpenSCAD JSON stores numbers as strings sometimes. Pass them through.
        new_value_str = str(new_value_raw)
        if old_value == new_value_str:
            unmatched.discard(name)
            continue
        new_line = f"{m.group('lead')}{new_value_str}{m.group('tail')}"
        if not new_line.endswith("\n") and line.endswith("\n"):
            new_line += "\n"
        changes.append((i + 1, name, old_value, new_value_str, i))
        lines[i] = new_line
        unmatched.discard(name)

    if not changes:
        print(f"no changes — preset values already match SCAD source.")
        return

    print(f"changes for preset '{preset_name}':")
    for lineno, name, old, new, _ in changes:
        print(f"  line {lineno:>4}: {name}: {old}  →  {new}")
    if unmatched:
        print(f"warning: {len(unmatched)} preset parameter(s) not found in SCAD: {sorted(unmatched)}")

    if dry_run:
        print("\n(dry-run; no files written)")
        return

    backup = scad_path.with_suffix(scad_path.suffix + ".bak")
    shutil.copy2(scad_path, backup)
    scad_path.write_text("".join(lines))
    print(f"\nwrote {scad_path}")
    print(f"backup at {backup}")


def collect_scads_with_presets(root: Path) -> list:
    """Walk `root` and return [(scad_path, [preset_names...])] for every SCAD with savable presets."""
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
    """Show a numbered menu, read user choice, return index or None on quit."""
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


def interactive_menu(root: Path) -> None:
    found = collect_scads_with_presets(root)
    if not found:
        print(f"No SCAD files with customizer presets under {root}.")
        print("Save a preset in OpenSCAD's customizer panel first, then re-run.")
        return

    print(f"\n=== bake-preset interactive ({len(found)} SCAD file(s) with presets under {root}) ===")

    # Step 1 — pick the SCAD
    scad_idx = prompt_choice(
        "Pick a SCAD file (number, or q to quit):",
        found,
        fmt=lambda item: f"{item[0].relative_to(root)}  ({len(item[1])} preset(s))",
    )
    if scad_idx is None:
        return
    scad_path, preset_names = found[scad_idx]

    # Step 2 — pick the preset
    preset_idx = prompt_choice(
        f"Pick a preset to bake into '{scad_path.name}' (number, or q to quit):",
        preset_names,
    )
    if preset_idx is None:
        return
    preset_name = preset_names[preset_idx]

    # Step 3 — dry-run or write
    mode_idx = prompt_choice(
        f"Bake '{preset_name}' into '{scad_path.name}'?",
        ["preview only (--dry-run)", "write changes (writes a .bak alongside)"],
    )
    if mode_idx is None:
        return
    dry_run = (mode_idx == 0)

    print()
    bake(scad_path, preset_name, dry_run)


def list_scads_with_presets(root: Path) -> None:
    """Print scads + presets in non-interactive form (for simple inspection)."""
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
    print("Run with a path + preset name to bake, OR with --menu for an interactive picker:")
    print(f'  python3 {Path(__file__).name} "<scad-path>" "<preset-name>"')
    print(f'  python3 {Path(__file__).name} --menu')


def main():
    p = argparse.ArgumentParser(
        description="Bake an OpenSCAD customizer preset into the .scad source.",
        epilog="With no arguments, drops into an interactive menu that walks you through SCAD → preset → dry-run/write.",
    )
    p.add_argument("scad", type=Path, nargs="?",
                   help="path to the .scad file (the .json sits next to it). Omit to use the menu.")
    p.add_argument("preset", nargs="?",
                   help="preset name to bake (omit to list available presets in this SCAD's JSON)")
    p.add_argument("--dry-run", action="store_true", help="show what would change without writing")
    p.add_argument("--menu", "-m", action="store_true", help="force interactive menu even when args are given")
    p.add_argument("--list", "-l", action="store_true", help="just list SCADs + presets and exit (no menu)")
    args = p.parse_args()

    # Default behavior with no args = interactive menu (was: bare list)
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
        list_presets(load_presets(scad_path.with_suffix(".json")))
        return

    bake(scad_path, args.preset, args.dry_run)


if __name__ == "__main__":
    main()
