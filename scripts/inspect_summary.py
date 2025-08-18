import feedparser
from bs4 import BeautifulSoup
import html

RSS_URL = "https://rss.trevorion.io/full-feed.xml"

feed = feedparser.parse(RSS_URL)
entry = feed.entries[0]

# Step 1: decode summary
decoded = html.unescape(entry.summary)

# Step 2: parse with soup
soup = BeautifulSoup(decoded, "html.parser")

# Step 3: find all strong sections
print("\n📌 <strong> tags found:")
for tag in soup.find_all("strong"):
    print(f"→ {tag.text.strip()}")

# Step 4: look for ul > li > a structure
print("\n🔍 First 3 <li> tweet links found anywhere:")
count = 0
for li in soup.find_all("li"):
    a = li.find("a")
    if a and a.get("href"):
        print(f"- {li.get_text(strip=True)} → {a['href']}")
        count += 1
    if count == 3:
        break

print("\n✅ Inspection complete.\n")
