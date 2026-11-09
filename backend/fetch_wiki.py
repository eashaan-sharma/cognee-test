"""Step 2: download Middle-earth articles from Wikipedia as plain-text files.

How it works
1. Ask the Wikipedia API for every page in a few categories
   (and one level of sub-categories), e.g. "Middle-earth characters".
2. For each page, ask the API for the article as plain text.
3. Cut off the reference sections, then save it as data/raw/<Title>.txt,
   with the title and source URL at the top (this is our provenance).

Run:  uv run python backend/fetch_wiki.py --max 10
"""
import argparse
import re
import time

import requests

from config import RAW_DIR

API = "https://en.wikipedia.org/w/api.php"

# Wikipedia asks every script to identify itself with a User-Agent.
HEADERS = {"User-Agent": "cognee-test-demo/0.1 (https://github.com/eashaan-sharma; research demo)"}

CATEGORIES = [
    "Middle-earth characters",
    "Middle-earth locations",
    "Middle-earth objects",
]

# Sections that are lists of sources, not content. Everything from the first one onward is dropped.
CUT_SECTIONS = ("References", "Notes", "Sources", "Citations", "Further reading",
                "External links", "See also", "Bibliography")


def api_get(params):
    """One call to the Wikipedia API, returning the JSON as a dict."""
    params = {**params, "format": "json", "formatversion": 2}
    response = requests.get(API, params=params, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def category_pages(category, depth, seen_categories):
    """All article titles in a category, going `depth` levels into sub-categories."""
    if category in seen_categories:
        return []
    seen_categories.add(category)

    titles = []
    params = {"action": "query", "list": "categorymembers",
              "cmtitle": f"Category:{category}", "cmlimit": 500, "cmtype": "page|subcat"}
    while True:
        data = api_get(params)
        for member in data["query"]["categorymembers"]:
            if member["ns"] == 0:  # namespace 0 = a normal article
                titles.append(member["title"])
            elif member["ns"] == 14 and depth > 0:  # namespace 14 = a sub-category
                sub = member["title"].removeprefix("Category:")
                titles += category_pages(sub, depth - 1, seen_categories)
        if "continue" not in data:  # the API returns results in pages of up to 500
            break
        params.update(data["continue"])
    return titles


def article_text(title):
    """The article as plain text (no HTML, no infobox), with reference sections removed."""
    data = api_get({"action": "query", "prop": "extracts", "explaintext": 1,
                    "redirects": 1, "titles": title})
    page = data["query"]["pages"][0]
    text = page.get("extract", "")

    # Plain-text headings look like "== References ==". Stop at the first source-list heading.
    pattern = r"\n=+\s*(" + "|".join(CUT_SECTIONS) + r")\s*=+"
    match = re.search(pattern, text)
    if match:
        text = text[: match.start()]
    return text.strip()

def is_in_universe(title):
    """Keep articles about Middle-earth itself; drop lists and real-world films/production."""
    if title.startswith("List of") or "(disambiguation)" in title:
        return False
    if "film" in title.lower() or title.startswith("Production of"):
        return False
    if ": " in title:  # film and game titles look like "The Lord of the Rings: The Return of the King"
        return False
    return True

def resolve_and_rank(titles):
    """Follow redirects, drop duplicates and list pages, and sort by article size (biggest first).

    Many category entries are redirects: e.g. "Alfrid" just points to a list of minor characters.
    Asking for page info with redirects=1 tells us the real target page and its size in bytes.
    """
    pages = {}
    for i in range(0, len(titles), 50):  # the API accepts up to 50 titles per call
        data = api_get({"action": "query", "prop": "info", "redirects": 1,
                        "titles": "|".join(titles[i:i + 50])})
        for page in data["query"]["pages"]:
            if page.get("missing") or page["ns"] != 0:
                continue
            pages[page["title"]] = page["length"]  # same target twice -> stored once
        real = {t: n for t, n in pages.items() if is_in_universe(t)}
    return sorted(real, key=real.get, reverse=True)


def safe_filename(title):
    """Windows doesn't allow characters like : ? / in file names."""
    return re.sub(r'[\\/:*?"<>|]', "_", title) + ".txt"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max", type=int, default=100, help="how many articles to save")
    parser.add_argument("--depth", type=int, default=1, help="how deep to go into sub-categories")
    parser.add_argument("--min-chars", type=int, default=1500, help="skip stubs shorter than this")
    args = parser.parse_args()

    # 1. Collect titles from all categories, then resolve redirects and rank by size.
    seen_categories = set()
    titles = []
    for category in CATEGORIES:
        found = category_pages(category, args.depth, seen_categories)
        print(f"{category}: {len(found)} articles")
        titles += found
    titles = resolve_and_rank(list(dict.fromkeys(titles)))
    print(f"{len(titles)} unique real articles after following redirects\n")

    # 2. Download until we have --max articles saved.
    saved = 0
    for title in titles:
        if saved >= args.max:
            break
        path = RAW_DIR / safe_filename(title)
        if path.exists():  # already downloaded in an earlier run
            saved += 1
            continue

        text = article_text(title)
        if len(text) < args.min_chars:
            print(f"  skip (too short): {title}")
            continue

        url = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
        path.write_text(f"Title: {title}\nSource: {url}\n\n{text}\n", encoding="utf-8")
        saved += 1
        print(f"  [{saved}/{args.max}] {title} ({len(text):,} chars)")
        time.sleep(0.2)  # be polite to Wikipedia's servers

    print(f"\nDone. {saved} articles in {RAW_DIR}")


if __name__ == "__main__":
    main()
