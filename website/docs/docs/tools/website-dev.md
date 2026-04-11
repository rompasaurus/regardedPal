# Website Dev CLI

A Python CLI for managing the MkDocs Material documentation site. Handles virtual environment setup, local development server, builds, and deployment — with an interactive menu or direct command invocation.

---

## Usage

```bash
cd website/
python3 dev.py              # interactive arrow-key menu
python3 dev.py <command>    # direct invocation
```

No external dependencies — runs on Python 3.9+ standard library. MkDocs and its dependencies are installed into an isolated virtual environment by the `install` command.

---

## Commands

| Command | Description |
|---------|-------------|
| `install` | Create Python venv and install MkDocs Material + all dependencies |
| `serve` | Start local dev server with hot-reload on `localhost:8000` |
| `build` | Build static site to `site/` directory |
| `deploy` | Deploy to GitHub Pages via `mkdocs gh-deploy` |
| `clean` | Remove the `site/` build output |
| `check` | Verify prerequisites (Python 3.10+, `mkdocs.yml` exists) |
| `status` | Show environment status (venv, installed packages, build state) |

---

## Interactive Menu

Running `dev.py` with no arguments launches an interactive menu with arrow-key navigation:

- **↑ / ↓** — navigate between commands
- **Enter** — execute the selected command
- **q** — quit

Each command shows a description footer and environment status badges. After execution, the menu returns for the next action.

---

## Typical Workflow

```bash
# First time — set up the environment
python3 dev.py install

# Development — edit Markdown, preview live
python3 dev.py serve
# Open http://localhost:8000 in your browser

# Ready to publish
python3 dev.py deploy
```

---

!!! info "Source"
    The script lives at [`website/dev.py`](https://github.com/rompasaurus/dilder/blob/main/website/dev.py). Site configuration is in [`website/mkdocs.yml`](https://github.com/rompasaurus/dilder/blob/main/website/mkdocs.yml).
