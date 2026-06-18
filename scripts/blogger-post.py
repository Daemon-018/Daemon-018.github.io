#!/usr/bin/env python3
"""
SecHunter Blog — Simple Blogger Poster
Uses Google API key for reading + OAuth token for posting
Simplified for Termux (no browser needed)
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"
CONFIG_FILE = os.path.join(BLOG_DIR, "scripts", "blogger-config.json")
TOKEN_FILE = os.path.join(BLOG_DIR, "scripts", "blogger_token.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def post_to_blogger(title, content, labels=None):
    """Post to Blogger using stored OAuth token"""
    config = load_config()
    blog_id = config.get("blog_id", "")
    
    if not blog_id:
        print("ERROR: No blog ID in config!")
        return False
    
    # Load token
    if not os.path.exists(TOKEN_FILE):
        print("ERROR: No token file! Run auth first.")
        print(f"Expected: {TOKEN_FILE}")
        return False
    
    with open(TOKEN_FILE) as f:
        token_data = json.load(f)
    
    access_token = token_data.get("access_token", "")
    if not access_token:
        print("ERROR: No access token!")
        return False
    
    # Build post
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
    payload = json.dumps({
        "kind": "blogger#post",
        "blog": {"id": blog_id},
        "title": title,
        "content": content,
        "labels": labels or [],
        "status": "LIVE"
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            post_url = result.get("url", "N/A")
            post_id = result.get("id", "N/A")
            print(f"✅ Posted successfully!")
            print(f"  Post ID: {post_id}")
            print(f"  URL: {post_url}")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else "No error body"
        print(f"HTTP Error {e.code}: {error_body[:500]}")
        
        if e.code == 401:
            print("\nToken expired! Need to re-authenticate.")
            print("Run: python3 scripts/blogger-auth.py")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    config = load_config()
    print(f"Blog: {config.get('blog_url', 'N/A')}")
    print(f"Blog ID: {config.get('blog_id', 'N/A')}")
    print()
    
    # Find latest post
    posts_dir = os.path.join(BLOG_DIR, "content", "posts")
    if not os.path.exists(posts_dir):
        print("ERROR: No posts directory!")
        sys.exit(1)
    
    post_files = sorted([f for f in os.listdir(posts_dir) if f.endswith(".md")], reverse=True)
    if not post_files:
        print("ERROR: No posts found!")
        sys.exit(1)
    
    latest_post = os.path.join(posts_dir, post_files[0])
    print(f"Posting: {post_files[0]}")
    
    with open(latest_post, "r") as f:
        content = f.read()
    
    # Extract title and body
    title = ""
    body = content
    tags = []
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].split("\n"):
                if line.startswith("title:"):
                    title = line.split("title:")[1].strip().strip('"')
                elif line.startswith("tags:"):
                    tags = [t.strip().strip('"') for t in line.split("tags:")[1].strip().strip("[]").split(",")]
            body = parts[2].strip()
    
    if not title:
        title = f"Cybersecurity Guide — {date.today().strftime('%B %d, %Y')}"
    
    print(f"Title: {title}")
    print(f"Tags: {tags}")
    print()
    
    # Post
    post_to_blogger(title, body, tags)

if __name__ == "__main__":
    main()
