"""Build the Discover Thailand site into dist/.

Photos come from the "Thailand" collection on Pexels (free to use under the
Pexels licence). The build downloads each photo by its Pexels ID into photos/
(kept between local builds, not committed), then resizes it into
dist/assets/img/ as 800 px and 1800 px wide versions. To use your own photo
for a slot, drop it into photos/ and put its file name in place of the ID.

Cloudflare Pages runs:
    pip install pillow && python3 build.py
with build output directory: dist
"""
import shutil
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from site_config import SITE

ROOT = Path(__file__).parent
PHOTOS = ROOT / "photos"
DIST = ROOT / "dist"
IMG = DIST / "assets" / "img"

# Image slot used in index.html -> Pexels photo ID (or a file name in photos/)
SLOTS = {
    "hero-longtail": 16840024,
    "strip-wat-arun": 30811254,
    "strip-tuk-tuks": 38921242,
    "strip-lagoon": 29007474,
    "strip-maya-bay": 1647110,
    "editions-skyline": 36527921,
    "guide-wat-arun-river": 11105012,
    "limestone-krabi": 19160369,
    "night-bangkok": 30516945,
    "journal-beach-aerial": 4159512,
    "journal-bangkok": 36751253,
    "journal-longtails": 797868,
    "seasons-tonsai": 14573824,
    "quiet-pandanus": 23643760,
    "checklist-beach": 29974430,
    "guides-islands": 31340332,
    "hl-wat-arun": 30811254,
    "hl-chao-phraya": 36786603,
    "hl-tuk-tuks": 35981262,
    "hl-skyline": 36751253,
    "hl-erawan": 4090081,
    "hl-phang-nga": 11967509,
    "hl-phi-phi": 14507005,
    "hl-maya-bay": 35134642,
    "hl-pileh": 30517086,
    "hl-ao-nang": 35126213,
    "hl-karon": 4159512,
    "hl-longtails": 797868,
}

# Book covers: add photos/cover-guide.jpg, cover-islands.jpg, cover-bangkok.jpg and
# cover-food.jpg (or .png) to replace the placeholders.
COVERS = {
    "cover-guide": "THE COMPLETE TRAVEL GUIDE",
    "cover-islands": "ISLANDS EDITION",
    "cover-bangkok": "BANGKOK EDITION",
    "cover-food": "STREET FOOD",
}

PAGE_FILES = ["index.html", "highlights.html", "robots.txt", "sitemap.xml"]
PAGE_DIRS = ["blog"]
UA = "Mozilla/5.0 (compatible; DiscoverThailandBuild/1.0)"


def photo_path(src):
    """Return a local file for a slot, downloading Pexels photos on first use."""
    if isinstance(src, str):
        return PHOTOS / src
    path = PHOTOS / f"pexels-{src}.jpg"
    if path.exists() and path.stat().st_size > 10_000:
        return path
    url = f"https://images.pexels.com/photos/{src}/pexels-photo-{src}.jpeg?auto=compress&cs=tinysrgb&w=2400"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            path.write_bytes(data)
            print("download", src, len(data) // 1024, "KB")
            return path
        except Exception as e:  # network hiccup: retry, then give up loudly
            print("download failed", src, e)
            time.sleep(2 * (attempt + 1))
    raise SystemExit(f"Could not download Pexels photo {src}")


def save_sizes(im, name, widths):
    im = im.convert("RGB")
    for w in widths:
        r = min(1, w / im.width)
        out = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
        out.save(IMG / f"{name}-{w}.jpg", quality=80, optimize=True, progressive=True)


def font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def placeholder_cover(subtitle):
    im = Image.new("RGB", (900, 1350), (14, 19, 23))
    d = ImageDraw.Draw(im)
    d.rectangle([90, 560, 190, 570], fill=(200, 32, 47))
    d.text((90, 600), "DISCOVER", font=font(64), fill=(255, 255, 255))
    d.text((90, 680), "THAILAND", font=font(64), fill=(255, 255, 255))
    d.text((90, 790), subtitle, font=font(32), fill=(170, 180, 186))
    return im


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    IMG.mkdir(parents=True)
    PHOTOS.mkdir(exist_ok=True)

    import make_articles
    make_articles.main()
    import make_highlights
    make_highlights.main()
    from highlights_content import HIGHLIGHTS
    for h in HIGHLIGHTS:
        SLOTS["hx-" + h["slug"]] = h["photo"]

    for f in PAGE_FILES:
        text = (ROOT / f).read_text(encoding="utf8").replace("__SITE__", SITE)
        (DIST / f).write_text(text, encoding="utf8")
    for d in PAGE_DIRS:
        shutil.copytree(ROOT / d, DIST / d)

    for slot, src in SLOTS.items():
        with Image.open(photo_path(src)) as im:
            save_sizes(im, slot, (800, 1800))
        print("photo", slot)

    for name, subtitle in COVERS.items():
        found = [p for p in (PHOTOS / f"{name}.jpg", PHOTOS / f"{name}.png") if p.exists()]
        if found:
            with Image.open(found[0]) as im:
                save_sizes(im, name, (500, 900))
            print("cover", name)
        else:
            save_sizes(placeholder_cover(subtitle), name, (500, 900))
            print("cover placeholder", name)


if __name__ == "__main__":
    main()
