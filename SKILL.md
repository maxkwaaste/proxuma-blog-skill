---
name: proxuma-blog
description: >-
  Build one fully-finished DRAFT blog post (English) on proxuma.io from a source
  article, on-brand and QA'd, ready for a human to review and publish. Use this whenever
  someone wants to publish, build, or draft a blog from an article or content package,
  says "proxuma blog", "build the blog from <file>", drops a Proxuma content-package HTML
  (the EN blog under section id="s1b"), or asks for a blog post on proxuma.io. It parses
  the source, writes the draft, generates on-brand Proxuma data-viz (charts as inline vector
  SVG, diagrams as inline HTML, sharp hero+og), adds internal links, and runs an independent
  QA capstone. It builds a DRAFT by default; it publishes ONLY when the request explicitly
  says to take it live ("publish" / "to live"). The Cloudflare Purge stays manual.
user-invocable: true
---

# Proxuma Blog Pipeline

Turn one source article into a finished blog post on proxuma.io: an English post, on-brand,
in-body charts as sharp inline SVG + diagrams as inline HTML, a sharp hero + og:image, and
internal links. The build ends at a **draft**; it goes live only on an explicit go-live.

This packages a proven pipeline. The live reference post every new post mirrors is EN post
**7055** (`/the-msp-market-is-doubling-to-847-billion/`).

## Hard rules (read first)

- **Draft by default; publish only on an explicit go-live.** A plain build ends at
  `post_status=draft` — print the human checklist and stop. Publish (Prompt 8) runs ONLY when
  the request says to take it live ("publish" / "to live" / "all the way to live"), via
  `$wpdb` (never `wp_update_post`). Cloudflare Purge Everything + the LinkedIn Post Inspector
  check always stay manual.
- **Never invent facts or figures.** Every number in a chart cites a source sentence from
  the article or is labelled "illustrative". Missing marketing copy gets flagged for a
  human, never written from thin air.
- **Never hardcode secrets.** WP SSH host/key and any API keys live only in the per-user
  config at `~/.config/proxuma-blog/config.env` (gitignored). See README + `.env.example`.
- **Body writes use `$wpdb->update`, never `wp_update_post`** (it strips the markup), and
  always confirm `wpautop` did not wrap the divs after writing. See
  `references/wp-access.md`.

## Setup (once per teammate)

1. Clone this repo into the skills folder so it loads as `/proxuma-blog`:
   `git clone <repo-url> ~/.claude/skills/proxuma-blog`
2. `cp ~/.claude/skills/proxuma-blog/.env.example ~/.config/proxuma-blog/config.env`
   then fill in your own WordPress SSH access. `chmod 600` it.
3. Tooling the pipeline auto-installs on first run if absent: `vega` / `vega-lite` /
   `vega-cli` (npm, for data charts) and headless Chrome (already on macOS). Python 3 only
   uses the standard library.

Read `config.env` at the start of every run. If it is missing or the SSH host is blank,
stop and tell the operator to do setup, do not guess credentials.

## Input

- **Primary:** the Proxuma content-package HTML (like `proxuma-L1-cm-versie (1).html`):
  `section id="s1b"` is the EN blog. Ignore every other section (the LinkedIn / e-mail /
  video / DM cascade, and the Dutch `section id="s1"`).
- **Also accepted:** a plainer article. The post is built in plain, direct English. Keep the
  copy as written; do not rewrite, and invent no facts.

## How to run it

**Step 0 — self-update.** Before anything else, pull the latest skill so you're always on the
maintainer's newest version: `git -C ~/.claude/skills/proxuma-blog pull --ff-only`. If the
pull fails (no network, local edits, not a git checkout), don't block — log a one-line note
and continue with the version on disk. Never touch `~/.config/proxuma-blog/config.env`; it is
gitignored and local-only, so a pull never disturbs it.

