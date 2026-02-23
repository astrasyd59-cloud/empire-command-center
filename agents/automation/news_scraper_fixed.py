#!/usr/bin/env python3
"""
NEWS SCRAPER - FIXED VERSION
Handles timestamp conversion for Notion
"""
import os
import json
import asyncio
import aiohttp
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
import email.utils  # For parsing RFC dates

from newsapi import NewsApiClient
from notion_client import Client as NotionClient

# Configuration
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_MORNING_BRIEFING_DB_ID")
OPENCLAW_WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", "~/.openclaw/workspace")).expanduser()

# Initialize clients
notion = NotionClient(auth=NOTION_TOKEN) if NOTION_TOKEN else None
news_api = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None

def parse_date_to_iso(date_str: str) -> str:
    """Convert various date formats to ISO 8601 for Notion"""
    if not date_str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    try:
        # Try RFC format first (Thu, 19 Feb 2026 22:44:25 +0000)
        parsed = email.utils.parsedate_to_datetime(date_str)
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    except:
        try:
            # Try ISO format
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except:
            # Fallback to now
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

async def fetch_from_newsapi(query: str, category: str = None) -> List[Dict]:
    """Fetch news from NewsAPI.org"""
    if not news_api:
        return []
    
    try:
        if category:
            articles = news_api.get_top_headlines(category=category, language='en', page_size=5)
        else:
            articles = news_api.get_everything(q=query, sort_by='publishedAt', page_size=5)
        return articles.get('articles', [])
    except Exception as e:
        print(f"  ⚠️ NewsAPI error: {e}")
        return []

def categorize_article(title: str, description: str = "") -> str:
    """Categorize article based on content"""
    text = f"{title} {description}".lower()
    
    if any(word in text for word in ['crypto', 'bitcoin', 'ethereum', 'blockchain', 'trading', 'market']):
        return "Crypto Trading"
    elif any(word in text for word in ['ai', 'artificial intelligence', 'machine learning', 'chatgpt', 'llm']):
        return "AI News"
    elif any(word in text for word in ['australia', 'sydney', 'aus', 'canberra']):
        return "Australia"
    else:
        return "International"

def update_notion(articles: List[Dict]):
    """Update Notion database with articles"""
    if not notion or not NOTION_DB_ID:
        print("  ⚠️ Notion not configured")
        return
    
    added_count = 0
    for article in articles[:10]:  # Limit to 10 articles per run
        try:
            # Parse and convert timestamp
            raw_date = article.get('publishedAt', '')
            iso_date = parse_date_to_iso(raw_date)
            
            # Determine category
            category = categorize_article(
                article.get('title', ''),
                article.get('description', '')
            )
            
            notion.pages.create(
                parent={"database_id": NOTION_DB_ID},
                properties={
                    "Title": {"title": [{"text": {"content": article.get('title', 'No Title')[:100]}}]},
                    "Category": {"select": {"name": category}},
                    "Link": {"url": article.get('url', 'https://example.com')},
                    "Summary": {"rich_text": [{"text": {"content": article.get('description', 'No summary')[:200]}}]},
                    "Source": {"rich_text": [{"text": {"content": article.get('source', {}).get('name', 'Unknown')}}]},
                    "Timestamp": {"date": {"start": iso_date}},
                    "Status": {"select": {"name": "Pending"}}
                }
            )
            added_count += 1
            print(f"    ✅ Added: {article.get('title', '')[:50]}...")
            
        except Exception as e:
            print(f"    ⚠️ Skip: {e}")
    
    print(f"  ✅ Added {added_count} articles to Notion")

async def run_scraper():
    """Main scraper"""
    print(f"\n{'='*60}")
    print(f"📰 NEWS SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Fetch from NewsAPI
    print("🔍 Fetching AI news...")
    ai_news = await fetch_from_newsapi("artificial intelligence", "technology")
    
    print("🔍 Fetching crypto news...")
    crypto_news = await fetch_from_newsapi("cryptocurrency OR bitcoin OR ethereum")
    
    print("🔍 Fetching trading news...")
    trading_news = await fetch_from_newsapi("stock market trading")
    
    # Combine all articles
    all_articles = ai_news + crypto_news + trading_news
    print(f"\n📊 Total articles fetched: {len(all_articles)}")
    
    # Cache locally
    cache_file = OPENCLAW_WORKSPACE / "cache" / f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, 'w') as f:
        json.dump({"articles": all_articles, "timestamp": datetime.now().isoformat()}, f)
    print(f"💾 Cached to {cache_file}")
    
    # Update Notion
    print("\n📝 Updating Notion database...")
    update_notion(all_articles)
    
    print("\n✅ NEWS SCRAPER COMPLETE")

if __name__ == "__main__":
    asyncio.run(run_scraper())
