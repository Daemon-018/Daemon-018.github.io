#!/bin/bash
# SecHunter AI Blog Engine — Powered by OpenRouter (owl-alpha)
# This is the MASTER script that runs everything 24/7

# ============================================
# CONFIGURATION — FILL THESE IN
# ============================================
OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-YOUR_API_KEY_HERE}"
OPENROUTER_MODEL="openrouter/owl-alpha"
BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
CONTENT_DIR="$BLOG_DIR/content"
POSTS_DIR="$CONTENT_DIR/posts"
LOG_DIR="$BLOG_DIR/logs"
DATE=$(date +%Y-%m-%d)
DATETIME=$(date '+%Y-%m-%d %H:%M:%S')
DAY_OF_YEAR=$(date +%j)

# Create directories
mkdir -p "$POSTS_DIR" "$LOG_DIR" "$CONTENT_DIR/news" "$CONTENT_DIR/bug-bounty" "$CONTENT_DIR/tutorials" "$CONTENT_DIR/tools" "$CONTENT_DIR/writeups" "$CONTENT_DIR/ai-security" "$CONTENT_DIR/penetration-testing" "$CONTENT_DIR/web-security" "$CONTENT_DIR/network-security" "$CONTENT_DIR/malware" "$CONTENT_DIR/forensics" "$CONTENT_DIR/mobile-security" "$CONTENT_DIR/cloud-security" "$CONTENT_DIR/compliance" "$CONTENT_DIR/career" "$CONTENT_DIR/news-roundup"

# ============================================
# LOGGING
# ============================================
LOG_FILE="$LOG_DIR/engine-$DATE.log"
log() {
    echo "[$DATETIME] $1" | tee -a "$LOG_FILE"
}

# ============================================
# STEP 1: RESEARCH LATEST NEWS
# ============================================
research_news() {
    log "=== RESEARCHING LATEST CYBERSECURITY NEWS ==="
    
    local news_file="$CONTENT_DIR/news/raw-$DATE.txt"
    local news_summary="$CONTENT_DIR/news/summary-$DATE.txt"
    
    {
        echo "=== CVE Latest ==="
        curl -s --max-time 15 "https://cve.circl.lu/api/last/10" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for item in data[:10]:
        cve_id = item.get('id', 'N/A')
        summary = item.get('summary', 'N/A')[:200]
        cvss = item.get('cvss', 'N/A')
        print(f'{cve_id} (CVSS: {cvss}): {summary}')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null
        
        echo ""
        echo "=== NVD Latest ==="
        curl -s --max-time 15 "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5" 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for vuln in data.get('vulnerabilities', [])[:5]:
        cve = vuln.get('cve', {})
        cve_id = cve.get('id', 'N/A')
        desc = cve.get('descriptions', [{}])[0].get('value', 'N/A')[:200]
        print(f'{cve_id}: {desc}')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null
        
        echo ""
        echo "=== HackerOne Hacktivity ==="
        curl -s --max-time 15 "https://hackerone.com/hacktivity/overview" 2>/dev/null | grep -oE '[A-Z][a-z]+ [A-Z][a-z]+ [0-9]+ — [A-Za-z0-9 ]+' | head -10
        
        echo ""
        echo "=== The Hacker News RSS ==="
        curl -s --max-time 15 "https://feeds.feedburner.com/TheHackersNews" 2>/dev/null | grep -oE '<title>[^<]+</title>' | sed 's/<[^>]*>//g' | head -10
        
        echo ""
        echo "=== BleepingComputer RSS ==="
        curl -s --max-time 15 "https://www.bleepingcomputer.com/feed/" 2>/dev/null | grep -oE '<title>[^<]+</title>' | sed 's/<[^>]*>//g' | head -10
        
    } > "$news_file" 2>/dev/null
    
    # Create a clean summary for the AI
    head -50 "$news_file" > "$news_summary" 2>/dev/null
    
    log "News research complete: $news_file"
    echo "$news_summary"
}

