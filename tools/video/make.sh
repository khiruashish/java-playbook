#!/usr/bin/env bash
# Build one topic video: tools/video/make.sh ch06  ->  tools/video/out/ch06.mp4 + ch06.srt
set -euo pipefail
cd "$(dirname "$0")"
[ $# -ge 1 ] || { echo "usage: $0 <topic> [--voice am_michael] [--speed 1.0] [--frames-only]"; ls topics; exit 2; }
.venv/bin/python -I build.py "$@" out
