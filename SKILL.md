---
name: proxuma-blog
description: >-
  Build two fully-finished DRAFT blog posts (English + Dutch) on proxuma.io from one
  source article, on-brand and QA'd, ready for a human to review and publish. Use this
  whenever someone wants to publish, build, or draft a blog from an article or content
  package, says "proxuma blog", "build the blog from <file>", "maak de blog", drops a
  Proxuma content-package HTML (sections id="s1" NL / id="s1b" EN), or asks for an EN/NL
  blog pair on proxuma.io. It parses the source, writes the structurally-twinned EN+NL
  drafts, generates on-brand Proxuma data-viz, places images and the og:image, stages the
  EN<->NL routing pair (dormant until publish), and runs an independent QA capstone. It
  STOPS at drafts and never auto-publishes: human review, publish, and the Cloudflare purge
  stay manual.
user-invocable: true
---

# Proxuma Blog Pipeline

Turn one source article into two finished **draft** blog posts on proxuma.io, an English
post and its Dutch twin, structurally identical, on-brand, with charts and og:image in
place and the language-routing pair staged. A human reviews and publishes. This skill never
publishes and never touches a live post's published state.

This packages a proven pipeline. The live reference pair every new post mirrors is EN post
**7055** (`/the-msp-market-is-doubling-to-847-billion/`) and NL post **7096**
(`/de-msp-markt-verdubbelt-naar-847-miljard/`).

## Hard rules (read first)

- **Never publish.** Both posts stay `post_status=draft`. Flipping to publish, purging
  Cloudflare, and the LinkedIn Post Inspector check are the human's job. Print the
  checklist, then stop.
- **Never invent facts or figures.** Every number in a chart cites a source sentence from
  the article or is labelled "illustratief / illustrative". Missing marketing copy (for
  example a Dutch CTA card with no source) gets flagged for a human, never written from
  thin air. Keep the EN copy as interim and say so.
- **Never hardcode secrets.** WP SSH host/key and any API keys live only in the per-user
  config at `~/.config/proxuma-blog/config.env` (gitignored). See README + `.env.example`.
- **One production-mutating step, and it is additive.** Only the routing edit (step 5)
  changes a shared live file. Back it up, keep existing maps intact, and gate the new pair
  behind the existing 404 guard so it stays dormant until the NL post is published.
- **Never cross language files.** English-labelled images never go on the Dutch post and
  vice versa. Mirror structure exactly; only the words differ.
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
  `section id="s1"` is the NL blog under the kicker "De blog", `section id="s1b"` is the EN
  blog. Ignore every other section (the LinkedIn / e-mail / video / DM cascade).
- **Also accepted:** a plainer article, or a single language. If only one language is
  present, translate the missing one into Proxuma's Dutch MSP voice using the `dutch-msp`
  skill (Dutch) and keep English plain and direct. Translate, do not rewrite, and invent no
  facts.

## How to run it

Work the phases in order. Phases 2, 3 and parts of 4 fan out to subagents; 5, 6, 7 are
sequential because they depend on the built posts. Each phase has a canonical, tested
prompt in `references/phase-prompts.md`: open that file and hand the relevant prompt to the
subagent (or follow it yourself), filling in the run-specific values (slugs, post IDs,
image folder). The house style every visual obeys is `references/house-style.md`.

Before dispatching, resolve the run config once and share it with every subagent:
the EN slug, the NL slug, the article folder `~/ClaudeCode/<slug>-images/`, and the source
file path. Keep the EN and NL posts structurally twinned at every step.

### 1. Parse the source (deterministic, do this yourself)

```
python3 assets/scripts/parse_source.py "<source.html>" --out /tmp/<slug>-parsed.json
```

This extracts, per language: title, lede, ordered blocks (headings, paragraphs, the
pull-quote, the numbered data-checks), the CTA, links, and the real figures. The stderr
summary shows block counts per language. If EN and NL block counts differ, note it: follow
the source for content and the reference post for tags, and flag the mismatch. If the file
is not a content-package (no `s1`/`s1b`), the parser falls back to parsing the whole body
as one post and reads its language from `<html lang>`; translate the other language then.
Decide the two slugs (mirror the live pair's pattern: EN is the English headline
kebab-cased; NL is the Dutch headline kebab-cased).

### 2. Create the EN + NL drafts (two subagents, parallel)

Use **Prompt 2** from `references/phase-prompts.md` for each language. The drafts are born
polished off the live reference post: pull `wp post get 7055 --field=post_content` as the
structural template (styled lede, cyan `#00B7FF` pull-quote block, white check-cards with
cyan number chips, brand CTA card), then map the parsed copy onto it 1:1, words verbatim.
Category Blogs (`term_id 10`), Yoast primary category 10, mirrored post meta, a Dutch and
an English Yoast title + meta description, agreed slugs, both `draft`.
The NL CTA-card marketing copy has no source: keep the EN card text as interim and flag it
for human Dutch copy. Do not invent it.

### 3. Generate on-brand data-viz (one subagent)

