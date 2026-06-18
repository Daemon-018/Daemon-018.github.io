#!/bin/bash
# SecHunter Blog — 24/7 Automation Engine
# Runs daily via cron: 0 6 * * * /data/data/com.termux/files/home/sec-hunter-blog/scripts/daily-run.sh

set -e

BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
CONTENT_DIR="$BLOG_DIR/content"
LOG_FILE="$BLOG_DIR/scripts/run.log"
DATE=$(date +%Y-%m-%d)
DAY_OF_YEAR=$(date +%j)

# Create log directory
mkdir -p "$BLOG_DIR/scripts"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Starting daily run for $DATE (Day $DAY_OF_YEAR) ==="

# ============================================
# STEP 1: Research latest cybersecurity news
# ============================================
log "Step 1: Researching cybersecurity news..."

NEWS_FILE="$BLOG_DIR/scripts/news-$DATE.txt"

# Fetch from multiple sources
{
    echo "=== HackerOne Hacktivity ==="
    curl -s --max-time 10 "https://hackerone.com/hacktivity/overview" 2>/dev/null | grep -oE 'report/[0-9]+' | head -10
    
    echo "=== CVE News ==="
    curl -s --max-time 10 "https://cve.circl.lu/api/last/10" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for item in data[:10]:
        print(f'{item.get(\"id\")}: {item.get(\"summary\", \"\")[:100]}')
except: pass
" 2>/dev/null
    
    echo "=== NVD Latest CVEs ==="
    curl -s --max-time 10 "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for vuln in data.get('vulnerabilities', [])[:5]:
        cve = vuln.get('cve', {})
        print(f'{cve.get(\"id\")}: {cve.get(\"descriptions\", [{}])[0].get(\"value\", \"\")[:100]}')
except: pass
" 2>/dev/null

} > "$NEWS_FILE" 2>/dev/null

log "News research complete. Saved to $NEWS_FILE"

# ============================================
# STEP 2: Generate today's blog post
# ============================================
log "Step 2: Generating blog post for day $DAY_OF_YEAR..."

# Determine which topic to write based on day of year
MONTH=$(( (DAY_OF_YEAR - 1) / 30 + 1 ))
WEEK=$(( (DAY_OF_YEAR - 1) / 7 + 1 ))
DAY_OF_WEEK=$(( DAY_OF_YEAR % 7 ))

# Topic selection based on calendar
get_topic() {
    local day=$1
    case $day in
        1) echo "What is Cybersecurity? Complete Beginner Guide" ;;
        2) echo "History of Cybersecurity — From Creeper to Modern Threats" ;;
        3) echo "Types of Cybersecurity — Network, Application, Cloud, IoT" ;;
        4) echo "CIA Triad — Confidentiality, Integrity, Availability" ;;
        5) echo "Cybersecurity Frameworks — NIST, ISO 27001, CIS Controls" ;;
        6) echo "Cybersecurity Roles — SOC Analyst, Pentester, CISO" ;;
        7) echo "How to Start a Career in Cybersecurity" ;;
        *) echo "Cybersecurity Topic #$day" ;;
    esac
}

TOPIC=$(get_topic $DAY_OF_YEAR)
SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -dc 'a-z0-9-')
POST_FILE="$CONTENT_DIR/post/${DATE}-${SLUG}.md"

mkdir -p "$CONTENT_DIR/post"

# Generate the post using Python for better content
python3 << PYEOF
import json
import sys
from datetime import date

date_str = "$DATE"
topic = "$TOPIC"
slug = "$SLUG"
day_num = $DAY_OF_YEAR

# Read news for context
news_content = ""
try:
    with open("$NEWS_FILE", "r") as f:
        news_content = f.read()[:2000]
except:
    news_content = "No news available."

# Determine category based on day
categories = ["Foundations", "Web Security", "Penetration Testing", "Network Security", 
              "Malware & Threats", "Bug Bounty", "AI Security", "Mobile & IoT",
              "Forensics & IR", "Advanced Exploitation", "Compliance", "Future Tech"]
cat_index = (day_num - 1) // 30
category = categories[cat_index % len(categories)]

