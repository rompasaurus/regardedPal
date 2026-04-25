#!/usr/bin/env python3
"""
OpenSCAD to 3MF exporter with menu and file browser.

Usage:
    python3 scad-export.py
    python3 scad-export.py --file middle-plate.scad --output middle.3mf
"""

import os
import sys
import subprocess
import shutil
import argparse
from datetime import datetime, date
from pathlib import Path

# Default search directories (relative to this script)
SCRIPT_DIR = Path(__file__).resolve().parent
HARDWARE_DIR = SCRIPT_DIR.parent
DEFAULT_SEARCH_DIRS = [SCRIPT_DIR, HARDWARE_DIR]

SUPPORTED_EXPORT_FORMATS = {
    "1": (".3mf", "3MF (recommended)"),
    "2": (".stl", "STL"),
    "3": (".off", "OFF"),
    "4": (".amf", "AMF"),
}


def find_openscad() -> str | None:
    """Locate the openscad binary."""
    return shutil.which("openscad")


def find_scad_files(search_dirs: list[Path]) -> list[Path]:
    """Recursively find all .scad files in the given directories."""
    files = []
    seen = set()
    for d in search_dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.rglob("*.scad")):
            resolved = f.resolve()
            if resolved not in seen:
                seen.add(resolved)
                files.append(resolved)
    return files


def detect_parts(scad_path: Path) -> list[str]:
    """Scan a .scad file for a part selector variable and return available parts."""
    parts = []
    text = scad_path.read_text(errors="replace")
    for line in text.splitlines():
        stripped = line.strip()
        # Look for comments listing parts like: part="base" | "middle" | ...
        if stripped.startswith("//") and "part" in stripped.lower():
            # Extract quoted strings
            import re
            found = re.findall(r'"(\w+)"', stripped)
            if found and len(found) > 1:
                parts = [p for p in found if p != "all"]
                break
    return parts


def print_header(title: str):
    width = 50
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def file_browser(search_dirs: list[Path]) -> Path | None:
    """Interactive file browser for selecting a .scad file."""
    scad_files = find_scad_files(search_dirs)

    if not scad_files:
        print("\n  No .scad files found in:")
        for d in search_dirs:
            print(f"    {d}")
        return None

    # Sort by modification time, most recent first
    scad_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    print_header("Select a .scad file")
    for i, f in enumerate(scad_files, 1):
        try:
            rel = f.relative_to(HARDWARE_DIR)
        except ValueError:
            rel = f.name
        size_kb = f.stat().st_size / 1024
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        time_str = mtime.strftime("%Y-%m-%d %H:%M")
        print(f"  [{i:2d}] {time_str}  {size_kb:6.1f} KB  {rel}")

    print(f"  [c] Enter a custom path")
    print(f"  [q] Quit")
    print()

    while True:
        choice = input("  > ").strip().lower()
        if choice == "q":
            return None
        if choice == "c":
            custom = input("  Path: ").strip()
            p = Path(custom).expanduser().resolve()
            if p.is_file() and p.suffix == ".scad":
                return p
            print("  Not a valid .scad file.")
            continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(scad_files):
                return scad_files[idx]
        except ValueError:
            pass
        print("  Invalid choice.")


def choose_format() -> tuple[str, str]:
    """Let the user pick an export format."""
    print_header("Export format")
    for key, (ext, desc) in SUPPORTED_EXPORT_FORMATS.items():
        print(f"  [{key}] {desc}  ({ext})")
    print()

    while True:
        choice = input("  > ").strip()
        if choice in SUPPORTED_EXPORT_FORMATS:
            return SUPPORTED_EXPORT_FORMATS[choice]
        print("  Invalid choice.")


def choose_output(scad_path: Path, ext: str) -> Path:
    """Choose where to save the exported file."""
    default_name = scad_path.stem + ext
    default_dir = HARDWARE_DIR / "enclosure-prints"
    if not default_dir.is_dir():
        default_dir = scad_path.parent
    default_path = default_dir / default_name

    print_header("Output file")
    print(f"  Default: {default_path}")
    print(f"  [Enter] Use default")
    print(f"  Or type a custom path")
    print()

    choice = input("  > ").strip()
    if not choice:
        return default_path

    p = Path(choice).expanduser().resolve()
    if p.is_dir():
        return p / default_name
    return p


def choose_part(parts: list[str]) -> str | None:
    """If the file has multiple parts, let the user pick one."""
    if not parts:
        return None

    print_header("Select part to export")
    print(f"  [0] All parts (full render)")
    for i, part in enumerate(parts, 1):
        print(f"  [{i}] {part}")
    print()

    while True:
        choice = input("  > ").strip()
        if choice == "0":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(parts):
                return parts[idx]
        except ValueError:
            pass
        print("  Invalid choice.")


def get_extra_params() -> list[str]:
    """Optionally let the user pass -D parameter overrides."""
    print_header("Parameter overrides (optional)")
    print("  Enter OpenSCAD -D overrides, one per line.")
    print("  Examples:  plate_thk=3   or   $fn=96")
    print("  Empty line to finish.")
    print()

    params = []
    while True:
        line = input("  -D ").strip()
        if not line:
            break
        params.extend(["-D", line])
    return params


