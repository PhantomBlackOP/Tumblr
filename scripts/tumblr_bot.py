import feedparser

RSS_URL = "https://rss.trevorion.io/full-feed.xml"
feed = feedparser.parse(RSS_URL)

print("🔎 Feed Title:", feed.feed.get("title", "[No title]"))
print("🔢 Total entries:", len(feed.entries))

if not feed.entries:
    print("⚠️ No entries found in the feed.")
    exit()

print("\n--- First Entry Inspection ---\n")

entry = feed.entries[0]

for key, value in entry.items():
    preview = repr(value)
    if isinstance(value, str):
        preview = value.strip().replace("\n", " ")[:300]
    elif isinstance(value, list):
        preview = [str(v)[:100] for v in value]
    print(f"{key}:\n  {preview}\n")
