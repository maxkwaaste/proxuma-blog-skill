# Proxuma Blog — Canonical Phase Prompts

These are the proven, tested prompts behind each pipeline phase. Hand the relevant one to a
subagent (or follow it yourself), filling in the run-specific values in `<ANGLE_BRACKETS>`.
They are lifted from the live pipeline that shipped EN post 7055 and NL post 7096.

**Run-specific values to resolve once and reuse everywhere:**

| Value | Meaning |
|-------|---------|
| `<REF_TEMPLATE_ID>` | The published reference post whose markup is the structural template. Default **7055** (the live EN MSP-market post). |
| `<EN_SLUG>` / `<NL_SLUG>` | The two agreed slugs (English headline kebab-cased / Dutch headline kebab-cased). |
| `<EN_TITLE>` / `<NL_TITLE>` | The two post titles. |
| `<SLUG>` | The article slug used for the image folder `~/ClaudeCode/<SLUG>-images/`. |
| `<SOURCE>` | Path to the source HTML. |
| `<PARSED>` | Path to the parse_source.py JSON output. |
| In **safe dry-run** mode | append `-skilltest` to both slugs, do not run Prompt 1 against the live plugin, and delete the drafts afterward. |

WordPress access, the `$wpdb->update` / `wpautop` / cache gotchas, and how to verify URLs
past Cloudflare are in `wp-access.md`. The image + chart house style is in `house-style.md`.
The exact routing edit is in `routing-edit.md`.

---

## Prompt 1 — Bidirectional language routing (reference; for one new pair use routing-edit.md)

> For a new blog pair you are only **adding one EN<->NL pair** to existing maps, so follow
> `routing-edit.md` rather than this full rebuild. This full prompt is kept as the source of
> truth for how the routing plugin works and how it is tested.

```
TASK: Make proxuma.io EN/NL language routing fully bidirectional, and add the new blog post pair. Single mu-plugin is the source of truth. This touches production redirect logic, so back up first, test exhaustively, and report the diff + test results before declaring done.

ACCESS
- SSH: <see wp-access.md for host/port/user from config.env>
- WP root: ~/www/proxuma.io/public_html  (use wp-cli)
- Plugin to extend: wp-content/mu-plugins/proxuma-nl-redirect.php  (v3.0)
- Hreflang plugin: wp-content/mu-plugins/proxuma-hreflang.php
- Gotchas: never wp_update_post (strips markup), use $wpdb->update. Cache after changes: wp cache flush && wp sg purge, then purge Cloudflare. Verify URLs with curl -sI.

GOAL
1. Powerbi reverse: English-preference visitor on any /nl-powerbi/* URL -> 302 to EN twin via a reverse NL->EN slug map. The EN->NL map is many-to-one in places; for the reverse pick ONE canonical EN slug per NL slug and verify each EN target returns 200 before trusting. Map the fixed pages too (/nl-powerbi/ -> /powerbi/, /nl-powerbi/ai-gegenereerde-rapporten/ -> /powerbi/insights/).
2. Blog post pair, bidirectional, root slugs: EN /<EN_SLUG>/ <-> NL /<NL_SLUG>/. Dutch on EN -> NL; English on NL -> EN. GUARD: no-op until the NL URL returns 200 so it never 302s to a 404.
3. Hreflang for the blog pair: both posts output rel=alternate hreflang en / nl / x-default (x-default -> EN URL).

SHARED PREFERENCE RESOLUTION (one helper, byte-identical to existing)
?lang=nl|en sets a 90-day cookie and wins -> else cookie -> else first visit: CF-IPCountry NL/BE = dutch; empty -> Accept-Language ^nl = dutch; else english. Exclude bot/crawler/preview UAs.

LOOP SAFETY (critical)
Redirect only when resolved-preference != current-page-language AND the twin exists. Consume ?lang (set cookie) then redirect to the clean other-language URL, no query string. Dutch-on-NL and English-on-EN must NOT redirect. Send Cache-Control: private, no-store on every 302. Zero loops.

PROCESS
- Back up: cp proxuma-nl-redirect.php proxuma-nl-redirect.php.bak.$(date +%Y%m%d%H%M%S) (same for hreflang).
- Keep ONE redirect plugin. Extend it, do not add a competitor. Do not break the existing EN->NL powerbi direction.

TEST MATRIX (document how you simulated each; CF-IPCountry is edge-set)
  a. EN on /powerbi/insights/<slug>/ -> stays 200
  b. NL on /powerbi/insights/<slug>/ -> 302 to /nl-powerbi/.../<nl-slug>/
  c. EN on /nl-powerbi/.../<nl-slug>/ -> 302 to /powerbi/insights/<en-slug>/
  d. NL on the NL report URL -> stays
  e. ?lang=en on an NL URL -> 302 to EN + cookie=en
  f. ?lang=nl on an EN URL -> 302 to NL + cookie=nl
  g. Bot UA -> never redirected
  h. Dutch on /<EN_SLUG>/ -> 302 to /<NL_SLUG>/ (once NL post live)
  i. English on /<NL_SLUG>/ -> 302 to /<EN_SLUG>/
  j. NL blog URL is 404 (post not created yet) -> EN blog does NOT redirect (guard holds)

DELIVERABLE
Unified diff of both plugins, the reverse map with the 200-checks, the filled test matrix with curl evidence. Purge caches at the end. Flag anything ambiguous in the many-to-one inversion rather than guessing.
```

