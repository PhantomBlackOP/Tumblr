import feedparser
import html
import json
import os
from bs4 import BeautifulSoup

RSS_URL = "https://rss.trevorion.io/full-feed.xml"
MEMORY_FILE = "posted_tweets.json"

# Categories we recognize
CATEGORIES = {
    "Dailies": "daily",
    "Fun": "papapun",
    "News": "news",
    "Article": "article"
}

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_memory(posted):
    with open(MEMORY_FILE, "w") as f:
        json.dump(list(posted), f)

def extract_links_from_section(soup, section_name):
    results = []
    print(f"🔍 Looking for section: {section_name}")
    for tag in soup.find_all("strong"):
        tag_text = tag.text.strip()
        print(f" → Found <strong>: '{tag_text}'")
        if tag_text == section_name:
            ul = tag.parent.find_next_sibling("ul")
            if ul:
                for li in ul.find_all("li"):
                    a = li.find("a")
                    if a and a.get("href", "").startswith("http"):
                        print(f"   ✅ Found link: {a['href']}")
                        results.append((li.get_text(strip=True), a["href"]))
                    else:
                        print("   ⚠️ No valid <a> tag in <li>")
            else:
                print("   ⚠️ No <ul> after this <strong>")
            break
    return results

def run():
    feed = feedparser.parse(RSS_URL)
    posted = load_memory()
    to_post = []

    for entry in feed.entries:
        decoded = html.unescape(entry.summary)
        print("\n=== DECODED SUMMARY SAMPLE ===\n")
        print(decoded[:1500])
        print("\n==============================\n")        
        soup = BeautifulSoup(decoded, "html.parser")

        for label, kind in CATEGORIES.items():
            items = extract_links_from_section(soup, label)
            for text, url in items:
                if url in posted:
                    continue
                to_post.append((kind, text, url))

    print(f"\n🔍 Extracted {len(to_post)} new tweet links for posting:\n")

    for kind, text, url in to_post:
        print(f"[{kind.upper()}] {text}\n → {url}\n")

    print("\n✅ DRY RUN COMPLETE. No posts made.")
    print("🧠 Saving tweet links to memory...")
    posted.update([url for _, _, url in to_post])
    save_memory(posted)

if __name__ == "__main__":
    run()
