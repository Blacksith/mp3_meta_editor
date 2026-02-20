#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements-dev.txt

PYINSTALLER_CONFIG_DIR=".pyinstaller" pyinstaller \
  --noconfirm \
  --windowed \
  --name "MP3 Meta Editor" \
  app.py

cd dist
rm -f "MP3 Meta Editor-macOS.zip"
zip -r "MP3 Meta Editor-macOS.zip" "MP3 Meta Editor.app"

echo "Build complete: $(pwd)/MP3 Meta Editor.app"
echo "Archive: $(pwd)/MP3 Meta Editor-macOS.zip"
