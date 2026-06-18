#!/usr/bin/env python3
"""
SecHunter Blog — Blogger Authentication (NO CARD REQUIRED)
Uses easyblogger to authenticate via browser OAuth
"""
import json
import os
import sys
import subprocess

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"
CONFIG_FILE = os.path.join(BLOG_DIR, "scripts", "blogger-config.json")

def main():
    print("=" * 60)
    print("  SecHunter Blog — Blogger Authentication")
    print("  NO CARD REQUIRED — Browser OAuth")
    print("=" * 60)
    print()
    
    # Check if easyblogger is installed
    try:
        import easyblogger
        print("✅ easyblogger is installed")
    except ImportError:
        print("Installing easyblogger...")
        result = subprocess.run(
            ["pip3", "install", "easyblogger"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"Install failed: {result.stderr[:200]}")
            print("Try: pip3 install easyblogger")
            sys.exit(1)
        print("✅ easyblogger installed")
    
    # Load config
    blog_id = ""
    blog_url = "https://daemon018.blogspot.com"
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        blog_id = config.get("blog_id", "")
        blog_url = config.get("blog_url", blog_url)
    
    if not blog_id:
        print()
        print("Enter your Blog ID.")
        print("To find it:")
        print("1. Go to https://daemon018.blogspot.com")
        print("2. View page source (Ctrl+U)")
        print("3. Search for 'blogId'")
        print("4. Copy the number (e.g., 1234567890123456789)")
        print()
        blog_id = input("Blog ID: ").strip()
        
        if not blog_id:
            print("ERROR: No blog ID provided!")
            sys.exit(1)
        
        # Save config
        config = {"blog_id": blog_id, "blog_url": blog_url}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print(f"Config saved to: {CONFIG_FILE}")
    
    print()
    print(f"Blog ID: {blog_id}")
    print(f"Blog URL: {blog_url}")
    print()
    print("Starting authentication...")
    print("A browser window will open. Sign in to Google and grant permission.")
    print()
    
    try:
        import easyblogger
        
        # This will open a browser for OAuth
        print("Authenticating with Blogger...")
        blog = easyblogger.Blogger(blog_id)
        
        # Test by getting blog info
        info = blog.get_blog_info()
        if info:
            print()
            print("=" * 60)
            print("  ✅ AUTHENTICATION SUCCESSFUL!")
            print("=" * 60)
            print()
            print(f"Blog Name: {info.get('name', 'N/A')}")
            print(f"Blog URL: {info.get('url', 'N/A')}")
            print(f"Posts: {info.get('posts', {}).get('totalItems', 'N/A')}")
            print()
            print("Your blog is now connected to the AI engine!")
            print("The cron job will auto-post new content daily.")
            print()
            
            # Update config with blog name
            config["blog_name"] = info.get("name", "")
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
        else:
            print("WARNING: Could not verify blog info, but auth may still work.")
            
    except Exception as e:
        print(f"Authentication error: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure you're signed in to the correct Google account")
        print("2. Make sure you granted all permissions")
        print("3. Try again: python3 scripts/blogger-auth.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
