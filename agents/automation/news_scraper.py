#!/usr/bin/env python3
"""
NEWS SCRAPER FOR MORNING BRIEFING
Runs at:
- Market close (4pm EST / 9pm Australian)
- 11pm daily

Scrapes:
- AI news
- Crypto/trading news
- Sydney/Australia news
- International news (relevant)

Updates Notion "Morning Briefing" database
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Dependencies: pip install aiohttp feedparser newsapi notion-client

import feedparser
from newsapi import NewsApiClient
from notion_client import Client as NotionClient

# Configuration
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB_ID = os.getenv("NOTION_MORNING_BRIEFING_DB_ID")  # You'll set this
OPENCLAW_WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", "~/.openclaw/workspace")).expanduser()

# Initialize clients
notion = NotionClient(auth=NOTION_TOKEN) if NOTION_TOKEN else None
news_api = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None

# News sources configuration
NEWS_SOURCES = {
    "ai_news": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://feeds.theverge.com/vergeoscience.xml",
    ],
    "crypto_trading": [
        "https://feeds.bloomberg.com/markets/cryptocurrency.rss",
        "https://coindesk.com/feed/",
    ],
    "australia": [
        "https://feeds.abc.net.au/news/national/",
        "https://www.smh.com.au/feed.xml",
    ],
    "international": [
        "https://feeds.reuters.com/reuters/worldNews",
        "https://feeds.bbci.co.uk/news/rss.xml",
    ]
}

# =============================================================================
# NEWS FETCHING
# =============================================================================

async def fetch_from_newsapi(query: str, category: str = None) -> List[Dict]:
    """
    Fetch news from NewsAPI.org
    Free tier: 100 requests/day, 30-day history
    """
    
    if not news_api:
        print("  ⚠️ NewsAPI not configured")
        return []
    
    try:
        if category:
            articles = news_api.get_top_headlines(category=category, language='en', page_size=5)
        else:
            articles = news_api.get_everything(q=query, sort_by='publishedAt', page_size=5)
        
        return articles.get('articles', [])
    except Exception as e:
        print(f"  ❌ NewsAPI error: {e}")
        return []

async def fetch_from_rss_feeds() -> Dict[str, List[Dict]]:
    """
    Fetch from RSS feeds
    Returns dict organized by category
    """
    
    results = {}
    
    async with aiohttp.ClientSession() as session:
        for category, feeds in NEWS_SOURCES.items():
            results[category] = []
            
            for feed_url in feeds:
                try:
                    async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            content = await resp.text()
                            feed = feedparser.parse(content)
                            
                            # Get last 5 entries
                            for entry in feed.entries[:5]:
                                article = {
                                    "title": entry.get('title', 'No title'),
                                    "link": entry.get('link', ''),
                                    "summary": entry.get('summary', '')[:200],
                                    "published": entry.get('published', datetime.now().isoformat()),
                                    "source": feed.feed.get('title', feed_url),
                                }
                                results[category].append(article)
                
                except asyncio.TimeoutError:
                    print(f"  ⏱️ Timeout fetching {feed_url}")
                except Exception as e:
                    print(f"  ⚠️ Error fetching {feed_url}: {e}")
    
    return results

# =============================================================================
# FILTERING & RANKING
# =============================================================================

def filter_relevant_news(articles: List[Dict], keywords: List[str]) -> List[Dict]:
    """
    Filter articles by relevance keywords
    """
    
    relevant = []
    
    for article in articles:
        title_lower = article.get('title', '').lower()
        summary_lower = article.get('summary', '').lower()
        
        for keyword in keywords:
            if keyword.lower() in title_lower or keyword.lower() in summary_lower:
                relevant.append(article)
                break
    
    return relevant

def rank_articles(articles: List[Dict]) -> List[Dict]:
    """
    Rank articles by relevance and recency
    """
    
    # Sort by published date (newest first)
    try:
        sorted_articles = sorted(
            articles,
            key=lambda x: datetime.fromisoformat(x.get('published', '').replace('Z', '+00:00')),
            reverse=True
        )
    except:
        sorted_articles = articles
    
    return sorted_articles[:5]  # Top 5 per category

# =============================================================================
# NOTION INTEGRATION
# =============================================================================

async def update_notion_briefing(news_data: Dict[str, List[Dict]]):
    """
    Update Notion "Morning Briefing" database with news
    """
    
    if not notion or not NOTION_DB_ID:
        print("  ⚠️ Notion not configured")
        return
    
    try:
        # Clear old entries (optional)
        # query_response = notion.databases.query(NOTION_DB_ID)
        # for page in query_response.get('results', []):
        #     notion.pages.update(page['id'], archived=True)
        
        # Add new entries
        for category, articles in news_data.items():
            for article in rank_articles(articles)[:3]:  # Top 3 per category
                
                # Create page in Notion
                notion.pages.create(
                    parent={"database_id": NOTION_DB_ID},
                    properties={
                        "Title": {
                            "title": [{"text": {"content": article.get('title', 'No title')[:100]}}]
                        },
                        "Category": {
                            "select": {"name": category.replace('_', ' ').title()}
                        },
                        "Link": {
                            "url": article.get('link', '')
                        },
                        "Summary": {
                            "rich_text": [{"text": {"content": article.get('summary', '')}}]
                        },
                        "Source": {
                            "rich_text": [{"text": {"content": article.get('source', 'Unknown')}}]
                        },
                        "Timestamp": {
                            "date": {"start": article.get('published', datetime.now().isoformat())}
                        }
                    }
                )
                
                print(f"    ✅ Added: {article.get('title', '')[:60]}...")
    
    except Exception as e:
        print(f"  ❌ Notion update error: {e}")

# =============================================================================
# MARKET DATA FETCHING (Optional but recommended)
# =============================================================================

async def fetch_crypto_snapshot() -> Dict:
    """
    Fetch crypto market snapshot from CoinGecko (free, no API key needed)
    """
    
    async with aiohttp.ClientSession() as session:
        try:
            # Get top 5 cryptos by market cap
            async with session.get(
                'https://api.coingecko.com/api/v3/coins/markets',
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 5,
                    'sparkline': False,
                },
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"  ⚠️ CoinGecko error: {e}")
    
    return []

async def fetch_market_data() -> Dict:
    """
    Fetch stock market data from Alpha Vantage (requires API key)
    For now, just crypto snapshot
    """
    
    data = {
        "crypto_snapshot": await fetch_crypto_snapshot(),
        "timestamp": datetime.now().isoformat()
    }
    
    return data

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def run_news_scraper():
    """
    Main scraper function
    """
    
    print(f"\n{'='*60}")
    print(f"📰 NEWS SCRAPER RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Fetch all news sources
    print("🔍 Fetching RSS feeds...")
    rss_news = await fetch_from_rss_feeds()
    
    print("🔍 Fetching NewsAPI articles...")
    newsapi_results = {
        "ai_latest": await fetch_from_newsapi("artificial intelligence OR machine learning", "technology"),
        "crypto_latest": await fetch_from_newsapi("cryptocurrency OR bitcoin OR ethereum"),
        "trading_latest": await fetch_from_newsapi("stock market OR trading OR finance"),
    }
    
    # Combine and filter
    all_news = {**rss_news, **newsapi_results}
    
    # Fetch market data
    print("📊 Fetching market data...")
    market_data = await fetch_market_data()
    
    # Save to local file for reference
    cache_file = OPENCLAW_WORKSPACE / "cache" / f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cache_file, 'w') as f:
        json.dump({
            "news": all_news,
            "market_data": market_data,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"✅ Cached to {cache_file}")
    
    # Update Notion
    print("\n📝 Updating Notion...")
    await update_notion_briefing(all_news)
    
    print(f"\n✅ News scraper complete!")
    print(f"   Categories processed: {', '.join(all_news.keys())}")
    print(f"   Total articles: {sum(len(v) for v in all_news.values())}")

# =============================================================================
# SCHEDULER SETUP (Run this to set up cron jobs)
# =============================================================================

def setup_scheduler():
    """
    Set up scheduler to run at:
    - 9pm daily (market close)
    - 11pm daily
    
    Using APScheduler
    
    Example cron:
    0 21 * * * /usr/bin/python3 /path/to/news_scraper.py run
    0 23 * * * /usr/bin/python3 /path/to/news_scraper.py run
    """
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        
        scheduler = BackgroundScheduler()
        
        # 9pm run (market close)
        scheduler.add_job(
            lambda: asyncio.run(run_news_scraper()),
            CronTrigger(hour=21, minute=0),
            id='news_scraper_market_close'
        )
        
        # 11pm run
        scheduler.add_job(
            lambda: asyncio.run(run_news_scraper()),
            CronTrigger(hour=23, minute=0),
            id='news_scraper_night'
        )
        
        scheduler.start()
        return scheduler
    
    except ImportError:
        print("⚠️ APScheduler not installed. Install with: pip install apscheduler")
        return None

# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "schedule":
        print("⏰ Setting up scheduler...")
        scheduler = setup_scheduler()
        if scheduler:
            print("✅ Scheduler running. Press Ctrl+C to stop.")
            try:
                while True:
                    asyncio.sleep(1)
            except KeyboardInterrupt:
                scheduler.shutdown()
    else:
        # Run once
        asyncio.run(run_news_scraper())
