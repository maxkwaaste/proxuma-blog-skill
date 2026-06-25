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
- Data semantics: up/positive `#49C481` · warning `#F4C755` · down/negative `#F1416C`
- Categorical series order: `#0D2CC6` · `#2487E4` · `#00B7FF` · `#844BE5` · `#27BFBD` · `#F39529` · `#41AA70` · `#E94040`

> For charts the working monochrome rule is stricter than the full palette: navy + cyan +
> greyscale, with **muted slate `#8A93A6` for "bad"/below**, never red or green. Reserve the
> red/green data-semantic colors for UI, not blog charts.

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

## Charts (the core — numbers are sacred)
- Data charts come from a validated **Vega-Lite spec** bound to a real data table
  (`render_vega.sh`), never hand-placed numbers. Diagrams/callouts are HTML/CSS
  (`render_png.sh`). All numbers, axes, labels, series bind to REAL data.
- One emphasis color per chart; everything else greyscale until meaning needs color.
- Primary metric = navy `#164387` or cyan `#00B7FF`. Below/bad = muted slate `#8A93A6`.
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