---

## Prompt 2 — Create a draft post (run once per language, born polished)

```
TASK: Create a DRAFT proxuma.io blog post in <LANG> for the article, STRUCTURALLY IDENTICAL to the reference post <REF_TEMPLATE_ID>, with the parsed copy used VERBATIM. Publish as a DRAFT for review. Do not publish, do not touch the reference post. When building both languages, the EN and NL bodies must be structurally identical twins; only the words differ.

ACCESS
- SSH + wp-cli per wp-access.md. WP root ~/www/proxuma.io/public_html.
- Parsed copy: <PARSED> (from parse_source.py). The <LANG> post copy is under posts.<LANG>.
- Gotchas: do NOT pass the body via wp-cli --post_content from a shell var and do NOT use wp_update_post (both mangle markup). Create the post first, then write the body with $wpdb->update directly. wpautop will try to wrap your divs; confirm it did not.

STRUCTURAL TEMPLATE
- Pull the reference markup: wp post get <REF_TEMPLATE_ID> --field=post_content. This defines the tags, order and the CTA card markup. Mirror it exactly:
  - lede -> a distinct lede block (Inter ~20px, navy #164387, weight 600), not just <strong>.
  - body paragraphs -> paragraph divs.
  - section headings -> the reference's heading level (h2).
  - pull-quote -> the reference's cyan #00B7FF left-border pull block. Never drop it.
  - the numbered data-checks -> the reference's white check-cards with cyan number chips.
  - closing CTA question + branded CTA card -> same card markup, same colors/fonts, same demo link (https://meetings-eu1.hubspot.com/proxuma/demo2).

STEPS
1. Map the parsed <LANG> blocks 1:1 onto the reference structure, copy verbatim. Keep proper nouns as-is (Autotask, RMM, Cooper Copilot, Proxuma, Dxfferent).
2. Create the post: post_type=post, post_status=draft, title "<TITLE>", post_name <SLUG>. Category Blogs (term_id 10); set _yoast_wpseo_primary_category = 10.
3. Mirror the reference post meta exactly (copy values from <REF_TEMPLATE_ID>): show_c2a, show_author (0), hide_header, hide_footer, hide_breadcrumbs, source, reviewedby.
4. Featured image: set the interim hero (the reference's hero) ONLY as a placeholder; the chart pipeline supplies the localized hero. Flag that a localized hero is still required. Do not invent or AI-generate a hero.
5. Write the body via $wpdb->update on the new post ID. Re-read it back and confirm the divs/h2 survived (wpautop did not wrap them).
6. Yoast: a <LANG> SEO title + meta description, concise, featuring the article's key terms (for the MSP article: "AI-ready", "Autotask", "MSP"). Keep the post a DRAFT.
7. Caches: wp cache flush && wp sg purge; Cloudflare purge is manual.
8. VERIFY: open the draft preview, screenshot it, confirm: styled lede, all section headings, the pull-quote, the formatted checks, and the CTA card with working demo link. Report the new post ID, preview URL, and screenshot. Leave it as a draft.

CTA COPY FLAG: if the source has no <LANG> marketing copy for the CTA card (common for NL), keep the EN card text as interim and FLAG it for human <LANG> copy. Do not translate-guess the marketing line.

GUARDRAILS
- New public-facing content stays a DRAFT.
- Do not modify the reference post. Do not touch the redirect plugin (separate phase).
- If the parsed copy and the reference disagree on block count, follow the parsed copy for content and the reference for tags, and flag the mismatch.
```

