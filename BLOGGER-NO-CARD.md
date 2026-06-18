# Blogger Setup — NO CARD REQUIRED
## daemon018.blogspot.com Auto-Posting Setup

---

## THE PROBLEM
Google Cloud requires a credit card to create OAuth credentials for posting.

## THE SOLUTION
Use **easyblogger** Python library — it handles authentication through your browser, no card needed.

---

## STEP 1: Create Blogger Blog (Done ✅)
Your blog is already live at: https://daemon018.blogspot.com

---

## STEP 2: Get Blog ID (No Card Needed)

### Option A: From Blog URL
1. Go to https://daemon018.blogspot.com
2. View page source (Ctrl+U)
3. Search for "blogId"
4. You'll find something like: `"blogId":"1234567890123456789"`

### Option B: From Blogger Dashboard
1. Go to https://www.blogger.com/blog/daemon018/settings
2. Look at the URL — it contains the blog ID
3. Or check Settings → Basic → Blog ID

### Option C: Use this script
```bash
python3 scripts/get-blog-id.py
```

**Save your blog ID. You'll need it in Step 4.**

---

## STEP 3: Install easyblogger (No Card Needed)

```bash
pip3 install easyblogger
```

This library handles authentication through your browser — no Google Cloud project needed!

---

## STEP 4: Configure Blog ID

Edit `scripts/blogger-config.json`:
```json
{
    "blog_id": "YOUR_BLOG_ID_HERE",
    "blog_url": "https://daemon018.blogspot.com"
}
```

---

## STEP 5: Authenticate (One-Time, No Card)

```bash
python3 scripts/blogger-auth.py
```

This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Grant permission to post to your blog
4. Save the token automatically

**No credit card needed!** This uses standard Google OAuth.

---

## STEP 6: Test Posting

```bash
python3 scripts/blogger-auto.py
```

If successful, you'll see:
```
✅ Posted successfully!
Post ID: xxxxxxxxx
URL: https://daemon018.blogspot.com/2026/06/your-post-title.html
```

---

## STEP 7: Enable Auto-Posting

The cron job is already set up. Once authenticated:
- Daily 6:00 AM: AI generates post
- Daily 6:30 AM: Auto-posts to Blogger

```bash
# Check cron
crontab -l

# Check logs
tail -f scripts/logs/blogger.log
```

---

## TROUBLESHOOTING

### "Browser doesn't open"
Run in a terminal that supports browser opening, or manually open the URL it prints.

### "Token expired"
Re-run: `python3 scripts/blogger-auth.py`

### "Blog ID not found"
Make sure you entered the correct blog ID in `blogger-config.json`

### "Permission denied"
Make sure you granted all permissions during OAuth.

---

## ALTERNATIVE: Manual Posting via Blogger API Key

If you prefer NOT to use OAuth at all:

1. Go to https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Copy the key
4. Use it for READ-ONLY operations (list posts, get blog info)

**Note:** POSTING requires OAuth. Reading can be done with API key.

---

## FILES

| File | Purpose |
|------|---------|
| `scripts/blogger-auth.py` | One-time OAuth authentication |
| `scripts/blogger-auto.py` | Auto-posts to Blogger |
| `scripts/blogger-config.json` | Blog ID and URL |
| `scripts/get-blog-id.py` | Gets blog ID from URL |

---

## EXPECTED TIMELINE

| Day | Action | Result |
|-----|--------|--------|
| 1 | Complete setup | Blog connected |
| 2 | First AI post published | Content building |
| 3-14 | 10-15 posts published | Traffic growing |
| 15 | Apply for AdSense | Application submitted |
| 15-22 | AdSense approval | Ads showing |
| 22+ | Earning! | $1-$10/day |

---

*Once set up, the system runs 100% automatically. No card needed. No manual work.*
