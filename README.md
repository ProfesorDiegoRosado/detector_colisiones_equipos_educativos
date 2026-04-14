# Collision Detector — Equipos Educativos

Desktop tool that detects **shared teachers between class groups** across all levels of a school. When a teacher appears in more than one group, that counts as a collision between those two groups. Results are displayed grouped by the number of collisions, from fewest to most.

---

## Features

- Load any `equipos_educativos.json` file via a file-browser dialog.
- Automatically computes every pair of groups (level + letter) and finds shared teachers.
- Results grouped in a collapsible tree: **Sin colisiones**, **1 colisión**, **2 colisiones**, etc.
- Click any pair to see exactly which teachers are causing the collision.
- Resizable split-pane layout (collision list on the left, detail panel on the right).
- Teacher names are whitespace-normalised on load to avoid false mismatches.

---

## Input format

The app expects a JSON file structured as an array of level objects, each containing a `groups` map. Each group holds a `teachers` array with `name` and `subject` fields.

```json
[
  {
    "level": "1º de E.S.O.",
    "groups": {
      "A": {
        "teachers": [
          { "name": "Apellido, Nombre", "subject": ["Matemáticas"] },
          ...
        ]
      },
      "B": { "teachers": [ ... ] }
    }
  },
  ...
]
```

---

## Project structure

```
evaluaciones_tool/
├── collision_detector.py       # Entry point — 3 lines, just launches the GUI
├── src/
│   ├── core.py                 # Business logic: load_json(), compute_collisions()
│   └── ui/
│       └── app.py              # tkinter GUI — imports only from src.core
├── requirements.txt            # No third-party deps — stdlib only
├── build_windows.bat           # Build script for Windows
├── build_ubuntu.sh             # Build script for Ubuntu (requires Docker)
├── .venv/                      # Local Python virtual environment
└── input/
    └── equipos_educativos.json # Sample input file
```

The `src/core.py` module has **zero UI imports** — a future CLI entry point can use it directly without touching any other file:

```python
# Example: future cli.py
from src.core import load_json, compute_collisions
```

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or newer |
| tkinter | Included with the standard Python installer |

No third-party packages are needed to **run** the app.  
[PyInstaller](https://pyinstaller.org/) is only needed to **build** the `.exe` (the build scripts install it automatically).

---

## Running the app (development)

### 1. Create and activate the virtual environment

**Ubuntu / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (CMD)**
```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Run the app

```bash
python collision_detector.py
```

### 3. Load a data file

Click **Cargar JSON** and select an `equipos_educativos.json` file.

---

## Building the Windows executable

### On Windows

> **Prerequisite:** Python 3.10+ installed and added to `PATH`.  
> Download from [python.org/downloads](https://www.python.org/downloads/) — check *"Add Python to PATH"* during setup.

Open **CMD** (not PowerShell) in the project folder and run:

```bat
build_windows.bat
```

The script will:
1. Verify Python is available.
2. Install / upgrade **PyInstaller** via `pip`.
3. Bundle the app into a single executable.
4. Clean up build artefacts.

**Output:** `dist\CollisionDetector.exe`

---

### On Ubuntu (cross-compile for Windows)

> **Prerequisite:** Docker installed and running.

```bash
# Install Docker if needed
sudo apt update && sudo apt install -y docker.io
sudo usermod -aG docker $USER   # log out and back in after this

# Run the build
./build_ubuntu.sh
```

The script uses the [`cdrx/pyinstaller-windows`](https://github.com/cdrx/docker-pyinstaller) Docker image, which bundles Wine + Python for Windows + PyInstaller. The image is pulled automatically on the first run (~1 GB download, cached afterwards).

**Output:** `dist/windows/CollisionDetector.exe`

> **Note:** The first run downloads the Docker image and may take a few minutes. Subsequent builds are fast.

---

## How collisions are calculated

For every pair of groups `(Level / Group A, Level / Group B)`, the app computes the intersection of their teacher sets. Each shared teacher counts as **one collision**. Pairs are then grouped by their total collision count.

**Example:**  
If `1º de E.S.O. / A` and `1º de E.S.O. / B` share 3 teachers, they appear under **3 colisiones** and clicking the pair shows those 3 teacher names.
