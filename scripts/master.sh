#!/bin/bash
# SecHunter Blog — Master Control Script
# Usage: ./master.sh [command]
# Commands: start | stop | status | post | news | seo | deploy | report

BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
SCRIPTS_DIR="$BLOG_DIR/scripts"

case "$1" in
    start)
        echo "=== Starting SecHunter Blog Automation ==="
        # Start cron daemon
        crond 2>/dev/null
        echo "Cron daemon started"
        echo "Cron jobs:"
        crontab -l 2>/dev/null
        echo ""
        echo "Automation is running. Posts will be generated daily at 6:00 AM."
        echo "News aggregation runs every 6 hours."
        ;;
    
    stop)
        echo "=== Stopping SecHunter Blog Automation ==="
        # Kill cron daemon
        pkill crond 2>/dev/null
        echo "Cron daemon stopped"
        echo "Note: Already scheduled jobs will not run until cron is restarted."
        ;;
    
    status)
        echo "=== SecHunter Blog Status ==="
        echo ""
        echo "--- Cron Jobs ---"
        crontab -l 2>/dev/null || echo "No cron jobs configured"
        echo ""
        echo "--- Cron Daemon ---"
        if pgrep crond > /dev/null 2>&1; then
            echo "Status: RUNNING"
        else
            echo "Status: STOPPED"
        fi
        echo ""
        echo "--- Content Stats ---"
        TOTAL=$(find "$BLOG_DIR/content" -name "*.md" -type f 2>/dev/null | wc -l)
        POSTS=$(find "$BLOG_DIR/content/post" -name "*.md" -type f 2>/dev/null | wc -l)
        echo "Total markdown files: $TOTAL"
        echo "Blog posts: $POSTS"
        echo ""
        echo "--- Recent Posts ---"
        find "$BLOG_DIR/content/post" -name "*.md" -type f -printf '%T@ %p\n' 2>/dev/null | \
            sort -rn | head -5 | while read line; do
            file=$(echo "$line" | cut -d' ' -f2-)
            title=$(grep -m1 '^title:' "$file" 2>/dev/null | sed 's/title: "//;s/"//')
            date=$(grep -m1 '^date:' "$file" 2>/dev/null | sed 's/date: //')
            echo "  $date - $title"
        done
        echo ""
        echo "--- Disk Usage ---"
        du -sh "$BLOG_DIR/" 2>/dev/null
        du -sh "$BLOG_DIR/content/" 2>/dev/null
        du -sh "$BLOG_DIR/public/" 2>/dev/null
        ;;
    
    post)
        echo "=== Generating today's blog post ==="
        bash "$SCRIPTS_DIR/daily-run.sh"
        ;;
    
    news)
        echo "=== Running news aggregation ==="
        bash "$SCRIPTS_DIR/news-aggregator.sh"
        echo ""
        LATEST_NEWS=$(ls -t "$SCRIPTS_DIR/news/digest-"* 2>/dev/null | head -1)
        if [ -n "$LATEST_NEWS" ]; then
            echo "=== Latest News Digest ==="
            cat "$LATEST_NEWS"
        fi
        ;;
    
    seo)
        echo "=== Running SEO report ==="
        bash "$SCRIPTS_DIR/seo-report.sh"
        LATEST_SEO=$(ls -t "$SCRIPTS_DIR/seo-report-"* 2>/dev/null | head -1)
        if [ -n "$LATEST_SEO" ]; then
            cat "$LATEST_SEO"
        fi
        ;;
    
    deploy)
        echo "=== Deploying blog ==="
        cd "$BLOG_DIR"
        hugo --minify 2>&1 | tail -5
        if [ -d "$BLOG_DIR/.git" ]; then
            git add -A 2>/dev/null
            git commit -m "Manual deploy: $(date '+%Y-%m-%d %H:%M')" 2>/dev/null
            git push origin main 2>/dev/null && echo "Deployed successfully" || echo "Push failed"
        else
            echo "Git not configured. Build complete in public/ folder."
        fi
        ;;
    
    report)
        echo "=== Generating monthly report ==="
        bash "$SCRIPTS_DIR/monthly-report.sh"
        ;;
    
    social)
        echo "=== Generating social media content ==="
        bash "$SCRIPTS_DIR/social-poster.sh"
        ;;
    
    *)
        echo "SecHunter Blog — Master Control"
        echo ""
        echo "Usage: ./master.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start   — Start automation (cron daemon)"
        echo "  stop    — Stop automation"
        echo "  status  — Show blog status and stats"
        echo "  post    — Generate today's blog post"
        echo "  news    — Run news aggregation"
        echo "  seo     — Run SEO report"
        echo "  deploy  — Build and deploy blog"
        echo "  report  — Generate monthly report"
        echo "  social  — Generate social media content"
        echo ""
        echo "Examples:"
        echo "  ./master.sh start"
        echo "  ./master.sh post"
        echo "  ./master.sh status"
        ;;
esac
