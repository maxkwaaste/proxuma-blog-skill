import sys, pathlib, re
svg_path = pathlib.Path(sys.argv[1])
svg = svg_path.read_text()
m = re.search(r'width="(\d+)"\s+height="(\d+)"', svg)
W,H = m.group(1), m.group(2)
base = svg_path.stem
html = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="proxuma-fonts.css">
<style>html,body{{margin:0;padding:0;width:{W}px;height:{H}px;overflow:hidden;background:#fff;}}
svg{{display:block;}}</style></head><body>
{svg}
</body></html>"""
pathlib.Path(f"{base}.html").write_text(html)
print(f"{base}.html  {W}x{H}")
