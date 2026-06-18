#!/usr/bin/env python3
"""
SecHunter Blog — Blogger Auto-Poster (NO CARD REQUIRED)
Uses Blogger API v3 with API key for reading
Uses Google OAuth for posting (free, no card needed)

ALTERNATIVE: Use easyblogger library which handles auth simply
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import date

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"

# ============================================
# METHOD 1: Simple API Key (Read-only, no card)
# ============================================
def get_blog_info_api_key(blog_url, api_key):
    """Get blog info using just an API key — NO CARD NEEDED"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/byurl?url={blog_url}&key={api_key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def list_posts_api_key(blog_id, api_key, max_results=10):
    """List posts using API key — NO CARD NEEDED"""
    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts?maxResults={max_results}&key={api_key}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("items", [])
    except Exception as e:
        print(f"Error: {e}")
        return []

# ============================================
# METHOD 2: EasyBlogger (Post without card)
# ============================================
def install_easyblogger():
    """Install easyblogger library"""
    import subprocess
    result = subprocess.run(
        ["pip3", "install", "easyblogger"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0:
        print("✅ easyblogger installed successfully!")
        return True
    else:
        print(f"Install error: {result.stderr[:200]}")
        return False

def post_with_easyblogger(blog_id, title, content, labels=None):
    """Post to Blogger using easyblogger — handles auth automatically"""
    try:
        import easyblogger
        blog = easyblogger.Blogger(blog_id)
        post = blog.post(
            title=title,
            content=content,
            labels=labels or [],
            draft=False
        )
        print(f"✅ Posted successfully!")
        print(f"Post ID: {post.get('id', 'N/A')}")
        print(f"URL: {post.get('url', 'N/A')}")
        return True
    except ImportError:
        print("easyblogger not installed. Run install_easyblogger() first.")
        return False
    except Exception as e:
        print(f"Post error: {e}")
        return False

# ============================================
# METHOD 3: Direct HTTP POST with OAuth token
# ============================================
def post_direct_oauth(blog_id, access_token, title, content, labels=None):
    """Post directly to Blogger API using OAuth token"""
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
            print(f"✅ Posted: {result.get('url', 'N/A')}")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# ============================================
# MAIN — Post latest AI content to Blogger
# ============================================
def main():
    print("=" * 60)
    print("  SecHunter — Blogger Auto-Poster")
    print("=" * 60)
    print()
    
    # Blog configuration
    BLOG_URL = "https://daemon018.blogspot.com"
    BLOG_ID = ""  # Will be fetched automatically
    
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
    print(f"Latest post: {post_files[0]}")
    
    # Read post
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
    print(f"Body length: {len(body)} chars")
    print()
    
    # Try to post using easyblogger
    if BLOG_ID:
        print(f"Posting to blog ID: {BLOG_ID}")
        post_with_easyblogger(BLOG_ID, title, body, tags)
    else:
        print("No blog ID configured.")
        print("Run setup first to get your blog ID.")

if __name__ == "__main__":
    main()
