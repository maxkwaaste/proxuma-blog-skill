# Proxuma Blog — Canonical Phase Prompts

These are the proven, tested prompts behind each pipeline phase. Hand the relevant one to a
subagent (or follow it yourself), filling in the run-specific values in `<ANGLE_BRACKETS>`.
They are lifted from the live pipeline that shipped EN post 7055.

**Run-specific values to resolve once and reuse everywhere:**

| Value | Meaning |
|-------|---------|
| `<REF_TEMPLATE_ID>` | The published reference post whose markup is the structural template. Default **7055** (the live EN MSP-market post). |
| `<EN_SLUG>` | The agreed slug (the English headline kebab-cased). |
| `<EN_TITLE>` | The post title. |
| `<SLUG>` | The article slug used for the image folder `~/ClaudeCode/<SLUG>-images/`. |
| `<SOURCE>` | Path to the source HTML. |
| `<PARSED>` | Path to the parse_source.py JSON output. |
| In **safe dry-run** mode | append `-skilltest` to the slug and delete the draft afterward. |

WordPress access, the `$wpdb->update` / `wpautop` / cache gotchas, and how to verify URLs
past Cloudflare are in `wp-access.md`. The image + chart house style is in `house-style.md`.

---

## Prompt 2 — Create the draft post (born polished)

```
TASK: Create a DRAFT proxuma.io blog post in English for the article, STRUCTURALLY IDENTICAL to the reference post <REF_TEMPLATE_ID>, with the parsed copy used VERBATIM. Publish as a DRAFT for review. Do not publish, do not touch the reference post.

ACCESS
- SSH + wp-cli per wp-access.md. WP root ~/www/proxuma.io/public_html.
- Parsed copy: <PARSED> (from parse_source.py). The post copy is under posts.en.
- Gotchas: do NOT pass the body via wp-cli --post_content from a shell var and do NOT use wp_update_post (both mangle markup). Create the post first, then write the body with $wpdb->update directly. wpautop will try to wrap your divs; confirm it did not.

STRUCTURAL TEMPLATE
- Pull the reference markup: wp post get <REF_TEMPLATE_ID> --field=post_content. This defines the tags, order and the CTA card markup. Mirror it exactly:
  - lede -> a distinct lede block (Inter ~20px, navy #164387, weight 600), not just <strong>.
  - body paragraphs -> paragraph divs.
  - section headings -> the reference's heading level (h2).
  - pull-quote -> the reference's cyan #00B7FF left-border pull block. Never drop it.
  - the numbered data-checks -> the reference's white check-cards with cyan number chips.
  - closing CTA question + branded CTA card -> same card markup, same colors/fonts, and MIRROR THE REFERENCE CTA BUTTON VERBATIM (its href + label). The reference card's button is "Read the full whitepaper ->" pointing at the whitepaper page (https://proxuma.io/intelligent-msp-unlocking-ai-driven-growth-through-operational-excellence/). Do NOT swap it for a demo/booking link. Only change the button if the SOURCE ARTICLE's own CTA names a different primary action verbatim (e.g. it says "book a demo" as the lead ask) - in that case use the article's action, otherwise keep the reference whitepaper button as-is.

STEPS
0. DUPLICATE GUARD (do this FIRST, before creating anything). Confirm no existing post/page already covers this article, matching on BOTH slug and title:
   - `wp post list --post_type=post,page --post_status=any --name=<SLUG> --field=ID`
   - `wp post list --post_type=post,page --post_status=any --fields=ID,post_status,post_title --format=csv | grep -iF "<distinctive title phrase>"`
   If either returns a hit, STOP — create nothing. Report the existing post (ID, status, permalink) and ask the human whether to update it in place, use a new slug, or abort. Proceed only when both come back empty.
1. Map the parsed blocks 1:1 onto the reference structure, copy verbatim. Keep proper nouns as-is (Autotask, RMM, Cooper Copilot, Proxuma, Dxfferent).
2. Create the post: post_type=post, post_status=draft, title "<TITLE>", post_name <SLUG>. Category Blogs (term_id 10); set _yoast_wpseo_primary_category = 10. AUTHOR: set post_author = 4 (Max de Kwaasteniet). Bart van der Meer (user 12) must NEVER be the author of any Proxuma blog post. If the new post lands on any other author, fix it with `$wpdb->update($wpdb->posts, ['post_author'=>4], ['ID'=><newid>])` (pure column update, never wp_update_post). Acceptable authors only, in order of preference: Max de Kwaasteniet (4) > Proxuma (a Proxuma-named user if one exists) > Jasper van Horssen (2). Default to Max.
3. Mirror the reference post meta exactly (copy values from <REF_TEMPLATE_ID>): show_c2a, hide_header, hide_footer, hide_breadcrumbs, source. EXCEPT set these two explicitly for E-E-A-T (do NOT copy the reference's blank values): reviewedby = 2 via `update_field('reviewedby', 2, <newid>)` (Jasper van Horssen, the expert reviewer), AND show_author = 1 via `update_field('show_author', 1, <newid>)`. show_author MUST be 1 — the theme renders the visible "✓ This article is reviewed by:" byline ONLY inside the `if($show_author)` block in single.php, so reviewedby alone is invisible without it. With show_author=1 the post shows the author (Max) and the reviewer (Jasper) — the intended author + expert-reviewer E-E-A-T pairing.
4. Featured image: set the interim hero (the reference's hero) ONLY as a placeholder; the chart pipeline supplies the final hero. Flag that the final hero is still required. Do not invent or AI-generate a hero.
5. Write the body via $wpdb->update on the new post ID. Re-read it back and confirm the divs/h2 survived (wpautop did not wrap them).
6. Yoast: an SEO title + meta description, concise, featuring the article's key terms (for the MSP article: "AI-ready", "Autotask", "MSP"). Keep the post a DRAFT.
7. Caches: wp cache flush && wp sg purge; Cloudflare purge is manual.
8. VERIFY: open the draft preview, screenshot it, confirm: styled lede, all section headings, the pull-quote, the formatted checks, and the CTA card whose button matches the reference (the whitepaper link, unless the source article specified a different action). Report the new post ID, preview URL, and screenshot. Leave it as a draft.

CTA COPY FLAG: if the source has no marketing copy for the CTA card, keep the reference card text as interim and FLAG it for human copy. Do not invent the marketing line.

GUARDRAILS
- New public-facing content stays a DRAFT.
- Do not modify the reference post.
- If the parsed copy and the reference disagree on block count, follow the parsed copy for content and the reference for tags, and flag the mismatch.
```

