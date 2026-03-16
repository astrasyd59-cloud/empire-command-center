#!/usr/bin/env python3
"""
NOTION CONNECTION TEST - Fixed write test
"""
import os
from notion_client import Client
from datetime import datetime, timezone

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DB_ID = os.getenv("NOTION_MORNING_BRIEFING_DB_ID")

print("🔍 Testing Notion connection...")
print(f"DB ID: {DB_ID}")

try:
    # Test database retrieve
    db = notion.databases.retrieve(database_id=DB_ID)
    print(f"✅ Database retrieved: {db['title'][0]['plain_text']}")
    
    # Test write with proper timestamp format
    print("📝 Testing write operation...")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    new_page = notion.pages.create(
        parent={"database_id": DB_ID},
        properties={
            "Title": {"title": [{"text": {"content": "Test Article - Deployment Check"}}]},
            "Category": {"select": {"name": "AI News"}},
            "Link": {"url": "https://example.com/test"},
            "Summary": {"rich_text": [{"text": {"content": "This is a test article to verify Notion integration is working."}}]},
            "Source": {"rich_text": [{"text": {"content": "Deployment Test"}}]},
            "Timestamp": {"date": {"start": now}},
            "Status": {"select": {"name": "Pending"}}
        }
    )
    print(f"✅ Write successful! Page ID: {new_page['id']}")
    print("✅ NOTION DATABASE: FULLY OPERATIONAL")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
