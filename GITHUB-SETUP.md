# GitHub Setup for daemon018 — DO THESE STEPS

## STEP 1: Create GitHub Repository (1 minute)

1. Go to https://github.com/new
2. **Repository name:** `Daemon-018.github.io`
3. **Description:** `daemon018 — AI-Powered Cybersecurity Blog`
4. **Visibility:** ✅ Public
5. **Do NOT** add README, .gitignore, or license (we have our own)
6. Click **"Create repository"**

---

## STEP 2: Create GitHub Personal Access Token (2 minutes)

1. Go to https://github.com/settings/tokens/new
2. **Note:** `daemon018-blog-token`
3. **Expiration:** 90 days (or No Expiration)
4. **Select scopes:** Check ALL of these:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages`
5. Click **"Generate token"**
6. **COPY THE TOKEN IMMEDIATELY** (shown only once!)
7. **Send me the token** so I can push the blog

---

## STEP 3: Add API Key as GitHub Secret (1 minute)

1. Go to https://github.com/Daemon-018/Daemon-018.github.io/settings/secrets/actions
2. Click **"New repository secret"**
3. **Name:** `OPENROUTER_API_KEY`
4. **Value:** (your OpenRouter API key)
5. Click **"Add secret"**

---

## STEP 4: Enable GitHub Pages (1 minute)

1. Go to https://github.com/Daemon-018/Daemon-018.github.io/settings/pages
2. **Source:** Deploy from a branch
3. **Branch:** main / root
4. Click **"Save"**

---

## STEP 5: Push Blog (I'll do this once you give me the token)

Once I have your PAT, I'll:
1. Push the blog code
2. Trigger the first AI post generation
3. Verify everything works
4. Your blog goes live at: https://Daemon-018.github.io

---

## AFTER SETUP

Your blog will be live at:
- **GitHub Pages:** https://Daemon-018.github.io
- **Blogger:** https://daemon018.blogspot.com

AI engine runs daily at 6:00 AM on GitHub Actions.
No need to keep your phone on.

---

## TROUBLESHOOTING

**"Could not resolve host: github.com"**
→ Check internet connection: `ping github.com`

**"Authentication failed"**
→ Regenerate PAT and send me the new one

**"Pages not showing"**
→ Wait 5-10 minutes after enabling Pages
→ Check: Settings → Pages → "Your site is published at..."
