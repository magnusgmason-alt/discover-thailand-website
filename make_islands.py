"""Generate the island guides in islands/ and the homepage island picker.

Island text lives in islands_content.py. Each guide reuses the journal article
template (make_articles.page). build.py runs main() and puts picker_html() into
index.html where it finds <!--ISLAND_PICKER-->.
"""
import html
import json
from pathlib import Path

import make_articles
from islands_content import ISLANDS

ROOT = Path(__file__).parent
COASTS = {"andaman": "Andaman coast", "gulf": "Gulf coast", "east": "Eastern Gulf"}

# Schematic map of southern Thailand (rough lon/lat outline, not to scale).
OUTLINE = [
    (100.9, 13.4), (100.5, 13.5), (100.0, 13.4), (99.95, 12.6), (99.85, 11.8), (99.5, 11.0), (99.2, 10.4),
    (99.3, 9.4), (99.9, 9.1), (100.3, 8.4), (100.4, 7.3), (101.0, 6.9), (101.6, 6.8), (102.1, 6.2),
    (101.8, 5.8), (101.1, 5.7), (100.6, 6.4), (100.2, 6.5), (99.7, 6.9), (99.3, 7.5), (98.9, 8.0),
    (98.6, 8.2), (98.3, 8.3), (98.3, 8.9), (98.6, 9.9), (98.9, 10.8), (99.55, 11.8), (99.15, 13.0),
    (99.2, 14.0), (101.0, 14.0), (101.7, 12.7), (100.95, 12.65),
]
# Pin positions are nudged apart so the Andaman islands stay readable.
PINS = {
    "phuket": ((98.25, 7.95), "end", -14, 5),
    "koh-yao-noi": ((98.62, 8.45), "end", -14, -4),
    "krabi-railay": ((99.0, 8.2), "start", 14, 0),
    "koh-phi-phi": ((98.72, 7.55), "end", -14, 5),
    "koh-lanta": ((99.1, 7.4), "start", 14, 5),
    "koh-lipe": ((99.3, 6.5), "start", 14, 5),
    "koh-tao": ((99.85, 10.15), "start", 14, 5),
    "koh-phangan": ((100.05, 9.8), "start", 14, 5),
    "koh-samui": ((100.0, 9.45), "start", 14, 5),
    "koh-samet": ((101.45, 12.45), "middle", 0, 26),
}
LON0, LAT0, K = 96.8, 14.2, 66


def xy(lon, lat):
    return round((lon - LON0) * K + 20), round((LAT0 - lat) * K + 20)


def slot(i):
    return "isl-" + i["slug"]


def img_attrs(i):
    s = slot(i)
    return (f'src="/assets/img/{s}-800.jpg" srcset="/assets/img/{s}-800.jpg 800w, /assets/img/{s}-1800.jpg 1800w" '
            f'sizes="(min-width: 1000px) 50vw, 100vw" alt="{html.escape(i["image_alt"])}"')


def picker_html():
    first = ISLANDS[0]
    w, h = xy(102.3, 5.4)
    land = "M" + " L".join("{} {}".format(*xy(*p)) for p in OUTLINE) + " Z"
    # The coastline stroke skips the two straight edges where the map is cut off inland.
    coast_pts = OUTLINE[-2:] + OUTLINE[:-4]
    coast = "M" + " L".join("{} {}".format(*xy(*p)) for p in coast_pts)
    bx, by = xy(100.5, 13.75)
    pins = []
    for i in ISLANDS:
        (lon, lat), anchor, dx, dy = PINS[i["slug"]]
        x, y = xy(lon, lat)
        active = " active" if i is first else ""
        pins.append(
            f'<g class="isl-pin{active}" data-slug="{i["slug"]}" data-coast="{i["coast"]}" role="button" tabindex="0" aria-label="{html.escape(i["name"])}">'
            f'<circle cx="{x}" cy="{y}" r="7"/><text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{html.escape(i["name"])}</text></g>'
        )
    chips = "".join(
        f'<button class="isl-chip{" active" if i is first else ""}" type="button" data-slug="{i["slug"]}" data-coast="{i["coast"]}" aria-pressed="{str(i is first).lower()}">{html.escape(i["name"])}</button>'
        for i in ISLANDS
    )
    data = {
        i["slug"]: {
            "name": i["name"], "coast": COASTS[i["coast"]], "tagline": i["tagline"], "summary": i["summary"],
            "months": i["best_months"], "getting": i["getting_there"], "best": " · ".join(i["best_for"]),
            "img": slot(i), "alt": i["image_alt"],
        }
        for i in ISLANDS
    }
    return f"""<section class="section deep" id="islands">
    <div class="container">
      <p class="eyebrow center">The islands</p>
      <h2 class="center">Which island is yours?</h2>
      <p class="lead center">Thailand has two island coasts with rainy seasons at different times of year. Pick a coast, then tap an island to see what it is like, when to go and how to get there.</p>
      <div class="coast-tabs" role="group" aria-label="Choose a coast">
        <button class="coast-btn" type="button" data-coast="all" aria-pressed="true">All islands</button>
        <button class="coast-btn" type="button" data-coast="andaman" aria-pressed="false">Andaman coast</button>
        <button class="coast-btn" type="button" data-coast="gulf" aria-pressed="false">Gulf coast</button>
      </div>
      <div class="isl-pick">
        <div class="isl-nav">
          <svg class="isl-map" viewBox="0 0 {w} {h}" role="group" aria-label="Schematic map of Thailand's islands">
            <path class="land" d="{land}"/>
            <path class="coast" d="{coast}"/>
            <text class="sea" x="{xy(97.7, 9.9)[0]}" y="{xy(97.7, 9.9)[1]}" text-anchor="middle">Andaman Sea</text>
            <text class="sea" x="{xy(101.1, 11.5)[0]}" y="{xy(101.1, 11.5)[1]}" text-anchor="middle"><tspan x="{xy(101.1, 11.5)[0]}">Gulf of</tspan><tspan x="{xy(101.1, 11.5)[0]}" dy="15">Thailand</tspan></text>
            <g class="city"><rect x="{bx - 5}" y="{by - 5}" width="10" height="10"/><text x="{bx + 12}" y="{by + 4}">Bangkok</text></g>
            {''.join(pins)}
          </svg>
          <div class="isl-chips">{chips}</div>
          <p class="fine">Schematic map, not to scale.</p>
        </div>
        <article class="isl-panel" aria-live="polite">
          <img id="islImg" {img_attrs(first)} width="1800" height="1200" loading="lazy" decoding="async">
          <div class="isl-body">
            <p class="isl-coast" id="islCoast">{COASTS[first["coast"]]}</p>
            <h3 id="islName">{html.escape(first["name"])}</h3>
            <p class="isl-tagline" id="islTagline">{html.escape(first["tagline"])}</p>
            <p id="islSummary">{html.escape(first["summary"])}</p>
            <dl class="isl-facts">
              <div><dt>Best months</dt><dd id="islMonths">{html.escape(first["best_months"])}</dd></div>
              <div><dt>Getting there</dt><dd id="islGetting">{html.escape(first["getting_there"])}</dd></div>
              <div><dt>Best for</dt><dd id="islBest">{html.escape(" · ".join(first["best_for"]))}</dd></div>
            </dl>
            <a class="link-arrow" id="islLink" href="/islands/{first["slug"]}">Read the {html.escape(first["name"])} guide →</a>
          </div>
        </article>
      </div>
    </div>
    <script type="application/json" id="islData">{json.dumps(data, ensure_ascii=False)}</script>
    <script>{PICKER_JS}</script>
  </section>"""


