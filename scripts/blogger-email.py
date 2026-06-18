#!/usr/bin/env python3
"""
SecHunter Blog — Blogger Email Poster (NO CARD, NO API, NO OAUTH)
Uses Blogger's built-in email posting feature
Just send an email → post appears on blog
"""
import json
import os
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"
CONFIG_FILE = os.path.join(BLOG_DIR, "scripts", "blogger-config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

def post_via_email(title, content, email_address, email_password, blog_email):
    """
    Post to Blogger via email
    Blog email format: daemon018@blogger.com (or custom email from Blogger settings)
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = email_address
    msg["To"] = blog_email
    
    # Plain text version
    msg.attach(MIMEText(content, "plain"))
    
    # HTML version (Blogger supports HTML in emails)
    html_content = f"""
    <html>
    <body>
    {content.replace(chr(10), '<br>')}
    </body>
    </html>
    """
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_address, email_password)
            server.sendmail(email_address, blog_email, msg.as_string())
        
        print(f"✅ Email sent to {blog_email}")
        print(f"   Post '{title}' will appear on your blog shortly!")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def main():
    config = load_config()
    print("=" * 60)
    print("  SecHunter Blog — Email Poster")
    print("  NO CARD | NO API | NO OAUTH")
    print("=" * 60)
    print()
    
    # Blogger email posting setup
    print("BLOGGER EMAIL POSTING SETUP:")
    print()
    print("1. Go to https://www.blogger.com/blog/daemon018/settings")
    print("2. Click 'Email' in the left menu")
    print("3. Set up email posting:")
    print("   - Create a secret email like: daemon018.post@blogger.com")
    print("   - OR use your own email (daemon018@gmail.com)")
    print("4. Save the blog email address")
    print()
    print("5. For Gmail sending, you need an App Password:")
    print("   - Go to https://myaccount.google.com/apppasswords")
    print("   - Create app password for 'Mail'")
    print("   - Use that password (not your regular password)")
    print()
    
    # Find latest post
    posts_dir = os.path.join(BLOG_DIR, "content", "posts")
    post_files = sorted([f for f in os.listdir(posts_dir) if f.endswith(".md")], reverse=True)
    
    if post_files:
        latest_post = os.path.join(posts_dir, post_files[0])
        with open(latest_post, "r") as f:
            content = f.read()
        
        title = ""
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].split("\n"):
                    if line.startswith("title:"):
                        title = line.split("title:")[1].strip().strip('"')
                body = parts[2].strip()
        
        if not title:
            title = f"Cybersecurity Guide — {date.today().strftime('%B %d, %Y')}"
        
        print(f"Latest post: {title}")
        print(f"Content: {len(body)} chars")
        print()
        print("To post this to Blogger, run:")
        print(f"  python3 scripts/blogger-email.py --send")
        print()
        print("You'll need to provide:")
        print("  - Your Gmail address")
        print("  - Your Gmail App Password")
        print("  - Your Blogger post email")

if __name__ == "__main__":
    main()
