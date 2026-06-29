# Proxuma Blog — Image & Chart House Style (v1)

Source of truth: **Proxuma Design System 2.0**, bundled here as `assets/proxuma-tokens.css`
(colors + type) and `assets/fonts/` + `assets/proxuma-fonts.css` (self-hosted Inter). These
tokens are authoritative and supersede the old live $847B hero, which is off-spec (it used
Poppins + #18a8f0; the brand is Inter + #00B7FF).

## Palette (authoritative)
- Navy (primary): `#164387`  | navy hover/deep: `#0F3066`
- Cyan accent: `#00B7FF` (sparingly: links, focus, the emphasis line, the trailing-period flourish)
- Text: `#181833` primary · `#5C5C71` secondary · `#A4A6AA` muted
- Surfaces: page `#F8F8F8` · card `#FFFFFF` · subtle `#F5F8FA`
- Border: `#DEE1E8` hairline 1px (borders carry more weight than shadows)
- Categorical series order: `#0D2CC6` · `#2487E4` · `#00B7FF` · `#844BE5` · `#27BFBD` · `#F39529` · `#41AA70` · `#E94040`

### Semantic accents (the supplied-blog set — teal / mint-green / amber / red)

Every supplied content-package blog ships one identical `:root` palette, and it leans on a
warmer semantic set than bare navy+cyan. These are **sanctioned** for blog visuals — use them
when **color carries meaning**, not decoration:

- Teal `#0F766E` (Proxuma teal) · light `#CCFBF1` · deep `#06403A` — secondary brand / the "operate" tone.
- Positive / win / good path: mint-green `#00D9A5` (emphasis), emerald `#059669` (text/stroke on light), wash `#ECFDF6`.
- Warning / attention: amber `#F59E0B`, deep `#B45309` (text on light), wash `#FFF4E6`.
- Negative / loss / the traditional (slow) path: red `#DC2626`, wash `#FDE0E0`.

> **Monochrome-first still holds.** Default a chart/diagram to navy + cyan + greyscale with
> muted slate `#8A93A6` for neutral-bad. Introduce a semantic accent ONLY where it earns its
> meaning: green/teal for the Proxuma/good outcome, red for the traditional/bad one, amber for
> a caution. One semantic pairing per visual (e.g. teal-green vs red, or navy vs amber); never
> a rainbow. The tokens live in `assets/proxuma-tokens.css` (`--accent-*`) and the Vega config
> exposes them under `_semantic` in `assets/vega-theme.json`.

## Type
- **Inter** (self-hosted woff2 in `assets/fonts/`, weights 400/500/600/700, `font-feature-settings:'cv11'`)
- Scale: 12 / 14 / 16 / 20 / 24 / 40px. Headings semibold, letter-spacing -0.01/-0.02em.
- Figures/labels may use JetBrains Mono (falls back to ui-monospace).
- Metadata labels UPPERCASE, 0.06 to 0.08em tracking. No serif anywhere.

## Form
- Flat. No gradients except ONE navy to cyan radial at hero scale.
- Radii 4/6/8/12/16. Cards: white + 1px `#DEE1E8` border + faint shadow.
- Cool palette only. No photography, no grain, no duotone. Flat-illustration + UI.
- Unicode arrows for trends. Trailing-period flourish on hero headlines only.
- Mascot Mr. Bunny: NEVER on data/charts (auth / empty / AI only).

## Logo / wordmark (NEVER hand-type "Proxuma")

The Proxuma wordmark is a LOGO ASSET, never styled text. Do NOT recreate it by typing
"Proxuma" with a colored "Pro" and white "xuma", or any HTML/CSS/SVG text imitation — that
produces an off-brand half-cyan/half-white blob. Always embed the real logo file.

- Real assets bundled in `assets/logos/`: `proxuma-white.png` (962x283, transparent),
  `proxuma-color.png`, `proxuma-black.png`, `proxuma-dxfferent.png` (combined Proxuma+Dxfferent),
  `proxuma-mark-white.png` / `proxuma-mark-navy.png` (the bunny mark only), `proxuma-primary.svg`.
- Easiest hermetic path: `assets/proxuma-logo.css` carries the logos as base64. Link it in the
  HTML and drop `<span class="proxuma-logo proxuma-logo-white" style="width:150px"></span>`
  (height auto-derives from the 962:283 aspect ratio). Or inline `<img alt="Proxuma" width="150"
  src="data:image/png;base64,…">` from the same data.
- **Dark backgrounds (hero, OG): use the WHITE logo.** Light backgrounds (in-body): COLOR or BLACK.
- Keep it the real proportion (≈3.4:1); never stretch, recolor, add effects, or retype it.
- The bunny mark (`proxuma-mark-*`) is for small icon spots only — NEVER on data/charts.
- Every hero/OG/diagram that shows the brand name shows this logo. After rendering, eyeball the
  logo region: if the wordmark looks like text instead of the real mark, it failed — re-render.

## Charts (the core — numbers are sacred)
- Data charts come from a validated **Vega-Lite spec** bound to a real data table
  (`render_vega.sh`), never hand-placed numbers. Diagrams/callouts are HTML/CSS
  (`render_png.sh`). All numbers, axes, labels, series bind to REAL data.
- One emphasis color per chart; everything else greyscale until meaning needs color.
- Primary metric = navy `#164387` or cyan `#00B7FF`. Neutral-bad = muted slate `#8A93A6`.
- When the comparison is genuinely good-vs-bad, you MAY use the semantic accents (see "Semantic
  accents" above): mint-green `#00D9A5` / emerald `#059669` / teal `#0F766E` for the positive
  side, red `#DC2626` for the negative, amber `#F59E0B` for a caution. One pairing per chart,
  for meaning only — otherwise stay monochrome.
- Gridlines `#EBEDF2`; axis text `#5C5C71`; value labels `#181833`.

## Backgrounds
- HERO + OG (1200x630): dark, radial navy `#164387` to `#0F3066`, faint dot grid, emphasis line in cyan.
- IN-BODY: light, page `#F8F8F8` or card `#FFFFFF` with 1px `#DEE1E8` border, hairlines `#EBEDF2`.
- Pick per image by role and keep it consistent across the whole set.

## Safe area + layout
- 64px hard safe margin on all sides; nothing touches or crosses it; never clip text.
- Reserve a left gutter for axis/baseline labels so they never sit under bars or lines.
- Snap to an 8px grid; align baselines and repeated components; equal gaps.
- Consistent components across the set: chip (rounded-6px, 1px border), pill (radius-100,
  12px h-padding), card (#FFFFFF + 1px #DEE1E8 + radius 12). Arrows: SOLID = working path
  (cyan/navy), DOTTED = broken/guessing path (muted grey). Run `collision_check.py`.

## Numbers (the gate)
- Use the article's REAL figures. Never invent a statistic. If a chart needs illustrative
  data, label it clearly "illustrative".
- After rendering, re-extract every figure and cite it to a source sentence, or mark it
  illustrative. Any unsourced or mismatched number fails the image.

## Images / rendering
- Code-rendered SVG/HTML to PNG. `render_vega.sh` (vega-cli, node-canvas) for data charts;
  `render_png.sh` (headless Chrome at 2x) for branded HTML diagrams/composites.
- Nano Banana: decoration ONLY (cool navy/cyan backgrounds, the cyan line-pattern motif),
  never a real number. Pattern-D composite (NB background + SVG chart overlaid via `sharp`)
  for the rare wow hero. Built via the isolated OpenRouter wrapper (phase-prompts Prompt 7).

## Consistency mechanism
One token set (`assets/proxuma-tokens.css` + `assets/vega-theme.json`) imported by every
chart component. Deterministic palette across every article, forever.
