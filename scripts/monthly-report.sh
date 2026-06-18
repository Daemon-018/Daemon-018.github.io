#!/bin/bash
# SecHunter Monthly Report
# Runs on 1st of each month at 9:00 AM

BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
REPORT_FILE="$BLOG_DIR/scripts/monthly-report-$(date +%Y-%m).txt"
LAST_MONTH=$(date -d "last month" +%Y-%m 2>/dev/null || date +%Y-%m)

{
    echo "======================================"
    echo "  SecHunter Monthly Report — $LAST_MONTH"
    echo "======================================"
    echo ""
    
    echo "=== Content Production ==="
    TOTAL_POSTS=$(find "$BLOG_DIR/content" -name "*.md" -type f 2>/dev/null | wc -l)
    echo "Total posts on blog: $TOTAL_POSTS"
    
    MONTH_POSTS=$(find "$BLOG_DIR/content" -name "*.md" -newermt "$LAST_MONTH-01" ! -newermt "$(date +%Y-%m)-01" -type f 2>/dev/null | wc -l)
    echo "Posts published in $LAST_MONTH: $MONTH_POSTS"
    
    echo ""
    echo "=== Category Breakdown ==="
    for dir in "$BLOG_DIR/content"/*/; do
        if [ -d "$dir" ]; then
            count=$(find "$dir" -name "*.md" -type f 2>/dev/null | wc -l)
            name=$(basename "$dir")
            printf "  %-25s %3d posts\n" "$name:" "$count"
        fi
    done
    
    echo ""
    echo "=== Tag Cloud ==="
    grep -rh "^tags:" "$BLOG_DIR/content/" 2>/dev/null | \
        sed 's/tags: \[//;s/\]//;s/"//g' | \
        tr ',' '\n' | sed 's/^ *//;s/ *$//' | \
        sort | uniq -c | sort -rn | head -20 | while read line; do
        echo "  $line"
    done
    
    echo ""
    echo "=== Top 10 Longest Posts (Most Comprehensive) ==="
    find "$BLOG_DIR/content" -name "*.md" -type f -exec wc -w {} \; 2>/dev/null | \
        sort -rn | head -10 | while read line; do
        words=$(echo "$line" | awk '{print $1}')
        file=$(echo "$line" | awk '{print $2}')
        title=$(grep -m1 '^title:' "$file" 2>/dev/null | sed 's/title: "//;s/"//' | cut -c1-60)
        echo "  ${words}w — $title"
    done
    
    echo ""
    echo "=== SEO Health Check ==="
    echo ""
    
    # Check for missing descriptions
    NO_DESC=$(grep -rl "^description: \"\"" "$BLOG_DIR/content/" 2>/dev/null | wc -l)
    echo "  Posts missing description: $NO_DESC"
    
    # Check for missing tags
    NO_TAGS=$(grep -rl "^tags: \[\]" "$BLOG_DIR/content/" 2>/dev/null | wc -l)
    echo "  Posts missing tags: $NO_TAGS"
    
    # Check for drafts
    DRAFTS=$(grep -rl "^draft: true" "$BLOG_DIR/content/" 2>/dev/null | wc -l)
    echo "  Draft posts: $DRAFTS"
    
    # Check total word count
    TOTAL_WORDS=$(find "$BLOG_DIR/content" -name "*.md" -exec cat {} + 2>/dev/null | wc -w)
    echo "  Total word count: $TOTAL_WORDS"
    AVG_WORDS=$((TOTAL_WORDS / (TOTAL_POSTS > 0 ? TOTAL_POSTS : 1)))
    echo "  Average words per post: $AVG_WORDS"
    
    echo ""
    echo "=== Monetization Readiness ==="
    echo ""
    
    # Check for affiliate links
    AFFILIATE=$(grep -rl "affiliate\|referral\|partner" "$BLOG_DIR/content/" 2>/dev/null | wc -l)
    echo "  Posts with affiliate content: $AFFILIATE"
    
    # Check for CTAs
    CTA=$(grep -rl "sign up\|subscribe\|join\|download\|get started\|learn more" "$BLOG_DIR/content/" 2>/dev/null | wc -l)
    echo "  Posts with CTAs: $CTA"
    
    echo ""
    echo "=== Recommendations for Next Month ==="
    echo ""
    echo "  CONTENT:"
    echo "  1. Publish at least 30 posts (1 per day)"
    echo "  2. Target 2000+ words per post for SEO"
    echo "  3. Add internal links between related posts"
    echo "  4. Include code examples in technical posts"
    echo ""
    echo "  SEO:"
    echo "  1. Add meta descriptions to all posts"
    echo "  2. Add tags to all posts"
    echo "  3. Create pillar content pages"
    echo "  4. Build internal link structure"
    echo "  5. Submit sitemap to Google Search Console"
    echo ""
    echo "  MONETIZATION:"
    echo "  1. Add affiliate links to tool review posts"
    echo "  2. Create email capture CTA"
    echo "  3. Write 'best of' list posts for affiliate revenue"
    echo "  4. Create downloadable resources (cheatsheets)"
    echo ""
    echo "  PROMOTION:"
    echo "  1. Share each post on Twitter/X"
    echo "  2. Share on Reddit (r/netsec, r/cybersecurity, r/bugbounty)"
    echo "  3. Share on Hacker News"
    echo "  4. Share on LinkedIn"
    echo "  5. Email newsletter (if set up)"
    
    echo ""
    echo "=== File Sizes ==="
    echo ""
    du -sh "$BLOG_DIR/content/" 2>/dev/null
    du -sh "$BLOG_DIR/public/" 2>/dev/null
    du -sh "$BLOG_DIR/" 2>/dev/null
    
} > "$REPORT_FILE"

echo "Monthly report saved to $REPORT_FILE"
cat "$REPORT_FILE"
