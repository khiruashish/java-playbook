#!/usr/bin/env bash
# One-time setup: Python venv, Playwright + Chromium, and the Kokoro voice model (~350 MB, not committed).
set -euo pipefail
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
[ -d node_modules/playwright ] || { npm install --no-save --silent playwright && npx playwright install chromium; }
mkdir -p models
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "models/$f" ] || curl -fL --progress-bar -o "models/$f" "$base/$f"
done
echo "Ready. Build a video with: tools/video/make.sh ch06"