---

## Prompt 3.1 — Data charts via Vega-Lite spec + numeric gate (canonical)

```
TASK: Generate the in-article visuals for the Proxuma blog post with two production paths and a numeric-accuracy gate. Charts with real plotted numbers are NOT hand-written SVG: emit a Vega-Lite spec and let the Vega engine bind the data and render, so figures are never transcribed into pixel coordinates. Diagrams and callouts stay HTML/CSS rendered via headless Chromium. Everything is on-brand (monochrome navy/cyan by default; sanctioned semantic accents — teal/mint-green/amber/red — only where color carries meaning, see step 3) and passes a numeric re-extraction gate. NO Nano Banana / no AI image model for anything containing a number.

WHY: hand-placing numbers in SVG causes drift + overlap; spec-driven charts bind real data and render deterministically; spec-validity does NOT prove numeric correctness, so a re-extraction gate is mandatory.

PATH A — DATA CHARTS (anything plotting real values)
1. Build a data table of the REAL figures (from <PARSED> / the article) as JSON rows.
2. Emit a Vega-Lite v5 JSON spec that binds that table via encodings; never type a value into an x/y pixel.
3. Merge assets/vega-theme.json into the spec's `config` (navy #164387, cyan #00B7FF emphasis, muted slate #8A93A6 for neutral-bad, greys, Inter, hairline gridlines #EBEDF2, axis text #5C5C71). Default monochrome. When the comparison is genuinely good-vs-bad you MAY use the SEMANTIC accents from the theme's `_semantic` block (mint-green #00D9A5 / emerald #059669 / teal #0F766E = positive, red #DC2626 = negative, amber #F59E0B = caution) — one pairing per chart, for meaning only. See house-style.md "Semantic accents". Never off-spec blues; never color for decoration.
4. Schema-validate; on error read the message, fix, retry up to 5x.
5. Render: assets/scripts/render_vega.sh <spec>.vl.json 2  (vega-cli, node-canvas, no browser). Dark bg for a hero chart, light for in-body.

PATH B — DIAGRAMS & CALLOUTS (flow, capture-vs-show, big-number comparisons, hero, OG card)
- Build as themed HTML/CSS. ALL text via HTML boxes (flex/grid or <foreignObject>), never free SVG <text> over shapes. Load Inter from assets/proxuma-fonts.css. Reserved label zones; label plates behind anything near a line; collision pass to zero intersections + 8px buffer; terminal markers (check/X) in their own padded slot >=16px clear; captions OUTSIDE any card; 64px safe area; nothing clipped.
- LOGO: if the visual shows the Proxuma wordmark (hero, OG, branded diagram), embed the REAL logo — NEVER type "Proxuma" as styled text (no cyan-"Pro" + white-"xuma" imitation). Link assets/proxuma-logo.css and use `<span class="proxuma-logo proxuma-logo-white" style="width:150px"></span>` — WHITE logo on the dark hero/OG, COLOR/BLACK on light in-body. Real files live in assets/logos/. See house-style.md "Logo / wordmark". Keep the real ~3.4:1 proportion; do not stretch or recolor.
- Render: assets/scripts/render_png.sh <file>.html <W> <H>  (Playwright/Chrome headless at 2x). Then run assets/scripts/collision_check.py for the safe-area + collision report.

NUMERIC RE-EXTRACTION GATE (both paths, mandatory)
After rendering, re-extract every figure that appears in the image into {value, label, source_sentence}. Diff each against the article and cite the exact source sentence. Any figure not in the article must be labelled "illustrative". Any unsourced or mismatched number FAILS the image; fix and re-render. Report the gate table.

RENDER + SELF-CHECK LOOP (per image, fix until all pass)
[ ] Charts came from a validated Vega-Lite spec bound to a real data table (no hand-placed numbers).
[ ] Numeric gate passed: every figure cited to a source sentence, or labelled illustrative.
[ ] Monochrome by default (navy / cyan / greyscale). Any color beyond that is a sanctioned semantic accent (teal/mint-green/amber/red per house-style "Semantic accents") used for MEANING only — one pairing, no rainbow, no off-spec blues, no decorative color.
[ ] No text overlaps any mark; no clipping; nothing crosses the 64px safe area; card borders fully visible.
[ ] Inter rendered (not a fallback); dark-hero / light-in-body consistent across the set.
[ ] Any Proxuma wordmark is the REAL bundled logo (assets/proxuma-logo.css / assets/logos/), white-on-dark, color/black-on-light — NOT hand-typed text. Eyeball the logo region; if it reads as text, re-render.

OUTPUT: ~/ClaudeCode/<SLUG>-images/ — per visual: the .vl.json spec (Path A) or .html source (Path B), the .svg, the .png (2x). Plus the numeric-gate report and contact-sheet.html (open it). Report each visual's path, role, render path, and gate result. Nothing pushed to WordPress.

TOOLING: render_vega.sh auto-installs vega/vega-lite/vega-cli via npx on first run.
```

