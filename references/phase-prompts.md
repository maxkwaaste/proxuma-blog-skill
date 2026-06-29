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
6. Yoast: an SEO title (<=60 chars) + meta description (<=155 chars — count it; do not exceed, Google truncates past ~155), concise, featuring the article's key terms (e.g. "Autotask", "MSP", "margin"). Keep the post a DRAFT.
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

OUTPUT: ~/ClaudeCode/<SLUG>-images/ — per visual the source AND the artifact that gets used downstream:
- In-body DATA CHARTS: keep the .vl.json spec + the rendered **.svg** — the SVG is what gets INLINED into the post (vector, sharp, light). The .png is for the contact sheet/preview only, never shipped in-body.
- In-body DIAGRAMS/CALLOUTS: keep the **.html** source — it gets INLINED into the post body. The .png is preview-only.
- HERO + OG card: keep the .html source + the **.png** (2x) — these two are the only raster files that ship (exported sharp in Prompt 5: WebP hero, PNG og, never JPEG).
Plus the numeric-gate report and contact-sheet.html (open it). Report each visual's path, role, render path, and gate result. Nothing pushed to WordPress.

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

## Prompt 5 — Place visuals (in-body inline SVG/HTML, sharp hero+OG, internal links)

```
TASK: Place the approved Proxuma visuals into the blog post AND finish its on-page SEO. In-body charts/diagrams go in as inline SVG / inline HTML-CSS (sharp text, light, accessible) — NOT raster images. Only the featured hero and the og:image card are raster files. Also add the internal links. Runs AFTER the data-viz is approved.

WHY INLINE: a Vega chart's SVG is real vector text — sharper than any PNG/JPEG and usually SMALLER. JPEG in particular smears letters/numbers (chroma subsampling). So in-body = vector/HTML; the only forced rasters (WP featured image + og:image need a real file URL) are exported sharp, never as JPEG.

ACCESS: SSH + wp-cli per wp-access.md. Post <post id>. Source visuals in ~/ClaudeCode/<SLUG>-images/ (the .svg specs for charts, the .html sources for diagrams/hero/og).
Gotchas: ALL body edits via $wpdb->update (never wp_update_post — it re-runs kses and strips inline SVG + styles). Guard wpautop after every write.

A) IN-BODY CHARTS -> inline SVG (no upload, no raster)
1. Take each data chart's .svg (from render_vega.sh). Make it responsive + sharp: remove any fixed width/height attributes, KEEP the viewBox, ensure the root <svg> carries style="width:100%;height:auto;max-width:760px" and font-family "Inter, 'Segoe UI', Arial, sans-serif" reaches its <text> (the site serves Inter). Strip the white background <rect> if the chart should sit on the page surface.
2. Wrap each in a figure at the matching narrative position (match by surrounding text):
   <figure role="img" aria-label="<key figure in a sentence>" style="margin:32px 0;text-align:center"><svg ... >...</svg><figcaption style="font:400 14px Inter,'Segoe UI',Arial,sans-serif;color:#5C5C71;margin-top:8px"><caption></figcaption></figure>

B) IN-BODY DIAGRAMS / CALLOUTS -> inline HTML/CSS (no upload, no raster)
3. Take each diagram's .html source and inline its markup into the body as a self-contained block: all styles inline on the elements (no external <style>/<link>), font-family Inter stack, fluid widths (%, max-width, flex/grid — NOT fixed px canvas), the real Proxuma logo via the base64 from assets/proxuma-logo.css if it shows the wordmark. Wrap as a <figure> with a <figcaption>. It must render correctly on the post's light surface and reflow on mobile.

C) HERO (featured) + OG (social) -> the only raster files, exported SHARP
4. Render hero + og at exact target size (no upscale-then-downscale). HERO: WebP at high quality for crisp text — `cwebp -q 90 -sharp_yuv <hero>.png -o hero.webp` (WebP is fine for an on-page <img>). OG: PNG, not JPEG — `magick <og>.png -resize 1200x630 -strip png/og.png` then quantize only if needed (`-colors 256` keeps text crisp on a flat card). NEVER JPEG for a card with text. Target hero <=120KB, og <=150KB; if a gradient pushes the hero over, prefer slightly bigger over blurry.
5. Upload hero+og: `wp media import <file> --porcelain --title=... --alt="..."`. Featured: `wp post meta update <id> _thumbnail_id <hero-media-id>` (core wp-cli has NO `wp post thumbnail`); verify read-back; if replacing a live hero, flag it. og:image: set `_yoast_wpseo_opengraph-image` (URL) + `_yoast_wpseo_opengraph-image-id` (id). If the hero is ALSO used as an in-body <img> anywhere, give it width+height attributes and loading="lazy" (the featured thumbnail itself stays eager).

D) INTERNAL LINKS (SEO)
6. Add 2-3 contextual internal links to LIVE proxuma.io pages, wrapping EXISTING body words (no new sentences), each cyan #00B7FF. Verify each target returns 200 first (follow redirects — use the final canonical URL). Good defaults when relevant: /the-msp-market-is-doubling-to-847-billion/, /powerbi/insights/unprofitable-contracts/, the whitepaper /intelligent-msp-unlocking-ai-driven-growth-through-operational-excellence/.

E) WRITE + VERIFY
7. Write the body once via $wpdb->update. Re-read; confirm wpautop did NOT wrap the <figure>/<svg>/divs in <p> (the inline SVG especially — if wpautop mangled it, the write needs the figures kept as single blocks). Caches: wp cache flush && wp sg purge (Cloudflare manual).
8. VERIFY: fetch the rendered the_content; confirm each inline SVG/HTML figure is present in the right section and is real vector/text (grep for <svg / the diagram markup, NOT an <img> to a chart). Confirm featured + og:image set and the og URL resolves 200. Report what went inline vs filed, the hero/og media IDs, the internal links added, and the wpautop result.

GUARDRAILS: visuals + links only, no word or structure changes. The post stays a draft (publishing is Prompt 8, only on explicit go-live).
```

