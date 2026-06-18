# Blogger Setup Guide for daemon018
## Step-by-step to enable auto-posting

---

## STEP 1: Create Blogger Blog (2 minutes)

1. Go to **https://blogger.com**
2. Sign in with your Google account
3. Click **"Create New Blog"**
4. **Blog name:** `daemon018`
5. **Blog address:** `daemon018.blogspot.com`
6. **Theme:** Choose any (we only use the API)
7. Click **"Create blog"**

**Your blog is now live at: https://daemon018.blogspot.com**

---

## STEP 2: Enable Blogger API (5 minutes)

1. Go to **https://console.cloud.google.com**
2. Create a new project: `daemon018-blog`
3. Go to **APIs & Services → Library**
4. Search for **"Blogger API v3"**
5. Click **Enable**
6. Go to **APIs & Services → Credentials**
7. Click **Create Credentials → OAuth client ID**
8. Application type: **Desktop app**
9. Name: `daemon018-poster`
10. Click **Create**
11. Download the JSON file
12. Save it as: `~/sec-hunter-blog/scripts/blogger_credentials.json`

---

## STEP 3: Get Blog ID

1. Go to your blog: https://daemon018.blogspot.com
2. Look at the URL when you click "Settings"
3. Or use this API call:

```bash
# After setting up credentials, run:
python3 ~/sec-hunter-blog/scripts/blogger-setup.py
```

The blog ID is a long number like `1234567890123456789`

---

## STEP 4: Configure the Auto-Poster

1. Edit `~/sec-hunter-blog/scripts/blogger-config.json`:
```json
{
    "blog_id": "YOUR_BLOG_ID_HERE",
    "blog_url": "https://daemon018.blogspot.com"
}
```

2. Run the setup to authenticate:
```bash
python3 ~/sec-hunter-blog/scripts/blogger-setup.py
```

3. This will open a browser for Google OAuth
4. Grant permission
5. Token is saved automatically

---

## STEP 5: Test Auto-Posting

```bash
# Test with a sample post
python3 ~/sec-hunter-blog/scripts/blogger-poster.py
```

If successful, you'll see:
```
✅ Posted to Blogger successfully!
Post ID: xxxxxxxxx
URL: https://daemon018.blogspot.com/2026/06/your-post-title.html
```

---

## STEP 6: Enable Auto-Posting in Cron

The cron job is already set up. Once credentials are configured,
every AI-generated post will automatically publish to Blogger.

```bash
# Check cron
crontab -l

# Check logs
tail -f ~/sec-hunter-blog/scripts/logs/cron.log
```

---

## STEP 7: Apply for AdSense (After 10-15 Posts)

1. Go to **https://www.google.com/adsense**
2. Sign in with your Google account
3. Add your blog: `https://daemon018.blogspot.com`
4. Add the AdSense code to your blog
5. Wait for approval (usually 1-7 days for Blogger)
6. Start earning from ads!

---

## TROUBLESHOOTING

### "Access token expired"
Run: `python3 scripts/blogger-setup.py` to refresh

### "Blog ID not found"
Check: `cat scripts/blogger-config.json`

### "HTTP 403: Forbidden"
Make sure Blogger API is enabled in Google Cloud Console

### "HTTP 401: Unauthorized"
Re-run the OAuth setup to get a fresh token

---

## FILES CREATED

| File | Purpose |
|------|---------|
| `scripts/blogger_credentials.json` | Google API credentials (you add this) |
| `scripts/blogger-config.json` | Blog ID and URL config |
| `scripts/blogger_token.json` | OAuth token (auto-generated) |
| `scripts/blogger-poster.py` | Auto-posts to Blogger |
| `scripts/blogger-setup.py` | Initial setup and auth |

---

## EXPECTED TIMELINE

| Day | Action | Result |
|-----|--------|--------|
| 1 | Create Blogger + API setup | Blog live |
| 2 | Configure auto-posting | First AI post published |
| 3-14 | 10-15 AI posts published | Content building |
| 15 | Apply for AdSense | Application submitted |
| 15-22 | AdSense approval | Ads start showing |
| 22+ | Earning from ads | $1-$10/day initially |
| 30+ | 30+ posts, growing traffic | $5-$20/day |
| 60+ | 60+ posts, SEO kicking in | $10-$50/day |
| 90+ | 90+ posts, established blog | $20-$100/day |

---

*Once set up, the system runs 100% automatically. AI writes posts, publishes to Blogger, and AdSense pays you.*
