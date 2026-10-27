# Discover Thailand

Landing page for Discover Thailand, hosted on Cloudflare Pages. Same design and layout as Discover Iceland.

## How it builds
- `index.html` is the site.
- Photos come from the "Thailand" collection on Pexels. The `SLOTS` list in `build.py` maps each image slot to a Pexels photo ID; the build downloads the photos and resizes them into `dist/assets/img/` (800 px and 1800 px versions). To use your own photo for a slot, add it to `photos/` and put its file name in place of the ID.
- Cloudflare Pages settings: build command `pip install pillow && python3 build.py`, build output directory `dist`.

## Domain
Set `SITE` in `site_config.py` to the final domain (for example `https://discoverthailand.org`). The build writes it into canonical links, the sitemap and robots.txt.

## Highlights page
`/highlights` is built from `highlights_content.py` by `make_highlights.py`. Add an entry (with a Pexels ID or a photo in `photos/`) to add a highlight; the category buttons update automatically.

## Journal
The three articles in `/blog` are built from `articles_content.py` by `make_articles.py`.

## Book covers
Add the final covers to `photos/` as `cover-guide.jpg`, `cover-islands.jpg`, `cover-bangkok.jpg` and `cover-food.jpg` (or .png). Until then the build makes a simple placeholder cover for each book.

## Sign-up form
Set `data-endpoint` on `<form id="signup">` in `index.html` to your form service URL. Until then the form does not collect addresses.
