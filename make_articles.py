"""Generate the journal articles in blog/ from the content below.

Reuses the homepage's styles, header and footer so articles match the site.
Run: python3 make_articles.py   (build.py runs it automatically)
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
from site_config import SITE
CHECKED = "October 2026"
PUBLISHED = "2026-10-27"

index = (ROOT / "index.html").read_text(encoding="utf8")
STYLE = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
FONTS = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', index).group(0)
HEADER = re.search(r'<header class="site-header".*?</header>', index, re.S).group(0)
FOOTER = re.search(r'<footer class="site-footer">.*?</footer>', index, re.S).group(0)


def sitewide(fragment):
    """Point in-page links at the homepage."""
    fragment = fragment.replace('href="#top"', 'href="/"')
    return re.sub(r'href="#([a-z]+)"', r'href="/#\1"', fragment)


HEADER = sitewide(HEADER).replace('href="/#journal"', 'href="/#journal" aria-current="page"')
FOOTER = sitewide(FOOTER)

ARTICLE_CSS = """
/* Article */
.a-hero { position: relative; min-height: 72svh; display: flex; align-items: flex-end; color: var(--white); background: var(--ink); overflow: hidden; }
.a-hero .bg { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.a-hero .shade { background: linear-gradient(180deg, rgba(8, 12, 16, 0.55) 0%, rgba(8, 12, 16, 0.25) 35%, rgba(8, 12, 16, 0.82) 100%); }
.a-hero-inner { position: relative; width: 100%; max-width: 920px; margin: 0 auto; padding: calc(var(--header-h) + 40px) 24px 56px; }
.a-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin-bottom: 18px; }
.a-pill { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; border: 1px solid rgba(255, 255, 255, 0.45); border-radius: 999px; padding: 5px 12px; }
.a-cat { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: #ff8a93; }
.a-hero h1 { font-size: clamp(2.1rem, 5.4vw, 3.9rem); font-weight: 800; letter-spacing: -0.03em; line-height: 1.04; text-wrap: balance; max-width: 22ch; }
.a-hero .rule { display: block; width: 64px; height: 4px; background: var(--red); margin: 26px 0 14px; }
.a-by { font-size: 0.85rem; opacity: 0.85; margin: 0; }
.a-crumbs { font-size: 0.78rem; margin-bottom: 18px; opacity: 0.85; }
.a-crumbs a { text-decoration: none; border-bottom: 1px solid rgba(255, 255, 255, 0.4); }

.a-body { max-width: 760px; margin: 0 auto; padding: 56px 24px 24px; font-size: 1.07rem; line-height: 1.75; }
.a-body > p:first-child { font-size: 1.22rem; line-height: 1.65; }
.a-body p { max-width: 68ch; }
.a-body h2 { font-size: clamp(1.5rem, 3vw, 2rem); line-height: 1.2; margin: 2.4em 0 0.7em; scroll-margin-top: calc(var(--header-h) + 16px); text-wrap: balance; }
.a-body h3 { font-size: 1.15rem; margin: 1.6em 0 0.5em; }
.a-body ul, .a-body ol { padding-left: 1.3em; margin: 0 0 1.2em; }
.a-body li { margin-bottom: 0.45em; }
.a-body a { color: var(--red-dark); text-underline-offset: 3px; }
.a-body strong { font-weight: 700; }

.toc { background: var(--stone); border-left: 4px solid var(--red); border-radius: 0 var(--radius) var(--radius) 0; padding: 22px 26px; margin: 32px 0; }
.toc p { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: var(--red); margin-bottom: 10px; }
.toc ol { margin: 0; font-size: 0.98rem; }
.toc a { color: var(--ink); text-decoration: none; border-bottom: 1px solid rgba(14, 19, 23, 0.25); }
.toc a:hover { border-color: var(--red); }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 32px 0 8px; }
.stat { background: var(--teal); color: var(--white); border-radius: var(--radius); padding: 18px 18px 16px; border-top: 3px solid var(--red); }
.stat strong { display: block; font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; font-variant-numeric: tabular-nums; }
.stat span { display: block; margin-top: 8px; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.85; line-height: 1.4; }

