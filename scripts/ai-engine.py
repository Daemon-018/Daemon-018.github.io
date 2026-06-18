#!/usr/bin/env python3
"""
SecHunter AI Blog Engine — Production Version
Uses OpenRouter (owl-alpha) to generate SEO-optimized cybersecurity content
Runs 24/7 via cron jobs
"""

import json
import urllib.request
import urllib.error
import os
import sys
import subprocess
from datetime import datetime, date
import time

# ============================================
# CONFIGURATION
# ============================================
# Load config from file
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
try:
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    API_KEY = config.get("api_key", "")
    MODEL = config.get("model", "openrouter/owl-alpha")
    API_URL = config.get("base_url", "https://openrouter.ai/api/v1/chat/completions")
except Exception as e:
    print(f"ERROR: Could not load config: {e}")
    sys.exit(1)

if not API_KEY:
    print("ERROR: API key not found in config.json!")
    sys.exit(1)

BLOG_DIR = "/data/data/com.termux/files/home/sec-hunter-blog"
CONTENT_DIR = os.path.join(BLOG_DIR, "content")
POSTS_DIR = os.path.join(CONTENT_DIR, "posts")
LOG_DIR = os.path.join(BLOG_DIR, "scripts", "logs")
LOG_FILE = os.path.join(LOG_DIR, "ai-engine.log")

# Create directories
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================
# LOGGING
# ============================================
def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ============================================
# OPENROUTER API
# ============================================
def call_openrouter(prompt, max_tokens=4000, temperature=0.7):
    """Call OpenRouter API and return the generated content"""
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }).encode()
    
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://sechunter.github.io",
            "X-Title": "SecHunter Blog"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            return content, tokens
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else "No error body"
        log(f"HTTP Error {e.code}: {error_body[:500]}")
        return None, 0
    except Exception as e:
        log(f"API Error: {e}")
        return None, 0

# ============================================
# NEWS RESEARCH
# ============================================
def research_news():
    """Research latest cybersecurity news from multiple sources"""
    log("Researching latest cybersecurity news...")
    news = {}
    
    # Source 1: CVE Latest
    try:
        req = urllib.request.Request("https://cve.circl.lu/api/last/5")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            news["cves"] = [f"{item.get('id')}: {item.get('summary', '')[:150]}" for item in data[:5]]
    except:
        news["cves"] = []
    
    # Source 2: The Hacker News RSS
    try:
        req = urllib.request.Request("https://feeds.feedburner.com/TheHackersNews")
        with urllib.request.urlopen(req, timeout=15) as resp:
            rss = resp.read().decode()
            titles = []
            for line in rss.split("\n"):
                if "<title>" in line and "</title>" in line:
                    title = line.split("<title>")[1].split("</title>")[0]
                    if title and title != "The Hacker News":
                        titles.append(title)
            news["thn"] = titles[:5]
    except:
        news["thn"] = []
    
    # Source 3: BleepingComputer RSS
    try:
        req = urllib.request.Request("https://www.bleepingcomputer.com/feed/")
        with urllib.request.urlopen(req, timeout=15) as resp:
            rss = resp.read().decode()
            titles = []
            for line in rss.split("\n"):
                if "<title>" in line and "</title>" in line:
                    title = line.split("<title>")[1].split("</title>")[0]
                    if title:
                        titles.append(title)
            news["bleep"] = titles[:5]
    except:
        news["bleep"] = []
    
    # Format news for AI context
    context = "Latest Cybersecurity News:\n"
    if news.get("cves"):
        context += "\nLatest CVEs:\n" + "\n".join(news["cves"])
    if news.get("thn"):
        context += "\n\nThe Hacker News:\n" + "\n".join(news["thn"])
    if news.get("bleep"):
        context += "\n\nBleepingComputer:\n" + "\n".join(news["bleep"])
    
    log(f"News research complete: {len(news.get('cves', []))} CVEs, {len(news.get('thn', []))} THN, {len(news.get('bleep', []))} BleepingComputer")
    return context