Use **Prompt 3.1** (the canonical Vega-Lite + numeric-gate path; Prompt 3 is the older
hand-SVG version, kept only for reference). Build 3 to 6 visuals into
`~/ClaudeCode/<slug>-images/`:
- **Data charts** (anything plotting real values): emit a Vega-Lite v5 spec bound to a JSON
  data table, merge `assets/vega-theme.json` into its `config`, then render with
  `assets/scripts/render_vega.sh <spec>.vl.json 2`. Numbers come from the data, never from
  pixels.
- **Diagrams / callouts** (flow, capture-vs-show, big-number comparisons, hero, OG card):
  themed HTML/CSS using `assets/proxuma-fonts.css` for Inter, rendered with
  `assets/scripts/render_png.sh <file>.html <W> <H>`. Run `assets/scripts/collision_check.py`
  for the 64px safe-area + collision pass.
- Produce an **EN label set and a NL label set** (text is baked into several visuals).
  `assets/scripts/nl_label_swap.example.py` shows the string-swap pattern; for new articles
  do the swap from the parsed NL copy.
- **Numeric gate (mandatory):** after rendering, re-extract every figure in each image and
  cite it to a source sentence, or label it illustrative. Any unsourced or mismatched
  number fails the image; fix and re-render. Report the gate table.
Nothing is pushed to WordPress here; this is Max's review set (open the contact sheet).

### 4. Place images (one subagent per language, after 2 and 3)

Use **Prompt 5**. Upload the approved PNGs to WP media (`wp media import`, alt text in brand
voice with the key figure), set the featured hero per language (replacing any interim),
insert in-body figures matched to sections by surrounding text, and set the **og:image**
(Yoast social) on both. If only one language's image set exists, stop and report; never put
EN-labelled images on the NL post.

### 5. Routing (the one production-mutating step, sequential)

Use **Prompt 1** logic, but for this run you are only **adding one EN<->NL blog slug pair**,
not rebuilding the maps. Follow `references/routing-edit.md` exactly: back up both
mu-plugins first, add the pair to `proxuma-nl-redirect.php` (bidirectional) and
`proxuma-hreflang.php` (additive), keep every existing entry intact, and keep the new pair
behind its 404 guard so it stays dormant until the NL post is published. `php -l` both files,
then test both directions with the documented curl matrix.

### 6. QA capstone (one subagent, FRESH context)

Use **Prompt 6**. Spawn this in a clean context so the verification is independent of the
build. It checks structure parity, both routing directions, hreflang, images present and in
the correct language, og:image resolves, and that links return 200, then writes a PASS/FAIL
report. It changes no content; it only flags, and may fix purely mechanical things like a
missing cache purge.

### 7. Hand-off (you, in the main thread)

Print the QA report and the short human publish-checklist:
1. Review both drafts (preview URLs).
2. Supply Dutch CTA-card copy if it was flagged (EN is interim).
3. Publish the NL post (the blog redirect + hreflang auto-activate on publish, no code
   change).
4. Cloudflare dashboard -> Purge Everything (covers the og:image and the new NL page).
5. Optional: `?lang=en` spot-check and a LinkedIn Post Inspector check on the og:image.

Then stop. Do not publish, do not purge Cloudflare.

## Safe dry-run mode

To prove the pipeline end-to-end without going near production state, run in **safe mode**:
- Give both drafts a clearly-temporary slug suffix `-skilltest`.
- Do **not** add a real routing pair (validate the routing edit on a backup copy of the
  plugin only, or skip step 5 and note it).
- Build the drafts, charts, images and QA report, screenshot them, then **delete the test
  drafts** (`wp post delete <id> --force`) and revert any plugin test edits.
- Report what was built with screenshots, then confirm cleanup.

## Reference files

- `references/phase-prompts.md` — the canonical, tested prompt for every phase. Source of
  truth for each step's instructions. Open it and lift the relevant prompt.
- `references/house-style.md` — the locked Proxuma image + chart house style (palette, type,
  the numeric gate, the dark-hero / light-in-body rule).
- `references/wp-access.md` — WordPress access, the `$wpdb->update` / `wpautop` / cache
  gotchas, and how to verify URLs past Cloudflare.
- `references/routing-edit.md` — the exact, backed-up, additive, gated procedure for adding
  one blog pair to the two mu-plugins, with the curl test matrix.

## Assets

- `assets/proxuma-tokens.css` — Proxuma Design System 2.0 colors + type tokens.
- `assets/proxuma-fonts.css` — self-hosted Inter (base64 woff2) for chart HTML.
- `assets/fonts/` — Inter woff2 (400/500/600/700).
- `assets/vega-theme.json` — the Proxuma Vega config to merge into every data-chart spec.
- `assets/scripts/parse_source.py` — the PARSE step.
- `assets/scripts/render_vega.sh` — Vega-Lite spec to SVG + PNG (data charts).
- `assets/scripts/render_png.sh` — HTML to PNG at 2x (diagrams / callouts).
- `assets/scripts/svg_to_html.py` — wrap a standalone SVG in an Inter-loading HTML page.
- `assets/scripts/collision_check.py` — 64px safe-area + label-collision pass.
- `assets/scripts/nl_label_swap.example.py` — worked example of the EN->NL chart-label swap.
