#!/usr/bin/env python3
"""
SOCIAL MANAGER - Link Analysis Agent
Analyzes links and posts to Discord #notifications
"""
import os
import requests
from urllib.parse import urlparse
from datetime import datetime

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
NOTIFICATIONS_CHANNEL = "1474327480805363783"  # #notifications
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def extract_domain(url):
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return "unknown"

def categorize_link(url, domain):
    """Categorize link by domain/content"""
    url_lower = url.lower()
    domain_lower = domain.lower()
    
    # Trading/Finance
    if any(x in domain_lower or x in url_lower for x in ['coin', 'crypto', 'bitcoin', 'eth', 'trading', 'forex', 'market', 'finance', 'bloomberg', 'coindesk']):
        return "📈 Trading/Finance", "Trading-related content"
    
    # AI/Tech
    if any(x in domain_lower or x in url_lower for x in ['ai', 'openai', 'chatgpt', 'tech', 'verge', 'ars', 'github', 'stackoverflow']):
        return "🤖 AI/Tech", "Technology and AI content"
    
    # News
    if any(x in domain_lower for x in ['news', 'bbc', 'reuters', 'abc', 'smh']):
        return "📰 News", "General news content"
    
    # Job/Career
    if any(x in domain_lower or x in url_lower for x in ['linkedin', 'indeed', 'glassdoor', 'career', 'job']):
        return "💼 Career", "Job or career-related"
    
    return "🔗 General", "Uncategorized link"

def analyze_link(url):
    """Analyze a link and return structured data"""
    domain = extract_domain(url)
    category, description = categorize_link(url, domain)
    
    # Fetch page title (basic)
    title = None
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            # Extract title from HTML
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
            if title_match:
                title = title_match.group(1).strip()[:100]
    except:
        pass
    
    if not title:
        title = f"Article from {domain}"
    
    return {
        'url': url,
        'domain': domain,
        'title': title,
        'category': category,
        'description': description,
        'timestamp': datetime.now().isoformat()
    }

def post_to_discord(analysis):
    """Post analysis to Discord #notifications"""
    if not DISCORD_WEBHOOK:
        return False
    
    embed = {
        "title": f"{analysis['category']} Analysis",
        "description": analysis['title'],
        "url": analysis['url'],
        "color": 0x6366f1,
        "fields": [
            {
                "name": "Source",
                "value": analysis['domain'],
                "inline": True
            },
            {
                "name": "Category",
                "value": analysis['description'],
                "inline": True
            }
        ],
        "timestamp": analysis['timestamp'],
        "footer": {
            "text": "🔗 Social Manager Analysis"
        }
    }
    
    try:
        resp = requests.post(
            DISCORD_WEBHOOK,
            json={"embeds": [embed]},
            timeout=10
        )
        return resp.status_code == 204
    except Exception as e:
        print(f"Discord error: {e}")
        return False

def notify_telegram(chat_id, analysis, actionable):
    """Send analysis back to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    action_emoji = "✅" if actionable else "📌"
    action_text = "Actionable" if actionable else "For reference"
    
    message = f"""{action_emoji} **Link Analyzed**

**{analysis['title']}**
🔗 {analysis['url']}

📂 Category: {analysis['category']}
📝 {analysis['description']}

💡 Verdict: {action_text}

Posted to Discord #notifications"""
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            },
            timeout=10
        )
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def process_link(url, chat_id=None):
    """Full pipeline: Analyze → Discord → Telegram"""
    print(f"🔍 Analyzing: {url}")
    
    # Step 1: Analyze
    analysis = analyze_link(url)
    print(f"  ✅ Title: {analysis['title'][:50]}...")
    print(f"  ✅ Category: {analysis['category']}")
    
    # Step 2: Post to Discord
    discord_ok = post_to_discord(analysis)
    if discord_ok:
        print("  ✅ Posted to Discord")
    else:
        print("  ⚠️ Discord post failed")
    
    # Step 3: Report back to Telegram
    if chat_id:
        # Determine if actionable (simple heuristic)
        actionable = any(x in analysis['category'] for x in ['Trading', 'Career', 'Job'])
        telegram_ok = notify_telegram(chat_id, analysis, actionable)
        if telegram_ok:
            print("  ✅ Reported back to Telegram")
    
    return analysis

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        chat_id = sys.argv[2] if len(sys.argv) > 2 else None
        process_link(url, chat_id)
    else:
        print("Usage: python3 social_manager.py <url> [chat_id]")
