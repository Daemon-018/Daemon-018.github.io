#!/usr/bin/env python3
"""
SecHunter Blog — Blogger Setup Script
Run this once to authenticate with Google Blogger API
"""
import json
import os
import sys

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"
CREDENTIALS_FILE = os.path.join(BLOG_DIR, "scripts", "blogger_credentials.json")
TOKEN_FILE = os.path.join(BLOG_DIR, "scripts", "blogger_token.json")
CONFIG_FILE = os.path.join(BLOG_DIR, "scripts", "blogger-config.json")

def main():
    print("=" * 60)
    print("  SecHunter Blog — Blogger API Setup")
    print("=" * 60)
    print()
    
    # Check if credentials file exists
    if not os.path.exists(CREDENTIALS_FILE):
        print("ERROR: Blogger credentials file not found!")
        print(f"Expected: {CREDENTIALS_FILE}")
        print()
        print("To get credentials:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create project 'daemon018-blog'")
        print("3. Enable Blogger API v3")
        print("4. Create OAuth Desktop App credentials")
        print("5. Download JSON and save as scripts/blogger_credentials.json")
        print()
        print("See BLOGGER-SETUP.md for detailed steps.")
        sys.exit(1)
    
    # Load credentials
    with open(CREDENTIALS_FILE) as f:
        creds = json.load(f)
    
    client_id = creds.get("installed", {}).get("client_id", "")
    client_secret = creds.get("installed", {}).get("client_secret", "")
    
    if not client_id or not client_secret:
        print("ERROR: Invalid credentials file!")
        print("Make sure it has 'installed.client_id' and 'installed.client_secret'")
        sys.exit(1)
    
    print(f"Client ID: {client_id[:20]}...")
    print()
    
    # Generate OAuth URL
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    scope = "https://www.googleapis.com/auth/blogger"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    print("Open this URL in your browser:")
    print()
    print(auth_url)
    print()
    print("After granting permission, you'll get a code.")
    print("Paste the code below:")
    print()
    
    auth_code = input("Authorization code: ").strip()
    
    if not auth_code:
        print("ERROR: No code provided!")
        sys.exit(1)
    
    # Exchange code for token
    print("\nExchanging code for access token...")
    
    import urllib.request
    import urllib.parse
    
    token_url = "https://oauth2.googleapis.com/token"
    data = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }).encode()
    
    try:
        req = urllib.request.Request(token_url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            token_data = json.loads(resp.read())
        
        # Save token
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)
        
        print(f"Token saved to: {TOKEN_FILE}")
        print(f"Access token: {token_data.get('access_token', '')[:20]}...")
        print(f"Refresh token: {token_data.get('refresh_token', '')[:20]}...")
        
    except Exception as e:
        print(f"Error getting token: {e}")
        sys.exit(1)
    
    # Get blog ID
    print("\nFetching blog information...")
    
    access_token = token_data.get("access_token")
    blog_url = "https://daemon018.blogspot.com"
    
    try:
        api_url = f"https://www.googleapis.com/blogger/v3/blogs/byurl?url={blog_url}"
        req = urllib.request.Request(
            api_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            blog_info = json.loads(resp.read())
        
        blog_id = blog_info.get("id", "")
        blog_name = blog_info.get("name", "")
        blog_url = blog_info.get("url", "")
        
        print(f"Blog found!")
        print(f"  Name: {blog_name}")
        print(f"  ID: {blog_id}")
        print(f"  URL: {blog_url}")
        
        # Save config
        config = {
            "blog_id": blog_id,
            "blog_name": blog_name,
            "blog_url": blog_url
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\nConfig saved to: {CONFIG_FILE}")
        
    except Exception as e:
        print(f"Error fetching blog info: {e}")
        print("You can manually add the blog ID to blogger-config.json")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("  Setup COMPLETE!")
    print("=" * 60)
    print()
    print("Your Blogger blog is now connected to the AI engine.")
    print("Run 'python3 scripts/blogger-poster.py' to test posting.")
    print()
    print("The cron job will auto-post new AI-generated content daily.")

if __name__ == "__main__":
    main()
