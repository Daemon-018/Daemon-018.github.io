#!/bin/bash
# SecHunter Social Media Auto-Poster
# Shares new posts to Twitter/X, Reddit, LinkedIn
# Runs after each blog post is published

BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
LOG_FILE="$BLOG_DIR/scripts/social.log"
DATE=$(date +%Y-%m-%d)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Get the latest post
LATEST_POST=$(find "$BLOG_DIR/content/post" -name "*.md" -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)

if [ -z "$LATEST_POST" ]; then
    log "No new posts found"
    exit 0
fi

# Extract post details
TITLE=$(grep -m1 '^title:' "$LATEST_POST" 2>/dev/null | sed 's/title: "//;s/"//')
DESC=$(grep -m1 '^description:' "$LATEST_POST" 2>/dev/null | sed 's/description: "//;s/"//')
TAGS=$(grep -m1 '^tags:' "$LATEST_POST" 2>/dev/null | sed 's/tags: \[//;s/\]//;s/"//g' | tr ',' ' ' | head -5)
SLUG=$(basename "$LATEST_POST" .md)
URL="https://sechunter.github.io/post/$SLUG/"

# Build tweet
TWEET="🔒 $TITLE\n\n$DESC\n\n#CyberSecurity #BugBounty #InfoSec #Hacking #PenTesting $TAGS\n\nRead more: $URL"

log "=== Social Media Post ==="
log "Title: $TITLE"
log "URL: $URL"
log ""
log "=== Tweet ==="
log "$TWEET"
log ""
log "=== Reddit Post ==="
log "Title: $TITLE"
log "URL: $URL"
log "Subreddits: r/netsec, r/cybersecurity, r/bugbounty, r/ethicalhacking"
log ""
log "=== LinkedIn Post ==="
log "Title: $TITLE"
log "Description: $DESC"
log "URL: $URL"

# Save social media content for manual posting
SOCIAL_FILE="$BLOG_DIR/scripts/social-$DATE.txt"
cat > "$SOCIAL_FILE" << SOCIAL
=== Social Media Content for $DATE ===

=== Twitter/X ===
$TWEET

=== Reddit ===
Title: $TITLE
URL: $URL
Subreddits: r/netsec, r/cybersecurity, r/bugbounty, r/ethicalhacking, r/hacking

=== LinkedIn ===
🔒 New Blog Post: $TITLE

$DESC

Read the full article: $URL

#CyberSecurity #BugBounty #InfoSec #PenTesting #Hacking #AI #SecurityResearch

=== Hacker News ===
Title: $TITLE
URL: $URL

=== Mastodon ===
🔒 $TITLE

$DESC

#CyberSecurity #BugBounty #InfoSec #Hacking

$URL
SOCIAL

log "Social media content saved to $SOCIAL_FILE"
echo "Done. Check $SOCIAL_FILE for content to post."