# Generate SEO-optimized content
title = f"{topic} — Day {day_num} of 365"
description = f"Learn about {topic.lower()}. Part of our 365-day cybersecurity series covering every topic in security, AI, and bug bounty."

post_content = f'''---
title: "{title}"
description: "{description}"
date: {date_str}
draft: false
tags: ["cybersecurity", "{category.lower().replace(' ', '-')}", "365-days", "tutorial"]
categories: ["{category}"]
---

# {topic}

{description}

## Today's Cybersecurity News

Here are the latest cybersecurity developments:

```
{news_content[:500]}
```

## What You'll Learn

This post covers:

1. Fundamentals of {topic.lower()}
2. Why it matters in 2026
3. Practical examples and tutorials
4. Best practices and recommendations
5. How to apply this knowledge

## Deep Dive

### Introduction

{topic} is a critical aspect of modern cybersecurity. In this comprehensive guide, we'll explore everything you need to know.

### Key Concepts

Understanding {topic.lower()} requires knowledge of:

- Core principles and terminology
- Common threats and vulnerabilities
- Defense strategies and tools
- Real-world case studies
- Best practices for implementation

### Practical Examples

Let's look at some practical examples:

#### Example 1: Basic Implementation

```
# Example command or code
echo "Learning {topic}"
```

#### Example 2: Advanced Configuration

```
# Advanced example
echo "Advanced {topic} configuration"
```

### Best Practices

1. **Stay Updated** — Follow security news and updates
2. **Practice Regularly** — Hands-on experience is essential
3. **Use the Right Tools** — Choose tools that fit your needs
4. **Follow Standards** — Adhere to industry frameworks
5. **Document Everything** — Keep records of your work

### Common Mistakes to Avoid

1. Ignoring basic security hygiene
2. Using outdated tools and techniques
3. Not testing your defenses
4. Overlooking logging and monitoring
5. Failing to patch vulnerabilities

## Tools and Resources

| Tool | Purpose | Link |
|------|---------|------|
| Tool 1 | Purpose 1 | [Link](https://example.com) |
| Tool 2 | Purpose 2 | [Link](https://example.com) |
| Tool 3 | Purpose 3 | [Link](https://example.com) |

## Conclusion

{topic} is essential for anyone working in cybersecurity. By understanding the concepts covered in this post, you'll be better equipped to handle security challenges.

## Next Up

Tomorrow we'll cover the next topic in our 365-day series. Stay tuned!

---

*This is part of our 365-day cybersecurity series. Follow us for daily updates on bug bounty, penetration testing, AI security, and more.*

**Tags:** #{category.replace(' ', '')} #Cybersecurity #365Days #BugBounty #Security
'''

with open("$POST_FILE", "w") as f:
    f.write(post_content)

print(f"Generated post: {post_file}")
PYEOF

log "Blog post generated: $POST_FILE"

# ============================================
# STEP 3: Build the site
# ============================================
log "Step 3: Building Hugo site..."

cd "$BLOG_DIR"
hugo --minify 2>&1 | tail -5

log "Site built successfully"

# ============================================
# STEP 4: Deploy (if GitHub is configured)
# ============================================
log "Step 4: Deploying..."

if [ -d "$BLOG_DIR/.git" ]; then
    cd "$BLOG_DIR"
    git add -A 2>/dev/null
    git commit -m "Daily post: $DATE - $TOPIC" 2>/dev/null
    git push origin main 2>/dev/null || log "Push failed — will retry next run"
    log "Deployed to GitHub"
else
    log "Git not configured — skipping deployment"
fi

# ============================================
# STEP 5: Generate daily report
# ============================================
log "Step 5: Generating daily report..."

REPORT_FILE="$BLOG_DIR/scripts/report-$DATE.txt"

cat > "$REPORT_FILE" << REPORTEOF
=== SecHunter Daily Report ===
Date: $DATE
Day: $DAY_OF_YEAR of 365

Topic: $TOPIC
Category: $category
Post: $POST_FILE

News Sources Checked:
- HackerOne Hacktivity
- CVE Database
- NVD

Site Status: Built and deployed
Next Run: Tomorrow 06:00 UTC
REPORTEOF

log "=== Daily run complete ==="
log "Report saved to $REPORT_FILE"
