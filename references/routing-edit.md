# Routing Edit — Adding One Blog Pair (the one production-mutating step)

This is the only step that changes a shared live file. Keep it additive, backed-up, gated,
and tested. You are adding a single EN<->NL blog slug pair to two mu-plugins. You are NOT
rebuilding the maps. Do not touch any existing entry.

Plugins (both in `$WP_ROOT/wp-content/mu-plugins/`):
- `proxuma-nl-redirect.php` (v3.0) — bidirectional language redirect. Source of truth for
  routing. Already holds the powerbi forward/reverse maps and the existing blog pair.
- `proxuma-hreflang.php` — emits `rel=alternate hreflang` for the pairs.

## Why a guard

The new pair must stay **dormant until the NL post is published**. The plugin already has a
`proxuma_blog_nl_live()` style publish check: the EN->NL blog redirect and the blog hreflang
emit nothing until the NL post returns 200 / is published. So adding the pair now is safe:
it activates automatically the moment the human publishes the NL draft, with no further code
change. The English-on-NL direction matches by path and is harmless while the NL post is a
draft (the URL 404s, so no one is there).

## Procedure

1. **Back up both plugins** with a timestamp before any edit:
   ```bash
   set -a; source ~/.config/proxuma-blog/config.env; set +a
   SSH="ssh -i $WP_SSH_KEY -p $WP_SSH_PORT $WP_SSH_USER@$WP_SSH_HOST"
   TS=$(date +%Y%m%d%H%M%S)
   $SSH "cd $WP_ROOT/wp-content/mu-plugins && \
         cp proxuma-nl-redirect.php proxuma-nl-redirect.php.bak.$TS && \
         cp proxuma-hreflang.php   proxuma-hreflang.php.bak.$TS && ls -la *.bak.$TS"
   ```

2. **Read both plugins fully** before editing. Find the existing blog-pair entry (the live
   pair is EN `the-msp-market-is-doubling-to-847-billion` <-> NL
   `de-msp-markt-verdubbelt-naar-847-miljard`). Copy that exact shape for the new pair.

3. **Add the pair to `proxuma-nl-redirect.php`** alongside the existing blog pair, both
   directions, keeping the 404 / publish guard. Pattern (match the file's actual style):
   ```php
   // blog pairs: EN slug => NL slug  (guarded; dormant until NL post is published)
   $blog_pairs = array(
       'the-msp-market-is-doubling-to-847-billion' => 'de-msp-markt-verdubbelt-naar-847-miljard',
       '<EN_SLUG>' => '<NL_SLUG>',   // <-- the only line you add
   );
   ```

4. **Add the pair to `proxuma-hreflang.php`** (additive). Both posts should output
   `hreflang en` / `nl` / `x-default` (x-default -> the EN URL), and the function should stay
   a no-op for this pair until both posts are published. Leave the existing 432-pair page
   logic and the existing blog pair untouched.

5. **Lint both files** before trusting them:
   ```bash
   $SSH "cd $WP_ROOT/wp-content/mu-plugins && php -l proxuma-nl-redirect.php && php -l proxuma-hreflang.php"
   ```

6. **Flush caches:** `wp cache flush && wp sg purge`. Cloudflare purge is the human's step.

## Test matrix (fill with real evidence)

Run after the edit. While the NL post is still a draft, only some rows are testable; note
which are gated. Every 302 must carry `Cache-Control: private, no-store`.

| # | Scenario | Expected | Result |
|---|----------|----------|--------|
| a | EN-pref on `/<EN_SLUG>/` | stays 200 | |
| b | NL-pref on `/<EN_SLUG>/` | 302 -> `/<NL_SLUG>/` (once NL published) | gated |
| c | EN-pref on `/<NL_SLUG>/` | 302 -> `/<EN_SLUG>/` | |
| d | NL-pref on `/<NL_SLUG>/` | stays 200 (once NL published) | gated |
| e | `?lang=en` on the NL URL | 302 -> EN + cookie=en | |
| f | `?lang=nl` on the EN URL | 302 -> NL + cookie=nl (once NL published) | gated |
| g | Bot UA on either | never redirected | |
| h | NL URL 404 (still a draft) | EN URL does NOT redirect (guard holds) | |

Simulate preference with `?lang=` or the `proxuma_lang` cookie, and add a cache-buster query
to beat the CDN. Document how you simulated `CF-IPCountry` (it is edge-set; log the resolved
country/pref at origin behind a short-lived debug param you remove afterward, or use
`?lang=`). Leave no debug code behind.

## Safe dry-run

In safe mode do **not** edit the live plugins. Instead `scp` `proxuma-nl-redirect.php` to a
local scratch copy, add the pair there, `php -l` it to prove the edit is syntactically valid,
and report the diff. Do not upload it. Restore nothing on the server because nothing changed.

## Rollback

If anything misbehaves, restore from the timestamped backup:
```bash
$SSH "cd $WP_ROOT/wp-content/mu-plugins && \
      cp proxuma-nl-redirect.php.bak.$TS proxuma-nl-redirect.php && \
      cp proxuma-hreflang.php.bak.$TS   proxuma-hreflang.php && \
      php -l proxuma-nl-redirect.php"
```
Then `wp cache flush && wp sg purge`.
