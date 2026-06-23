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

2. **Read both plugins fully** before editing. The live `proxuma-nl-redirect.php` holds the
   blog pair as **three constants and two dedicated `if` blocks**, not a map:
   ```php
   define('PROXUMA_BLOG_EN', '/the-msp-market-is-doubling-to-847-billion');
   define('PROXUMA_BLOG_NL', '/de-msp-markt-verdubbelt-naar-847-miljard');
   define('PROXUMA_BLOG_NL_SLUG', 'de-msp-markt-verdubbelt-naar-847-miljard');
   function proxuma_blog_nl_live() { /* true only when the NL post is published */ }
   // inside proxuma_nl_redirect(): if ($norm === PROXUMA_BLOG_EN) {...}  if ($norm === PROXUMA_BLOG_NL) {...}
   ```
   `proxuma-hreflang.php` holds the pair as a hardcoded `proxuma_hreflang_blog_pair()`
   function. So adding a pair is NOT a one-line map entry; you mirror this structure.

3. **Add the pair to `proxuma-nl-redirect.php`, additively.** Lowest-risk pattern (verified
   `php -l` clean, zero existing lines removed): add a parallel set of constants, a parallel
   `proxuma_blog2_nl_live()` guard, and two parallel `if` blocks for the new pair. Touch
   nothing existing:
   ```php
   /* Second blog pair -- ADDITIVE, existing pair untouched. */
   define('PROXUMA_BLOG2_EN', '/<EN_SLUG>');
   define('PROXUMA_BLOG2_NL', '/<NL_SLUG>');
   define('PROXUMA_BLOG2_NL_SLUG', '<NL_SLUG>');

   function proxuma_blog2_nl_live() {
       $p = get_page_by_path(PROXUMA_BLOG2_NL_SLUG, OBJECT, 'post');
       return $p && $p->post_status === 'publish';
   }
   // inside proxuma_nl_redirect(), after the existing blog blocks:
   if ($norm === PROXUMA_BLOG2_EN) {
       if (proxuma_resolve_lang() === 'nl' && proxuma_blog2_nl_live()) proxuma_do_redirect(PROXUMA_BLOG2_NL . '/');
       return;
   }
   if ($norm === PROXUMA_BLOG2_NL) {
       if (proxuma_resolve_lang() === 'en') proxuma_do_redirect(PROXUMA_BLOG2_EN . '/');
       return;
   }
   ```
   > For the third pair and beyond, prefer a one-time refactor to a
   > `$proxuma_blog_pairs = [[EN, NL, NL_SLUG], ...]` array iterated in a loop, so each new
   > article becomes a single array row. That refactor is a separate, tested change; for a
   > single new pair the additive-mirror above is safest.

4. **Add the pair to `proxuma-hreflang.php`** (additive). Mirror `proxuma_hreflang_blog_pair()`
   with a second function (or generalize it to loop the same pairs array), emitting
   `hreflang en` / `nl` / `x-default` (x-default -> the EN URL), staying a no-op until both
   posts are published. Leave the existing page-pair hreflang logic and the existing blog
   pair untouched.

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
