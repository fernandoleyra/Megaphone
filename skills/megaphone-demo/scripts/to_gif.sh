#!/usr/bin/env bash
# megaphone-demo · frames → GIF
#
# Usage:
#   to_gif.sh <frames_dir> <out_path> [--width 1024] [--fps 12]
#
# Uses ffmpeg's two-pass palette workflow for a small, sharp GIF (much
# better than naive single-pass conversion).

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: to_gif.sh <frames_dir> <out_path> [--width 1024] [--fps 12]" >&2
  exit 2
fi

FRAMES_DIR="$1"; shift
OUT="$1"; shift
WIDTH=1024
FPS=12

while [[ $# -gt 0 ]]; do
  case "$1" in
    --width) WIDTH="$2"; shift 2;;
    --fps)   FPS="$2";   shift 2;;
    *) echo "Unknown flag: $1" >&2; exit 2;;
  esac
done

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo '{"ok": false, "error": "ffmpeg not installed. Try: brew install ffmpeg / apt install ffmpeg / choco install ffmpeg"}' >&2
  exit 3
fi

if [[ ! -d "$FRAMES_DIR" ]]; then
  echo "{\"ok\": false, \"error\": \"frames dir not found: $FRAMES_DIR\"}" >&2
  exit 4
fi

mkdir -p "$(dirname "$OUT")"
PALETTE="$(mktemp -t megaphone-palette-XXXXXX.png)"

# Pattern: frames are NNN_label.png in lexicographic order.
FILTER="fps=${FPS},scale=${WIDTH}:-1:flags=lanczos"

# Pass 1 — generate optimized palette
ffmpeg -y -framerate "$FPS" -pattern_type glob -i "${FRAMES_DIR}/*.png" \
  -vf "${FILTER},palettegen=max_colors=128:stats_mode=diff" \
  "$PALETTE" 2>/dev/null

# Pass 2 — encode using the palette
ffmpeg -y -framerate "$FPS" -pattern_type glob -i "${FRAMES_DIR}/*.png" -i "$PALETTE" \
  -filter_complex "${FILTER}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
  "$OUT" 2>/dev/null

rm -f "$PALETTE"

# Report final size
SIZE=$(stat -f%z "$OUT" 2>/dev/null || stat -c%s "$OUT" 2>/dev/null || echo 0)
echo "{\"ok\": true, \"out\": \"$OUT\", \"size_bytes\": $SIZE}"
