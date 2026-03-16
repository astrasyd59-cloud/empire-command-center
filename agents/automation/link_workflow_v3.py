#!/usr/bin/env python3
"""
LINK WORKFLOW v3.0 - REAL ANALYSIS PIPELINE
Integrates content extraction with honest failure handling
"""
import os
import sys
import json
import re
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Import the real analyzer
sys.path.insert(0, '/home/astra/.openclaw/workspace/agents/automation')
from link_analyzer_real import analyze_link_real, download_content, extract_domain

# Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_LINK_DB_ID = os.getenv("NOTION_LINK_ANALYSIS_DB_ID", "30d8b652-b7df-819f-8506-f330141e9670")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN")

def generate_report_html_real(url, title, domain, analysis, content_info):
    """Generate professional HTML report from REAL analysis"""
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    # Extract from analysis
    summary = analysis.get('summary', 'No summary available')
    ideas = analysis.get('ideas', [])
    actionable = analysis.get('actionable', analysis.get('implementation', 'Review content for actionable items'))
    pros = analysis.get('pros', [])
    cons = analysis.get('cons', [])
    steps = analysis.get('steps', [])
    
    # Build HTML lists
    ideas_html = "".join([f'<li>{idea}</li>' for idea in ideas]) if ideas else '<li>No key ideas extracted</li>'
    pros_html = "".join([f'<li>{pro}</li>' for pro in pros]) if pros else '<li>No pros identified</li>'
    cons_html = "".join([f'<li>{con}</li>' for con in cons]) if cons else '<li>No cons identified</li>'
    steps_html = "".join([f'<li>{step}</li>' for step in steps]) if steps else '<li>No steps defined</li>'
    
    # Content quality indicator
    content_quality = content_info.get('quality', 'unknown')
    quality_badge = {
        'full': '🟢 Full Analysis',
        'partial': '🟡 Partial Analysis', 
        'failed': '🔴 Analysis Failed'
    }.get(content_quality, '⚪ Unknown')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Analysis | {title[:50]}...</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            line-height: 1.6;
            min-height: 100vh;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        header {{ 
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 30px;
        }}
        header h1 {{ font-size: 2rem; margin-bottom: 10px; color: white; }}
        header .meta {{ opacity: 0.9; font-size: 0.9rem; color: rgba(255,255,255,0.8); }}
        .quality-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 10px;
            background: {'#10b981' if content_quality == 'full' else '#f59e0b' if content_quality == 'partial' else '#ef4444'};
            color: white;
        }}
        .card {{ 
            background: #1a1a25;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid #2a2a35;
        }}
        .card h2 {{ 
            color: #10b981;
            margin-bottom: 15px;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .card h2::before {{ content: "▸"; color: #6366f1; }}
        .summary {{ font-size: 1.1rem; line-height: 1.8; color: #e0e0e0; }}
        ul {{ list-style: none; padding-left: 0; }}
        ul li {{ 
            padding: 12px 0;
            padding-left: 30px;
            position: relative;
            border-bottom: 1px solid #2a2a35;
            line-height: 1.6;
        }}
        ul li:last-child {{ border-bottom: none; }}
        ul li::before {{ 
            position: absolute;
            left: 0;
            font-weight: bold;
        }}
        .ideas li::before {{ content: "💡"; }}
        .pros li::before {{ content: "✓"; color: #10b981; }}
        .cons li::before {{ content: "✗"; color: #ef4444; }}
        .steps li::before {{ content: "⚡"; color: #f59e0b; }}
        .source-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: #6366f1;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .source-link:hover {{ background: #5558e0; transform: translateY(-1px); }}
        .actionable-box {{
            background: linear-gradient(135deg, #1e3a2f 0%, #2d5a4a 100%);
            border-left: 4px solid #10b981;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .actionable-box h3 {{
            color: #10b981;
            margin-bottom: 10px;
            font-size: 1.1rem;
        }}
        .warning {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 15px;
            border-radius: 8px;
            color: #fca5a5;
            margin: 20px 0;
        }}
        @media (max-width: 600px) {{
            .container {{ padding: 20px 15px; }}
            header {{ padding: 25px; }}
            header h1 {{ font-size: 1.5rem; }}
            .card {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔗 Link Analysis Report</h1>
            <div class="meta">{domain} • Analyzed on {now}</div>
            <span class="quality-badge">{quality_badge}</span>
        </header>
        
        <div class="card">
            <h2>Source</h2>
            <p><strong>{title}</strong></p>
            <a href="{url}" target="_blank" class="source-link">View Original →</a>
        </div>
        
        <div class="card">
            <h2>Summary</h2>
            <p class="summary">{summary}</p>
        </div>
        
        <div class="card">
            <h2>Key Ideas</h2>
            <ul class="ideas">{ideas_html}</ul>
        </div>
        
        <div class="actionable-box">
            <h3>🎯 Actionable Insights</h3>
            <p>{actionable}</p>
        </div>
        
        <div class="card">
            <h2>Pros</h2>
            <ul class="pros">{pros_html}</ul>
        </div>
        
        <div class="card">
            <h2>Cons & Considerations</h2>
            <ul class="cons">{cons_html}</ul>
        </div>
        
        <div class="card">
            <h2>Priority Steps</h2>
            <ul class="steps">{steps_html}</ul>
        </div>
        
        {('<div class="warning"><strong>⚠️ Note:</strong> ' + content_info.get('warning', '') + '</div>') if content_info.get('warning') else ''}
    </div>
</body>
</html>"""
    
    return html

def process_link_v3(url, chat_id):
    """
    v3.0 Workflow with REAL analysis
    """
    print(f"\n🗡️ LINK WORKFLOW v3.0 - REAL ANALYSIS")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    # Step 1: Try real analysis
    print("🔍 Attempting real content analysis...")
    result = analyze_link_real(url, chat_id)
    
    content_info = {
        'quality': 'failed',
        'warning': None
    }
    
    if result.get('success'):
        # Got real analysis
        analysis = result['analysis']
        title = result['title']
        
        if result.get('content_length', 0) > 1000:
            content_info['quality'] = 'full'
        else:
            content_info['quality'] = 'partial'
            content_info['warning'] = 'Limited content was extracted. Analysis may be incomplete.'
        
        print(f"\n✅ REAL ANALYSIS SUCCESSFUL")
        print(f"   Content type: {result.get('content_type')}")
        print(f"   Content length: {result.get('content_length')} chars")
        
    else:
        # Failed - need manual intervention
        print(f"\n❌ AUTOMATED ANALYSIS FAILED")
        print(f"   Reason: {result.get('error', 'Unknown')}")
        print(f"   Content sample: {result.get('content_sample', 'N/A')[:200]}...")
        
        # Create honest "needs manual review" report
        analysis = {
            'summary': f"Automated analysis failed for this {result.get('content_type', 'content')}. Manual review required.",
            'ideas': ['Content could not be automatically extracted', 'Requires manual reading and analysis'],
            'actionable': 'Open the original link and read manually. Take notes on key takeaways.',
            'pros': ['Content may contain valuable insights', 'Worth manual review'],
            'cons': ['Requires your time to extract value', 'No automated summary available'],
            'steps': [
                '1. Open the original link',
                '2. Read/skim the full content',
                '3. Extract 3-5 key takeaways',
                '4. Identify 1-2 actionable items'
            ]
        }
        title = result.get('title', 'Unknown Content')
        content_info['quality'] = 'failed'
        content_info['warning'] = f"Automated extraction failed: {result.get('error', 'Could not access content')}. Manual review recommended."
    
    # Step 2: Generate report
    print("\n🎨 Generating report...")
    html = generate_report_html_real(url, title, extract_domain(url), analysis, content_info)
    
    # Step 3: Deploy
    print("\n🚀 Deploying...")
    vercel_url = None
    netlify_url = None
    
    # ... deployment code (same as before) ...
    
    # Step 4: Notify
    if content_info['quality'] == 'failed':
        # Send honest message
        message = f"""⚠️ **Link Analysis - Manual Review Needed**

I couldn't automatically analyze this content.

**Why:** {content_info['warning']}

**What you can do:**
1. Open the link directly
2. Read and extract key points yourself
3. Send me a summary if you want me to help prioritize/action

Sorry - the automated extraction hit a wall on this one. Some content types (PDFs, paywalls, complex sites) need manual review.

🔗 {url}"""
    else:
        message = f"""📊 **Link Analysis Complete**

Quality: {'Full' if content_info['quality'] == 'full' else 'Partial'} Analysis

{content_info['warning'] if content_info.get('warning') else ''}

Summary: {analysis.get('summary', 'N/A')[:100]}...

**Next steps:**
{chr(10).join(analysis.get('steps', [])[:2])}

View full report: [Vercel URL would be here]"""
    
    print("\n✅ WORKFLOW COMPLETE")
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        chat_id = sys.argv[2] if len(sys.argv) > 2 else None
        process_link_v3(url, chat_id)
    else:
        print("Usage: python3 link_workflow_v3.py <url> [chat_id]")
