import feedparser
from bs4 import BeautifulSoup
import html
import json
import os
from pytumblr import TumblrRestClient
import datetime

# === Config ===
RSS_URL = "https://rss.trevorion.io/full-feed.xml"
MEMORY_FILE = "scripts/memory.json"
MAX_POSTS = 5  # Set to None to disable cap
DRY_RUN = False
CATEGORIES = {
    "Dailies": "daily",
    "Fun": "papapun",
    "News": "news",
    "Article": "article"
}
EMOJIS = {
    "daily": "🎨",
    "papapun": "😂",
    "news": "🚖️",
    "article": "🧠"
}
TAG_MAP = {
    "daily": ["AnimeAI", "AIart", "Dailies"],
    "papapun": ["PapaPun", "DadJokes", "AnimeHumor"],
    "news": ["AInews", "AnimeIndustry"],
    "article": ["AIwriting", "AnimeAnalysis", "Trevorion"]
}

# === Tumblr Auth ===
client = TumblrRestClient(
    os.getenv("TUMBLR_CONSUMER_KEY"),
    os.getenv("TUMBLR_CONSUMER_SECRET"),
    os.getenv("TUMBLR_OAUTH_TOKEN"),
    os.getenv("TUMBLR_OAUTH_TOKEN_SECRET")
)

BLOG_NAME = "trevorion.tumblr.com"

# === Helpers ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        print("📂 No memory file found. Starting fresh.")
        return []

    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Corrupted memory file: {MEMORY_FILE}")
        print(f"   {e}")
        backup_path = MEMORY_FILE + ".corrupt_backup"
        os.rename(MEMORY_FILE, backup_path)
        print(f"🔐 Renamed corrupted file to {backup_path}")
        return []

    # Upgrade legacy string-only format
    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        print("🔄 Upgrading legacy memory format...")
        return [{"url": x, "section": "unknown", "label": "", "posted_at": None} for x in data]

    # Accept modern format, but sanitize
    if isinstance(data, list) and all(isinstance(x, dict) and "url" in x for x in data):
        cleaned = []
        for x in data:
            if not x.get("url"):
                continue
            cleaned.append({
                "url": x["url"],
                "section": x.get("section", "unknown"),
                "label": x.get("label", ""),
                "posted_at": x.get("posted_at", None)
            })
        return cleaned

    print(f"⚠️ Unrecognized memory format. Backing up and starting fresh.")
    backup_path = MEMORY_FILE + ".unrecognized_backup"
    os.rename(MEMORY_FILE, backup_path)
    return []

def save_memory(memory_records):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_records, f, indent=2)
    print(f"💾 Memory saved to {MEMORY_FILE} with {len(memory_records)} entries.")

def extract_links_from_section(soup, section_name):
    results = []
    print(f"\n🔍 Looking for section: {section_name}")
    for tag in soup.find_all("strong"):
        if tag.text.strip() == section_name + ":":
            ul = tag.parent.find_next_sibling("ul")
            if ul:
                for li in ul.find_all("li"):
                    a = li.find("a")
                    if a and a.get("href", "").startswith("http"):
                        print(f"   ✅ Found link: {a['href']}")
                        results.append((li.get_text(strip=True), a["href"]))
            break
    return results

def tumblr_caption(section_key, label, url):
    emoji = EMOJIS.get(section_key, "🔗")
    return f"{emoji} {label}<br>{url}"

# === Main ===
feed = feedparser.parse(RSS_URL)
memory_records = load_memory()
seen_urls = [item["url"] for item in memory_records]
new_links = []

for entry in feed.entries:
    decoded = html.unescape(entry.summary)
    soup = BeautifulSoup(decoded, "html.parser")

    for section, section_key in CATEGORIES.items():
        extracted = extract_links_from_section(soup, section)
        for label, tweet_url in extracted:
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

post_count = 0
now = datetime.datetime.utcnow().isoformat() + "Z"

for section_key, label, url in new_links:
    if MAX_POSTS is not None and post_count >= MAX_POSTS:
        print(f"\n🔐 MAX_POSTS limit of {MAX_POSTS} reached.")
        break

    if not label or len(label.strip()) < 3:
        label = "Untitled Post"
        print(f"⚠️ Empty or short label for {url} — using fallback.")

    tags = TAG_MAP.get(section_key, [section_key])
    tumblr_tags = [f"#{tag}" for tag in tags]

    if DRY_RUN:
        print(f"🥯 DRY RUN: Would post [{section_key}] {label} → {url}")
        memory_records.append({
            "url": url,
            "section": section_key,
            "label": label,
            "posted_at": None
        })
    else:
        try:
            if section_key in ["daily", "papapun"]:
                client.create_photo(
                    BLOG_NAME,
                    state="published",
                    source=url,
                    tags=tumblr_tags
                )
                print(f"📸 Photo posted: {label} → {url}")
            else:
                client.create_text(
                    BLOG_NAME,
                    state="published",
                    title=label,
                    body=url,
                    tags=tumblr_tags
                )
                print(f"📝 Text posted: {label} → {url}")
            post_count += 1
            memory_records.append({
                "url": url,
                "section": section_key,
                "label": label,
                "posted_at": now
            })
        except Exception as e:
            print(f"❌ Failed to post {url}: {e}")

save_memory(memory_records)
print(f"🧠 Saving tweet links to memory...")
print(f"🧠 Total records: {len(memory_records)}, New: {len(new_links)}, Posted: {post_count}")