# ============================================
# CONTENT GENERATION
# ============================================
def generate_post(topic, category, news_context):
    """Generate a complete blog post using OpenRouter"""
    log(f"Generating post: {topic} ({category})")
    
    prompt = f"""You are an expert cybersecurity researcher, bug bounty hunter, and professional content writer. You write for SecHunter, a leading cybersecurity blog.

Write a comprehensive, SEO-optimized blog post about: {topic}

Category: {category}

Latest cybersecurity context to reference:
{news_context}

WRITING REQUIREMENTS:
1. Write 2500-3500 words (this is critical for SEO)
2. Use proper markdown formatting with H2 (##) and H3 (###) headings
3. Start with an engaging hook/statistic
4. Include a table of contents after the introduction
5. Cover the topic comprehensively with real-world examples
6. Include code examples, commands, or configurations where relevant
7. Add comparison tables where appropriate
8. Include a "Key Takeaways" section at the end
9. Add a "Further Reading" section with 5 internal link suggestions
10. Write in a professional but accessible tone
11. Use short paragraphs (2-3 sentences max)
12. Include bullet points and numbered lists
13. Add call-to-action at the end
14. Reference the latest news context where relevant

SEO REQUIREMENTS:
- Include the target keyword "{topic}" in the first paragraph
- Use the keyword naturally throughout (5-8 times)
- Include related keywords naturally
- Write a compelling meta description (already provided)
- Use heading hierarchy properly (H2 for main sections, H3 for subsections)

IMPORTANT: Output ONLY the markdown content. Do NOT include the frontmatter (title, date, etc). Start directly with the introduction paragraph."""

    content, tokens = call_openrouter(prompt, max_tokens=6000, temperature=0.7)
    
    if content:
        log(f"Post generated: {tokens} words approximately")
        return content
    else:
        log("ERROR: Failed to generate content")
        return None

# ============================================
# TOPIC CALENDAR
# ============================================
def get_todays_topic():
    """Get today's topic based on the 365-day calendar"""
    day_of_year = int(date.today().strftime("%j"))
    
    # Full 365-day calendar organized by month
    calendar = {
        # JANUARY - Foundations
        1: ("What is Cybersecurity? Complete Beginner Guide 2026", "Foundations"),
        2: ("History of Cybersecurity — From Creeper to Modern Threats", "Foundations"),
        3: ("Types of Cybersecurity — Network, Application, Cloud, IoT", "Foundations"),
        4: ("CIA Triad Explained — Confidentiality, Integrity, Availability", "Foundations"),
        5: ("Top Cybersecurity Frameworks — NIST, ISO 27001, CIS Controls", "Compliance"),
        6: ("Cybersecurity Career Guide — Roles, Salaries, and How to Start", "Career"),
        7: ("How to Start a Career in Cybersecurity — Complete Roadmap", "Career"),
        8: ("OSI Model Explained — All 7 Layers with Examples", "Network Security"),
        9: ("TCP/IP Protocol Suite — Complete Technical Guide", "Network Security"),
        10: ("IP Addressing and Subnetting — Practical Guide", "Network Security"),
        11: ("DNS Security — How DNS Works and Common Attacks", "Network Security"),
        12: ("HTTP vs HTTPS — Web Protocols and Security Headers", "Web Security"),
        13: ("Firewalls, IDS/IPS — Network Security Essentials", "Network Security"),
        14: ("VPN Security — How Virtual Private Networks Work", "Network Security"),
        15: ("Linux Security Fundamentals — Hardening and Auditing", "Penetration Testing"),
        16: ("Windows Security Architecture — Active Directory and GPO", "Penetration Testing"),
        17: ("File Permissions and Access Control — Linux and Windows", "Penetration Testing"),
        18: ("Privilege Escalation Techniques — Linux and Windows", "Penetration Testing"),
        19: ("Log Analysis and Security Monitoring — SIEM, Splunk, ELK", "Forensics"),
        20: ("Cryptography Basics — Encryption, Hashing, Digital Signatures", "Foundations"),
        21: ("AES vs DES vs RSA — Symmetric and Asymmetric Encryption", "Foundations"),
        22: ("TLS/SSL Deep Dive — How HTTPS Actually Works", "Web Security"),
        23: ("PKI and Digital Certificates — Complete Guide", "Foundations"),
        24: ("How the Web Works — Complete Architecture for Security Pros", "Web Security"),
        25: ("HTML, CSS, JavaScript Security — Common Vulnerabilities", "Web Security"),
        26: ("Cookies, Sessions, Tokens — Web Authentication Security", "Web Security"),
        27: ("CORS, CSP, HSTS — Security Headers Explained", "Web Security"),
        28: ("OWASP Top 10 2026 — Complete Guide with Examples", "Web Security"),
        29: ("Broken Access Control — The #1 Web Vulnerability", "Web Security"),
        30: ("Cryptographic Failures — How to Find and Exploit Them", "Web Security"),
        31: ("SQL Injection Masterclass — From Basic to Advanced", "Web Security"),
    }
    
    if day_of_year in calendar:
        return calendar[day_of_year]
    else:
        # For days beyond 31, generate based on category rotation
        categories = [
            ("Web Security", "Web Security"),
            ("Penetration Testing", "Penetration Testing"),
            ("Network Security", "Network Security"),
            ("Cloud Security", "Cloud Security"),
            ("AI Security", "AI Security"),
            ("Malware Analysis", "Malware Analysis"),
            ("Bug Bounty", "Bug Bounty"),
            ("Forensics", "Forensics"),
            ("Mobile Security", "Mobile Security"),
            ("Compliance", "Compliance"),
            ("Career", "Career"),
            ("Tools", "Tools"),
        ]
        cat_index = (day_of_year - 1) % 12
        cat_name, cat_slug = categories[cat_index]
        return (f"Advanced {cat_name} — Deep Dive Day {day_of_year}", cat_slug)

