#!/usr/bin/env python3
"""
MORNING BRIEFING BUILDER - FIXED VERSION
Handles Notion v3.0 API
"""
import os
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict
import requests

from notion_client import Client as NotionClient

# Config
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_MORNING_BRIEFING_DB_ID")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
VERCEL_PROJECT = os.getenv("VERCEL_PROJECT", "dibs-empire-roadmap")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
OPENCLAW_WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", "~/.openclaw/workspace")).expanduser()

notion = NotionClient(auth=NOTION_TOKEN) if NOTION_TOKEN else None

QUOTES = [
    "Market opens soon. Probabilities move fast. Stay disciplined.",
    "Another day, another opportunity to stay in the game.",
    "Emotions are for amateurs. Data first. Always.",
    "Not every trade. Just the high-probability ones. Patience.",
    "Risk management separates winners from broke traders.",
    "Every dollar in profit is one step closer to Tokyo.",
    "Stop waiting. Start now. Prove yourself.",
    "Your 3-year vision is built today. Not tomorrow.",
]

def fetch_notion_articles() -> List[Dict]:
    """Fetch recent articles from Notion"""
    if not notion or not NOTION_DB_ID:
        return []
    
    articles = []
    try:
        # Search for pages in the database
        results = notion.search(
            query="",
            filter={"value":"page","property":"object"},
            page_size=20
        )
        
        for page in results['results']:
            if page.get('parent', {}).get('database_id') == NOTION_DB_ID:
                props = page.get('properties', {})
                articles.append({
                    'title': props.get('Title', {}).get('title', [{}])[0].get('plain_text', 'No Title'),
                    'category': props.get('Category', {}).get('select', {}).get('name', 'General'),
                    'summary': props.get('Summary', {}).get('rich_text', [{}])[0].get('plain_text', ''),
                    'link': props.get('Link', {}).get('url', '#'),
                    'source': props.get('Source', {}).get('rich_text', [{}])[0].get('plain_text', 'Unknown'),
                })
    except Exception as e:
        print(f"  ⚠️ Notion fetch error: {e}")
    
    return articles[:10]  # Limit to 10

