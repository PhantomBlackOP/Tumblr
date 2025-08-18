import os, json
import feedparser
from requests_oauthlib import OAuth1Session

# Load secrets
CONSUMER_KEY = os.environ["TUMBLR_CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["TUMBLR_CONSUMER_SECRET"]
OAUTH_TOKEN = os.environ["TUMBLR_OAUTH_TOKEN"]
OAUTH_TOKEN_SECRET = os.environ["TUMBLR_OAUTH_TOKEN_SECRET"]

BLOG_HOSTNAME = "trevorion.tumblr.com"
RSS_URL = "https://rss.trevorion.io/full-feed.xml"
MEMORY_FILE = "posted.json"

tumblr = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=OAUTH_TOKEN,
    resource_owner_secret=OAUTH_TOKEN_SECRET
)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_memory(posted):
    with open(MEMORY_FILE, "w") as f:
        json.dump(list(posted), f)

def post_to_tumblr(title, body, tags=[]):
    url = f"https://api.tumblr.com/v2/blog/{BLOG_HOSTNAME}/post"
    payload = {
        "type": "text",
        "title": title,
        "body": body,
        "tags": ",".join(tags)
    }
    response = tumblr.post(url, data=payload)
    if response.status_code == 201:
        print(f"✅ Posted: {title}")
        return True
    else:
        print(f"❌ Failed: {title} — {response.status_code}\n{response.text}")
        return False

def run():
    posted_links = load_memory()
    feed = feedparser.parse(RSS_URL)

    for entry in feed.entries:
        if entry.link in posted_links:
            continue

        title = entry.title
        body = entry.summary
        tags = [tag.term for tag in entry.tags] if "tags" in entry else []

        if post_to_tumblr(title, body, tags):
            posted_links.add(entry.link)

    save_memory(posted_links)

if __name__ == "__main__":
    run()
