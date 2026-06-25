# Proxuma Blog Skill (`/proxuma-blog`)

A Claude Code skill that turns one source article into a **finished draft blog post** on
proxuma.io, an English post, on-brand, charted, and QA'd, ready for a human to review and
publish.

Drop in a source article, run one command, get back: a polished draft, on-brand Proxuma
data-viz placed in body, the featured hero and og:image set, a QA report, and a short
publish checklist. **It stops at a draft and never auto-publishes.** Human review, publish,
and the Cloudflare purge stay manual.

## What it does

1. **Parse** the source (title, lede, sections, pull-quote, the numbered data-checks, CTA,
   real figures).
2. **Create** the draft, born polished off the live reference post: styled lede, cyan
   pull-quote block, white check-cards with cyan number chips, brand CTA card, category
   Blogs, Yoast, mirrored meta, the agreed slug. Words verbatim.
3. **Generate** 3 to 6 on-brand visuals: data charts as Vega-Lite specs bound to real data,
   themed HTML diagrams for callouts, through the collision checker and a numeric gate
   (every figure cited to a source sentence or labelled illustrative).
4. **Place** images: featured hero + in-body figures matched to sections, captions + alt,
   og:image.
5. **QA capstone** (fresh context): structure, images, og:image, links -> PASS/FAIL report.
6. **Hand-off**: print the human publish checklist, then stop.

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

You also need read access to proxuma.io's WordPress (SiteGround SSH).

## Use

In Claude Code:

```
/proxuma-blog ~/Downloads/my-article.html
```

or just ask: "build the blog from ~/Downloads/my-article.html". The skill drives the phases,
spinning up subagents for the parallel ones.

### Input formats

- **Primary:** the Proxuma content-package HTML (`section id="s1b"` = EN blog; the Dutch
  `section id="s1"`, the LinkedIn / e-mail / video / DM cascade are ignored).
- **Also:** a plainer article, parsed as one English post.

### Safe dry-run

To prove it end-to-end without touching production state, ask for a **safe dry-run**: it
suffixes the slug with `-skilltest`, builds the draft + charts + QA report with screenshots,
then deletes the test draft.

## Security / sharing

- **No secrets in the repo.** WP SSH key/host and any API key live only in
  `~/.config/proxuma-blog/config.env` (gitignored). The committed `.env.example` is a
  template. A thorough `.gitignore` blocks `.env`, keys, backups, and per-run build output.
- **Never auto-publishes.** A draft plus a human gate, always.

## Repo layout

```
proxuma-blog-skill/            (clone to ~/.claude/skills/proxuma-blog)
├── SKILL.md                   the orchestration workflow (the phases)
├── README.md                  this file
├── .env.example               per-user config template
├── .gitignore
├── references/
│   ├── phase-prompts.md       the canonical, tested prompt per phase (source of truth)
│   ├── house-style.md         locked image + chart house style + numeric gate
│   └── wp-access.md           WordPress access + $wpdb->update / wpautop / cache gotchas
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
        └── collision_check.py     64px safe-area + label-collision pass
```

## Notes

- The reference post this skill mirrors: EN post 7055
  (`/the-msp-market-is-doubling-to-847-billion/`).
- If the source has no marketing copy for the CTA card, the skill keeps the reference card
  as interim and flags it for human copy rather than inventing it.
