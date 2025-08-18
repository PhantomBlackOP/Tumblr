import feedparser
from bs4 import BeautifulSoup
import html
import json
import os

# === Config ===
RSS_URL = "https://rss.trevorion.io/full-feed.xml"
MEMORY_FILE = "scripts/memory.json"
DRY_RUN = True  # Change to False to post for real
CATEGORIES = {
    "Dailies": "daily",
    "Fun": "papapun",
    "News": "news",
    "Article": "article"
}

# === Helpers ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_memory(seen_urls):
    with open(MEMORY_FILE, "w") as f:
        json.dump(seen_urls, f, indent=2)

def extract_links_from_section(soup, section_name):
    results = []
    print(f"\n🔍 Looking for section: {section_name}")
    for tag in soup.find_all("strong"):
        tag_text = tag.text.strip()
        print(f" → Found <strong>: '{tag_text}'")
        if tag_text == section_name + ":":
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

# === Main ===
feed = feedparser.parse(RSS_URL)
seen_urls = load_memory()
new_links = []

for entry in feed.entries:
    decoded = html.unescape(entry.summary)
    soup = BeautifulSoup(decoded, "html.parser")

    for section, section_key in CATEGORIES.items():
        extracted = extract_links_from_section(soup, section)
        for label, tweet_url in extracted:
            print(f"🧪 Raw extracted: {tweet_url}")
            if tweet_url not in seen_urls:
                new_links.append((section_key, label, tweet_url))
            else:
                print(f"⏩ Already seen: {tweet_url}")

# === Summary ===
print(f"\n🔍 Extracted {len(new_links)} new tweet links for posting:\n")
for section_key, label, url in new_links:
    prefix = {
        "daily": "[D]",
        "papapun": "[P]",
        "news": "[N]",
        "article": "[A]"
    }.get(section_key, "[?]")
    print(f"{prefix} {label} → {url}")

if DRY_RUN:
    print("\n✅ DRY RUN COMPLETE. No posts made.")
else:
    print("\n🚀 Posting to Tumblr...")
    for section_key, label, url in new_links:
        # Replace this with actual Tumblr API call
        print(f"📤 Posting: {label} → {url}")
        # Example:
        # tumblr.create_text_post(...)

# === Save Memory ===
seen_urls += [url for _, _, url in new_links]
seen_urls = list(set(seen_urls))
save_memory(seen_urls)
print("🧠 Saving tweet links to memory...")
