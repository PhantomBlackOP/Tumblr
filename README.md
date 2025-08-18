# 🤖 Tumblr Auto Poster

Auto-posts your RSS feed to Tumblr daily using a GitHub Actions workflow and the Tumblr API.

## 🛠 Setup

1. Add these secrets in your GitHub repo:
   - `TUMBLR_CONSUMER_KEY`
   - `TUMBLR_CONSUMER_SECRET`
   - `TUMBLR_OAUTH_TOKEN`
   - `TUMBLR_OAUTH_TOKEN_SECRET`
2. Edit your RSS feed in `scripts/tumblr_bot.py` (default: `https://rss.trevorion.io/full-feed.xml`)
3. Run manually via Actions, or let it auto-run daily at 08:00 UTC

## 📁 File Structure

- `scripts/tumblr_bot.py`: The main script
- `.github/workflows/tumblr.yml`: Automation workflow

