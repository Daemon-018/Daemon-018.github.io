#!/usr/bin/env python3
"""
SecHunter Blog — Get Blog ID from URL
NO CARD REQUIRED — Uses public Blogger API
"""
import json
import urllib.request
import urllib.error
import os
import re
import sys

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"
CONFIG_FILE = os.path.join(BLOG_DIR, "scripts", "blogger-config.json")

def get_blog_id_from_url(blog_url):
    """Extract blog ID from Blogger URL"""
    # Try to get from page source
    try:
        req = urllib.request.Request(blog_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
            # Search for blogId in the HTML
            patterns = [
                r'"blogId":"(\d+)"',
                r'blogId["\s:]+(\d{10,})',
                r'blog/(\d+)',
                r'"blog_id":"(\d+)"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    return match.group(1)
    except Exception as e:
        print(f"Error fetching blog: {e}")
    
    return None

def get_blog_id_from_api(blog_url):
    """Get blog ID using Blogger API (no key needed for public blogs)"""
    # Try without API key first
    url = f"https://www.googleapis.com/blogger/v3/blogs/byurl?url={blog_url}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("id", "")
    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            print("API key required for this method.")
            print("Trying alternative method...")
        else:
            print(f"API Error: {e.code}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def main():
    print("=" * 60)
    print("  SecHunter Blog — Get Blog ID")
    print("  NO CARD REQUIRED")
    print("=" * 60)
    print()
    
    blog_url = "https://daemon018.blogspot.com"
    
    print(f"Blog URL: {blog_url}")
    print()
    print("Method 1: Extracting from page source...")
    blog_id = get_blog_id_from_url(blog_url)
    
    if not blog_id:
        print("Method 1 failed. Trying API...")
        blog_id = get_blog_id_from_api(blog_url)
    
    if blog_id:
        print(f"✅ Blog ID found: {blog_id}")
        
        # Save to config
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config = json.load(f)
        
        config["blog_id"] = blog_id
        config["blog_url"] = blog_url
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"Config saved to: {CONFIG_FILE}")
        print()
        print("Next step: Run authentication")
        print("  python3 scripts/blogger-auth.py")
    else:
        print("❌ Could not find blog ID automatically.")
        print()
        print("Manual method:")
        print("1. Go to https://daemon018.blogspot.com")
        print("2. Right-click → View Page Source")
        print("3. Search (Ctrl+F) for: blogId")
        print("4. Copy the number (e.g., 1234567890123456789)")
        print()
        manual_id = input("Paste blog ID here: ").strip()
        
        if manual_id:
            config = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE) as f:
                    config = json.load(f)
            
            config["blog_id"] = manual_id
            config["blog_url"] = blog_url
            
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Config saved. Blog ID: {manual_id}")
            print()
            print("Next step: Run authentication")
            print("  python3 scripts/blogger-auth.py")
        else:
            print("No blog ID provided. Exiting.")

if __name__ == "__main__":
    main()