# ============================================
# FILE WRITING
# ============================================
def write_post(topic, category, content):
    """Write the blog post to a markdown file"""
    today = date.today().strftime("%Y-%m-%d")
    slug = topic.lower().replace(" ", "-").replace("—", "-").replace("'", "").replace(",", "")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:60]
    filename = f"{today}-{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)
    
    frontmatter = f"""---
title: "{topic}"
description: "Comprehensive guide to {topic.lower()}. Learn with real-world examples, best practices, and expert insights from SecHunter."
date: {today}T06:00:00+05:30
draft: false
tags: ["cybersecurity", "{category.lower().replace(' ', '-')}", "tutorial", "guide"]
categories: ["{category}"]
author: "SecHunter"
---

"""
    
    with open(filepath, "w") as f:
        f.write(frontmatter + content)
    
    log(f"Post written to: {filepath}")
    return filepath

# ============================================
# BUILD AND DEPLOY
# ============================================
def build_and_deploy():
    """Build Hugo site and deploy"""
    log("Building Hugo site...")
    try:
        result = subprocess.run(
            ["hugo", "--minify"],
            cwd=BLOG_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            log("Hugo build successful")
        else:
            log(f"Hugo build error: {result.stderr[:500]}")
    except Exception as e:
        log(f"Build error: {e}")
    
    # Deploy via git
    log("Deploying to GitHub...")
    try:
        subprocess.run(["git", "add", "-A"], cwd=BLOG_DIR, timeout=30)
        subprocess.run(["git", "commit", "-m", f"AI Post: {date.today().strftime('%Y-%m-%d')}"], cwd=BLOG_DIR, timeout=30)
        result = subprocess.run(["git", "push", "origin", "main"], cwd=BLOG_DIR, timeout=60, capture_output=True, text=True)
        if result.returncode == 0:
            log("Deployed successfully!")
        else:
            log(f"Push failed: {result.stderr[:200]}")
    except Exception as e:
        log(f"Deploy error: {e}")

# ============================================
# MAIN
# ============================================
def main():
    log("=" * 60)
    log("SecHunter AI Blog Engine — Starting")
    log(f"Date: {date.today().strftime('%Y-%m-%d')} | Model: {MODEL}")
    log("=" * 60)
    
    # Step 1: Research news
    news_context = research_news()
    
    # Step 2: Get today's topic
    topic, category = get_todays_topic()
    log(f"Today's topic: {topic} ({category})")
    
    # Step 3: Generate content
    content = generate_post(topic, category, news_context)
    
    if content:
        # Step 4: Write post
        filepath = write_post(topic, category, content)
        
        # Step 5: Build and deploy
        build_and_deploy()
        
        log("=" * 60)
        log("Daily run COMPLETE!")
        log(f"Post: {filepath}")
        log("=" * 60)
    else:
        log("ERROR: Failed to generate post. Will retry next run.")

if __name__ == "__main__":
    main()
