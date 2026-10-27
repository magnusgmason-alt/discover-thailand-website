"""Generate highlights.html (served at /highlights) from highlights_content.py.

Reuses the homepage's styles, header and footer. build.py runs it.
"""
import html
import json
import re
from pathlib import Path

from highlights_content import CATEGORIES, HIGHLIGHTS

ROOT = Path(__file__).parent
from site_config import SITE
HERO = "hx-longtail-cliffs"

index = (ROOT / "index.html").read_text(encoding="utf8")
STYLE = re.search(r"<style>(.*?)</style>", index, re.S).group(1)
FONTS = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', index).group(0)
HEADER = re.search(r'<header class="site-header".*?</header>', index, re.S).group(0)
FOOTER = re.search(r'<footer class="site-footer">.*?</footer>', index, re.S).group(0)
SCRIPT = re.search(r"<script>(.*?)</script>", index, re.S).group(1)


def sitewide(fragment):
    fragment = fragment.replace('href="#top"', 'href="/"')
    return re.sub(r'href="#([a-z-]+)"', r'href="/#\1"', fragment)


HEADER = sitewide(HEADER).replace('href="/highlights"', 'href="/highlights" aria-current="page"')
FOOTER = sitewide(FOOTER)
# Keep only the header/menu part of the homepage script (no sign-up form here).
SCRIPT = SCRIPT.split("// Checklist sign-up")[0] + "\n})();"

PAGE_CSS = """
/* Highlights page */
.hx-hero { position: relative; min-height: 70svh; display: flex; align-items: flex-end; overflow: hidden; background: var(--night); color: var(--white); }
.hx-hero .bg { -webkit-mask-image: linear-gradient(180deg, #000 55%, transparent 100%); mask-image: linear-gradient(180deg, #000 55%, transparent 100%); }
.hx-hero .shade { background: linear-gradient(180deg, rgba(10, 17, 22, 0.55) 0%, rgba(10, 17, 22, 0.15) 40%, rgba(10, 17, 22, 0.55) 75%, var(--night) 100%); }
.hx-hero .container { position: relative; padding-top: calc(var(--header-h) + 60px); padding-bottom: 40px; }
.hx-hero h1 { font-family: var(--serif); font-weight: 700; font-size: clamp(2.6rem, 7vw, 5.2rem); letter-spacing: -0.01em; line-height: 1; }
.hx-hero .rule { display: block; width: 64px; height: 3px; background: var(--red); margin: 24px 0 18px; }
.hx-hero .lead { color: rgba(255, 255, 255, 0.88); }

.filters { position: sticky; top: var(--header-h); z-index: 20; background: rgba(10, 17, 22, 0.92); backdrop-filter: blur(10px); border-bottom: 1px solid var(--line); }
.filters .container { display: flex; gap: 8px; padding-top: 14px; padding-bottom: 14px; overflow-x: auto; scrollbar-width: none; }
.filters .container::-webkit-scrollbar { display: none; }
.chip { flex: none; background: transparent; color: var(--frost); border: 1px solid rgba(232, 238, 241, 0.3); border-radius: 999px; padding: 9px 16px; font: 600 0.72rem var(--sans); letter-spacing: 0.14em; text-transform: uppercase; cursor: pointer; transition: background 0.2s, color 0.2s, border-color 0.2s; }
.chip:hover { border-color: var(--frost); }
.chip[aria-pressed="true"] { background: var(--frost); color: var(--night); border-color: var(--frost); }
.chip .n { opacity: 0.55; margin-left: 6px; }

.hx-count { color: var(--mist); font-size: 0.85rem; margin: 36px 0 0; }
.hx-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 44px 28px; margin: 24px 0 0; padding: 0; list-style: none; }
.hx { display: flex; flex-direction: column; scroll-margin-top: calc(var(--header-h) + 80px); }
.hx[hidden] { display: none; }
.hx-img { position: relative; display: block; border-radius: var(--radius); overflow: hidden; aspect-ratio: 4 / 5; background: var(--night-2); }
.hx-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.8s; }
.hx:hover .hx-img img { transform: scale(1.04); }
.hx-img::after { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(10, 17, 22, 0) 55%, rgba(10, 17, 22, 0.6)); }
.hx-tags { position: absolute; z-index: 1; top: 12px; left: 12px; right: 12px; display: flex; flex-wrap: wrap; gap: 6px; }
.hx-tags span { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; padding: 5px 9px; border-radius: 2px; background: rgba(10, 17, 22, 0.55); backdrop-filter: blur(6px); color: var(--white); }
.hx-body { padding: 18px 2px 0; }
.hx-region { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: var(--glacier); }
.hx h2 { font-family: var(--serif); font-size: 1.55rem; line-height: 1.15; margin: 8px 0 10px; letter-spacing: 0; }
.hx p { color: var(--mist); font-size: 0.93rem; margin: 0; }
.hx-cta { text-align: center; padding: 88px 0 100px; }
.hx-cta h2 { font-size: clamp(1.8rem, 3.6vw, 2.6rem); }

@media (max-width: 1000px) { .hx-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) {
  .hx-grid { grid-template-columns: 1fr; gap: 40px; }
  .hx-img { aspect-ratio: 4 / 3; }
}
"""