Work the phases in order. Phases 2 and 3 and parts of 4 fan out to subagents; 5 and 6 are
sequential because they depend on the built post. Each phase has a canonical, tested prompt
in `references/phase-prompts.md`: open that file and hand the relevant prompt to the
subagent (or follow it yourself), filling in the run-specific values (slug, post ID, image
folder). The house style every visual obeys is `references/house-style.md`.

Before dispatching, resolve the run config once and share it with every subagent: the EN
slug, the article folder `~/ClaudeCode/<slug>-images/`, and the source file path.

### 1. Parse the source (deterministic, do this yourself)

```
python3 assets/scripts/parse_source.py "<source.html>" --out /tmp/<slug>-parsed.json
```

This extracts, for the English post: title, lede, ordered blocks (headings, paragraphs, the
pull-quote, the numbered data-checks), the CTA, links, and the real figures. The stderr
summary shows the block count. If the file is not a content-package (no `s1b`), the parser
falls back to parsing the whole body as one post. Decide the slug (mirror the live post's
pattern: the English headline kebab-cased).

### 1b. Pre-flight: does this article already exist? (do this yourself, BEFORE Phase 2)

Never create a duplicate. Once you have the slug + title, check proxuma.io for an existing
post/page, matching on BOTH slug and title (WordPress silently appends `-2` to a clashing
slug, so a slug-only check misses near-duplicates):

```
# exact slug, any status
wp post list --post_type=post,page --post_status=any --name=<slug> --field=ID
# title match (catches a re-run that got a different slug)
wp post list --post_type=post,page --post_status=any --fields=ID,post_status,post_title --format=csv \
  | grep -iF "<distinctive title phrase>"
```

If either returns a hit, **STOP — do not build or create anything.** Report the existing
post (ID, status, permalink) and ask the human which they want: update that post in place,
publish under a new slug, or abort. Only when both checks come back empty do you proceed to
Phase 2. (In safe dry-run mode the `-skilltest` slug sidesteps this, so the check still runs
but a clash is near-impossible.)

### 2. Create the draft (one subagent)

Use **Prompt 2** from `references/phase-prompts.md`. The draft is born polished off the live
reference post: pull `wp post get 7055 --field=post_content` as the structural template
(styled lede, cyan `#00B7FF` pull-quote block, white check-cards with cyan number chips,
brand CTA card), then map the parsed copy onto it 1:1, words verbatim. Category Blogs
(`term_id 10`), Yoast primary category 10, mirrored post meta, an English Yoast title + meta
description, the agreed slug, `draft`.

### 3. Generate on-brand data-viz (one subagent)

Use **Prompt 3.1** (the canonical Vega-Lite + numeric-gate path; Prompt 3 is the older
hand-SVG version, kept only for reference). Build 3 to 6 visuals into
`~/ClaudeCode/<slug>-images/`:
- **Data charts** (anything plotting real values): emit a Vega-Lite v5 spec bound to a JSON
  data table, merge `assets/vega-theme.json` into its `config`, then render with
  `assets/scripts/render_vega.sh <spec>.vl.json 2`. The deliverable that ships is the **.svg**
  (real vector Inter text — inlined in-body later, sharp + light). Numbers come from the data.
- **Diagrams / callouts** (flow, capture-vs-show, big-number comparisons) and the **hero / OG**:
  themed HTML/CSS using `assets/proxuma-fonts.css` for Inter (and `assets/proxuma-logo.css` for
  the real wordmark), rendered with `assets/scripts/render_png.sh <file>.html <W> <H>`. Run
  `assets/scripts/collision_check.py`. Diagrams ship as **inlined HTML**; hero/OG ship as sharp
  raster files. The PNGs are for the contact sheet / preview, not for in-body.
- **Numeric gate (mandatory):** after rendering, re-extract every figure in each image and
  cite it to a source sentence, or label it illustrative. Any unsourced or mismatched
  number fails the image; fix and re-render. Report the gate table.
Nothing is pushed to WordPress here; this is Max's review set (open the contact sheet).

