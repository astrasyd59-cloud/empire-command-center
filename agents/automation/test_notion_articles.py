#!/usr/bin/env python3
"""
Test Notion article fetching
"""
import os
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DB_ID = os.getenv("NOTION_MORNING_BRIEFING_DB_ID")

print(f"Database ID: {DB_ID}")

# Try to query the database directly
try:
    # Method 1: Search for pages
    results = notion.search(
        query="",
        filter={"value":"page","property":"object"},
        page_size=50
    )
    print(f"\nTotal pages found: {len(results['results'])}")
    
    # Check which ones belong to our database
    db_pages = []
    for page in results['results']:
        parent = page.get('parent', {})
        if parent.get('database_id') == DB_ID:
            db_pages.append(page)
    
    print(f"Pages in our database: {len(db_pages)}")
    
    for page in db_pages[:5]:
        props = page.get('properties', {})
        title = props.get('Title', {}).get('title', [{}])[0].get('plain_text', 'No Title')
        print(f"  - {title}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
