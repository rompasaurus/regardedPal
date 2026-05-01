# Design Tracker

CLI tool for tracking FreeCAD design iterations, print history, and snapshot comparisons.

## Usage

```bash
python3 tools/design-tracker/design-tracker.py           # interactive menu
python3 tools/design-tracker/design-tracker.py status     # current state
python3 tools/design-tracker/design-tracker.py snap "msg" # take snapshot
python3 tools/design-tracker/design-tracker.py log        # timeline
python3 tools/design-tracker/design-tracker.py diff 1 3   # compare snapshots
python3 tools/design-tracker/design-tracker.py naming     # naming guide
```

## Features

- **Status** — file counts, newest model, uncommitted changes
- **Snapshot** — bookmark current state with FCStd backup
- **Timeline** — chronological history of snapshots and prints
- **Print log** — record what was printed and whether it worked
- **Compare** — diff two snapshots (hashes, counts, renders)
- **Naming guide** — recommended file naming convention

## Data

Stored in `tools/design-tracker/.design-tracker/`:
- `history.json` — all snapshots and prints
- `snapshots/snap-NNNN/` — FCStd backups
