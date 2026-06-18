#!/bin/bash
# SecHunter News Aggregator
# Runs every 6 hours via cron: 0 */6 * * * /data/data/com.termux/files/home/sec-hunter-blog/scripts/news-aggregator.sh

BLOG_DIR="/data/data/com.termux/files/home/sec-hunter-blog"
NEWS_DIR="$BLOG_DIR/scripts/news"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)

mkdir -p "$NEWS_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:S')] $1" >> "$BLOG_DIR/scripts/news.log"
}

log "=== News aggregation started ==="

# Source 1: HackerOne Hacktivity
curl -s --max-time 15 "https://hackerone.com/hacktivity/overview" 2>/dev/null | \
    grep -oE '>[A-Za-z]+ [A-Za-z]+ [0-9]+<' | head -20 > "$NEWS_DIR/hackerone-$DATE-$TIME.txt" 2>/dev/null

# Source 2: CVE Latest
curl -s --max-time 15 "https://cve.circl.lu/api/last/5" 2>/dev/null | \
    python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for item in data:
        print(f'{item.get(\"id\")}: {item.get(\"summary\", \"\")[:120]}')
except: pass
" > "$NEWS_DIR/cve-$DATE-$TIME.txt" 2>/dev/null

# Source 3: NVD CVE Feed
curl -s --max-time 15 "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5&pubStartDate=${DATE}T00:00:00.000" 2>/dev/null | \
    python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for vuln in data.get('vulnerabilities', []):
        cve = vuln.get('cve', {})
        desc = cve.get('descriptions', [{}])[0].get('value', '')[:120]
        print(f'{cve.get(\"id\")}: {desc}')
except: pass
" > "$NEWS_DIR/nvd-$DATE-$TIME.txt" 2>/dev/null

# Source 4: Security News RSS (The Hacker News)
curl -s --max-time 15 "https://feeds.feedburner.com/TheHackersNews" 2>/dev/null | \
    grep -oE '<title>[^<]+</title>' | head -10 > "$NEWS_DIR/thn-$DATE-$TIME.txt" 2>/dev/null

# Source 5: SecurityWeek
curl -s --max-time 15 "https://www.securityweek.com/feed/" 2>/dev/null | \
    grep -oE '<title>[^<]+</title>' | head -10 > "$NEWS_DIR/securityweek-$DATE-$TIME.txt" 2>/dev/null

# Source 6: BleepingComputer
curl -s --max-time 15 "https://www.bleepingcomputer.com/feed/" 2>/dev/null | \
    grep -oE '<title>[^<]+</title>' | head -10 > "$NEWS_DIR/bleepingcomputer-$DATE-$TIME.txt" 2>/dev/null

# Source 7: Krebs on Security
curl -s --max-time 15 "https://krebsonsecurity.com/feed/" 2>/dev/null | \
    grep -oE '<title>[^<]+</title>' | head -10 > "$NEWS_DIR/krebs-$DATE-$TIME.txt" 2>/dev/null

# Source 8: Dark Reading
curl -s --max-time 15 "https://www.darkreading.com/rss.xml" 2>/dev/null | \
    grep -oE '<title>[^<]+</title>' | head -10 > "$NEWS_DIR/darkreading-$DATE-$TIME.txt" 2>/dev/null

# Combine all news
{
    echo "=== SecHunter News Digest ==="
    echo "Date: $DATE $TIME"
    echo ""
    echo "=== Latest CVEs ==="
    cat "$NEWS_DIR/cve-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== NVD Latest ==="
    cat "$NEWS_DIR/nvd-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== HackerOne Hacktivity ==="
    cat "$NEWS_DIR/hackerone-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== The Hacker News ==="
    cat "$NEWS_DIR/thn-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== SecurityWeek ==="
    cat "$NEWS_DIR/securityweek-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== BleepingComputer ==="
    cat "$NEWS_DIR/bleepingcomputer-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== Krebs on Security ==="
    cat "$NEWS_DIR/krebs-$DATE-$TIME.txt" 2>/dev/null
    echo ""
    echo "=== Dark Reading ==="
    cat "$NEWS_DIR/darkreading-$DATE-$TIME.txt" 2>/dev/null
} > "$NEWS_DIR/digest-$DATE-$TIME.txt"

# Clean up old news files (keep last 7 days)
find "$NEWS_DIR" -name "*.txt" -mtime +7 -delete 2>/dev/null

log "=== News aggregation complete ==="
log "Digest saved to $NEWS_DIR/digest-$DATE-$TIME.txt"
