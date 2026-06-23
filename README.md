# Proxuma Blog Skill (`/proxuma-blog`)

A Claude Code skill that turns one source article into **two finished draft blog posts** on
proxuma.io, an English post and its Dutch twin, on-brand, charted, and QA'd, ready for a
human to review and publish.

Drop in a source article, run one command, get back: two structurally-identical drafts (EN +
NL), on-brand Proxuma data-viz placed in body, the featured hero and og:image set, the
EN<->NL routing pair staged (dormant until publish), a QA report, and a short publish
checklist. **It stops at drafts and never auto-publishes.** Human review, publish, and the
Cloudflare purge stay manual.

## What it does

1. **Parse** the source (title, lede, sections, pull-quote, the numbered data-checks, CTA,
   real figures). Detects language(s); translates the missing one in Proxuma's Dutch MSP
   voice (no invented facts).
2. **Create** the EN + NL drafts (parallel), born polished off the live reference post:
   styled lede, cyan pull-quote block, white check-cards with cyan number chips, brand CTA
   card, category Blogs, Yoast, mirrored meta, agreed slugs. Structurally identical twins,
   words verbatim.
3. **Generate** 3 to 6 on-brand visuals: data charts as Vega-Lite specs bound to real data,
   themed HTML diagrams for callouts, each EN + NL labelled, through the collision checker
   and a numeric gate (every figure cited to a source sentence or labelled illustrative).
4. **Place** images: featured hero + in-body figures matched to sections by language,
   captions + alt, og:image on both.
5. **Routing** (the one production-mutating step): add the EN<->NL pair to
   `proxuma-nl-redirect.php` + `proxuma-hreflang.php`, backed up, additive, gated dormant
   until the NL post publishes.
6. **QA capstone** (fresh context): structure parity, routing both ways, hreflang, images,
   og:image, links -> PASS/FAIL report.
7. **Hand-off**: print the human publish checklist, then stop.

## Install (per teammate)

1. **Clone into your skills folder** so it loads as `/proxuma-blog`:
   ```bash
   git clone git@github.com:Proxuma/proxuma-blog-skill.git ~/.claude/skills/proxuma-blog
   ```
2. **Wire your own WordPress access** (nothing is committed):
   ```bash
   mkdir -p ~/.config/proxuma-blog
   cp ~/.claude/skills/proxuma-blog/.env.example ~/.config/proxuma-blog/config.env
   chmod 600 ~/.config/proxuma-blog/config.env
   # edit config.env: WP_SSH_HOST / PORT / USER / KEY / WP_ROOT
   ```
3. **Tooling** auto-installs on first run if missing: `vega` / `vega-lite` / `vega-cli` (npm,
   via `npx`) for data charts. Headless Chrome is already on macOS. Python 3 standard library
   only. Node 18+ recommended.

You also need read access to proxuma.io's WordPress (SiteGround SSH) and the `dutch-msp`
skill installed (used when a language has to be translated).

## Use

In Claude Code:

```
/proxuma-blog ~/Downloads/my-article.html
```

or just ask: "build the blog from ~/Downloads/my-article.html" / "maak de blog van dit
artikel". The skill drives the seven phases, spinning up subagents for the parallel ones.

### Input formats

- **Primary:** the Proxuma content-package HTML (`section id="s1"` = NL blog under "De blog",
  `section id="s1b"` = EN blog; the LinkedIn / e-mail / video / DM cascade is ignored).
- **Also:** a plainer article, or a single language (the other is translated).

### Safe dry-run

To prove it end-to-end without touching production state, ask for a **safe dry-run**: it
suffixes both slugs with `-skilltest`, skips the live routing edit (validates it on a backup
copy only), builds the drafts + charts + QA report with screenshots, then deletes the test
drafts. Used to verify the skill on `proxuma-L1-cm-versie (1).html`.

## Security / sharing

- **No secrets in the repo.** WP SSH key/host and any API key live only in
  `~/.config/proxuma-blog/config.env` (gitignored). The committed `.env.example` is a
  template. A thorough `.gitignore` blocks `.env`, keys, backups, and per-run build output.
- **The routing edit mutates a shared production file.** It is explicit, backed up first,
  additive (existing maps untouched), syntax-checked, tested, and gated behind the existing
  404 / publish guard so the new pair stays dormant until the NL post is published.
- **Never auto-publishes.** Drafts plus a human gate, always.

## Repo layout

```
proxuma-blog-skill/            (clone to ~/.claude/skills/proxuma-blog)
├── SKILL.md                   the orchestration workflow (the 7 phases)
├── README.md                  this file
├── .env.example               per-user config template
├── .gitignore
├── references/
│   ├── phase-prompts.md       the canonical, tested prompt per phase (source of truth)
│   ├── house-style.md         locked image + chart house style + numeric gate
│   ├── wp-access.md           WordPress access + $wpdb->update / wpautop / cache gotchas
│   └── routing-edit.md        the backed-up, additive, gated blog-pair edit + test matrix
└── assets/
    ├── proxuma-tokens.css     Proxuma DS 2.0 colors + type
    ├── proxuma-fonts.css      self-hosted Inter (base64) for chart HTML
    ├── vega-theme.json        Proxuma Vega config (merge into every data-chart spec)
    ├── fonts/                 Inter woff2 (400/500/600/700)
    └── scripts/
        ├── parse_source.py        the PARSE step (content-package or plain article -> JSON)
        ├── render_vega.sh         Vega-Lite spec -> SVG + PNG (data charts)
        ├── render_png.sh          HTML -> PNG at 2x (diagrams / callouts)
        ├── svg_to_html.py         wrap an SVG in an Inter-loading HTML page
        ├── collision_check.py     64px safe-area + label-collision pass
        └── nl_label_swap.example.py   worked example of the EN->NL chart-label swap
```

## Notes

- The reference pair this skill mirrors: EN post 7055
  (`/the-msp-market-is-doubling-to-847-billion/`) and NL post 7096
  (`/de-msp-markt-verdubbelt-naar-847-miljard/`).
- The Dutch CTA-card marketing copy has no source on the MSP article; the skill keeps the EN
  card as interim and flags it for human Dutch copy rather than inventing it. Expect to
  supply localized marketing lines and a localized hero before publishing.