---

## Prompt 4 — Look polish + brand alignment (only if a post is not born-polished)

> When step 2 builds off the live polished reference post, the draft is already on-brand
> and this phase is not needed. Use it only to re-skin an older off-brand post. Words never
> change: typography, spacing and color only.

```
TASK: Polish the reading experience and bring it fully on-brand WITHOUT changing a single word. Typography, spacing and color only.

Brand source of truth: assets/proxuma-tokens.css (navy #164387, navy-deep #0F3066, cyan #00B7FF, text #181833/#5C5C71, surfaces #F8F8F8/#FFFFFF, hairline #DEE1E8, Inter only).
Gotchas: $wpdb->update (never wp_update_post). Guard wpautop. Keep the inline-style approach; just make the values brand-correct.

POLISH (words unchanged):
1. Lede: Inter ~20px, navy #164387, weight 600, line-height ~1.5. Not just <strong>.
2. Pull-quote: a real block — left 3px cyan #00B7FF border, Inter ~24px, navy #164387, 32px top/bottom margin, 20px left padding. Lift it out of any paragraph into its own block in the same position.
3. Section headings: Inter semibold, navy #164387, letter-spacing -0.01em, ~36px top / ~12px bottom margin.
4. The numbered checks: a stack of white cards (#FFFFFF, 1px #DEE1E8, radius 12, padding 18px) with the number in a small cyan/navy chip (radius 6).
5. Body: Inter, #181833, line-height ~1.65. Links cyan #00B7FF.
6. CTA card: Inter, accent cyan #00B7FF, primary navy #164387. Keep copy + the CTA button href/label exactly as the reference (the whitepaper link by default).

PROCESS: back up the post's current post_content first. Write via $wpdb->update; re-read and confirm wpautop did not wrap. Caches: wp cache flush && wp sg purge. VERIFY with a screenshot, confirm on-brand rendering, report a short diff.
```

