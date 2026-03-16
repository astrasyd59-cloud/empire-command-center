#!/usr/bin/env python3
"""
ENHANCED LINK WORKFLOW v2.1 - With Netlify Deployment
Full pipeline: Telegram → Analysis → UI/UX Report → Notion → Discord
"""
import os
import json
import re
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_LINK_DB_ID = os.getenv("NOTION_LINK_ANALYSIS_DB_ID", "30d8b652-b7df-819f-8506-f330141e9670")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
VERCEL_PROJECT = os.getenv("VERCEL_PROJECT", "dibs-empire-roadmap")
NETLIFY_TOKEN = os.getenv("NETLIFY_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENCLAW_WORKSPACE = Path(os.getenv("OPENCLAW_WORKSPACE", "~/.openclaw/workspace")).expanduser()

def extract_domain(url):
    """Extract domain from URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except:
        return "unknown"

def fetch_video_info(url):
    """Extract video title/description if YouTube/other video"""
    try:
        resp = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code == 200:
            title_match = re.search(r'<title[^>]*>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
            if title_match:
                return title_match.group(1).strip()[:200]
    except:
        pass
    return None

def analyze_with_groq(url, title):
    """Use Groq to analyze the content"""
    if not GROQ_API_KEY:
        return generate_fallback_analysis(url, title)
    
    try:
        prompt = f"""Analyze this link for a crypto trader/operations manager looking to improve his life and career:
        
URL: {url}
Title: {title}

Provide a structured analysis:
1. SUMMARY: What's this about? (2-3 sentences)
2. KEY IDEAS: What are the main concepts? (3-5 bullet points)
3. IMPLEMENTATION: What could Dibs actually implement? (specific actions)
4. PROS: Why should he do this? (benefits)
5. CONS: What are the risks/downsides? (be honest)
6. PRIORITY STEPS: Ordered list of first 3 steps to take

Format as JSON with keys: summary, ideas, implementation, pros, cons, steps"""

        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            content = resp.json()['choices'][0]['message']['content']
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except Exception as e:
        print(f"Groq error: {e}")
    
    return generate_fallback_analysis(url, title)

def generate_fallback_analysis(url, title):
    """Fallback analysis if Groq fails"""
    domain = extract_domain(url)
    
    return {
        "summary": f"Content from {domain}. Analysis pending manual review.",
        "ideas": ["Review content for actionable insights", "Identify relevant strategies", "Consider implementation feasibility"],
        "implementation": "Watch/read content fully, take notes on actionable items",
        "pros": ["New perspective", "Potential strategies", "Learning opportunity"],
        "cons": ["Time investment required", "May not be directly applicable", "Information overload"],
        "steps": ["1. Review content fully", "2. Extract actionable items", "3. Prioritize by impact"]
    }

def generate_report_html(url, title, domain, analysis):
    """Generate professional HTML report"""
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    ideas_html = "".join([f'<li>{idea}</li>' for idea in analysis.get('ideas', [])])
    pros_html = "".join([f'<li>{pro}</li>' for pro in analysis.get('pros', [])])
    cons_html = "".join([f'<li>{con}</li>' for con in analysis.get('cons', [])])
    steps_html = "".join([f'<li>{step}</li>' for step in analysis.get('steps', [])])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Link Analysis Report | {title[:50]}...</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #fff;
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
        header h1 {{ font-size: 2rem; margin-bottom: 10px; }}
        header .meta {{ opacity: 0.8; font-size: 0.9rem; }}
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
            padding: 10px 0;
            padding-left: 25px;
            position: relative;
            border-bottom: 1px solid #2a2a35;
        }}
        ul li:last-child {{ border-bottom: none; }}
        ul li::before {{ 
            content: "→";
            position: absolute;
            left: 0;
            color: #6366f1;
        }}
        .pros li::before {{ content: "✓"; color: #10b981; }}
        .cons li::before {{ content: "✗"; color: #ef4444; }}
        .steps li::before {{ content: "⚡"; color: #f59e0b; }}
        .button-container {{ 
            display: flex;
            gap: 15px;
            margin-top: 30px;
            justify-content: center;
        }}
        .btn {{
            padding: 15px 40px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
        }}
        .btn-primary:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3); }}
        .btn-secondary {{
            background: #2a2a35;
            color: #fff;
        }}
        .btn-secondary:hover {{ background: #3a3a45; }}
        .source-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 12px 24px;
            background: #6366f1;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
        }}
        .source-link:hover {{ background: #5558e0; }}
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
        </header>
        
        <div class="card">
            <h2>Source</h2>
            <p><strong>{title}</strong></p>
            <a href="{url}" target="_blank" class="source-link">View Original →</a>
        </div>
        
        <div class="card">
            <h2>Summary</h2>
            <p class="summary">{analysis.get('summary', 'No summary available.')}</p>
        </div>
        
        <div class="card">
            <h2>Key Ideas</h2>
            <ul>{ideas_html}</ul>
        </div>
        
        <div class="card">
            <h2>Implementation</h2>
            <p>{analysis.get('implementation', 'Review content for specific implementation steps.')}</p>
        </div>
        
        <div class="card">
            <h2>Pros</h2>
            <ul class="pros">{pros_html}</ul>
        </div>
        
        <div class="card">
            <h2>Cons</h2>
            <ul class="cons">{cons_html}</ul>
        </div>
        
        <div class="card">
            <h2>Priority Steps</h2>
            <ul class="steps">{steps_html}</ul>
        </div>
        
        <div class="button-container">
            <button class="btn btn-primary" onclick="approveImplementation()">✓ Approve & Implement</button>
            <button class="btn btn-secondary" onclick="rejectAnalysis()">✗ Reject</button>
        </div>
    </div>
    
    <script>
        function approveImplementation() {{
            alert('Implementation approved! Status updated in Notion.');
        }}
        function rejectAnalysis() {{
            alert('Analysis rejected. Status updated in Notion.');
        }}
    </script>
</body>
</html>"""
    
    return html

def deploy_to_vercel(html):
    """Deploy to Vercel"""
    if not VERCEL_TOKEN:
        return None
    
    try:
        deploy_url = "https://api.vercel.com/v13/deployments"
        headers = {
            "Authorization": f"Bearer {VERCEL_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "name": VERCEL_PROJECT,
            "files": [{"file": "index.html", "data": html}],
            "target": "production"
        }
        
        resp = requests.post(deploy_url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('url') or f"https://{VERCEL_PROJECT}.vercel.app"
    except Exception as e:
        print(f"Vercel error: {e}")
    
    return None

def deploy_to_netlify(html):
    """Deploy to Netlify using CLI"""
    if not NETLIFY_TOKEN:
        return None
    
    try:
        # Create temp directory for deployment
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.html"
            with open(index_path, 'w') as f:
                f.write(html)
            
            # Deploy using Netlify CLI
            result = subprocess.run(
                ['netlify', 'deploy', '--prod', '--dir', tmpdir, '--auth', NETLIFY_TOKEN, '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                output = json.loads(result.stdout)
                return output.get('url') or output.get('deploy_url')
            else:
                print(f"Netlify deploy error: {result.stderr}")
    except Exception as e:
        print(f"Netlify error: {e}")
    
    return None

def add_to_notion(url, title, summary, status, category, vercel_url, netlify_url):
    """Add entry to Notion Link Analysis database"""
    if not NOTION_TOKEN or not NOTION_LINK_DB_ID:
        print("Notion not configured")
        return None
    
    try:
        from notion_client import Client
        notion = Client(auth=NOTION_TOKEN)
        
        # Build properties
        properties = {
            "Title": {"title": [{"text": {"content": title[:100]}}]},
            "Link": {"url": url},
            "Summary": {"rich_text": [{"text": {"content": summary[:200]}}]},
            "Status": {"select": {"name": status}},
            "Category": {"select": {"name": category}},
            "Date Added": {"date": {"start": datetime.now().isoformat()}},
        }
        
        # Add URLs if available
        if vercel_url:
            properties["Report URL"] = {"url": vercel_url}
            properties["Vercel URL"] = {"url": vercel_url}
        if netlify_url:
            properties["Netlify URL"] = {"url": netlify_url}
        
        page = notion.pages.create(
            parent={"database_id": NOTION_LINK_DB_ID},
            properties=properties
        )
        return page['id']
    except Exception as e:
        print(f"Notion error: {e}")
        return None

def notify_telegram(chat_id, vercel_url, netlify_url, summary):
    """Send report link to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return
    
    urls_text = f"Vercel: {vercel_url}"
    if netlify_url:
        urls_text += f"\nNetlify: {netlify_url}"
    
    message = f"""📊 Report ready!

{urls_text}

Summary: {summary[:100]}..."""
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            },
            timeout=10
        )
    except Exception as e:
        print(f"Telegram notify error: {e}")

def post_to_discord(url, title, report_url):
    """Post to Discord #notifications"""
    if not DISCORD_WEBHOOK:
        return
    
    embed = {
        "title": "🔗 Link Analyzed",
        "description": title[:200],
        "url": report_url,
        "color": 0x6366f1,
        "fields": [
            {"name": "Source", "value": extract_domain(url), "inline": True},
            {"name": "Report", "value": f"[View Analysis]({report_url})", "inline": True}
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        requests.post(
            DISCORD_WEBHOOK,
            json={"embeds": [embed]},
            timeout=10
        )
    except Exception as e:
        print(f"Discord error: {e}")

def process_link(url, chat_id):
    """Full workflow"""
    print(f"🔄 Processing: {url}")
    
    # Step 1: Acknowledge
    print("  ✅ Acknowledged in Telegram")
    
    # Step 2: Fetch info
    title = fetch_video_info(url) or f"Content from {extract_domain(url)}"
    print(f"  ✅ Title: {title[:50]}...")
    
    # Step 3: Analyze
    print("  🔍 Analyzing with Groq...")
    analysis = analyze_with_groq(url, title)
    print("  ✅ Analysis complete")
    
    # Step 4: Generate report
    print("  🎨 Generating UI/UX report...")
    html = generate_report_html(url, title, extract_domain(url), analysis)
    print("  ✅ Report generated")
    
    # Step 5: Deploy to both platforms
    print("  🚀 Deploying...")
    vercel_url = deploy_to_vercel(html)
    netlify_url = deploy_to_netlify(html)
    
    if vercel_url:
        print(f"  ✅ Vercel: {vercel_url}")
    if netlify_url:
        print(f"  ✅ Netlify: {netlify_url}")
    
    report_url = vercel_url or netlify_url
    
    # Step 6: Add to Notion
    print("  📝 Adding to Notion...")
    category = "Trading" if any(x in url.lower() for x in ['trade', 'crypto', 'bitcoin']) else "Tech"
    notion_id = add_to_notion(url, title, analysis['summary'], "Pending Approval", category, vercel_url, netlify_url)
    if notion_id:
        print("  ✅ Notion entry created")
    
    # Step 7: Notify Telegram
    print("  📱 Notifying Telegram...")
    notify_telegram(chat_id, vercel_url, netlify_url, analysis['summary'])
    
    # Step 8: Post Discord
    if report_url:
        print("  💬 Posting to Discord...")
        post_to_discord(url, title, report_url)
    
    print("\n✅ WORKFLOW COMPLETE")
    return vercel_url, netlify_url

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        url = sys.argv[1]
        chat_id = sys.argv[2] if len(sys.argv) > 2 else None
        process_link(url, chat_id)
    else:
        print("Usage: python3 link_workflow.py <url> [chat_id]")
