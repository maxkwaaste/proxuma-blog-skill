# WordPress Access + Gotchas (proxuma.io on SiteGround)

All credentials are per-user and live ONLY in `~/.config/proxuma-blog/config.env`
(gitignored). Never put a host, port, key path or token in the repo. Load the config at the
start of a run:

```bash
set -a; source ~/.config/proxuma-blog/config.env; set +a
```

Expected variables (see `.env.example`):

| Variable | Example | Meaning |
|----------|---------|---------|
| `WP_SSH_HOST` | `es33.siteground.eu` | SiteGround SSH host |
| `WP_SSH_PORT` | `18765` | SSH port |
| `WP_SSH_USER` | `u1434-...` | SSH user |
| `WP_SSH_KEY`  | `~/.ssh/id_ed25519` | private key path |
| `WP_ROOT`     | `~/www/proxuma.io/public_html` | WordPress root on the server |
| `OPENROUTER_API_KEY` | (optional) | only for the decorative Nano-Banana wrapper |

Connect / run wp-cli:

```bash
SSH="ssh -i $WP_SSH_KEY -p $WP_SSH_PORT $WP_SSH_USER@$WP_SSH_HOST"
$SSH "cd $WP_ROOT && wp post list --post_type=post --posts_per_page=5"
```

## The non-negotiable gotchas

1. **Body writes: `$wpdb->update`, never `wp_update_post` and never `wp post update`
   with a shell var.** `wp_update_post()` (and piping `--post_content` through the shell)
   strips/mangles the inline-styled `<div>`/`<h2>`/`<figure>` markup these posts rely on.
   Create the post first, then write `post_content` with a small PHP script that calls
   `$wpdb->update( $wpdb->posts, ['post_content'=>$html], ['ID'=>$id] )`. Pass the HTML to
   the script via a file, not a shell argument.

2. **Guard `wpautop`.** After writing, re-read `post_content` and confirm your `<div>`s and
   `<h2>`s were not wrapped in stray `<p>`/`<br>`. If they were, the theme's `the_content`
   filter is auto-formatting; write already-balanced block markup and re-verify.

3. **Caches after any change:** `wp cache flush && wp sg purge` (dynamic cache). The
   SiteGround CDN socket is no longer reachable from CLI, so the **Cloudflare "Purge
   Everything" is manual in the dashboard** and is a human step (it is on the publish
   checklist, not something this skill does).

4. **Verifying public URLs past Cloudflare.** Origin-less `curl` can get a 202 challenge
   (Cloudflare challenges fake-Googlebot UAs), so do not trust raw curl for "is it published"
   checks. Prefer `wp post get <id> --field=post_status`, `get_page_by_path()` via a wp eval
   script, or the wp-blog-header loopback. For redirect/header checks, `curl -sI` from a real
   browser-like UA is fine; document how you simulated `CF-IPCountry` (it is edge-set).

5. **Never use `wp_update_post` on report pages** either; the same markup-stripping applies
   site-wide. Gallery/report pages have extra rules outside this skill's scope.

## Useful one-liners

```bash
# resolve a post ID from a slug
$SSH "cd $WP_ROOT && wp post list --post_type=post --name=<slug> --field=ID"

# copy reference markup to use as the structural template
$SSH "cd $WP_ROOT && wp post get 7055 --field=post_content" > /tmp/ref-7055.html

# read post meta you must mirror
$SSH "cd $WP_ROOT && wp post meta list <id>"

# set Yoast primary category + og:image
$SSH "cd $WP_ROOT && wp post meta update <id> _yoast_wpseo_primary_category 10"
$SSH "cd $WP_ROOT && wp post meta update <id> _yoast_wpseo_opengraph-image-id <media-id>"

# safe-mode cleanup
$SSH "cd $WP_ROOT && wp post delete <id> --force"
```

Write the PHP body-update helper to the server `/tmp`, run it with `wp eval-file`, then
delete it. Keep no scratch PHP on the server after the run.