---

## Prompt 6 — End-to-end QA capstone (run in a FRESH context)

```
TASK: Final end-to-end QA of the blog post on proxuma.io before it goes live. Verify, report, do not change content. Only flag issues (and fix purely mechanical ones like a missing cache purge).

SCOPE: the draft post <post id> at /<EN_SLUG>/.
Access: SSH + wp-cli per wp-access.md. Verify public URLs with curl -sI (Cloudflare/SiteGround may captcha origin-less curls; use wp-cli or the wp-blog-header loopback trick where needed).

CHECKS
1. Structure: the body matches the reference structure (lede, headings, pull-quote, check-cards, CTA). Diff the tag skeleton against the reference.
2. Rendering: screenshot full-length. No broken layout; lede/pull-quote/check-cards/CTA on-brand (Inter, navy #164387, cyan #00B7FF). In-body charts are inline SVG and diagrams inline HTML (sharp vector/text — grep the body for `<svg`/diagram markup; FAIL if a chart is a blurry `<img>` to a raster). Figures in matching positions with captions.
3. Cards: featured hero set; og:image resolves (check the meta + URL 200). Both are sharp non-JPEG files (hero WebP, og PNG); text on them is crisp.
4. SEO: Yoast title (<=60) + meta description present and **<=155 chars**; canonical correct; slug is <EN_SLUG>; 2-3 internal links present.
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

---

## Prompt 8 — Publish (ONLY on an explicit go-live)

> The build (Prompts 2-6) ends at a DRAFT. Run this ONLY when the operator's request says to take it live ("publish", "to live", "all the way to live"). On a plain build, do NOT run this — print the human checklist and stop.

```
TASK: Publish the finished, QA-passed draft <post id> to live on proxuma.io. Pre-checked, then flip to publish via $wpdb, then verify.

PRE-PUBLISH GATE (all must hold; if any fails, STOP and report instead of publishing):
- QA capstone (Prompt 6) passed.
- post_author = 4 (Max), "Bart van der Meer" appears nowhere, reviewedby = 2, show_author = 1.
- CTA button = the whitepaper link (unless the article named a different primary action).
- Featured hero + og:image set and resolve 200; in-body charts are inline SVG/HTML (not blurry rasters); the wordmark is the real logo.
- Yoast meta description <= 155 chars; slug correct; 2-3 internal links present and 200.

PUBLISH (never wp_update_post — it strips the styled markup):
1. Flip status + stamp the date via $wpdb directly:
   $now = current_time('mysql'); $gmt = current_time('mysql', 1);
   $wpdb->update($wpdb->posts, ['post_status'=>'publish','post_date'=>$now,'post_date_gmt'=>$gmt,'post_modified'=>$now,'post_modified_gmt'=>$gmt], ['ID'=><post id>]);
   clean_post_cache(<post id>); do_action('save_post', <post id>, get_post(<post id>), true);
2. Caches: wp cache flush && wp sg purge.
3. VERIFY: get_permalink; confirm post_status=publish, the live URL returns 200, it is NOT noindex, post_content is intact (whitepaper button still present, body length unchanged). Open the live URL with bash `open` (NEVER claude-in-chrome).

AFTER: print the one manual step left — Cloudflare dashboard -> Purge Everything (flushes the edge cache + og:image), plus an optional LinkedIn Post Inspector re-scrape. Do NOT purge Cloudflare yourself (SG CDN socket is unreachable from CLI). Report the live URL and the publish confirmation.
```