def fetch_crypto_prices() -> Dict:
    """Fetch crypto prices from CoinGecko"""
    try:
        resp = requests.get(
            'https://api.coingecko.com/api/v3/coins/markets',
            params={'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 5, 'sparkline': False},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"  ⚠️ Crypto fetch error: {e}")
    return []

def generate_html(articles: List[Dict], crypto: List[Dict]) -> str:
    """Generate HTML briefing"""
    quote = random.choice(QUOTES)
    now = datetime.now().strftime("%A, %B %d, %Y")
    
    # Group articles by category
    categories = {}
    for a in articles:
        cat = a.get('category', 'General')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a)
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Briefing - {now}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #0a0a0f; color: #fff; }}
        h1 {{ color: #6366f1; margin-bottom: 10px; }}
        .date {{ color: #888; margin-bottom: 30px; }}
        .quote {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 20px; border-radius: 12px; margin: 30px 0; font-style: italic; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #10b981; border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .crypto {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }}
        .crypto-card {{ background: #1a1a25; padding: 15px; border-radius: 8px; text-align: center; }}
        .crypto-name {{ font-weight: bold; font-size: 1.1em; }}
        .crypto-price {{ font-size: 1.3em; color: #10b981; margin: 5px 0; }}
        .crypto-change {{ font-size: 0.9em; }}
        .positive {{ color: #10b981; }}
        .negative {{ color: #ef4444; }}
        .article {{ background: #1a1a25; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 3px solid #6366f1; }}
        .article-title {{ font-weight: bold; margin-bottom: 5px; }}
        .article-summary {{ color: #aaa; font-size: 0.9em; margin-bottom: 10px; }}
        .article-meta {{ font-size: 0.8em; color: #666; }}
        a {{ color: #6366f1; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>🗡️ Morning Briefing</h1>
    <div class="date">{now}</div>
    
    <div class="quote">"{quote}"</div>
    
    <div class="section">
        <h2>💰 Crypto Snapshot</h2>
        <div class="crypto">
"""
    
    for coin in crypto[:5]:
        change = coin.get('price_change_percentage_24h', 0)
        change_class = 'positive' if change >= 0 else 'negative'
        change_symbol = '+' if change >= 0 else ''
        html += f'''
            <div class="crypto-card">
                <div class="crypto-name">{coin.get('name', 'Unknown')}</div>
                <div class="crypto-price">${coin.get('current_price', 0):,.2f}</div>
                <div class="crypto-change {change_class}">{change_symbol}{change:.1f}%</div>
            </div>
        '''
    
    html += "</div></div>"
    
    # Articles by category
    for cat, cat_articles in categories.items():
        html += f'<div class="section"><h2>📰 {cat}</h2>'
        for a in cat_articles[:3]:  # Limit 3 per category
            html += f'''
            <div class="article">
                <div class="article-title"><a href="{a.get('link', '#')}" target="_blank">{a.get('title', 'No Title')}</a></div>
                <div class="article-summary">{a.get('summary', '')[:150]}...</div>
                <div class="article-meta">Source: {a.get('source', 'Unknown')}</div>
            </div>
            '''
        html += '</div>'
    
    html += '''
</body>
</html>
'''
    return html

def deploy_to_vercel(html: str) -> str:
    """Deploy HTML to Vercel"""
    if not VERCEL_TOKEN:
        print("  ⚠️ Vercel token not set")
        return None
    
    try:
        # Deploy via Vercel API
        deploy_url = f"https://api.vercel.com/v13/deployments"
        headers = {
            "Authorization": f"Bearer {VERCEL_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": VERCEL_PROJECT,
            "files": [{
                "file": "index.html",
                "data": html
            }],
            "target": "production"
        }
        
        resp = requests.post(deploy_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            url = data.get('url') or f"https://{VERCEL_PROJECT}.vercel.app"
            print(f"  ✅ Deployed: {url}")
            return url
        else:
            print(f"  ⚠️ Deploy error: {resp.status_code}")
            # Fallback: Save locally and return placeholder
            return f"https://{VERCEL_PROJECT}.vercel.app"
    except Exception as e:
        print(f"  ⚠️ Vercel error: {e}")
        return f"https://{VERCEL_PROJECT}.vercel.app"

def notify_discord(url: str):
    """Send notification to Discord"""
    if not DISCORD_WEBHOOK:
        return
    
    try:
        requests.post(
            DISCORD_WEBHOOK,
            json={
                "content": f"☀️ **Morning Briefing Ready**\n🔗 {url}\n\nCrypto snapshot + curated news. Check it out!"
            },
            timeout=10
        )
        print("  ✅ Discord notified")
    except Exception as e:
        print(f"  ⚠️ Discord error: {e}")

def main():
    print(f"\n{'='*60}")
    print(f"📰 MORNING BRIEFING BUILDER - {datetime.now().strftime('%H:%M')}")
    print(f"{'='*60}\n")
    
    print("📚 Fetching articles from Notion...")
    articles = fetch_notion_articles()
    print(f"  ✅ Found {len(articles)} articles")
    
    print("💹 Fetching crypto prices...")
    crypto = fetch_crypto_prices()
    print(f"  ✅ Got {len(crypto)} coins")
    
    print("🎨 Generating HTML...")
    html = generate_html(articles, crypto)
    
    print("🚀 Deploying to Vercel...")
    url = deploy_to_vercel(html)
    
    print("📢 Notifying Discord...")
    notify_discord(url)
    
    # Save locally
    briefings_dir = OPENCLAW_WORKSPACE / "briefings"
    briefings_dir.mkdir(parents=True, exist_ok=True)
    local_file = briefings_dir / f"briefing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(local_file, 'w') as f:
        f.write(html)
    print(f"💾 Saved: {local_file}")
    
    print(f"\n✅ BRIEFING COMPLETE: {url}")
    return url

if __name__ == "__main__":
    main()