PICKER_JS = """
(function () {
  var data = JSON.parse(document.getElementById("islData").textContent);
  var pins = document.querySelectorAll(".isl-pin");
  var chips = document.querySelectorAll(".isl-chip");
  var coastBtns = document.querySelectorAll(".coast-btn");
  var $ = function (id) { return document.getElementById(id); };
  var current = document.querySelector(".isl-chip.active").getAttribute("data-slug");
  function inCoast(el, coast) {
    var c = el.getAttribute("data-coast");
    return coast === "all" || c === coast || (coast === "gulf" && c === "east");
  }
  function show(slug) {
    var d = data[slug];
    if (!d) return;
    current = slug;
    var img = $("islImg");
    img.src = "/assets/img/" + d.img + "-800.jpg";
    img.srcset = "/assets/img/" + d.img + "-800.jpg 800w, /assets/img/" + d.img + "-1800.jpg 1800w";
    img.alt = d.alt;
    $("islCoast").textContent = d.coast;
    $("islName").textContent = d.name;
    $("islTagline").textContent = d.tagline;
    $("islSummary").textContent = d.summary;
    $("islMonths").textContent = d.months;
    $("islGetting").textContent = d.getting;
    $("islBest").textContent = d.best;
    $("islLink").href = "/islands/" + slug;
    $("islLink").textContent = "Read the " + d.name + " guide \\u2192";
    pins.forEach(function (p) { p.classList.toggle("active", p.getAttribute("data-slug") === slug); });
    chips.forEach(function (c) {
      var on = c.getAttribute("data-slug") === slug;
      c.classList.toggle("active", on);
      c.setAttribute("aria-pressed", String(on));
    });
  }
  function filter(coast) {
    coastBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-coast") === coast)); });
    pins.forEach(function (p) { p.classList.toggle("dim", !inCoast(p, coast)); });
    var first = null;
    chips.forEach(function (c) {
      var ok = inCoast(c, coast);
      c.hidden = !ok;
      if (ok && !first) first = c.getAttribute("data-slug");
    });
    var cur = document.querySelector('.isl-chip[data-slug="' + current + '"]');
    if (cur && cur.hidden && first) show(first);
  }
  pins.forEach(function (p) {
    p.addEventListener("click", function () { show(p.getAttribute("data-slug")); });
    p.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); show(p.getAttribute("data-slug")); }
    });
  });
  chips.forEach(function (c) { c.addEventListener("click", function () { show(c.getAttribute("data-slug")); }); });
  coastBtns.forEach(function (b) { b.addEventListener("click", function () { filter(b.getAttribute("data-coast")); }); });
})();
"""


CTA = """<div class="isl-cta">
      <p class="eyebrow">Discover Thailand · Islands Edition</p>
      <h2>Every island, in one book.</h2>
      <p>The Islands Edition covers the Andaman and Gulf islands in depth, with ferry routes, beach maps and which coast to pick in each month. Leave your email and we will tell you the day it launches.</p>
      <a class="btn primary" href="/#checklist">Notify me at launch</a>
    </div>"""


def main():
    out = ROOT / "islands"
    out.mkdir(exist_ok=True)
    for i in ISLANDS:
        # Keep reading: the other islands on the same coast first, then the rest.
        others = sorted((o for o in ISLANDS if o is not i), key=lambda o: o["coast"] != i["coast"])[:3]
        page = make_articles.page(i, others, section="islands", crumb=("Islands", "/#islands"),
                                  keep=("More islands", "Other islands to consider"), cta=CTA)
        page = page.replace('href="/#journal" aria-current="page"', 'href="/#journal"')
        page = page.replace('href="/#islands">Islands</a>', 'href="/#islands" aria-current="page">Islands</a>', 1)
        (out / f"{i['slug']}.html").write_text(page, encoding="utf8")
        print("island", i["slug"])


if __name__ == "__main__":
    main()
