#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_source.py — turn a Proxuma content-package (or a plain article) into the
structured JSON the blog pipeline builds from.

Primary input is the content-package HTML we author: a <section id="s1b"> holding
the EN blog. Any other sections (the Dutch <section id="s1">, the LinkedIn / e-mail
/ video / DM cascade) are ignored.

Also handles a plainer single-article HTML file: if no s1b section exists, the
whole document body is parsed as one English post.

Usage:
    python3 parse_source.py "<path-to-source.html>" [--out parsed.json]

Output JSON shape:
{
  "languages": ["en"],
  "posts": {
    "en": {
      "lang": "en",
      "title": "...",
      "lede": "...",
      "blocks": [ {"type":"h", "text":"..."},
                  {"type":"p", "text":"...", "html":"..."},
                  {"type":"pull", "text":"..."},
                  {"type":"check", "n":"1", "text":"...", "html":"..."} ],
      "cta": {"headline":"...", "body":"...", "links":["https://..."]},
      "links": ["https://..."],
      "numbers": ["$847.41 billion", "9.9%", "80%", "215", "180", ...]
    }
  }
}

The "blocks" array preserves document order so the build phase can mirror the
structure 1:1. No words are altered, no facts invented — this only extracts.
"""
import sys, re, json, html, argparse

BLOG_TAGS = ("h2", "h3", "p", "div")

def _section(doc, sid):
    """Return inner HTML of <section id="sid">...</section> or None."""
    m = re.search(r'<section\b[^>]*\bid="%s"[^>]*>(.*?)</section>' % re.escape(sid),
                  doc, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else None

def _blog_inner(section_html):
    """Inner HTML of the .blog container inside a section (or the section itself)."""
    m = re.search(r'<div[^>]*\bclass="[^"]*\bblog\b[^"]*"[^>]*>(.*)</div>',
                  section_html, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else section_html

def _text(frag):
    """Strip tags -> plain text, unescape entities, collapse whitespace."""
    t = re.sub(r"<[^>]+>", "", frag)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def _inner_html(frag):
    return re.sub(r"\s+", " ", frag).strip()

def _links(frag):
    return re.findall(r'href="([^"]+)"', frag)

# numbers worth flagging for the numeric gate: currency, percentages, multipliers, bare counts
_NUM = re.compile(r"(\$[\d.,]+\s?(?:billion|million|B|M|K)?|"
                  r"\d[\d.,]*\s?%|\d[\d.,]*\s?(?:×|x)\b|\b\d{2,}\b)")

def _numbers(text):
    seen, out = set(), []
    for m in _NUM.findall(text):
        s = m.strip()
        if s and s not in seen:
            seen.add(s); out.append(s)
    return out

def parse_post(blog_html, lang):
    post = {"lang": lang, "title": "", "lede": "", "blocks": [],
            "cta": None, "links": [], "numbers": []}
    all_text = []

    # Walk top-level block elements in document order.
    for m in re.finditer(r'<(h2|h3|p|div)\b([^>]*)>(.*?)</\1>', blog_html, re.DOTALL | re.IGNORECASE):
        tag, attrs, inner = m.group(1).lower(), m.group(2), m.group(3)
        cls = (re.search(r'class="([^"]*)"', attrs) or [None, ""])[1]
        text = _text(inner)
        if not text and tag != "div":
            continue

        if tag == "h2" and "title" in cls and not post["title"]:
            post["title"] = text
        elif tag == "p" and "lede" in cls:
            post["lede"] = text; all_text.append(text)
        elif tag == "p" and "pull" in cls:
            post["blocks"].append({"type": "pull", "text": text}); all_text.append(text)
        elif tag in ("h2", "h3") and "title" not in cls:
            post["blocks"].append({"type": "h", "text": text}); all_text.append(text)
        elif tag == "div" and "cta" in cls:
            b = re.search(r'<b\b[^>]*>(.*?)</b>', inner, re.DOTALL | re.IGNORECASE)
            p = re.search(r'<p\b[^>]*>(.*?)</p>', inner, re.DOTALL | re.IGNORECASE)
            post["cta"] = {"headline": _text(b.group(1)) if b else "",
                           "body": _text(p.group(1)) if p else "",
                           "links": _links(inner)}
            all_text.append(_text(inner))
        elif tag == "p":
            chk = re.match(r'\s*<strong>\s*(\d+)\.', inner, re.IGNORECASE)
            if chk:
                post["blocks"].append({"type": "check", "n": chk.group(1),
                                       "text": text, "html": _inner_html(inner)})
            else:
                post["blocks"].append({"type": "p", "text": text, "html": _inner_html(inner)})
            all_text.append(text)
        post["links"].extend(_links(inner))

    post["links"] = sorted(set(post["links"]))
    post["numbers"] = _numbers(" ".join([post["lede"]] + all_text))
    return post

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    doc = open(args.source, encoding="utf-8").read()
    posts = {}

    en_sec = _section(doc, "s1b")
    if en_sec:
        # Content-package: parse only the EN blog (s1b); the Dutch s1 is ignored.
        posts["en"] = parse_post(_blog_inner(en_sec), "en")
    else:
        # Plain single-article fallback: parse the whole body as the English post.
        body = re.search(r"<body\b[^>]*>(.*)</body>", doc, re.DOTALL | re.IGNORECASE)
        posts["en"] = parse_post(body.group(1) if body else doc, "en")

    result = {"languages": list(posts.keys()), "posts": posts}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(out)
        # brief stderr summary so the operator sees what was found
        for lang, p in posts.items():
            print(f"[{lang}] title={p['title'][:60]!r} blocks={len(p['blocks'])} "
                  f"checks={sum(1 for b in p['blocks'] if b['type']=='check')} "
                  f"numbers={len(p['numbers'])} cta={'yes' if p['cta'] else 'no'}",
                  file=sys.stderr)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(out)

if __name__ == "__main__":
    main()