### 4. Place visuals + finish on-page SEO (one subagent, after 2 and 3)

Use **Prompt 5**. In-body **charts go in as inline SVG** and **diagrams as inline HTML/CSS**
(sharp, light, accessible — NOT raster). Only the **hero (featured)** and **og:image card** are
raster files, exported sharp (WebP `-q 90` hero, PNG og — never JPEG). Also add **2-3 contextual
internal links** to live proxuma.io pages (wrapping existing words, each verified 200). All body
edits via `$wpdb->update`, wpautop guarded.

### 5. QA capstone (one subagent, FRESH context)

Use **Prompt 6**. Spawn this in a clean context so the verification is independent of the
build. It checks structure against the reference, images present and crisp, og:image
resolves, and that links return 200, then writes a PASS/FAIL report. It changes no content;
it only flags, and may fix purely mechanical things like a missing cache purge.

### 6. Hand-off, or publish (you, in the main thread)

**Default (plain build):** print the QA report and the short human checklist, then STOP — do
not publish, do not purge Cloudflare:
1. Review the draft (preview URL).
2. Publish the post.
3. Cloudflare dashboard -> Purge Everything (covers the og:image and the new page).
4. Optional: a LinkedIn Post Inspector check on the og:image.

**On an explicit go-live** (the request said "publish" / "to live" / "all the way to live"):
run **Prompt 8** — re-check the pre-publish gate, flip to `publish` via `$wpdb` (never
`wp_update_post`), verify the live URL is 200 + indexable + markup intact, then `open` it with
bash (never claude-in-chrome). Cloudflare Purge Everything stays the one manual step (the SG CDN
socket is unreachable from CLI) — print that reminder.

## Safe dry-run mode

To prove the pipeline end-to-end without going near production state, run in **safe mode**:
- Give the draft a clearly-temporary slug suffix `-skilltest`.
- Build the draft, charts, images and QA report, screenshot them, then **delete the test
  draft** (`wp post delete <id> --force`).
- Report what was built with screenshots, then confirm cleanup.

## Reference files

- `references/phase-prompts.md` — the canonical, tested prompt for every phase. Source of
  truth for each step's instructions. Open it and lift the relevant prompt.
- `references/house-style.md` — the locked Proxuma image + chart house style (palette, type,
  the numeric gate, the dark-hero / light-in-body rule).
- `references/wp-access.md` — WordPress access, the `$wpdb->update` / `wpautop` / cache
  gotchas, and how to verify URLs past Cloudflare.

## Assets

- `assets/proxuma-tokens.css` — Proxuma Design System 2.0 colors + type tokens.
- `assets/proxuma-fonts.css` — self-hosted Inter (base64 woff2) for chart HTML.
- `assets/fonts/` — Inter woff2 (400/500/600/700).
- `assets/proxuma-logo.css` — the REAL Proxuma wordmark as base64 (white/color/black). Link it and use `.proxuma-logo .proxuma-logo-white|-color|-black`. NEVER hand-type "Proxuma" as text — see house-style.md "Logo / wordmark".
- `assets/logos/` — real logo files: `proxuma-white.png` (dark bg), `proxuma-color.png` / `proxuma-black.png` (light bg), `proxuma-dxfferent.png`, `proxuma-mark-white.png` / `proxuma-mark-navy.png` (bunny mark, icon spots only), `proxuma-primary.svg`.
- `assets/vega-theme.json` — the Proxuma Vega config to merge into every data-chart spec.
- `assets/scripts/parse_source.py` — the PARSE step.
- `assets/scripts/render_vega.sh` — Vega-Lite spec to SVG + PNG (data charts).
- `assets/scripts/render_png.sh` — HTML to PNG at 2x (diagrams / callouts).
- `assets/scripts/svg_to_html.py` — wrap a standalone SVG in an Inter-loading HTML page.
- `assets/scripts/collision_check.py` — 64px safe-area + label-collision pass.