---

## Prompt 5 — Image placement

```
TASK: Place the approved Proxuma data-viz images into the blog post, matching each image to its narrative position. Upload to WP media, set the featured image, insert in-body figures, set og:image. Runs AFTER the data-viz is approved.

ACCESS: SSH + wp-cli per wp-access.md. Post <post id>. Images: final PNGs in ~/ClaudeCode/<SLUG>-images/.
Gotchas: $wpdb->update for body edits (never wp_update_post). Guard wpautop. Verify with a screenshot.

STEPS
1. Inventory the image set. Confirm a hero (1200x630) + the in-body visuals exist.
2. Upload to media: wp media import <file> --title=... --alt="...". Alt text: brand voice, sentence case, include the key figure.
3. Featured hero: set the final hero, replacing any interim placeholder. Core wp-cli has NO `wp post thumbnail` command, so set the meta directly: `wp post meta update <id> _thumbnail_id <media-id>` (then verify it reads back). If this changes a live post's hero, call it out for Max.
4. In-body placement: if the post already has in-body <img> tags, replace their src in the SAME position; else insert each as
   <figure style="margin:32px 0;text-align:center"><img src="..." alt="..." style="max-width:100%;height:auto;border-radius:12px"><figcaption style="font:400 14px Inter;color:#5C5C71;margin-top:8px">caption</figcaption></figure>
   at the matching narrative position (match by surrounding text).
5. og:image: set Yoast social image (_yoast_wpseo_opengraph-image / -id) to the hero.
6. Captions: short, brand voice, sentence case, Inter.
7. Write via $wpdb->update; re-read and confirm wpautop did not wrap the figures. Caches: wp cache flush && wp sg purge.
8. VERIFY: screenshot the post full-length. Confirm each image renders, right section, crisp (2x), featured + og:image set. Report screenshots, the media IDs, and any live-hero-replacement note.

GUARDRAILS: images only, no word or polish changes. The post stays a draft.
```

---

## Prompt 6 — End-to-end QA capstone (run in a FRESH context)

```
TASK: Final end-to-end QA of the blog post on proxuma.io before it goes live. Verify, report, do not change content. Only flag issues (and fix purely mechanical ones like a missing cache purge).

SCOPE: the draft post <post id> at /<EN_SLUG>/.
Access: SSH + wp-cli per wp-access.md. Verify public URLs with curl -sI (Cloudflare/SiteGround may captcha origin-less curls; use wp-cli or the wp-blog-header loopback trick where needed).

CHECKS
1. Structure: the body matches the reference structure (lede, headings, pull-quote, check-cards, CTA). Diff the tag skeleton against the reference.
2. Rendering: screenshot full-length. No broken layout; lede/pull-quote/check-cards/CTA on-brand (Inter, navy #164387, cyan #00B7FF); images present and crisp.
3. Images: featured set; og:image resolves (check og:image meta). In-body figures in matching positions.
4. SEO: Yoast title + meta description present; canonical correct; the slug is <EN_SLUG>.
5. Links: the CTA button link (the whitepaper page by default) and any in-body links return 200.
6. Author + reviewer (E-E-A-T): post_author = 4 (Max de Kwaasteniet). Bart van der Meer (user 12) must appear NOWHERE — FAIL if "Bart van der Meer" is anywhere on the page. show_author = 1 and reviewedby = 2, so the rendered page shows the "✓ This article is reviewed by: Jasper van Horssen" byline AND Max as author. Confirm both names render and Bart does not.

DELIVERABLE: a short PASS/FAIL report per check with evidence (screenshots, curl -I). List anything that must be fixed before publishing. If all passes, say so and note the post is ready for Max to flip from draft to publish (do NOT publish it yourself).
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
