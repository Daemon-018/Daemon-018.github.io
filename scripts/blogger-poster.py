#!/usr/bin/env python3
"""
SecHunter Blog — Blogger Auto-Poster
Posts AI-generated content to Blogger (daemon018.blogspot.com)
Requires: Google API credentials (client_secret.json)
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import date, datetime

# ============================================
# BLOGGER API CONFIGURATION
# ============================================
BLOGGER_CONFIG = {
    "blog_id": "",  # Will be set after creating blog
    "client_secret_file": "scripts/blogger_credentials.json",
    "token_file": "scripts/blogger_token.json",
    "blog_url": "https://daemon018.blogspot.com"
}

# ============================================
# GOOGLE BLOGGER API
# ============================================
class BloggerPoster:
    def __init__(self):
        self.config = BLOGGER_CONFIG
        self.access_token = None
        self.blog_id = None
        self.load_config()
    
    def load_config(self):
        """Load Blogger configuration"""
        config_file = "scripts/blogger-config.json"
        if os.path.exists(config_file):
            with open(config_file) as f:
                config = json.load(f)
            self.blog_id = config.get("blog_id", "")
            print(f"Blog ID: {self.blog_id}")
        else:
            print("ERROR: Blogger config not found!")
            print("Run setup first: python3 scripts/blogger-setup.py")
    
    def get_access_token(self):
        """Get OAuth2 access token"""
        token_file = self.config["token_file"]
        if os.path.exists(token_file):
            with open(token_file) as f:
                token = json.load(f)
            self.access_token = token.get("access_token")
            return self.access_token
        return None
    
    def post_to_blogger(self, title, content, labels=None, is_draft=False):
        """Post content to Blogger via API"""
        if not self.access_token:
            self.get_access_token()
        
        if not self.access_token:
            print("ERROR: No access token. Run setup first.")
            return False
        
        if not self.blog_id:
            print("ERROR: No blog ID. Run setup first.")
            return False
        
        # Build the post payload
        payload = {
            "kind": "blogger#post",
            "blog": {"id": self.blog_id},
            "title": title,
            "content": content,
            "labels": labels or [],
            "status": "DRAFT" if is_draft else "LIVE"
        }
        
        # Make the API request
        url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts/"
        data = json.dumps(payload).encode()
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            },
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                post_id = result.get("id", "N/A")
                post_url = result.get("url", "N/A")
                print(f"Post published successfully!")
                print(f"  Post ID: {post_id}")
                print(f"  URL: {post_url}")
                return True
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else "No error body"
            print(f"HTTP Error {e.code}: {error_body[:500]}")
            return False
        except Exception as e:
            print(f"Error posting: {e}")
            return False
    
    def list_posts(self, max_results=10):
        """List recent posts on the blog"""
        if not self.access_token:
            self.get_access_token()
        
        url = f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts?maxResults={max_results}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                posts = result.get("items", [])
                print(f"Recent posts ({len(posts)}):")
                for post in posts:
                    print(f"  - {post.get('title', 'N/A')} ({post.get('status', 'N/A')})")
                return posts
        except Exception as e:
            print(f"Error listing posts: {e}")
            return []

# ============================================
# MAIN — Auto-post latest content
# ============================================
def main():
    """Post the latest AI-generated content to Blogger"""
    blog_dir = "/data/data/com.termux/files/home/sec-hunter-blog"
    posts_dir = os.path.join(blog_dir, "content", "posts")
    
    # Find the latest post
    if not os.path.exists(posts_dir):
        print("ERROR: No posts directory found!")
        sys.exit(1)
    
    post_files = sorted([f for f in os.listdir(posts_dir) if f.endswith(".md")], reverse=True)
    
    if not post_files:
        print("ERROR: No posts found!")
        sys.exit(1)
    
    latest_post = os.path.join(posts_dir, post_files[0])
    print(f"Latest post: {latest_post}")
    
    # Read the post
    with open(latest_post, "r") as f:
        content = f.read()
    
    # Extract frontmatter and content
    title = ""
    tags = []
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()
            
            for line in frontmatter.split("\n"):
                if line.startswith("title:"):
                    title = line.split("title:")[1].strip().strip('"')
                elif line.startswith("tags:"):
                    tags_str = line.split("tags:")[1].strip()
                    tags = [t.strip().strip('"') for t in tags_str.strip("[]").split(",")]
        else:
            body = content
    else:
        body = content
    
    if not title:
        title = f"Cybersecurity Post — {date.today().strftime('%Y-%m-%d')}"
    
    print(f"Title: {title}")
    print(f"Tags: {tags}")
    print(f"Content length: {len(body)} chars")
    
    # Post to Blogger
    poster = BloggerPoster()
    success = poster.post_to_blogger(title, body, labels=tags, is_draft=False)
    
    if success:
        print("\n✅ Posted to Blogger successfully!")
    else:
        print("\n❌ Failed to post to Blogger. Check credentials.")

if __name__ == "__main__":
    main()
