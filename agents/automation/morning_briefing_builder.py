#!/usr/bin/env python3
"""
MORNING BRIEFING BUILDER
Runs daily at 5:30am

Pulls from Notion:
- Yesterday's news (AI, crypto, trading, AUS, international)
- Market snapshots
- Any urgent items from yesterday

Generates:
- Beautiful HTML page
- Motivational quote (based on Dibs' patterns)
- Market summary
- News curated by importance

Deploys to Vercel
Posts Discord notification with link
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import hashlib

# Dependencies: pip install notion-client requests

from notion_client import Client as NotionClient
import requests

# Configuration
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_MORNING_BRIEFING_DB_ID")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
VERCEL_PROJECT = os.getenv("VERCEL_PROJECT", "dibs-empire-roadmap")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
OPENCLAW_WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", "~/.openclaw/workspace")).expanduser()

# Initialize clients
notion = NotionClient(auth=NOTION_TOKEN) if NOTION_TOKEN else None

# =============================================================================
# QUOTE GENERATION
# =============================================================================

MOTIVATIONAL_QUOTES = {
    "morning_trading": [
        "Market opens in {hours}h. Probabilities move fast. Stay disciplined.",
        "Another day another opportunity to stay in the game. What's your first trade?",
        "Emotions are for amateurs. Data first. Always.",
        "You're only 1 good trade away from a big week. Let's go.",
    ],
    "probability": [
        "Not every trade. Just the high-probability ones. Patience.",
        "Risk management separates winners from broke traders.",
        "You don't need to be right often. Just when it matters.",
    ],
    "freedom": [
        "Every dollar in profit is one step closer to Tokyo.",
        "Your brother got it made. You're building something. Stay hungry.",
        "10x income = 10x freedom. What's your next move?",
    ],
    "accountability": [
        "Sober-you would execute this. Do it.",
        "Stop waiting. Start now. Prove yourself.",
        "Your 3-year vision is built today. Not tomorrow.",
    ]
}

def generate_motivational_quote() -> str:
    """
    Generate a motivational quote based on time of day and Dibs' patterns
    """
    
    import random
    
    now = datetime.now()
    hour = now.hour
    
    # Choose category based on time and mood
    if 6 <= hour < 10:
        # Morning = trading prep
        category = "morning_trading"
    elif 10 <= hour < 12:
        # Mid-morning = probability focus
        category = "probability"
    elif 16 <= hour < 18:
        # Late afternoon = freedom focus
        category = "freedom"
    else:
        # Everything else = accountability
        category = "accountability"
    
    quotes = MOTIVATIONAL_QUOTES.get(category, MOTIVATIONAL_QUOTES["accountability"])
    quote = random.choice(quotes)
    
    # Format with context
    if "{hours}" in quote:
        # Market opens at 9:30pm Sydney time (8:30am EST)
        if hour < 21:
            hours_until = 21 - hour
            quote = quote.format(hours=hours_until)
    
    return quote

# =============================================================================
# FETCH NOTION DATA
# =============================================================================

def fetch_yesterday_news() -> Dict[str, List[Dict]]:
    """
    Fetch news articles from Notion created in the last 24 hours
    Organized by category
    """
    
    if not notion or not NOTION_DB_ID:
        print("  ⚠️ Notion not configured")
        return {}
    
    yesterday = datetime.now() - timedelta(days=1)
    
    try:
        response = notion.databases.query(
            NOTION_DB_ID,
            filter={
                "property": "Timestamp",
                "date": {
                    "on_or_after": yesterday.isoformat()
                }
            },
            sorts=[
                {
                    "property": "Timestamp",
                    "direction": "descending"
                }
            ]
        )
        
        news_by_category = {}
        
        for page in response.get('results', []):
            props = page.get('properties', {})
            
            category = "general"
            if 'Category' in props and props['Category'].get('select'):
                category = props['Category']['select']['name']
            
            if category not in news_by_category:
                news_by_category[category] = []
            
            article = {
                "title": extract_text(props.get('Title', {})),
                "summary": extract_text(props.get('Summary', {})),
                "source": extract_text(props.get('Source', {})),
                "link": props.get('Link', {}).get('url', '#'),
                "timestamp": props.get('Timestamp', {}).get('date', {}).get('start', datetime.now().isoformat()),
            }
            
            news_by_category[category].append(article)
        
        return news_by_category
    
    except Exception as e:
        print(f"  ❌ Notion fetch error: {e}")
        return {}

def fetch_crypto_snapshot() -> Dict:
    """
    Fetch latest crypto data
    """
    
    try:
        response = requests.get(
            'https://api.coingecko.com/api/v3/coins/markets',
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 5,
                'sparkline': False,
            },
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"  ⚠️ CoinGecko error: {e}")
    
    return []

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def extract_text(notion_block: Dict) -> str:
    """Extract plain text from Notion rich text block"""
    
    if 'title' in notion_block:
        return ''.join([t.get('text', {}).get('content', '') for t in notion_block['title']])
    elif 'rich_text' in notion_block:
        return ''.join([t.get('text', {}).get('content', '') for t in notion_block['rich_text']])
    
    return ""

# =============================================================================
# HTML GENERATION
# =============================================================================

def generate_html(
    news_data: Dict[str, List[Dict]],
    crypto_data: List[Dict],
    quote: str
) -> str:
    """
    Generate beautiful HTML for morning briefing
    """
    
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    
    # Build news sections HTML
    news_html = ""
    category_emojis = {
        "ai news": "🤖",
        "crypto trading": "💰",
        "australia": "🇦🇺",
        "international": "🌍",
    }
    
    for category, articles in sorted(news_data.items()):
        emoji = category_emojis.get(category.lower(), "📰")
        news_html += f"""
        <section class="category">
            <h2>{emoji} {category.title()}</h2>
            <div class="articles">
        """
        
        for article in articles[:3]:  # Top 3 per category
            news_html += f"""
                <article>
                    <h3><a href="{article['link']}" target="_blank">{article['title']}</a></h3>
                    <p class="summary">{article['summary']}</p>
                    <p class="meta">— {article['source']}</p>
                </article>
            """
        
        news_html += """
            </div>
        </section>
        """
    
    # Build crypto snapshot HTML
    crypto_html = ""
    if crypto_data:
        crypto_html = """
        <section class="crypto-snapshot">
            <h2>💹 Crypto Snapshot</h2>
            <div class="crypto-grid">
        """
        
        for coin in crypto_data[:5]:
            price_change = coin.get('price_change_percentage_24h', 0)
            change_color = "green" if price_change >= 0 else "red"
            
            crypto_html += f"""
                <div class="crypto-card">
                    <h3>{coin.get('name')}</h3>
                    <p class="price">${coin.get('current_price', 0):,.2f}</p>
                    <p class="change {change_color}">{price_change:+.2f}%</p>
                </div>
            """
        
        crypto_html += """
            </div>
        </section>
        """
    
    # Full HTML page
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dibs Morning Briefing — {date_str}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header .date {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .quote-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px;
            border-radius: 8px;
            font-style: italic;
            font-size: 1.1em;
            color: #555;
        }}
        
        .content {{
            padding: 40px 20px;
        }}
        
        section {{
            margin-bottom: 40px;
        }}
        
        section h2 {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .articles {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }}
        
        article {{
            border: 1px solid #e0e0e0;
            padding: 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        
        article:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        article h3 {{
            margin-bottom: 10px;
        }}
        
        article a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        
        article a:hover {{
            text-decoration: underline;
        }}
        
        .summary {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        
        .meta {{
            font-size: 0.9em;
            color: #999;
        }}
        
        .crypto-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .crypto-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        
        .crypto-card h3 {{
            margin-bottom: 10px;
        }}
        
        .price {{
            font-size: 1.4em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .change {{
            font-weight: bold;
        }}
        
        .change.green {{
            color: #10b981;
        }}
        
        .change.red {{
            color: #ef4444;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #999;
            border-top: 1px solid #e0e0e0;
        }}
        
        footer p {{
            margin: 5px 0;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 1.8em;
            }}
            
            section h2 {{
                font-size: 1.4em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🗡️ Dibs Morning Briefing</h1>
            <div class="date">{date_str}</div>
        </header>
        
        <div class="quote-box">
            "{quote}"
        </div>
        
        <div class="content">
            {crypto_html}
            {news_html}
        </div>
        
        <footer>
            <p>Briefing generated at {now.strftime('%H:%M %Z')}</p>
            <p>📊 Your personalized intelligence summary</p>
        </footer>
    </div>
</body>
</html>
"""
    
    return html