---

## Prompt 3.1 — Data charts via Vega-Lite spec + numeric gate (canonical)

```
TASK: Generate the in-article visuals for the Proxuma blog post with two production paths and a numeric-accuracy gate. Charts with real plotted numbers are NOT hand-written SVG: emit a Vega-Lite spec and let the Vega engine bind the data and render, so figures are never transcribed into pixel coordinates. Diagrams and callouts stay HTML/CSS rendered via headless Chromium. Everything is monochrome on-brand and passes a numeric re-extraction gate. NO Nano Banana / no AI image model for anything containing a number.

WHY: hand-placing numbers in SVG causes drift + overlap; spec-driven charts bind real data and render deterministically; spec-validity does NOT prove numeric correctness, so a re-extraction gate is mandatory.

PATH A — DATA CHARTS (anything plotting real values)
1. Build a data table of the REAL figures (from <PARSED> / the article) as JSON rows.
2. Emit a Vega-Lite v5 JSON spec that binds that table via encodings; never type a value into an x/y pixel.
3. Merge assets/vega-theme.json into the spec's `config` (navy #164387, cyan #00B7FF emphasis, muted slate #8A93A6 for negative/below, greys, Inter, hairline gridlines #EBEDF2, axis text #5C5C71; no red/green).
4. Schema-validate; on error read the message, fix, retry up to 5x.
5. Render: assets/scripts/render_vega.sh <spec>.vl.json 2  (vega-cli, node-canvas, no browser). Dark bg for a hero chart, light for in-body.

PATH B — DIAGRAMS & CALLOUTS (flow, capture-vs-show, big-number comparisons, hero, OG card)
- Build as themed HTML/CSS. ALL text via HTML boxes (flex/grid or <foreignObject>), never free SVG <text> over shapes. Load Inter from assets/proxuma-fonts.css. Reserved label zones; label plates behind anything near a line; collision pass to zero intersections + 8px buffer; terminal markers (check/X) in their own padded slot >=16px clear; captions OUTSIDE any card; 64px safe area; nothing clipped.
- Render: assets/scripts/render_png.sh <file>.html <W> <H>  (Playwright/Chrome headless at 2x). Then run assets/scripts/collision_check.py for the safe-area + collision report.

LANGUAGE: produce an EN label set and a NL label set (text is baked into several visuals). assets/scripts/nl_label_swap.example.py shows the swap pattern; do the swap from the parsed NL copy.

NUMERIC RE-EXTRACTION GATE (both paths, mandatory)
After rendering, re-extract every figure that appears in the image into {value, label, source_sentence}. Diff each against the article and cite the exact source sentence. Any figure not in the article must be labelled "illustratief / illustrative". Any unsourced or mismatched number FAILS the image; fix and re-render. Report the gate table.

RENDER + SELF-CHECK LOOP (per image, fix until all pass)
[ ] Charts came from a validated Vega-Lite spec bound to a real data table (no hand-placed numbers).
[ ] Numeric gate passed: every figure cited to a source sentence, or labelled illustrative.
[ ] Only navy / cyan / greyscale. No red, green, coral, orange.
[ ] No text overlaps any mark; no clipping; nothing crosses the 64px safe area; card borders fully visible.
[ ] Inter rendered (not a fallback); dark-hero / light-in-body consistent across the set.

OUTPUT: ~/ClaudeCode/<SLUG>-images/ — per visual: the .vl.json spec (Path A) or .html source (Path B), the .svg, the .png (2x). Plus the numeric-gate report and contact-sheet.html (open it). Report each visual's path, role, render path, and gate result. Nothing pushed to WordPress.

TOOLING: render_vega.sh auto-installs vega/vega-lite/vega-cli via npx on first run.
```