FILTER_JS = """
<script>
(function () {
  var chips = document.querySelectorAll(".chip");
  var items = document.querySelectorAll(".hx");
  var count = document.getElementById("hxCount");
  function apply(cat) {
    var shown = 0;
    items.forEach(function (el) {
      var on = cat === "all" || el.getAttribute("data-cats").split(" ").indexOf(cat) > -1;
      el.hidden = !on;
      if (on) shown++;
    });
    chips.forEach(function (c) { c.setAttribute("aria-pressed", String(c.getAttribute("data-cat") === cat)); });
    count.textContent = shown + (shown === 1 ? " highlight" : " highlights");
  }
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      var cat = c.getAttribute("data-cat");
      apply(cat);
      try { history.replaceState(null, "", cat === "all" ? location.pathname : "#" + cat); } catch (e) {}
    });
  });
  var start = location.hash.slice(1);
  var known = Array.prototype.some.call(chips, function (c) { return c.getAttribute("data-cat") === start; });
  if (known) { apply(start); }
  else {
    apply("all");
    var target = start && document.getElementById(start);
    if (target) setTimeout(function () { target.scrollIntoView(); }, 50);
  }
})();
</script>
"""


def img_slot(h):
    return "hx-" + h["slug"]


def main():
    labels = dict(CATEGORIES)
    counts = {cid: sum(cid in h["cats"] for h in HIGHLIGHTS) for cid, _ in CATEGORIES}
    chips = f'<button class="chip" type="button" data-cat="all" aria-pressed="true">All<span class="n">{len(HIGHLIGHTS)}</span></button>'
    chips += "".join(
        f'<button class="chip" type="button" data-cat="{cid}" aria-pressed="false">{html.escape(label)}<span class="n">{counts[cid]}</span></button>'
        for cid, label in CATEGORIES if counts[cid]
    )
    cards = []
    for h in HIGHLIGHTS:
        s = img_slot(h)
        tags = "".join(f"<span>{html.escape(labels[c])}</span>" for c in h["cats"])
        cards.append(f"""      <li class="hx" id="{h['slug']}" data-cats="{' '.join(h['cats'])}">
        <div class="hx-img"><img src="/assets/img/{s}-800.jpg" srcset="/assets/img/{s}-800.jpg 800w, /assets/img/{s}-1800.jpg 1800w" sizes="(min-width: 1000px) 33vw, (min-width: 560px) 50vw, 100vw" alt="{html.escape(h['alt'])}"{' style="object-position: ' + h['pos'] + '"' if h.get('pos') else ''} loading="lazy" decoding="async"><div class="hx-tags">{tags}</div></div>
        <div class="hx-body"><p class="hx-region">{html.escape(h['region'])}</p><h2>{html.escape(h['name'])}</h2><p>{html.escape(h['text'])}</p></div>
      </li>""")
    ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Thailand highlights",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": h["name"], "url": f"{SITE}/highlights#{h['slug']}"}
            for i, h in enumerate(HIGHLIGHTS)
        ],
    }
    title = "Thailand Highlights: Temples, Islands, Beaches and More"
    desc = f"{len(HIGHLIGHTS)} of Thailand's best places, from Wat Arun and the Chao Phraya to Phang Nga Bay, Maya Bay and Erawan Falls. Filter by temples, Bangkok, beaches, islands, limestone cliffs and more."
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · Discover Thailand</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}/highlights">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Discover Thailand">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}/highlights">
<meta property="og:image" content="{SITE}/assets/img/{HERO}-1800.jpg">
<meta name="twitter:card" content="summary_large_image">
{FONTS}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{STYLE}{PAGE_CSS}</style>
</head>
<body>
{HEADER}
<main id="top">
  <section class="hx-hero">
    <img class="bg" src="/assets/img/{HERO}-1800.jpg" srcset="/assets/img/{HERO}-800.jpg 800w, /assets/img/{HERO}-1800.jpg 1800w" sizes="100vw" alt="A longtail boat on clear turquoise water below limestone cliffs" fetchpriority="high">
    <div class="shade"></div>
    <div class="container">
      <p class="eyebrow light">Thailand highlights</p>
      <h1>Where to go in Thailand.</h1>
      <span class="rule"></span>
      <p class="lead">Temples, island lagoons, limestone cliffs and white sand. Pick a theme to see only what you are after.</p>
    </div>
  </section>
  <nav class="filters" aria-label="Filter highlights">
    <div class="container">{chips}</div>
  </nav>
  <section class="container">
    <p class="hx-count" id="hxCount" aria-live="polite">{len(HIGHLIGHTS)} highlights</p>
    <ul class="hx-grid">
{chr(10).join(cards)}
    </ul>
  </section>
  <section class="hx-cta">
    <div class="container narrow">
      <p class="eyebrow">Plan the trip</p>
      <h2>Put it all on one route.</h2>
      <p class="lead center">The complete guide links these places into day trips and island-hopping routes, with maps for each region.</p>
      <div class="btn-row center-row"><a class="btn primary" href="/#guides">See the guides</a><a class="btn outline" href="/#journal">Read the journal</a></div>
    </div>
  </section>
</main>
{FOOTER}
<script>{SCRIPT}</script>
{FILTER_JS}
</body>
</html>
"""
    (ROOT / "highlights.html").write_text(page, encoding="utf8")
    print("page highlights")


if __name__ == "__main__":
    main()
