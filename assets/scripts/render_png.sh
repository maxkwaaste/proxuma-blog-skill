#!/bin/zsh
# render.sh <html> <W> <H>  -> writes <base>.png at deviceScaleFactor 2 (W*2 x H*2)
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
html="$1"; W="$2"; H="$3"
base="${html%.html}"
abs="$(cd "$(dirname "$html")" && pwd)/$(basename "$html")"
prof="$(mktemp -d)"
rm -f "$base.png"
( "$CHROME" --headless=new --hide-scrollbars --disable-gpu --force-device-scale-factor=2 \
   --user-data-dir="$prof" --no-first-run --no-default-browser-check --disable-extensions \
   --window-size="$W,$H" --screenshot="$base.png" "file://$abs" >/dev/null 2>&1 ) & CPID=$!
( sleep 30 && kill -9 $CPID 2>/dev/null ) & WPID=$!
wait $CPID 2>/dev/null; kill $WPID 2>/dev/null; rm -rf "$prof"
if [ -f "$base.png" ]; then sips -g pixelWidth -g pixelHeight "$base.png" 2>/dev/null | grep pixel; else echo "FAILED: $base.png"; fi