.table-wrap { overflow-x: auto; margin: 20px 0 24px; border: 1px solid rgba(14, 19, 23, 0.12); border-radius: var(--radius); background: var(--white); }
.a-body table { width: 100%; border-collapse: collapse; font-size: 0.9rem; line-height: 1.45; font-variant-numeric: tabular-nums; }
.a-body th { text-align: left; font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; background: var(--ink); color: var(--white); padding: 11px 12px; white-space: nowrap; }
.a-body td { padding: 10px 12px; border-top: 1px solid rgba(14, 19, 23, 0.08); vertical-align: top; }
.a-body tbody tr:nth-child(even) td { background: #faf8f4; }

.callout { background: var(--white); border: 1px solid rgba(14, 19, 23, 0.1); border-top: 3px solid var(--red); border-radius: var(--radius); padding: 18px 22px; margin: 24px 0; }
.callout p:last-child { margin-bottom: 0; }

.a-figure { margin: 32px -24px; }
.a-figure img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
.a-figure figcaption { font-size: 0.8rem; color: var(--muted); padding: 8px 24px 0; }

.checked { font-size: 0.88rem; color: var(--muted); border-top: 1px solid rgba(14, 19, 23, 0.12); padding-top: 18px; margin-top: 40px; }
.sources { font-size: 0.86rem; color: var(--muted); }
.sources h2 { font-size: 0.78rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink); margin: 18px 0 10px; }
.sources a { color: var(--muted); }

.keep { background: var(--stone); padding: 64px 0 80px; margin-top: 56px; }
.keep h2 { font-size: clamp(1.6rem, 3vw, 2.2rem); text-align: center; margin-bottom: 0; }
.journal-card a.cover-link { display: block; }
.journal-card h3 a { text-decoration: none; }
.journal-card h3 a:hover { text-decoration: underline; text-underline-offset: 3px; }


