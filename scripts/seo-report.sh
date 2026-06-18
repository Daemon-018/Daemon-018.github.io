#!/bin/bash
# SecHunter Weekly SEO Report
# Runs every Sunday at 8:00 AM

BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
REPORT_FILE="$BLOG_DIR/scripts/seo-report-$(date +%Y-%m-%d).txt"

{
    echo "=== SecHunter Weekly SEO Report ==="
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    
    echo "=== Content Stats ==="
    TOTAL_POSTS=$(find "$BLOG_DIR/content" -name "*.md" -type f 2>/dev/null | wc -l)
    echo "Total posts: $TOTAL_POSTS"
    
    THIS_WEEK=$(find "$BLOG_DIR/content" -name "*.md" -mtime -7 -type f 2>/dev/null | wc -l)
    echo "Posts this week: $THIS_WEEK"
    
    echo ""
    echo "=== Categories ==="
    for dir in "$BLOG_DIR/content"/*/; do
        if [ -d "$dir" ]; then
            count=$(find "$dir" -name "*.md" -type f 2>/dev/null | wc -l)
            echo "  $(basename "$dir"): $count posts"
        fi
    done
    
    echo ""
    echo "=== Recent Posts ==="
    find "$BLOG_DIR/content" -name "*.md" -type f -printf '%T@ %p\n' 2>/dev/null | \
        sort -rn | head -10 | while read line; do
        file=$(echo "$line" | cut -d' ' -f2-)
        title=$(grep -m1 '^title:' "$file" 2>/dev/null | sed 's/title: "//;s/"//')
        date=$(grep -m1 '^date:' "$file" 2>/dev/null | sed 's/date: //')
        echo "  $date - $title"
    done
    
    echo ""
    echo "=== SEO Checklist ==="
    echo "  [ ] All posts have meta descriptions"
    echo "  [ ] All posts have tags"
    echo "  [ ] All posts have categories"
    echo "  [ ] Internal links between related posts"
    echo "  [ ] External links to authoritative sources"
    echo "  [ ] Image alt tags (if applicable)"
    echo "  [ ] XML sitemap generated"
    echo "  [ ] robots.txt configured"
    echo "  [ ] Google Search Console configured"
    echo "  [ ] Analytics configured"
    
    echo ""
    echo "=== Recommended Actions ==="
    echo "  1. Review and update old posts"
    echo "  2. Add internal links to new posts"
    echo "  3. Share new posts on social media"
    echo "  4. Check for broken links"
    echo "  5. Update meta descriptions if needed"
    
} > "$REPORT_FILE"

echo "SEO report saved to $REPORT_FILE"