# =============================================================================
# VERCEL DEPLOYMENT
# =============================================================================

def deploy_to_vercel(html_content: str) -> Optional[str]:
    """
    Deploy briefing HTML to Vercel
    Returns public URL
    """
    
    if not VERCEL_TOKEN or not VERCEL_PROJECT:
        print("  ⚠️ Vercel not configured")
        return None
    
    try:
        # Create deployment
        response = requests.post(
            f"https://api.vercel.com/v13/deployments",
            headers={
                "Authorization": f"Bearer {VERCEL_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "name": VERCEL_PROJECT,
                "files": [
                    {
                        "file": "briefing.html",
                        "data": html_content,
                    }
                ],
                "projectSettings": {
                    "buildCommand": None,
                    "devCommand": None,
                    "outputDirectory": None,
                }
            }
        )
        
        if response.status_code in [200, 201]:
            deployment = response.json()
            url = f"https://{deployment.get('alias', deployment.get('url'))}"
            return url
        else:
            print(f"  ❌ Vercel error: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"  ❌ Deployment error: {e}")
        return None

# =============================================================================
# DISCORD NOTIFICATION
# =============================================================================

def notify_discord(briefing_url: str):
    """
    Post notification to Discord with briefing link
    """
    
    if not DISCORD_WEBHOOK:
        print("  ⚠️ Discord webhook not configured")
        return
    
    try:
        message = {
            "embeds": [
                {
                    "title": "🗡️ Morning Briefing Ready",
                    "description": f"Your personalized briefing is ready to read",
                    "color": 6649471,  # Purple
                    "fields": [
                        {
                            "name": "📊 Contents",
                            "value": "AI news, Crypto snapshot, Trading alerts, Aus/International news",
                            "inline": False
                        },
                        {
                            "name": "⏰ Time",
                            "value": datetime.now().strftime("%H:%M %Z"),
                            "inline": True
                        }
                    ],
                    "url": briefing_url,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Read Briefing",
                            "style": 5,
                            "url": briefing_url
                        }
                    ]
                }
            ]
        }
        
        requests.post(DISCORD_WEBHOOK, json=message)
        print(f"  ✅ Discord notified")
    
    except Exception as e:
        print(f"  ⚠️ Discord notification error: {e}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_morning_briefing_builder():
    """
    Main briefing builder function
    """
    
    print(f"\n{'='*60}")
    print(f"📰 MORNING BRIEFING BUILDER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Fetch data
    print("📚 Fetching news from Notion...")
    news_data = fetch_yesterday_news()
    
    print("💹 Fetching crypto snapshot...")
    crypto_data = fetch_crypto_snapshot()
    
    print("✨ Generating motivational quote...")
    quote = generate_motivational_quote()
    
    # Generate HTML
    print("🎨 Generating HTML...")
    html = generate_html(news_data, crypto_data, quote)
    
    # Deploy
    print("🚀 Deploying to Vercel...")
    briefing_url = deploy_to_vercel(html)
    
    if briefing_url:
        print(f"✅ Deployed: {briefing_url}")
        
        # Notify Discord
        print("📢 Notifying Discord...")
        notify_discord(briefing_url)
        
        # Save to local file
        local_file = OPENCLAW_WORKSPACE / "briefings" / f"briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        local_file.parent.mkdir(parents=True, exist_ok=True)
        with open(local_file, 'w') as f:
            f.write(html)
        print(f"✅ Saved locally: {local_file}")
    else:
        print("❌ Deployment failed")

# =============================================================================
# SCHEDULER SETUP
# =============================================================================

def setup_scheduler():
    """
    Set up scheduler to run daily at 5:30am
    
    Cron: 0 5 * * * /usr/bin/python3 /path/to/morning_briefing_builder.py run
    """
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BackgroundScheduler()
        
        scheduler.add_job(
            run_morning_briefing_builder,
            CronTrigger(hour=5, minute=30),
            id='morning_briefing_builder'
        )
        
        scheduler.start()
        return scheduler
    
    except ImportError:
        print("⚠️ APScheduler not installed")
        return None

# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "schedule":
        print("⏰ Setting up scheduler for daily 5:30am run...")
        scheduler = setup_scheduler()
        if scheduler:
            print("✅ Scheduler running. Press Ctrl+C to stop.")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                scheduler.shutdown()
    else:
        # Run once
        run_morning_briefing_builder()