---

## Prompt 4 — Look polish + brand alignment (only if a post is not born-polished)

> When step 2 builds off the live polished reference post, the drafts are already on-brand
> and this phase is not needed. Use it only to re-skin an older off-brand post. Words never
> change: typography, spacing and color only.

```
TASK: Polish the reading experience and bring it fully on-brand in BOTH languages WITHOUT changing a single word. Typography, spacing and color only. Apply the SAME treatment to both posts so they stay structurally twinned.

Brand source of truth: assets/proxuma-tokens.css (navy #164387, navy-deep #0F3066, cyan #00B7FF, text #181833/#5C5C71, surfaces #F8F8F8/#FFFFFF, hairline #DEE1E8, Inter only).
Gotchas: $wpdb->update (never wp_update_post). Guard wpautop. Keep the inline-style approach; just make the values brand-correct.

POLISH (words unchanged):
1. Lede: Inter ~20px, navy #164387, weight 600, line-height ~1.5. Not just <strong>.
2. Pull-quote: a real block — left 3px cyan #00B7FF border, Inter ~24px, navy #164387, 32px top/bottom margin, 20px left padding. Lift it out of any paragraph into its own block in the same position.
3. Section headings: Inter semibold, navy #164387, letter-spacing -0.01em, ~36px top / ~12px bottom margin.
4. The numbered checks: a stack of white cards (#FFFFFF, 1px #DEE1E8, radius 12, padding 18px) with the number in a small cyan/navy chip (radius 6).
5. Body: Inter, #181833, line-height ~1.65. Links cyan #00B7FF.
6. CTA card: Inter, accent cyan #00B7FF, primary navy #164387. Keep copy + demo link exactly.

PROCESS: back up each post's current post_content first. EN/NL twinned. Write via $wpdb->update; re-read and confirm wpautop did not wrap. Caches: wp cache flush && wp sg purge. VERIFY with screenshots of both, confirm identical structure and on-brand rendering, report a short diff.
```

---

## Prompt 5 — Image placement (per language)

```
TASK: Place the approved Proxuma data-viz images into the blog post in BOTH languages, matching each image to its language and its narrative position. Upload to WP media, set featured images, insert in-body figures, set og:image. Runs AFTER the data-viz is approved.

ACCESS: SSH + wp-cli per wp-access.md. EN post <EN post id>, NL post <NL post id>. Images: final PNGs in ~/ClaudeCode/<SLUG>-images/, an EN set and a NL set.
Gotchas: $wpdb->update for body edits (never wp_update_post). Guard wpautop. Verify with screenshots.

STEPS
1. Inventory the image sets. Confirm an EN set and a NL set exist, each with hero (1200x630) + the in-body visuals. If only one language set exists, STOP and report; never put English-labelled images on the Dutch post.
2. Upload to media: wp media import <file> --title=... --alt="...". Alt text: brand voice, sentence case, include the key figure. One upload per language per image.
3. Featured hero: set the localized hero per post, replacing any interim placeholder. If this changes a live post's hero, call it out for Max.
4. In-body placement: if a post already has in-body <img> tags, replace their src in the SAME position; else insert each as
   <figure style="margin:32px 0;text-align:center"><img src="..." alt="..." style="max-width:100%;height:auto;border-radius:12px"><figcaption style="font:400 14px Inter;color:#5C5C71;margin-top:8px">caption</figcaption></figure>
   at the matching narrative position (match by surrounding text, identically EN and NL).
5. og:image: set Yoast social image (_yoast_wpseo_opengraph-image / -id) to the hero on both.
6. Captions: short, brand voice, sentence case, Inter.
7. Write via $wpdb->update; re-read and confirm wpautop did not wrap the figures. Caches: wp cache flush && wp sg purge.
8. VERIFY: screenshot both posts full-length. Confirm each image renders, correct language, right section, crisp (2x), featured + og:image set. Report screenshots, the media IDs, and any live-hero-replacement note.

GUARDRAILS: images only, no word or polish changes. NL stays a draft. Never cross language files.
```

