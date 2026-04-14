#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# CollisionDetector – Ubuntu cross-build script
# Produces a Windows .exe using the cdrx/pyinstaller-windows Docker image,
# which bundles Wine + Python for Windows + PyInstaller internally.
#
# Requirements: Docker must be installed and running.
# Output:       dist/windows/CollisionDetector.exe
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="dist/windows/CollisionDetector.exe"

echo "============================================"
echo " CollisionDetector - Ubuntu Build Script"
echo "============================================"
echo

# ── Check Docker ──────────────────────────────────────────────────────────────
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not in PATH."
    echo
    echo "Install Docker with:"
    echo "  sudo apt update && sudo apt install -y docker.io"
    echo "  sudo usermod -aG docker \$USER   # then log out and back in"
    echo
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running."
    echo "Start it with:  sudo systemctl start docker"
    echo
    exit 1
fi

echo "Docker found: $(docker --version)"
echo

# ── Build ─────────────────────────────────────────────────────────────────────
echo "[1/2] Running PyInstaller inside Wine container..."
echo "      (First run will pull the image – this may take a few minutes)"
echo

docker run --rm \
    -v "${SCRIPT_DIR}:/src/" \
    cdrx/pyinstaller-windows \
    "pyinstaller --onefile --windowed --name CollisionDetector collision_detector.py"

# ── Cleanup ───────────────────────────────────────────────────────────────────
echo
echo "[2/2] Cleaning up build artefacts..."
rm -rf "${SCRIPT_DIR}/build"
rm -f  "${SCRIPT_DIR}/CollisionDetector.spec"

# ── Done ──────────────────────────────────────────────────────────────────────
echo
echo "============================================"
echo " Build successful!"
echo " Output: ${SCRIPT_DIR}/${OUTPUT}"
echo "============================================"