# ============================================
# STEP 2: GENERATE CONTENT VIA OPENROUTER
# ============================================
generate_post() {
    local topic="$1"
    local category="$2"
    local news_context="$3"
    local output_file="$4"
    
    log "Generating post: $topic"
    
    # Build the prompt for OpenRouter
    local prompt="You are an expert cybersecurity researcher and bug bounty hunter writing for a professional blog called 'SecHunter'. 

Write a comprehensive, SEO-optimized blog post about: ${topic}

Category: ${category}

Latest cybersecurity news context:
${news_context}

Requirements:
1. Write 2000-3000 words
2. Use proper markdown formatting with H2, H3 headings
3. Include an engaging introduction
4. Cover the topic comprehensively with real-world examples
5. Include code examples or commands where relevant
6. Add a 'Key Takeaways' section
7. Add a 'Further Reading' section with 3-5 links
8. Use SEO-friendly headings (include target keywords naturally)
9. Write in a professional but accessible tone
10. Include practical tips and best practices
11. Add internal link suggestions to related SecHunter posts
12. End with a call-to-action

The post should be original, valuable, and rank well on Google. Do NOT just list facts — provide deep insights and practical knowledge.

Output ONLY the markdown content, no explanations."
    
    # Call OpenRouter API
    local response=$(curl -s --max-time 120 "https://openrouter.ai/api/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENROUTER_API_KEY" \
        -H "HTTP-Referer: https://sechunter.github.io" \
        -H "X-Title: SecHunter Blog" \
        -d "{
            \"model\": \"$OPENROUTER_MODEL\",
            \"messages\": [{\"role\": \"user\", \"content\": $(echo "$prompt" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")}],
            \"max_tokens\": 4000,
            \"temperature\": 0.7
        }" 2>/dev/null)
    
    # Extract the content from the response
    local content=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data['choices'][0]['message']['content'])
except Exception as e:
    print(f'ERROR: {e}')
" 2>/dev/null)
    
    if [ -z "$content" ] || [ "$content" = "ERROR: " ]; then
        log "ERROR: Failed to generate content for: $topic"
        log "Response: ${response:0:500}"
        return 1
    fi
    
    # Write the post with frontmatter
    cat > "$output_file" << POSTEOF
---
title: "$topic"
description: "Comprehensive guide to $topic. Learn about ${topic.toLowerCase()} with real-world examples, best practices, and expert insights."
date: $(date +%Y-%m-%dT%H:%M:%S%z)
draft: false
tags: ["cybersecurity", "$(echo $category | tr '[:upper:]' '[:lower:]' | tr ' ' '-')", "tutorial", "guide"]
categories: ["$category"]
author: "SecHunter"
---

$content

---

*This article was written by SecHunter. For more cybersecurity guides, visit [SecHunter Blog](https://sechunter.github.io).*

**Tags:** #CyberSecurity #$(echo $category | tr ' ' '') #InfoSec #SecurityResearch
POSTEOF
    
    log "Post generated: $output_file ($(wc -w < "$output_file") words)"
    return 0
}

# ============================================
# STEP 3: DETERMINE TODAY'S TOPIC
# ============================================
get_todays_topic() {
    local day=$1
    
    # 365-day content calendar
    case $day in
        1) echo "What is Cybersecurity? Complete Beginner Guide 2026|Foundations" ;;
        2) echo "History of Cybersecurity — From Creeper to Modern Threats|Foundations" ;;
        3) echo "Types of Cybersecurity — Network, Application, Cloud, IoT, and More|Foundations" ;;
        4) echo "CIA Triad Explained — Confidentiality, Integrity, Availability|Foundations" ;;
        5) echo "Top Cybersecurity Frameworks — NIST, ISO 27001, CIS Controls Compared|Compliance" ;;
        6) echo "Cybersecurity Career Guide — Roles, Salaries, and How to Start in 2026|Career" ;;
        7) echo "How to Start a Career in Cybersecurity — Complete Roadmap|Career" ;;
        8) echo "OSI Model Explained — All 7 Layers with Examples|Network Security" ;;
        9) echo "TCP/IP Protocol Suite — Complete Technical Guide|Network Security" ;;
        10) echo "IP Addressing and Subnetting — Practical Guide for Security Professionals|Network Security" ;;
        11) echo "DNS Security — How DNS Works and Common Attacks|Network Security" ;;
        12) echo "HTTP vs HTTPS — Web Protocols and Security Headers Explained|Web Security" ;;
        13) echo "Firewalls, IDS/IPS — Network Security Essentials|Network Security" ;;
        14) echo "VPN Security — How Virtual Private Networks Work and Their Limitations|Network Security" ;;
        15) echo "Linux Security Fundamentals — Hardening, Permissions, and Auditing|Penetration Testing" ;;
        16) echo "Windows Security Architecture — Active Directory, GPO, and Hardening|Penetration Testing" ;;
        17) echo "File Permissions and Access Control — Linux and Windows|Penetration Testing" ;;
        18) echo "Privilege Escalation Techniques — Linux and Windows|Penetration Testing" ;;
        19) echo "Log Analysis and Security Monitoring — SIEM, Splunk, ELK|Forensics" ;;
        20) echo "Cryptography Basics — Encryption, Hashing, and Digital Signatures|Foundations" ;;
        21) echo "AES vs DES vs RSA — Symmetric and Asymmetric Encryption Explained|Foundations" ;;
        22) echo "TLS/SSL Deep Dive — How HTTPS Actually Works|Web Security" ;;
        23) echo "PKI and Digital Certificates — Complete Guide|Foundations" ;;
        24) echo "How the Web Works — Complete Architecture for Security Professionals|Web Security" ;;
        25) echo "HTML, CSS, JavaScript Security — Common Vulnerabilities|Web Security" ;;
        26) echo "Cookies, Sessions, Tokens — Web Authentication Security|Web Security" ;;
        27) echo "CORS, CSP, HSTS — Security Headers Explained|Web Security" ;;
        28) echo "OWASP Top 10 2026 — Complete Guide with Examples|Web Security" ;;
        29) echo "Broken Access Control — The #1 Web Vulnerability|Web Security" ;;
        30) echo "Cryptographic Failures — How to Find and Exploit Them|Web Security" ;;
        31) echo "SQL Injection Masterclass — From Basic to Advanced|Web Security" ;;
        *) 
            # For days beyond 31, generate based on category rotation
            local categories=("Web Security" "Penetration Testing" "Network Security" "Cloud Security" "AI Security" "Malware Analysis" "Bug Bounty" "Forensics" "Mobile Security" "Compliance" "Career" "Tools")
            local cat_index=$(( (day - 1) % 12 ))
            local category="${categories[$cat_index]}"
            echo "Advanced $category — Deep Dive Day $day|$category"
            ;;
    esac
}

