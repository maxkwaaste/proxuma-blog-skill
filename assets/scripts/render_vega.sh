#!/bin/zsh
# render_vega.sh <spec.vl.json> [scale]
# Render a Vega-Lite spec to SVG + PNG with the Vega engine (node-canvas, no browser),
# so plotted numbers come from the bound data table and never from hand-placed pixels.
# Falls back to a global install if present; otherwise uses npx (first run downloads the CLIs).
#
#   render_vega.sh charts/01-market-trend.vl.json 2
#
# Writes <base>.svg and <base>.png next to the spec. PNG is rasterised at <scale> (default 2).
set -e
spec="$1"; scale="${2:-2}"
base="${spec%.vl.json}"; base="${base%.json}"

run() { if command -v "$1" >/dev/null 2>&1; then "$@"; else npx -y -p vega -p vega-lite -p vega-cli "$@"; fi }

run vl2svg "$spec" "$base.svg"
run vl2png -s "$scale" "$spec" "$base.png"

if command -v sips >/dev/null 2>&1; then sips -g pixelWidth -g pixelHeight "$base.png" 2>/dev/null | grep pixel || true; fi
echo "rendered: $base.svg  $base.png"