/* Thailand: articles read on light paper; the hero photo dissolves into it */
body.article { background: var(--paper); color: var(--ink); }
.article .a-hero-inner { padding-bottom: 150px; }
.article .a-hero::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 130px; background: linear-gradient(180deg, rgba(245, 243, 238, 0), var(--paper)); }
.article .a-hero .bg { -webkit-mask-image: linear-gradient(180deg, #000 70%, transparent 100%); mask-image: linear-gradient(180deg, #000 70%, transparent 100%); }
.article .a-hero { background: var(--paper); }
.article .a-hero .shade { background: linear-gradient(180deg, rgba(10, 17, 22, 0.6) 0%, rgba(10, 17, 22, 0.25) 35%, rgba(10, 17, 22, 0.75) 80%, rgba(10, 17, 22, 0) 100%); }
.article .a-hero h1 { font-family: var(--serif); font-weight: 800; letter-spacing: -0.035em; }
.article .a-body h2 { color: var(--ink); }
.article .a-body a { color: var(--ink); }
.article .stat span { color: var(--white); }
.article .callout { color: var(--ink); }
.article .keep { background: var(--night); color: var(--frost); margin-top: 72px; padding-top: 88px; }
.article .keep h2 { color: var(--frost); }
.article .a-figure figcaption { color: var(--muted); }

@media (max-width: 760px) {
  .a-hero { min-height: 62svh; }
  .a-body { padding-top: 40px; font-size: 1.02rem; }
  .a-body > p:first-child { font-size: 1.1rem; }
}
"""

SCRIPT = """
<script>
(function () {
  var header = document.getElementById("header");
  var nav = document.getElementById("nav");
  var toggle = document.getElementById("navToggle");
  function onScroll() { header.classList.toggle("solid", window.scrollY > 40); }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  toggle.addEventListener("click", function () {
    var open = nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });
  var dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach(function (dd) {
    dd.querySelector(".dropdown-btn").addEventListener("click", function (e) {
      e.stopPropagation();
      var willOpen = !dd.classList.contains("open");
      dropdowns.forEach(function (o) { o.classList.remove("open"); });
      dd.classList.toggle("open", willOpen);
    });
  });
  document.addEventListener("click", function () {
    dropdowns.forEach(function (o) { o.classList.remove("open"); });
  });
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
</script>
"""


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def page(a, others):
    body = a["body"].strip()
    # Number the question headings and build the table of contents.
    heads = re.findall(r"<h2>(.*?)</h2>", body)
    for h in heads:
        body = body.replace(f"<h2>{h}</h2>", f'<h2 id="{slugify(h)}">{h}</h2>', 1)
    toc = "".join(f'<li><a href="#{slugify(h)}">{h}</a></li>' for h in heads)
    toc_html = f'<nav class="toc" aria-label="In this article"><p>In this article</p><ol>{toc}</ol></nav>'
    stats = "".join(f"<div class=\"stat\"><strong>{v}</strong><span>{k}</span></div>" for v, k in a["stats"])
    stats_html = f'<div class="stats-row">{stats}</div>' if stats else ""
    body = body.replace("<!--TOC-->", toc_html + stats_html, 1)

    words = len(re.sub(r"<[^>]+>", " ", body).split())
    minutes = max(3, round(words / 220))
    url = f"{SITE}/blog/{a['slug']}"
    img_url = f"{SITE}/assets/img/{a['image']}-1800.jpg"
    sources = "".join(f'<li><a href="{u}" rel="noopener">{html.escape(t)}</a></li>' for t, u in a["sources"])
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a["title"],
        "description": a["description"],
        "image": [img_url],
        "datePublished": PUBLISHED,
        "dateModified": PUBLISHED,
        "author": {"@type": "Organization", "name": "Discover Thailand", "url": SITE},
        "publisher": {"@type": "Organization", "name": "Discover Thailand", "url": SITE},
        "mainEntityOfPage": url,
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Discover Thailand", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Journal", "item": SITE + "/#journal"},
            {"@type": "ListItem", "position": 3, "name": a["short"], "item": url},
        ],
    }
    cards = "".join(
        f"""<article class="journal-card">
          <a class="cover-link" href="/blog/{o['slug']}"><img src="/assets/img/{o['image']}-800.jpg" alt="{html.escape(o['image_alt'])}" width="800" height="533" loading="lazy" decoding="async"></a>
          <div><span class="tags">{o['category']}</span><h3><a href="/blog/{o['slug']}">{o['short']}</a></h3><p>{o['teaser']}</p><a class="link-arrow" href="/blog/{o['slug']}">Read the guide →</a></div>
        </article>"""
        for o in others
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(a['title'])} · Discover Thailand</title>
<meta name="description" content="{html.escape(a['description'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Discover Thailand">
<meta property="og:title" content="{html.escape(a['title'])}">
<meta property="og:description" content="{html.escape(a['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img_url}">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<script type="application/ld+json">{json.dumps(ld)}</script>
<script type="application/ld+json">{json.dumps(crumbs)}</script>
<style>{STYLE}{ARTICLE_CSS}</style>
</head>
<body class="article">
{HEADER}
<main id="top">
  <section class="a-hero">
    <img class="bg" src="/assets/img/{a['image']}-1800.jpg" srcset="/assets/img/{a['image']}-800.jpg 800w, /assets/img/{a['image']}-1800.jpg 1800w" sizes="100vw" alt="{html.escape(a['image_alt'])}" fetchpriority="high">
    <div class="shade"></div>
    <div class="a-hero-inner">
      <p class="a-crumbs"><a href="/">Discover Thailand</a> / <a href="/#journal">Journal</a></p>
      <div class="a-meta"><span class="a-pill">{minutes} min read</span><span class="a-cat">{a['category']}</span></div>
      <h1>{a['title']}</h1>
      <span class="rule"></span>
      <p class="a-by">By Discover Thailand · Facts checked {CHECKED}</p>
    </div>
  </section>
  <article class="a-body">
    {body}
    <p class="checked">{a['checked_note']}</p>
    <div class="sources"><h2>Sources</h2><ul>{sources}</ul></div>
  </article>
  <section class="keep">
    <div class="container">
      <p class="eyebrow center">From the journal</p>
      <h2>Keep reading</h2>
      <div class="journal-grid">{cards}</div>
    </div>
  </section>
</main>
{FOOTER}
{SCRIPT}
</body>
</html>
"""


from articles_content import ARTICLES  # noqa: E402


def main():
    out = ROOT / "blog"
    out.mkdir(exist_ok=True)
    for a in ARTICLES:
        others = [o for o in ARTICLES if o is not a]
        (out / f"{a['slug']}.html").write_text(page(a, others), encoding="utf8")
        print("article", a["slug"])


if __name__ == "__main__":
    main()
