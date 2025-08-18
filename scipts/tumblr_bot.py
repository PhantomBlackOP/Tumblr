import os
import feedparser
from requests_oauthlib import OAuth1Session

# Load secrets from GitHub Actions environment
CONSUMER_KEY = os.environ["TUMBLR_CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["TUMBLR_CONSUMER_SECRET"]
OAUTH_TOKEN = os.environ["TUMBLR_OAUTH_TOKEN"]
OAUTH_TOKEN_SECRET = os.environ["TUMBLR_OAUTH_TOKEN_SECRET"]

# Static config (or make these secrets too)
BLOG_HOSTNAME = "trevorion.tumblr.com"
RSS_URL = "https://rss.trevorion.io/full-feed.xml"

# OAuth session
tumblr = OAuth1Session(
    CONSUMER_KEY,
    client_secret=CONSUMER_SECRET,
    resource_owner_key=OAUTH_TOKEN,
    resource_owner_secret=OAUTH_TOKEN_SECRET
)

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
    else:
        print(f"❌ Failed: {title} — {response.status_code}\n{response.text}")

def run():
    feed = feedparser.parse(RSS_URL)
    for entry in feed.entries[:5]:
        title = entry.title
        body = entry.summary
        tags = [tag.term for tag in entry.tags] if "tags" in entry else []
        post_to_tumblr(title, body, tags)

if __name__ == "__main__":
    run()
