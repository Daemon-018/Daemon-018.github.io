# SecHunter Blog — Deployment Guide

## Option 1: GitHub Pages (Free)

### Step 1: Create GitHub Repository
1. Go to github.com and create a new repository named `sechunter.github.io`
2. Make it public

### Step 2: Push the blog
```bash
cd /data/data/com.termux/files/home/sec-hunter-blog/public
git init
git add .
git commit -m "Initial blog deployment"
git remote add origin https://github.com/sechunter/sechunter.github.io.git
git push -u origin main
```

### Step 3: Enable GitHub Pages
1. Go to repository Settings → Pages
2. Source: Deploy from branch → main
3. Your blog will be live at: https://sechunter.github.io

## Option 2: Cloudflare Pages (Free, Faster)

### Step 1: Create Cloudflare Account
1. Go to dash.cloudflare.com
2. Sign up for free

### Step 2: Create Pages Project
1. Go to Workers & Pages → Create application → Pages
2. Connect to GitHub repository
3. Build command: `hugo --minify`
4. Build output directory: `public`

### Step 3: Custom Domain (Optional)
1. Add your domain in Cloudflare
2. Update DNS nameservers
3. Your blog will be live at: https://blog.yourdomain.com

## Option 3: Netlify (Free)

### Step 1: Create Netlify Account
1. Go to netlify.com
2. Sign up for free

### Step 2: Deploy
1. Drag and drop the `public` folder
2. Or connect to GitHub repository
3. Your blog will be live at: https://sechunter.netlify.app

## Option 4: Self-Hosted (Your Own Server)

### Requirements
- A VPS (DigitalOcean, Linode, AWS) — $5/month
- A domain name — $10/year
- Nginx or Apache

### Setup
```bash
# On your server
apt install nginx
cp -r public/* /var/www/html/
# Configure nginx for your domain
```

## Recommended: GitHub Pages + Cloudflare

This gives you:
- **Free hosting** (GitHub Pages)
- **Free CDN** (Cloudflare)
- **Free SSL** (Cloudflare)
- **Custom domain** (optional)
- **Fast loading** (Cloudflare CDN)

## Monetization Setup

### 1. Google AdSense
1. Sign up for Google AdSense
2. Add ad code to blog template
3. Earn from ad impressions

### 2. Affiliate Links
1. Join affiliate programs (Burp Suite, HackTheBox, TryHackMe)
2. Add affiliate links to tool reviews
3. Earn commission on referrals

### 3. Sponsored Content
1. Once you have traffic, companies will pay for sponsored posts
2. Charge $100-$1000 per sponsored post

### 4. Digital Products
1. Sell security cheatsheets, templates, courses
2. Use Gumroad or LemonSqueezy
3. Passive income from each sale