def run_export(openscad: str, scad_path: Path, output_path: Path,
               part: str | None, extra_params: list[str]):
    """Run the openscad export command."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [openscad]
    if part:
        cmd.extend(["-D", f'part="{part}"'])
    cmd.extend(extra_params)
    cmd.extend(["-o", str(output_path), str(scad_path)])

    print_header("Exporting")
    print(f"  Source:  {scad_path}")
    print(f"  Output:  {output_path}")
    if part:
        print(f"  Part:    {part}")
    print(f"  Command: {' '.join(cmd)}")
    print()
    print("  Rendering... (this may take a moment)")
    print()

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        size = output_path.stat().st_size
        print(f"  Done! Exported {size:,} bytes to:")
        print(f"  {output_path}")
    else:
        print("  Export FAILED.")
        if result.stderr:
            for line in result.stderr.strip().splitlines():
                print(f"    {line}")
    print()
    return result.returncode


def view_todays_models(search_dirs: list[Path]):
    """Show only SCAD files modified today, sorted by modification time."""
    all_files = find_scad_files(search_dirs)
    today = date.today()

    todays_files = []
    for f in all_files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        if mtime.date() == today:
            todays_files.append((f, mtime))

    # Sort by modification time (most recent first)
    todays_files.sort(key=lambda x: x[1], reverse=True)

    print_header(f"SCAD files modified today ({today.isoformat()})")

    if not todays_files:
        print("  No .scad files modified today.")
        print()
        input("  Press Enter to continue...")
        return

    print(f"  {len(todays_files)} file(s) found:\n")
    for i, (f, mtime) in enumerate(todays_files, 1):
        try:
            rel = f.relative_to(HARDWARE_DIR)
        except ValueError:
            rel = f.name
        size_kb = f.stat().st_size / 1024
        time_str = mtime.strftime("%H:%M:%S")
        print(f"  [{i:2d}] {time_str}  {size_kb:6.1f} KB  {rel}")

    print()
    input("  Press Enter to continue...")


def interactive_menu():
    """Main interactive menu loop."""
    openscad = find_openscad()
    if not openscad:
        print("Error: openscad not found. Install it first.")
        print("  Arch/CachyOS: sudo pacman -S openscad")
        print("  Ubuntu/Debian: sudo apt install openscad")
        sys.exit(1)

    while True:
        print_header("OpenSCAD Export Tool")
        print(f"  OpenSCAD: {openscad}")
        print()
        print("  [1] Browse and export a .scad file")
        print("  [2] Batch export all parts from enclosure")
        print("  [3] Quick export (middle-plate.scad -> middle.3mf)")
        print("  [4] View today's SCAD models")
        print("  [q] Quit")
        print()

        choice = input("  > ").strip().lower()

        if choice == "q":
            print("  Bye!")
            break

        elif choice == "1":
            scad_path = file_browser(DEFAULT_SEARCH_DIRS)
            if not scad_path:
                continue

            parts = detect_parts(scad_path)
            part = choose_part(parts) if parts else None

            ext, _ = choose_format()
            output_path = choose_output(scad_path, ext)

            extra = get_extra_params()
            run_export(openscad, scad_path, output_path, part, extra)

            input("  Press Enter to continue...")

        elif choice == "2":
            enclosure = HARDWARE_DIR / "esp32s3-enclosure.scad"
            if not enclosure.is_file():
                print(f"  Not found: {enclosure}")
                continue

            out_dir = HARDWARE_DIR / "enclosure-prints"
            parts = ["base", "middle", "topmid", "cover", "screws"]

            print_header("Batch export — all enclosure parts")
            for part in parts:
                out = out_dir / f"{part}.3mf"
                run_export(openscad, enclosure, out, part, [])

            print("  Batch export complete.")
            input("  Press Enter to continue...")

        elif choice == "3":
            middle = SCRIPT_DIR / "middle-plate.scad"
            if not middle.is_file():
                print(f"  Not found: {middle}")
                continue
            out = HARDWARE_DIR / "enclosure-prints" / "middle.3mf"
            run_export(openscad, middle, out, None, [])
            input("  Press Enter to continue...")

        elif choice == "4":
            view_todays_models(DEFAULT_SEARCH_DIRS)

        else:
            print("  Invalid choice.")


def cli_export(args):
    """Non-interactive export from command line arguments."""
    openscad = find_openscad()
    if not openscad:
        print("Error: openscad not found.")
        sys.exit(1)

    scad_path = Path(args.file).expanduser().resolve()
    if not scad_path.is_file():
        print(f"Error: {scad_path} not found.")
        sys.exit(1)

    output_path = Path(args.output).expanduser().resolve()

    extra = []
    if args.part:
        extra.extend(["-D", f'part="{args.part}"'])
    if args.params:
        for p in args.params:
            extra.extend(["-D", p])

    rc = run_export(openscad, scad_path, output_path, None, extra)
    sys.exit(rc)


def main():
    parser = argparse.ArgumentParser(description="Export OpenSCAD files to 3MF/STL")
    parser.add_argument("--file", "-f", help="Path to .scad file (skip interactive mode)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--part", "-p", help="Part name to export")
    parser.add_argument("--params", "-D", nargs="*", help="OpenSCAD -D overrides")
    args = parser.parse_args()

    if args.file and args.output:
        cli_export(args)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
