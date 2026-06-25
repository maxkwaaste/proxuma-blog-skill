# Handoff — getting `/proxuma-blog` running on your machine

You've been given this skill to build blog drafts on **proxuma.io**. Two things have to be
in place: the **code** (this repo) and **runtime access** (SSH into the proxuma.io
SiteGround hosting). GitHub gives you the first, not the second. Do both.

## 1. Install the code

```bash
git clone git@github.com:maxkwaaste/proxuma-blog-skill.git ~/.claude/skills/proxuma-blog
```

If you clone over HTTPS instead, use:
```bash
git clone https://github.com/maxkwaaste/proxuma-blog-skill.git ~/.claude/skills/proxuma-blog
```

## 2. Generate your own SSH key (do NOT reuse anyone else's)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_proxuma -C "you@yourmail — proxuma-blog"
cat ~/.ssh/id_ed25519_proxuma.pub   # <-- send THIS (the .pub) to Max
```

Send the **public** key (`.pub`) to Max. Never send the private key to anyone. Max adds
your public key to the proxuma.io SiteGround account (Site Tools → Devs → SSH Keys Manager).
Until he does, the SSH connection will be refused.

## 3. Wire your config (nothing here is committed)

```bash
mkdir -p ~/.config/proxuma-blog
cp ~/.claude/skills/proxuma-blog/.env.example ~/.config/proxuma-blog/config.env
chmod 600 ~/.config/proxuma-blog/config.env
```

Edit `~/.config/proxuma-blog/config.env`:

```
WP_SSH_HOST="es33.siteground.eu"
WP_SSH_PORT="18765"
WP_SSH_USER="<the uXXXX-... account user Max gives you>"
WP_SSH_KEY="$HOME/.ssh/id_ed25519_proxuma"
WP_ROOT="~/www/proxuma.io/public_html"
REF_TEMPLATE_ID="7055"
```

`WP_SSH_USER` is the SiteGround account username (not your name) — Max passes it to you
privately. It's the same for everyone on the account; access is controlled by your key.

## 4. Test the connection before running the skill

```bash
ssh -i ~/.ssh/id_ed25519_proxuma -p 18765 <WP_SSH_USER>@es33.siteground.eu \
  "cd ~/www/proxuma.io/public_html && wp option get blogname"
```

A successful response prints the site name. If it hangs or says "Permission denied
(publickey)", your key isn't on the account yet — ping Max.

## 5. Run it

```
/proxuma-blog ~/Downloads/my-article.html
```

First run, ask for a **safe dry-run** — it builds a `-skilltest` draft + charts + a QA
report, then deletes the test draft, so you can prove it end-to-end without touching
production. The skill always stops at a draft and never publishes. Review, publish, and the
Cloudflare purge stay manual on your side.

## Notes

- Node 18+ and a working `npx` are needed (charts auto-install `vega` on first run).
- You have read access to this repo, so `git pull` brings future fixes.
- No secrets live in this repo. Your key and the account user live only in your local
  `config.env`, which is gitignored.