# ============================================
# STEP 4: BUILD AND DEPLOY
# ============================================
build_and_deploy() {
    log "=== BUILDING HUGO SITE ==="
    
    cd "$BLOG_DIR"
    hugo --minify 2>&1 | tail -3
    
    local total_pages=$(find public -name "*.html" 2>/dev/null | wc -l)
    log "Site built: $total_pages pages"
    
    # Deploy if git is configured
    if [ -d "$BLOG_DIR/.git" ] && git remote -v 2>/dev/null | grep -q "github"; then
        log "=== DEPLOYING ==="
        git add -A 2>/dev/null
        git commit -m "AI Post: $DATE - $(date +%H:%M)" 2>/dev/null
        git push origin main 2>/dev/null && log "Deployed successfully" || log "Push failed"
    else
        log "Git not configured — build only"
    fi
}

# ============================================
# MAIN EXECUTION
# ============================================
main() {
    log "=========================================="
    log "  SecHunter AI Blog Engine — Starting"
    log "  Date: $DATE | Day: $DAY_OF_YEAR"
    log "  Model: $OPENROUTER_MODEL"
    log "=========================================="
    
    # Check API key
    if [ "$OPENROUTER_API_KEY" = "YOUR_API_KEY_HERE" ]; then
        log "ERROR: OpenRouter API key not set!"
        log "Set it with: export OPENROUTER_API_KEY=your_key_here"
        log "Or edit this script and add your key."
        exit 1
    fi
    
    # Step 1: Research news
    local news_summary=$(research_news)
    
    # Step 2: Get today's topic
    local topic_info=$(get_todays_topic $DAY_OF_YEAR)
    local topic=$(echo "$topic_info" | cut -d'|' -f1)
    local category=$(echo "$topic_info" | cut -d'|' -f2)
    
    log "Today's topic: $topic ($category)"
    
    # Step 3: Generate the post
    local slug=$(echo "$topic" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -dc 'a-z0-9-' | cut -c1-60)
    local output_file="$POSTS_DIR/${DATE}-${slug}.md"
    
    if generate_post "$topic" "$category" "$news_summary" "$output_file"; then
        log "Post generated successfully!"
    else
        log "Failed to generate post. Creating fallback."
        # Create a basic post as fallback
        cat > "$output_file" << FALLBACK
---
title: "$topic"
description: "Comprehensive guide to $topic"
date: $(date +%Y-%m-%dT%H:%M:%S%z)
draft: false
tags: ["cybersecurity", "$(echo $category | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"]
categories: ["$category"]
---

# $topic

This article is being updated. Check back soon for the full content.

## Key Points

- Comprehensive coverage of $topic
- Real-world examples and case studies
- Best practices and recommendations

---

*This article was written by SecHunter.*
FALLBACK
    fi
    
    # Step 4: Build and deploy
    build_and_deploy
    
    # Step 5: Generate social media content
    bash "$BLOG_DIR/scripts/social-poster.sh" 2>/dev/null || true
    
    log "=========================================="
    log "  Daily run complete!"
    log "  Next run: Tomorrow 06:00 AM"
    log "=========================================="
}

# Run main
main "$@"
