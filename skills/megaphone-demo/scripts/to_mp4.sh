#!/usr/bin/env bash
# megaphone-demo · frames → MP4 (H.264, web-friendly)
#
# Usage:
#   to_mp4.sh <frames_dir> <out_path> [--width 1280] [--fps 24]

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: to_mp4.sh <frames_dir> <out_path> [--width 1280] [--fps 24]" >&2
  exit 2
fi

FRAMES_DIR="$1"; shift
OUT="$1"; shift
WIDTH=1280
FPS=24

while [[ $# -gt 0 ]]; do
  case "$1" in
    --width) WIDTH="$2"; shift 2;;
    --fps)   FPS="$2";   shift 2;;
    *) echo "Unknown flag: $1" >&2; exit 2;;
  esac
done

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo '{"ok": false, "error": "ffmpeg not installed."}' >&2
  exit 3
fi

mkdir -p "$(dirname "$OUT")"

ffmpeg -y -framerate "$FPS" -i "${FRAMES_DIR}/%03d_*.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 22 \
  -vf "scale=${WIDTH}:trunc(ow/a/2)*2:flags=lanczos" \
  -movflags +faststart \
  "$OUT" 2>/dev/null

SIZE=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT" 2>/dev/null || echo 0)
echo "{\"ok\": true, \"out\": \"$OUT\", \"size_bytes\": $SIZE}"