---

## Prompt 6 — End-to-end QA capstone (run in a FRESH context)

```
TASK: Final end-to-end QA of the blog pair on proxuma.io before the NL post goes live. Verify, report, do not change content. Only flag issues (and fix purely mechanical ones like a missing cache purge).

SCOPE: EN /<EN_SLUG>/ (post <EN id>), NL /<NL_SLUG>/ (draft until this QA passes).
Access: SSH + wp-cli per wp-access.md. Verify public URLs with curl -sI (Cloudflare/SiteGround may captcha origin-less curls; use wp-cli or the wp-blog-header loopback trick where needed).

CHECKS
1. Structure parity: EN and NL bodies have identical structure (same headings, lede, pull-quote, check-cards, CTA). Only language differs. Diff the tag skeletons.
2. Rendering: screenshot both full-length. No broken layout; lede/pull-quote/check-cards/CTA on-brand (Inter, navy #164387, cyan #00B7FF); images present, correct language, crisp.
3. Images: featured set on both; og:image resolves (check og:image meta). In-body figures in matching positions, right language.
4. Language routing: with the resolver, confirm Dutch-on-EN -> NL, English-on-NL -> EN, ?lang overrides set the cookie, bots never redirected, no loops. Document how you simulated CF-IPCountry.
5. hreflang: both posts output rel=alternate hreflang en / nl / x-default pointing correctly, resolves both ways.
6. SEO: Yoast title + meta description present on both in the right language; canonical correct; the NL slug is <NL_SLUG>.
7. Links: the CTA demo link and any in-body links return 200.

DELIVERABLE: a short PASS/FAIL report per check with evidence (screenshots, curl -I, redirect traces). List anything that must be fixed before publishing NL. If all passes, say so and note the NL post is ready for Max to flip from draft to publish (do NOT publish it yourself).
```

---

## Prompt 7 — OpenRouter Nano-Banana wrapper (decoration only, optional, build when needed)

```
TASK: Build an ISOLATED wrapper to generate DECORATIVE images via Nano Banana through OpenRouter, with zero impact on Claude Code. Decorative backgrounds / hero scenes ONLY, never charts or anything containing a real number (those are deterministic Vega/SVG, Prompt 3.1).

HARD RULES (do not break Claude Code):
- Do NOT follow the OpenRouter "claude-code-integration" cookbook. Do NOT set ANTHROPIC_BASE_URL or ANTHROPIC_AUTH_TOKEN anywhere. Those reroute ALL Claude Code traffic through OpenRouter. Verify none are set before and after.
- Read the key from a GITIGNORED env file (~/.config/proxuma-blog/config.env, chmod 600); never hardcode or commit it.

IMPLEMENTATION: a standalone script that POSTs to https://openrouter.ai/api/v1/chat/completions with model "google/gemini-2.5-flash-image", modalities ["image","text"], an image_config for aspect ratio. Inputs: a prompt + optional locked reference image(s). Output: PNG to a given path.

USE: decoration only (Pattern D composite — Nano Banana paints a navy/cyan background, the deterministic Vega/SVG chart is overlaid with sharp; numbers stay vector-perfect). Never let Nano Banana render a figure.

VERIFY: confirm no ANTHROPIC_* env vars exist; one test generation -> a saved PNG; confirm Claude Code still talks to Anthropic directly. Report the wrapper path, the gitignored env location, and the test image.
```
